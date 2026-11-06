"""Calidad versionada sobre observaciones inmutables, publicación y confirmación de marca."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from datafwk import rutas
from datafwk.auditoria import Ejecucion, registrar_ejecucion
from datafwk.calidad import aplicar_contrato
from datafwk.config import Contrato, Entorno, Fuente
from datafwk.control import Control, Lote, leer_version, version
from datafwk.errores import ConfiguracionInvalida, ContratoIncumplido
from datafwk.escritura import escribir
from datafwk.estandarizar import renombrar_columnas
from datafwk.observaciones import con_dato_bruto, evidencias, ultimas
from datafwk.scd2 import validar_claves

if TYPE_CHECKING:
    from pyspark.sql import SparkSession


def a_silver(
    spark: SparkSession,
    fuente: Fuente,
    contrato: Contrato,
    entorno: Entorno,
    batch_id: str | None = None,
    *,
    revalidar: bool = False,
) -> Ejecucion:
    """Exige batch explícito. Revalidar reconstruye el estado actual desde todo bronze sin avanzar la marca."""
    from pyspark.sql import functions as F

    if not batch_id:
        raise ConfiguracionInvalida("indica batch_id; para revisar reglas usa revalidar=True y un lote nuevo")
    spark.conf.set("spark.sql.session.timeZone", "UTC")
    control = Control(spark, entorno)
    identidad = fuente.identidad
    lote = control.lote(identidad, batch_id)
    bronze = rutas.tabla(entorno, "bronze", fuente.tabla_bronze)
    if revalidar and lote is None:
        ahora = datetime.now(timezone.utc)
        lote = control.iniciar(
            Lote(
                identidad,
                batch_id,
                "revalidacion",
                ahora,
                None,
                ahora,
                "revalidacion",
                version_bronze=version(spark, bronze),
                version_contrato=contrato.version,
            )
        )
    if lote is None or lote.version_bronze is None:
        raise ConfiguracionInvalida("bronze debe finalizar antes de silver")
    if (lote.modo == "revalidacion") != revalidar:
        raise ConfiguracionInvalida("el tipo de lote no coincide con la operación solicitada")
    ejecucion = Ejecucion(
        batch_id, entorno.nombre, "silver", identidad, fuente.tabla_silver, datetime.now(timezone.utc)
    )
    validas = rechazadas = None
    try:
        if lote.estado == "confirmado":
            if contrato.version != lote.version_contrato:
                raise ConfiguracionInvalida("el lote ya usó otra versión de contrato; crea una revalidación")
            return ejecucion.cerrar("reutilizado")
        origen = leer_version(spark, bronze, lote.version_bronze)
        if not revalidar:
            origen = origen.where(F.col("_batch_id") == batch_id)
        if "_observado_en" not in origen.columns:
            origen = origen.withColumn("_observado_en", F.col("_ingested_at"))
        origen = renombrar_columnas(origen)
        ejecucion.filas_leidas = origen.count()
        actuales = ultimas(origen, contrato.clave)
        validas, rechazadas = aplicar_contrato(con_dato_bruto(actuales), contrato)
        validas, rechazadas = validas.cache(), rechazadas.cache()
        aceptadas, n_rechazadas = validas.count(), rechazadas.count()
        ejecucion.filas_rechazadas = n_rechazadas
        ejecucion.filas_consolidadas = ejecucion.filas_leidas - aceptadas - n_rechazadas
        if n_rechazadas and contrato.politica_rechazo == "fallar":
            raise ContratoIncumplido(f"{contrato.tabla}: {n_rechazadas} filas incumplen el contrato; no se publica")
        validar_claves(validas, contrato.clave)
        if n_rechazadas:
            escribir(
                spark,
                evidencias(rechazadas, identidad, contrato.version),
                rutas.tabla(entorno, "silver", "fwk_cuarentena"),
                "merge",
                ("id_rechazo",),
            )
        destino = rutas.tabla(entorno, "silver", fuente.tabla_silver)
        escribir(
            spark,
            validas.drop("_dato_bruto"),
            destino,
            "overwrite" if revalidar else fuente.modo_carga,
            contrato.clave,
            batch_id=batch_id,
        )
        ejecucion.filas_escritas = aceptadas
        control.confirmar(lote, version(spark, destino), contrato.version, avanzar=not revalidar)
        ejecucion.cerrar()
    except Exception as exc:
        ejecucion.cerrar("error", str(exc)[:2000])
        raise
    finally:
        if validas is not None:
            validas.unpersist()
        if rechazadas is not None:
            rechazadas.unpersist()
        registrar_ejecucion(spark, ejecucion, rutas.auditoria(entorno))
    return ejecucion
