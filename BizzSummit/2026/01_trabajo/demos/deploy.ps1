#requires -Version 7.0
<#
.SYNOPSIS
    Despliega el escenario completo de las cuatro demos de la sesión
    "De la jungla de agentes al control plane" — Bizz Summit Madrid 2026.

.DESCRIPTION
    Ocho etapas acumulativas. El tenant de destino se toma de config.local.json,
    así que el mismo repositorio sirve para varios tenants sin tocar código.

    El proceso es idempotente: reutiliza lo que ya existe con el mismo nombre y
    solo crea lo que falta. Los identificadores se guardan en el archivo de estado
    para que cleanup.ps1 sepa qué es suyo y qué se reutilizó.

    Las etapas que exigen Global Admin o Compliance Admin (Purview y Exchange)
    se intentan de verdad. Si faltan permisos, el paso se anota en un runbook
    manual con el comando exacto ya relleno, y el despliegue continúa.

.PARAMETER ConfigPath
    Ruta a config.local.json. Cópialo de config.example.json.

.PARAMETER Stage
    Etapa máxima a ejecutar (1-8). Por defecto, la de config.despliegue.stage.

.PARAMETER OnlyStage
    Ejecuta exclusivamente esa etapa, sin las anteriores. Útil para reintentar una sola.

.PARAMETER ValidateOnly
    No toca el tenant: valida config, rutas de datos, herramientas y YAML del agente.

.EXAMPLE
    pwsh ./deploy.ps1 -ConfigPath ./config.local.json -ValidateOnly

.EXAMPLE
    pwsh ./deploy.ps1 -ConfigPath ./config.local.json -Stage 8

.EXAMPLE
    pwsh ./deploy.ps1 -ConfigPath ./config.local.json -OnlyStage 3 -WhatIf
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.local.json"),
    [ValidateRange(1, 8)][int]$Stage,
    [ValidateRange(1, 8)][int]$OnlyStage,
    [switch]$ValidateOnly
)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"

Import-Module (Join-Path $PSScriptRoot "scripts/Common.psm1") -Force

$ETAPAS = [ordered]@{
    1 = @{ Nombre = "Entornos y grupo de entornos"; Script = "Stage1-Entornos.ps1" }
    2 = @{ Nombre = "Sitios de SharePoint y conocimiento"; Script = "Stage2-SharePoint.ps1" }
    3 = @{ Nombre = "Purview: etiqueta y DLP de IBAN"; Script = "Stage3-Purview.ps1" }
    4 = @{ Nombre = "Dataverse: tablas y datos"; Script = "Stage4-Dataverse.ps1" }
    5 = @{ Nombre = "DLP de Power Platform y endpoint filtering"; Script = "Stage5-DlpPlataforma.ps1" }
    6 = @{ Nombre = "Agente de Copilot Studio"; Script = "Stage6-Agente.ps1" }
    7 = @{ Nombre = "Buzón de devoluciones y siembra de correos"; Script = "Stage7-Buzon.ps1" }
    8 = @{ Nombre = "Test sets y evaluaciones"; Script = "Stage8-Evaluaciones.ps1" }
}

Write-Host ""
Write-Host "FraSoHome · Bizz Summit 2026 — despliegue de demos" -ForegroundColor White
Write-Host "--------------------------------------------------" -ForegroundColor DarkGray

$config = Get-DemoConfig -ConfigPath $ConfigPath
Write-Paso "Tenant destino: $($config.tenant.displayName) <$($config.tenant.domain)>" -Nivel Ok

$raizDatos = Resolve-RutaDemo -Config $config -Ruta $config.datos.raizFraSoHome
if (-not (Test-Path -LiteralPath $raizDatos -PathType Container)) {
    throw "No encuentro el material de FraSoHome en '$raizDatos'. Ajusta datos.raizFraSoHome en $ConfigPath."
}
Write-Paso "Material FraSoHome: $raizDatos" -Nivel Ok

# ---------------------------------------------------------------- preflight
Write-Etapa "Preflight"
$ok = $true
$ok = (Test-Herramienta -Nombre "pac") -and $ok
$ok = (Test-Herramienta -Nombre "az") -and $ok
$ok = (Test-ModuloPowerShell -Nombre "Microsoft.PowerApps.Administration.PowerShell") -and $ok
$ok = (Test-ModuloPowerShell -Nombre "Microsoft.Graph.Sites") -and $ok
$ok = (Test-ModuloPowerShell -Nombre "ExchangeOnlineManagement") -and $ok

if (-not $ok) {
    if ($ValidateOnly) {
        Write-Paso "Faltan requisitos. En -ValidateOnly se avisa y se continúa." -Nivel Aviso
    }
    else {
        throw "Faltan requisitos previos. Instálalos y vuelve a lanzar el despliegue."
    }
}

# Validación de los ficheros de datos que cada etapa espera encontrar
Write-Etapa "Validación de material de entrada"
$kbOrigen = Join-Path $raizDatos "01_datos/rag_copilot_studio/knowledge_base/Documentos_Knowledge_Clasificados"
$csvOrigen = Join-Path $raizDatos "01_datos/rag_copilot_studio/structured_csv"
$testOrigen = Join-Path $raizDatos "01_datos/rag_copilot_studio/test_sets"

foreach ($carpeta in @($kbOrigen, $csvOrigen, $testOrigen)) {
    if (Test-Path -LiteralPath $carpeta -PathType Container) {
        Write-Paso "OK $carpeta" -Nivel Ok
    }
    else {
        Write-Paso "No existe $carpeta" -Nivel Error
        $ok = $false
    }
}

$faltan = @()
foreach ($doc in @($config.datos.documentosVigentes) + @($config.datos.documentoObsoleto)) {
    $encontrado = Get-ChildItem -LiteralPath $kbOrigen -Recurse -Filter $doc -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if (-not $encontrado) { $faltan += $doc }
}
if ($faltan.Count -gt 0) {
    Write-Paso "No se encontraron $($faltan.Count) documentos: $($faltan -join ', ')" -Nivel Error
    $ok = $false
}
else {
    Write-Paso "Los 9 documentos FS-KB de origen están donde deben" -Nivel Ok
}

# El agente se empaqueta desde YAML: se valida la sintaxis antes de tocar nada
$agenteDir = Join-Path $PSScriptRoot "agente"
$yamls = Get-ChildItem -LiteralPath $agenteDir -Recurse -Include "*.yaml", "*.yml" -File
Write-Paso "Proyecto del agente: $($yamls.Count) archivos YAML" -Nivel Ok

if ($ValidateOnly) {
    Write-Host ""
    if ($ok) {
        Write-Host "Validación superada. Nada se ha escrito en el tenant." -ForegroundColor Green
        exit 0
    }
    Write-Host "Validación con errores. Revisa lo marcado arriba." -ForegroundColor Red
    exit 1
}

if (-not $ok) { throw "El material de entrada no está completo. Corrígelo antes de desplegar." }

# ---------------------------------------------------------------- ejecución
$estadoPath = Resolve-RutaDemo -Config $config -Ruta $config.despliegue.estadoPath
$estado = Get-EstadoDespliegue -EstadoPath $estadoPath
$estado["tenant"] = $config.tenant.domain

$objetivo = if ($PSBoundParameters.ContainsKey("Stage")) { $Stage } else { [int]$config.despliegue.stage }
$aEjecutar = if ($PSBoundParameters.ContainsKey("OnlyStage")) { @($OnlyStage) } else { 1..$objetivo }

$contexto = [pscustomobject]@{
    Config    = $config
    Estado    = $estado
    RaizDatos = $raizDatos
    RaizDemo  = $PSScriptRoot
    Simular   = -not $PSCmdlet.ShouldProcess($config.tenant.domain, "Desplegar demos")
}

try {
    foreach ($n in $aEjecutar) {
        $etapa = $ETAPAS[$n]
        Write-Etapa "Etapa $n — $($etapa.Nombre)"
        $script = Join-Path $PSScriptRoot "scripts/stages/$($etapa.Script)"
        if (-not (Test-Path -LiteralPath $script -PathType Leaf)) {
            throw "No existe el script de la etapa $n : $script"
        }
        & $script -Contexto $contexto
        $estado["ultimaEtapa"] = $n
        Save-EstadoDespliegue -Estado $estado -EstadoPath $estadoPath
    }
}
finally {
    Save-EstadoDespliegue -Estado $estado -EstadoPath $estadoPath
    Write-RunbookFile -Estado $estado -RunbookPath (Resolve-RutaDemo -Config $config -Ruta $config.despliegue.runbookPath)
}

Write-Host ""
Write-Host "Despliegue terminado." -ForegroundColor Green
Write-Host "Siguiente paso: poblar telemetría con uso/Invoke-TraficoAgente.ps1" -ForegroundColor Gray
