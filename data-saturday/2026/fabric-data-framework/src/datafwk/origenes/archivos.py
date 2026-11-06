"""Ventana temporal sobre archivos: filtrado lógico, sin prometer lectura parcial del CSV."""

from __future__ import annotations

from typing import TYPE_CHECKING

from datafwk.config import Extraccion
from datafwk.errores import ConfiguracionInvalida
from datafwk.incremental import Intervalo

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


def aplicar_ventana(df: DataFrame, extraccion: Extraccion, intervalo: Intervalo) -> DataFrame:
    from pyspark.sql import functions as F

    marca = extraccion.columna_marca
    if marca is None:
        return df
    if marca not in df.columns:
        raise ConfiguracionInvalida(f"No existe la columna de marca {marca} en el archivo")
    resultado = df.withColumn("_source_updated_at", F.expr(f"try_cast(`{marca}` AS TIMESTAMP)"))
    if resultado.where(F.col("_source_updated_at").isNull()).limit(1).count():
        raise ConfiguracionInvalida("Hay marcas temporales nulas o inválidas; no se puede avanzar la ventana")
    condicion = F.col("_source_updated_at") <= F.lit(intervalo.hasta)
    if intervalo.desde is not None:
        condicion = condicion & (F.col("_source_updated_at") >= F.lit(intervalo.desde))
    return resultado.where(condicion)
