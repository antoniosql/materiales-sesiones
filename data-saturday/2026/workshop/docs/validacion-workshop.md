# Entrega del framework evolutivo · 2026-10-31

Repositorio inicializado en `main` con la plantilla original (`bca65cf`). Implementación en
`feat/framework-evolutivo-workshop`, versión de biblioteca `0.2.0`. No hay remoto configurado.

## Contenido implementado

- Generador de proyecto independiente, sustitución de nombres y renovación de los `logicalId` de Fabric.
- Lectura SQL nativa con proyección declarativa, conexión por entorno y autenticación de la identidad de Fabric.
- Extracción completa/incremental independiente de la escritura silver y de la historificación gold.
- Lotes, marcas y versiones Delta persistidos; reintentos desde bronze sin releer el origen mutable.
- Cuarentena con dato bruto y versión de contrato; revalidación de filas aceptadas y rechazadas; política fallar.
- Dimensión tipo1, activación explícita SCD2, cierre/alta en un MERGE, intervalos de observación y proyección actual.
- Notebooks de gold, revalidación y activación; cinco checkpoints copiables y cuatro prompts de evolución.
- API de publicación del wheel actualizada a subida binaria y publicación estable con seguimiento de operación 202.

Recorrido paso a paso: [runbook de cuatro horas](runbooks/workshop-evolutivo.md).

## Verificación local

- `pytest --delta -q`: **80 pruebas correctas**, sin omisiones, en 238,98 segundos.
- `pre-commit run --all-files`: correcto, incluidos secretos, Ruff, mypy, contratos, catálogo, SQL y Terraform.
  El hook de modelos no tiene archivos activos que revisar: los modelos de ejemplo están en `templates/` y
  `tests/contracts/test_workshop.py` verifica sus esquemas y referencias en cada checkpoint.
- Generación completa en carpeta temporal independiente: 161 archivos y ocho GUID nuevos; referencias y reglas
  del framework correctas. Copia temporal eliminada después de comprobarla.
- Wheel `datafwk-0.2.0-py3-none-any.whl` construido y contenido comprobado; artefacto local en `.herramientas/wheels/`.
- `git diff --check`: correcto.

Las pruebas cubren SCD2 A→B→A, nulos, repetición, cambios tipo1, unicidad e intervalos; calidad con ANSI activado;
ventanas y validación de SQL; generación greenfield; checkpoints y carga de configuración; publicación HTTP 200/202.
Los escenarios Delta escriben tablas reales locales y simulan únicamente la lectura SQL. Comprueban revalidación,
fallo sin publicación, marcas, migración y recuperación entre histórico y proyección.

Runtime local: Python 3.12, Spark 3.5, Delta 3.3.2 y Java 17. En Windows las pruebas Delta usaron utilidades nativas
Hadoop 3.3.5, instaladas solo en `.herramientas/` (compilación del repositorio cdarlint/winutils,
commit `7386986d5d8a079b5cd4464f4599766dd27e7d13`). CI ejecuta `pytest --delta` en Linux/Python 3.11.

## Contratos y compatibilidad que deben revisarse

- Cinco contratos técnicos nuevos: `fwk_lotes`, `fwk_marcas`, `fwk_modelos`, `fwk_cuarentena`, `fwk_ejecuciones`.
- El esquema admite versión del contrato, clave de negocio separada y columnas técnicas declaradas.
- Los checkpoints Q2/Q3 cambian explícitamente el contrato de devoluciones; el checkpoint SCD2 cambia el grano y la
  clave de `dim_cliente` y añade `dim_cliente_actual`. Deben anunciarse al consumidor al aplicar esos checkpoints.
- `a_silver` requiere lote explícito. La revalidación reemplaza el uso anterior de un batch vacío.
- La auditoría añade `filas_consolidadas` y usa `dominio.fuente`. La cuarentena nueva se guarda en `fwk_cuarentena`.
  `filas_escritas` expresa claves aceptadas, incluidas las que no cambian, no el contador físico de modificaciones Delta.
- Los timestamps leídos desde Spark se convierten mediante epoch; no se confunden datetimes locales de Windows con UTC.

## Revisión de checklist y límites pendientes

Contratos antes de código, catálogo regenerado, notebooks derivados de plantilla con GUID únicos, lógica en biblioteca,
tests, ADR, trazabilidad y reglas declarativas revisados. Las reglas Q1–Q3 son las del caso docente, no nuevas definiciones
universales de negocio. No se ha definido ningún KPI adicional.

Pendiente de ensayo en un entorno real: autenticación Entra, permisos y conectividad SQL/OneLake, asociación del
Environment, publicación remota, serialización de pipelines y consumo Power BI. Las pruebas locales no certifican
estos puntos. No se ejecutaron mutaciones en bases SQL ni despliegues en Fabric. Analítica no fue modificada;
BPA/Fab Inspector no aplican a este cambio.

Requiere un escritor por fuente/modelo y conservar las versiones usadas por operaciones pendientes. No hay transacción
distribuida entre tablas. La marca temporal no captura borrados físicos ni garantiza cambios tardíos fuera del solape.
La revalidación completa está pensada para el tamaño de la demo. El cierre automático de evidencias de cuarentena,
CDC, historia retroactiva y reclasificación de atributos de una dimensión ya SCD2 quedan fuera de esta implementación.

Excepciones de linter justificadas en la misma línea: `S608` en SQL generado exclusivamente con identificadores
validados y datetimes tipados; `S105` para el marcador `<token>` de una prueba, que no contiene un secreto.
Se conservan las excepciones que ya tenía la plantilla y se explica el import tardío del validador.

API verificada contra documentación oficial:
[subida de bibliotecas](https://learn.microsoft.com/en-us/rest/api/fabric/environment/staging/upload-custom-library)
y [publicación estable](https://learn.microsoft.com/en-us/rest/api/fabric/environment/items/publish-environment).
