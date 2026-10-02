#requires -Version 7.0
<#
    Dataverse.psm1 — creación de tablas y carga de datos por Web API.

    No hay cmdlet para "crea una tabla a partir de este CSV", así que el módulo
    infiere el esquema leyendo el propio CSV. Eso evita mantener un esquema
    duplicado que se desincroniza del dato en cuanto alguien toca una columna.
#>

Set-StrictMode -Version 1.0

function Get-DataverseToken {
    param([Parameter(Mandatory)][string]$EnvironmentUrl)
    $recurso = ([Uri]$EnvironmentUrl).GetLeftPart([UriPartial]::Authority)
    $json = az account get-access-token --resource "https://$recurso" --output json 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $json) {
        throw "No se pudo obtener token para $EnvironmentUrl. Ejecuta 'az login' contra el tenant correcto."
    }
    return ($json | ConvertFrom-Json).accessToken
}

function Invoke-DataverseApi {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$Token,
        [Parameter(Mandatory)][string]$Ruta,
        [ValidateSet("GET", "POST", "PATCH", "DELETE")][string]$Metodo = "GET",
        $Cuerpo,
        [switch]$TolerarError
    )
    $uri = "$($EnvironmentUrl.TrimEnd('/'))/api/data/v9.2/$Ruta"
    $cabeceras = @{
        Authorization    = "Bearer $Token"
        Accept           = "application/json"
        "OData-Version"  = "4.0"
        "OData-MaxVersion" = "4.0"
    }
    $parametros = @{ Uri = $uri; Method = $Metodo; Headers = $cabeceras; ErrorAction = "Stop" }
    if ($null -ne $Cuerpo) {
        $parametros.Body = ($Cuerpo | ConvertTo-Json -Depth 12 -Compress)
        $parametros.ContentType = "application/json; charset=utf-8"
    }
    try {
        return Invoke-RestMethod @parametros
    }
    catch {
        if ($TolerarError) { return $null }
        $detalle = $_.ErrorDetails.Message
        throw "Dataverse $Metodo $Ruta falló: $($_.Exception.Message)`n$detalle"
    }
}

function ConvertTo-NombreLogico {
    param([Parameter(Mandatory)][string]$Texto, [string]$Prefijo = "fsh")
    $limpio = ($Texto -replace "[^A-Za-z0-9]", "").ToLowerInvariant()
    if ([string]::IsNullOrWhiteSpace($limpio)) { throw "Nombre no convertible: '$Texto'" }
    return "${Prefijo}_$limpio"
}

function Get-TipoColumna {
    <#
        Infiere el tipo de una columna a partir de una muestra de valores.
        Conservador: ante la duda, texto. Un decimal mal inferido rompe la carga;
        un texto de más solo es feo.
    #>
    param([string[]]$Muestra)

    $valores = $Muestra | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    if ($valores.Count -eq 0) { return @{ tipo = "String"; longitud = 100 } }

    $cultura = [Globalization.CultureInfo]::InvariantCulture
    $todosEnteros = $true
    $todosDecimales = $true
    $todasFechas = $true
    foreach ($v in $valores) {
        $i = 0; $d = 0.0; $f = [datetime]::MinValue
        if (-not [int]::TryParse($v, [ref]$i)) { $todosEnteros = $false }
        if (-not [double]::TryParse($v, [Globalization.NumberStyles]::Any, $cultura, [ref]$d)) { $todosDecimales = $false }
        if (-not [datetime]::TryParse($v, $cultura, [Globalization.DateTimeStyles]::None, [ref]$f)) { $todasFechas = $false }
    }
    if ($todosEnteros) { return @{ tipo = "Integer" } }
    if ($todasFechas) { return @{ tipo = "DateTime" } }
    if ($todosDecimales) { return @{ tipo = "Decimal" } }

    $maxima = ($valores | Measure-Object -Property Length -Maximum).Maximum
    $longitud = [Math]::Min(4000, [Math]::Max(100, [int]($maxima * 1.5)))
    return @{ tipo = "String"; longitud = $longitud }
}

function New-DataverseTabla {
    <#
        Crea la tabla si no existe. Devuelve el LogicalName. Idempotente.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$Token,
        [Parameter(Mandatory)][string]$NombreMostrado,
        [Parameter(Mandatory)][string]$Prefijo,
        [Parameter(Mandatory)][string]$ColumnaPrincipal,
        [switch]$Simular
    )
    $logico = ConvertTo-NombreLogico -Texto $NombreMostrado -Prefijo $Prefijo
    $esquema = ($logico -replace "^${Prefijo}_", "$($Prefijo)_")

    $existe = Invoke-DataverseApi -EnvironmentUrl $EnvironmentUrl -Token $Token -TolerarError `
        -Ruta "EntityDefinitions(LogicalName='$logico')?`$select=LogicalName"
    if ($existe) {
        Write-Verbose "Tabla $logico ya existe"
        return $logico
    }
    if ($Simular) {
        Write-Verbose "[simulado] Crearía la tabla $logico"
        return $logico
    }

    $cuerpo = [ordered]@{
        "@odata.type"           = "Microsoft.Dynamics.CRM.EntityMetadata"
        SchemaName              = $esquema
        LogicalName             = $logico
        DisplayName             = @{ LocalizedLabels = @(@{ Label = $NombreMostrado; LanguageCode = 3082 }) }
        DisplayCollectionName   = @{ LocalizedLabels = @(@{ Label = $NombreMostrado; LanguageCode = 3082 }) }
        OwnershipType           = "UserOwned"
        HasActivities           = $false
        HasNotes                = $false
        IsActivity              = $false
        Attributes              = @(
            [ordered]@{
                "@odata.type" = "Microsoft.Dynamics.CRM.StringAttributeMetadata"
                SchemaName    = "$($Prefijo)_name"
                LogicalName   = "$($Prefijo)_name"
                MaxLength     = 200
                IsPrimaryName = $true
                RequiredLevel = @{ Value = "ApplicationRequired" }
                DisplayName   = @{ LocalizedLabels = @(@{ Label = $ColumnaPrincipal; LanguageCode = 3082 }) }
                AttributeType = "String"
                AttributeTypeName = @{ Value = "StringType" }
            }
        )
    }
    Invoke-DataverseApi -EnvironmentUrl $EnvironmentUrl -Token $Token -Metodo POST -Ruta "EntityDefinitions" -Cuerpo $cuerpo | Out-Null
    return $logico
}

function New-DataverseColumna {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$Token,
        [Parameter(Mandatory)][string]$TablaLogica,
        [Parameter(Mandatory)][string]$NombreMostrado,
        [Parameter(Mandatory)][hashtable]$Tipo,
        [Parameter(Mandatory)][string]$Prefijo,
        [switch]$Simular
    )
    $logico = ConvertTo-NombreLogico -Texto $NombreMostrado -Prefijo $Prefijo

    $existe = Invoke-DataverseApi -EnvironmentUrl $EnvironmentUrl -Token $Token -TolerarError `
        -Ruta "EntityDefinitions(LogicalName='$TablaLogica')/Attributes(LogicalName='$logico')?`$select=LogicalName"
    if ($existe) { return $logico }
    if ($Simular) { return $logico }

    $etiqueta = @{ LocalizedLabels = @(@{ Label = $NombreMostrado; LanguageCode = 3082 }) }
    $cuerpo = switch ($Tipo.tipo) {
        "Integer" {
            [ordered]@{
                "@odata.type" = "Microsoft.Dynamics.CRM.IntegerAttributeMetadata"
                AttributeType = "Integer"; AttributeTypeName = @{ Value = "IntegerType" }
                MinValue = -2147483648; MaxValue = 2147483647
            }
        }
        "Decimal" {
            [ordered]@{
                "@odata.type" = "Microsoft.Dynamics.CRM.DecimalAttributeMetadata"
                AttributeType = "Decimal"; AttributeTypeName = @{ Value = "DecimalType" }
                Precision = 2; MinValue = -100000000000; MaxValue = 100000000000
            }
        }
        "DateTime" {
            [ordered]@{
                "@odata.type" = "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata"
                AttributeType = "DateTime"; AttributeTypeName = @{ Value = "DateTimeType" }
                Format = "DateOnly"; DateTimeBehavior = @{ Value = "DateOnly" }
            }
        }
        default {
            [ordered]@{
                "@odata.type" = "Microsoft.Dynamics.CRM.StringAttributeMetadata"
                AttributeType = "String"; AttributeTypeName = @{ Value = "StringType" }
                MaxLength = $Tipo.longitud
            }
        }
    }
    $cuerpo.SchemaName = $logico
    $cuerpo.LogicalName = $logico
    $cuerpo.DisplayName = $etiqueta
    $cuerpo.RequiredLevel = @{ Value = "None" }

    Invoke-DataverseApi -EnvironmentUrl $EnvironmentUrl -Token $Token -Metodo POST `
        -Ruta "EntityDefinitions(LogicalName='$TablaLogica')/Attributes" -Cuerpo $cuerpo | Out-Null
    return $logico
}

function Add-DataverseFilas {
    <#
        Carga por lotes con $batch. Dataverse admite 1000 operaciones por lote;
        se usan 100 para que un fallo sea fácil de leer.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$Token,
        [Parameter(Mandatory)][string]$ConjuntoEntidades,
        [Parameter(Mandatory)][object[]]$Filas,
        [int]$TamanoLote = 100,
        [switch]$Simular
    )
    if ($Simular) {
        Write-Verbose "[simulado] Insertaría $($Filas.Count) filas en $ConjuntoEntidades"
        return $Filas.Count
    }
    $insertadas = 0
    for ($i = 0; $i -lt $Filas.Count; $i += $TamanoLote) {
        $lote = $Filas[$i..([Math]::Min($i + $TamanoLote - 1, $Filas.Count - 1))]
        foreach ($fila in $lote) {
            Invoke-DataverseApi -EnvironmentUrl $EnvironmentUrl -Token $Token -Metodo POST `
                -Ruta $ConjuntoEntidades -Cuerpo $fila | Out-Null
            $insertadas++
        }
        Write-Verbose "$insertadas / $($Filas.Count)"
    }
    return $insertadas
}

Export-ModuleMember -Function `
    Get-DataverseToken, Invoke-DataverseApi, ConvertTo-NombreLogico, Get-TipoColumna, `
    New-DataverseTabla, New-DataverseColumna, Add-DataverseFilas
