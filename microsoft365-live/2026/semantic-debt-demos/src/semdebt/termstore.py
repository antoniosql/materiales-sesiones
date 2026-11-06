"""Term store: grupo FraSoHome con los conjuntos «Estado documental» y «Dominio» (Graph)."""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def _label(item: dict) -> str:
    names = item.get("localizedNames") or item.get("labels") or []
    return (names[0].get("name") if names else item.get("displayName", "")) or ""


def run(ctx) -> dict:
    site = ctx.state.get("site", "kb_oficial") or ctx.state.get("site", "comercial")
    if not site:
        raise RuntimeError("Necesito un sitio desplegado (ejecuta antes `semdebt sharepoint --fase antes`).")
    sid = site["id"]
    cfg = ctx.scenario["termstore"]
    g = ctx.graph
    store = g.get(f"sites/{sid}/termStore") or {"id": "dry-store", "defaultLanguageTag": "es-ES"}
    lang = store.get("defaultLanguageTag", "es-ES")
    ctx.state.put("termstore", "store", store["id"], created=False, site_id=sid, language=lang)

    groups = g.get_all(f"sites/{sid}/termStore/groups")
    group = next((x for x in groups if x.get("displayName") == cfg["group"]), None)
    if group:
        prev = ctx.state.get("termgroup", cfg["group"]) or {}
        ctx.state.put("termgroup", cfg["group"], group["id"], created=bool(prev.get("created")), site_id=sid)
    else:
        group = g.post(f"sites/{sid}/termStore/groups", {"displayName": cfg["group"], "scope": "global"})
        ctx.state.put("termgroup", cfg["group"], group["id"], created=True, site_id=sid)

    result = {"store_id": store["id"], "group_id": group["id"], "sets": {}}
    existing_sets = g.get_all(f"sites/{sid}/termStore/groups/{group['id']}/sets")
    for key, sdef in cfg["sets"].items():
        tset = next((x for x in existing_sets if _label(x) == sdef["name"]), None)
        created = False
        if not tset:
            tset = g.post(f"sites/{sid}/termStore/sets", {
                "parentGroup": {"id": group["id"]},
                "localizedNames": [{"languageTag": lang, "name": sdef["name"]}],
            })
            created = True
        ctx.state.put("termset", key, tset["id"], created=created or bool((ctx.state.get("termset", key) or {}).get("created")),
                      site_id=sid, name=sdef["name"])
        terms = {}
        existing_terms = g.get_all(f"sites/{sid}/termStore/sets/{tset['id']}/children")
        for label in sdef["terms"]:
            term = next((x for x in existing_terms if _label(x) == label), None)
            t_created = False
            if not term:
                term = g.post(f"sites/{sid}/termStore/sets/{tset['id']}/children", {
                    "labels": [{"languageTag": lang, "name": label, "isDefault": True}]})
                t_created = True
            prev = ctx.state.get("term", f"{key}:{label}") or {}
            ctx.state.put("term", f"{key}:{label}", term["id"], created=t_created or bool(prev.get("created")),
                          site_id=sid, set_id=tset["id"], label=label)
            terms[label] = term["id"]
        result["sets"][key] = {"id": tset["id"], "terms": terms}
    print(f"✔ Term store: grupo «{cfg['group']}» con {len(cfg['sets'])} conjuntos ({lang})")
    return result
