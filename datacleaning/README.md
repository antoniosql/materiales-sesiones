# FraSoHome — Caso Retail Omnicanal (Datos + Notebooks + Streamlit)

Repositorio formativo para el caso **FraSoHome**, una cadena **ficticia** de retail de hogar y decoración en entorno **B2C omnicanal** (tiendas físicas + e-commerce). Incluye:

- **Fuentes de datos simuladas (CSV UTF-8)** con **errores intencionales** de calidad (nulos, duplicados, formatos heterogéneos, claves huérfanas, anomalías).
- **Notebooks (1–8)** que guían el ciclo completo: ingesta → perfilado → limpieza → integración → features → ML-ready 

> ⚠️ **Importante (formativo):** los datos contienen errores deliberados para practicar **data cleaning** y validación. No representan un sistema real.

---

## Qué puedes hacer con este repositorio

En este se repositorio se preparan los datos de origen para poder soportar casos de uso como:

- **Abandono de clientes (churn)**: reglas y modelos baseline a partir de RFM, recencia, devoluciones, etc.
- **Propensión de compra**: dataset por snapshots (ventanas temporales) y modelos baseline.
- **Análisis de cesta (Market Basket)**: tickets/pedidos → pares frecuentes y métricas (soporte/confianza/lift).
- **Segmentación RFM**: scoring por cuantiles/quintiles, clasificación VIP/inactivos.
- **Conciliación y consistencia**: pedidos vs líneas, ventas POS vs pagos, devoluciones vs ventas, stock con anomalías, integridad referencial entre maestros y transacciones.


> Nota: Si prefieres, puedes dejar los `outputs/` fuera del repo (recomendado) y generarlos en cada ejecución.

---

## Datos (CSV, UTF-8)

Todos los CSV están en **UTF-8** y contienen **imperfecciones intencionales**.

### Maestros
- `crm.csv`  
  Clientes del programa de fidelización (alta, tier, puntos, contacto, etc.). Incluye duplicados, emails inválidos, fechas heterogéneas, CP nulo, etc.

- `productos.csv`  
  Catálogo de productos (SKU), categoría/subcategoría, coste, precio, atributos logísticos. Incluye precios/costes en formatos mixtos, IDs con casing/espacios, algún coste negativo, campos vacíos.

- `tiendas.csv`  
  Maestro de tiendas (`S001…S005` + `ONLINE`). Incluye duplicado intencional, CP nulo, coordenadas inválidas, fechas heterogéneas.

### Operacionales (e-commerce)
- `pedidos.csv`  
  Pedidos online con `order_id`, `customer_id`, fechas y estado. Incluye `customer_id` nulo/inválido, fechas en formatos distintos y duplicados.

- `lineas_pedido.csv`  
  Detalle por producto de cada pedido (líneas). Incluye `order_id` huérfano, `product_id` inválido, importes inconsistentes y duplicados.

- `devoluciones_online.csv`  
  Devoluciones online. Incluye devoluciones huérfanas, fechas incoherentes, importes con formatos mixtos y cantidades anómalas.

### Operacionales (POS)
- `ventas_pos.csv`  
  Líneas de ticket en tienda. Incluye `customer_id` frecuentemente nulo/guest, `store_id` malformado, fechas mixtas, importes/qty anómalas, duplicados.

- `devoluciones_tienda.csv`  
  Devoluciones registradas en tienda (algunas referencian ticket original). Incluye tickets huérfanos, importes incoherentes y duplicados.

- `pagos_tienda.csv`  
  Pagos por ticket (incluye pagos partidos). Incluye tickets huérfanos, métodos inconsistentes, descuadres intencionales y duplicados.

### Inventario
- `stock_diario.csv`  
  Stock diario por tienda/online y SKU. Incluye nulos, duplicados, stocks negativos y fechas en formatos mixtos.

### Fact table
- `fact_transacciones.csv`  
  Tabla unificada (ventas + devoluciones + online + POS). Es la base para features, RFM, churn, basket y propensión.

---

## Notebooks (pipeline del curso)

> Todos los notebooks siguen un patrón **formativo**:
> - carga “raw” (`dtype=str`) para no perder errores
> - funciones reutilizables (reciben `DataFrame` como parámetro)
> - reportes y checks para discusión en clase
> - exportaciones a CSV por etapas

### 1) Notebook 1 — Ingesta y tipado
**Objetivo:** cargar fuentes origen, inspección inicial, conversiones de tipos con foco en **fechas**.  
Incluye funciones para:
- carga robusta de CSV
- parsing de fechas heterogéneas (ISO / DD/MM / texto español)
- parsing de numéricos con `€`, coma/punto, miles
- checks básicos de shape/nulos/duplicados

### 2) Notebook 2 — Perfilado y reporte de calidad
**Objetivo:** data profiling + “Data Quality Report” provisional.  
Incluye:
- nulos, cardinalidad, duplicados exactos
- tasas de parseo de fechas/importes
- integridad referencial (PK/FK)
- conciliaciones (pedidos vs líneas, ventas POS vs pagos)
- export del reporte (CSV)

### 3) Notebook 3 — Limpieza y estandarización
**Objetivo:** aplicar reglas de limpieza y estandarización (IDs, fechas, numéricos, textos, outliers).  
Incluye:
- funciones por dataset (clean_crm, clean_productos, etc.)
- generación de *extras* (duplicados/descartados) para docencia
- export de `*_clean.csv`

### 4) Notebook 4 — Integración y fact table
**Objetivo:** construir fact integrada (granularidad: línea de venta/devolución) y enriquecer con dimensiones.  
Incluye:
- builders para ventas/devoluciones online y POS
- enriquecimiento con producto/cliente/tienda
- devoluciones como negativos (cantidad/importes)
- export `fact_transacciones_integrada.csv`

### 5) Notebook 5 — Features (cliente y producto)
**Objetivo:** crear datasets agregados:
- **clientes**: RFM, devoluciones, canal preferido, descuentos, label churn didáctico
- **productos**: ventas/devoluciones/márgenes
- **cesta**: formato basket_long (doc_id–product_id)
- **propensión**: snapshots temporales (lookback/horizon)  
Export a `output_features/`.

### 6) Notebook 6 — Preprocesamiento final (ML/BI-ready)
**Objetivo:** imputación + escalado + one-hot encoding con sklearn.  
Export a `output_ml/`:
- `FraSoHome_clientes_ML_ready.csv`
- `FraSoHome_propension_ML_ready.csv` (si aplica)
- `FraSoHome_productos_ML_ready.csv` (si aplica)


---
