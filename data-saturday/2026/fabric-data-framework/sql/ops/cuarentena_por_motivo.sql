-- Motivos de rechazo de un lote, por fuente. Lee las evidencias de silver.fwk_cuarentena.
-- Ejecutar con: spark.sql(consulta, args={"batch_id": "<batch_id>"})
SELECT
    c.fuente,
    m.motivo,
    count(*) AS filas
FROM lh_silver.fwk_cuarentena AS c
    LATERAL VIEW explode(from_json(c.motivos, 'array<string>')) m AS motivo
WHERE c.batch_id = :batch_id
GROUP BY c.fuente, m.motivo
ORDER BY filas DESC
