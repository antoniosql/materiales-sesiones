#requires -Version 7.0
<#
    Etapa 3 — Purview.

    Dos controles, y son los dos beats de la demo 2:

      1. Etiqueta de confidencialidad con cifrado sobre FS-KB-11.
         El agente no extrae contenido salvo derechos EXTRACT y VIEW.
      2. Política DLP que bloquea la respuesta cuando aparece un IBAN.

    IMPORTANTE: la propagación de ambas cosas NO es inmediata. Ejecuta esta etapa
    con al menos una semana de margen y comprueba el bloqueo antes del evento.
#>
[CmdletBinding()]
param([Parameter(Mandatory)]$Contexto)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "../Common.psm1") -Force

$cfg = $Contexto.Config
$estado = $Contexto.Estado
$sim = $Contexto.Simular
$pv = $cfg.purview

Import-Module ExchangeOnlineManagement -ErrorAction Stop

if ($sim) {
    Write-Paso "[simulado] Connect-IPPSSession" -Nivel Salta
}
else {
    try {
        Connect-IPPSSession -ShowBanner:$false -ErrorAction Stop
        Write-Paso "Conectado a Security & Compliance PowerShell" -Nivel Ok
    }
    catch {
        Add-Runbook -Estado $estado `
            -Titulo "Etiqueta de confidencialidad y DLP de IBAN" `
            -Motivo "No se pudo abrir sesión de Security & Compliance: $($_.Exception.Message)" `
            -Comando "Connect-IPPSSession   # necesita rol Compliance Administrator o Security Administrator"
        Write-Paso "Etapa 3 delegada al runbook." -Nivel Aviso
        return
    }
}

# --- 1. Etiqueta de confidencialidad ------------------------------------------
$tieneRol = Test-PermisoRol -Descripcion "administrar etiquetas de confidencialidad" -Sondeo {
    if ($sim) { return $true }
    Get-Label -ErrorAction Stop | Out-Null
}

if ($tieneRol) {
    $existe = if ($sim) { $null } else { Get-Label -Identity $pv.labelName -ErrorAction SilentlyContinue }
    if ($existe) {
        Write-Paso "Reutilizo la etiqueta '$($pv.labelDisplayName)'" -Nivel Salta
        $estado.propiedad["label"] = $false
    }
    elseif ($sim) {
        Write-Paso "[simulado] New-Label -Name $($pv.labelName) (cifrado, coautoría)" -Nivel Salta
    }
    else {
        New-Label `
            -Name $pv.labelName `
            -DisplayName $pv.labelDisplayName `
            -Tooltip $pv.labelTooltip `
            -EncryptionEnabled $true `
            -EncryptionProtectionType "Template" `
            -EncryptionRightsDefinitions "$($cfg.personas.platformAdmin.upn):VIEW,VIEWRIGHTSDATA,EDIT,DOCEDIT,PRINT,EXTRACT,OBJMODEL" `
            -ContentType "File, Email" | Out-Null
        Write-Paso "Etiqueta creada: $($pv.labelDisplayName)" -Nivel Ok
        $estado.propiedad["label"] = $true

        # Sin política de publicación, la etiqueta no aparece para nadie.
        $pol = Get-LabelPolicy -Identity $pv.labelPolicyName -ErrorAction SilentlyContinue
        if ($pol) {
            Set-LabelPolicy -Identity $pv.labelPolicyName -AddLabels $pv.labelName | Out-Null
            Write-Paso "Etiqueta añadida a la política existente" -Nivel Ok
        }
        else {
            New-LabelPolicy -Name $pv.labelPolicyName -Labels $pv.labelName -ExchangeLocation All | Out-Null
            Write-Paso "Política de publicación creada" -Nivel Ok
            $estado.propiedad["labelPolicy"] = $true
        }
    }
    $estado["labelName"] = $pv.labelName
}
else {
    Add-Runbook -Estado $estado `
        -Titulo "Crear la etiqueta '$($pv.labelDisplayName)' con cifrado" `
        -Motivo "La cuenta conectada no puede administrar etiquetas de confidencialidad." `
        -Comando @"
New-Label -Name '$($pv.labelName)' ``
    -DisplayName '$($pv.labelDisplayName)' ``
    -Tooltip '$($pv.labelTooltip)' ``
    -EncryptionEnabled `$true ``
    -EncryptionProtectionType 'Template' ``
    -EncryptionRightsDefinitions '$($cfg.personas.platformAdmin.upn):VIEW,VIEWRIGHTSDATA,EDIT,DOCEDIT,PRINT,EXTRACT,OBJMODEL' ``
    -ContentType 'File, Email'
New-LabelPolicy -Name '$($pv.labelPolicyName)' -Labels '$($pv.labelName)' -ExchangeLocation All
"@
}

# --- 2. DLP: bloquear respuestas con IBAN -------------------------------------
$tieneDlp = Test-PermisoRol -Descripcion "administrar políticas DLP" -Sondeo {
    if ($sim) { return $true }
    Get-DlpCompliancePolicy -ErrorAction Stop | Out-Null
}

if ($tieneDlp) {
    $existe = if ($sim) { $null } else { Get-DlpCompliancePolicy -Identity $pv.dlpPolicyName -ErrorAction SilentlyContinue }
    if ($existe) {
        Write-Paso "Reutilizo la política DLP '$($pv.dlpPolicyName)'" -Nivel Salta
    }
    elseif ($sim) {
        Write-Paso "[simulado] New-DlpCompliancePolicy + New-DlpComplianceRule (IBAN)" -Nivel Salta
    }
    else {
        # La ubicación de Microsoft 365 Copilot es la que cubre las respuestas de agentes.
        New-DlpCompliancePolicy `
            -Name $pv.dlpPolicyName `
            -Comment "Demo Bizz Summit 2026. Bloquea respuestas de agentes que contengan IBAN." `
            -Mode Enable `
            -MicrosoftCopilotLocation All | Out-Null
        Write-Paso "Política DLP creada" -Nivel Ok
        $estado.propiedad["dlpPolicy"] = $true

        New-DlpComplianceRule `
            -Name $pv.dlpRuleName `
            -Policy $pv.dlpPolicyName `
            -ContentContainsSensitiveInformation @{ Name = $pv.sensitiveInfoTypeName; minCount = $pv.sensitiveInfoMinCount } `
            -BlockAccess $true `
            -NotifyUser "LastModifier" `
            -Comment "Demo 2: el IBAN de $($cfg.datos.devolucionSensible) no puede salir en una respuesta." | Out-Null
        Write-Paso "Regla DLP creada sobre el tipo '$($pv.sensitiveInfoTypeName)'" -Nivel Ok
        $estado.propiedad["dlpRule"] = $true
    }
    $estado["dlpPolicyName"] = $pv.dlpPolicyName
}
else {
    Add-Runbook -Estado $estado `
        -Titulo "Crear la política DLP que bloquea IBAN en respuestas de agentes" `
        -Motivo "La cuenta conectada no puede administrar DLP de cumplimiento." `
        -Comando @"
New-DlpCompliancePolicy -Name '$($pv.dlpPolicyName)' ``
    -Mode Enable -MicrosoftCopilotLocation All
New-DlpComplianceRule -Name '$($pv.dlpRuleName)' ``
    -Policy '$($pv.dlpPolicyName)' ``
    -ContentContainsSensitiveInformation @{ Name = '$($pv.sensitiveInfoTypeName)'; minCount = $($pv.sensitiveInfoMinCount) } ``
    -BlockAccess `$true -NotifyUser 'LastModifier'
"@
}

Write-Paso "Etapa 3 completada. La propagación tarda: comprueba el bloqueo antes del evento." -Nivel Aviso
