-- Ejecuciones del framework que no han terminado bien en los últimos 7 días.
-- Runbook: docs/runbooks/carga-fallida.md
SELECT
    batch_id,
    capa,
    fuente,
    tabla,
    estado,
    filas_leidas,
    filas_escritas,
    filas_rechazadas,
    inicio,
    mensaje
FROM lh_silver.fwk_ejecuciones
WHERE
    estado != 'ok'
    AND inicio >= current_timestamp() - INTERVAL 7 DAYS
ORDER BY inicio DESC
