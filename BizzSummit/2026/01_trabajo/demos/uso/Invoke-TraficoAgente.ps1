#requires -Version 7.0
<#
.SYNOPSIS
    Genera conversaciones reales contra el agente para que las demos tengan datos que enseñar.

.DESCRIPTION
    Un agente recién creado sale en blanco en Usage, en Monitor y en la columna
    Risks de All agents. Una demo sobre inventario y gobierno con todos los
    contadores a cero no se sostiene.

    Este script habla con el agente por Direct Line, como lo haría un usuario,
    y deja huella en telemetría. Reparte las conversaciones a lo largo de varios
    días simulados usando -Dias, porque una gráfica con un único pico se nota.

    Lánzalo al menos una semana antes del evento y déjalo correr a diario.

.PARAMETER Conversaciones
    Número de conversaciones a generar en esta pasada.

.PARAMETER Dias
    Reparte las conversaciones en tandas y espera entre ellas. Con -Dias 1 va del tirón.

.EXAMPLE
    pwsh ./uso/Invoke-TraficoAgente.ps1 -ConfigPath ./config.local.json -Conversaciones 40

.EXAMPLE
    # Ensayo sin hablar con el tenant
    pwsh ./uso/Invoke-TraficoAgente.ps1 -ConfigPath ./config.local.json -WhatIf
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "../config.local.json"),
    [int]$Conversaciones = 40,
    [int]$Dias = 1,
    [int]$PausaSegundos = 2
)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "../scripts/Common.psm1") -Force

$cfg = Get-DemoConfig -ConfigPath $ConfigPath
$sim = -not $PSCmdlet.ShouldProcess($cfg.agente.displayName, "Generar $Conversaciones conversaciones")

# Preguntas reales del proceso de devoluciones. Mezcla documentales, métricas y
# alguna que el agente debe rechazar: así la telemetría se parece a la de verdad.
$PREGUNTAS = @(
    "¿Cuál es el plazo de devolución para compras online?"
    "Un cliente Oro compró un sofá online el 20 de agosto y quiere devolverlo. ¿Está en plazo?"
    "¿Qué productos no admiten devolución voluntaria?"
    "¿Cómo se reembolsa un pago mixto tarjeta más efectivo?"
    "¿Qué significa ventas netas y cómo se calcula?"
    "¿Qué es stock disponible?"
    "¿Qué plazo tengo para reportar un daño en transporte?"
    "¿Qué hago si el cliente no tiene ticket?"
    "¿En qué casos se escala una devolución por sospecha de fraude?"
    "¿Qué tier tiene derecho a una excepción de devolución por semestre?"
    "Dame las ventas netas online entre 2026-02-01 y 2026-02-15"
    "¿Cuál fue la tienda con más ventas netas el 2026-02-10?"
    "Calcula la tasa de devolución en importe para febrero de 2026 en online"
    "Lista cinco devoluciones aprobadas con motivo R04 en enero de 2026"
    "¿Cuántos pedidos hubo en tienda la semana del 2026-02-01?"
    "¿Qué SKUs tienen alerta de quiebra de stock hoy?"
    "¿Puedo aceptar una devolución de un artículo OUTLET?"
    "¿Cómo se gestiona una devolución cruzada de online a tienda?"
    "Un cliente ha hecho cuatro devoluciones del mismo pedido esta semana"
    "¿Qué información debe incluir una respuesta sobre un KPI?"
)

function Get-DirectLineToken {
    param($Config)
    $uri = $Config.agente.directLineTokenEndpoint.Replace("{schemaName}", $Config.agente.schemaName)
    $respuesta = Invoke-RestMethod -Method GET -Uri $uri -ErrorAction Stop
    return $respuesta.token
}

function Start-Conversacion {
    param([string]$Token, [string]$ApiRoot)
    return Invoke-RestMethod -Method POST -Uri "$ApiRoot/conversations" `
        -Headers @{ Authorization = "Bearer $Token" } -ErrorAction Stop
}

function Send-Mensaje {
    param([string]$Token, [string]$ApiRoot, [string]$ConversationId, [string]$Texto, [string]$Usuario)
    $cuerpo = @{
        type = "message"
        from = @{ id = $Usuario; name = $Usuario }
        text = $Texto
    } | ConvertTo-Json -Depth 5
    Invoke-RestMethod -Method POST -Uri "$ApiRoot/conversations/$ConversationId/activities" `
        -Headers @{ Authorization = "Bearer $Token" } `
        -ContentType "application/json; charset=utf-8" -Body $cuerpo -ErrorAction Stop | Out-Null
}

function Get-Respuestas {
    param([string]$Token, [string]$ApiRoot, [string]$ConversationId, [string]$Watermark)
    $uri = "$ApiRoot/conversations/$ConversationId/activities"
    if ($Watermark) { $uri += "?watermark=$Watermark" }
    return Invoke-RestMethod -Method GET -Uri $uri -Headers @{ Authorization = "Bearer $Token" } -ErrorAction Stop
}

# ------------------------------------------------------------------ ejecución
Write-Host ""
Write-Host "Tráfico contra '$($cfg.agente.displayName)'" -ForegroundColor White
Write-Paso "Tenant: $($cfg.tenant.domain)" -Nivel Info
Write-Paso "$Conversaciones conversaciones repartidas en $Dias tanda(s)" -Nivel Info

if ($sim) {
    Write-Paso "[simulado] no se contacta con Direct Line" -Nivel Salta
    $porTanda = [Math]::Ceiling($Conversaciones / $Dias)
    for ($d = 1; $d -le $Dias; $d++) {
        Write-Paso "[simulado] tanda $d : $porTanda conversaciones" -Nivel Salta
    }
    Write-Paso "Preguntas disponibles en el guion: $($PREGUNTAS.Count)" -Nivel Info
    return
}

$token = Get-DirectLineToken -Config $cfg
Write-Paso "Token de Direct Line obtenido" -Nivel Ok

$usuarios = @(
    $cfg.personas.storeManager.displayName
    "Tienda MAD01"
    "Tienda BCN01"
    "Tienda VLC01"
    "Atención al cliente"
    "Operaciones"
)

$porTanda = [Math]::Ceiling($Conversaciones / $Dias)
$hechas = 0
$fallos = 0

for ($d = 1; $d -le $Dias; $d++) {
    Write-Paso "Tanda $d de $Dias" -Nivel Info
    for ($i = 0; $i -lt $porTanda -and $hechas -lt $Conversaciones; $i++) {
        $pregunta = $PREGUNTAS | Get-Random
        $usuario = $usuarios | Get-Random
        try {
            $conv = Start-Conversacion -Token $token -ApiRoot $cfg.agente.directLineApiRoot
            Send-Mensaje -Token $token -ApiRoot $cfg.agente.directLineApiRoot `
                -ConversationId $conv.conversationId -Texto $pregunta -Usuario $usuario

            Start-Sleep -Seconds $PausaSegundos
            $act = Get-Respuestas -Token $token -ApiRoot $cfg.agente.directLineApiRoot `
                -ConversationId $conv.conversationId
            $respuesta = ($act.activities | Where-Object { $_.from.id -ne $usuario -and $_.text } |
                Select-Object -Last 1).text

            $hechas++
            $corta = if ($respuesta) { $respuesta.Substring(0, [Math]::Min(70, $respuesta.Length)) } else { "(sin respuesta)" }
            Write-Paso "$hechas/$Conversaciones · $usuario · $corta..." -Nivel Ok
        }
        catch {
            $fallos++
            Write-Paso "Fallo en la conversación $($hechas + $fallos): $($_.Exception.Message)" -Nivel Aviso
            if ($fallos -ge 5) { throw "Cinco fallos seguidos. Revisa el canal de Direct Line del agente." }
        }
    }
    if ($d -lt $Dias) {
        Write-Paso "Fin de tanda. Vuelve a lanzar el script mañana para repartir la telemetría." -Nivel Info
        break
    }
}

Write-Host ""
Write-Paso "$hechas conversaciones completadas, $fallos fallidas" -Nivel Ok
Write-Paso "Comprueba en el PPAC > Copilot Studio Monitor que las sesiones aparecen." -Nivel Info
