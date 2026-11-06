"""Sitios de SharePoint (grupos de Microsoft 365), carpetas, subidas, columnas y metadatos.

fase "antes":   FraSoHome-Comercial, sin columnas, con carpetas como única taxonomía.
fase "despues": FraSoHome-KB-Oficial, con columnas Estado / Dominio / Propietario / Vigente desde.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path

from .http import ApiError, path_segment
from .identities import ensure_m365_group
from .state import read_json, write_json

log = logging.getLogger(__name__)
SMALL_UPLOAD = 4 * 1024 * 1024


# ------------------------------------------------------------------ sitio
def wait_for_site(ctx, group_id: str, timeout_s: int = 900) -> dict:
    if ctx.settings.dry_run:
        return {"id": f"dry-site-{group_id}", "webUrl": f"https://{ctx.settings.sp_host}/sites/dry-{group_id}"}
    start = time.time()
    while time.time() - start < timeout_s:
        try:
            site = ctx.graph.get(f"groups/{group_id}/sites/root?$select=id,webUrl,displayName", ok_404=True)
            if site and site.get("id"):
                return site
        except ApiError as e:
            if e.status not in (400, 403, 404):
                raise
        log.info("Esperando a que SharePoint aprovisione el sitio del grupo %s…", group_id)
        time.sleep(20)
    raise TimeoutError("El sitio no se ha aprovisionado en 15 min. Vuelve a lanzar el comando más tarde.")


def ensure_site(ctx, key: str) -> dict:
    cfg = ctx.scenario["sites"][key]
    group = ensure_m365_group(ctx, f"site:{key}", cfg["alias"], cfg["display_name"], cfg["description"], cfg["members"])
    site = wait_for_site(ctx, group["id"])
    drive = ctx.graph.get(f"sites/{site['id']}/drive?$select=id,webUrl") or {"id": f"dry-drive-{key}", "webUrl": site["webUrl"]}
    lst = ctx.graph.get(f"drives/{drive['id']}/list?$select=id,displayName") or {"id": f"dry-list-{key}", "displayName": "Documentos"}
    created = ctx.state.get("group", f"site:{key}")["created"]
    ctx.state.put("site", key, site["id"], created=created, webUrl=site["webUrl"], group_id=group["id"],
                  drive_id=drive["id"], list_id=lst["id"], list_name=lst.get("displayName"))
    log.info("Sitio %s: %s", key, site["webUrl"])
    return ctx.state.get("site", key)


# ------------------------------------------------------------------ ficheros
def ensure_folder(ctx, drive_id: str, name: str) -> dict:
    existing = ctx.graph.get(f"drives/{drive_id}/root:/{path_segment(name)}", ok_404=True)
    if existing:
        return existing
    return ctx.graph.post(f"drives/{drive_id}/root/children",
                          {"name": name, "folder": {}, "@microsoft.graph.conflictBehavior": "fail"})


def entry(item) -> tuple[str, str]:
    """Entrada del escenario: 'fichero' o {file: fichero, as: nombre_en_sharepoint}."""
    if isinstance(item, dict):
        return item["file"], item.get("as") or item["file"]
    return item, item


def upload(ctx, drive_id: str, folder: str | None, local: Path, target: str | None = None) -> dict:
    if not local.exists():
        raise FileNotFoundError(f"Falta {local}. Ejecuta `semdebt documents` o revisa la carpeta documentos/.")
    target = target or local.name
    rel = f"{path_segment(folder)}/{path_segment(target)}" if folder else path_segment(target)
    data = local.read_bytes()
    if len(data) <= SMALL_UPLOAD:
        item = ctx.graph.request("PUT", f"drives/{drive_id}/root:/{rel}:/content", data=data,
                                 headers={"Content-Type": "application/octet-stream"})
    else:
        sess = ctx.graph.post(f"drives/{drive_id}/root:/{rel}:/createUploadSession",
                              {"item": {"@microsoft.graph.conflictBehavior": "replace"}})
        item = None
        chunk = 5 * 1024 * 1024
        for start in range(0, len(data), chunk):
            part = data[start:start + chunk]
            resp = ctx.graph.session.put(sess["uploadUrl"], data=part, headers={
                "Content-Range": f"bytes {start}-{start + len(part) - 1}/{len(data)}"}, timeout=300)
            resp.raise_for_status()
            if resp.status_code in (200, 201):
                item = resp.json()
    if ctx.settings.dry_run:
        return {"id": f"dry-item-{target}", "webUrl": f"https://dry.run/{target}", "listItemId": "1"}
    li = ctx.graph.get(f"drives/{drive_id}/items/{item['id']}?$select=id,webUrl&$expand=listItem($select=id)")
    return {"id": li["id"], "webUrl": li["webUrl"], "listItemId": li["listItem"]["id"]}


def labels_file(ctx) -> Path:
    return ctx.settings.state_dir / "labels.json"


def apply_label(ctx, site_key: str, file_name: str, label_key: str) -> None:
    labels = read_json(labels_file(ctx))
    site = ctx.state.get("site", site_key)
    item = ctx.state.get("file", f"{site_key}:{file_name}")
    display = ctx.scenario["labels"][label_key]["display_name"]
    manual = f"Aplicar la etiqueta «{display}» a {file_name} en {site['webUrl']} (Word o SharePoint › Etiqueta de confidencialidad)"
    if label_key not in labels:
        log.warning("No hay id para la etiqueta %s: ejecuta Deploy-Labels.ps1. Queda como paso manual.", label_key)
        ctx.todo(manual)
        return
    if ctx.settings.label_apply_method == "manual":
        ctx.todo(manual)
        return
    try:
        ctx.graph.post(f"drives/{site['drive_id']}/items/{item['id']}/assignSensitivityLabel", {
            "sensitivityLabelId": labels[label_key]["id"],
            "assignmentMethod": "privileged",
            "justificationText": "Escenario de demo FraSoHome (Semantic Debt)",
        })
        log.info("Etiqueta «%s» solicitada para %s (operación asíncrona)", display, file_name)
    except ApiError as e:
        log.error("assignSensitivityLabel falló (%s). ¿Están habilitadas las API medidas de Graph?", e.status)
        ctx.todo(manual)


# ------------------------------------------------------------------ columnas
def _column_body(col: dict, mode: str) -> dict | None:
    base = {"name": col["name"], "displayName": col["display"], "enforceUniqueValues": False, "indexed": False}
    t = col["type"]
    if t == "choice":
        return {**base, "choice": {"allowTextEntry": False, "choices": col["choices"], "displayAs": "dropDownMenu"}}
    if t == "text":
        return {**base, "text": {"allowMultipleLines": False, "maxLength": 255}}
    if t == "date":
        return {**base, "dateTime": {"displayAs": "default", "format": "dateOnly"}}
    if t == "taxonomy_or_choice":
        if mode == "taxonomy":
            return None   # la crea Set-DominioTaxonomy.ps1 con PnP
        return {**base, "choice": {"allowTextEntry": False, "choices": [], "displayAs": "dropDownMenu"}}
    raise ValueError(t)


def ensure_columns(ctx, site: dict) -> None:
    sid, lid = site["id"], site["list_id"]
    existing = {c.get("name") for c in ctx.graph.get_all(f"sites/{sid}/lists/{lid}/columns")}
    mode = ctx.settings.dominio_column_mode
    terms = ctx.scenario["termstore"]["sets"]["dominio"]["terms"]
    for key, col in ctx.scenario["columns"].items():
        body = _column_body(col, mode)
        if body is None or col["name"] in existing:
            continue
        if col["type"] == "taxonomy_or_choice":
            body["choice"]["choices"] = terms
        ctx.graph.post(f"sites/{sid}/lists/{lid}/columns", body)
        ctx.state.put("column", f"kb_oficial:{col['name']}", col["name"], created=True, site_id=sid, list_id=lid)
    log.info("Columnas de la biblioteca oficial listas (Dominio: %s)", mode)


def set_metadata(ctx, site: dict, list_item_id: str, meta: dict) -> None:
    cols = ctx.scenario["columns"]
    fields = {cols["estado"]["name"]: meta["estado"], cols["propietario"]["name"]: meta["propietario"]}
    if meta.get("vigente_desde"):
        fields[cols["vigente_desde"]["name"]] = f"{meta['vigente_desde']}T00:00:00Z"
    if ctx.settings.dominio_column_mode == "choice":
        fields[cols["dominio"]["name"]] = meta["dominio"]
    ctx.graph.patch(f"sites/{site['id']}/lists/{site['list_id']}/items/{list_item_id}/fields", fields)


# ------------------------------------------------------------------ fases
def deploy_antes(ctx) -> None:
    site = ensure_site(ctx, "comercial")
    cfg = ctx.scenario["sites"]["comercial"]
    for folder, files in cfg["folders"].items():
        ensure_folder(ctx, site["drive_id"], folder)
        for it in files:
            src, target = entry(it)
            item = upload(ctx, site["drive_id"], folder, ctx.settings.doc(src), target)
            ctx.state.put("file", f"comercial:{target}", item["id"], created=True, webUrl=item["webUrl"],
                          folder=folder, list_item_id=item["listItemId"])
    for name, label_key in (cfg.get("labels") or {}).items():
        apply_label(ctx, "comercial", name, label_key)
    print(f"✔ Estado ANTES desplegado: {site['webUrl']} (sin columnas, solo carpetas)")


def deploy_despues(ctx) -> None:
    site = ensure_site(ctx, "kb_oficial")
    cfg = ctx.scenario["sites"]["kb_oficial"]
    ensure_columns(ctx, site)
    plan_items = []
    for meta in cfg["files"]:
        name = meta["file"]
        item = upload(ctx, site["drive_id"], None, ctx.settings.doc(name))
        ctx.state.put("file", f"kb_oficial:{name}", item["id"], created=True, webUrl=item["webUrl"],
                      list_item_id=item["listItemId"])
        set_metadata(ctx, site, item["listItemId"], meta)
        plan_items.append({"file": name, "listItemId": item["listItemId"], "term": meta["dominio"]})
    for name, label_key in (cfg.get("labels") or {}).items():
        apply_label(ctx, "kb_oficial", name, label_key)

    if ctx.settings.dominio_column_mode == "taxonomy":
        group = ctx.scenario["termstore"]["group"]
        dset = ctx.scenario["termstore"]["sets"]["dominio"]
        for it in plan_items:
            t = ctx.state.get("term", f"dominio:{it['term']}")
            it["termId"] = t["id"] if t else None
        plan = {"siteUrl": site["webUrl"], "listId": site["list_id"],
                "column": ctx.scenario["columns"]["dominio"], "termSetPath": f"{group}|{dset['name']}",
                "items": plan_items}
        write_json(ctx.settings.state_dir / "dominio_plan.json", plan)
        if any(i["termId"] is None for i in plan_items):
            log.warning("Faltan términos del conjunto Dominio: ejecuta `semdebt termstore` y repite esta fase.")
        ctx.todo("pwsh scripts/powershell/Set-DominioTaxonomy.ps1  (columna Dominio enlazada al term store)")
    print(f"✔ Estado DESPUÉS desplegado: {site['webUrl']} (Estado, Propietario, Vigente desde"
          f"{', Dominio' if ctx.settings.dominio_column_mode == 'choice' else ''})")


def run(ctx, fase: str) -> None:
    if fase == "antes":
        deploy_antes(ctx)
    elif fase == "despues":
        deploy_despues(ctx)
    else:
        raise ValueError("fase debe ser 'antes' o 'despues'")
