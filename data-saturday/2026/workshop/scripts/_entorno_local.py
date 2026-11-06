"""Lectura de dotenv sin ejecutar comandos ni expandir secretos."""

from pathlib import Path

from dotenv import dotenv_values


def leer(ruta: Path) -> dict[str, str]:
    if not ruta.is_file():
        raise ValueError(f"No existe {ruta}; copia primero el fichero .example")
    return {k: v or "" for k, v in dotenv_values(ruta, interpolate=False).items()}


def obligatorio(datos: dict[str, str], clave: str) -> str:
    valor = datos.get(clave, "")
    if not valor or "<" in valor:
        raise ValueError(f"Completa {clave} en el fichero de entorno")
    return valor
