#requires -Version 7.0
<#
    Etapa 2 — SharePoint.

    Dos sitios, y la diferencia entre ellos es media demo 2:

      FraSoHome-KB-Operaciones      → lo que el agente SÍ puede ver
      FraSoHome-PrevencionPerdidas  → lo que no. Aquí vive FS-KB-11.

    Sube los ocho documentos VIGENTES más el obsoleto FS-KB-02 (que es lo que
    provoca la regresión de la demo 3) y genera FS-KB-11 si no existe.
    FS-KB-10 (prompt injection) NO se sube: no pinta nada en esta sesión.
#>
[CmdletBinding()]
param([Parameter(Mandatory)]$Contexto)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "../Common.psm1") -Force

$cfg = $Contexto.Config
$estado = $Contexto.Estado
$sim = $Contexto.Simular

Import-Module Microsoft.Graph.Sites -ErrorAction Stop
Import-Module Microsoft.Graph.Files -ErrorAction Stop

$ambitos = @("Sites.ReadWrite.All", "Sites.Manage.All", "Files.ReadWrite.All")
if (-not $sim) {
    Connect-MgGraph -Scopes $ambitos -NoWelcome -ErrorAction Stop
    Write-Paso "Conectado a Graph como $((Get-MgContext).Account)" -Nivel Ok
}

$kbOrigen = Join-Path $Contexto.RaizDatos "01_datos/rag_copilot_studio/knowledge_base/Documentos_Knowledge_Clasificados"

function Resolve-SitioGraph {
    param([string]$RootUrl, [string]$Alias)
    $host_ = ([Uri]$RootUrl).Host
    try {
        return Get-MgSite -SiteId "${host_}:/sites/$Alias" -ErrorAction Stop
    }
    catch {
        return $null
    }
}

foreach ($clave in @("kbSite", "restrictedSite")) {
    $sitio = $cfg.sharepoint.$clave
    Write-Paso "Sitio '$($sitio.alias)'" -Nivel Info

    if ($sim) {
        Write-Paso "[simulado] Crearía/reutilizaría $($cfg.sharepoint.rootUrl)/sites/$($sitio.alias)" -Nivel Salta
        continue
    }

    $existente = Resolve-SitioGraph -RootUrl $cfg.sharepoint.rootUrl -Alias $sitio.alias
    if ($existente) {
        Write-Paso "Reutilizo el sitio existente [$($existente.Id)]" -Nivel Salta
        $estado.propiedad["site_$($sitio.alias)"] = $false
    }
    else {
        # La creación de sitios de comunicación va por el endpoint de SharePoint REST,
        # que acepta el token de Graph del usuario conectado.
        Add-Runbook -Estado $estado `
            -Titulo "Crear el sitio de SharePoint '$($sitio.alias)'" `
            -Motivo "El sitio no existe y la creación de site collections requiere rol de administrador de SharePoint." `
            -Comando @"
# Con el módulo PnP.PowerShell y una cuenta de SharePoint Administrator:
Connect-PnPOnline -Url '$($cfg.sharepoint.rootUrl)' -Interactive
New-PnPSite -Type CommunicationSite ``
    -Title '$($sitio.title)' ``
    -Url '$($cfg.sharepoint.rootUrl)/sites/$($sitio.alias)' ``
    -Description '$($sitio.description)'
"@
        continue
    }
    $estado["site_$($sitio.alias)"] = $existente.Id
}

# --- Documentos vigentes + el obsoleto ---------------------------------------
$aSubir = @()
foreach ($doc in @($cfg.datos.documentosVigentes) + @($cfg.datos.documentoObsoleto)) {
    $f = Get-ChildItem -LiteralPath $kbOrigen -Recurse -Filter $doc -File -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($f) { $aSubir += $f } else { Write-Paso "No encontrado: $doc" -Nivel Aviso }
}

Write-Paso "$($aSubir.Count) documentos para el sitio de conocimiento" -Nivel Info

if ($sim) {
    foreach ($f in $aSubir) { Write-Paso "[simulado] Subiría $($f.Name)" -Nivel Salta }
}
else {
    $siteId = $estado["site_$($cfg.sharepoint.kbSite.alias)"]
    if ($siteId) {
        $drive = Get-MgSiteDefaultDrive -SiteId $siteId
        foreach ($f in $aSubir) {
            $destino = "root:/Documentos compartidos/$($f.Name):"
            try {
                Set-MgDriveItemContent -DriveId $drive.Id -DriveItemId $destino -InFile $f.FullName -ErrorAction Stop | Out-Null
                Write-Paso "Subido $($f.Name)" -Nivel Ok
            }
            catch {
                Write-Paso "No se pudo subir $($f.Name): $($_.Exception.Message)" -Nivel Aviso
            }
        }
    }
    else {
        Write-Paso "El sitio de conocimiento no está disponible todavía; la subida queda pendiente." -Nivel Aviso
    }
}

# --- FS-KB-11: el documento confidencial --------------------------------------
$kb11Local = Join-Path $Contexto.RaizDemo "datos/kb/$($cfg.datos.documentoConfidencial)"
if (-not (Test-Path -LiteralPath $kb11Local -PathType Leaf)) {
    Write-Paso "Genero $($cfg.datos.documentoConfidencial)" -Nivel Info
    & (Join-Path $Contexto.RaizDemo "datos/kb/New-DocumentoConfidencial.ps1") `
        -Destino $kb11Local -Config $cfg
}

if ($sim) {
    Write-Paso "[simulado] Subiría FS-KB-11 al sitio restringido" -Nivel Salta
}
else {
    $siteRestId = $estado["site_$($cfg.sharepoint.restrictedSite.alias)"]
    if ($siteRestId -and (Test-Path -LiteralPath $kb11Local)) {
        $driveR = Get-MgSiteDefaultDrive -SiteId $siteRestId
        $destino = "root:/Documentos compartidos/$($cfg.datos.documentoConfidencial):"
        Set-MgDriveItemContent -DriveId $driveR.Id -DriveItemId $destino -InFile $kb11Local | Out-Null
        Write-Paso "FS-KB-11 subido al sitio restringido" -Nivel Ok
        $estado["kb11DriveId"] = $driveR.Id
    }
    else {
        Write-Paso "El sitio restringido no está disponible: FS-KB-11 queda sin subir." -Nivel Aviso
    }
}

Write-Paso "Etapa 2 completada." -Nivel Ok
