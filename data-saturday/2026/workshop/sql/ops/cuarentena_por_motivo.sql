-- Motivos de rechazo de un lote en la cuarentena de pedidos. Para otra tabla, cambia el FROM.
-- Ejecutar con: spark.sql(consulta, args={"batch_id": "<batch_id>"})
SELECT
    m.motivo,
    count(*) AS filas
FROM lh_silver._cuarentena_pedidos AS c
    LATERAL VIEW explode(c._motivo_rechazo) m AS motivo
WHERE c._batch_id = :batch_id
GROUP BY m.motivo
ORDER BY filas DESC
