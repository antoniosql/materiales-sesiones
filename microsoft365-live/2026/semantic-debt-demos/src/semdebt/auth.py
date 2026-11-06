"""Tokens: app-only para preparar el tenant y delegado (Laura) para evaluar.

Regla de la sesión: las preguntas se lanzan como un usuario real, nunca como admin.
`user_token` se niega a devolver un token del ADMIN_UPN salvo que se pida explícitamente.
"""
from __future__ import annotations

import logging
from pathlib import Path

import msal

from .config import Settings

log = logging.getLogger(__name__)

GRAPH_APP_SCOPE = ["https://graph.microsoft.com/.default"]
PURVIEW_APP_SCOPE = ["https://purview.azure.net/.default"]

# Permisos delegados documentados para la Chat API de Copilot (beta) y la Retrieval API.
COPILOT_CHAT_SCOPES = [
    "https://graph.microsoft.com/Sites.Read.All",
    "https://graph.microsoft.com/Mail.Read",
    "https://graph.microsoft.com/People.Read.All",
    "https://graph.microsoft.com/OnlineMeetingTranscript.Read.All",
    "https://graph.microsoft.com/Chat.Read",
    "https://graph.microsoft.com/ChannelMessage.Read.All",
    "https://graph.microsoft.com/ExternalItem.Read.All",
]
RETRIEVAL_SCOPES = [
    "https://graph.microsoft.com/Files.Read.All",
    "https://graph.microsoft.com/Sites.Read.All",
]
POWER_PLATFORM_SCOPES = ["https://api.powerplatform.com/CopilotStudio.Copilots.Invoke"]


class AuthError(RuntimeError):
    pass


# --- Modo delegado (AUTH_MODE=delegated): sin registro de aplicación -----------------
# El admin inicia sesión con código de dispositivo en aplicaciones públicas de Microsoft.
GRAPH_CLI_CLIENT = "14d82eec-204b-4c2f-b7e8-296a70dab67e"   # Microsoft Graph Command Line Tools
AZURE_CLI_CLIENT = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"   # Microsoft Azure CLI
ADMIN_GRAPH_SCOPES = [f"https://graph.microsoft.com/{p}" for p in (
    "User.ReadWrite.All", "Group.ReadWrite.All", "Sites.FullControl.All", "TermStore.ReadWrite.All",
    "Files.ReadWrite.All", "LicenseAssignment.ReadWrite.All", "Organization.Read.All")]


def admin_token(settings: Settings, scopes: list[str]) -> str:
    if scopes == GRAPH_APP_SCOPE:
        client, scopes = GRAPH_CLI_CLIENT, ADMIN_GRAPH_SCOPES
    else:
        client = AZURE_CLI_CLIENT
    cache_path = settings.state_dir / f"msal_admin_{client[:8]}.bin"
    cache = msal.SerializableTokenCache()
    if cache_path.exists():
        cache.deserialize(cache_path.read_text(encoding="utf-8"))
    app = msal.PublicClientApplication(client, authority=settings.authority, token_cache=cache)
    accounts = [a for a in app.get_accounts() if a.get("username", "").lower() == settings.admin_upn.lower()] or app.get_accounts()
    result = app.acquire_token_silent(scopes, account=accounts[0]) if accounts else None
    if not result:
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise AuthError(f"No se pudo iniciar el device code: {flow}")
        print(f"\n>>> Inicia sesión como admin ({settings.admin_upn})\n{flow['message']}\n", flush=True)
        result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        raise AuthError(f"Login fallido: {result.get('error')} {result.get('error_description')}")
    if cache.has_state_changed:
        cache_path.write_text(cache.serialize(), encoding="utf-8")
    return result["access_token"]


_app_cache: dict[str, msal.ConfidentialClientApplication] = {}


def _confidential(settings: Settings) -> msal.ConfidentialClientApplication:
    if "app" in _app_cache:
        return _app_cache["app"]
    if settings.has_certificate:
        key = Path(settings.cert_pem_key_path).read_text(encoding="utf-8")
        credential = {"private_key": key, "thumbprint": settings.cert_thumbprint}
    else:
        credential = settings.client_secret
    app = msal.ConfidentialClientApplication(
        settings.client_id, authority=settings.authority, client_credential=credential)
    _app_cache["app"] = app
    return app


def app_token(settings: Settings, scopes: list[str] = GRAPH_APP_SCOPE) -> str:
    if settings.dry_run:
        return "dry-run-token"
    if settings.auth_mode == "delegated":
        return admin_token(settings, scopes)
    result = _confidential(settings).acquire_token_for_client(scopes=scopes)
    if "access_token" not in result:
        raise AuthError(f"No se pudo obtener token de aplicación para {scopes}: "
                        f"{result.get('error')} {result.get('error_description')}")
    return result["access_token"]


def _public(settings: Settings) -> tuple[msal.PublicClientApplication, msal.SerializableTokenCache, Path]:
    cache_path = settings.state_dir / "msal_user_cache.bin"
    cache = msal.SerializableTokenCache()
    if cache_path.exists():
        cache.deserialize(cache_path.read_text(encoding="utf-8"))
    app = msal.PublicClientApplication(settings.client_id, authority=settings.authority, token_cache=cache)
    return app, cache, cache_path


def user_token(settings: Settings, scopes: list[str], expected_upn: str, allow_admin: bool = False) -> str:
    """Token delegado con device code. Comprueba que la cuenta es la esperada (Laura)."""
    if settings.dry_run:
        return "dry-run-user-token"
    if not allow_admin and expected_upn.lower() == settings.admin_upn.lower():
        raise AuthError("La evaluación no se hace como admin: el admin ve más que Laura y la demo deja de ser verdad.")
    app, cache, cache_path = _public(settings)
    accounts = [a for a in app.get_accounts() if a.get("username", "").lower() == expected_upn.lower()]
    result = app.acquire_token_silent(scopes, account=accounts[0]) if accounts else None
    if not result:
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise AuthError(f"No se pudo iniciar el device code: {flow}")
        print(f"\n>>> Inicia sesión como {expected_upn}\n{flow['message']}\n", flush=True)
        result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        raise AuthError(f"Login fallido: {result.get('error')} {result.get('error_description')}")
    upn = (result.get("id_token_claims") or {}).get("preferred_username", "")
    if upn and upn.lower() != expected_upn.lower():
        raise AuthError(f"Has iniciado sesión como {upn}, pero la evaluación debe hacerse como {expected_upn}.")
    if cache.has_state_changed:
        cache_path.write_text(cache.serialize(), encoding="utf-8")
    return result["access_token"]
