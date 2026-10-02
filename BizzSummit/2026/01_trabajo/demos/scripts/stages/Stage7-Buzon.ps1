#requires -Version 7.0
<#
    Etapa 7 — El buzón de devoluciones.

    Es la fuente que consume el agente externo de la demo 4. Crea el buzón
    compartido y lo siembra con reclamaciones variadas: motivos R01 a R04 y
    dos o tres del mismo cliente que parecen un patrón anómalo, para que el
    triaje tenga algo que encontrar.
#>
[CmdletBinding()]
param([Parameter(Mandatory)]$Contexto)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "../Common.psm1") -Force

$cfg = $Contexto.Config
$estado = $Contexto.Estado
$sim = $Contexto.Simular
$ex = $cfg.exchange

Import-Module ExchangeOnlineManagement -ErrorAction Stop

if ($sim) {
    Write-Paso "[simulado] Connect-ExchangeOnline" -Nivel Salta
}
else {
    try {
        Connect-ExchangeOnline -ShowBanner:$false -DisableWAM -ErrorAction Stop
        Write-Paso "Conectado a Exchange Online" -Nivel Ok
    }
    catch {
        Add-Runbook -Estado $estado `
            -Titulo "Crear el buzón compartido $($ex.sharedMailbox)" `
            -Motivo "No se pudo abrir sesión de Exchange Online: $($_.Exception.Message)" `
            -Comando @"
Connect-ExchangeOnline
New-Mailbox -Shared -Name '$($ex.displayName)' -DisplayName '$($ex.displayName)' ``
    -Alias '$($ex.alias)' -PrimarySmtpAddress '$($ex.sharedMailbox)'
Add-MailboxPermission -Identity '$($ex.sharedMailbox)' ``
    -User '$($cfg.personas.developer.upn)' -AccessRights FullAccess -InheritanceType All
"@
        Write-Paso "Etapa 7 delegada al runbook." -Nivel Aviso
        return
    }
}

# --- Buzón compartido ---------------------------------------------------------
$existe = if ($sim) { $null } else { Get-Mailbox -Identity $ex.sharedMailbox -ErrorAction SilentlyContinue }
if ($existe) {
    Write-Paso "Reutilizo el buzón $($ex.sharedMailbox)" -Nivel Salta
    $estado.propiedad["buzon"] = $false
}
elseif ($sim) {
    Write-Paso "[simulado] New-Mailbox -Shared $($ex.sharedMailbox)" -Nivel Salta
}
else {
    New-Mailbox -Shared -Name $ex.displayName -DisplayName $ex.displayName `
        -Alias $ex.alias -PrimarySmtpAddress $ex.sharedMailbox | Out-Null
    Write-Paso "Buzón compartido creado" -Nivel Ok
    $estado.propiedad["buzon"] = $true

    Add-MailboxPermission -Identity $ex.sharedMailbox `
        -User $cfg.personas.developer.upn -AccessRights FullAccess -InheritanceType All | Out-Null
    Write-Paso "Permiso FullAccess para $($cfg.personas.developer.displayName)" -Nivel Ok
}
$estado["buzon"] = $ex.sharedMailbox

# --- Siembra de correos -------------------------------------------------------
# Se envían por Graph con sendMail, que es lo único que garantiza que aparezcan
# como mensajes recibidos reales y no como items importados sin cabeceras.
$plantillas = Join-Path $Contexto.RaizDemo "datos/buzon/correos.json"
if (-not (Test-Path -LiteralPath $plantillas -PathType Leaf)) {
    Write-Paso "No hay plantillas de correo en $plantillas" -Nivel Aviso
}
else {
    $correos = Get-Content -LiteralPath $plantillas -Raw -Encoding UTF8 | ConvertFrom-Json
    Write-Paso "$($correos.Count) correos de siembra" -Nivel Info

    $enviador = Join-Path $Contexto.RaizDemo "uso/Send-CorreosDevolucion.ps1"
    if ($sim) {
        Write-Paso "[simulado] enviaría $($correos.Count) correos a $($ex.sharedMailbox)" -Nivel Salta
    }
    else {
        & $enviador -ConfigPath $cfg._configPath -Cantidad $ex.seedMessageCount
    }
}

Write-Paso "Etapa 7 completada." -Nivel Ok
