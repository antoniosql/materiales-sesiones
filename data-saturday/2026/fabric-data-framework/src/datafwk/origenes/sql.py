"""Lectura Azure SQL mediante el conector nativo de Spark y autenticación Entra."""

from __future__ import annotations

import importlib
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from datafwk.config import ConexionSql, Fuente, identificador
from datafwk.errores import ConfiguracionInvalida
from datafwk.incremental import Intervalo, utc

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession


def consulta(fuente: Fuente, intervalo: Intervalo) -> str:
    origen = fuente.origen_sql
    if origen is None:
        raise ConfiguracionInvalida("se esperaba una fuente SQL")
    columnas = [f"[{identificador(k)}] AS [{identificador(v)}]" for k, v in origen.columnas.items()]
    marca = fuente.extraccion.columna_marca
    condiciones = []
    if marca:
        marca = identificador(marca)
        columnas.append(f"[{marca}] AS [_source_updated_at]")
        condiciones.append(f"[{marca}] <= CAST('{utc(intervalo.hasta).isoformat()}' AS datetimeoffset)")
        if intervalo.desde is not None:
            condiciones.append(f"[{marca}] >= CAST('{utc(intervalo.desde).isoformat()}' AS datetimeoffset)")
    filtro = " WHERE " + " AND ".join(condiciones) if condiciones else ""
    # Solo identificadores validados y datetimes tipados; nunca se acepta SQL del usuario.
    return (
        f"SELECT {', '.join(columnas)} FROM [{identificador(origen.esquema)}].[{identificador(origen.tabla)}]{filtro}"  # noqa: S608 -- identificadores en lista permitida y límites datetime tipados
    )


def leer_consulta(spark: SparkSession, conexion: ConexionSql, texto: str) -> DataFrame:
    # El módulo registra .mssql en DataFrameReader; las credenciales pertenecen a Fabric.
    importlib.import_module("com.microsoft.sqlserver.jdbc.spark")
    return spark.read.option("url", conexion.url).option("query", texto).mssql()


def reloj(spark: SparkSession, conexion: ConexionSql) -> datetime:
    fila = leer_consulta(
        spark, conexion, "SELECT datediff_big(microsecond, '1970-01-01', sysutcdatetime()) AS reloj"
    ).first()
    if fila is None:
        raise ConfiguracionInvalida("SQL no devolvió el reloj del origen")
    return datetime.fromtimestamp(fila["reloj"] / 1_000_000, timezone.utc)


def leer(spark: SparkSession, fuente: Fuente, conexion: ConexionSql, intervalo: Intervalo) -> DataFrame:
    return leer_consulta(spark, conexion, consulta(fuente, intervalo))
