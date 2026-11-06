# Convenciones

Las convenciones se deciden una vez y se cumplen siempre. Cambiar una requiere un ADR en `docs/adr/`.

## Workspaces
`<proyecto>-<función>-<entorno>`

| Función | Contenido | Quién escribe |
|---|---|---|
| `datos` | Lakehouses `lh_bronze`, `lh_silver`, `lh_gold` | Solo la identidad de los pipelines |
| `ing` | Notebooks, pipelines, Environment `env_fwk` | Ingeniería de datos |
| `ana` | Modelos semánticos e informes | Analítica / BI |

Entornos: `dev`, `test`, `prod`. Además, cada persona trabaja en un workspace de feature
(`<proyecto>-ing-feat-<iniciales>`) creado con *branch out* desde su rama.

## Lakehouses y tablas
- Capas: `lh_bronze` (raw, append-only), `lh_silver` (limpio y conforme a contrato), `lh_gold` (modelo de consumo)
- Tablas silver: `<entidad>` en singular de negocio (`pedidos`, `clientes`)
- Tablas gold: `fact_<hecho>_<grano>` y `dim_<entidad>`
- Cuarentena nueva: `silver.fwk_cuarentena`, evidencias JSON por fuente/observación/versión de contrato
- Las antiguas `_cuarentena_<tabla>` se conservan como legado; no se migran automáticamente
- Auditoría del framework: `fwk_ejecuciones` en silver
- Control: `fwk_lotes`, `fwk_marcas` y `fwk_modelos` en silver; todos tienen contrato
- Ficheros de entrada: `lh_bronze/Files/landing/<dominio>/<fuente>/`
- Configuración publicada: `lh_bronze/Files/_framework/`

## Columnas
- `snake_case`, sin tildes ni ñ, en español de negocio
- Técnicas con prefijo `_`: `_ingested_at`, `_source`, `_batch_id`, `_motivo_rechazo`
- Observación de origen: `_observado_en` estable por lote y `_source_updated_at` si hay marca SQL o CSV
- Dimensiones SCD2: `id_version`, `vigente_desde`, `vigente_hasta`, `es_actual`, `_hash_scd2`, `_batch_id`
- SCD2 usa intervalos UTC de observación `[desde, hasta)`; hasta NULL significa versión vigente
- Fechas `fecha_<qué>`, importes `importe_<qué>`, indicadores `es_<qué>` o `tiene_<qué>`, identificadores `id_<entidad>`

## Notebooks y pipelines
- `nb_<nn>_<capa>_<propósito>`: `10` bronze, `20` silver, `30` gold, `90` operación
- `pl_<propósito>` para pipelines de orquestación

## Código
- Toda la lógica en `src/datafwk/`; los notebooks solo orquestan
- Ramas: `feat/<descripción>`, `fix/<descripción>`; PR obligatorio contra `main`
- Commits en español, en imperativo: `Añade fuente devoluciones`

## Evolución declarativa

- Contratos con `version` positiva (1 por defecto); incrementar al cambiar una condición de calidad o el grano
- Extracción en `fuentes.extraccion`; escritura silver en `modo_carga`; historia gold en `config/modelos/`
- SCD2 exige clasificar todos los atributos no clave y declarar el contrato histórico y el de proyección actual
- Un escritor por fuente/modelo; mantener el mismo `batch_id` para reintentar y no iniciar otro mientras quede pendiente
- Las mutaciones se aplican en el origen: SQL para el recorrido conectado o CSV de trabajo para el laboratorio portable.
  El CSV original se conserva con hashes; no se manipula el DataFrame extraído para simular errores.
- ADR y procedimiento: `docs/adr/0002-evolucion-cargas-calidad-historia.md` y `docs/runbooks/workshop-evolutivo.md`
