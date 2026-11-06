-- Ejecuciones que no reconcilian: leídas <> escritas + rechazadas. Debe devolver 0 filas.
-- Si devuelve alguna, se han perdido filas por el camino: es un bug del framework.
SELECT
    batch_id,
    capa,
    fuente,
    filas_leidas,
    filas_escritas,
    filas_rechazadas
FROM lh_silver.fwk_ejecuciones
WHERE filas_leidas != filas_escritas + filas_rechazadas
