"""Tokens delegados de Microsoft Graph para Nuria (código de dispositivo o navegador).

Cada comando pide solo los permisos que necesita. MSAL guarda la caché en state/, así que
los consentimientos se piden una vez.
"""

from __future__ import annotations

import msal

from agentid.config import Settings

GRAPH = "https://graph.microsoft.com/"

# Todo lo que usan los comandos. Se pide de una vez en el primer login para no repetir el código de
# dispositivo; si el tenant rechaza alguno (invalid_scope), se reintenta solo con lo que pide el comando.
TODOS = (
    "User.ReadWrite.All", "Group.ReadWrite.All", "Directory.Read.All", "Application.Read.All",
    "AgentIdentityBlueprint.Create", "AgentIdentityBlueprint.ReadWrite.All",
    "AgentIdentityBlueprint.AddRemoveCreds.All", "AgentIdentityBlueprintPrincipal.Create",
    "AgentIdentity.Create.All", "AgentIdentity.ReadWrite.All",
    "CustomSecAttributeDefinition.ReadWrite.All", "CustomSecAttributeAssignment.ReadWrite.All",
    "Policy.Read.All", "Policy.ReadWrite.ConditionalAccess", "LifecycleWorkflows.ReadWrite.All",
    "IdentityRiskyAgent.ReadWrite.All", "AuditLog.Read.All",
)


class Credencial:
    def __init__(self, s: Settings) -> None:
        self.s = s
        self._ruta = s.state_dir / "msal_cache.bin"
        s.state_dir.mkdir(parents=True, exist_ok=True)
        self._cache = msal.SerializableTokenCache()
        if self._ruta.exists():
            self._cache.deserialize(self._ruta.read_text(encoding="utf-8"))
        self._app: msal.PublicClientApplication | None = None

    @property
    def app(self) -> msal.PublicClientApplication:
        # Perezosa: los comandos que no tocan Graph funcionan aunque falte TENANT_ID.
        if self._app is None:
            if not self.s.tenant_id:
                raise RuntimeError("Falta TENANT_ID en .env.")
            self._app = msal.PublicClientApplication(
                self.s.graph_client_id, authority=f"https://login.microsoftonline.com/{self.s.tenant_id}",
                token_cache=self._cache)
        return self._app

    def _persistir(self) -> None:
        if self._cache.has_state_changed:
            self._ruta.write_text(self._cache.serialize(), encoding="utf-8")

    def token(self, scopes: list[str]) -> str:
        scopes = [sc if sc.startswith("http") else GRAPH + sc for sc in scopes]
        cuentas = self.app.get_accounts(username=self.s.admin_upn) or self.app.get_accounts()
        resultado = self.app.acquire_token_silent(scopes, account=cuentas[0]) if cuentas else None
        if not resultado:
            completos = list(dict.fromkeys(scopes + [GRAPH + t for t in TODOS]))
            resultado = self._login(completos)
            if "access_token" not in resultado and "invalid_scope" in str(resultado.get("error")):
                resultado = self._login(scopes)
        self._persistir()
        if "access_token" not in resultado:
            raise RuntimeError(f"Login fallido: {resultado.get('error')}: {resultado.get('error_description')}")
        return resultado["access_token"]

    def _login(self, scopes: list[str]) -> dict:
        if self.s.graph_login == "interactive":
            return self.app.acquire_token_interactive(scopes, login_hint=self.s.admin_upn)
        flujo = self.app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flujo:
            return {"error": flujo.get("error", "device_flow"), "error_description": flujo.get("error_description")}
        print(f"\n🔑 {flujo['message']}\n   (inicia sesión como {self.s.admin_upn})\n")
        return self.app.acquire_token_by_device_flow(flujo)
