#requires -Version 7.0
<#
    Etapa 5 — DLP de Power Platform y endpoint filtering.

    Es el beat 1 de la demo 2. La política deja el connector de SharePoint en
    el grupo de negocio y le pone una regla de endpoints:

        1. Allow  https://<tenant>.sharepoint.com/sites/FraSoHome-KB-Operaciones
        2. Deny   *

    El sitio de Prevención de Pérdidas no está permitido, así que para el agente
    ese documento no existe. No es que se le niegue: es que no lo ve.
#>
[CmdletBinding()]
param([Parameter(Mandatory)]$Contexto)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "../Common.psm1") -Force

$cfg = $Contexto.Config
$estado = $Contexto.Estado
$sim = $Contexto.Simular

Import-Module Microsoft.PowerApps.Administration.PowerShell -ErrorAction Stop
Add-PowerAppsAccount -Endpoint prod | Out-Null

$nombre = $cfg.powerPlatform.dlpPolicyName
$defaultId = $estado["defaultEnvironmentId"]
if (-not $defaultId) { throw "Falta el id del entorno Default. Ejecuta antes la etapa 1." }

# --- Política -----------------------------------------------------------------
$existente = Get-DlpPolicy -ErrorAction SilentlyContinue |
    Where-Object { $_.displayName -eq $nombre } | Select-Object -First 1

if ($existente) {
    Write-Paso "Reutilizo la política '$nombre' [$($existente.name)]" -Nivel Salta
    $politicaId = $existente.name
    $estado.propiedad["dlpPlataforma"] = $false
}
elseif ($sim) {
    Write-Paso "[simulado] New-DlpPolicy -DisplayName '$nombre' sobre el entorno Default" -Nivel Salta
    $politicaId = "simulado"
}
else {
    $nueva = New-DlpPolicy -DisplayName $nombre -EnvironmentType OnlyEnvironments -Environments @($defaultId)
    $politicaId = $nueva.name
    Write-Paso "Política creada [$politicaId]" -Nivel Ok
    $estado.propiedad["dlpPlataforma"] = $true
}
$estado["dlpPlataformaId"] = $politicaId

# --- Connectors bloqueados: los tres del bloque 4.3 ---------------------------
# Chat sin autenticación de Entra ID, HTTP y HTTP con Entra ID.
$aBloquear = @(
    "Chat sin autenticación de Entra ID"
    "HTTP"
    "HTTP con Entra ID"
)
Write-Paso "Connectors de Copilot Studio que la regla 1 del bloque 4.3 manda bloquear:" -Nivel Aviso
foreach ($c in $aBloquear) { Write-Paso "  · $c" -Nivel Info }
$estado["connectorsABloquear"] = $aBloquear

# --- Endpoint filtering sobre SharePoint --------------------------------------
$sitioPermitido = "$($cfg.sharepoint.rootUrl.TrimEnd('/'))/sites/$($cfg.sharepoint.kbSite.alias)"

$configuraciones = @{
    connectorActionConfigurations = @()
    endpointConfigurations        = @(
        @{
            connectorId   = "/providers/Microsoft.PowerApps/apis/shared_sharepointonline"
            endpointRules = @(
                @{ order = 1; behavior = "Allow"; endpoint = $sitioPermitido }
                @{ order = 2; behavior = "Deny";  endpoint = "*" }
            )
        }
        @{
            connectorId   = "/providers/Microsoft.PowerApps/apis/shared_webcontents"
            endpointRules = @(
                @{ order = 1; behavior = "Deny"; endpoint = "*" }
            )
        }
    )
}

if ($sim) {
    Write-Paso "[simulado] endpoint filtering: Allow $sitioPermitido, Deny *" -Nivel Salta
}
else {
    $yaTiene = Get-PowerAppDlpPolicyConnectorConfigurations -TenantId $cfg.tenant.id -PolicyName $politicaId -ErrorAction SilentlyContinue
    if ($yaTiene) {
        Set-PowerAppDlpPolicyConnectorConfigurations -TenantId $cfg.tenant.id -PolicyName $politicaId `
            -UpdatedConnectorConfigurations $configuraciones | Out-Null
        Write-Paso "Endpoint filtering actualizado" -Nivel Ok
    }
    else {
        New-PowerAppDlpPolicyConnectorConfigurations -TenantId $cfg.tenant.id -PolicyName $politicaId `
            -NewDlpPolicyConnectorConfigurations $configuraciones | Out-Null
        Write-Paso "Endpoint filtering creado" -Nivel Ok
    }
    Write-Paso "Permitido: $sitioPermitido" -Nivel Ok
    Write-Paso "Denegado:  todo lo demás, incluido /sites/$($cfg.sharepoint.restrictedSite.alias)" -Nivel Ok
}

$estado["endpointPermitido"] = $sitioPermitido

Add-Runbook -Estado $estado `
    -Titulo "Comprobar el endpoint filtering en la propia demo" `
    -Motivo "La propagación de políticas de datos no es inmediata y es el mayor riesgo de la demo 2." `
    -Comando @"
# Desde Teams, con la cuenta de $($cfg.personas.storeManager.displayName):
#   "Dame el listado de clientes con devoluciones anómalas de este trimestre"
# Esperado: el agente no encuentra la información y propone escalar a Prevención de Pérdidas.
# Si devuelve contenido de $($cfg.sharepoint.restrictedSite.alias), la política aún no ha propagado.
"@

Write-Paso "Etapa 5 completada." -Nivel Ok
