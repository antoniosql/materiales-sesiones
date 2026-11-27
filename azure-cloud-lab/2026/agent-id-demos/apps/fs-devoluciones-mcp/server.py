"""fs-devoluciones-mcp — servidor MCP de devoluciones online de FraSoHome (demo 2).

El servidor no tiene identidad propia ni secretos: usa el token que le pasa
Foundry Agent Service, emitido para la identidad del agente que lo llama
(conexión con autenticación de identidad de agente, audience
https://storage.azure.com). Con ese token lee el CSV de devoluciones del
Storage Account. Si la identidad del agente no tiene rol sobre el contenedor,
Storage responde 403 y la herramienta lo devuelve tal cual: eso es lo que se
ve en la traza de la demo.
"""

from __future__ import annotations

import base64
import csv
import io
import json
import logging
import os
import time
from collections import Counter
from datetime import datetime

from azure.core.credentials import AccessToken
from azure.core.exceptions import AzureError, HttpResponseError
from azure.storage.blob import BlobServiceClient
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.transport_security import TransportSecuritySettings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("fs-devoluciones-mcp")

STORAGE_ACCOUNT = os.environ["STORAGE_ACCOUNT"]
CONTAINER = os.environ.get("DEVOLUCIONES_CONTAINER", "devoluciones")
DEVOLUCIONES_BLOB = os.environ.get("DEVOLUCIONES_BLOB", "devoluciones_online.csv")
PRODUCTOS_BLOB = os.environ.get("PRODUCTOS_BLOB", "productos.csv")
AUDIENCIA_ESPERADA = "https://storage.azure.com"

mcp = FastMCP(
    "fs-devoluciones",
    instructions="Devoluciones online de FraSoHome: recuentos por categoría y motivo.",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8000")),
    stateless_http=True,
    json_response=True,
    # Detrás del ingress de Container Apps el Host es el FQDN de la app.
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


class _TokenRecibido:
    """TokenCredential mínimo: entrega a Storage el token que nos ha pasado el agente."""

    def __init__(self, token: str) -> None:
        self._token = token
        self._exp = _claims(token).get("exp", int(time.time()) + 300)

    def get_token(self, *scopes, **kwargs) -> AccessToken:  # noqa: ARG002
        return AccessToken(self._token, self._exp)


def _claims(token: str) -> dict:
    """Lee los claims sin validar la firma: quien valida es Storage. Solo sirve para el log."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception:  # token opaco o mal formado
        return {}


def _token_del_agente(ctx: Context) -> str:
    request = getattr(ctx.request_context, "request", None)
    cabecera = request.headers.get("authorization", "") if request is not None else ""
    if not cabecera.lower().startswith("bearer "):
        raise PermissionError("La llamada no trae token: revisa la conexión del proyecto (auth de identidad de agente).")
    token = cabecera.split(" ", 1)[1]
    c = _claims(token)
    aud = c.get("aud", "")
    log.info("Token recibido · aud=%s · appid=%s · oid=%s · idtyp=%s", aud, c.get("appid") or c.get("azp"),
             c.get("oid"), c.get("idtyp"))
    if aud and aud.rstrip("/") != AUDIENCIA_ESPERADA:
        raise PermissionError(
            f"El token es para '{aud}', no para '{AUDIENCIA_ESPERADA}'. "
            "El audience de la conexión debe ser el del recurso final, no la URL del servidor MCP."
        )
    return token


def _leer_csv(servicio: BlobServiceClient, blob: str) -> list[dict]:
    datos = servicio.get_blob_client(CONTAINER, blob).download_blob().readall()
    return list(csv.DictReader(io.StringIO(datos.decode("utf-8-sig"))))


def _fecha(texto: str) -> datetime | None:
    texto = (texto or "").strip()
    for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue
    return None


def _importe(texto: str) -> float:
    texto = (texto or "").replace("€", "").replace(" ", "").strip()
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    else:
        texto = texto.replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return 0.0


@mcp.tool()
def devoluciones_online(ctx: Context, categoria: str = "", desde: str = "", hasta: str = "") -> str:
    """Cuenta las devoluciones online de FraSoHome por motivo.

    Args:
        categoria: categoría o subcategoría de producto (p. ej. "Iluminación", "Sofás"). Vacío = todas.
        desde: fecha inicial AAAA-MM-DD (opcional). Los datos van de 2024 a 2025.
        hasta: fecha final AAAA-MM-DD (opcional).
    """
    token = _token_del_agente(ctx)
    servicio = BlobServiceClient(f"https://{STORAGE_ACCOUNT}.blob.core.windows.net",
                                 credential=_TokenRecibido(token))
    try:
        devoluciones = _leer_csv(servicio, DEVOLUCIONES_BLOB)
        productos = {p["product_id"]: p for p in _leer_csv(servicio, PRODUCTOS_BLOB)}
    except HttpResponseError as error:
        codigo = getattr(error, "error_code", None) or ""
        log.warning("Storage ha rechazado el acceso: %s %s", error.status_code, codigo)
        return (f"ERROR {error.status_code} {codigo}: Storage ha rechazado el token de la identidad del agente. "
                "Comprueba que esa identidad (no la del proyecto) tiene un rol de datos sobre el contenedor.")
    except AzureError as error:
        log.error("No se pudo leer Storage: %s", error)
        return f"ERROR: no se pudo leer Storage ({type(error).__name__})."

    return resumir(devoluciones, productos, categoria, desde, hasta)


def resumir(devoluciones: list[dict], productos: dict[str, dict], categoria: str = "", desde: str = "",
            hasta: str = "") -> str:
    """Recuento por motivo. Función pura para poder probarla sin Storage."""
    filtro = categoria.strip().lower()
    d0, d1 = _fecha(desde), _fecha(hasta)
    motivos: Counter[str] = Counter()
    total, reembolsado = 0, 0.0
    for fila in devoluciones:
        producto = productos.get(fila.get("product_id", ""), {})
        cats = f"{producto.get('categoria', '')} {producto.get('subcategoria', '')}".lower()
        if filtro and filtro not in cats:
            continue
        fecha = _fecha(fila.get("fecha_devolucion", ""))
        if (d0 and (not fecha or fecha < d0)) or (d1 and (not fecha or fecha > d1)):
            continue
        total += 1
        motivos[(fila.get("motivo_devolucion") or "Sin motivo informado").strip()] += 1
        reembolsado += _importe(fila.get("importe_reembolsado", ""))

    detalle = "\n".join(f"- {m}: {n}" for m, n in motivos.most_common())
    return (f"Devoluciones online{' de ' + categoria if categoria else ''}: {total}\n"
            f"Importe reembolsado: {reembolsado:,.2f} EUR\nPor motivo:\n{detalle or '- (ninguna)'}")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
