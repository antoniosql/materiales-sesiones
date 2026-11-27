"""Clasificación de correos de devolución por motivo (códigos de FS-KB-01 v1.3).

Reglas deterministas a propósito: la demo va de identidad, no de modelos. La versión
con Claude Agent SDK es la que se usó en el Bizz Summit 2026.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter

MOTIVOS = {
    "R01": "No me gusta / cambio de opinión",
    "R02": "No encaja (medidas/estilo)",
    "R03": "Defecto de fabricación",
    "R04": "Daño en transporte",
    "R05": "Faltan piezas / incompleto",
    "R06": "Error de preparación (producto incorrecto)",
    "R00": "Sin clasificar: revisión humana",
}

# El orden importa: las incidencias (R06…R03) antes que las voluntarias (R02, R01).
REGLAS: list[tuple[str, tuple[str, ...]]] = [
    ("R06", ("producto equivocado", "otro modelo", "no es el que pedi", "me ha llegado otro", "me llego otro",
             "producto incorrecto", "color equivocado", "referencia equivocada")),
    ("R05", ("falta", "faltan", "incomplet", "sin tornillos", "piezas")),
    ("R04", ("llego roto", "llego rota", "llego ayer con", "roto", "rota", "partid", "golpe", "transporte",
             "embalaje danado", "abollad", "aplastad")),
    ("R03", ("defect", "cruje", "no funciona", "no enciende", "fallo", "mancha", "costura", "se ha roto", "se rompio",
             "parpadea")),
    ("R02", ("no encaja", "medidas", "no cabe", "demasiado grande", "demasiado pequen", "estilo", "tamano")),
    ("R01", ("no me gusta", "cambio de opinion", "arrepent", "ya no lo quiero", "he cambiado de idea",
             "no me convence")),
]

UMBRAL_PATRON = 3


def _normaliza(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    return re.sub(r"\s+", " ", "".join(c for c in texto if not unicodedata.combining(c)))


def clasificar(asunto: str, cuerpo: str) -> tuple[str, str]:
    texto = _normaliza(f"{asunto} {cuerpo}")
    for codigo, pistas in REGLAS:
        if any(p in texto for p in pistas):
            return codigo, MOTIVOS[codigo]
    return "R00", MOTIVOS["R00"]


def patrones(remitentes: list[str]) -> list[str]:
    """Remitentes con varias devoluciones: lo que interesa a Prevención de Pérdidas."""
    return [r for r, n in Counter(remitentes).items() if n >= UMBRAL_PATRON]


def resumen(resultados: list[dict]) -> str:
    por_motivo = Counter(r["motivo"] for r in resultados)
    lineas = [f"# Resumen de devoluciones para el Store Manager · {len(resultados)} correos", ""]
    lineas += [f"- {codigo} · {MOTIVOS[codigo]}: {n}" for codigo, n in sorted(por_motivo.items())]
    sospechosos = patrones([r["remitente"] for r in resultados])
    if sospechosos:
        lineas += ["", "## A revisar por Prevención de Pérdidas"] + [f"- {s}" for s in sospechosos]
    return "\n".join(lineas) + "\n"
