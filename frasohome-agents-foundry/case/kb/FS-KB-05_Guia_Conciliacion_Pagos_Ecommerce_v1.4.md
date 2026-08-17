# Guía de conciliación de pagos (E-commerce) - FraSoHome

Fuente: `FS-KB-05_Guia_Conciliacion_Pagos_Ecommerce_v1.4.docx`.

## 1. Objetivo

Asegurar que cada pedido de E-commerce tiene correspondencia 1:1 con su cobro en pasarela de pagos y que los reembolsos y contracargos se contabilizan correctamente.

## 2. Fuentes y campos clave

## 3. Conciliación diaria (paso a paso)

- 1) Extraer listado de pedidos confirmados del día D (Estado = 'Pagado' o 'En preparación').
- 2) Extraer listado de transacciones capturadas del día D en la pasarela.
- 3) Hacer match por OrderID (o por referencia de pedido).
- 4) Identificar discrepancias: pedido sin cobro, cobro sin pedido, importes distintos.
- 5) Registrar discrepancias en el log 'Conciliación - Incidencias' y asignar responsable.
- 6) Validar que el total capturado = total contabilizado en ERP para el día D.
## 4. Escenarios y reglas

## 5. SLAs

- Conciliación diaria: completada antes de las 12:00 del día D+1.
- Discrepancias críticas (importe > 500 EUR): investigadas el mismo día.
- Cierre mensual: conciliación completa antes del día 3 del mes siguiente.
## Tablas extraídas

### Tabla 1

| ID documento | FS-KB-05 |
| --- | --- |
| Título | Guía de conciliación de pagos - E-commerce |
| Versión | 1.4 |
| Estado | VIGENTE |
| Área propietaria | Finanzas |
| Aprobado por | Contabilidad |
| Vigente desde | 01/10/2025 |
| Última revisión | 12/02/2026 |
| Sensibilidad | Uso interno (finanzas) |

### Tabla 2

| Sistema | Entidad | Campos clave (mínimos) |
| --- | --- | --- |
| E-commerce | Pedido | OrderID, FechaPedido, TotalBruto, Descuentos, TotalNeto, Estado |
| Pasarela pagos | Transacción | PaymentID, OrderID, Importe, Estado (capturado/retenido/fallido), Método |
| ERP/Contabilidad | Asiento | Fecha, Cuenta, Importe, Referencia (OrderID/PaymentID) |
| E-commerce | Reembolso | RefundID, OrderID, Importe, Motivo, FechaConfirmación |

### Tabla 3

| Escenario | Regla | Acción |
| --- | --- | --- |
| Pago retenido (no capturado) | No contabilizar ventas hasta captura. | Revisar antifraude; reintentar captura o cancelar. |
| Reembolso parcial | Ajustar ventas netas y devoluciones por el importe reembolsado. | Registrar RefundID y vincular a asiento. |
| Contracargo/chargeback | Registrar como devolución + coste de contracargo. | Escalar a Atención al cliente y prevención de fraude. |
| Pedido duplicado | Anular duplicado antes de contabilizar. | Corregir en E-commerce y reportar a IT. |
