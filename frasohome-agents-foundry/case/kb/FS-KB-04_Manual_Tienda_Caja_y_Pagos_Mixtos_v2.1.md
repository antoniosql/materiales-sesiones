# Manual de tienda: cierre de caja y pagos mixtos - FraSoHome

Fuente: `FS-KB-04_Manual_Tienda_Caja_y_Pagos_Mixtos_v2.1.docx`.

## 1. Objetivo

Estandarizar el proceso de cierre de caja y el tratamiento de pagos mixtos y devoluciones en tienda para reducir descuadres y errores de reembolso.

## 2. Apertura de caja (inicio de turno)

- 1) Iniciar sesión en POS con usuario personal (no compartir credenciales).
- 2) Contar fondo fijo y registrar importe inicial (FondoCajaEUR).
- 3) Verificar impresora de tickets y lector de tarjetas.
- 4) Comprobar sincronización de precios (actualización diaria) y avisar si hay fallos.
## 3. Cierre de caja (fin de turno)

- 1) Ejecutar 'Cierre de turno' en POS y generar informe Z.
- 2) Contar efectivo y comparar con efectivo esperado.
- 3) Registrar incidencias (diferencias, anulaciones, devoluciones).
- 4) Depositar efectivo según protocolo y cerrar sesión.
Umbrales: cualquier descuadre > 10 EUR debe registrarse y notificarse al Store Manager el mismo día.

## 4. Pagos mixtos (tarjeta + efectivo / tarjeta regalo)

Un pago mixto ocurre cuando un mismo ticket se paga con más de un medio (p. ej., 30 EUR en tarjeta y 20 EUR en efectivo).

- Regla: registrar cada tramo de pago como línea separada en POS (no 'ajustar a mano').
- Si el POS no permite dividir un método, NO completar la venta: escalar a Soporte POS.
## 5. Devoluciones en tienda (flujo)

- 1) Localizar la compra: ticket, o búsqueda por fidelización (correo/teléfono).
- 2) Validar política vigente (FS-KB-01) y estado del producto.
- 3) Seleccionar motivo de devolución (R01-R06) y condición del artículo.
- 4) Ejecutar reembolso conforme al método de pago original.
## 6. Reembolso en pagos mixtos (regla operativa)

## 7. Incidencias frecuentes y qué hacer

- Cliente sin ticket y sin fidelización: no procesar devolución; ofrecer alternativa de cambio solo con aprobación del Store Manager.
- Precio incorrecto en ticket: registrar incidencia de pricing y adjuntar evidencia (foto etiqueta).
- Sospecha de fraude: no acusar al cliente; seguir protocolo de Prevención de pérdidas y registrar en el sistema.
## 8. Contactos y escalado

- Soporte POS (24/7): canal interno 'POS-SOPORTE'.
- Finanzas (conciliación): finanzas@frasohome (interno).
- Prevención de pérdidas: canal 'LOSS-PREVENTION'.
## Tablas extraídas

### Tabla 1

| ID documento | FS-KB-04 |
| --- | --- |
| Título | Manual de tienda: cierre de caja, devoluciones y pagos mixtos |
| Versión | 2.1 |
| Estado | VIGENTE |
| Área propietaria | Operaciones Retail |
| Aprobado por | Retail Operations Manager |
| Vigente desde | 20/11/2025 |
| Última revisión | 05/02/2026 |
| Sensibilidad | Uso interno (tienda) |

### Tabla 2

| Ticket original | Regla en devolución | Ejemplo |
| --- | --- | --- |
| Tarjeta + efectivo | Reembolsar primero a tarjeta hasta su importe; resto en efectivo. | Pagó 30 tarjeta + 20 efectivo -> devolver 30 tarjeta + 20 efectivo. |
| Tarjeta + tarjeta regalo | Reembolsar primero a tarjeta regalo hasta su importe; resto a tarjeta. | Pagó 10 regalo + 40 tarjeta -> devolver 10 regalo + 40 tarjeta. |
| Financiación | No devolver en efectivo. Gestionar anulación/regularización. | Derivar a Finanzas/Financiación. |
