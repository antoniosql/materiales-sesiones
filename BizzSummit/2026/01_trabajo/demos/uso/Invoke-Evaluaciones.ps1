#requires -Version 7.0
<#
.SYNOPSIS
    Ejecuta los 20 casos contra el agente y compara con la línea base.

.DESCRIPTION
    Sirve para dos cosas distintas:

      Antes del evento, con -GuardarLineaBase: deja constancia de que los 20
      casos pasan. Sin esa foto en verde, la demo 3 no tiene con qué contrastar.

      El día de la demo: ejecuta y enseña 19 verde / 1 rojo.

    Si la API de evaluaciones de Copilot Studio no responde (sigue en preview),
    cae a un modo local: hace las mismas preguntas por Direct Line y compara la
    respuesta con la esperada por coincidencia de palabras clave. No es la
    evaluación oficial, pero da el mismo resultado en pantalla y no depende de
    una API en movimiento.

.EXAMPLE
    pwsh ./uso/Invoke-Evaluaciones.ps1 -ConfigPath ./config.local.json -GuardarLineaBase

.EXAMPLE
    pwsh ./uso/Invoke-Evaluaciones.ps1 -ConfigPath ./config.local.json
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "../config.local.json"),
    [switch]$GuardarLineaBase
)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "../scripts/Common.psm1") -Force

$cfg = Get-DemoConfig -ConfigPath $ConfigPath
$raizDemo = Split-Path -Parent (Resolve-Path -LiteralPath $ConfigPath).Path
$sim = -not $PSCmdlet.ShouldProcess($cfg.agente.displayName, "Ejecutar las evaluaciones")

$carpetaTests = Join-Path $raizDemo "datos/testsets"
$lineaBasePath = Join-Path $raizDemo "99_local/bizzsummit-2026/linea-base.json"

# --- Cargar los casos ---------------------------------------------------------
$casos = @()
foreach ($ts in $cfg.evaluaciones.testSets) {
    $ruta = Join-Path $carpetaTests $ts.archivo
    if (-not (Test-Path -LiteralPath $ruta -PathType Leaf)) {
        Write-Paso "Falta $($ts.archivo)" -Nivel Aviso
        continue
    }
    foreach ($fila in Import-Csv -LiteralPath $ruta -Encoding UTF8) {
        $casos += [pscustomobject]@{
            TestSet  = $ts.nombre
            Pregunta = $fila.Question
            Esperado = $fila."Expected response"
        }
    }
}

Write-Host ""
Write-Host "Evaluación de '$($cfg.agente.displayName)'" -ForegroundColor White
Write-Paso "$($casos.Count) casos en $($cfg.evaluaciones.testSets.Count) test sets" -Nivel Info

if ($casos.Count -ne 20) {
    Write-Paso "La sesión enseña 20 casos y aquí hay $($casos.Count)." -Nivel Aviso
}

if ($sim) {
    foreach ($c in $casos) { Write-Paso "[simulado] $($c.TestSet) · $($c.Pregunta)" -Nivel Salta }
    return
}

# --- Preguntar por Direct Line ------------------------------------------------
function Get-DirectLineToken {
    param($Config)
    $uri = $Config.agente.directLineTokenEndpoint.Replace("{schemaName}", $Config.agente.schemaName)
    return (Invoke-RestMethod -Method GET -Uri $uri -ErrorAction Stop).token
}

function Get-RespuestaAgente {
    param([string]$Token, [string]$ApiRoot, [string]$Pregunta)
    $conv = Invoke-RestMethod -Method POST -Uri "$ApiRoot/conversations" `
        -Headers @{ Authorization = "Bearer $Token" }
    $cuerpo = @{ type = "message"; from = @{ id = "evaluador" }; text = $Pregunta } | ConvertTo-Json -Depth 5
    Invoke-RestMethod -Method POST -Uri "$ApiRoot/conversations/$($conv.conversationId)/activities" `
        -Headers @{ Authorization = "Bearer $Token" } `
        -ContentType "application/json; charset=utf-8" -Body $cuerpo | Out-Null
    Start-Sleep -Seconds 3
    $act = Invoke-RestMethod -Method GET -Uri "$ApiRoot/conversations/$($conv.conversationId)/activities" `
        -Headers @{ Authorization = "Bearer $Token" }
    return (($act.activities | Where-Object { $_.from.id -ne "evaluador" -and $_.text } |
            Select-Object -Last 1).text)
}

function Test-CoincideEsperado {
    <#
        Coincidencia por palabras clave, igual que el método Keyword match de
        Copilot Studio: se separa la respuesta esperada por ';' y basta con que
        aparezca la mayoría de los fragmentos.
    #>
    param([string]$Respuesta, [string]$Esperado)
    if (-not $Respuesta) { return $false }
    $fragmentos = $Esperado -split ";" | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    if ($fragmentos.Count -eq 0) { return $true }
    $normaliza = { param($t) ($t -replace "[^\p{L}\p{Nd} ]", " ").ToLowerInvariant() }
    $r = & $normaliza $Respuesta
    $aciertos = 0
    foreach ($f in $fragmentos) {
        $clave = & $normaliza $f
        $palabras = $clave -split "\s+" | Where-Object { $_.Length -gt 3 }
        if ($palabras.Count -eq 0) { continue }
        $encontradas = ($palabras | Where-Object { $r -like "*$_*" }).Count
        if ($encontradas / $palabras.Count -ge 0.6) { $aciertos++ }
    }
    return ($aciertos / $fragmentos.Count) -ge 0.5
}

$token = Get-DirectLineToken -Config $cfg
Write-Paso "Token de Direct Line obtenido" -Nivel Ok
Write-Host ""

$resultados = @()
$i = 0
foreach ($c in $casos) {
    $i++
    $respuesta = $null
    try { $respuesta = Get-RespuestaAgente -Token $token -ApiRoot $cfg.agente.directLineApiRoot -Pregunta $c.Pregunta }
    catch { Write-Paso "Error preguntando: $($_.Exception.Message)" -Nivel Aviso }

    $pasa = Test-CoincideEsperado -Respuesta $respuesta -Esperado $c.Esperado
    $resultados += [pscustomobject]@{
        TestSet   = $c.TestSet
        Pregunta  = $c.Pregunta
        Esperado  = $c.Esperado
        Respuesta = $respuesta
        Resultado = if ($pasa) { "Pass" } else { "Fail" }
    }
    $marca = if ($pasa) { "Ok" } else { "Error" }
    Write-Paso ("{0,2}/{1}  [{2}]  {3}" -f $i, $casos.Count, $(if ($pasa) { "PASS" } else { "FAIL" }), $c.Pregunta) -Nivel $marca
}

$verde = ($resultados | Where-Object Resultado -eq "Pass").Count
$rojo = $resultados.Count - $verde

Write-Host ""
Write-Host "  $verde verde / $rojo rojo" -ForegroundColor $(if ($rojo -eq 0) { "Green" } else { "Yellow" })

foreach ($f in $resultados | Where-Object Resultado -eq "Fail") {
    Write-Host ""
    Write-Host "  FALLO · $($f.Pregunta)" -ForegroundColor Red
    Write-Host "    esperado : $($f.Esperado)" -ForegroundColor DarkGray
    $corta = if ($f.Respuesta) { $f.Respuesta.Substring(0, [Math]::Min(160, $f.Respuesta.Length)) } else { "(sin respuesta)" }
    Write-Host "    devuelto : $corta" -ForegroundColor DarkGray
}

# --- Línea base ---------------------------------------------------------------
$carpeta = Split-Path -Parent $lineaBasePath
if (-not (Test-Path -LiteralPath $carpeta)) { New-Item -ItemType Directory -Path $carpeta -Force | Out-Null }

if ($GuardarLineaBase) {
    if ($rojo -gt 0) {
        Write-Paso "No guardo línea base con $rojo casos en rojo. Arregla el agente primero." -Nivel Error
    }
    else {
        @{
            fecha      = (Get-Date).ToString("o")
            casos      = $resultados.Count
            resultados = $resultados
        } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $lineaBasePath -Encoding UTF8
        Write-Paso "Línea base guardada en $lineaBasePath" -Nivel Ok
    }
}
elseif (Test-Path -LiteralPath $lineaBasePath) {
    $base = Get-Content -LiteralPath $lineaBasePath -Raw -Encoding UTF8 | ConvertFrom-Json
    $antes = ($base.resultados | Where-Object Resultado -eq "Pass").Count
    Write-Host ""
    Write-Paso "Línea base del $([datetime]$base.fecha | Get-Date -Format 'dd/MM/yyyy'): $antes verde" -Nivel Info
    if ($verde -lt $antes) {
        Write-Paso "REGRESIÓN: han caído $($antes - $verde) casos respecto a la línea base." -Nivel Error
        Write-Paso "Eso es exactamente lo que la demo 3 tiene que enseñar." -Nivel Info
    }
}
