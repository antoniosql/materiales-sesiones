"""Usuarios (Laura, Paco), licencias y grupo FS-Finanzas."""
from __future__ import annotations

import logging
import secrets
import string

from .http import ApiError, path_segment, q

log = logging.getLogger(__name__)


def _password() -> str:
    alphabet = string.ascii_letters + string.digits
    core = "".join(secrets.choice(alphabet) for _ in range(14))
    return f"Fs!{core}9a"


def user_by_upn(ctx, upn: str) -> dict | None:
    return ctx.graph.get(f"users/{path_segment(upn)}?$select=id,userPrincipalName,displayName", ok_404=True)


def ensure_user(ctx, key: str) -> dict:
    s, p = ctx.settings, ctx.scenario["personas"][key]
    upn = ctx.upn(key)
    existing = user_by_upn(ctx, upn)
    if existing:
        log.info("Usuario %s ya existe: se reutiliza (la limpieza no lo borrará)", upn)
        ctx.state.put("user", key, existing["id"], created=False, upn=upn)
        return existing
    password = s.env(p["password_env"]) or _password()
    body = {
        "accountEnabled": True,
        "displayName": s.env(p["name_env"]) or key,
        "mailNickname": upn.split("@")[0].replace(".", ""),
        "userPrincipalName": upn,
        "usageLocation": s.usage_location,
        "jobTitle": p.get("job_title"),
        "department": p.get("department"),
        "passwordProfile": {"forceChangePasswordNextSignIn": False, "password": password},
    }
    user = ctx.graph.post("users", body)
    ctx.state.put("user", key, user["id"], created=True, upn=upn)
    if not s.env(p["password_env"]):
        print(f"  Contraseña inicial de {upn}: {password}  (no se guarda en ningún sitio)")
    return user


def ensure_licenses(ctx, key: str) -> None:
    s, p = ctx.settings, ctx.scenario["personas"][key]
    wanted = [x.strip() for x in (s.env(p["licenses_env"]) or "").split(",") if x.strip()]
    if not wanted:
        return
    user = ctx.state.get("user", key)
    if not user:
        raise RuntimeError(f"Crea primero el usuario {key}")
    if s.dry_run:
        log.info("[dry-run] asignar licencias %s a %s", wanted, key)
        return
    skus = {x["skuPartNumber"]: x["skuId"] for x in ctx.graph.get_all("subscribedSkus")}
    current = {x["skuId"] for x in ctx.graph.get_all(f"users/{user['id']}/licenseDetails")}
    missing = [w for w in wanted if w not in skus]
    if missing:
        raise RuntimeError(f"El tenant no tiene estas licencias: {missing}. Disponibles: {sorted(skus)}")
    to_add = [skus[w] for w in wanted if skus[w] not in current]
    if to_add:
        ctx.graph.post(f"users/{user['id']}/assignLicense",
                       {"addLicenses": [{"skuId": x} for x in to_add], "removeLicenses": []})
    added_before = set(user.get("licenses_added", []))
    ctx.state.put("user", key, user["id"], created=False, licenses_added=sorted(added_before | set(to_add)))
    log.info("Licencias de %s: %s (añadidas ahora: %d)", key, wanted, len(to_add))


def group_by_alias(ctx, alias: str) -> dict | None:
    if ctx.settings.dry_run:
        return None
    hits = ctx.graph.get(f"groups?$filter=mailNickname eq '{q(alias)}'&$select=id,displayName,mail,mailNickname") or {}
    values = hits.get("value") or []
    return values[0] if values else None


def ensure_m365_group(ctx, key: str, alias: str, display_name: str, description: str,
                      member_keys: list[str]) -> dict:
    existing = group_by_alias(ctx, alias)
    if existing:
        log.info("Grupo %s ya existe: se reutiliza", alias)
        ctx.state.put("group", key, existing["id"], created=False, alias=alias, mail=existing.get("mail"))
        return existing
    admin = ctx.graph.get(f"users/{path_segment(ctx.settings.admin_upn)}?$select=id", ok_404=True) or {"id": "dry-admin"}
    members = []
    for m in member_keys:
        u = ctx.state.get("user", m)
        if u:
            members.append(f"https://graph.microsoft.com/v1.0/users/{u['id']}")
    body = {
        "displayName": display_name,
        "description": description,
        "mailNickname": alias,
        "mailEnabled": True,
        "securityEnabled": False,
        "groupTypes": ["Unified"],
        "visibility": "Private",
        "owners@odata.bind": [f"https://graph.microsoft.com/v1.0/users/{admin['id']}"],
    }
    if members:
        body["members@odata.bind"] = members
    group = ctx.graph.post("groups", body)
    ctx.state.put("group", key, group["id"], created=True, alias=alias,
                  mail=group.get("mail") or f"{alias}@{ctx.settings.tenant_domain}")
    return group


def run(ctx) -> None:
    for key in ctx.scenario["personas"]:
        ensure_user(ctx, key)
        try:
            ensure_licenses(ctx, key)
        except (ApiError, RuntimeError) as e:
            log.error("Licencias de %s: %s", key, e)
            ctx.todo(f"Asignar a mano las licencias de {ctx.upn(key)} ({e})")
    g = ctx.scenario["groups"]["finanzas"]
    alias = ctx.settings.env(g["alias_env"]) or ctx.settings.finanzas_group_alias
    ensure_m365_group(ctx, "finanzas", alias, g["display_name"], g["description"], g["members"])
    print("✔ Identidades listas: Laura, Paco y el grupo de Finanzas")
