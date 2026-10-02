#requires -Version 7.0
<#
.SYNOPSIS
    Comprueba el repositorio sin tocar ningún tenant.

.DESCRIPTION
    Lo que valida:
      · Que todos los .ps1 y .psm1 parsean.
      · Que config.example.json es JSON válido y tiene las claves que el código lee.
      · Que existen las ocho etapas y los scripts de uso.
      · Que el test set de seguridad suma 20 casos con los otros dos.
      · Que los YAML del agente no tienen tabuladores ni marcadores sin sustituir
        distintos de los conocidos.
      · Que el Python del agente externo compila.

    Ejecútalo antes de cada despliegue y después de tocar cualquier script.
#>
[CmdletBinding()]
param([string]$Raiz = (Split-Path -Parent $PSScriptRoot))

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"

$fallos = @()
$avisos = @()

function Assert-Cierto {
    param([bool]$Condicion, [string]$Mensaje)
    if ($Condicion) {
        Write-Host "  ok   $Mensaje" -ForegroundColor Green
    }
    else {
        Write-Host "  FALLO $Mensaje" -ForegroundColor Red
        $script:fallos += $Mensaje
    }
}

function Add-Aviso {
    param([string]$Mensaje)
    Write-Host "  aviso $Mensaje" -ForegroundColor Yellow
    $script:avisos += $Mensaje
}

Write-Host ""
Write-Host "Test-Repositorio — demos Bizz Summit 2026" -ForegroundColor White
Write-Host "Raíz: $Raiz" -ForegroundColor DarkGray

# --- 1. Sintaxis de PowerShell -------------------------------------------------
Write-Host "`n[1] Sintaxis de PowerShell" -ForegroundColor Cyan
$scripts = Get-ChildItem -LiteralPath $Raiz -Recurse -Include "*.ps1", "*.psm1" -File |
    Where-Object { $_.FullName -notmatch "[\\/]\.pac[\\/]" }
foreach ($s in $scripts) {
    $errores = $null
    [void][System.Management.Automation.Language.Parser]::ParseFile($s.FullName, [ref]$null, [ref]$errores)
    $rel = $s.FullName.Substring($Raiz.Length).TrimStart('\', '/')
    Assert-Cierto (($null -eq $errores) -or ($errores.Count -eq 0)) "$rel parsea"
    if ($errores) {
        foreach ($e in $errores | Select-Object -First 3) {
            Write-Host "        línea $($e.Extent.StartLineNumber): $($e.Message)" -ForegroundColor DarkRed
        }
    }
}

# --- 2. Configuración ----------------------------------------------------------
Write-Host "`n[2] Configuración" -ForegroundColor Cyan
$ejemplo = Join-Path $Raiz "config.example.json"
Assert-Cierto (Test-Path -LiteralPath $ejemplo) "existe config.example.json"

$cfg = $null
try {
    $cfg = Get-Content -LiteralPath $ejemplo -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Cierto $true "config.example.json es JSON válido"
}
catch {
    Assert-Cierto $false "config.example.json es JSON válido — $($_.Exception.Message)"
}

if ($cfg) {
    $claves = @(
        "tenant.domain", "tenant.id",
        "powerPlatform.publisherPrefix", "powerPlatform.dlpPolicyName",
        "agente.schemaName", "agente.displayName", "agente.directLineTokenEndpoint",
        "sharepoint.rootUrl", "sharepoint.kbSite.alias", "sharepoint.restrictedSite.alias",
        "purview.labelName", "purview.dlpPolicyName", "purview.sensitiveInfoTypeName",
        "exchange.sharedMailbox",
        "datos.raizFraSoHome", "datos.devolucionSensible", "datos.ibanSintetico",
        "evaluaciones.apiRoot",
        "despliegue.estadoPath", "despliegue.runbookPath"
    )
    foreach ($ruta in $claves) {
        $v = $cfg
        foreach ($p in $ruta.Split(".")) {
            if ($null -eq $v) { break }
            $prop = $v.PSObject.Properties[$p]
            $v = if ($prop) { $prop.Value } else { $null }
        }
        Assert-Cierto ($null -ne $v) "config tiene $ruta"
    }
    Assert-Cierto ($cfg.datos.documentosVigentes.Count -eq 8) "8 documentos vigentes declarados"
    Assert-Cierto ($cfg.evaluaciones.testSets.Count -eq 3) "3 test sets declarados"

    # El IBAN de demostración tiene que parecer un IBAN o Purview no lo detecta
    Assert-Cierto ($cfg.datos.ibanSintetico -match '^ES\d{22}$') "el IBAN sintético tiene forma de IBAN español"
}

# --- 3. Etapas y scripts de uso ------------------------------------------------
Write-Host "`n[3] Etapas y scripts de uso" -ForegroundColor Cyan
$etapas = @(
    "Stage1-Entornos.ps1", "Stage2-SharePoint.ps1", "Stage3-Purview.ps1", "Stage4-Dataverse.ps1",
    "Stage5-DlpPlataforma.ps1", "Stage6-Agente.ps1", "Stage7-Buzon.ps1", "Stage8-Evaluaciones.ps1"
)
foreach ($e in $etapas) {
    Assert-Cierto (Test-Path -LiteralPath (Join-Path $Raiz "scripts/stages/$e")) "existe $e"
}
foreach ($u in @("Invoke-TraficoAgente.ps1", "Invoke-Evaluaciones.ps1", "Set-RegresionVersionado.ps1", "Send-CorreosDevolucion.ps1")) {
    Assert-Cierto (Test-Path -LiteralPath (Join-Path $Raiz "uso/$u")) "existe uso/$u"
}
foreach ($m in @("Common.psm1", "Dataverse.psm1")) {
    Assert-Cierto (Test-Path -LiteralPath (Join-Path $Raiz "scripts/$m")) "existe scripts/$m"
}
Assert-Cierto (Test-Path -LiteralPath (Join-Path $Raiz "cleanup.ps1")) "existe cleanup.ps1"

# --- 4. Test sets: la cifra que sale en pantalla -------------------------------
Write-Host "`n[4] Test sets" -ForegroundColor Cyan
$seguridad = Join-Path $Raiz "datos/testsets/FS_TestSet_Seguridad.csv"
Assert-Cierto (Test-Path -LiteralPath $seguridad) "existe FS_TestSet_Seguridad.csv"
if (Test-Path -LiteralPath $seguridad) {
    $n = @(Import-Csv -LiteralPath $seguridad -Encoding UTF8).Count
    Assert-Cierto ($n -eq 4) "el test set de seguridad tiene 4 casos (tiene $n)"
}
$documental = Join-Path $Raiz "datos/testsets/FS_TestSet_Documental.csv"
$metrico = Join-Path $Raiz "datos/testsets/FS_TestSet_Metrico_Mixto.csv"
if ((Test-Path -LiteralPath $documental) -and (Test-Path -LiteralPath $metrico)) {
    $total = @(Import-Csv -LiteralPath $documental).Count + @(Import-Csv -LiteralPath $metrico).Count + 4
    Assert-Cierto ($total -eq 20) "los tres test sets suman 20 casos (suman $total)"
}
else {
    Add-Aviso "los test sets documental y métrico se copian de 01_datos en la etapa 8; aquí no están todavía"
}

# --- 5. YAML del agente --------------------------------------------------------
Write-Host "`n[5] Proyecto del agente" -ForegroundColor Cyan
$marcadoresConocidos = @("{{SHAREPOINT_KB}}", "{{AGENTE_NOMBRE}}", "{{AGENTE_SCHEMA}}", "{{PREFIJO}}")
$yamls = Get-ChildItem -LiteralPath (Join-Path $Raiz "agente") -Recurse -Include "*.yaml", "*.yml" -File
Assert-Cierto ($yamls.Count -ge 4) "hay al menos 4 archivos YAML ($($yamls.Count))"
foreach ($y in $yamls) {
    $texto = Get-Content -LiteralPath $y.FullName -Raw -Encoding UTF8
    $rel = $y.FullName.Substring($Raiz.Length).TrimStart('\', '/')
    Assert-Cierto (-not ($texto -match "`t")) "$rel sin tabuladores"
    foreach ($m in [regex]::Matches($texto, "\{\{[A-Z_]+\}\}")) {
        if ($m.Value -notin $marcadoresConocidos) {
            Assert-Cierto $false "$rel usa el marcador desconocido $($m.Value)"
        }
    }
}
$instr = Join-Path $Raiz "agente/instrucciones.md"
Assert-Cierto (Test-Path -LiteralPath $instr) "existe agente/instrucciones.md"
if (Test-Path -LiteralPath $instr) {
    $t = Get-Content -LiteralPath $instr -Raw -Encoding UTF8
    Assert-Cierto ($t -match "REGLA-VERSIONADO-INICIO") "las instrucciones llevan el marcador de inicio de la regla"
    Assert-Cierto ($t -match "REGLA-VERSIONADO-FIN") "las instrucciones llevan el marcador de fin de la regla"
    Assert-Cierto ($t -match "Prioriza siempre la versión VIGENTE") "la regla de versionado está presente y sin aplicar la regresión"
}

# --- 6. Datos de siembra -------------------------------------------------------
Write-Host "`n[6] Datos de siembra" -ForegroundColor Cyan
$correos = Join-Path $Raiz "datos/buzon/correos.json"
Assert-Cierto (Test-Path -LiteralPath $correos) "existe datos/buzon/correos.json"
if (Test-Path -LiteralPath $correos) {
    $lista = Get-Content -LiteralPath $correos -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Cierto ($lista.Count -ge 15) "hay al menos 15 correos ($($lista.Count))"
    $porRemitente = $lista | Group-Object remitente | Sort-Object Count -Descending | Select-Object -First 1
    Assert-Cierto ($porRemitente.Count -ge 3) "hay un patrón anómalo sembrado: $($porRemitente.Name) con $($porRemitente.Count) mensajes"
    $motivos = ($lista | Group-Object motivo).Name | Sort-Object
    Assert-Cierto (($motivos -join ",") -eq "R01,R02,R03,R04") "aparecen los cuatro motivos R01-R04"
}

# --- 7. Agente externo ---------------------------------------------------------
Write-Host "`n[7] Agente externo" -ForegroundColor Cyan
$py = Join-Path $Raiz "agente-externo/fs-triage-devoluciones/src"
foreach ($f in @("agent.py", "buzon.py")) {
    Assert-Cierto (Test-Path -LiteralPath (Join-Path $py $f)) "existe src/$f"
}
$python = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python -ErrorAction SilentlyContinue }
if ($python) {
    foreach ($f in Get-ChildItem -LiteralPath $py -Filter "*.py" -File) {
        & $python.Source -m py_compile $f.FullName 2>&1 | Out-Null
        Assert-Cierto ($LASTEXITCODE -eq 0) "$($f.Name) compila"
    }
}
else {
    Add-Aviso "no hay python en el PATH: no se comprueba la compilación del agente externo"
}
$envEjemplo = Join-Path $Raiz "agente-externo/fs-triage-devoluciones/.env.example"
Assert-Cierto (Test-Path -LiteralPath $envEjemplo) "existe .env.example"
Assert-Cierto (-not (Test-Path -LiteralPath (Join-Path $Raiz "agente-externo/fs-triage-devoluciones/.env"))) ".env NO está en el repositorio"

# --- 8. Higiene ----------------------------------------------------------------
Write-Host "`n[8] Higiene" -ForegroundColor Cyan
Assert-Cierto (-not (Test-Path -LiteralPath (Join-Path $Raiz "config.local.json"))) "config.local.json no está versionado"

# --- Resumen -------------------------------------------------------------------
Write-Host ""
if ($fallos.Count -eq 0) {
    Write-Host "Todo correcto." -ForegroundColor Green
    if ($avisos.Count -gt 0) { Write-Host "$($avisos.Count) aviso(s)." -ForegroundColor Yellow }
    exit 0
}
Write-Host "$($fallos.Count) fallo(s):" -ForegroundColor Red
$fallos | ForEach-Object { Write-Host "  · $_" -ForegroundColor Red }
exit 1
