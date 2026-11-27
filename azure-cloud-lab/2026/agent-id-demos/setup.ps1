<#
.SYNOPSIS
  Prepara el entorno de las demos de Entra Agent ID: entorno virtual de Python, dependencias, .env y Git.

.DESCRIPTION
  1. Comprueba Python 3.10+ y crea .venv en la raíz del repositorio.
  2. Instala el CLI `agentid` en modo editable con los extras de Foundry y de pruebas.
  3. Crea .env a partir de .env.example y .vscode a partir de config\vscode si no existen.
  4. Inicializa el repositorio Git con un primer commit si todavía no lo es (-SinGit para saltarlo).
  5. Comprueba Azure CLI, Bicep y Azure Developer CLI.
  6. Ejecuta las pruebas sin red (-SinPruebas para saltarlas).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\setup.ps1
#>
param(
    [switch]$SinPruebas,
    [switch]$SinGit
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

function Paso($texto) { Write-Host "`n▶ $texto" -ForegroundColor Cyan }
function Ok($texto)   { Write-Host "  ✔ $texto" -ForegroundColor Green }
function Aviso($texto){ Write-Host "  ⚠ $texto" -ForegroundColor Yellow }

# --- 1 · Python -----------------------------------------------------------------------------
Paso 'Python 3.10 o superior'
if (Get-Command py -ErrorAction SilentlyContinue) { $pyExe = 'py'; $pyArgs = @('-3') }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $pyExe = 'python'; $pyArgs = @() }
else { throw 'No encuentro Python. Instálalo con: winget install Python.Python.3.12' }
& $pyExe @pyArgs -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if ($LASTEXITCODE -ne 0) { throw 'Hace falta Python 3.10 o superior.' }
Ok (& $pyExe @pyArgs --version)

# --- 2 · Entorno virtual y dependencias -----------------------------------------------------
Paso 'Entorno virtual .venv'
if (-not (Test-Path '.venv')) { & $pyExe @pyArgs -m venv .venv; Ok 'creado' } else { Ok 'ya existía' }
$venvPy = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'

Paso 'Dependencias (agentid + Foundry + pruebas)'
& $venvPy -m pip install --upgrade pip --quiet
& $venvPy -m pip install -e '.[foundry,dev]' --quiet
if ($LASTEXITCODE -ne 0) { throw 'pip install ha fallado.' }
Ok 'instaladas'

# --- 3 · Variables de entorno ---------------------------------------------------------------
Paso 'Fichero .env'
if (-not (Test-Path '.env')) { Copy-Item '.env.example' '.env'; Ok '.env creado desde .env.example' }
else { Ok '.env ya existe (no se toca)' }
$pendientes = Get-Content '.env' | Where-Object { $_ -match '^(TENANT_ID|SUBSCRIPTION_ID|NAME_SUFFIX)=\s*$' }
if ($pendientes) { Aviso ("Rellena en .env: " + (($pendientes | ForEach-Object { $_.TrimEnd('=') }) -join ', ')) }

# --- 3b · VS Code -----------------------------------------------------------------------------
Paso 'Configuración de VS Code'
if (-not (Test-Path '.vscode')) {
    New-Item -ItemType Directory '.vscode' | Out-Null
    Copy-Item 'config\vscode\*.json' '.vscode\'
    Ok '.vscode creado (intérprete .venv, .env y pytest)'
} else { Ok '.vscode ya existe (no se toca)' }

# --- 4 · Git ------------------------------------------------------------------------------------
if (-not $SinGit) {
    Paso 'Repositorio Git'
    if (Test-Path '.git') { Ok 'ya es un repositorio' }
    elseif (Get-Command git -ErrorAction SilentlyContinue) {
        git init -b main | Out-Null
        git add . | Out-Null
        git commit -m 'Demos de Entra Agent ID · Azure Cloud Lab 2026 (FraSoHome)' | Out-Null
        if ($LASTEXITCODE -eq 0) { Ok 'inicializado con un primer commit en main' }
        else { Aviso 'git init hecho, pero el commit ha fallado (¿user.name/user.email sin configurar?)' }
    }
    else { Aviso 'Git no está instalado: winget install Git.Git' }
}

# --- 5 · Herramientas de Azure ----------------------------------------------------------------
Paso 'Herramientas de Azure'
if (Get-Command az -ErrorAction SilentlyContinue) {
    Ok ("Azure CLI " + (az version 2>$null | ConvertFrom-Json).'azure-cli')
    az bicep version 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { Ok 'Bicep' } else { Aviso 'Bicep no instalado: az bicep install' }
} else { Aviso 'Azure CLI no instalada: winget install Microsoft.AzureCLI' }
if (Get-Command azd -ErrorAction SilentlyContinue) { Ok 'Azure Developer CLI' }
else { Aviso 'azd no instalado (solo para la conexión MCP de Foundry): winget install Microsoft.Azd' }

# --- 6 · Pruebas ------------------------------------------------------------------------------------
if (-not $SinPruebas) {
    Paso 'Pruebas sin red'
    & $venvPy -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Las pruebas han fallado.' }
}

Write-Host "`nListo. Siguientes pasos:" -ForegroundColor Cyan
Write-Host '  .\.venv\Scripts\Activate.ps1'
Write-Host '  notepad .env                  # TENANT_ID, SUBSCRIPTION_ID, NAME_SUFFIX…'
Write-Host '  az login --tenant <TENANT_ID>'
Write-Host '  agentid check'
Write-Host '  agentid desplegar'
