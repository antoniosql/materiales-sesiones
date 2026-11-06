"""Publicación recuperable de dimensiones tipo 1 y SCD2 desde una versión confirmada de silver."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from datafwk import rutas, scd2
from datafwk.auditoria import Ejecucion, registrar_ejecucion
from datafwk.calidad import aplicar_contrato
from datafwk.config import Contrato, Entorno, Fuente, Modelo
from datafwk.control import ESQUEMA_MODELOS, Control, existe, guardar_fila, leer_version, version
from datafwk.errores import ConfiguracionInvalida, ContratoIncumplido
from datafwk.escritura import escribir

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession


def comprobar(df: DataFrame, contrato: Contrato) -> DataFrame:
    validas, rechazadas = aplicar_contrato(df, contrato)
    if rechazadas.limit(1).count():
        raise ContratoIncumplido(f"{contrato.tabla}: gold no admite rechazos parciales")
    scd2.validar_claves(validas, contrato.clave)
    return validas


def a_gold(
    spark: SparkSession,
    modelo: Modelo,
    fuente: Fuente,
    contrato: Contrato,
    entorno: Entorno,
    batch_id: str,
    contrato_actual: Contrato | None = None,
    *,
    activar_scd2: bool = False,
) -> Ejecucion:
    from pyspark.sql import functions as F

    spark.conf.set("spark.sql.session.timeZone", "UTC")
    if modelo.origen != fuente.tabla_silver or modelo.dominio != fuente.dominio:
        raise ConfiguracionInvalida("el modelo debe consumir la fuente indicada")
    if contrato.tabla != modelo.modelo or contrato.capa != "gold":
        raise ConfiguracionInvalida("el contrato no corresponde al modelo gold")
    if modelo.tipo == "scd2" and (contrato_actual is None or contrato_actual.tabla != modelo.tabla_actual):
        raise ConfiguracionInvalida("falta el contrato de la proyección actual")
    control = Control(spark, entorno)
    lote = control.lote(fuente.identidad, batch_id)
    if lote is None or lote.estado != "confirmado" or lote.version_silver is None:
        raise ConfiguracionInvalida("gold necesita un lote silver confirmado")
    destino = rutas.tabla(entorno, "gold", modelo.modelo)
    registro = control.ruta("fwk_modelos")
    firma_historia = (
        hashlib.sha256(
            json.dumps([modelo.clave_negocio, modelo.columnas_scd2, modelo.columnas_tipo1], sort_keys=True).encode()
        ).hexdigest()
        if modelo.tipo == "scd2"
        else ""
    )
    firma = hashlib.sha256(
        json.dumps(
            [asdict(modelo), asdict(contrato), asdict(contrato_actual) if contrato_actual else None], sort_keys=True
        ).encode()
    ).hexdigest()
    previo = (
        leer_version(spark, registro)
        .where(F.col("modelo") == modelo.modelo)
        .withColumn("_epoch", F.col("observado_en").cast("double"))
        .first()
        if existe(spark, registro)
        else None
    )
    if previo and previo["batch_id"] != batch_id:
        if previo["estado"] != "confirmado":
            raise ConfiguracionInvalida("reanuda el lote gold pendiente antes de publicar otro")
        if datetime.fromtimestamp(previo["_epoch"], timezone.utc) >= lote.observado_en:
            raise ConfiguracionInvalida("gold debe consumir los lotes en orden de observación")
        if previo["firma_historia"] and previo["firma_historia"] != firma_historia:
            raise ConfiguracionInvalida("cambiar atributos de una dimensión ya SCD2 requiere otra migración")
    if previo and previo["batch_id"] == batch_id:
        datos = previo.asDict()
        datos["observado_en"] = datetime.fromtimestamp(datos.pop("_epoch"), timezone.utc)
        if datos["firma_config"] != firma or datos["migracion"] != activar_scd2:
            raise ConfiguracionInvalida("no cambies modelo/contratos/operación durante un reintento")
    else:
        datos = {
            "modelo": modelo.modelo,
            "batch_id": batch_id,
            "observado_en": lote.observado_en,
            "estado": "preparado",
            "version_silver": lote.version_silver,
            "version_gold": None,
            "firma_config": firma,
            "firma_historia": firma_historia,
            "migracion": activar_scd2,
            "version_previa": version(spark, destino) if existe(spark, destino) else None,
        }
        guardar_fila(spark, registro, datos, ESQUEMA_MODELOS, ("modelo",))
    ejecucion = Ejecucion(batch_id, entorno.nombre, "gold", modelo.modelo, modelo.modelo, datetime.now(timezone.utc))
    try:
        if datos["estado"] == "confirmado":
            return ejecucion.cerrar("reutilizado")
        entrada = leer_version(spark, rutas.tabla(entorno, "silver", fuente.tabla_silver), lote.version_silver).select(
            *modelo.columnas
        )
        ejecucion.filas_leidas = ejecucion.filas_escritas = entrada.count()
        if datos["estado"] == "preparado":
            anterior = (
                leer_version(spark, destino, datos["version_previa"]) if datos["version_previa"] is not None else None
            )
            if modelo.tipo == "tipo1":
                if activar_scd2 or (anterior is not None and "id_version" in anterior.columns):
                    raise ConfiguracionInvalida("no se permite desactivar SCD2 ni activar con configuración tipo1")
                candidato = comprobar(entrada, contrato)
                escribir(spark, candidato, destino, "overwrite", modelo.clave_negocio)
            else:
                migracion = anterior is not None and "id_version" not in anterior.columns
                if migracion != activar_scd2:
                    raise ConfiguracionInvalida("la conversión de tipo1 exige activar_scd2=True explícito")
                if anterior is None or migracion:
                    candidato = scd2.inicializar(
                        entrada if anterior is None else anterior, modelo, lote.observado_en, batch_id
                    )
                else:
                    candidato = scd2.evolucionar(anterior, entrada, modelo, lote.observado_en, batch_id)
                candidato = comprobar(candidato, contrato)
                scd2.validar_historia(candidato, modelo)
                escribir(spark, candidato, destino, "overwrite" if migracion else "merge", ("id_version",))
            datos.update(estado="historia", version_gold=version(spark, destino))
            guardar_fila(spark, registro, datos, ESQUEMA_MODELOS, ("modelo",))
        if modelo.tipo == "scd2" and contrato_actual is not None and modelo.tabla_actual is not None:
            historia = leer_version(spark, destino, datos["version_gold"])
            actual = comprobar(scd2.proyeccion_actual(historia, modelo), contrato_actual)
            escribir(
                spark, actual, rutas.tabla(entorno, "gold", modelo.tabla_actual), "overwrite", modelo.clave_negocio
            )
        datos["estado"] = "confirmado"
        guardar_fila(spark, registro, datos, ESQUEMA_MODELOS, ("modelo",))
        ejecucion.cerrar()
    except Exception as exc:
        ejecucion.cerrar("error", str(exc)[:2000])
        raise
    finally:
        registrar_ejecucion(spark, ejecucion, rutas.auditoria(entorno))
    return ejecucion
