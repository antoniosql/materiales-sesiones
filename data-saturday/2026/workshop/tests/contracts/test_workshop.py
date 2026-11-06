"""Valida cada checkpoint copiándolo en orden sobre la configuración anterior."""

import json
import shutil
from pathlib import Path

import jsonschema
import yaml

from scripts.validar_contratos import validar

RAIZ = Path(__file__).resolve().parents[2]


def test_checkpoints_workshop_validos(tmp_path):
    for etapa in sorted((RAIZ / "templates/workshop").glob("[0-9]*")):
        shutil.copytree(etapa, tmp_path, dirs_exist_ok=True)
        for ruta in etapa.rglob("*.yml"):
            relativa = ruta.relative_to(etapa)
            tipo = (
                "contrato"
                if relativa.parts[0] == "contracts"
                else {"fuentes": "fuentes", "modelos": "modelo"}[relativa.parts[1]]
            )
            esquema = json.loads((RAIZ / f"schemas/{tipo}.schema.json").read_text(encoding="utf-8"))
            jsonschema.validate(yaml.safe_load(ruta.read_text(encoding="utf-8")), esquema)
        assert validar(tmp_path) == []
