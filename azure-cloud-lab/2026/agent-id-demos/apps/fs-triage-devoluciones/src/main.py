"""fs-triage-devoluciones · bucle de triaje (Container Apps).

Lee los correos del contenedor buzon-devoluciones, los clasifica y deja el resultado
y el resumen diario en triage-resultados. Todo el acceso a Storage es con el token de
la identidad de agente (identity.TokenDelAgente): si Entra deja de emitirlo, el agente
se queda fuera sin tocar su código ni su contenedor.
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient

from identity import TokenDelAgente
from triage import clasificar, resumen

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("fs-triage")
logging.getLogger("azure").setLevel(logging.WARNING)

CUENTA = os.environ["STORAGE_ACCOUNT"]
BUZON = os.environ.get("BUZON_CONTAINER", "buzon-devoluciones")
RESULTADOS = os.environ.get("RESULTADOS_CONTAINER", "triage-resultados")
ESPERA = int(os.environ.get("POLL_SECONDS", "60"))


def una_pasada(servicio: BlobServiceClient) -> int:
    buzon = servicio.get_container_client(BUZON)
    salida = servicio.get_container_client(RESULTADOS)
    nuevos = 0
    for blob in buzon.list_blobs():
        if not blob.name.endswith(".json"):
            continue
        destino = salida.get_blob_client(blob.name)
        if destino.exists():
            continue
        correo = json.loads(buzon.download_blob(blob.name).readall())
        codigo, motivo = clasificar(correo.get("asunto", ""), correo.get("cuerpo", ""))
        resultado = {"correo": blob.name, "remitente": correo.get("remitente"), "asunto": correo.get("asunto"),
                     "motivo": codigo, "descripcion": motivo,
                     "procesado": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        destino.upload_blob(json.dumps(resultado, ensure_ascii=False, indent=1), overwrite=True)
        log.info("✔ %s → %s %s", blob.name, codigo, motivo)
        nuevos += 1
    if nuevos:
        todos = [json.loads(salida.download_blob(b.name).readall())
                 for b in salida.list_blobs() if b.name.endswith(".json")]
        salida.get_blob_client("resumen-diario.md").upload_blob(resumen(todos), overwrite=True)
        log.info("Resumen diario actualizado (%d correos)", len(todos))
    return nuevos


def main() -> None:
    servicio = BlobServiceClient(f"https://{CUENTA}.blob.core.windows.net", credential=TokenDelAgente())
    log.info("fs-triage-devoluciones arrancado · cuenta=%s · cada %ss", CUENTA, ESPERA)
    while True:
        try:
            n = una_pasada(servicio)
            if not n:
                log.info("Sin correos nuevos")
        except ClientAuthenticationError as error:
            log.error("🛑 Entra ha denegado el token del agente: %s", error.message if hasattr(error, "message") else error)
        except (HttpResponseError, ResourceNotFoundError) as error:
            log.error("⚠ Storage ha respondido %s %s", getattr(error, "status_code", ""), getattr(error, "error_code", ""))
        time.sleep(ESPERA)


if __name__ == "__main__":
    main()
