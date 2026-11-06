<#
.SYNOPSIS
    Fab Inspector (antes PBI Inspector) sobre todos los informes PBIR de fabric/.

.DESCRIPTION
    Usa las reglas base de Fab Inspector (fijadas por commit y huella) o, si existe,
    calidad/fab-inspector/reglas.json. Descarga la CLI en .herramientas/ con 'gh'.

    Antes del primer uso: comprobar el nombre del zip de la CLI en
    https://github.com/NatVanG/fab-inspector/releases y fijar su huella en $CliSha256.

.EXAMPLE
    ./scripts/inspeccionar_informes.ps1
#>
$ErrorActionPreference = "Stop"

$CliVersion = "v3.5.0"
$CliPatron = "*CLI*win*.zip"      # VERIFICAR contra los ficheros de la release
$CliSha256 = ""                   # rellenar tras la primera descarga verificada
$ReglasBaseCommit = "cdaaeec3cca8e97b0fd493e080dfa264f9cd44f8"
$ReglasBaseSha256 = "22868be9acd696c96e62f214dbe0efc72fd1bfffda1736b3b9a4d7fba21f883c"

$Raiz = Split-Path -Parent $PSScriptRoot
$Herramientas = Join-Path $Raiz ".herramientas"
New-Item -ItemType Directory -Force $Herramientas | Out-Null

$Informes = Get-ChildItem (Join-Path $Raiz "fabric") -Recurse -Directory -Filter "*.Report"
if (-not $Informes) { Write-Host "No hay informes que inspeccionar."; exit 0 }

# CLI
$CliDir = Join-Path $Herramientas "fab-inspector-$CliVersion"
if (-not (Test-Path $CliDir)) {
    $Descarga = Join-Path $Herramientas "descarga-fab-inspector"
    gh release download $CliVersion --repo NatVanG/fab-inspector --pattern $CliPatron --dir $Descarga --clobber
    $Zip = Get-ChildItem $Descarga -Filter *.zip | Select-Object -First 1
    $Huella = (Get-FileHash $Zip.FullName -Algorithm SHA256).Hash.ToLower()
    if ($CliSha256 -and $Huella -ne $CliSha256) { throw "Huella SHA256 inesperada en $($Zip.Name) ($Huella)" }
    if (-not $CliSha256) { Write-Warning "Fija `$CliSha256 = `"$Huella`" en este script para verificar las próximas descargas." }
    Expand-Archive -Path $Zip.FullName -DestinationPath $CliDir
}
$Cli = Get-ChildItem $CliDir -Recurse -Filter "fab-inspector*.exe" | Select-Object -First 1
if (-not $Cli) { throw "No se encuentra fab-inspector.exe en $CliDir" }

# Reglas: las del proyecto si existen; si no, las base
$Reglas = Join-Path $Raiz "calidad/fab-inspector/reglas.json"
if (-not (Test-Path $Reglas)) {
    $Reglas = Join-Path $Herramientas "Base-rules-$ReglasBaseCommit.json"
    if (-not (Test-Path $Reglas)) {
        Invoke-WebRequest "https://raw.githubusercontent.com/NatVanG/PBI-InspectorV2/$ReglasBaseCommit/Rules/Base-rules.json" -OutFile $Reglas
    }
    if ((Get-FileHash $Reglas -Algorithm SHA256).Hash.ToLower() -ne $ReglasBaseSha256) { throw "Huella inesperada en las reglas base" }
}

$Formato = if ($env:GITHUB_ACTIONS) { "GitHub" } else { "Console,HTML" }
$Salida = Join-Path $Herramientas "resultado-fab-inspector"
& $Cli.FullName -fabricitem (Join-Path $Raiz "fabric/analitica") -rules $Reglas -formats $Formato -output $Salida -overwriteoutput true
if ($LASTEXITCODE -ne 0) { throw "Fab Inspector ha encontrado incumplimientos (código $LASTEXITCODE)" }
Write-Host "Fab Inspector: $($Informes.Count) informe(s) revisado(s). Detalle en $Salida"
