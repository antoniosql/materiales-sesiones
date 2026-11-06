<#
.SYNOPSIS
  Crea las etiquetas de sensibilidad de la demo y una directiva que las publica a Laura, Paco y la admin.

.DESCRIPTION
  - «Altamente confidencial – Finanzas»: cifrado; solo el grupo FS-Finanzas tiene derechos (incluido EXTRACT).
    Laura no los tiene, así que Copilot no puede usar el documento para ella (demo 2).
  - «Interno – Definiciones oficiales»: sin cifrado (demo 4).
  Escribe state/labels.json con los GUID para que Python aplique las etiquetas.
  Lo que ya existía se reutiliza y Remove-Labels.ps1 no lo borra.

  Las etiquetas tardan hasta 24 h en estar disponibles en todas las apps: ejecútalo con margen.
  Requiere ExchangeOnlineManagement y que el etiquetado de ficheros de Office en SharePoint esté habilitado
  (Set-SPOTenant -EnableAIPIntegration $true).
#>
[CmdletBinding()]
param([string]$EnvFile)

. "$PSScriptRoot/Common.ps1"
if ($EnvFile) { Import-DotEnv $EnvFile } else { Import-DotEnv }
Assert-Module 'ExchangeOnlineManagement' ''

$tenant = Get-Env TENANT_DOMAIN -Required
$admin  = Get-Env ADMIN_UPN -Required
$laura  = Get-Env LAURA_UPN -Required
$paco   = Get-Env PACO_UPN -Required
$finAlias = Get-Env FINANZAS_GROUP_ALIAS 'FS-Finanzas'
$finRes = Get-DeployedResource 'group' 'finanzas'
$finMail = if ($finRes -and $finRes.mail) { $finRes.mail } else { "$finAlias@$tenant" }

if ((Get-Env PURVIEW_PS_AUTH 'interactive') -eq 'app') {
    Connect-IPPSSession -AppId (Get-Env CLIENT_ID -Required) -CertificateThumbprint (Get-Env CERT_THUMBPRINT -Required) -Organization $tenant
} else {
    Connect-IPPSSession -UserPrincipalName $admin
}

$labelsPath = Join-Path (Get-StateDir) 'labels.json'
$out = @{}
$prev = Read-JsonFile $labelsPath
if ($prev) { $prev.PSObject.Properties | ForEach-Object { $out[$_.Name] = $_.Value } }

function Ensure-Label($Key, $Name, $Display, $Tooltip, [hashtable]$Extra) {
    $existing = Get-Label -Identity $Name -ErrorAction SilentlyContinue
    $created = $false
    if (-not $existing) {
        $params = @{ Name = $Name; DisplayName = $Display; Tooltip = $Tooltip; ContentType = 'File, Email' } + $Extra
        $existing = New-Label @params
        $created = $true
        Write-Host "  ✔ etiqueta creada: $Display"
    } else {
        Write-Host "  · etiqueta ya existía (se reutiliza): $Display"
    }
    $id = if ($existing.ImmutableId) { $existing.ImmutableId } else { $existing.Guid }
    $wasOurs = $out.ContainsKey($Key) -and $out[$Key].created
    $script:out[$Key] = @{ id = "$id"; name = $Name; display = $Display; created = ($created -or $wasOurs) }
}

$rights = "${finMail}:VIEW,VIEWRIGHTSDATA,DOCEDIT,EDIT,PRINT,EXTRACT,REPLY,REPLYALL,FORWARD,OBJMODEL"
Ensure-Label 'alta_confidencial_finanzas' 'FS-Demo-AltConf-Finanzas' 'Altamente confidencial – Finanzas' 'Solo Finanzas. Cifrado.' @{
    EncryptionEnabled = $true
    EncryptionProtectionType = 'Template'
    EncryptionRightsDefinitions = $rights
    EncryptionContentExpiredOnDateInDaysOrNever = 'Never'
}
Ensure-Label 'interno_definiciones' 'FS-Demo-Interno-Definiciones' 'Interno – Definiciones oficiales' 'Definiciones oficiales de uso interno. Sin cifrado.' @{}

$policyName = 'FS-Demo-Etiquetas'
$policy = Get-LabelPolicy -Identity $policyName -ErrorAction SilentlyContinue
if (-not $policy) {
    New-LabelPolicy -Name $policyName -Labels 'FS-Demo-AltConf-Finanzas', 'FS-Demo-Interno-Definiciones' `
        -ExchangeLocation $laura, $paco, $admin | Out-Null
    $out['policy'] = @{ name = $policyName; created = $true }
    Write-Host "  ✔ directiva publicada a Laura, Paco y la admin: $policyName"
} else {
    if (-not $out.ContainsKey('policy')) { $out['policy'] = @{ name = $policyName; created = $false } }
    Write-Host "  · directiva ya existía: $policyName"
}

Write-JsonFile $labelsPath $out
Write-Host "✔ $labelsPath actualizado. Cifrado de «Altamente confidencial – Finanzas» para: $finMail"
Write-Host "  Recuerda: la propagación puede tardar hasta 24 h."
