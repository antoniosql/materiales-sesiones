"""Pruebas de aceptación contra Delta real; el origen SQL se sustituye por una tabla en memoria."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest
from pyspark.sql import functions as F

from datafwk import rutas
from datafwk.config import Columna, ConexionSql, Contrato, Entorno, Extraccion, Fuente, Modelo, OrigenSql
from datafwk.control import Control, leer_version, version
from datafwk.errores import ConfiguracionInvalida, ContratoIncumplido
from datafwk.gold import a_gold
from datafwk.ingesta import a_bronze
from datafwk.origenes import sql
from datafwk.silver import a_silver


def test_csv_completa_incremental_reintento_y_lote_vacio(spark, tmp_path, monkeypatch):
    from datafwk import ingesta

    entorno, fuente, contrato, estado = escenario(spark, tmp_path, monkeypatch)
    fichero = tmp_path / "clientes.csv"
    fuente = replace(
        fuente,
        formato="csv",
        ruta_landing="landing/clientes.csv",
        origen_sql=None,
        opciones_lectura={"header": "true"},
        extraccion=Extraccion(columna_marca="fecha_cambio", estabilizacion_segundos=0, solape_segundos=0),
    )
    monkeypatch.setattr(rutas, "ficheros", lambda *_: str(fichero))

    class Reloj:
        @staticmethod
        def now(_zona):
            return estado["reloj"]

    monkeypatch.setattr(ingesta, "datetime", Reloj)
    fichero.write_text("id_cliente,ciudad,fecha_cambio\n1,A,2025-12-31T23:00:00Z\n", encoding="utf-8")
    assert a_bronze(spark, fuente, entorno, "csv0").filas_leidas == 1
    a_silver(spark, fuente, contrato, entorno, "csv0")
    fuente = replace(fuente, extraccion=replace(fuente.extraccion, modo="incremental"))
    estado["reloj"] += timedelta(minutes=1)
    fichero.write_text("id_cliente,ciudad,fecha_cambio\n1,B,2026-01-01T00:00:30Z\n", encoding="utf-8")
    assert a_bronze(spark, fuente, entorno, "csv1").filas_leidas == 1
    fichero.write_text("id_cliente,ciudad,fecha_cambio\n1,C,2026-01-01T00:00:40Z\n", encoding="utf-8")
    a_bronze(spark, fuente, entorno, "csv1")
    a_silver(spark, fuente, contrato, entorno, "csv1")
    resultado = leer_version(spark, rutas.tabla(entorno, "silver", "clientes"))
    assert resultado.select("ciudad").first()[0] == "B"
    estado["reloj"] += timedelta(minutes=1)
    assert a_bronze(spark, fuente, entorno, "csv2").filas_leidas == 0
    a_silver(spark, fuente, contrato, entorno, "csv2")
    assert Control(spark, entorno).marca(fuente.identidad) == estado["reloj"]


pytestmark = [pytest.mark.spark, pytest.mark.delta]


def escenario(spark, tmp_path, monkeypatch):
    monkeypatch.setattr(rutas, "tabla", lambda entorno, capa, nombre: (tmp_path / capa / nombre).as_posix())
    entorno = Entorno("prueba", "<workspace>", {}, conexiones_sql={"origen": ConexionSql("<server>", "<base>")})
    fuente = Fuente(
        "clientes",
        "crm",
        "sql",
        "",
        "clientes",
        "clientes",
        ("id_cliente",),
        "contracts/silver/clientes.yml",
        origen_sql=OrigenSql(
            "origen", "crm", "customer", {"id_cliente": "id_cliente", "ciudad": "ciudad", "updated_at": "fecha_cambio"}
        ),
        extraccion=Extraccion(columna_marca="updated_at", estabilizacion_segundos=0),
    )
    contrato = Contrato(
        "clientes",
        "silver",
        "crm",
        "@equipo",
        "Prueba técnica de ciudad",
        ("id_cliente",),
        (
            Columna("id_cliente", "string", False),
            Columna("ciudad", "string"),
            Columna("fecha_cambio", "timestamp", False),
        ),
    )
    estado = {"reloj": datetime(2026, 1, 1, tzinfo=timezone.utc), "lecturas": 0, "ciudad": "Madrid"}
    monkeypatch.setattr(sql, "reloj", lambda *_: estado["reloj"])

    def leer(_spark, _fuente, _conexion, _intervalo):
        estado["lecturas"] += 1
        return spark.createDataFrame(
            [("1", estado["ciudad"], estado["reloj"], estado["reloj"])],
            "id_cliente string, ciudad string, fecha_cambio timestamp, _source_updated_at timestamp",
        )

    monkeypatch.setattr(sql, "leer", leer)
    return entorno, fuente, contrato, estado


def test_reintento_revalidacion_fallar_y_marca(spark, tmp_path, monkeypatch):
    entorno, fuente, contrato, estado = escenario(spark, tmp_path, monkeypatch)
    estado["ciudad"] = None
    a_bronze(spark, fuente, entorno, "b0")
    a_bronze(spark, fuente, entorno, "b0")
    assert estado["lecturas"] == 1
    assert a_silver(spark, fuente, contrato, entorno, "b0").filas_escritas == 1
    control = Control(spark, entorno)
    marca = control.marca(fuente.identidad)
    estricto = replace(
        contrato,
        version=2,
        columnas=(contrato.columnas[0], replace(contrato.columnas[1], nulo=False), contrato.columnas[2]),
    )
    resultado = a_silver(spark, fuente, estricto, entorno, "q2", revalidar=True)
    assert resultado.filas_rechazadas == 1
    assert leer_version(spark, rutas.tabla(entorno, "silver", "clientes")).count() == 0
    assert control.marca(fuente.identidad) == marca
    cuarentena = rutas.tabla(entorno, "silver", "fwk_cuarentena")
    a_silver(spark, fuente, estricto, entorno, "q2", revalidar=True)
    assert leer_version(spark, cuarentena).count() == 1
    antes = version(spark, rutas.tabla(entorno, "silver", "clientes"))
    with pytest.raises(ContratoIncumplido):
        a_silver(spark, fuente, replace(estricto, version=3, politica_rechazo="fallar"), entorno, "q3", revalidar=True)
    assert version(spark, rutas.tabla(entorno, "silver", "clientes")) == antes
    assert control.marca(fuente.identidad) == marca
    # Corrige la regla del intento fallido y reanuda ese mismo lote, sin dejarlo bloqueado.
    a_silver(spark, fuente, replace(contrato, version=4), entorno, "q3", revalidar=True)
    assert leer_version(spark, rutas.tabla(entorno, "silver", "clientes")).count() == 1


def test_migracion_y_recuperacion_tras_historia_antes_de_proyeccion(spark, tmp_path, monkeypatch):
    import datafwk.gold as gold

    entorno, fuente, contrato, estado = escenario(spark, tmp_path, monkeypatch)
    a_bronze(spark, fuente, entorno, "b0")
    a_silver(spark, fuente, contrato, entorno, "b0")
    modelo = Modelo(
        "dim_cliente", "crm", "clientes", "contracts/gold/dim_cliente.yml", ("id_cliente",), ("id_cliente", "ciudad")
    )
    c1 = replace(contrato, tabla="dim_cliente", capa="gold", columnas=contrato.columnas[:2])
    a_gold(spark, modelo, fuente, c1, entorno, "b0")
    fuente = replace(fuente, extraccion=replace(fuente.extraccion, modo="incremental"))
    estado["reloj"] += timedelta(minutes=1)
    a_bronze(spark, fuente, entorno, "activar")
    a_silver(spark, fuente, contrato, entorno, "activar")
    modelo = replace(
        modelo,
        tipo="scd2",
        columnas_scd2=("ciudad",),
        tabla_actual="dim_cliente_actual",
        contrato_actual="contracts/gold/dim_cliente_actual.yml",
    )
    c2 = replace(
        c1,
        version=2,
        clave=("id_version",),
        clave_negocio=("id_cliente",),
        columnas=(
            *c1.columnas,
            Columna("id_version", "string", False),
            Columna("vigente_desde", "timestamp", False),
            Columna("vigente_hasta", "timestamp"),
            Columna("es_actual", "boolean", False),
            Columna("_hash_scd2", "string", False),
            Columna("_batch_id", "string", False),
        ),
    )
    actual = replace(c1, tabla="dim_cliente_actual")
    a_gold(spark, modelo, fuente, c2, entorno, "activar", actual, activar_scd2=True)
    estado["reloj"] += timedelta(minutes=1)
    estado["ciudad"] = "Barcelona"
    a_bronze(spark, fuente, entorno, "b2")
    a_silver(spark, fuente, contrato, entorno, "b2")
    original = gold.escribir

    def fallar_proyeccion(*args, **kwargs):
        if args[2].endswith("dim_cliente_actual"):
            raise RuntimeError("fallo simulado antes de publicar la proyección")
        return original(*args, **kwargs)

    monkeypatch.setattr(gold, "escribir", fallar_proyeccion)
    with pytest.raises(RuntimeError, match="simulado"):
        a_gold(spark, modelo, fuente, c2, entorno, "b2", actual)
    historia = rutas.tabla(entorno, "gold", "dim_cliente")
    revision = version(spark, historia)
    monkeypatch.setattr(gold, "escribir", original)
    a_gold(spark, modelo, fuente, c2, entorno, "b2", actual)
    assert version(spark, historia) == revision
    assert leer_version(spark, historia).count() == 2
    assert leer_version(spark, historia).where(F.col("es_actual")).first()["ciudad"] == "Barcelona"
    assert leer_version(spark, rutas.tabla(entorno, "gold", "dim_cliente_actual")).first()["ciudad"] == "Barcelona"
    # Un cambio de grano/historia posterior no puede desactivarse con un YAML tipo1.
    estado["reloj"] += timedelta(minutes=1)
    a_bronze(spark, fuente, entorno, "b3")
    a_silver(spark, fuente, contrato, entorno, "b3")
    with pytest.raises(ConfiguracionInvalida, match="otra migración"):
        a_gold(spark, replace(modelo, tipo="tipo1"), fuente, c1, entorno, "b3")
