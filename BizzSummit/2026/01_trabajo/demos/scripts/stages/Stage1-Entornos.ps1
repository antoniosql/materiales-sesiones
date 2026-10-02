#requires -Version 7.0
<#
    Etapa 1 — Entornos.

    El agente de las demos 1-3 vive DELIBERADAMENTE en el entorno Default, sin
    Managed Environment y sin propietario nombrado: ese desorden es el hallazgo
    de la demo 1. Esta etapa no lo endurece; solo lo localiza y lo registra.

    Sí crea el entorno FraSoHome-Plataforma (para la component collection y el
    pipeline del bloque 6) y el grupo de entornos al que apuntará la DLP.
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

# --- Default -----------------------------------------------------------------
$default = Get-AdminPowerAppEnvironment | Where-Object { $_.IsDefault -eq $true } | Select-Object -First 1
if (-not $default) { throw "No se pudo localizar el entorno Default del tenant." }

$estado["defaultEnvironmentId"] = $default.EnvironmentName
$estado["defaultEnvironmentUrl"] = $default.Internal.properties.linkedEnvironmentMetadata.instanceUrl
Write-Paso "Default: $($default.DisplayName) [$($default.EnvironmentName)]" -Nivel Ok
Write-Paso "URL: $($estado['defaultEnvironmentUrl'])" -Nivel Info

$esManaged = $false
try {
    $esManaged = [bool]$default.Internal.properties.governanceConfiguration.protectionLevel -eq "Standard"
}
catch {
    # Un tenant sin gobierno configurado no expone esa propiedad: se asume no gestionado.
    Write-Verbose "No hay governanceConfiguration en el Default: $($_.Exception.Message)"
}
if ($esManaged) {
    Write-Paso "El Default ya es Managed Environment. La demo 1 pierde el contraste: considera usar un tenant limpio." -Nivel Aviso
}
else {
    Write-Paso "El Default NO es Managed Environment. Es lo que la demo 1 necesita enseñar." -Nivel Ok
}

# --- Entorno de plataforma ----------------------------------------------------
$pe = $cfg.powerPlatform.platformEnvironment
$existente = Get-AdminPowerAppEnvironment | Where-Object { $_.DisplayName -eq $pe.displayName } | Select-Object -First 1

if ($existente) {
    Write-Paso "Reutilizo el entorno '$($pe.displayName)' [$($existente.EnvironmentName)]" -Nivel Salta
    $estado["platformEnvironmentId"] = $existente.EnvironmentName
    $estado.propiedad["platformEnvironment"] = $false
}
elseif ($sim) {
    Write-Paso "[simulado] Crearía el entorno '$($pe.displayName)' ($($pe.sku), $($pe.region))" -Nivel Salta
}
else {
    # New-AdminPowerAppEnvironment falla en pwsh 7 ("Cannot process argument
    # transformation on parameter 'Route'"): se crea con pac, que además
    # provisiona Dataverse por defecto.
    $perfilAdmin = "FraSoHome-Admin"
    $perfiles = Invoke-Pac -TolerarError auth list
    if (($perfiles -join "`n") -match [regex]::Escape($perfilAdmin)) {
        Invoke-Pac auth select --name $perfilAdmin | Out-Null
    }
    else {
        Write-Paso "Inicia sesión en Power Platform CLI con la cuenta del tenant" -Nivel Info
        Invoke-Pac auth create --name $perfilAdmin --tenant $cfg.tenant.domain | Out-Null
    }

    Write-Paso "Creando entorno '$($pe.displayName)' (tarda unos minutos)..." -Nivel Info
    Invoke-Pac admin create `
        --name $pe.displayName `
        --region $pe.region `
        --type $pe.sku `
        --currency $pe.currency `
        --language $pe.languageCode | Out-Null

    $nuevo = Get-AdminPowerAppEnvironment | Where-Object { $_.DisplayName -eq $pe.displayName } | Select-Object -First 1
    if (-not $nuevo) { throw "pac creó el entorno pero no aparece en Get-AdminPowerAppEnvironment." }
    $estado["platformEnvironmentId"] = $nuevo.EnvironmentName
    $estado.propiedad["platformEnvironment"] = $true
    Write-Paso "Creado [$($nuevo.EnvironmentName)]" -Nivel Ok
}

# --- Grupo de entornos --------------------------------------------------------
# Los grupos de entornos se administran hoy desde el PPAC o Graph; el módulo de
# administración no expone un cmdlet estable, así que se delega al runbook.
$grupo = $cfg.powerPlatform.environmentGroupName
Add-Runbook -Estado $estado `
    -Titulo "Crear el grupo de entornos '$grupo' y meter el entorno de plataforma" `
    -Motivo "Los environment groups se crean desde el Power Platform Admin Center; no hay cmdlet estable en el módulo de administración." `
    -Comando @"
# Power Platform Admin Center > Manage > Environment groups > New group
#   Nombre: $grupo
#   Añadir: $($pe.displayName)
#   Reglas de grupo: Managed Environments ON, sharing limitado, Settings Enforcer ON
# Deja el entorno Default FUERA del grupo: la demo 1 necesita que siga sin gobernar.
"@

Write-Paso "Etapa 1 completada." -Nivel Ok
