#requires -Version 7.0
<#
.SYNOPSIS
    Provoca (o revierte) la regresión que la demo 3 pone en pantalla.

.DESCRIPTION
    La demo 3 enseña un test set que pasa de 20 verdes a 19 verdes y 1 rojo,
    y un Agent Change Tracker con el diff de quién lo rompió.

    Lo que se rompe es la regla de versionado de las instrucciones del sistema.
    Sin ella, el agente mezcla FS-KB-01 v1.3 (vigente, 45 días) con FS-KB-02
    v1.2 (obsoleta, 30 días) y responde 30.

    Aplícalo el 1 de octubre y no antes, para que el timeline del Change Tracker
    enseñe un cambio reciente y creíble. Y hazlo con la cuenta de Marta: el
    nombre que aparece en el diff es parte de la historia.

.PARAMETER Aplicar
    Borra la regla de versionado y publica. Es lo que rompe la demo a propósito.

.PARAMETER Revertir
    Devuelve la regla a su sitio. Úsalo después del evento, o si ensayas dos veces.

.EXAMPLE
    pwsh ./uso/Set-RegresionVersionado.ps1 -ConfigPath ./config.local.json -Aplicar

.EXAMPLE
    pwsh ./uso/Set-RegresionVersionado.ps1 -ConfigPath ./config.local.json -Revertir
#>
[CmdletBinding(SupportsShouldProcess, DefaultParameterSetName = "Aplicar")]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "../config.local.json"),
    [Parameter(ParameterSetName = "Aplicar")][switch]$Aplicar,
    [Parameter(ParameterSetName = "Revertir")][switch]$Revertir
)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "../scripts/Common.psm1") -Force

if (-not $Aplicar -and -not $Revertir) {
    $Aplicar = $true   # sin flags, la acción por defecto es provocar la regresión
}

$cfg = Get-DemoConfig -ConfigPath $ConfigPath
$raizDemo = Split-Path -Parent (Resolve-Path -LiteralPath $ConfigPath).Path

$proyecto = Join-Path $raizDemo ".pac/$($cfg.agente.schemaName)"
$instrucciones = Join-Path $proyecto "instrucciones.md"
$original = Join-Path $raizDemo "agente/instrucciones.md"

if (-not (Test-Path -LiteralPath $instrucciones -PathType Leaf)) {
    if (-not (Test-Path -LiteralPath $original -PathType Leaf)) {
        throw "No encuentro las instrucciones del agente. Ejecuta antes la etapa 6 del despliegue."
    }
    Write-Paso "No hay proyecto sincronizado: se trabaja sobre $original" -Nivel Aviso
    $instrucciones = $original
}

$MARCA_INICIO = "<!-- REGLA-VERSIONADO-INICIO -->"
$MARCA_FIN = "<!-- REGLA-VERSIONADO-FIN -->"
$REGLA = @"
Prioriza siempre la versión VIGENTE de la política.
Ignora documentos marcados OBSOLETA.
"@

$contenido = Get-Content -LiteralPath $instrucciones -Raw -Encoding UTF8
$patron = [regex]::Escape($MARCA_INICIO) + "(?s).*?" + [regex]::Escape($MARCA_FIN)

if (-not ($contenido -match $patron)) {
    throw "No encuentro los marcadores de la regla de versionado en $instrucciones. ¿Se editaron a mano?"
}

$tieneRegla = $contenido -match ([regex]::Escape($MARCA_INICIO) + "(?s)\s*Prioriza siempre")

if ($Revertir) {
    if ($tieneRegla) {
        Write-Paso "La regla ya está en su sitio. Nada que revertir." -Nivel Salta
        return
    }
    $nuevo = [regex]::Replace($contenido, $patron, "$MARCA_INICIO`n$REGLA$MARCA_FIN")
    $accion = "Restaurar la regla de versionado"
}
else {
    if (-not $tieneRegla) {
        Write-Paso "La regla ya está borrada. La regresión sigue activa." -Nivel Salta
        return
    }
    $nuevo = [regex]::Replace($contenido, $patron, "$MARCA_INICIO`n$MARCA_FIN")
    $accion = "Borrar la regla de versionado"
}

if (-not $PSCmdlet.ShouldProcess($instrucciones, $accion)) {
    Write-Paso "[simulado] $accion" -Nivel Salta
    Write-Paso "[simulado] pac copilot push --project-dir $proyecto" -Nivel Salta
    return
}

# Copia de seguridad, por si el ensayo sale raro y hay que volver deprisa
$respaldo = "$instrucciones.$(Get-Date -Format 'yyyyMMdd-HHmmss').bak"
Copy-Item -LiteralPath $instrucciones -Destination $respaldo
Write-Paso "Respaldo en $respaldo" -Nivel Info

$nuevo | Set-Content -LiteralPath $instrucciones -Encoding UTF8
Write-Paso $accion -Nivel Ok

# --- Publicar, que es lo que hace que el Change Tracker registre el cambio ----
if (Test-Path -LiteralPath $proyecto -PathType Container) {
    Invoke-Pac copilot push --project-dir $proyecto | Out-Null
    Write-Paso "Cambio subido al entorno" -Nivel Ok
}
else {
    Write-Paso "No hay proyecto pac sincronizado: publica el cambio a mano." -Nivel Aviso
}

Write-Host ""
if ($Revertir) {
    Write-Paso "Vuelve a ejecutar las evaluaciones: deben salir los 20 en verde." -Nivel Info
}
else {
    Write-Paso "Comprueba AHORA que la regresión existe, no lo supongas:" -Nivel Aviso
    Write-Paso "  pwsh ./uso/Invoke-Evaluaciones.ps1 -ConfigPath '$ConfigPath'" -Nivel Info
    Write-Paso "  Esperado: 19 verde / 1 rojo. El caso del plazo online debe devolver 30 días." -Nivel Info
    Write-Paso "  Y en el Agent Change Tracker debe verse el diff a nombre de $($cfg.agente.owner.displayName)." -Nivel Info
}
