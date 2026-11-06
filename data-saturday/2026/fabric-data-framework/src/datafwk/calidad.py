"""Aplicación de contratos de datos: tipado, nulos, valores permitidos y reglas de negocio.

aplicar_contrato() devuelve (validas, rechazadas). Las rechazadas llevan la columna
_motivo_rechazo (array<string>) con TODOS los motivos, no solo el primero: quien revisa
la cuarentena necesita saber todo lo que está mal en una fila.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from datafwk.config import Contrato
from datafwk.errores import ContratoIncumplido

if TYPE_CHECKING:
    from pyspark.sql import Column, DataFrame

COLUMNA_MOTIVO = "_motivo_rechazo"


def _nulo() -> Column:
    from pyspark.sql import functions as F

    return F.lit(None).cast("string")


def aplicar_contrato(df: DataFrame, contrato: Contrato) -> tuple[DataFrame, DataFrame]:
    from pyspark.sql import functions as F

    faltan = [c for c in contrato.nombres_columnas if c not in df.columns]
    if faltan:
        raise ContratoIncumplido(f"{contrato.tabla}: faltan columnas del contrato: {faltan}")

    tecnicas = [c for c in df.columns if c.startswith("_") and c not in contrato.nombres_columnas]

    # 1. Tipado. Un valor que no se puede convertir no se pierde en silencio: es un rechazo.
    errores_tipo = [
        F.when(
            F.col(c.nombre).isNotNull() & F.expr(f"try_cast(`{c.nombre}` AS {c.tipo})").isNull(),
            F.lit(f"tipo:{c.nombre}"),
        )
        for c in contrato.columnas
    ]
    tipado = df.select(
        *[F.expr(f"try_cast(`{c.nombre}` AS {c.tipo})").alias(c.nombre) for c in contrato.columnas],
        *[F.col(c) for c in tecnicas],
        F.array(_nulo(), *errores_tipo).alias("_errores_tipo"),
    )

    # 2. Nulos, valores permitidos y reglas, sobre los datos ya tipados.
    comprobaciones = []
    for c in contrato.columnas:
        if not c.nulo:
            comprobaciones.append(F.when(F.col(c.nombre).isNull(), F.lit(f"nulo:{c.nombre}")))
        if c.valores:
            comprobaciones.append(
                F.when(
                    F.col(c.nombre).isNotNull() & ~F.col(c.nombre).isin(list(c.valores)),
                    F.lit(f"valor:{c.nombre}"),
                )
            )
    for r in contrato.reglas:
        # Un nulo no incumple una regla: de los nulos se ocupa 'nulo: false'.
        comprobaciones.append(F.when(~F.coalesce(F.expr(r.expresion), F.lit(True)), F.lit(f"regla:{r.nombre}")))

    motivos = F.filter(F.concat(F.col("_errores_tipo"), F.array(_nulo(), *comprobaciones)), lambda x: x.isNotNull())
    evaluado = tipado.withColumn(COLUMNA_MOTIVO, motivos).drop("_errores_tipo")

    validas = evaluado.where(F.size(COLUMNA_MOTIVO) == 0).drop(COLUMNA_MOTIVO)
    rechazadas = evaluado.where(F.size(COLUMNA_MOTIVO) > 0)
    return validas, rechazadas
