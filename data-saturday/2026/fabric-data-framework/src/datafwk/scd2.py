"""Transformaciones SCD2 por observación. No consultan ni escriben almacenamiento."""

from __future__ import annotations

from datetime import datetime
from functools import reduce
from operator import and_, or_
from typing import TYPE_CHECKING

from datafwk.config import Modelo
from datafwk.errores import ContratoIncumplido
from datafwk.incremental import utc

if TYPE_CHECKING:
    from pyspark.sql import DataFrame

TECNICAS = ("id_version", "vigente_desde", "vigente_hasta", "es_actual", "_hash_scd2", "_batch_id")


def validar_claves(df: DataFrame, claves: tuple[str, ...]) -> None:
    from pyspark.sql import functions as F

    if not claves:
        raise ContratoIncumplido("la clave no puede estar vacía")
    if df.where(reduce(or_, (F.col(c).isNull() for c in claves))).limit(1).count():
        raise ContratoIncumplido("clave nula")
    if df.groupBy(*claves).count().where("count > 1").limit(1).count():
        raise ContratoIncumplido("clave duplicada")


def inicializar(df: DataFrame, modelo: Modelo, instante: datetime, batch_id: str) -> DataFrame:
    """Conserva el estado conocido desde la activación; no inventa historia previa."""
    from pyspark.sql import functions as F

    validar_claves(df, modelo.clave_negocio)
    resultado = (
        df.select(*modelo.columnas)
        .withColumn("vigente_desde", F.lit(utc(instante)))
        .withColumn("vigente_hasta", F.lit(None).cast("timestamp"))
        .withColumn("es_actual", F.lit(True))
        .withColumn("_batch_id", F.lit(batch_id))
    )
    return (
        resultado.withColumn(
            "_hash_scd2", F.sha2(F.to_json(F.struct(*modelo.columnas_scd2), {"ignoreNullFields": "false"}), 256)
        )
        .withColumn("id_version", F.sha2(F.to_json(F.struct(*modelo.clave_negocio, "vigente_desde", "_batch_id")), 256))
        .select(*modelo.columnas, *TECNICAS)
    )


def evolucionar(
    historico: DataFrame, entrada: DataFrame, modelo: Modelo, instante: datetime, batch_id: str
) -> DataFrame:
    """Devuelve el histórico completo candidato. Cierre y alta se publican en un único MERGE."""
    from pyspark.sql import functions as F

    validar_historia(historico, modelo)
    validar_claves(entrada, modelo.clave_negocio)
    actuales = historico.where("es_actual").alias("t")
    nuevos = entrada.select(*modelo.columnas).alias("s")
    union = reduce(and_, (F.col(f"t.{c}") == F.col(f"s.{c}") for c in modelo.clave_negocio))
    cambia = reduce(or_, (~F.col(f"t.{c}").eqNullSafe(F.col(f"s.{c}")) for c in modelo.columnas_scd2))
    comparadas = actuales.join(nuevos, union, "inner")
    # Repetir un lote sin cambios es inocuo; un cambio distinto en el mismo instante no lo es.
    fuera_orden = (F.col("t.vigente_desde") > F.lit(utc(instante))) | (
        cambia & (F.col("t.vigente_desde") == F.lit(utc(instante)))
    )
    if comparadas.where(fuera_orden).limit(1).count():
        raise ContratoIncumplido("observación fuera de orden o dos cambios en el mismo instante")
    altas = nuevos.join(actuales, union, "left").where(F.col("t.id_version").isNull() | cambia).select("s.*")
    altas = inicializar(altas, modelo, instante, batch_id)
    presentes = F.col(f"s.{modelo.clave_negocio[0]}").isNotNull()
    cerrar = presentes & cambia
    expresiones = []
    for c in (*modelo.columnas, *TECNICAS):
        valor = F.col(f"t.{c}")
        if c == "vigente_hasta":
            valor = F.when(cerrar, F.lit(utc(instante))).otherwise(valor)
        elif c == "es_actual":
            valor = ~cerrar
        elif c in modelo.columnas_tipo1:
            # Tipo 1 solo actualiza la versión vigente, nunca el histórico cerrado.
            valor = F.when(presentes & ~cambia, F.col(f"s.{c}")).otherwise(valor)
        expresiones.append(valor.alias(c))
    anteriores = actuales.join(nuevos, union, "left").select(*expresiones)
    return historico.where("NOT es_actual").unionByName(anteriores).unionByName(altas)


def validar_historia(df: DataFrame, modelo: Modelo) -> None:
    from pyspark.sql import Window
    from pyspark.sql import functions as F

    validar_claves(df, ("id_version",))
    validar_claves(df.where("es_actual"), modelo.clave_negocio)
    estados = df.groupBy(*modelo.clave_negocio).agg(F.sum(F.col("es_actual").cast("int")).alias("n"))
    if estados.where("n <> 1").limit(1).count():
        raise ContratoIncumplido("cada clave necesita exactamente una versión vigente")
    ventana = Window.partitionBy(*modelo.clave_negocio).orderBy("vigente_desde")
    intervalos = df.withColumn("_siguiente", F.lead("vigente_desde").over(ventana))
    incorrecto = (
        F.col("vigente_desde").isNull()
        | F.col("es_actual").isNull()
        | (F.col("es_actual") != F.col("vigente_hasta").isNull())
        | (F.col("vigente_hasta") <= F.col("vigente_desde"))
        | (
            F.col("_siguiente").isNotNull()
            & (F.col("vigente_hasta").isNull() | (F.col("vigente_hasta") > F.col("_siguiente")))
        )
    )
    if intervalos.where(incorrecto).limit(1).count():
        raise ContratoIncumplido("intervalos SCD2 nulos, vacíos o solapados")


def proyeccion_actual(df: DataFrame, modelo: Modelo) -> DataFrame:
    return df.where("es_actual").select(*modelo.columnas)
