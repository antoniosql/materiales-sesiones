"""Transformaciones puras de observaciones y evidencias de calidad."""

from __future__ import annotations

from typing import TYPE_CHECKING

from datafwk.errores import ContratoIncumplido

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


def ultimas(df: DataFrame, claves: tuple[str, ...]) -> DataFrame:
    """Elige la última observación; no decide arbitrariamente entre dos valores simultáneos."""
    from pyspark.sql import Window
    from pyspark.sql import functions as F

    orden = [c for c in ("_source_updated_at", "_observado_en", "_ingested_at") if c in df.columns]
    if not orden:
        raise ContratoIncumplido("faltan columnas para ordenar las observaciones")
    negocio = sorted(c for c in df.columns if not c.startswith("_"))
    datos = df.withColumn("_firma_fila", F.to_json(F.struct(*negocio), {"ignoreNullFields": "false"}))
    ventana = Window.partitionBy(*claves).orderBy(*[F.col(c).desc_nulls_last() for c in orden])
    candidatas = datos.withColumn("_posicion", F.dense_rank().over(ventana)).where("_posicion = 1")
    ambiguas = candidatas.groupBy(*claves).agg(F.countDistinct("_firma_fila").alias("n")).where("n > 1")
    if ambiguas.limit(1).count():
        raise ContratoIncumplido("valores contradictorios con la misma clave y orden de observación")
    return candidatas.dropDuplicates(list(claves)).drop("_posicion", "_firma_fila")


def con_dato_bruto(df: DataFrame) -> DataFrame:
    from pyspark.sql import functions as F

    columnas = sorted(c for c in df.columns if not c.startswith("_"))
    return df.withColumn("_dato_bruto", F.to_json(F.struct(*columnas), {"ignoreNullFields": "false"}))


def evidencias(df: DataFrame, fuente: str, version_contrato: int) -> DataFrame:
    from pyspark.sql import functions as F

    resultado = df.select(
        F.lit(fuente).alias("fuente"),
        F.col("_batch_id").alias("batch_id"),
        F.col("_observado_en").alias("observado_en"),
        F.lit(version_contrato).alias("version_contrato"),
        F.col("_dato_bruto").alias("dato_bruto"),
        F.to_json("_motivo_rechazo").alias("motivos"),
        F.lit(None).cast("timestamp").alias("resuelta_en"),
    )
    return resultado.withColumn(
        "id_rechazo",
        F.sha2(F.to_json(F.struct("fuente", "batch_id", "observado_en", "version_contrato", "dato_bruto")), 256),
    ).dropDuplicates(["id_rechazo"])
