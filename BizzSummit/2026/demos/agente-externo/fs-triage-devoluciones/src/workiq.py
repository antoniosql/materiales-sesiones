# A365 WorkIQ — best-effort wiring (verify against SDK source before production)
"""Servidores MCP de Work IQ para el Claude Agent SDK.

No hay adaptador publicado de Work IQ para Python + Claude, así que se cablea a
mano: se leen los servidores de ToolingManifest.json (lo escribe
`a365 develop add-mcp-servers`) y se pasan al SDK como servidores MCP HTTP.

Cada servidor V2 tiene su propia audiencia, así que cada uno lleva su token
delegado (OBO) en BEARER_TOKEN_<NOMBRE>, p. ej. BEARER_TOKEN_MCP_MAILTOOLS.
BEARER_TOKEN sirve de comodín. Los tokens caducan: se renuevan con
`a365 develop get-token`.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

MANIFIESTO = Path(__file__).resolve().parents[1] / "ToolingManifest.json"


def servidores_workiq() -> tuple[dict[str, dict], list[str]]:
    """Devuelve (mcp_servers, allowed_tools) para ClaudeAgentOptions."""
    if not MANIFIESTO.exists():
        return {}, []

    omitir_errores = os.environ.get("SKIP_TOOLING_ON_ERRORS", "false").lower() == "true"
    servidores: dict[str, dict] = {}
    permitidas: list[str] = []

    for servidor in json.loads(MANIFIESTO.read_text(encoding="utf-8")).get("mcpServers", []):
        nombre = servidor["mcpServerName"]
        token = os.environ.get(f"BEARER_TOKEN_{nombre.upper()}") or os.environ.get("BEARER_TOKEN")
        if not token:
            mensaje = f"Sin token para {nombre}: define BEARER_TOKEN_{nombre.upper()} (a365 develop get-token)."
            if omitir_errores:
                print(f"  [workiq] {mensaje} Se omite.", file=sys.stderr)
                continue
            raise RuntimeError(mensaje)

        servidores[nombre] = {
            "type": "http",
            "url": servidor["url"],
            "headers": {"Authorization": f"Bearer {token}"},
        }
        permitidas.append(f"mcp__{nombre}")  # todas las herramientas de ese servidor

    return servidores, permitidas
