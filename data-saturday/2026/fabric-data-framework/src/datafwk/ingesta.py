"""SQL o landing -> bronze inmutable; los reintentos reutilizan la observación persistida."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from datafwk import rutas
from datafwk.auditoria import Ejecucion, nuevo_batch_id, registrar_ejecucion
from datafwk.config import Entorno, Fuente
from datafwk.control import Control, Lote, existe, leer_version, version
from datafwk.incremental import planificar
from datafwk.origenes import archivos, sql

if TYPE_CHECKING:
    from pyspark.sql import SparkSession


def a_bronze(spark: SparkSession, fuente: Fuente, entorno: Entorno, batch_id: str | None = None) -> Ejecucion:
    from pyspark.sql import functions as F

    spark.conf.set("spark.sql.session.timeZone", "UTC")
    batch_id = batch_id or nuevo_batch_id()
    destino = rutas.tabla(entorno, "bronze", fuente.tabla_bronze)
    control = Control(spark, entorno)
    ejecucion = Ejecucion(
        batch_id, entorno.nombre, "bronze", fuente.identidad, fuente.tabla_bronze, datetime.now(timezone.utc)
    )
    try:
        lote = control.lote(fuente.identidad, batch_id)
        if lote is None:
            ahora = (
                sql.reloj(spark, entorno.conexiones_sql[fuente.origen_sql.conexion])
                if fuente.origen_sql
                else datetime.now(timezone.utc)
            )
            intervalo = planificar(fuente.extraccion, ahora, control.marca(fuente.identidad))
            lote = control.iniciar(
                Lote(
                    fuente.identidad,
                    batch_id,
                    "iniciado",
                    intervalo.observado_en,
                    intervalo.desde,
                    intervalo.hasta,
                    fuente.extraccion.modo,
                )
            )
        # Recupera incluso el fallo entre el append de bronze y la actualización del control.
        previo = (
            leer_version(spark, destino, lote.version_bronze).where(F.col("_batch_id") == batch_id)
            if existe(spark, destino)
            else None
        )
        if lote.version_bronze is not None or (previo is not None and previo.limit(1).count()):
            total = previo.count() if previo is not None else 0
        else:
            if fuente.origen_sql:
                df = sql.leer(spark, fuente, entorno.conexiones_sql[fuente.origen_sql.conexion], lote.intervalo)
            else:
                df = (
                    spark.read.format(fuente.formato)
                    .options(**fuente.opciones_lectura)
                    .load(rutas.ficheros(entorno, "bronze", fuente.ruta_landing))
                )
                df = archivos.aplicar_ventana(df, fuente.extraccion, lote.intervalo)
            df = (
                df.withColumn("_ingested_at", F.lit(lote.observado_en))
                .withColumn("_observado_en", F.lit(lote.observado_en))
                .withColumn("_source", F.lit(fuente.identidad))
                .withColumn("_batch_id", F.lit(batch_id))
            )
            # Una sola lectura de SQL; el conteo se hace sobre Delta, nunca relee el origen mutable.
            (
                df.write.format("delta")
                .mode("append")
                .option("mergeSchema", "true")
                .option("txnAppId", f"{fuente.identidad}:{batch_id}")
                .option("txnVersion", 0)
                .save(destino)
            )
            total = leer_version(spark, destino).where(F.col("_batch_id") == batch_id).count()
        if lote.version_bronze is None:
            control.guardar(replace(lote, estado="bronze", version_bronze=version(spark, destino)))
        ejecucion.filas_leidas = ejecucion.filas_escritas = total
        ejecucion.cerrar()
    except Exception as exc:
        ejecucion.cerrar("error", str(exc)[:2000])
        raise
    finally:
        registrar_ejecucion(spark, ejecucion, rutas.auditoria(entorno))
    return ejecucion
