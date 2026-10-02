#requires -Version 7.0
<#
    Etapa 6 — El agente de Copilot Studio.

    Se construye desde YAML con la Power Platform CLI, no a mano por la UI:
    así el agente es reproducible, versionable y la demo 3 puede provocar la
    regresión editando un archivo en vez de haciendo clics.

        pac copilot init   -> anda el andamiaje canónico en una carpeta de trabajo
        (se superpone ./agente encima)
        pac copilot push   -> lo sube al entorno
        pac copilot publish

    El agente se queda en el entorno Default y SIN propietario nombrado.
    Eso no es un descuido: es el hallazgo de la demo 1.
#>
[CmdletBinding()]
param([Parameter(Mandatory)]$Contexto)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "../Common.psm1") -Force

$cfg = $Contexto.Config
$estado = $Contexto.Estado
$sim = $Contexto.Simular
$ag = $cfg.agente

$envUrl = $estado["defaultEnvironmentUrl"]
if (-not $envUrl) { throw "Falta la URL del entorno Default. Ejecuta antes la etapa 1." }

# --- Autenticación de pac contra el entorno correcto --------------------------
$perfiles = Invoke-Pac -Simular:$sim -TolerarError auth list
$nombrePerfil = "bizzsummit2026"
if ($sim) {
    Write-Paso "[simulado] pac auth create --environment $envUrl --name $nombrePerfil" -Nivel Salta
}
elseif ($perfiles -match $nombrePerfil) {
    Invoke-Pac auth select --name $nombrePerfil | Out-Null
    Write-Paso "Perfil de autenticación '$nombrePerfil' seleccionado" -Nivel Ok
}
else {
    Invoke-Pac auth create --environment $envUrl --name $nombrePerfil | Out-Null
    Write-Paso "Perfil de autenticación creado" -Nivel Ok
}

# --- Carpeta de trabajo -------------------------------------------------------
$trabajo = Join-Path $Contexto.RaizDemo ".pac/$($ag.schemaName)"
$fuente = Join-Path $Contexto.RaizDemo "agente"
$instrucciones = Join-Path $fuente "instrucciones.md"

if (-not (Test-Path -LiteralPath $instrucciones -PathType Leaf)) {
    throw "No existe $instrucciones. Es el archivo que la demo 3 modifica."
}

if (Test-Path -LiteralPath $trabajo) {
    Write-Paso "Reutilizo la carpeta de trabajo $trabajo" -Nivel Salta
}
else {
    if ($sim) {
        Write-Paso "[simulado] pac copilot init --name '$($ag.displayName)' --project-dir $trabajo" -Nivel Salta
    }
    else {
        New-Item -ItemType Directory -Path $trabajo -Force | Out-Null
        Invoke-Pac copilot init `
            --name $ag.displayName `
            --schema-name $ag.schemaName `
            --publisher-prefix $cfg.powerPlatform.publisherPrefix `
            --project-dir $trabajo `
            --authoring-mode "generative" `
            --instructions (Get-Content -LiteralPath $instrucciones -Raw -Encoding UTF8) `
            --environment $envUrl | Out-Null
        Write-Paso "Andamiaje creado en $trabajo" -Nivel Ok
    }
}

# --- Superponer nuestro YAML sobre el andamiaje -------------------------------
$aCopiar = Get-ChildItem -LiteralPath $fuente -Recurse -File |
    Where-Object { $_.Extension -in ".yaml", ".yml" }

foreach ($f in $aCopiar) {
    $relativo = $f.FullName.Substring($fuente.Length).TrimStart([IO.Path]::DirectorySeparatorChar, '/')
    $destino = Join-Path $trabajo $relativo
    if ($sim) {
        Write-Paso "[simulado] copiaría $relativo" -Nivel Salta
        continue
    }
    $carpeta = Split-Path -Parent $destino
    if (-not (Test-Path -LiteralPath $carpeta)) { New-Item -ItemType Directory -Path $carpeta -Force | Out-Null }

    # Los YAML llevan marcadores que dependen del tenant
    $contenido = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8
    $contenido = $contenido.
        Replace("{{SHAREPOINT_KB}}", "$($cfg.sharepoint.rootUrl.TrimEnd('/'))/sites/$($cfg.sharepoint.kbSite.alias)").
        Replace("{{AGENTE_NOMBRE}}", $ag.displayName).
        Replace("{{AGENTE_SCHEMA}}", $ag.schemaName).
        Replace("{{PREFIJO}}", $cfg.powerPlatform.publisherPrefix)
    $contenido | Set-Content -LiteralPath $destino -Encoding UTF8
    Write-Paso "  $relativo" -Nivel Info
}

# Las instrucciones del sistema viven en su propio archivo para que
# uso/Set-RegresionVersionado.ps1 pueda editarlas sin tocar nada más.
if (-not $sim) {
    Copy-Item -LiteralPath $instrucciones -Destination (Join-Path $trabajo "instrucciones.md") -Force
}

# --- Subir y publicar ---------------------------------------------------------
Invoke-Pac -Simular:$sim copilot push --project-dir $trabajo | Out-Null
Write-Paso "Agente subido al entorno Default" -Nivel Ok

$listado = Invoke-Pac -Simular:$sim -TolerarError copilot list --environment $envUrl
$botId = $null
if (-not $sim -and $listado) {
    $linea = $listado | Where-Object { $_ -match [regex]::Escape($ag.displayName) } | Select-Object -First 1
    if ($linea -match "([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})") {
        $botId = $Matches[1]
    }
}
if ($botId) {
    $estado["botId"] = $botId
    Write-Paso "Bot id: $botId" -Nivel Ok
    Invoke-Pac -Simular:$sim copilot publish --bot $botId --environment $envUrl | Out-Null
    Write-Paso "Agente publicado" -Nivel Ok
}
else {
    Write-Paso "No se pudo resolver el bot id automáticamente." -Nivel Aviso
    Add-Runbook -Estado $estado `
        -Titulo "Publicar el agente y anotar su bot id" `
        -Motivo "pac copilot list no devolvió un identificador reconocible." `
        -Comando @"
pac copilot list --environment '$envUrl'
pac copilot publish --bot <BOT_ID> --environment '$envUrl'
# Anota el id en el estado para que los scripts de uso puedan usarlo.
"@
}

$estado["agenteSchemaName"] = $ag.schemaName
$estado.propiedad["agente"] = $true

# --- Canales y propietario ----------------------------------------------------
Add-Runbook -Estado $estado `
    -Titulo "Publicar el agente en Teams y dejar el propietario VACÍO" `
    -Motivo "La configuración de canales se hace desde Copilot Studio; y el propietario se deja sin nombrar a propósito." `
    -Comando @"
# Copilot Studio > $($ag.displayName) > Channels > Microsoft Teams > Turn on
# Compartir con el grupo de usuarios de prueba (unas 40 personas).
# NO rellenes el campo de propietario: la demo 1 consiste precisamente en que está vacío.
# Fecha de creación que se cuenta en la demo: $($ag.createdOnLabel), autora $($ag.owner.displayName).
"@

Write-Paso "Etapa 6 completada." -Nivel Ok
