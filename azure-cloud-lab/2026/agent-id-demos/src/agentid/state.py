"""Registro de lo desplegado (state/estado.json).

Cada recurso se guarda con su id y con `creado`: True si lo crearon estos scripts. La limpieza
solo borra lo creado; lo que ya existía se reutiliza y no se toca.
"""

from __future__ import annotations

import json
from pathlib import Path


class Estado:
    def __init__(self, carpeta: Path) -> None:
        carpeta.mkdir(parents=True, exist_ok=True)
        self.ruta = carpeta / "estado.json"
        self.datos: dict = json.loads(self.ruta.read_text(encoding="utf-8")) if self.ruta.exists() else {}

    def guardar(self) -> None:
        self.ruta.write_text(json.dumps(self.datos, ensure_ascii=False, indent=2), encoding="utf-8")

    def registrar(self, clave: str, id_: str, creado: bool, **extra) -> None:
        previo = self.datos.get(clave, {})
        # si alguna vez lo creamos nosotros, sigue siendo nuestro aunque luego se reutilice
        self.datos[clave] = {**previo, **extra, "id": id_, "creado": bool(previo.get("creado")) or creado}
        self.guardar()

    def id(self, clave: str) -> str | None:
        return self.datos.get(clave, {}).get("id")

    def get(self, clave: str, defecto=None):
        return self.datos.get(clave, defecto)

    def poner(self, clave: str, valor) -> None:
        self.datos[clave] = valor
        self.guardar()

    def quitar(self, clave: str) -> None:
        self.datos.pop(clave, None)
        self.guardar()
