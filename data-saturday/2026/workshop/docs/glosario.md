# Glosario de negocio

> Este es el fichero que más necesita un asistente de IA y el que más falta en los proyectos.
> Cada término lo aprueba su propietario de negocio (ver `.github/CODEOWNERS`).
> Si un KPI no está aquí, no se implementa: se define primero.

| Término | Definición | Cálculo | Propietario |
|---|---|---|---|
| **Pedido** | Compra confirmada por un cliente en cualquier canal | Una fila de `silver.pedidos` | Ventas |
| **Pedido cancelado** | Pedido con `estado = cancelado`. No cuenta como venta | — | Ventas |
| **Ventas netas** | Importe de los pedidos no cancelados, con impuestos | `SUM(importe_total) WHERE estado <> 'cancelado'` | Ventas |
| **Canal** | Origen del pedido: `tienda`, `web` o `app` | — | Ventas |
| **Cliente activo** | *Pendiente de definir por negocio* | — | Ventas |

## Cómo añadir un término
1. Rama + PR que añade la fila
2. Aprobación del propietario (CODEOWNERS lo exige)
3. Solo entonces se implementa la medida o la tabla que lo usa
