"""Cliente mínimo de Microsoft Graph con reintentos y paginación."""

from __future__ import annotations

import time
from typing import Any

import requests

from agentid.auth import Credencial

BASE = "https://graph.microsoft.com"


class GraphError(RuntimeError):
    def __init__(self, status: int, codigo: str, mensaje: str, url: str) -> None:
        super().__init__(f"Graph {status} {codigo}: {mensaje} ({url})")
        self.status, self.codigo, self.mensaje = status, codigo, mensaje

    @property
    def sin_licencia(self) -> bool:
        m = self.mensaje.lower()
        return self.status == 403 and ("not licensed" in m or "insufficient license" in m)


AYUDA_LICENCIA = ("    El tenant no tiene la licencia: acceso condicional para agentes → Entra ID P1 + Agent 365 (o M365 E7);\n"
                  "    Lifecycle Workflows de sponsors → Agent 365 o Entra ID Governance; riesgo de agentes → ID Protection\n"
                  "    (Entra ID P2) + Agent 365. Ver DESPLIEGUE.md §1.")


class Graph:
    def __init__(self, credencial: Credencial, scopes: list[str]) -> None:
        self.credencial = credencial
        self.scopes = scopes

    def _url(self, ruta: str, version: str) -> str:
        return ruta if ruta.startswith("http") else f"{BASE}/{version}/{ruta.lstrip('/')}"

    def request(self, metodo: str, ruta: str, *, json: Any = None, version: str = "v1.0",
                cabeceras: dict | None = None, reintentos_404: int = 0) -> Any:
        url = self._url(ruta, version)
        intento = 0
        while True:
            h = {"Authorization": f"Bearer {self.credencial.token(self.scopes)}", "OData-Version": "4.0"}
            if json is not None:
                h["Content-Type"] = "application/json"
            h.update(cabeceras or {})
            r = requests.request(metodo, url, json=json, headers=h, timeout=60)
            if r.status_code in (429, 502, 503, 504) and intento < 6:
                time.sleep(int(r.headers.get("Retry-After", 2 ** intento)))
                intento += 1
                continue
            # Réplica de Entra: un objeto recién creado puede tardar unos segundos en verse
            if r.status_code == 404 and intento < reintentos_404:
                time.sleep(5)
                intento += 1
                continue
            if r.status_code >= 400:
                try:
                    err = r.json().get("error", {})
                except ValueError:
                    err = {}
                raise GraphError(r.status_code, err.get("code", ""), err.get("message", r.text[:300]), url)
            if r.status_code == 204 or not r.content:
                return None
            return r.json()

    def get(self, ruta: str, **kw) -> Any:
        return self.request("GET", ruta, **kw)

    def post(self, ruta: str, cuerpo: Any = None, **kw) -> Any:
        return self.request("POST", ruta, json=cuerpo if cuerpo is not None else {}, **kw)

    def patch(self, ruta: str, cuerpo: Any, **kw) -> Any:
        return self.request("PATCH", ruta, json=cuerpo, **kw)

    def put(self, ruta: str, cuerpo: Any, **kw) -> Any:
        return self.request("PUT", ruta, json=cuerpo, **kw)

    def delete(self, ruta: str, **kw) -> Any:
        return self.request("DELETE", ruta, **kw)

    def todos(self, ruta: str, **kw) -> list[dict]:
        pagina = self.get(ruta, **kw)
        valores = list(pagina.get("value", []))
        while pagina.get("@odata.nextLink"):
            pagina = self.get(pagina["@odata.nextLink"])
            valores += pagina.get("value", [])
        return valores

    def existe(self, ruta: str, **kw) -> dict | None:
        try:
            return self.get(ruta, **kw)
        except GraphError as e:
            if e.status == 404:
                return None
            raise


def odata_id(tipo: str, id_: str) -> str:
    return f"{BASE}/v1.0/{tipo}/{id_}"
