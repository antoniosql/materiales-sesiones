"""Sube el wheel de datafwk al Environment env_fwk y lo publica.

Usa la API REST de Fabric para Environments (staging + publish). Publicar un Environment tarda
varios minutos; el script espera a que termine.
Referencia: https://learn.microsoft.com/rest/api/fabric/environment/staging/upload-custom-library
"""

from __future__ import annotations

import argparse
import glob
import os
import time
import uuid
from urllib.parse import quote

API = "https://api.fabric.microsoft.com/v1"


def main(credencial=None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", required=True, help="ruta o patrón del .whl")
    args = parser.parse_args()

    import requests
    from azure.identity import AzureCliCredential

    coincidencias = sorted(glob.glob(args.wheel))
    if len(coincidencias) != 1:
        raise SystemExit("El patrón debe identificar exactamente un wheel")
    wheel = coincidencias[0]
    workspace, environment = os.environ["WS_ING_ID"], os.environ["ENV_FWK_ID"]
    token = (credencial or AzureCliCredential()).get_token("https://api.fabric.microsoft.com/.default").token
    cabeceras = {"Authorization": f"Bearer {token}"}
    base = f"{API}/workspaces/{workspace}/environments/{environment}"

    with open(wheel, "rb") as f:
        r = requests.post(
            f"{base}/staging/libraries/{quote(os.path.basename(wheel), safe='')}",
            headers={**cabeceras, "Content-Type": "application/octet-stream"},
            data=f,
            timeout=300,
        )
    r.raise_for_status()
    print(f"Subido {os.path.basename(wheel)}")

    r = requests.post(f"{base}/staging/publish", params={"beta": "false"}, headers=cabeceras, timeout=60)
    r.raise_for_status()
    operacion = None
    if r.status_code == 202:
        identificador = r.headers.get("x-ms-operation-id")
        if not identificador:
            raise SystemExit("Fabric aceptó la publicación sin identificador de operación; revisar en el portal")
        operacion = f"{API}/operations/{uuid.UUID(identificador)}"
    for _ in range(60):
        respuesta = requests.get(operacion or base, headers=cabeceras, timeout=60)
        respuesta.raise_for_status()
        estado = respuesta.json()
        situacion = (
            estado.get("status", "")
            if operacion
            else estado.get("properties", {}).get("publishDetails", {}).get("state", "")
        )
        print(f"  publicación: {situacion}")
        if situacion.lower() in ("success", "succeeded", "failed", "cancelled"):
            if situacion.lower() not in ("success", "succeeded"):
                raise SystemExit(f"La publicación del Environment terminó en '{situacion}'")
            return
        time.sleep(20)
    raise SystemExit("La publicación del Environment no terminó en 20 minutos")


if __name__ == "__main__":
    main()
