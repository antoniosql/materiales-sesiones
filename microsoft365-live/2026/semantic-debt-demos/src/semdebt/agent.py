"""Agente de Copilot Studio «Asistente Comercial FraSoHome» mediante Power Platform CLI (pac).

Flujo:
1. La primera vez se monta en Copilot Studio siguiendo copilot-studio/README.md
   (fuente de conocimiento, filtrado por metadatos e instrucciones).
2. `semdebt agent extract-template --bot <id>` guarda la plantilla en AGENT_TEMPLATE_FILE.
3. Desde ahí, `semdebt agent create` lo recrea por código en cualquier entorno, y `semdebt agent delete` lo borra.

Requiere `pac` en el PATH y un perfil autenticado (`pac auth create --environment <id>`).
"""
from __future__ import annotations

import logging
import re
import shutil
import subprocess

log = logging.getLogger(__name__)
GUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)


def _pac(ctx, *args: str) -> str:
    cmd = ["pac", "copilot", *args]
    if ctx.settings.pp_environment_id:
        cmd += ["--environment", ctx.settings.pp_environment_id]
    if ctx.settings.dry_run:
        log.info("[dry-run] %s", " ".join(cmd))
        return ""
    if not shutil.which("pac"):
        raise RuntimeError("No encuentro `pac` (Power Platform CLI). Instálalo: dotnet tool install --global Microsoft.PowerApps.CLI.Tool")
    log.info("$ %s", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"pac falló ({proc.returncode}): {proc.stdout}\n{proc.stderr}")
    return proc.stdout


def find_bot_id(ctx) -> str | None:
    out = _pac(ctx, "list")
    for line in out.splitlines():
        if ctx.settings.agent_schema_name in line or ctx.settings.agent_display_name in line:
            m = GUID.search(line)
            if m:
                return m.group(0)
    return None


def create(ctx) -> None:
    s = ctx.settings
    tpl = s.agent_template_file
    if not tpl or not tpl.exists():
        ctx.todo("Montar el agente la primera vez a mano (copilot-studio/README.md) y exportar la plantilla con "
                 "`semdebt agent extract-template --bot <id>`")
        print(f"⚠ No existe la plantilla {tpl}. Sigue copilot-studio/README.md para montarlo la primera vez.")
        return
    existing = find_bot_id(ctx)
    if existing:
        log.info("El agente ya existe (%s): se reutiliza", existing)
        ctx.state.put("agent", s.agent_schema_name, existing, created=bool((ctx.state.get("agent", s.agent_schema_name) or {}).get("created")))
        return
    _pac(ctx, "create", "--displayName", s.agent_display_name, "--schemaName", s.agent_schema_name,
         "--solution", s.agent_solution, "--templateFileName", str(tpl))
    bot_id = find_bot_id(ctx) or "dry-bot"
    ctx.state.put("agent", s.agent_schema_name, bot_id, created=True)
    _pac(ctx, "publish", "--bot", bot_id)
    ctx.todo("Copilot Studio › Conocimiento: comprobar que el filtrado por metadatos (Estado = Vigente) sigue activo "
             "y que la fuente apunta a FraSoHome-KB-Oficial")
    print(f"✔ Agente creado y publicado: {s.agent_display_name} ({bot_id})")


def extract_template(ctx, bot: str) -> None:
    tpl = ctx.settings.agent_template_file
    tpl.parent.mkdir(parents=True, exist_ok=True)
    _pac(ctx, "extract-template", "--bot", bot, "--templateFileName", str(tpl), "--overwrite")
    ctx.state.put("agent", ctx.settings.agent_schema_name, bot, created=False)
    print(f"✔ Plantilla guardada en {tpl}")


def delete(ctx, rec: dict) -> None:
    _pac(ctx, "delete", "--bot", rec["id"], "--confirm")
