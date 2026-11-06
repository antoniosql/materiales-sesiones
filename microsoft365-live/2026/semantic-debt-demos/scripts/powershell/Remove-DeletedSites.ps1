<#
.SYNOPSIS
  Purga de la papelera de SharePoint los sitios de la demo que `semdebt cleanup` ya borró.
.DESCRIPTION
  Al borrar un grupo de Microsoft 365, su sitio pasa a la papelera del tenant (93 días).
  Si quieres volver a desplegar con el mismo alias antes de ese plazo, hay que purgarlo.
  Lee la lista de state/deployed.json (notes.sites_to_purge). Requiere el rol SharePoint Administrator.
#>
[CmdletBinding()]
param([string]$EnvFile, [switch]$Yes)

. "$PSScriptRoot/Common.ps1"
if ($EnvFile) { Import-DotEnv $EnvFile } else { Import-DotEnv }

$statePath = Join-Path (Get-StateDir) 'deployed.json'
$state = Read-JsonFile $statePath
$urls = @($state.notes.sites_to_purge | Where-Object { $_ })
if (-not $urls -or $urls.Count -eq 0) { Write-Host 'No hay sitios pendientes de purgar.'; return }
Write-Host 'Se van a purgar de la papelera de SharePoint:'; $urls | ForEach-Object { Write-Host "  - $_" }
if (-not $Yes -and (Read-Host '¿Continuar? [s/N]') -notin @('s', 'si', 'sí', 'y')) { return }

$spHost = Get-Env SP_HOST -Required
$adminUrl = "https://" + $spHost.Replace('.sharepoint.com', '-admin.sharepoint.com')
Connect-PnPWithEnv $adminUrl

$left = @()
foreach ($u in $urls) {
    try {
        $deleted = Get-PnPTenantDeletedSite -Identity $u -ErrorAction SilentlyContinue
        if (-not $deleted) { Write-Warning "  · $u aún no está en la papelera (el borrado del grupo tarda); repite más tarde"; $left += $u; continue }
        Remove-PnPTenantDeletedSite -Identity $u -Force
        Write-Host "  ✔ $u"
    } catch { Write-Warning "  ✘ ${u}: $_"; $left += $u }
}
$state.notes | Add-Member -NotePropertyName sites_to_purge -NotePropertyValue ([object[]]$left) -Force
Write-JsonFile $statePath $state
