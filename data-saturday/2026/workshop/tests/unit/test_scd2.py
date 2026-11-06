"""Casos temporales de SCD2 por observación, sin almacenamiento."""

from datetime import datetime, timedelta, timezone

import pytest
from pyspark.sql import functions as F

from datafwk.config import Modelo
from datafwk.errores import ContratoIncumplido
from datafwk.scd2 import evolucionar, inicializar, proyeccion_actual, validar_historia

pytestmark = pytest.mark.spark
T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
MODELO = Modelo(
    "dim_cliente",
    "crm",
    "clientes",
    "contracts/gold/dim_cliente.yml",
    ("id_cliente",),
    ("id_cliente", "ciudad", "nombre"),
    "scd2",
    ("ciudad",),
    ("nombre",),
    "dim_cliente_actual",
    "contracts/gold/dim_cliente_actual.yml",
)


def entrada(spark, ciudad="Madrid", nombre="Ana"):
    return spark.createDataFrame([(1, ciudad, nombre)], "id_cliente int, ciudad string, nombre string")


def materializar(spark, df):
    # Rompe el linaje entre pasos para simular versiones Delta en este test de transformación pura.
    return spark.createDataFrame(df.collect(), df.schema)


def test_activacion_reintento_a_b_a_y_tipo1(spark):
    inicial = materializar(spark, inicializar(entrada(spark), MODELO, T0, "activacion"))
    t1, t2 = T0 + timedelta(minutes=1), T0 + timedelta(minutes=2)
    cambiado = materializar(spark, evolucionar(inicial, entrada(spark, "Barcelona"), MODELO, t1, "b1"))
    assert cambiado.count() == 2
    validar_historia(cambiado, MODELO)
    repetido = materializar(spark, evolucionar(cambiado, entrada(spark, "Barcelona"), MODELO, t1, "b1"))
    assert repetido.orderBy("id_version").collect() == cambiado.orderBy("id_version").collect()
    vuelta = materializar(spark, evolucionar(repetido, entrada(spark), MODELO, t2, "b2"))
    assert vuelta.count() == 3
    assert vuelta.select("id_version").distinct().count() == 3
    assert vuelta.where("es_actual").first()["ciudad"] == "Madrid"
    tipo1 = materializar(
        spark, evolucionar(vuelta, entrada(spark, nombre="Ana nueva"), MODELO, t2 + timedelta(minutes=1), "b3")
    )
    assert tipo1.count() == 3
    assert proyeccion_actual(tipo1, MODELO).first()["nombre"] == "Ana nueva"
    assert {r["nombre"] for r in tipo1.where("NOT es_actual").collect()} == {"Ana"}
    validar_historia(tipo1, MODELO)


def test_nulos_no_se_confunden_con_cadena_y_ausencia_no_borra(spark):
    inicial = inicializar(entrada(spark, None), MODELO, T0, "b0")
    cambiado = materializar(
        spark, evolucionar(inicial, entrada(spark, "null"), MODELO, T0 + timedelta(seconds=1), "b1")
    )
    assert cambiado.count() == 2
    vacio = entrada(spark).limit(0)
    assert evolucionar(cambiado, vacio, MODELO, T0 + timedelta(seconds=2), "b2").count() == 2


def test_rechaza_duplicados_y_cambio_en_mismo_instante(spark):
    with pytest.raises(ContratoIncumplido, match="duplicada"):
        inicializar(entrada(spark).union(entrada(spark)), MODELO, T0, "b0")
    inicial = inicializar(entrada(spark), MODELO, T0, "b0")
    with pytest.raises(ContratoIncumplido, match="instante"):
        evolucionar(inicial, entrada(spark, "Barcelona"), MODELO, T0, "b1")
    corrupta = inicial.withColumn("vigente_hasta", F.col("vigente_desde"))
    with pytest.raises(ContratoIncumplido, match="intervalos"):
        validar_historia(corrupta, MODELO)
