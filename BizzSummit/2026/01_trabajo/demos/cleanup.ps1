#requires -Version 7.0
<#
.SYNOPSIS
    Deshace el despliegue de las demos. Solo borra lo que creó el propio despliegue.

.DESCRIPTION
    Lee el archivo de estado y elimina únicamente los objetos marcados como
    propios. Lo que se reutilizó de un despliegue anterior se conserva salvo
    que se pida -EliminarReutilizados.

    El entorno Default NUNCA se toca. Lo que se creó dentro de él (tablas de
    Dataverse, agente, política de datos) sí.

.EXAMPLE
    pwsh ./cleanup.ps1 -ConfigPath ./config.local.json -WhatIf

.EXAMPLE
    pwsh ./cleanup.ps1 -ConfigPath ./config.local.json -EliminarEntornoPlataforma
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = "High")]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.local.json"),
    [switch]$EliminarReutilizados,
    [switch]$EliminarEntornoPlataforma,
    [switch]$ConservarEstado
)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "scripts/Common.psm1") -Force

$cfg = Get-DemoConfig -ConfigPath $ConfigPath
$estadoPath = Resolve-RutaDemo -Config $cfg -Ruta $cfg.despliegue.estadoPath

if (-not (Test-Path -LiteralPath $estadoPath -PathType Leaf)) {
    throw "No hay estado de despliegue en $estadoPath. Nada que limpiar."
}
$estado = Get-EstadoDespliegue -EstadoPath $estadoPath

Write-Host ""
Write-Host "Limpieza del despliegue en $($estado['tenant'])" -ForegroundColor White
Write-Paso "Estado: $estadoPath" -Nivel Info

function Test-EsPropio {
    param([string]$Clave)
    if (-not $estado.ContainsKey("propiedad")) { return $false }
    if (-not $estado.propiedad.ContainsKey($Clave)) { return $false }
    if ([bool]$estado.propiedad[$Clave]) { return $true }
    if ($EliminarReutilizados) { return $true }
    Write-Paso "Conservado por reutilizado: $Clave" -Nivel Salta
    return $false
}

# --- 1. Agente ----------------------------------------------------------------
if ((Test-EsPropio -Clave "agente") -and $estado["botId"]) {
    if ($PSCmdlet.ShouldProcess("Agente $($cfg.agente.displayName)", "Eliminar")) {
        Invoke-Pac -TolerarError copilot delete --bot $estado["botId"] `
            --environment $estado["defaultEnvironmentUrl"] --confirm | Out-Null
        Write-Paso "Agente eliminado" -Nivel Ok
    }
}

# --- 2. Tablas de Dataverse ---------------------------------------------------
if (Test-EsPropio -Clave "dataverseTablas") {
    Import-Module (Join-Path $PSScriptRoot "scripts/Dataverse.psm1") -Force
    $envUrl = $estado["defaultEnvironmentUrl"]
    if ($envUrl -and $PSCmdlet.ShouldProcess("Tablas de Dataverse", "Eliminar")) {
        $token = Get-DataverseToken -EnvironmentUrl $envUrl
        foreach ($nombre in @($estado["dataverseTablas"])) {
            $logica = ConvertTo-NombreLogico -Texto $nombre -Prefijo $cfg.powerPlatform.publisherPrefix
            try {
                Invoke-DataverseApi -EnvironmentUrl $envUrl -Token $token -Metodo DELETE `
                    -Ruta "EntityDefinitions(LogicalName='$logica')" | Out-Null
                Write-Paso "Tabla $logica eliminada" -Nivel Ok
            }
            catch {
                Write-Paso "No se pudo eliminar $logica : $($_.Exception.Message)" -Nivel Aviso
            }
        }
    }
}

# --- 3. DLP de Power Platform -------------------------------------------------
if ((Test-EsPropio -Clave "dlpPlataforma") -and $estado["dlpPlataformaId"]) {
    Import-Module Microsoft.PowerApps.Administration.PowerShell -ErrorAction Stop
    Add-PowerAppsAccount -Endpoint prod | Out-Null
    if ($PSCmdlet.ShouldProcess("Política DLP $($cfg.powerPlatform.dlpPolicyName)", "Eliminar")) {
        Remove-DlpPolicy -PolicyName $estado["dlpPlataformaId"] | Out-Null
        Write-Paso "Política de datos eliminada" -Nivel Ok
    }
}

# --- 4. Purview ---------------------------------------------------------------
if ((Test-EsPropio -Clave "dlpPolicy") -or (Test-EsPropio -Clave "label")) {
    Import-Module ExchangeOnlineManagement -ErrorAction Stop
    try {
        Connect-IPPSSession -ShowBanner:$false
        if ((Test-EsPropio -Clave "dlpRule") -and $PSCmdlet.ShouldProcess($cfg.purview.dlpRuleName, "Eliminar regla DLP")) {
            Remove-DlpComplianceRule -Identity $cfg.purview.dlpRuleName -Confirm:$false
            Write-Paso "Regla DLP eliminada" -Nivel Ok
        }
        if ((Test-EsPropio -Clave "dlpPolicy") -and $PSCmdlet.ShouldProcess($cfg.purview.dlpPolicyName, "Eliminar política DLP")) {
            Remove-DlpCompliancePolicy -Identity $cfg.purview.dlpPolicyName -Confirm:$false
            Write-Paso "Política DLP eliminada" -Nivel Ok
        }
        if ((Test-EsPropio -Clave "labelPolicy") -and $PSCmdlet.ShouldProcess($cfg.purview.labelPolicyName, "Eliminar política de etiquetas")) {
            Remove-LabelPolicy -Identity $cfg.purview.labelPolicyName -Confirm:$false
            Write-Paso "Política de publicación eliminada" -Nivel Ok
        }
        if ((Test-EsPropio -Clave "label") -and $PSCmdlet.ShouldProcess($cfg.purview.labelDisplayName, "Eliminar etiqueta")) {
            Remove-Label -Identity $cfg.purview.labelName -Confirm:$false
            Write-Paso "Etiqueta eliminada" -Nivel Ok
        }
    }
    catch {
        Write-Paso "Purview no se pudo limpiar automáticamente: $($_.Exception.Message)" -Nivel Aviso
        Write-Paso "Bórralo desde el portal de cumplimiento." -Nivel Info
    }
}

# --- 5. Buzón -----------------------------------------------------------------
if (Test-EsPropio -Clave "buzon") {
    Import-Module ExchangeOnlineManagement -ErrorAction Stop
    try {
        Connect-ExchangeOnline -ShowBanner:$false
        if ($PSCmdlet.ShouldProcess($cfg.exchange.sharedMailbox, "Eliminar buzón compartido")) {
            Remove-Mailbox -Identity $cfg.exchange.sharedMailbox -Confirm:$false
            Write-Paso "Buzón eliminado" -Nivel Ok
        }
    }
    catch {
        Write-Paso "El buzón no se pudo eliminar: $($_.Exception.Message)" -Nivel Aviso
    }
}

# --- 6. Entorno de plataforma -------------------------------------------------
if ($EliminarEntornoPlataforma -and (Test-EsPropio -Clave "platformEnvironment")) {
    Import-Module Microsoft.PowerApps.Administration.PowerShell -ErrorAction Stop
    Add-PowerAppsAccount -Endpoint prod | Out-Null
    if ($PSCmdlet.ShouldProcess($cfg.powerPlatform.platformEnvironment.displayName, "Eliminar entorno")) {
        Remove-AdminPowerAppEnvironment -EnvironmentName $estado["platformEnvironmentId"] | Out-Null
        Write-Paso "Entorno de plataforma eliminado" -Nivel Ok
    }
}
elseif ($estado["platformEnvironmentId"]) {
    Write-Paso "Entorno de plataforma conservado. Usa -EliminarEntornoPlataforma para borrarlo." -Nivel Info
}

# --- 7. Los sitios de SharePoint NO se borran ---------------------------------
Write-Paso "Los sitios de SharePoint se conservan: bórralos a mano si de verdad quieres." -Nivel Info
Write-Paso "  $($cfg.sharepoint.rootUrl)/sites/$($cfg.sharepoint.kbSite.alias)" -Nivel Info
Write-Paso "  $($cfg.sharepoint.rootUrl)/sites/$($cfg.sharepoint.restrictedSite.alias)" -Nivel Info

# --- Estado -------------------------------------------------------------------
if (-not $ConservarEstado -and $PSCmdlet.ShouldProcess($estadoPath, "Eliminar estado local")) {
    Remove-Item -LiteralPath $estadoPath -Force
    Write-Paso "Estado local eliminado" -Nivel Ok
}

Write-Host ""
Write-Host "Limpieza terminada." -ForegroundColor Green
