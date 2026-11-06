"""Genera una copia independiente y parametrizada de esta plantilla en una carpeta nueva."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
EXCLUIR = {
    ".git",
    ".venv",
    "venv",
    ".herramientas",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "__pycache__",
    "dist",
    "build",
    "spark-warehouse",
    "metastore_db",
    ".terraform",
    ".agent",
    ".agents",
    ".codex",
    ".aws",
}


def excluido(ruta: Path) -> bool:
    return (
        ruta.name in EXCLUIR
        or (ruta.name.startswith(".env") and ruta.name != ".env.alumno.example")
        or ruta.suffix in {".pyc", ".tfstate", ".tfvars"}
        or ruta.name.endswith(".egg-info")
        or ruta.name == "derby.log"
    )


def crear(destino: Path, proyecto: str, origen: Path = RAIZ) -> int:
    if not re.fullmatch(r"[a-z][a-z0-9-]{2,39}", proyecto):
        raise ValueError("proyecto debe tener entre 3 y 40 letras minúsculas, números o guiones")
    origen, destino = origen.resolve(), destino.resolve()
    if destino == origen or destino.is_relative_to(origen) or origen.is_relative_to(destino):
        raise ValueError("el destino no puede estar dentro de la plantilla ni contenerla")
    if destino.exists():
        raise ValueError("el destino debe ser una carpeta nueva; no se sobrescribe ningún proyecto")
    candidatas = []
    for ruta in origen.rglob("*"):
        relativa = ruta.relative_to(origen)
        if relativa.parts[:2] == ("data", "laboratorio"):
            continue
        if any(excluido(Path(p)) for p in relativa.parts):
            continue
        if ruta.is_symlink():
            raise ValueError(f"no se copian enlaces simbólicos: {relativa}")
        if ruta.is_file():
            candidatas.append((ruta, relativa))
    # Valida todo antes de crear el destino. No ejecuta Git, despliegues ni conexiones externas.
    destino.mkdir(parents=True)
    for ruta, relativa in candidatas:
        salida = destino / relativa
        salida.parent.mkdir(parents=True, exist_ok=True)
        if ruta.name == ".platform":
            datos = json.loads(ruta.read_text(encoding="utf-8"))
            datos["config"]["logicalId"] = str(uuid.uuid4())
            salida.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        elif relativa.parts[0] == "config" or ruta.name in {"parameter.yml", "notebook-content.py"}:
            salida.write_text(ruta.read_text(encoding="utf-8").replace("proyecto-", proyecto + "-"), encoding="utf-8")
        else:
            shutil.copy2(ruta, salida)
    return len(candidatas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destino", type=Path)
    parser.add_argument("--proyecto", required=True)
    args = parser.parse_args()
    print(f"Proyecto creado: {crear(args.destino, args.proyecto)} ficheros en {args.destino.resolve()}")
