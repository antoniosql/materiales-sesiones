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
    Connect-GraphDemo -Ambitos $ambitos -TenantId $cfg.tenant.domain
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

function Get-TokenSharePoint {
    # Graph no crea sitios de comunicación: hace falta SharePoint REST, con un
    # token cuya audiencia sea el propio tenant de SharePoint. Lo da az.
    param([string]$RootUrl, [string]$Tenant)
    $token = az account get-access-token --resource $RootUrl --query accessToken -o tsv 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $token) {
        Write-Paso "Inicia sesión en Azure CLI con la cuenta del tenant (se abre el navegador)" -Nivel Info
        az login --tenant $Tenant --allow-no-subscriptions --only-show-errors | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "az login falló." }
        $token = az account get-access-token --resource $RootUrl --query accessToken -o tsv
        if ($LASTEXITCODE -ne 0 -or -not $token) { throw "No se pudo obtener un token de SharePoint con az." }
    }
    return $token
}

function New-SitioComunicacion {
    param([string]$RootUrl, [string]$Token, $Sitio, [string]$Owner, [int]$Lcid)
    $cuerpo = @{
        request = @{
            Title               = $Sitio.title
            Url                 = "$RootUrl/sites/$($Sitio.alias)"
            Description         = $Sitio.description
            Lcid                = $Lcid
            WebTemplate         = "SITEPAGEPUBLISHING#0"
            Owner               = $Owner
            ShareByEmailEnabled = $false
        }
    } | ConvertTo-Json -Depth 5
    $r = Invoke-RestMethod -Method Post -Uri "$RootUrl/_api/SPSiteManager/create" `
        -Headers @{ Authorization = "Bearer $Token"; Accept = "application/json;odata=nometadata" } `
        -ContentType "application/json;odata=nometadata" `
        -Body ([Text.Encoding]::UTF8.GetBytes($cuerpo))
    # SiteStatus: 1 = aprovisionando, 2 = listo, 3 = error
    if ($r.SiteStatus -eq 3) { throw "SharePoint devolvió SiteStatus=3 (error) al crear $($Sitio.alias)." }
    return $r
}

function Send-ArchivoDrive {
    # El drive por defecto ES la biblioteca "Documentos compartidos": la ruta va
    # relativa a su raíz. Subida simple: los FS-KB están muy por debajo de 4 MB.
    param([string]$DriveId, [string]$Archivo)
    $nombre = [Uri]::EscapeDataString((Split-Path -Leaf $Archivo))
    Invoke-MgGraphRequest -Method PUT `
        -Uri "https://graph.microsoft.com/v1.0/drives/$DriveId/root:/${nombre}:/content" `
        -InputFilePath $Archivo -ContentType "application/octet-stream" -ErrorAction Stop | Out-Null
}

$tokenSp = $null

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
        try {
            if (-not $tokenSp) { $tokenSp = Get-TokenSharePoint -RootUrl $cfg.sharepoint.rootUrl -Tenant $cfg.tenant.domain }
            Write-Paso "Creando sitio de comunicación $($cfg.sharepoint.rootUrl)/sites/$($sitio.alias)..." -Nivel Info
            New-SitioComunicacion -RootUrl $cfg.sharepoint.rootUrl -Token $tokenSp -Sitio $sitio `
                -Owner (Get-MgContext).Account -Lcid $cfg.powerPlatform.platformEnvironment.languageCode | Out-Null
            # El aprovisionamiento es asíncrono: se espera a que Graph lo vea.
            for ($i = 0; $i -lt 24 -and -not $existente; $i++) {
                Start-Sleep -Seconds 5
                $existente = Resolve-SitioGraph -RootUrl $cfg.sharepoint.rootUrl -Alias $sitio.alias
            }
            if (-not $existente) { throw "El sitio se pidió pero no aparece en Graph tras 2 minutos." }
            Write-Paso "Sitio creado [$($existente.Id)]" -Nivel Ok
            $estado.propiedad["site_$($sitio.alias)"] = $true
        }
        catch {
            Add-Runbook -Estado $estado `
                -Titulo "Crear el sitio de SharePoint '$($sitio.alias)'" `
                -Motivo "No se pudo crear automáticamente: $($_.Exception.Message)" `
                -Comando @"
# SharePoint admin center > Sitios activos > Crear > Sitio de comunicación
#   Nombre:      $($sitio.title)
#   Dirección:   $($cfg.sharepoint.rootUrl)/sites/$($sitio.alias)
#   Descripción: $($sitio.description)
"@
            continue
        }
    }
    $estado["site_$($sitio.alias)"] = $existente.Id
    # Si una ejecución anterior lo dejó en el runbook, ya no está pendiente.
    if ($estado.ContainsKey("runbook")) {
        $estado["runbook"] = @($estado["runbook"] | Where-Object { $_.titulo -ne "Crear el sitio de SharePoint '$($sitio.alias)'" })
    }
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
            try {
                Send-ArchivoDrive -DriveId $drive.Id -Archivo $f.FullName
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
        Send-ArchivoDrive -DriveId $driveR.Id -Archivo $kb11Local
        Write-Paso "FS-KB-11 subido al sitio restringido" -Nivel Ok
        $estado["kb11DriveId"] = $driveR.Id
    }
    else {
        Write-Paso "El sitio restringido no está disponible: FS-KB-11 queda sin subir." -Nivel Aviso
    }
}

Write-Paso "Etapa 2 completada." -Nivel Ok
