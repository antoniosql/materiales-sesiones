"""Despliega las carpetas de fabric/ en los workspaces de un entorno con fabric-cicd.

Uso (en el pipeline, tras azure/login): python scripts/desplegar.py --entorno test
Los IDs de workspace llegan por variables de entorno (vars del GitHub Environment).
Verificar la API contra la versión de fabric-cicd fijada en pyproject.toml.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# Orden de despliegue: primero dónde están los datos, después quién los procesa, al final quién los consume.
WORKSPACES = [
    # carpeta,     variable con el ID,  tipos de item,                                   limpiar huérfanos
    ("datos", "WS_DATOS_ID", ["Lakehouse"], False),  # NUNCA borrar lakehouses: contienen los datos
    ("ingenieria", "WS_ING_ID", ["Environment", "Notebook", "DataPipeline"], True),
    ("analitica", "WS_ANA_ID", ["SemanticModel", "Report"], True),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--entorno", required=True, choices=["dev", "test", "prod"])
    parser.add_argument("--solo", choices=[w[0] for w in WORKSPACES], help="desplegar un único workspace")
    args = parser.parse_args()

    from azure.identity import AzureCliCredential
    from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items

    credencial = AzureCliCredential()
    for carpeta, variable, tipos, limpiar in WORKSPACES:
        if args.solo and carpeta != args.solo:
            continue
        print(f"→ {args.entorno} · {carpeta}")
        workspace = FabricWorkspace(
            workspace_id=os.environ[variable],
            environment=args.entorno.upper(),
            repository_directory=str(RAIZ / "fabric" / carpeta),
            item_type_in_scope=tipos,
            token_credential=credencial,
        )
        publish_all_items(workspace)
        if limpiar:
            unpublish_all_orphan_items(workspace)


if __name__ == "__main__":
    main()
