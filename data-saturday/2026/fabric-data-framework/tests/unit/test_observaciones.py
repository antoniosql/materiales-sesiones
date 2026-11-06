from datetime import datetime, timedelta

import pytest

from datafwk.calidad import aplicar_contrato
from datafwk.config import Columna, Contrato
from datafwk.errores import ContratoIncumplido
from datafwk.observaciones import con_dato_bruto, evidencias, ultimas

pytestmark = pytest.mark.spark


def test_calidad_conserva_bruto_y_cambia_identidad_al_versionar(spark):
    contrato = Contrato(
        "datos",
        "silver",
        "prueba",
        "@equipo",
        "Prueba técnica",
        ("id",),
        (Columna("id", "int", False), Columna("valor", "int", False)),
    )
    df = spark.createDataFrame(
        [(1, "no-numero", "b1", datetime(2026, 1, 1))],
        "id int, valor string, _batch_id string, _observado_en timestamp",
    )
    spark.conf.set("spark.sql.ansi.enabled", "true")
    try:
        validas, rechazadas = aplicar_contrato(con_dato_bruto(df), contrato)
        assert validas.count() == 0
        v1 = evidencias(rechazadas, "prueba.datos", 1).first()
        v2 = evidencias(rechazadas, "prueba.datos", 2).first()
        assert "no-numero" in v1["dato_bruto"]
        assert "tipo:valor" in v1["motivos"]
        assert v1["id_rechazo"] != v2["id_rechazo"]
    finally:
        spark.conf.set("spark.sql.ansi.enabled", "false")


def test_ultima_observacion_y_empate_contradictorio(spark):
    t0 = datetime(2026, 1, 1)
    esquema = "id int, valor string, _observado_en timestamp"
    df = spark.createDataFrame([(1, "A", t0), (1, "B", t0 + timedelta(seconds=1))], esquema)
    assert ultimas(df, ("id",)).first()["valor"] == "B"
    empate = spark.createDataFrame([(1, "A", t0), (1, "B", t0)], esquema)
    with pytest.raises(ContratoIncumplido, match="contradictorios"):
        ultimas(empate, ("id",))
