"""Comprobación de requisitos antes de desplegar o de ensayar."""

from __future__ import annotations

import shutil

from agentid.az import AzError, az
from agentid.contexto import Ctx


def _ok(cond: bool, texto: str, ayuda: str = "") -> bool:
    print(f"  {'✔' if cond else '✘'} {texto}" + ("" if cond or not ayuda else f"\n      → {ayuda}"))
    return cond


def comprobar(ctx: Ctx, graph: bool = True) -> bool:
    s = ctx.s
    ok = True
    ok &= _ok(bool(s.tenant_id and s.tenant_domain and s.admin_upn), "TENANT_ID, TENANT_DOMAIN y ADMIN_UPN en .env")
    ok &= _ok(3 <= len(s.name_suffix) <= 8 and s.name_suffix.islower(), f"NAME_SUFFIX válido ({s.name_suffix!r})",
              "3–8 caracteres en minúsculas")
    ok &= _ok(bool(shutil.which("az") or shutil.which("az.cmd")), "Azure CLI instalada", "https://aka.ms/installazurecli")
    try:
        cuenta = az("account", "show")
        ok &= _ok(cuenta.get("tenantId") == s.tenant_id, f"az conectado al tenant {cuenta.get('tenantId')}",
                  "az login --tenant <TENANT_ID>")
        if s.subscription_id:
            ok &= _ok(cuenta.get("id") == s.subscription_id, f"suscripción activa {cuenta.get('id')}",
                      f"az account set --subscription {s.subscription_id}")
    except AzError as e:
        ok &= _ok(False, "az account show", str(e))
    ok &= _ok((s.case_data_dir / "devoluciones_online.csv").exists(), f"datos del caso en {s.case_data_dir}")
    ok &= _ok(s.buzon_json.exists(), f"correos del buzón en {s.buzon_json}")
    if graph:
        try:
            me = ctx.graph("User.ReadWrite.All").get("me?$select=userPrincipalName")
            ok &= _ok(me["userPrincipalName"].lower() == s.admin_upn.lower(), f"Graph como {me['userPrincipalName']}")
        except Exception as e:  # noqa: BLE001
            ok &= _ok(False, "login en Microsoft Graph", str(e))
    print("\n  Roles que necesita Nuria: Agent ID Administrator, Conditional Access Administrator, "
          "Lifecycle Workflows Administrator,\n  Attribute Definition Administrator, Attribute Assignment Administrator, "
          "Security Operator (riesgo) y Owner del grupo de recursos.")
    return ok
