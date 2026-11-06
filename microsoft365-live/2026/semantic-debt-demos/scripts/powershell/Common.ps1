# Funciones comunes: lectura de .env y del estado compartido con Python.
$ErrorActionPreference = 'Stop'

$script:RepoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..')

function Import-DotEnv {
    param([string]$Path = (Join-Path $script:RepoRoot '.env'))
    if (-not (Test-Path $Path)) { throw "No encuentro $Path. Copia .env.example a .env." }
    foreach ($line in Get-Content -Path $Path -Encoding UTF8) {
        $t = $line.Trim()
        if (-not $t -or $t.StartsWith('#') -or -not $t.Contains('=')) { continue }
        $k, $v = $t.Split('=', 2)
        $v = $v.Trim().Trim('"').Trim("'")
        if (-not [Environment]::GetEnvironmentVariable($k.Trim())) {
            [Environment]::SetEnvironmentVariable($k.Trim(), $v)
        }
    }
}

function Get-Env {
    param([Parameter(Mandatory)][string]$Name, [string]$Default = $null, [switch]$Required)
    $v = [Environment]::GetEnvironmentVariable($Name)
    if (-not $v) { $v = $Default }
    if ($Required -and -not $v) { throw "Falta $Name en .env" }
    return $v
}

function Get-StateDir {
    $d = Get-Env STATE_DIR 'state'
    if (-not [IO.Path]::IsPathRooted($d)) { $d = Join-Path $script:RepoRoot $d }
    New-Item -ItemType Directory -Force -Path $d | Out-Null
    return $d
}

function Read-JsonFile([string]$Path) {
    if (Test-Path $Path) { return Get-Content $Path -Raw -Encoding UTF8 | ConvertFrom-Json }
    return $null
}

function Write-JsonFile([string]$Path, $Object) {
    $Object | ConvertTo-Json -Depth 10 | Set-Content -Path $Path -Encoding UTF8
}

function Assert-Module([string]$Name, [string]$Hint) {
    if (-not (Get-Module -ListAvailable -Name $Name)) {
        throw "Falta el módulo $Name. Instálalo con: Install-Module $Name -Scope CurrentUser  $Hint"
    }
    Import-Module $Name -ErrorAction Stop
}

function Get-DeployedResource([string]$Type, [string]$Key) {
    $state = Read-JsonFile (Join-Path (Get-StateDir) 'deployed.json')
    if (-not $state) { return $null }
    return $state.resources | Where-Object { $_.type -eq $Type -and $_.key -eq $Key } | Select-Object -First 1
}

function Connect-PnPWithEnv([string]$Url) {
    Assert-Module 'PnP.PowerShell' ''
    $clientId = Get-Env CLIENT_ID -Required
    $tenant = Get-Env TENANT_DOMAIN -Required
    $pfx = Get-Env CERT_PFX_PATH
    $thumb = Get-Env CERT_THUMBPRINT
    if ($pfx) {
        $pfxPwd = Get-Env CERT_PFX_PASSWORD
        $sec = if ($pfxPwd) { ConvertTo-SecureString $pfxPwd -AsPlainText -Force } else { $null }
        Connect-PnPOnline -Url $Url -ClientId $clientId -Tenant $tenant -CertificatePath $pfx -CertificatePassword $sec
    } elseif ($thumb -and $env:OS -eq 'Windows_NT') {
        Connect-PnPOnline -Url $Url -ClientId $clientId -Tenant $tenant -Thumbprint $thumb
    } else {
        Connect-PnPOnline -Url $Url -ClientId $clientId -Interactive
    }
}
