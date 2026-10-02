#requires -Version 7.0
<#
.SYNOPSIS
    Genera FS-KB-11, el documento que la demo 2 no debe poder leer.

.DESCRIPTION
    Construye un .docx mínimo pero válido (OOXML empaquetado a mano, sin
    dependencias externas) con un listado ficticio de clientes con patrones
    anómalos de devolución.

    Todos los datos son inventados. El documento existe para llevar encima una
    etiqueta de confidencialidad con cifrado y vivir en un sitio de SharePoint
    que la política de datos deja fuera del alcance del agente.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Destino,
    $Config
)

Set-StrictMode -Version 1.0
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$clientes = @(
    @{ Cliente = "CL-004182"; Nombre = "H. V."; Devoluciones = 14; ImporteEUR = "3.418,20"; Patron = "Cuatro devoluciones del mismo pedido en cinco días" }
    @{ Cliente = "CL-007731"; Nombre = "M. C."; Devoluciones = 11; ImporteEUR = "2.905,00"; Patron = "Compra y devuelve sistemáticamente en campaña" }
    @{ Cliente = "CL-002094"; Nombre = "J. R. S."; Devoluciones = 9;  ImporteEUR = "2.140,75"; Patron = "Devoluciones sin ticket en tres tiendas distintas" }
    @{ Cliente = "CL-009003"; Nombre = "A. P."; Devoluciones = 8;  ImporteEUR = "1.980,40"; Patron = "Motivo R04 declarado siempre fuera de las 72 horas" }
    @{ Cliente = "CL-001566"; Nombre = "L. G. M."; Devoluciones = 7;  ImporteEUR = "1.744,10"; Patron = "Reembolso solicitado siempre a cuenta distinta del pago" }
    @{ Cliente = "CL-005410"; Nombre = "F. D."; Devoluciones = 7;  ImporteEUR = "1.612,90"; Patron = "Devuelve solo artículos OUTLET, excluidos por política" }
    @{ Cliente = "CL-008827"; Nombre = "S. N. B."; Devoluciones = 6;  ImporteEUR = "1.455,30"; Patron = "Coincidencia de dirección con otros dos expedientes" }
    @{ Cliente = "CL-003318"; Nombre = "R. M."; Devoluciones = 6;  ImporteEUR = "1.402,00"; Patron = "Alta y baja de fidelización en el mismo trimestre" }
)

function Get-XmlEscapado { param([string]$T) return [Security.SecurityElement]::Escape($T) }

function New-Parrafo {
    param([string]$Texto, [switch]$Titulo, [switch]$Subtitulo, [switch]$Negrita)
    $estilo = if ($Titulo) { "Title" } elseif ($Subtitulo) { "Heading1" } else { "Normal" }
    $rPr = if ($Negrita -or $Titulo) { "<w:rPr><w:b/></w:rPr>" } else { "" }
    return "<w:p><w:pPr><w:pStyle w:val=`"$estilo`"/></w:pPr><w:r>$rPr<w:t xml:space=`"preserve`">$(Get-XmlEscapado $Texto)</w:t></w:r></w:p>"
}

$cuerpo = [Text.StringBuilder]::new()
[void]$cuerpo.Append((New-Parrafo -Titulo -Texto "FS-KB-11 · Clientes con devoluciones anómalas — 2026 Q1"))
$etiqueta = if ($Config -and $Config.purview) { $Config.purview.labelDisplayName } else { "Confidencial – Prevención de Pérdidas" }
[void]$cuerpo.Append((New-Parrafo -Texto "$etiqueta. Distribución restringida."))
[void]$cuerpo.Append((New-Parrafo -Texto "Documento sintético para demostración. Todos los datos son ficticios."))
[void]$cuerpo.Append((New-Parrafo -Subtitulo -Texto "1. Alcance"))
[void]$cuerpo.Append((New-Parrafo -Texto "Expedientes abiertos por el equipo de Prevención de Pérdidas sobre patrones de devolución que superan los umbrales de FS-KB-08. Este listado no debe compartirse con atención al cliente ni con personal de tienda, ni ser accesible por asistentes automáticos."))
[void]$cuerpo.Append((New-Parrafo -Subtitulo -Texto "2. Expedientes"))

foreach ($c in $clientes) {
    $linea = "$($c.Cliente) · $($c.Nombre) · $($c.Devoluciones) devoluciones · $($c.ImporteEUR) EUR · $($c.Patron)"
    [void]$cuerpo.Append((New-Parrafo -Texto $linea))
}

[void]$cuerpo.Append((New-Parrafo -Subtitulo -Texto "3. Procedimiento"))
[void]$cuerpo.Append((New-Parrafo -Texto "Ningún expediente se comunica al cliente. La resolución la firma el responsable de Prevención de Pérdidas junto con el Store Manager de la tienda implicada. Cualquier consulta llega por caso interno, nunca por el asistente de devoluciones."))

$documentXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    $($cuerpo.ToString())
    <w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr>
  </w:body>
</w:document>
"@

$contentTypes = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"@

$rels = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"@

$carpeta = Split-Path -Parent $Destino
if ($carpeta -and -not (Test-Path -LiteralPath $carpeta)) {
    New-Item -ItemType Directory -Path $carpeta -Force | Out-Null
}
if (Test-Path -LiteralPath $Destino) { Remove-Item -LiteralPath $Destino -Force }

$zip = [IO.Compression.ZipFile]::Open($Destino, [IO.Compression.ZipArchiveMode]::Create)
try {
    foreach ($parte in @(
            @{ Ruta = "[Content_Types].xml"; Contenido = $contentTypes }
            @{ Ruta = "_rels/.rels";          Contenido = $rels }
            @{ Ruta = "word/document.xml";    Contenido = $documentXml }
        )) {
        $entrada = $zip.CreateEntry($parte.Ruta, [IO.Compression.CompressionLevel]::Optimal)
        $flujo = New-Object IO.StreamWriter($entrada.Open(), [Text.UTF8Encoding]::new($false))
        $flujo.Write($parte.Contenido)
        $flujo.Dispose()
    }
}
finally {
    $zip.Dispose()
}

Write-Host "Generado $Destino ($($clientes.Count) expedientes ficticios)" -ForegroundColor Green
Write-Host "Recuerda: hay que aplicarle la etiqueta de confidencialidad antes de la demo." -ForegroundColor Yellow
