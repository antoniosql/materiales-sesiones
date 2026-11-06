<#
.SYNOPSIS
  Crea la columna de metadatos administrados «Dominio» en la biblioteca de FraSoHome-KB-Oficial,
  enlazada al conjunto «FraSoHome|Dominio» del term store, y rellena cada documento.
.DESCRIPTION
  Lee state/dominio_plan.json, que genera `semdebt sharepoint --fase despues`.
  Usa PnP.PowerShell con el mismo registro de aplicación (certificado) o en modo interactivo.
#>
[CmdletBinding()]
param([string]$EnvFile)

. "$PSScriptRoot/Common.ps1"
if ($EnvFile) { Import-DotEnv $EnvFile } else { Import-DotEnv }

$plan = Read-JsonFile (Join-Path (Get-StateDir) 'dominio_plan.json')
if (-not $plan) { throw 'No existe state/dominio_plan.json: ejecuta antes `semdebt sharepoint --fase despues`.' }

Connect-PnPWithEnv $plan.siteUrl
$list = Get-PnPList -Identity $plan.listId
$col = $plan.column

$field = Get-PnPField -List $list -Identity $col.name -ErrorAction SilentlyContinue
if (-not $field) {
    Add-PnPTaxonomyField -List $list -DisplayName $col.display -InternalName $col.name `
        -TermSetPath $plan.termSetPath -TermPathDelimiter '|' -AddToDefaultView | Out-Null
    Write-Host "  ✔ columna $($col.display) enlazada a $($plan.termSetPath)"
} else {
    Write-Host "  · la columna $($col.name) ya existe"
}

foreach ($it in $plan.items) {
    if (-not $it.termId) { Write-Warning "  ✘ $($it.file): sin id de término ($($it.term))"; continue }
    Set-PnPListItem -List $list -Identity $it.listItemId -Values @{ $col.name = $it.termId } -UpdateType SystemUpdate | Out-Null
    Write-Host "  ✔ $($it.file) → $($it.term)"
}
Write-Host '✔ Dominio aplicado a la biblioteca oficial.'
