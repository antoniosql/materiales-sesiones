"""Publica config/ y contracts/ en OneLake: <workspace_datos>/lh_bronze.Lakehouse/Files/_framework/.

Los notebooks leen la configuración desde ahí (datafwk.arranque). Así la configuración que se ejecuta
es siempre la del commit desplegado, no la que alguien editó a mano en el lakehouse.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from datafwk.arranque import CARPETA_CONFIG, LAKEHOUSE_CONFIG  # noqa: E402
from datafwk.config import Entorno, cargar_yaml  # noqa: E402

ONELAKE = "https://onelake.dfs.fabric.microsoft.com"


def main(credencial=None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--entorno", required=True, choices=["dev", "test", "prod"])
    args = parser.parse_args()

    from azure.identity import AzureCliCredential
    from azure.storage.filedatalake import DataLakeServiceClient

    entorno = Entorno.desde_dict(cargar_yaml(str(RAIZ / "config" / "entornos" / f"{args.entorno}.yml")))
    sistema = DataLakeServiceClient(ONELAKE, credential=credencial or AzureCliCredential()).get_file_system_client(
        entorno.workspace_datos
    )
    ficheros = sorted([*(RAIZ / "config").rglob("*.yml"), *(RAIZ / "contracts").rglob("*.yml")])
    for local in ficheros:
        destino = f"{LAKEHOUSE_CONFIG}.Lakehouse/Files/{CARPETA_CONFIG}/{local.relative_to(RAIZ).as_posix()}"
        sistema.get_file_client(destino).upload_data(local.read_bytes(), overwrite=True)
        print(f"  {destino}")
    print(f"{len(ficheros)} ficheros publicados en {entorno.workspace_datos}")


if __name__ == "__main__":
    main()
