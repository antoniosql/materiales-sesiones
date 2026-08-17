# Diccionario de KPI y reglas de cálculo - FraSoHome

Fuente: `FS-KB-03_Diccionario_KPI_Reglas_Calculo_v1.0.docx`.

## 1. Principios generales

Este diccionario define las métricas oficiales que deben usarse en informes, dashboards y respuestas del asistente.

- Si un usuario pregunta por un KPI, el asistente debe citar esta fuente y declarar la fórmula usada.
- Cuando una pregunta requiera un periodo/canal y no esté especificado, el asistente debe pedir aclaración (o proponer un valor por defecto y confirmarlo).
- Las métricas de ventas y devoluciones deben presentarse, como mínimo, con: periodo, canal, moneda y definición.
## 2. Tabla de KPIs

## 3. Reglas de calendario y redondeo

- Calendario: mes natural (01-31) salvo indicación contraria.
- Moneda: EUR. Redondeo a 2 decimales en importes.
- Tasa de devolución: mostrar en % con 1 decimal (p. ej., 7,3%).
## 4. Reglas de calidad y excepciones

- Importes negativos: solo se admiten en devoluciones/ajustes; revisar si aparecen en ventas.
- Duplicados de pedidos/tickets: excluir del reporting hasta reconciliación.
- Coste unitario faltante: si COGS está nulo, el margen bruto se reporta como 'no disponible' para evitar errores.
## Tablas extraídas

### Tabla 1

| ID documento | FS-KB-03 |
| --- | --- |
| Título | Diccionario de KPI y reglas de cálculo (oficial) |
| Versión | 1.0 |
| Estado | VIGENTE |
| Área propietaria | Equipo de Datos + Finanzas |
| Aprobado por | CFO |
| Vigente desde | 01/02/2026 |
| Última revisión | 15/02/2026 |
| Sensibilidad | Uso interno (definiciones oficiales) |

### Tabla 2

| KPI | Definición | Fórmula (conceptual) | Fuentes | Notas |
| --- | --- | --- | --- | --- |
| Ventas brutas | Importe total vendido antes de descuentos y devoluciones. | SUM(Importe_linea_bruto) | POS + E-commerce | Incluye IVA. No resta devoluciones. |
| Descuentos comerciales | Descuentos aplicados en línea o ticket (promos, cupones, rebajas). | SUM(Descuento_linea) | POS + E-commerce | No incluye puntos canjeados (ver 'Descuento por puntos'). |
| Descuento por puntos | Importe descontado por canje de puntos de fidelización. | SUM(Importe_puntos_canjeados) | CRM + POS/E-commerce | Se informa por separado para análisis de fidelización. |
| Devoluciones (importe) | Importe reembolsado por devoluciones confirmadas. | SUM(Importe_reembolso) | POS + E-commerce | Se registra en la fecha de confirmación de devolución. |
| Ventas netas | Ventas brutas menos descuentos comerciales, menos descuento por puntos, menos devoluciones. | Ventas brutas - Descuentos comerciales - Descuento por puntos - Devoluciones | Modelo consolidado | KPI principal para reporting comercial. |
| Margen bruto | Ventas netas menos coste de mercancía vendida (COGS). | Ventas netas - SUM(Coste_unitario * Unidades_vendidas) | ERP (coste) + Ventas | Coste estándar mensual. No incluye logística. |
| Tasa de devolución (unidades) | Porcentaje de unidades devueltas sobre unidades vendidas. | Unidades_devueltas / Unidades_vendidas | Ventas + Devoluciones | Se calcula por canal y categoría. |
| Tasa de devolución (importe) | Porcentaje de importe devuelto sobre ventas netas. | Importe_devoluciones / Ventas netas | Ventas + Devoluciones | Recomendado usar a nivel mensual. |
| Stock disponible | Unidades disponibles para venta = stock en mano - reservado - bloqueado. | Stock_on_hand - Stock_reservado - Stock_bloqueado | ERP | Si < 0, corregir calidad de datos. |
| Quiebra de stock | SKU con stock disponible = 0 y demanda reciente > 0. | Stock disponible = 0 AND Ventas_7d > 0 | ERP + Ventas | Usar para priorizar reposición. |
| Rotación de inventario | Velocidad de salida del stock (en unidades). | Unidades_vendidas_periodo / Stock_medio_periodo | ERP + Ventas | Stock medio = (stock inicio + stock fin)/2. |
| Ticket medio | Promedio de ventas netas por ticket/pedido. | Ventas netas / Nº pedidos | POS + E-commerce | Comparar por canal. |
| Clientes activos | Clientes con al menos 1 compra en los últimos 12 meses. | COUNTDISTINCT(CustomerID) con compra_12m | CRM + Ventas | Para segmentación y campañas. |
