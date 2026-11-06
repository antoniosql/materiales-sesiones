"""Comprobaciones previas: parámetros, token, permisos y herramientas."""
from __future__ import annotations

import shutil

from . import auth
from .http import ApiError, path_segment


def _ok(msg):
    print(f"  ✔ {msg}")


def _ko(msg):
    print(f"  ✘ {msg}")


def run(ctx) -> bool:
    s, good = ctx.settings, True
    print("Parámetros")
    from .documents import required_files
    missing = sorted(n for n in required_files(ctx.scenario) if not s.doc(n).exists())
    if missing:
        _ko(f"Faltan documentos para subir: {missing} (ejecuta `semdebt documents`)"); good = False
    else:
        _ok(f"Documentos para subir: {s.docs_dir}")
    for label, value in (("Datos del caso", s.case_data_dir), ("KB del caso", s.case_kb_dir)):
        if value and value.exists():
            _ok(f"{label}: {value}")
        else:
            print(f"  · {label} no configurado o no existe ({value}): solo hace falta para regenerar documentos/")
    if s.dry_run:
        print("(dry-run: no se comprueba el tenant)")
        return good

    print("Tenant (token de aplicación)")
    try:
        auth.app_token(s); _ok("token de Graph")
    except auth.AuthError as e:
        _ko(str(e)); return False
    probes = [
        ("Leer la organización", "organization?$select=id,displayName"),
        ("Leer licencias (Organization.Read.All)", "subscribedSkus"),
        ("Leer usuarios (User.Read.All)", f"users/{path_segment(s.admin_upn)}?$select=id"),
        ("Leer sitios (Sites.Read.All)", "sites/root?$select=id,webUrl"),
        ("Leer grupos (Group.Read.All)", "groups?$top=1&$select=id"),
    ]
    for label, path in probes:
        try:
            ctx.graph.get(path); _ok(label)
        except ApiError as e:
            _ko(f"{label}: {e.status}"); good = False
    try:
        root = ctx.graph.get("sites/root?$select=id")
        ctx.graph.get(f"sites/{root['id']}/termStore"); _ok("Term store (TermStore.Read/ReadWrite.All)")
    except ApiError as e:
        _ko(f"Term store: {e.status}"); good = False

    print("Herramientas")
    for tool, why in (("pwsh", "etiquetas de Purview y columna Dominio"), ("pac", "agente de Copilot Studio")):
        (_ok if shutil.which(tool) else _ko)(f"{tool} ({why})")
    print("Opcional")
    print(f"  · Purview Unified Catalog: dominio {'configurado' if s.purview_domain_id else 'SIN configurar (PURVIEW_DOMAIN_ID)'}")
    print(f"  · Etiquetado: {s.label_apply_method} · Columna Dominio: {s.dominio_column_mode}")
    if s.label_apply_method == "graph":
        print("    assignSensitivityLabel es una API medida: requiere habilitar la facturación de Graph para la app.")
    return good
