#requires -Version 7.0
<#
    Etapa 4 — Dataverse.

    Crea una tabla por cada CSV de 01_datos/rag_copilot_studio/structured_csv,
    infiriendo el esquema del propio fichero, y las carga.

    Añade además la fila DEV-2026-0418 con su IBAN. Sin esa fila no hay beat 2
    en la demo 2: es el dato que Purview tiene que bloquear.
#>
[CmdletBinding()]
param([Parameter(Mandatory)]$Contexto)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSScriptRoot "../Common.psm1") -Force
Import-Module (Join-Path $PSScriptRoot "../Dataverse.psm1") -Force

$cfg = $Contexto.Config
$estado = $Contexto.Estado
$sim = $Contexto.Simular
$prefijo = $cfg.powerPlatform.publisherPrefix

$envUrl = $estado["defaultEnvironmentUrl"]
if (-not $envUrl) { throw "Falta la URL del entorno Default. Ejecuta antes la etapa 1." }
Write-Paso "Entorno destino: $envUrl" -Nivel Info

$token = if ($sim) { "simulado" } else { Get-DataverseToken -EnvironmentUrl $envUrl }

$csvDir = Join-Path $Contexto.RaizDatos "01_datos/rag_copilot_studio/structured_csv"
$csvs = Get-ChildItem -LiteralPath $csvDir -Filter "*.csv" -File | Sort-Object Name
Write-Paso "$($csvs.Count) CSV de origen" -Nivel Info

$tablas = @{}

foreach ($csv in $csvs) {
    $nombre = [IO.Path]::GetFileNameWithoutExtension($csv.Name)
    Write-Paso "Tabla $nombre" -Nivel Info

    $filas = Import-Csv -LiteralPath $csv.FullName -Encoding UTF8
    if ($filas.Count -eq 0) { Write-Paso "CSV vacío, se salta" -Nivel Salta; continue }

    $columnas = $filas[0].PSObject.Properties.Name
    $principal = $columnas[0]

    $tablaLogica = New-DataverseTabla -EnvironmentUrl $envUrl -Token $token `
        -NombreMostrado $nombre -Prefijo $prefijo -ColumnaPrincipal $principal -Simular:$sim
    Write-Paso "  entidad $tablaLogica" -Nivel Ok

    # Columnas: la primera va al campo principal, el resto se crean por inferencia
    $mapa = @{ $principal = "$($prefijo)_name" }
    foreach ($col in $columnas | Select-Object -Skip 1) {
        $muestra = $filas | Select-Object -First 200 | ForEach-Object { [string]$_.$col }
        $tipo = Get-TipoColumna -Muestra $muestra
        $logica = New-DataverseColumna -EnvironmentUrl $envUrl -Token $token `
            -TablaLogica $tablaLogica -NombreMostrado $col -Tipo $tipo -Prefijo $prefijo -Simular:$sim
        $mapa[$col] = $logica
        Write-Paso "  columna $col -> $logica ($($tipo.tipo))" -Nivel Info
    }

    # Dataverse tarda en publicar metadatos nuevos antes de aceptar filas
    if (-not $sim) { Start-Sleep -Seconds 5 }

    $conjunto = "$($tablaLogica)s"
    $registros = foreach ($fila in $filas) {
        $registro = [ordered]@{}
        foreach ($col in $columnas) {
            $valor = $fila.$col
            if ([string]::IsNullOrWhiteSpace([string]$valor)) { continue }
            $registro[$mapa[$col]] = $valor
        }
        $registro
    }

    $n = Add-DataverseFilas -EnvironmentUrl $envUrl -Token $token `
        -ConjuntoEntidades $conjunto -Filas $registros -Simular:$sim
    Write-Paso "  $n filas cargadas" -Nivel Ok

    $tablas[$nombre] = @{ logica = $tablaLogica; conjunto = $conjunto; mapa = $mapa }
}

# --- La fila que hace posible la demo 2 ---------------------------------------
$devTabla = $tablas.Keys | Where-Object { $_ -match "Devolucion" } | Select-Object -First 1
if (-not $devTabla) {
    Write-Paso "No hay tabla de devoluciones: la fila con IBAN queda pendiente." -Nivel Aviso
}
else {
    $t = $tablas[$devTabla]
    $ibanLogica = New-DataverseColumna -EnvironmentUrl $envUrl -Token $token `
        -TablaLogica $t.logica -NombreMostrado "IBANReembolso" `
        -Tipo @{ tipo = "String"; longitud = 34 } -Prefijo $prefijo -Simular:$sim
    Write-Paso "Columna $ibanLogica añadida a $($t.logica)" -Nivel Ok

    $fila = [ordered]@{
        "$($prefijo)_name" = $cfg.datos.devolucionSensible
        $ibanLogica        = $cfg.datos.ibanSintetico
    }
    Add-DataverseFilas -EnvironmentUrl $envUrl -Token $token `
        -ConjuntoEntidades $t.conjunto -Filas @($fila) -Simular:$sim | Out-Null
    Write-Paso "Fila $($cfg.datos.devolucionSensible) creada con IBAN sintético" -Nivel Ok
    $estado["devolucionSensibleTabla"] = $t.logica
}

$estado["dataverseTablas"] = $tablas.Keys | Sort-Object
$estado.propiedad["dataverseTablas"] = $true
Write-Paso "Etapa 4 completada." -Nivel Ok
