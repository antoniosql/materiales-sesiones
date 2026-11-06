"""Registro de lo que crean los scripts (state/deployed.json).

La limpieza solo borra lo que está aquí con created=True: lo que ya existía en el
tenant (usuarios reutilizados, etiquetas previas…) se registra con created=False y no se toca.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class State:
    def __init__(self, path: Path):
        self.path = path
        self.data = {"resources": [], "notes": {}}
        if path.exists():
            self.data = json.loads(path.read_text(encoding="utf-8"))
            self.data.setdefault("resources", [])
            self.data.setdefault("notes", {})

    # --- recursos -----------------------------------------------------------
    def get(self, rtype: str, key: str) -> dict | None:
        for r in self.data["resources"]:
            if r["type"] == rtype and r["key"] == key:
                return r
        return None

    def put(self, rtype: str, key: str, rid: str, created: bool, **extra) -> dict:
        existing = self.get(rtype, key)
        if existing:
            existing.update({"id": rid, **extra})
            # si alguna vez lo creamos nosotros, sigue siendo nuestro
            existing["created"] = existing.get("created", False) or created
            self.save()
            return existing
        rec = {"type": rtype, "key": key, "id": rid, "created": created,
               "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **extra}
        self.data["resources"].append(rec)
        self.save()
        return rec

    def remove(self, rtype: str, key: str) -> None:
        self.data["resources"] = [r for r in self.data["resources"]
                                  if not (r["type"] == rtype and r["key"] == key)]
        self.save()

    def of_type(self, rtype: str) -> list[dict]:
        return [r for r in self.data["resources"] if r["type"] == rtype]

    # --- notas libres (p. ej. sitios pendientes de purgar) ------------------
    def note(self, key: str, value) -> None:
        self.data["notes"][key] = value
        self.save()

    def get_note(self, key: str, default=None):
        return self.data["notes"].get(key, default)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
