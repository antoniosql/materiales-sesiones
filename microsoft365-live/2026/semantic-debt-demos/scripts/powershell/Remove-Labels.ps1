<#
.SYNOPSIS
  Borra la directiva y las etiquetas que creó Deploy-Labels.ps1 (solo las marcadas created=true en state/labels.json).
.NOTES
  Purview no deja borrar una etiqueta mientras está publicada: primero se borra la directiva.
  Si el borrado de la etiqueta falla, espera a que se propague la eliminación de la directiva y repite.
#>
[CmdletBinding()]
param([string]$EnvFile, [switch]$Yes)

. "$PSScriptRoot/Common.ps1"
if ($EnvFile) { Import-DotEnv $EnvFile } else { Import-DotEnv }
Assert-Module 'ExchangeOnlineManagement' ''

$labelsPath = Join-Path (Get-StateDir) 'labels.json'
$labels = Read-JsonFile $labelsPath
if (-not $labels) { Write-Host 'No hay state/labels.json: nada que borrar.'; return }

$mine = $labels.PSObject.Properties | Where-Object { $_.Value.created }
if (-not $mine) { Write-Host 'Las etiquetas no las crearon estos scripts: no se tocan.'; return }
Write-Host 'Se va a borrar:'; $mine | ForEach-Object { Write-Host "  - $($_.Name): $($_.Value.name)" }
if (-not $Yes -and (Read-Host '¿Continuar? [s/N]') -notin @('s', 'si', 'sí', 'y')) { return }

$tenant = Get-Env TENANT_DOMAIN -Required
if ((Get-Env PURVIEW_PS_AUTH 'interactive') -eq 'app') {
    Connect-IPPSSession -AppId (Get-Env CLIENT_ID -Required) -CertificateThumbprint (Get-Env CERT_THUMBPRINT -Required) -Organization $tenant
} else {
    Connect-IPPSSession -UserPrincipalName (Get-Env ADMIN_UPN -Required)
}

$remaining = @{}
$labels.PSObject.Properties | ForEach-Object { $remaining[$_.Name] = $_.Value }

if ($labels.policy -and $labels.policy.created) {
    try { Remove-LabelPolicy -Identity $labels.policy.name -Confirm:$false; $remaining.Remove('policy'); Write-Host "  ✔ directiva $($labels.policy.name)" }
    catch { Write-Warning "  ✘ directiva: $_" }
}
foreach ($p in $mine | Where-Object { $_.Name -ne 'policy' }) {
    try { Remove-Label -Identity $p.Value.name -Confirm:$false; $remaining.Remove($p.Name); Write-Host "  ✔ etiqueta $($p.Value.display)" }
    catch { Write-Warning "  ✘ etiqueta $($p.Value.name): $_ (vuelve a ejecutarlo cuando se propague el borrado de la directiva)" }
}
if ($remaining.Count -eq 0) { Remove-Item $labelsPath } else { Write-JsonFile $labelsPath $remaining }
