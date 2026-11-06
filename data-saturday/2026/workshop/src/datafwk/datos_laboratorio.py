"""Mutaciones puras del origen CSV docente; no modifica el volcado ni DataFrames extraídos."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

Fila = dict[str, str]
NULO = "\\N"


def candidatos_calidad(filas: list[Fila]) -> list[str]:
    validos = []
    for fila in sorted(filas, key=lambda f: f["id_linea_devolucion"]):
        try:
            importe = Decimal(fila["importe_reembolso"])
        except InvalidOperation:
            continue
        if importe.is_finite() and importe >= 0 and fila["motivo"] not in (NULO, ""):
            validos.append(fila["id_linea_devolucion"])
    if len(validos) < 4:
        raise ValueError("Se necesitan cuatro devoluciones válidas para las demos")
    return validos[:4]


def defectos(filas: list[Fila], ids: list[str]) -> list[Fila]:
    if len(ids) != 4 or len(set(ids)) != 4:
        raise ValueError("Se requieren cuatro claves distintas")
    cambios = {
        ids[0]: {"importe_reembolso": "-1.00"},
        ids[1]: {"importe_reembolso": NULO},
        ids[2]: {"motivo": NULO},
        ids[3]: {"motivo": NULO},
    }
    if not set(ids).issubset({f["id_linea_devolucion"] for f in filas}):
        raise ValueError("Faltan las claves de la demo")
    return [{**fila, **cambios.get(fila["id_linea_devolucion"], {})} for fila in filas]


def cambiar_ciudad(filas: list[Fila], cliente: str, ciudad: str, instante: str) -> list[Fila]:
    if sum(f["id_cliente"] == cliente for f in filas) != 1:
        raise ValueError("El cliente debe existir exactamente una vez")
    return [
        {**fila, "ciudad": ciudad, "fecha_cambio": instante} if fila["id_cliente"] == cliente else dict(fila)
        for fila in filas
    ]
