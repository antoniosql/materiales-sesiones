# Defectos en la base SQL de origen

Ejecutar únicamente en la base dedicada al workshop, desde el editor SQL, con una identidad de escritura.
El framework lector no ejecuta estos cambios. Seleccionar cuatro IDs reales distintos de `returns.return_line`;
guardar primero el resultado de esta consulta como respaldo de valores, sin exportar CSV:

```sql
SELECT return_line_id, refund_amount, return_reason
INTO lab.workshop_respaldo_calidad
FROM returns.return_line
WHERE return_line_id IN (
    N'<linea_negativa>', N'<linea_importe_nulo>', N'<linea_motivo_nulo_1>', N'<linea_motivo_nulo_2>'
);
```

Antes de ejecutar, comprobar que `lab.workshop_respaldo_calidad` no existe y que la selección tiene exactamente cuatro
filas. Mantener los importes originales válidos de las dos líneas a las que se quitará el motivo.
Aplicar en una transacción y comprobar cuatro filas afectadas en conjunto:

```sql
BEGIN TRANSACTION;
UPDATE returns.return_line SET refund_amount = -1.00
WHERE return_line_id = N'<linea_negativa>';
UPDATE returns.return_line SET refund_amount = NULL
WHERE return_line_id = N'<linea_importe_nulo>';
UPDATE returns.return_line SET return_reason = NULL
WHERE return_line_id IN (N'<linea_motivo_nulo_1>', N'<linea_motivo_nulo_2>');
COMMIT;
```

La demo de ciudad modifica un cliente real del mismo origen. Guardar previamente `customer_id`, `city` y `updated_at`.

```sql
UPDATE crm.customer
SET city = N'<ciudad_nueva>', updated_at = sysutcdatetime()
WHERE customer_id = N'<cliente_demo>';
```

Restauración de calidad (las tablas del origen mantienen sus PK/FK/CHECK):

```sql
UPDATE r
SET refund_amount = b.refund_amount, return_reason = b.return_reason
FROM returns.return_line AS r
INNER JOIN lab.workshop_respaldo_calidad AS b ON b.return_line_id = r.return_line_id;
```

Restaurar la ciudad original con una nueva `updated_at`, para que la extracción incremental vea la corrección.
Verificar en SQL antes de volver a ejecutar el pipeline. Conservar el respaldo hasta completar la comprobación.
No se han ejecutado estas sentencias como parte de la implementación de la plantilla.
