"""Término «Cliente activo» en el glosario del Unified Catalog de Purview.

borrador  → demo 3: en borrador, sin dueño de negocio (solo la admin) y sin recursos vinculados.
publicado → demo 4: publicado, dueña Laura (Dirección Comercial), enlazado a FS-KB-03.

API: Purview Unified Catalog (preview). Ruta y versión configurables en .env
(PURVIEW_ENDPOINT, PURVIEW_API_VERSION). El dominio de gobierno debe existir y estar publicado.
"""
from __future__ import annotations

import logging
import uuid

from . import auth
from .http import Api, ApiError, path_segment

log = logging.getLogger(__name__)


def _api(ctx) -> Api:
    return Api(lambda: auth.app_token(ctx.settings, auth.PURVIEW_APP_SCOPE), ctx.settings.purview_endpoint,
               ctx.settings.dry_run)


def _object_id(ctx, key: str) -> str:
    upn = ctx.upn(key)
    u = ctx.graph.get(f"users/{path_segment(upn)}?$select=id", ok_404=True)
    if not u:
        if ctx.settings.dry_run:
            return f"dry-{key}"
        raise RuntimeError(f"No encuentro {upn} en Entra ID")
    return u["id"]


def run(ctx, estado: str) -> dict:
    s = ctx.settings
    if not s.purview_domain_id and not s.dry_run:
        raise RuntimeError("Falta PURVIEW_DOMAIN_ID en .env (id del dominio de gobierno de Unified Catalog).")
    cfg = ctx.scenario["glossary"]
    variant = cfg["borrador" if estado == "borrador" else "publicado"]
    api, ver = _api(ctx), s.purview_api_version
    rec = ctx.state.get("glossary_term", cfg["term"])
    term_id = rec["id"] if rec else str(uuid.uuid4())
    body = {
        "id": term_id,
        "name": cfg["term"],
        "description": variant["description"],
        "domain": s.purview_domain_id or "dry-domain",
        "status": "DRAFT" if estado == "borrador" else "PUBLISHED",
        "contacts": {"owner": [{"id": _object_id(ctx, variant["owner"]),
                                "description": "Dirección Comercial" if variant["owner"] == "laura" else "Admin M365"}]},
        "isLeaf": True,
    }
    if estado == "publicado":
        kb03 = ctx.state.get("file", "kb_oficial:FS-KB-03_Diccionario_KPI_v1.0.docx")
        if kb03:
            body["resources"] = [{"name": variant["resource_name"], "url": kb03["webUrl"]}]

    path = "datagovernance/catalog/terms"
    if rec:
        try:
            result = api.put(f"{path}/{term_id}?api-version={ver}", body)
        except ApiError as e:
            if e.status != 405:
                raise
            result = api.patch(f"{path}/{term_id}?api-version={ver}", body)
    else:
        existing = None
        if not s.dry_run:
            listing = api.get(f"{path}?api-version={ver}&domainId={s.purview_domain_id}", ok_404=True) or {}
            existing = next((t for t in listing.get("value", []) if t.get("name") == cfg["term"]), None)
        if existing:
            log.info("El término ya existía en el catálogo: se reutiliza y se actualiza")
            term_id = body["id"] = existing["id"]
            ctx.state.put("glossary_term", cfg["term"], term_id, created=False)
            result = api.put(f"{path}/{term_id}?api-version={ver}", body)
        else:
            result = api.post(f"{path}?api-version={ver}", body)
            ctx.state.put("glossary_term", cfg["term"], result.get("id", term_id), created=True)
    print(f"✔ Glosario: «{cfg['term']}» en estado {body['status']} (dueño: {variant['owner']})")
    return result
