"""Transformaciones puras de estandarización. Se prueban en local con Spark (tests/unit)."""

from __future__ import annotations

import re
import unicodedata
from typing import TYPE_CHECKING

from datafwk.errores import ConfiguracionInvalida

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


def a_snake_case(nombre: str) -> str:
    """'FechaPedido' -> 'fecha_pedido'; 'Importe (€)' -> 'importe'; 'Año Fiscal' -> 'ano_fiscal'."""
    sin_acentos = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode("ascii")
    separado = re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", sin_acentos)
    limpio = re.sub(r"[^0-9a-zA-Z]+", "_", separado).strip("_").lower()
    return re.sub(r"_+", "_", limpio)


def renombrar_columnas(df: DataFrame) -> DataFrame:
    """Pasa a snake_case todas las columnas de negocio. Las técnicas (prefijo '_') no se tocan."""
    nuevos = [c if c.startswith("_") else a_snake_case(c) for c in df.columns]
    duplicados = sorted({n for n in nuevos if nuevos.count(n) > 1})
    if duplicados:
        raise ConfiguracionInvalida(f"al pasar a snake_case colisionan las columnas: {duplicados}")
    return df.toDF(*nuevos)


def deduplicar(df: DataFrame, clave: tuple[str, ...] | list[str], orden: str | None = None) -> DataFrame:
    """Una fila por clave de negocio. Con 'orden', se queda con la más reciente según esa columna."""
    if not orden:
        return df.dropDuplicates(list(clave))

    from pyspark.sql import Window
    from pyspark.sql import functions as F

    ventana = Window.partitionBy(*clave).orderBy(F.col(orden).desc())
    return df.withColumn("_rn", F.row_number().over(ventana)).where("_rn = 1").drop("_rn")
