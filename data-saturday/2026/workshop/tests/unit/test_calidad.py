import pytest

from datafwk.calidad import COLUMNA_MOTIVO, aplicar_contrato
from datafwk.config import Contrato
from datafwk.errores import ContratoIncumplido

CONTRATO = Contrato.desde_dict(
    {
        "tabla": "pedidos",
        "capa": "silver",
        "dominio": "ventas",
        "propietario": "@equipo",
        "descripcion": "test",
        "clave": ["id_pedido"],
        "columnas": {
            "id_pedido": {"tipo": "string", "nulo": False},
            "canal": {"tipo": "string", "valores": ["tienda", "web"]},
            "importe_total": {"tipo": "decimal(12,2)", "nulo": False},
        },
        "reglas": [{"nombre": "importe_no_negativo", "expresion": "importe_total >= 0"}],
    }
)

pytestmark = pytest.mark.spark


def _motivos(rechazadas):
    return {r.id_pedido: sorted(r[COLUMNA_MOTIVO]) for r in rechazadas.collect()}


def test_filas_validas_pasan_tipadas(spark):
    df = spark.createDataFrame([("P1", "web", "10.50", "b1")], ["id_pedido", "canal", "importe_total", "_batch_id"])
    validas, rechazadas = aplicar_contrato(df, CONTRATO)
    assert rechazadas.count() == 0
    fila = validas.collect()[0]
    assert str(fila.importe_total) == "10.50"
    assert validas.columns == ["id_pedido", "canal", "importe_total", "_batch_id"]


def test_cada_incumplimiento_tiene_su_motivo(spark):
    df = spark.createDataFrame(
        [
            ("P1", "fax", "10"),  # valor no permitido
            ("P2", "web", "-5"),  # regla
            ("P3", "web", "abc"),  # tipo inválido: no se pierde en silencio
            (None, "web", "1"),  # nulo en columna obligatoria
        ],
        ["id_pedido", "canal", "importe_total"],
    )
    validas, rechazadas = aplicar_contrato(df, CONTRATO)
    assert validas.count() == 0
    motivos = _motivos(rechazadas)
    assert motivos["P1"] == ["valor:canal"]
    assert motivos["P2"] == ["regla:importe_no_negativo"]
    assert "tipo:importe_total" in motivos["P3"]
    assert motivos[None] == ["nulo:id_pedido"]


def test_una_fila_acumula_todos_sus_motivos(spark):
    df = spark.createDataFrame([("P1", "fax", "-1")], ["id_pedido", "canal", "importe_total"])
    _, rechazadas = aplicar_contrato(df, CONTRATO)
    assert _motivos(rechazadas)["P1"] == ["regla:importe_no_negativo", "valor:canal"]


def test_faltan_columnas_del_contrato(spark):
    df = spark.createDataFrame([("P1",)], ["id_pedido"])
    with pytest.raises(ContratoIncumplido, match="faltan columnas"):
        aplicar_contrato(df, CONTRATO)
