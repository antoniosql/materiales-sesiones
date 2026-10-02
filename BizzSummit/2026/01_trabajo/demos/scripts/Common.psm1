#requires -Version 7.0
<#
    Common.psm1 — utilidades compartidas por el despliegue de las demos del Bizz Summit 2026.
    Configuración, registro, estado idempotente y comprobación de herramientas.
#>

Set-StrictMode -Version 1.0

$script:Indent = 0

function Write-Paso {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Mensaje,
        [ValidateSet("Info", "Ok", "Aviso", "Error", "Salta")][string]$Nivel = "Info"
    )
    $prefijo = @{
        Info  = "  ·"
        Ok    = "  +"
        Aviso = "  !"
        Error = "  x"
        Salta = "  ="
    }[$Nivel]
    $color = @{
        Info  = "Gray"
        Ok    = "Green"
        Aviso = "Yellow"
        Error = "Red"
        Salta = "DarkGray"
    }[$Nivel]
    $sangria = " " * ($script:Indent * 2)
    Write-Host "$sangria$prefijo $Mensaje" -ForegroundColor $color
}

function Write-Etapa {
    param([Parameter(Mandatory)][string]$Titulo)
    Write-Host ""
    Write-Host "== $Titulo " -NoNewline -ForegroundColor Cyan
    Write-Host ("=" * [Math]::Max(0, 74 - $Titulo.Length)) -ForegroundColor DarkCyan
}

function Get-DemoConfig {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$ConfigPath)

    if (-not (Test-Path -LiteralPath $ConfigPath -PathType Leaf)) {
        throw "No existe el archivo de configuración: $ConfigPath"
    }
    $config = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json

    $obligatorios = @(
        "tenant.domain",
        "sharepoint.rootUrl",
        "agente.schemaName",
        "datos.raizFraSoHome"
    )
    foreach ($ruta in $obligatorios) {
        $valor = $config
        foreach ($parte in $ruta.Split(".")) {
            if ($null -eq $valor) { break }
            $valor = $valor.PSObject.Properties[$parte].Value
        }
        if ([string]::IsNullOrWhiteSpace([string]$valor)) {
            throw "Falta el valor obligatorio '$ruta' en $ConfigPath"
        }
    }

    # El tenant es configurable: todo lo que lleve el dominio de ejemplo se reescribe
    # a partir de tenant.domain, para que un config.local.json solo tenga que cambiarlo ahí.
    $config | Add-Member -NotePropertyName "_configPath" -NotePropertyValue (Resolve-Path -LiteralPath $ConfigPath).Path -Force
    return $config
}

function Resolve-RutaDemo {
    <#
        Convierte una ruta relativa del config en absoluta, tomando como base
        la carpeta del propio config.
    #>
    param(
        [Parameter(Mandatory)]$Config,
        [Parameter(Mandatory)][string]$Ruta
    )
    if ([IO.Path]::IsPathRooted($Ruta)) { return [IO.Path]::GetFullPath($Ruta) }
    $base = Split-Path -Parent $Config._configPath
    return [IO.Path]::GetFullPath((Join-Path $base $Ruta))
}

function Get-EstadoDespliegue {
    param([Parameter(Mandatory)][string]$EstadoPath)
    if (Test-Path -LiteralPath $EstadoPath -PathType Leaf) {
        return Get-Content -LiteralPath $EstadoPath -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
    }
    return @{
        creado    = (Get-Date).ToString("o")
        propiedad = @{}
    }
}

function Save-EstadoDespliegue {
    param(
        [Parameter(Mandatory)]$Estado,
        [Parameter(Mandatory)][string]$EstadoPath
    )
    $carpeta = Split-Path -Parent $EstadoPath
    if (-not (Test-Path -LiteralPath $carpeta)) {
        New-Item -ItemType Directory -Path $carpeta -Force | Out-Null
    }
    $Estado["actualizado"] = (Get-Date).ToString("o")
    $Estado | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $EstadoPath -Encoding UTF8
    Write-Paso "Estado guardado en $EstadoPath" -Nivel Info
}

function Test-Herramienta {
    <#
        Comprueba que un ejecutable está en el PATH. Devuelve $true/$false y no lanza,
        para que el preflight pueda listar todo lo que falta de una vez.
    #>
    param(
        [Parameter(Mandatory)][string]$Nombre,
        [string]$ComandoVersion = "--version"
    )
    $cmd = Get-Command $Nombre -ErrorAction SilentlyContinue
    if (-not $cmd) {
        Write-Paso "$Nombre no está en el PATH" -Nivel Error
        return $false
    }
    try {
        $version = (& $Nombre $ComandoVersion 2>&1 | Select-Object -First 1)
        Write-Paso "$Nombre disponible ($version)" -Nivel Ok
    }
    catch {
        Write-Paso "$Nombre disponible" -Nivel Ok
    }
    return $true
}

function Test-ModuloPowerShell {
    param(
        [Parameter(Mandatory)][string]$Nombre,
        [string]$InstalarCon
    )
    if (Get-Module -ListAvailable -Name $Nombre) {
        Write-Paso "Módulo $Nombre disponible" -Nivel Ok
        return $true
    }
    $sugerencia = if ($InstalarCon) { $InstalarCon } else { "Install-Module $Nombre -Scope CurrentUser" }
    Write-Paso "Falta el módulo $Nombre. Instálalo con: $sugerencia" -Nivel Error
    return $false
}

function Connect-GraphDemo {
    <#
        Conexión a Microsoft Graph robusta para el terminal integrado de VS Code,
        donde la ventana interactiva a menudo no aparece y falla con
        "User canceled authentication". Reutiliza la sesión si ya tiene los
        ámbitos; si no, intenta interactivo y cae a código de dispositivo.
    #>
    param(
        [Parameter(Mandatory)][string[]]$Ambitos,
        [string]$TenantId
    )
    $ctx = Get-MgContext
    if ($ctx -and -not ($Ambitos | Where-Object { $ctx.Scopes -notcontains $_ })) {
        Write-Paso "Reutilizando sesión de Graph de $($ctx.Account)" -Nivel Ok
        return
    }
    $params = @{ Scopes = $Ambitos; NoWelcome = $true; ErrorAction = "Stop" }
    if ($TenantId) { $params["TenantId"] = $TenantId }
    try {
        Connect-MgGraph @params
    }
    catch {
        Write-Paso "Inicio de sesión interactivo fallido ($($_.Exception.Message)). Probando con código de dispositivo..." -Nivel Aviso
        Connect-MgGraph @params -UseDeviceCode
    }
    Write-Paso "Conectado a Graph como $((Get-MgContext).Account)" -Nivel Ok
}

function Invoke-Pac {
    <#
        Envoltorio de la Power Platform CLI. Respeta -WhatIf del script llamante:
        con -Simular solo imprime el comando.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, ValueFromRemainingArguments)][string[]]$Argumentos,
        [switch]$Simular,
        [switch]$TolerarError
    )
    $linea = "pac " + ($Argumentos -join " ")
    if ($Simular) {
        Write-Paso "[simulado] $linea" -Nivel Salta
        return $null
    }
    Write-Paso $linea -Nivel Info
    $salida = & pac @Argumentos 2>&1
    if ($LASTEXITCODE -ne 0 -and -not $TolerarError) {
        throw "Falló '$linea':`n$($salida -join [Environment]::NewLine)"
    }
    return $salida
}

function Add-Runbook {
    <#
        Acumula pasos que el script no ha podido ejecutar por falta de permisos,
        con el comando exacto ya relleno desde la config, para pasárselo a quien
        sí tenga el rol.
    #>
    param(
        [Parameter(Mandatory)]$Estado,
        [Parameter(Mandatory)][string]$Titulo,
        [Parameter(Mandatory)][string]$Motivo,
        [string]$Comando
    )
    if (-not $Estado.ContainsKey("runbook")) { $Estado["runbook"] = @() }
    # Relanzar el despliegue no debe duplicar pasos: el título identifica al paso.
    $Estado["runbook"] = @($Estado["runbook"] | Where-Object { $_.titulo -ne $Titulo })
    $Estado["runbook"] += [ordered]@{
        titulo  = $Titulo
        motivo  = $Motivo
        comando = $Comando
    }
    Write-Paso "Anotado en el runbook manual: $Titulo" -Nivel Aviso
}

function Write-RunbookFile {
    param(
        [Parameter(Mandatory)]$Estado,
        [Parameter(Mandatory)][string]$RunbookPath
    )
    if (-not $Estado.ContainsKey("runbook") -or $Estado["runbook"].Count -eq 0) {
        Write-Paso "No hay pasos pendientes de delegar: no se genera runbook." -Nivel Ok
        return
    }
    $carpeta = Split-Path -Parent $RunbookPath
    if (-not (Test-Path -LiteralPath $carpeta)) {
        New-Item -ItemType Directory -Path $carpeta -Force | Out-Null
    }
    $sb = [Text.StringBuilder]::new()
    [void]$sb.AppendLine("# Runbook manual — demos Bizz Summit 2026")
    [void]$sb.AppendLine()
    [void]$sb.AppendLine("Pasos que el despliegue no pudo completar. Cada uno lleva el comando exacto,")
    [void]$sb.AppendLine("ya relleno con los valores de tu configuración, para quien tenga el rol necesario.")
    [void]$sb.AppendLine()
    [void]$sb.AppendLine("Generado: " + (Get-Date).ToString("yyyy-MM-dd HH:mm"))
    [void]$sb.AppendLine()
    $i = 1
    foreach ($paso in $Estado["runbook"]) {
        [void]$sb.AppendLine("## $i. $($paso.titulo)")
        [void]$sb.AppendLine()
        [void]$sb.AppendLine("**Por qué quedó pendiente:** $($paso.motivo)")
        [void]$sb.AppendLine()
        if ($paso.comando) {
            [void]$sb.AppendLine('```powershell')
            [void]$sb.AppendLine($paso.comando)
            [void]$sb.AppendLine('```')
            [void]$sb.AppendLine()
        }
        $i++
    }
    $sb.ToString() | Set-Content -LiteralPath $RunbookPath -Encoding UTF8
    Write-Paso "Runbook manual escrito en $RunbookPath" -Nivel Aviso
}

function Test-PermisoRol {
    <#
        Ejecuta un bloque de sondeo. Si falla por permisos, devuelve $false en vez
        de reventar el despliegue: cada etapa decide si continúa o anota runbook.
    #>
    param(
        [Parameter(Mandatory)][scriptblock]$Sondeo,
        [Parameter(Mandatory)][string]$Descripcion
    )
    try {
        & $Sondeo | Out-Null
        return $true
    }
    catch {
        Write-Paso "Sin permisos para $Descripcion : $($_.Exception.Message)" -Nivel Aviso
        return $false
    }
}

Export-ModuleMember -Function `
    Write-Paso, Write-Etapa, Get-DemoConfig, Resolve-RutaDemo, `
    Get-EstadoDespliegue, Save-EstadoDespliegue, Test-Herramienta, Test-ModuloPowerShell, `
    Connect-GraphDemo, Invoke-Pac, Add-Runbook, Write-RunbookFile, Test-PermisoRol
