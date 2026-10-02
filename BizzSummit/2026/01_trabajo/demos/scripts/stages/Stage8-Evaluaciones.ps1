#requires -Version 7.0
<#
    Etapa 8 — Test sets y evaluaciones.

    Deja los 20 casos listos: 10 documentales, 6 métricos y 4 de seguridad.
    Ese es el umbral que la sesión recomienda en el bloque 6.3, así que conviene
    que la cifra que se ve en pantalla sea exactamente 20.

    La API de evaluaciones de Power Platform sigue en preview y su ruta ha
    cambiado más de una vez. Por eso el endpoint está en config.evaluaciones y
    no incrustado aquí: si Microsoft lo mueve, se toca un valor y no el código.
    Si la llamada falla, la etapa no rompe el despliegue: genera runbook.
#>
[CmdletBinding()]
param([Parameter(Mandatory)]$Contexto)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "../Common.psm1") -Force

$cfg = $Contexto.Config
$estado = $Contexto.Estado
$sim = $Contexto.Simular

$destino = Join-Path $Contexto.RaizDemo "datos/testsets"
$origen = Join-Path $Contexto.RaizDatos "01_datos/rag_copilot_studio/test_sets"

# --- Reunir los tres test sets ------------------------------------------------
$total = 0
foreach ($ts in $cfg.evaluaciones.testSets) {
    $local = Join-Path $destino $ts.archivo
    if (-not (Test-Path -LiteralPath $local -PathType Leaf)) {
        $desdeOrigen = Join-Path $origen $ts.archivo
        if (Test-Path -LiteralPath $desdeOrigen -PathType Leaf) {
            Copy-Item -LiteralPath $desdeOrigen -Destination $local -Force
            Write-Paso "Copiado $($ts.archivo) desde 01_datos" -Nivel Ok
        }
        else {
            Write-Paso "No encuentro $($ts.archivo) ni en el pack ni en 01_datos" -Nivel Error
            continue
        }
    }
    $casos = @(Import-Csv -LiteralPath $local -Encoding UTF8)
    $total += $casos.Count
    Write-Paso "$($ts.nombre): $($casos.Count) casos" -Nivel Ok
}

Write-Paso "Total de casos: $total" -Nivel $(if ($total -eq 20) { "Ok" } else { "Aviso" })
if ($total -ne 20) {
    Write-Paso "La sesión dice 20 casos en pantalla. Ajusta los CSV o el guion." -Nivel Aviso
}
$estado["casosEvaluacion"] = $total

# --- Subida por API -----------------------------------------------------------
$envId = $estado["defaultEnvironmentId"]
$apiRoot = $cfg.evaluaciones.apiRoot.Replace("{environmentId}", $envId)

if ($sim) {
    Write-Paso "[simulado] subiría los 3 test sets a $apiRoot" -Nivel Salta
}
else {
    $subidos = 0
    foreach ($ts in $cfg.evaluaciones.testSets) {
        $local = Join-Path $destino $ts.archivo
        if (-not (Test-Path -LiteralPath $local)) { continue }
        try {
            $token = (az account get-access-token --resource "https://api.powerplatform.com" --output json | ConvertFrom-Json).accessToken
            $casos = Import-Csv -LiteralPath $local -Encoding UTF8 | ForEach-Object {
                @{ input = $_.Question; expectedResponse = $_."Expected response" }
            }
            $cuerpo = @{ name = $ts.nombre; testCases = @($casos) } | ConvertTo-Json -Depth 8
            Invoke-RestMethod -Method POST `
                -Uri "$apiRoot/testSets?api-version=$($cfg.evaluaciones.apiVersion)" `
                -Headers @{ Authorization = "Bearer $token" } `
                -ContentType "application/json; charset=utf-8" -Body $cuerpo -ErrorAction Stop | Out-Null
            Write-Paso "Subido $($ts.nombre)" -Nivel Ok
            $subidos++
        }
        catch {
            Write-Paso "La API rechazó $($ts.nombre): $($_.Exception.Message)" -Nivel Aviso
        }
    }
    if ($subidos -lt $cfg.evaluaciones.testSets.Count) {
        Add-Runbook -Estado $estado `
            -Titulo "Importar los test sets desde la interfaz de Copilot Studio" `
            -Motivo "La API de evaluaciones está en preview y rechazó al menos una subida." `
            -Comando @"
# Copilot Studio > $($cfg.agente.displayName) > Evaluation > New evaluation
#   Import test cases from a file, y arrastra cada CSV de:
#   $destino
#   Nombres: FS_Documental_v1, FS_MetricoMixto_v1, FS_Seguridad_v1
#   Métodos: Keyword match + Text similarity (documental y seguridad)
#            + Capability use en el métrico, esperando DV_ListSalesSummary y DV_ListReturns
"@
    }
}

# --- Línea base ---------------------------------------------------------------
Add-Runbook -Estado $estado `
    -Titulo "Ejecutar los 20 casos y guardar la línea base EN VERDE" `
    -Motivo "La demo 3 solo funciona si antes existe una ejecución con los 20 casos en verde." `
    -Comando @"
pwsh ./uso/Invoke-Evaluaciones.ps1 -ConfigPath '$($cfg._configPath)' -GuardarLineaBase
# Después, el 1 de octubre y no antes:
pwsh ./uso/Set-RegresionVersionado.ps1 -ConfigPath '$($cfg._configPath)' -Aplicar
# Y vuelve a ejecutar: deben salir 19 verde / 1 rojo, con 45 dias -> 30 dias.
"@

Write-Paso "Etapa 8 completada." -Nivel Ok
