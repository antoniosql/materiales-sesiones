"""Acceso al buzón de devoluciones.

Ahora mismo, con credenciales propias en un .env. Ese es el punto de partida
de la demo 4: el agente funciona, pero su acceso al correo de FraSoHome no lo
ve, ni lo audita, ni lo puede cortar ningún administrador.

El beat 2 de la demo sustituye esto por los servidores MCP gobernados de
Work IQ, y entonces el mismo acceso pasa a estar bajo control del admin.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

GRAPH = "https://graph.microsoft.com/v1.0"
_RAIZ_DEMOS = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Mensaje:
    id: str
    asunto: str
    remitente: str
    recibido: datetime
    cuerpo: str

    def resumen_corto(self) -> str:
        return f"[{self.recibido:%d/%m %H:%M}] {self.remitente} — {self.asunto}"


class BuzonDevoluciones:
    """Cliente mínimo de Graph para un buzón compartido."""

    def __init__(self) -> None:
        self.tenant_id = _requerido("AZURE_TENANT_ID")
        self.client_id = _requerido("AZURE_CLIENT_ID")
        self.client_secret = _requerido("AZURE_CLIENT_SECRET")
        self.buzon = _requerido("BUZON_DEVOLUCIONES")
        self._token: str | None = None
        self._token_expira = datetime.now(timezone.utc)

    def _acceso(self) -> str:
        if self._token and datetime.now(timezone.utc) < self._token_expira:
            return self._token
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        datos = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }
        respuesta = httpx.post(url, data=datos, timeout=30)
        respuesta.raise_for_status()
        payload = respuesta.json()
        self._token = payload["access_token"]
        self._token_expira = datetime.now(timezone.utc) + timedelta(
            seconds=payload.get("expires_in", 3600) - 120
        )
        return self._token

    def listar(self, limite: int = 25) -> list[Mensaje]:
        url = f"{GRAPH}/users/{self.buzon}/mailFolders/inbox/messages"
        parametros = {
            "$top": str(limite),
            "$select": "id,subject,from,receivedDateTime,bodyPreview",
            "$orderby": "receivedDateTime desc",
        }
        respuesta = httpx.get(
            url,
            params=parametros,
            headers={"Authorization": f"Bearer {self._acceso()}"},
            timeout=30,
        )
        respuesta.raise_for_status()
        return [_a_mensaje(m) for m in respuesta.json().get("value", [])]

    def leer(self, mensaje_id: str) -> Mensaje:
        url = f"{GRAPH}/users/{self.buzon}/messages/{mensaje_id}"
        respuesta = httpx.get(
            url,
            params={"$select": "id,subject,from,receivedDateTime,body"},
            headers={"Authorization": f"Bearer {self._acceso()}"},
            timeout=30,
        )
        respuesta.raise_for_status()
        return _a_mensaje(respuesta.json())


class BuzonLocal:
    """El mismo buzón, servido desde datos/buzon/correos.json.

    Para ensayar y para la sala sin depender de Exchange: mismas 18 reclamaciones
    que se sembrarían en el buzón real, repartidas en los últimos días para que
    la detección de patrones encuentre el caso anómalo.
    """

    def __init__(self, ruta: Path | None = None) -> None:
        ruta = ruta or Path(
            os.environ.get("BUZON_FICHERO") or _RAIZ_DEMOS / "datos" / "buzon" / "correos.json"
        )
        brutos = json.loads(ruta.read_text(encoding="utf-8"))
        ahora = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        self._mensajes = [
            Mensaje(
                id=f"local-{i:03d}",
                asunto=b.get("asunto", "(sin asunto)"),
                remitente=b.get("remitente", "desconocido"),
                # El más reciente primero, uno cada ~9 horas: 18 correos en una semana.
                recibido=ahora - timedelta(hours=9 * i),
                cuerpo=b.get("cuerpo", "").strip(),
            )
            for i, b in enumerate(brutos, start=1)
        ]

    def listar(self, limite: int = 25) -> list[Mensaje]:
        return self._mensajes[:limite]

    def leer(self, mensaje_id: str) -> Mensaje:
        for m in self._mensajes:
            if m.id == mensaje_id:
                return m
        raise KeyError(f"No existe el mensaje {mensaje_id}")


def crear_buzon() -> BuzonDevoluciones | BuzonLocal:
    """BUZON_ORIGEN=graph usa Exchange con las credenciales del .env; cualquier otro valor, el fichero local."""
    if os.environ.get("BUZON_ORIGEN", "local").lower() == "graph":
        return BuzonDevoluciones()
    return BuzonLocal()


def _a_mensaje(bruto: dict) -> Mensaje:
    direccion = (
        bruto.get("from", {}).get("emailAddress", {}).get("address")
        or bruto.get("from", {}).get("emailAddress", {}).get("name")
        or "desconocido"
    )
    cuerpo = bruto.get("bodyPreview") or bruto.get("body", {}).get("content", "")
    return Mensaje(
        id=bruto["id"],
        asunto=bruto.get("subject", "(sin asunto)"),
        remitente=direccion,
        recibido=datetime.fromisoformat(
            bruto["receivedDateTime"].replace("Z", "+00:00")
        ),
        cuerpo=cuerpo.strip(),
    )


def _requerido(nombre: str) -> str:
    valor = os.environ.get(nombre)
    if not valor:
        raise RuntimeError(
            f"Falta la variable de entorno {nombre}. Copia .env.example a .env y rellénalo."
        )
    return valor
