import pytest

from datafwk.errores import ConfiguracionInvalida
from datafwk.estandarizar import a_snake_case, deduplicar, renombrar_columnas


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("FechaPedido", "fecha_pedido"),
        ("IDCliente", "id_cliente"),
        ("Importe (€)", "importe"),
        ("Año Fiscal", "ano_fiscal"),
        ("  codigo--postal ", "codigo_postal"),
        ("ya_en_snake", "ya_en_snake"),
    ],
)
def test_a_snake_case(entrada, esperado):
    assert a_snake_case(entrada) == esperado


@pytest.mark.spark
def test_renombrar_respeta_columnas_tecnicas(spark):
    df = spark.createDataFrame([(1, "x")], ["IdPedido", "_batch_id"])
    assert renombrar_columnas(df).columns == ["id_pedido", "_batch_id"]


@pytest.mark.spark
def test_renombrar_detecta_colisiones(spark):
    df = spark.createDataFrame([(1, 2)], ["IdPedido", "id_pedido"])
    with pytest.raises(ConfiguracionInvalida, match="colisionan"):
        renombrar_columnas(df)


@pytest.mark.spark
def test_deduplicar_se_queda_con_la_mas_reciente(spark):
    df = spark.createDataFrame(
        [("P1", "viejo", 1), ("P1", "nuevo", 2), ("P2", "unico", 1)],
        ["id_pedido", "estado", "_ingested_at"],
    )
    resultado = {r.id_pedido: r.estado for r in deduplicar(df, ["id_pedido"], orden="_ingested_at").collect()}
    assert resultado == {"P1": "nuevo", "P2": "unico"}
