"""Token del agente sin secretos: managed identity → blueprint → identidad de agente → recurso.

Es el fichero que se enseña en la demo 3. Las tres líneas que importan están marcadas
con [1], [2] y [3]. Flujo documentado en «Autonomous agent authentication and
authorization flow» (Microsoft Entra Agent ID).
"""

from __future__ import annotations

import os
import time

import requests
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import ManagedIdentityCredential

JWT_BEARER = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
INTERCAMBIO = "api://AzureADTokenExchange/.default"


class DenegadoPorEntra(ClientAuthenticationError):
    """Entra no ha emitido el token (acceso condicional, riesgo, identidad deshabilitada…)."""


class TokenDelAgente:
    """TokenCredential para los SDK de Azure. Pide tokens como la identidad de agente, nunca como la MI."""

    def __init__(self) -> None:
        self.tenant = os.environ["AZURE_TENANT_ID"]
        self.blueprint = os.environ["BLUEPRINT_APP_ID"]          # appId del blueprint
        self.agente = os.environ["AGENT_IDENTITY_CLIENT_ID"]    # client id de la identidad de agente
        self.mi = ManagedIdentityCredential(client_id=os.environ["AZURE_CLIENT_ID"])
        self._cache: dict[str, AccessToken] = {}
        # En la demo el token se renueva cada pocos minutos para que el bloqueo de CA-AG-01 se vea sin reiniciar.
        self.ttl = int(os.environ.get("TOKEN_TTL_SECONDS", "0")) or None

    def _token(self, datos: dict) -> dict:
        url = f"https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0/token"
        r = requests.post(url, data=datos, timeout=30)
        cuerpo = r.json()
        if r.status_code != 200:
            raise DenegadoPorEntra(
                f"{cuerpo.get('error')}: {cuerpo.get('error_codes')} {cuerpo.get('error_description', '').splitlines()[0]}")
        return cuerpo

    def get_token(self, *scopes: str, **kwargs) -> AccessToken:  # noqa: ARG002
        scope = scopes[0]
        guardado = self._cache.get(scope)
        if guardado and guardado.expires_on - 300 > time.time():
            return guardado
        mi = self.mi.get_token(INTERCAMBIO).token                                      # [1] token de la MI
        t1 = self._token({"client_id": self.blueprint, "scope": INTERCAMBIO,           # [2] T1: el blueprint
                          "grant_type": "client_credentials", "client_assertion_type": JWT_BEARER,
                          "client_assertion": mi, "fmi_path": self.agente})["access_token"]
        final = self._token({"client_id": self.agente, "scope": scope,                  # [3] la identidad de agente
                             "grant_type": "client_credentials", "client_assertion_type": JWT_BEARER,
                             "client_assertion": t1})
        vida = int(final.get("expires_in", 3600))
        if self.ttl:
            vida = min(vida, self.ttl + 300)  # get_token renueva cuando quedan menos de 300 s
        token = AccessToken(final["access_token"], int(time.time()) + vida)
        self._cache[scope] = token
        return token
