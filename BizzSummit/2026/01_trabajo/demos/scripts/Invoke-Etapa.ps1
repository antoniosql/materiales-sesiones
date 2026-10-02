#requires -Version 7.0
<#
    Ejecuta UNA etapa en un proceso pwsh propio. deploy.ps1 lo lanza por etapa.

    Motivo: Microsoft.Graph, ExchangeOnlineManagement y
    Microsoft.PowerApps.Administration.PowerShell traen cada uno su versión de
    Microsoft.Identity.Client (MSAL). En un mismo proceso solo se carga la
    primera y los demás fallan con "Assembly with same name is already loaded".

    El estado se comparte por disco: se lee al empezar y se guarda al terminar,
    también si la etapa falla, para no perder lo que ya se hizo.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ConfigPath,
    [Parameter(Mandatory)][string]$EstadoPath,
    [Parameter(Mandatory)][string]$Script,
    [switch]$Simular
)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "Common.psm1") -Force

$config = Get-DemoConfig -ConfigPath $ConfigPath
$estado = Get-EstadoDespliegue -EstadoPath $EstadoPath

$contexto = [pscustomobject]@{
    Config    = $config
    Estado    = $estado
    RaizDatos = Resolve-RutaDemo -Config $config -Ruta $config.datos.raizFraSoHome
    RaizDemo  = Split-Path -Parent $PSScriptRoot
    Simular   = [bool]$Simular
}

try {
    & $Script -Contexto $contexto
}
finally {
    Save-EstadoDespliegue -Estado $estado -EstadoPath $EstadoPath
}
