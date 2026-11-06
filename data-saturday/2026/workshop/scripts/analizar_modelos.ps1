<#
.SYNOPSIS
    Best Practice Analyzer (Tabular Editor 2) sobre todos los modelos semánticos de fabric/.

.DESCRIPTION
    Aplica las reglas de Microsoft (fijadas por commit y huella) más las del proyecto
    (calidad/bpa/reglas-proyecto.json). Falla si hay alguna regla de severidad 3.
    Descarga lo que necesita en .herramientas/ (ignorado por Git); no requiere instalar nada.

    Requisitos: Windows (Tabular Editor 2 es una aplicación .NET Framework).
    Tabular Editor 2 lee modelos en formato TMDL (carpeta definition/).

.EXAMPLE
    ./scripts/analizar_modelos.ps1
#>
$ErrorActionPreference = "Stop"

$TeVersion = "2.29.0"
$TeSha256 = "c0d3a7abda4572baaf3aeedf9cb342ce7ad4d9840e6438d6b13df02267d308a4"
$ReglasMsCommit = "d3ccb5032c9029b097276b88412f7b61df6e73b8"
$ReglasMsSha256 = "ddb9cff4c2a0611a6467e2559d38319d9867381998066473ffa1e11c2d360392"

$Raiz = Split-Path -Parent $PSScriptRoot
$Herramientas = Join-Path $Raiz ".herramientas"
New-Item -ItemType Directory -Force $Herramientas | Out-Null

function Get-Verificado([string]$Url, [string]$Destino, [string]$Sha256) {
    if (-not (Test-Path $Destino)) { Invoke-WebRequest -Uri $Url -OutFile $Destino }
    $Huella = (Get-FileHash $Destino -Algorithm SHA256).Hash.ToLower()
    if ($Huella -ne $Sha256) {
        Remove-Item $Destino
        throw "Huella SHA256 inesperada en $Url ($Huella). No se ejecuta un binario no verificado."
    }
}

$Zip = Join-Path $Herramientas "TabularEditor-$TeVersion.zip"
Get-Verificado "https://github.com/TabularEditor/TabularEditor/releases/download/$TeVersion/TabularEditor.Portable.zip" $Zip $TeSha256
$TeDir = Join-Path $Herramientas "TabularEditor-$TeVersion"
if (-not (Test-Path $TeDir)) { Expand-Archive -Path $Zip -DestinationPath $TeDir }
$Te = Join-Path $TeDir "TabularEditor.exe"

$ReglasMs = Join-Path $Herramientas "BPARules-$ReglasMsCommit.json"
Get-Verificado "https://raw.githubusercontent.com/microsoft/Analysis-Services/$ReglasMsCommit/BestPracticeRules/BPARules.json" $ReglasMs $ReglasMsSha256

# Reglas de Microsoft + reglas del proyecto en un único fichero
$Reglas = @(Get-Content $ReglasMs -Raw | ConvertFrom-Json) +
          @(Get-Content (Join-Path $Raiz "calidad/bpa/reglas-proyecto.json") -Raw | ConvertFrom-Json)
$ReglasCombinadas = Join-Path $Herramientas "reglas-bpa.json"
ConvertTo-Json -InputObject $Reglas -Depth 10 | Set-Content $ReglasCombinadas -Encoding utf8

$Modelos = Get-ChildItem (Join-Path $Raiz "fabric") -Recurse -Directory -Filter "*.SemanticModel"
if (-not $Modelos) { Write-Host "No hay modelos semánticos que analizar."; exit 0 }

$Fallidos = @()
foreach ($Modelo in $Modelos) {
    Write-Host "→ $($Modelo.Name)"
    $Argumentos = @("`"$(Join-Path $Modelo.FullName 'definition')`"", "-A", "`"$ReglasCombinadas`"")
    if ($env:GITHUB_ACTIONS) { $Argumentos += "-G" }  # anotaciones en el PR
    # TabularEditor.exe es una aplicación de ventanas: Start-Process -Wait para esperar y leer el código de salida
    $Proceso = Start-Process -FilePath $Te -ArgumentList $Argumentos -Wait -NoNewWindow -PassThru
    if ($Proceso.ExitCode -ne 0) { $Fallidos += $Modelo.Name }
}

if ($Fallidos) { throw "Best Practice Analyzer con errores en: $($Fallidos -join ', ')" }
Write-Host "Best Practice Analyzer: sin errores en $($Modelos.Count) modelo(s)."
