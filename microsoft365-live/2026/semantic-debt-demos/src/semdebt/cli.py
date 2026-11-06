"""semdebt — reproduce y limpia las demos de «Semantic Debt» (Microsoft 365 Live 2026).

Uso rápido:
  semdebt check
  semdebt deploy            # todos los pasos en orden (llama a pwsh si está instalado)
  semdebt evaluate --target chat
  semdebt glossary --estado publicado   # justo antes de la demo 4
  semdebt cleanup
"""
from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
import sys

from . import agent, check, cleanup, documents, evaluate, figures, glossary, identities, sharepoint, termstore
from .config import ROOT, ConfigError
from .context import Ctx

PS = ROOT / "scripts" / "powershell"


def _pwsh(ctx, script: str, *args: str) -> bool:
    path = PS / script
    if ctx.settings.dry_run:
        print(f"[dry-run] pwsh -File {path} {' '.join(args)}")
        return True
    exe = shutil.which("pwsh") or shutil.which("powershell")
    if not exe:
        ctx.todo(f"pwsh {path.relative_to(ROOT)} {' '.join(args)}")
        return False
    print(f"\n$ pwsh -File {path.relative_to(ROOT)}")
    return subprocess.run([exe, "-NoProfile", "-File", str(path), *args]).returncode == 0


def _ps_step(ctx, script: str) -> None:
    if _pwsh(ctx, script):
        ctx.pending[:] = [x for x in ctx.pending if script not in x]
    else:
        ctx.todo(f"pwsh scripts/powershell/{script}  (ha fallado o no hay PowerShell: revisa la salida)")


def deploy(ctx, args) -> None:
    steps = [
        ("Cifras", lambda: figures.run(ctx)),
        ("Documentos", lambda: documents.run(ctx)),
        ("Identidades", lambda: identities.run(ctx)),
        ("Etiquetas (PowerShell)", lambda: _ps_step(ctx, "Deploy-Labels.ps1")),
        ("SharePoint · antes", lambda: sharepoint.run(ctx, "antes")),
        ("Term store", lambda: termstore.run(ctx)),
        ("SharePoint · después", lambda: sharepoint.run(ctx, "despues")),
    ]
    if ctx.settings.dominio_column_mode == "taxonomy":
        steps.append(("Columna Dominio (PowerShell)", lambda: _ps_step(ctx, "Set-DominioTaxonomy.ps1")))
    steps += [
        ("Glosario · borrador", lambda: glossary.run(ctx, "borrador") if (ctx.settings.purview_domain_id or ctx.settings.dry_run)
         else ctx.todo("Configurar PURVIEW_DOMAIN_ID y ejecutar `semdebt glossary --estado borrador`")),
        ("Agente", lambda: agent.create(ctx)),
    ]
    for i, (name, fn) in enumerate(steps, 1):
        print(f"\n=== {i}/{len(steps)} · {name} ===")
        fn()
    ctx.todo("Esperar a la indexación (horas) y medir: `semdebt evaluate --target retrieval|chat|agent`")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="semdebt", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--env-file", help="Ruta del .env (por defecto ./.env)")
    p.add_argument("--dry-run", action="store_true", help="No llama a ningún servicio: enseña lo que haría")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="Comprueba parámetros, permisos y herramientas")
    sub.add_parser("figures", help="Recalcula las cifras de las slides con los datos del caso")
    sub.add_parser("documents", help="Genera los documentos del escenario en output/docs")
    sub.add_parser("identities", help="Laura, Paco, licencias y grupo FS-Finanzas")
    sp = sub.add_parser("sharepoint", help="Despliega un estado de SharePoint")
    sp.add_argument("--fase", choices=["antes", "despues"], required=True)
    sub.add_parser("termstore", help="Grupo FraSoHome y conjuntos de términos")
    gl = sub.add_parser("glossary", help="Término «Cliente activo» del glosario de Purview")
    gl.add_argument("--estado", choices=["borrador", "publicado"], required=True)
    ag = sub.add_parser("agent", help="Agente de Copilot Studio (pac)")
    ag.add_argument("accion", choices=["create", "extract-template", "delete"])
    ag.add_argument("--bot", help="Id o schema name del agente (extract-template)")
    ev = sub.add_parser("evaluate", help="Mide la TRC con el test set, como Laura")
    ev.add_argument("--target", choices=["retrieval", "chat", "agent"], required=True)
    ev.add_argument("--only", help="Ids separados por comas (p. ej. X1,X2,X3)")
    ev.add_argument("--sitio", choices=["comercial", "kb_oficial"], default="comercial",
                    help="Sitio al que se limita la Retrieval API (antes = comercial, después = kb_oficial)")
    ev.add_argument("--allow-admin", action="store_true", help=argparse.SUPPRESS)
    sub.add_parser("deploy", help="Todos los pasos de despliegue en orden")
    sub.add_parser("status", help="Qué hay desplegado según state/deployed.json")
    cl = sub.add_parser("cleanup", help="Borra solo lo creado por estos scripts")
    cl.add_argument("--yes", action="store_true", help="Sin confirmación")
    cl.add_argument("--purge", action="store_true", help="Purga también usuarios y grupos de la papelera de Entra")
    cl.add_argument("--keep-identities", action="store_true", help="No borra usuarios ni el grupo de Finanzas")
    cl.add_argument("--keep-local", action="store_true", help="No borra output/docs")

    a = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO, format="%(levelname)s %(message)s")
    try:
        ctx = Ctx.build(a.env_file, dry_run=a.dry_run, need_tenant=a.cmd not in ("figures", "documents", "status"))
    except ConfigError as e:
        print(f"Configuración: {e}", file=sys.stderr)
        return 2

    if a.cmd == "check":
        return 0 if check.run(ctx) else 1
    if a.cmd == "figures":
        figures.run(ctx)
    elif a.cmd == "documents":
        documents.run(ctx)
    elif a.cmd == "identities":
        identities.run(ctx)
    elif a.cmd == "sharepoint":
        sharepoint.run(ctx, a.fase)
    elif a.cmd == "termstore":
        termstore.run(ctx)
    elif a.cmd == "glossary":
        glossary.run(ctx, a.estado)
    elif a.cmd == "agent":
        if a.accion == "create":
            agent.create(ctx)
        elif a.accion == "extract-template":
            if not a.bot:
                p.error("extract-template necesita --bot")
            agent.extract_template(ctx, a.bot)
        else:
            rec = ctx.state.get("agent", ctx.settings.agent_schema_name)
            if not rec:
                print("No hay agente registrado en state/deployed.json")
                return 1
            agent.delete(ctx, rec)
            ctx.state.remove("agent", ctx.settings.agent_schema_name)
    elif a.cmd == "evaluate":
        evaluate.run(ctx, a.target, a.only.split(",") if a.only else None, a.allow_admin, a.sitio)
    elif a.cmd == "deploy":
        deploy(ctx, a)
    elif a.cmd == "status":
        for r in ctx.state.data["resources"]:
            print(f"{r['type']:<13} {r['key']:<45} {'creado' if r.get('created') else 'reutilizado'}  {r.get('webUrl', '')}")
    elif a.cmd == "cleanup":
        cleanup.run(ctx, a.yes, a.purge, a.keep_identities, a.keep_local)

    if ctx.pending:
        print("\nPendiente (manual o PowerShell):")
        for t in dict.fromkeys(ctx.pending):
            print(f"  □ {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
