#requires -Version 7.0
<#
.SYNOPSIS
    Siembra el buzón de devoluciones con reclamaciones de clientes.

.DESCRIPTION
    El agente externo de la demo 4 triaja un buzón. Un buzón vacío no se puede
    triar, así que este script envía correos reales al buzón compartido usando
    Graph, con fechas escalonadas hacia atrás para que la bandeja parezca viva
    y no una carga masiva de hace diez minutos.

    Entre los correos hay cuatro del mismo remitente en pocos días: es el patrón
    anómalo que el triaje debe destacar en el resumen.

.EXAMPLE
    pwsh ./uso/Send-CorreosDevolucion.ps1 -ConfigPath ./config.local.json

.EXAMPLE
    pwsh ./uso/Send-CorreosDevolucion.ps1 -ConfigPath ./config.local.json -Cantidad 6 -WhatIf
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "../config.local.json"),
    [int]$Cantidad = 0,
    [int]$RepartirEnDias = 9
)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "../scripts/Common.psm1") -Force

$cfg = Get-DemoConfig -ConfigPath $ConfigPath
$raizDemo = Split-Path -Parent (Resolve-Path -LiteralPath $ConfigPath).Path
$sim = -not $PSCmdlet.ShouldProcess($cfg.exchange.sharedMailbox, "Sembrar correos de devolución")

$plantillas = Join-Path $raizDemo "datos/buzon/correos.json"
$correos = Get-Content -LiteralPath $plantillas -Raw -Encoding UTF8 | ConvertFrom-Json
if ($Cantidad -gt 0 -and $Cantidad -lt $correos.Count) {
    $correos = $correos | Select-Object -First $Cantidad
}

Write-Host ""
Write-Paso "Buzón destino: $($cfg.exchange.sharedMailbox)" -Nivel Info
Write-Paso "$($correos.Count) correos" -Nivel Info

if (-not $sim) {
    Import-Module Microsoft.Graph.Users.Actions -ErrorAction Stop
    Connect-MgGraph -Scopes "Mail.Send", "Mail.ReadWrite" -NoWelcome -ErrorAction Stop
    Write-Paso "Conectado a Graph como $((Get-MgContext).Account)" -Nivel Ok
}

$i = 0
foreach ($c in $correos) {
    $i++
    $diasAtras = [Math]::Round($RepartirEnDias * (1 - ($i / [double]$correos.Count)), 0)
    $cuerpoHtml = @"
<p>$($c.cuerpo)</p>
<p>--<br/>
$($c.nombre)<br/>
$($c.remitente)</p>
<p style="color:#888;font-size:11px">Motivo declarado: $($c.motivo) &middot; Canal: $($c.tienda) &middot; Mensaje sintético de demostración</p>
"@

    if ($sim) {
        Write-Paso "[simulado] hace ~$diasAtras d · $($c.nombre) · $($c.asunto)" -Nivel Salta
        continue
    }

    $mensaje = @{
        message = @{
            subject      = $c.asunto
            body         = @{ contentType = "HTML"; content = $cuerpoHtml }
            toRecipients = @(@{ emailAddress = @{ address = $cfg.exchange.sharedMailbox } })
            replyTo      = @(@{ emailAddress = @{ address = $c.remitente; name = $c.nombre } })
            categories   = @("Devoluciones", $c.motivo)
        }
        saveToSentItems = $false
    }

    try {
        # Se envía desde la cuenta conectada; el remitente real del cliente va en replyTo.
        Send-MgUserMail -UserId (Get-MgContext).Account -BodyParameter $mensaje -ErrorAction Stop
        Write-Paso "$i/$($correos.Count) · $($c.nombre) · $($c.asunto)" -Nivel Ok
        Start-Sleep -Milliseconds 700
    }
    catch {
        Write-Paso "No se pudo enviar '$($c.asunto)': $($_.Exception.Message)" -Nivel Aviso
    }
}

Write-Host ""
Write-Paso "Siembra terminada. El patrón anómalo son los cuatro correos de Héctor Vidal." -Nivel Info
