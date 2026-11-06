# Catálogo de datos

> Generado por `scripts/generar_catalogo.py` desde `contracts/`. No editar a mano.

## silver

### `clientes`

Un cliente por fila, con su segmento comercial vigente.

- **Dominio:** ventas · **Propietario:** @org/negocio-ventas
- **Clave:** id_cliente · **Si incumple el contrato:** cuarentena

| Columna | Tipo | Nulos | Valores | Descripción |
|---|---|---|---|---|
| `id_cliente` | string | no |  | Identificador único del cliente |
| `fecha_alta` | date | no |  | Fecha de alta como cliente |
| `segmento` | string | sí | particular, profesional, empresa | Segmento comercial |
| `provincia` | string | sí |  | Provincia de residencia o domicilio fiscal |
| `acepta_comunicaciones` | boolean | no |  | Consentimiento de comunicaciones comerciales |

### `fwk_cuarentena`

Evidencias de rechazo por fuente, observacion y version de contrato. Conserva el dato bruto.

- **Dominio:** framework · **Propietario:** @org/plataforma
- **Clave:** id_rechazo · **Si incumple el contrato:** fallar

| Columna | Tipo | Nulos | Valores | Descripción |
|---|---|---|---|---|
| `id_rechazo` | string | no |  | Hash de identidad de la evidencia |
| `fuente` | string | no |  | Dominio y fuente |
| `batch_id` | string | no |  | Lote que produjo la observacion |
| `observado_en` | timestamp | no |  | Instante de observacion UTC |
| `version_contrato` | int | no |  | Version que rechazo la fila |
| `dato_bruto` | string | no |  | JSON previo a conversiones de tipo |
| `motivos` | string | no |  | Array JSON de motivos de rechazo |
| `resuelta_en` | timestamp | sí |  | Reservado para una resolucion explicita de la evidencia |

### `fwk_ejecuciones`

Intentos de ejecucion y reconciliacion de filas; escritas cuenta claves aceptadas, incluso sin cambios.

- **Dominio:** framework · **Propietario:** @org/plataforma
- **Clave:** batch_id, capa, fuente, inicio · **Si incumple el contrato:** fallar

| Columna | Tipo | Nulos | Valores | Descripción |
|---|---|---|---|---|
| `batch_id` | string | no |  | Identificador reutilizado en reintentos |
| `entorno` | string | no |  | Entorno configurado |
| `capa` | string | no |  | Etapa ejecutada |
| `fuente` | string | no |  | Fuente o modelo procesado |
| `tabla` | string | no |  | Tabla destino |
| `inicio` | timestamp | no |  | Inicio del intento UTC |
| `fin` | timestamp | sí |  | Fin del intento UTC |
| `filas_leidas` | bigint | no |  | Filas evaluadas |
| `filas_escritas` | bigint | no |  | Claves aceptadas incluidas las que ya existian sin cambios |
| `filas_rechazadas` | bigint | no |  | Filas que incumplen el contrato |
| `filas_consolidadas` | bigint | no |  | Observaciones anteriores o duplicadas descartadas |
| `estado` | string | no |  | Resultado del intento |
| `mensaje` | string | no |  | Diagnostico operativo sin secretos |

### `fwk_lotes`

Estado recuperable de un lote de extracción y publicación silver.

- **Dominio:** framework · **Propietario:** @org/plataforma
- **Clave:** fuente, batch_id · **Si incumple el contrato:** fallar

| Columna | Tipo | Nulos | Valores | Descripción |
|---|---|---|---|---|
| `fuente` | string | no |  | Dominio y fuente de la carga |
| `batch_id` | string | no |  | Identificador estable del lote |
| `estado` | string | no |  | Fase persistida de la carga |
| `observado_en` | timestamp | no |  | Instante UTC fijado al planificar |
| `desde` | timestamp | sí |  | Límite inferior inclusivo si es incremental |
| `hasta` | timestamp | no |  | Límite superior inclusivo de la extracción |
| `modo` | string | no |  | Estrategia completa o incremental |
| `version_bronze` | bigint | sí |  | Versión Delta con la imagen de entrada |
| `version_silver` | bigint | sí |  | Versión Delta publicada para consumidores |
| `version_contrato` | int | no |  | Revisión del contrato aplicado |

### `fwk_marcas`

Último límite de extracción confirmado por fuente dentro del entorno.

- **Dominio:** framework · **Propietario:** @org/plataforma
- **Clave:** fuente · **Si incumple el contrato:** fallar

| Columna | Tipo | Nulos | Valores | Descripción |
|---|---|---|---|---|
| `fuente` | string | no |  | Dominio y fuente de la carga |
| `hasta` | timestamp | no |  | Límite confirmado sin retrocesos |
| `batch_id` | string | no |  | Lote que confirmó la marca |

### `fwk_modelos`

Última publicación de un modelo y su fase pendiente recuperable.

- **Dominio:** framework · **Propietario:** @org/plataforma
- **Clave:** modelo · **Si incumple el contrato:** fallar

| Columna | Tipo | Nulos | Valores | Descripción |
|---|---|---|---|---|
| `firma_historia` | string | no |  | Firma de claves y atributos SCD2; vacia en tipo1, impide reclasificar historia sin migracion |
| `firma_config` | string | no |  | Hash de la configuracion y contratos usados; impide cambiarlos durante un reintento |
| `migracion` | boolean | no |  | Activacion explicita de SCD2 sobre una dimension tipo 1 |
| `version_previa` | bigint | sí |  | Version gold anterior a este lote para recuperar y auditar la migracion |
| `modelo` | string | no |  | Nombre del modelo gold |
| `batch_id` | string | no |  | Lote origen o identificador de migración |
| `observado_en` | timestamp | no |  | Instante UTC estable de publicación |
| `estado` | string | no |  | Pendiente o confirmado |
| `version_silver` | bigint | no |  | Versión fijada de entrada |
| `version_gold` | bigint | sí |  | Versión histórica publicada |

### `pedidos`

Un pedido de cliente por fila, en cualquier canal de venta.

- **Dominio:** ventas · **Propietario:** @org/negocio-ventas
- **Clave:** id_pedido · **Si incumple el contrato:** cuarentena

| Columna | Tipo | Nulos | Valores | Descripción |
|---|---|---|---|---|
| `id_pedido` | string | no |  | Identificador del pedido en el sistema origen |
| `id_cliente` | string | no |  | Cliente que hace el pedido |
| `fecha_pedido` | date | no |  | Fecha en que se confirma el pedido |
| `canal` | string | no | tienda, web, app | Canal de venta |
| `importe_total` | decimal(12,2) | no |  | Importe con impuestos, en euros |
| `estado` | string | sí | confirmado, enviado, entregado, cancelado | Estado actual |

**Reglas:**

- `importe_no_negativo`: `importe_total >= 0` — Un pedido no puede tener importe negativo; las devoluciones van en su propia tabla
- `fecha_no_futura`: `fecha_pedido <= current_date()` — Ningún pedido puede estar fechado en el futuro

## gold

### `fact_ventas_diarias`

Ventas agregadas por día y canal. Base de los informes de ventas.

- **Dominio:** ventas · **Propietario:** @org/negocio-ventas
- **Clave:** fecha, canal · **Si incumple el contrato:** fallar

| Columna | Tipo | Nulos | Valores | Descripción |
|---|---|---|---|---|
| `fecha` | date | no |  | Día natural |
| `canal` | string | no | tienda, web, app | Canal de venta |
| `num_pedidos` | int | no |  | Pedidos no cancelados del día |
| `importe_ventas` | decimal(14,2) | no |  | Ver 'Ventas netas' en docs/glosario.md |

**Reglas:**

- `pedidos_positivos`: `num_pedidos > 0`
