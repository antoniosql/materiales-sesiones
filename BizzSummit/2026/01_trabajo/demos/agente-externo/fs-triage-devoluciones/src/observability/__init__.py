# observability/__init__.py
# A365 Observability — best-effort instrumentation (verify against official sample)
"""Telemetría de Agent 365 para fs-triage-devoluciones.

Se importa ANTES que claude_agent_sdk: use_microsoft_opentelemetry() tiene que
configurar el pipeline antes de que se cree ningún span.

A365 auth mode: obo — telemetry uses an app-only token on the S2S route.
"""

from __future__ import annotations

import atexit
import contextvars
import functools
import json
import logging
import os

from dotenv import load_dotenv

load_dotenv()

from opentelemetry import trace  # noqa: E402
from microsoft.opentelemetry import use_microsoft_opentelemetry  # noqa: E402
from microsoft.opentelemetry.a365.core import (  # noqa: E402
    AgentDetails,
    CallerDetails,
    Channel,
    ExecuteToolScope,
    Request,
    ToolCallDetails,
    UserDetails,
)

from .app_token_resolver import AppTokenResolver  # noqa: E402

logger = logging.getLogger(__name__)

TENANT_ID = os.environ.get("AGENT365OBSERVABILITY__TENANTID", "")
BLUEPRINT_ID = os.environ.get("AGENT365OBSERVABILITY__AGENTBLUEPRINTID", "")
# Identidad de agente que creó `a365 setup all`. Nunca el blueprint: el exportador
# se autentica como esta identidad y la ruta S2S rechazaría el id del blueprint.
_agent_id = os.environ.get("AGENT365OBSERVABILITY__AGENTID", "")
AGENT_ID = _agent_id if _agent_id and _agent_id.lower() != BLUEPRINT_ID.lower() else ""

OBS_TOKENS = AppTokenResolver()

use_microsoft_opentelemetry(
    enable_a365=bool(AGENT_ID and TENANT_ID),
    a365_enable_observability_exporter=os.environ.get("ENABLE_A365_OBSERVABILITY_EXPORTER", "false").lower() == "true",
    a365_use_s2s_endpoint=True,  # every auth mode exports over the S2S route
    a365_token_resolver=OBS_TOKENS.resolve,
    a365_exporter_disable_offline_storage=True,
    # El SDK de Claude no se autoinstrumenta; los spans los abren los scopes de agent.py.
    # Sin esto el distro intenta cargar las de OpenAI Agents y Agent Framework y falla.
    instrumentation_options={"openai_agents": {"enabled": False}, "agent_framework": {"enabled": False}},
)

agent_details = AgentDetails(
    agent_id=AGENT_ID,
    agent_name=os.environ.get("AGENT365OBSERVABILITY__AGENTNAME", "FsTriageDevoluciones"),
    agent_description=os.environ.get("AGENT365OBSERVABILITY__AGENTDESCRIPTION", ""),
    agent_blueprint_id=BLUEPRINT_ID,
    tenant_id=TENANT_ID,
    provider_name="anthropic",
)

# El agente corre como tarea programada, sin usuario conectado: el llamante que se
# reporta es el sponsor del blueprint. Sin CallerDetails las trazas no salen en MAC.
user_details = UserDetails(
    user_id=os.environ.get("AGENT365_SPONSOR_USER_ID", BLUEPRINT_ID),
    user_email=os.environ.get("AGENT365_SPONSOR_USER_EMAIL", ""),
    user_name=os.environ.get("AGENT365_SPONSOR_USER_NAME", ""),
)
caller_details = CallerDetails(user_details=user_details)

CANAL = Channel(name="cli")
SESION: contextvars.ContextVar[str] = contextvars.ContextVar("sesion", default="")


async def preparar_token() -> None:
    """Pide el token de telemetría antes de la ejecución; si falla, el agente sigue."""
    try:
        await OBS_TOKENS.prefetch(TENANT_ID, AGENT_ID)
    except Exception as e:
        logger.warning("Failed to acquire observability token: %s", e)


def peticion(contenido: str, sesion: str) -> Request:
    return Request(content=contenido, session_id=sesion, conversation_id=sesion, channel=CANAL)


def trazar_herramienta(nombre: str, descripcion: str | None = None):
    """Envuelve el handler de una herramienta en un ExecuteToolScope."""

    def decorador(fn):
        @functools.wraps(fn)
        async def envoltorio(args: dict) -> dict:
            detalles = ToolCallDetails(
                tool_name=nombre,
                arguments=json.dumps(args, ensure_ascii=False),
                description=descripcion,
                tool_type="function",
            )
            with ExecuteToolScope.start(peticion(nombre, SESION.get()), detalles, agent_details, user_details) as scope:
                resultado = await fn(args)
                scope.record_response(
                    "\n".join(b.get("text", "") for b in resultado.get("content", []))
                )
                return resultado

        return envoltorio

    return decorador


def _cerrar_trazas() -> None:
    proveedor = trace.get_tracer_provider()
    if hasattr(proveedor, "shutdown"):
        proveedor.shutdown()


atexit.register(_cerrar_trazas)
