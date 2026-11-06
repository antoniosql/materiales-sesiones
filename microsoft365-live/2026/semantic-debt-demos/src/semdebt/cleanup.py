"""Limpieza: borra solo lo que estos scripts crearon (state/deployed.json, created=True).

Orden: agente → término del glosario → dominio de gobierno → term store → grupos (y sus sitios)
→ licencias añadidas → usuarios → devolver al admin la licencia de Copilot que se pasó a Laura.
Lo que queda para PowerShell: etiquetas de Purview (Remove-Labels.ps1) y la purga de los sitios
de la papelera de SharePoint (Remove-DeletedSites.ps1).
"""
from __future__ import annotations

import logging
import shutil

from . import agent as agent_mod
from . import auth
from .config import ROOT
from .http import Api, ApiError

log = logging.getLogger(__name__)


def _try(label: str, fn) -> bool:
    try:
        fn()
        print(f"  ✔ {label}")
        return True
    except ApiError as e:
        if e.status == 404:
            print(f"  · {label} (ya no existía)")
            return True
        print(f"  ✘ {label}: {e}")
        return False
    except Exception as e:  # noqa: BLE001
        print(f"  ✘ {label}: {e}")
        return False


def _purview(ctx) -> Api:
    return Api(lambda: auth.app_token(ctx.settings, auth.PURVIEW_APP_SCOPE), ctx.settings.purview_endpoint,
               ctx.settings.dry_run)


def _delete_domain(ctx, rid: str) -> None:
    """Un dominio publicado no se puede borrar: se pasa a borrador y después se borra."""
    api, v = _purview(ctx), ctx.settings.purview_api_version
    path = f"datagovernance/catalog/businessdomains/{rid}?api-version={v}"
    dom = api.get(path)
    if str(dom.get("status", "")).lower() == "published":
        api.put(path, {**dom, "status": "Draft"})
    api.delete(path)


def _restore_admin_copilot(ctx, g) -> None:
    """Si el despliegue pasó la licencia de Copilot del admin a Laura, se le devuelve."""
    note = ctx.state.get_note("restaurar_copilot_admin")
    if not note:
        return
    laura = ctx.state.get("user", "laura")
    if laura and note["skuId"] in (laura.get("licenses_added") or []):
        print("  · la licencia de Copilot sigue en Laura: no se devuelve al admin")
        return
    if _try(f"devolver Copilot a {note['upn']}", lambda: g.post(
            f"users/{note['upn']}/assignLicense", {"addLicenses": [{"skuId": note["skuId"]}], "removeLicenses": []})):
        ctx.state.data["notes"].pop("restaurar_copilot_admin", None)
        ctx.state.save()


def plan(ctx, keep_identities: bool) -> list[dict]:
    order = ["agent", "glossary_term", "governance_domain", "term", "termset", "termgroup", "group", "user"]
    res = [r for r in ctx.state.data["resources"] if r["type"] in order]
    res = [r for r in res if r.get("created") or (r["type"] == "user" and r.get("licenses_added"))]
    if keep_identities:
        res = [r for r in res if r["type"] != "user" and not (r["type"] == "group" and r["key"] == "finanzas")]
    return sorted(res, key=lambda r: order.index(r["type"]))


def run(ctx, yes: bool, purge: bool, keep_identities: bool, keep_local: bool) -> None:
    todo = plan(ctx, keep_identities)
    if not todo:
        print("No hay nada creado por estos scripts que limpiar.")
    else:
        print("Se va a borrar (solo lo creado por estos scripts):")
        for r in todo:
            what = "quitar licencias añadidas" if r["type"] == "user" and not r.get("created") else "borrar"
            print(f"  - {r['type']:<13} {r['key']:<40} {what}")
        if not yes and input("¿Continuar? [s/N] ").strip().lower() not in ("s", "si", "sí", "y", "yes"):
            print("Cancelado.")
            return

    g = ctx.graph
    sites_to_purge = ctx.state.get_note("sites_to_purge", []) or []
    if isinstance(sites_to_purge, str):
        sites_to_purge = [sites_to_purge]

    # Ficheros subidos a sitios que NO creamos nosotros: se borran uno a uno (el sitio se queda).
    for f in list(ctx.state.of_type("file")):
        site_key = f["key"].split(":", 1)[0]
        site = ctx.state.get("site", site_key)
        group = ctx.state.get("group", f"site:{site_key}")
        if site and group and not group.get("created"):
            if _try(f"fichero {f['key']}", lambda: g.delete(f"drives/{site['drive_id']}/items/{f['id']}")):
                ctx.state.remove("file", f["key"])

    for r in todo:
        t, rid, key = r["type"], r["id"], r["key"]
        ok = True
        if t == "agent":
            ok = _try(f"agente {key}", lambda: agent_mod.delete(ctx, r))
        elif t == "glossary_term":
            api = _purview(ctx)
            ok = _try(f"término «{key}»", lambda: api.delete(
                f"datagovernance/catalog/terms/{rid}?api-version={ctx.settings.purview_api_version}"))
        elif t == "governance_domain":
            ok = _try(f"dominio de gobierno «{key}»", lambda: _delete_domain(ctx, rid))
        elif t == "term":
            ok = _try(f"término {key}", lambda: g.delete(f"sites/{r['site_id']}/termStore/sets/{r['set_id']}/terms/{rid}"))
        elif t == "termset":
            ok = _try(f"conjunto {key}", lambda: g.delete(f"sites/{r['site_id']}/termStore/sets/{rid}"))
        elif t == "termgroup":
            ok = _try(f"grupo de términos {key}", lambda: g.delete(f"sites/{r['site_id']}/termStore/groups/{rid}"))
        elif t == "group":
            site = ctx.state.get("site", key.split(":", 1)[1]) if key.startswith("site:") else None
            ok = _try(f"grupo {r.get('alias', key)}", lambda: g.delete(f"groups/{rid}"))
            if ok and site:
                sites_to_purge.append(site["webUrl"])
            if ok and purge:
                _try(f"purgar grupo {r.get('alias', key)}", lambda: g.delete(f"directory/deletedItems/{rid}"))
        elif t == "user":
            if r.get("created"):
                ok = _try(f"usuario {r.get('upn', key)}", lambda: g.delete(f"users/{rid}"))
                if ok and purge:
                    _try(f"purgar usuario {r.get('upn', key)}", lambda: g.delete(f"directory/deletedItems/{rid}"))
            else:
                lic = r.get("licenses_added", [])
                ok = _try(f"licencias añadidas a {r.get('upn', key)}", lambda: g.post(
                    f"users/{rid}/assignLicense", {"addLicenses": [], "removeLicenses": lic}))
                if ok:
                    r["licenses_added"] = []
                    ctx.state.save()
                    continue
        if ok:
            ctx.state.remove(t, key)

    _restore_admin_copilot(ctx, g)

    # lo que dependía de lo borrado
    gone = {r["key"] for r in ctx.state.of_type("site") if not ctx.state.get("group", f"site:{r['key']}")}
    for r in list(ctx.state.of_type("file")) + list(ctx.state.of_type("column")):
        if r["key"].split(":", 1)[0] in gone:
            ctx.state.remove(r["type"], r["key"])
    for key in gone:
        ctx.state.remove("site", key)
    if not ctx.state.of_type("termgroup"):
        for r in list(ctx.state.of_type("termstore")):
            ctx.state.remove("termstore", r["key"])
    ctx.state.note("sites_to_purge", sorted(set(sites_to_purge)))

    if not keep_local:
        # documentos/ está versionado en el repo: no se borra. Solo salidas regenerables y cachés.
        gen = ctx.settings.output_dir / "docs"
        if gen.exists() and gen != ROOT / "documentos":
            shutil.rmtree(gen)
            print(f"  ✔ borrado {gen}")
        for f in ("dominio_plan.json", "msal_user_cache.bin"):
            p = ctx.settings.state_dir / f
            if p.exists():
                p.unlink()

    print("\nQueda por PowerShell:")
    print("  pwsh scripts/powershell/Remove-Labels.ps1        # etiquetas y directiva de Purview creadas")
    if sites_to_purge:
        print("  pwsh scripts/powershell/Remove-DeletedSites.ps1  # purga de la papelera de SharePoint:")
        for u in sorted(set(sites_to_purge)):
            print(f"      {u}")
