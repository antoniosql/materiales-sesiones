# ADR 0002 · Extracción, calidad e historia independientes

- Estado: aceptado para la implementación del framework
- Fecha: 2026-10-31

## Decisión

La extracción completa o incremental pertenece a la fuente; append/merge/overwrite
pertenece a silver; tipo 1/SCD2 pertenece al modelo gold. Las fuentes de ficheros
existentes mantienen sus valores por defecto.

Los lotes conservan límites, instante UTC de observación y versiones Delta.
Se reanuda desde bronze y solo se confirma la marca después de silver y cuarentena.
Los consumidores gold leen la versión silver del lote, en orden.
Los escritores se serializan por fuente y modelo mediante la orquestación:
el registro de un lote pendiente detecta conflictos pero no sustituye un bloqueo distribuido.

La marca temporal requiere un origen que actualice su columna de modificación.
No captura borrados físicos ni todos los estados intermedios; tampoco garantiza
capturar transacciones arbitrariamente tardías. El solape no es CDC.

La revalidación evalúa también filas antes aceptadas, conserva evidencia por versión
del contrato y reemplaza la proyección vigente. Fallar valida antes de publicar.

SCD2 conserva tiempo de observación desde una migración explícita. Se separa la
clave de negocio de la clave de versión, con intervalos [desde, hasta).
La salida actual mantiene una fila por entidad. No se inventa historia anterior.

## Consecuencias

No hay una transacción distribuida entre tablas Delta. Cada fase es reintentable;
se conservan las versiones necesarias y se detienen consumidores hasta completar
una publicación. No ejecutar VACUUM sobre versiones aún necesarias.

Los contratos de control y de salida histórica preceden a su implementación.
Cambios de grano, versión de contrato y contabilidad se anuncian a consumidores.
La publicación de items no ejecuta migraciones de datos de forma implícita.
