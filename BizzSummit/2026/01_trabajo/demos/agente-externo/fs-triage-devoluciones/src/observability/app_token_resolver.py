# observability/app_token_resolver.py
# A365 Observability — best-effort instrumentation (verify against official sample)
"""App-only token for A365 observability export over the S2S route.

A365 auth mode: obo — telemetry uses an app-only token on the S2S route.

The skill's reference resolver takes the blueprint credential from the hosting
connection manager. This agent is a CLI job with no CloudAdapter, so the same
credential is read from the CONNECTIONS__SERVICE_CONNECTION__SETTINGS__* values
that `a365 setup all` wrote to .env:

  Step 1: the blueprint (client secret) gets an FMI assertion for the agent
          identity: client_credentials + fmi_path=<agent identity id>.
  Step 2: the agent identity exchanges that assertion (client_credentials) for an
          app-only Observability API token. The S2S route rejects delegated tokens.
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import threading
import time

import httpx
import msal

FMI_SCOPE = "api://AzureADTokenExchange/.default"
OBSERVABILITY_SCOPE = "api://9b975845-388f-4429-889e-eab1ef63949c/.default"
OBSERVABILITY_AUDIENCES = {"api://9b975845-388f-4429-889e-eab1ef63949c", "9b975845-388f-4429-889e-eab1ef63949c"}
SERVE_SKEW_SECONDS = 60      # resolve() stops serving a token this close to expiry
REFRESH_SKEW_SECONDS = 300   # prefetch() replaces a token this close to expiry


class AppTokenResolver:
    """Caches app-only observability tokens per (tenant, agent identity)."""

    def __init__(self) -> None:
        self._tokens: dict[tuple[str, str], tuple[str, float]] = {}
        self._lock = threading.Lock()

    def resolve(self, agent_id: str, tenant_id: str) -> str | None:
        """Sync a365_token_resolver: returns a cached, unexpired token or None."""
        return self._cached(agent_id, tenant_id, SERVE_SKEW_SECONDS)

    def _cached(self, agent_id: str, tenant_id: str, skew_seconds: int) -> str | None:
        if not agent_id or not tenant_id:
            return None
        with self._lock:
            cached = self._tokens.get((tenant_id.lower(), agent_id.lower()))
        if cached and time.time() < cached[1] - skew_seconds:
            return cached[0]
        return None

    async def prefetch(self, tenant_id: str, agent_id: str) -> None:
        """Acquires the token for the agent identity before its spans are exported."""
        if not tenant_id or not agent_id or self._cached(agent_id, tenant_id, REFRESH_SKEW_SECONDS):
            return
        blueprint_id = os.environ.get("CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID", "")
        blueprint_secret = os.environ.get("CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET", "")
        if not blueprint_id or not blueprint_secret:
            raise RuntimeError("Blueprint credential missing from .env; run 'a365 setup all'.")

        assertion = await _fmi_assertion(tenant_id, blueprint_id, blueprint_secret, agent_id)
        result = await asyncio.to_thread(_acquire, tenant_id, agent_id, assertion)
        token = result.get("access_token")
        if not token:
            raise RuntimeError(f"Observability token request failed: {result.get('error_description') or result.get('error')}")

        claims = _claims(token)
        if "scp" in claims:
            raise RuntimeError("Observability token is delegated (scp claim); the S2S route rejects it.")
        client = str(claims.get("azp") or claims.get("appid") or "").lower()
        if client != agent_id.lower() or str(claims.get("tid", "")).lower() != tenant_id.lower():
            raise RuntimeError("Observability token client or tenant does not match the exporting agent.")
        if str(claims.get("aud", "")) not in OBSERVABILITY_AUDIENCES:
            raise RuntimeError("Observability token audience does not match the Observability API.")

        expires_at = float(claims.get("exp") or time.time() + float(result.get("expires_in", 0)))
        with self._lock:
            self._tokens[(tenant_id.lower(), agent_id.lower())] = (token, expires_at)


async def _fmi_assertion(tenant_id: str, blueprint_id: str, blueprint_secret: str, agent_id: str) -> str:
    # MSAL Python does not serialize fmi_path, so this hop is a direct POST.
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
            data={
                "grant_type": "client_credentials",
                "client_id": blueprint_id,
                "client_secret": blueprint_secret,
                "scope": FMI_SCOPE,
                "fmi_path": agent_id,
            },
        )
    result = resp.json()
    if "access_token" not in result:
        raise RuntimeError(f"FMI assertion failed: {result.get('error_description') or result.get('error')}")
    return result["access_token"]


def _acquire(tenant_id: str, agent_id: str, assertion: str) -> dict:
    app = msal.ConfidentialClientApplication(
        agent_id,
        client_credential={"client_assertion": assertion},
        authority=f"https://login.microsoftonline.com/{tenant_id}",
    )
    return app.acquire_token_for_client(scopes=[OBSERVABILITY_SCOPE])


def _claims(token: str) -> dict:
    payload = token.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
