"""Planificación pura de ventanas; no consulta SQL ni confirma marcas."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from datafwk.config import Extraccion
from datafwk.errores import ConfiguracionInvalida


def utc(instante: datetime) -> datetime:
    """Los argumentos Python sin zona se interpretan como UTC; al leer Spark usa epoch, no datetime local."""
    return instante.replace(tzinfo=timezone.utc) if instante.tzinfo is None else instante.astimezone(timezone.utc)


@dataclass(frozen=True)
class Intervalo:
    desde: datetime | None
    hasta: datetime
    observado_en: datetime


def planificar(extraccion: Extraccion, ahora: datetime, marca: datetime | None = None) -> Intervalo:
    observado = utc(ahora)
    hasta = observado - timedelta(seconds=extraccion.estabilizacion_segundos)
    if marca is not None:
        marca = utc(marca)
        if marca > observado:
            raise ConfiguracionInvalida("la marca confirmada está en el futuro")
        hasta = max(hasta, marca)
    if extraccion.modo == "incremental":
        if marca is None:
            raise ConfiguracionInvalida("incremental sin carga completa confirmada; inicializa la fuente")
        return Intervalo(marca - timedelta(seconds=extraccion.solape_segundos), hasta, observado)
    return Intervalo(None, hasta, observado)
