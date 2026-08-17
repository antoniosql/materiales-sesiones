from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    fuente: str = ""
    calculo: str = ""
    valor: str = ""


class SpecialistResult(BaseModel):
    agent: str
    hallazgos: list[Any] = Field(default_factory=list)
    evidencias: list[Any] = Field(default_factory=list)
    riesgos: list[str] = Field(default_factory=list)
    confianza: float = 0.0


class OrchestratorResult(BaseModel):
    pregunta: str
    causa_probable: str
    evidencias: list[Evidence] = Field(default_factory=list)
    riesgos: list[str] = Field(default_factory=list)
    accion_7_dias: str
    metrica_seguimiento: str
    requiere_validacion_humana: bool
