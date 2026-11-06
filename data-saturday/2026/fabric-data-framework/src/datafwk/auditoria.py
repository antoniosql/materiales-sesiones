"""Columnas técnicas y registro de ejecuciones.

Sin _ingested_at, _source y _batch_id no se puede responder a la pregunta
"¿de dónde sale este dato y cuándo llegó?".
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession

COLUMNAS_TECNICAS = ("_ingested_at", "_source", "_batch_id")


def nuevo_batch_id() -> str:
    return f"{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:8]}"


def anadir_columnas_tecnicas(df: DataFrame, fuente: str, batch_id: str) -> DataFrame:
    from pyspark.sql import functions as F

    return (
        df.withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source", F.lit(fuente))
        .withColumn("_batch_id", F.lit(batch_id))
    )


@dataclass
class Ejecucion:
    batch_id: str
    entorno: str
    capa: str
    fuente: str
    tabla: str
    inicio: datetime
    fin: datetime | None = None
    filas_leidas: int = 0
    filas_escritas: int = 0
    filas_rechazadas: int = 0
    filas_consolidadas: int = 0
    estado: str = "en_curso"
    mensaje: str = ""

    @property
    def reconcilia(self) -> bool:
        """Leídas = escritas + rechazadas. Si no cuadra, hay filas que se han perdido por el camino."""
        return self.filas_leidas == self.filas_escritas + self.filas_rechazadas + self.filas_consolidadas

    def cerrar(self, estado: str = "ok", mensaje: str = "") -> Ejecucion:
        self.fin = datetime.now(timezone.utc)
        self.estado = estado if (estado != "ok" or self.reconcilia) else "no_reconcilia"
        self.mensaje = mensaje
        return self


def registrar_ejecucion(spark: SparkSession, ejecucion: Ejecucion, ruta_tabla: str) -> None:
    esquema = (
        "batch_id string, entorno string, capa string, fuente string, tabla string, inicio timestamp, fin timestamp, "
        "filas_leidas long, filas_escritas long, filas_rechazadas long, filas_consolidadas long, "
        "estado string, mensaje string"
    )
    spark.createDataFrame([asdict(ejecucion)], esquema).write.format("delta").mode("append").option(
        "mergeSchema", "true"
    ).save(ruta_tabla)
