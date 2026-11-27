"""Puerta 2 · Foundry: conexión MCP con identidad de agente, agente frasohome-returns y el «antes» de la demo 2."""

from __future__ import annotations

from agentid import agentes, atributos
from agentid.az import AzError, ambito_contenedor, asignar_rol, azd, quitar_rol
from agentid.contexto import Ctx

ROL = "Storage Blob Data Reader"
CONTENEDOR = "devoluciones"
AUDIENCE = "https://storage.azure.com"


def endpoint(ctx: Ctx) -> str:
    ep = ctx.s.foundry_project_endpoint or (ctx.estado.get("infra") or {}).get("foundryProjectEndpoint")
    if not ep:
        raise RuntimeError("Falta el endpoint del proyecto: FOUNDRY_PROJECT_ENDPOINT o `agentid infra` con DEPLOY_FOUNDRY=true.")
    return ep


def _cliente(ctx: Ctx):
    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential
    except ImportError as e:
        raise RuntimeError('Faltan los paquetes de Foundry: pip install -e ".[foundry]"') from e
    return AIProjectClient(endpoint=endpoint(ctx), credential=DefaultAzureCredential(), allow_preview=True)


def identidades(ctx: Ctx) -> None:
    """Lista las identidades de agente que parecen del proyecto o del agente, para rellenar el .env."""
    proyecto = endpoint(ctx).rstrip("/").split("/")[-1]
    agente = ctx.esc["agentes"]["foundry"]["nombre"]
    filas = [i for i in agentes.listar_identidades(ctx)
             if any(x in (i.get("displayName") or "").lower() for x in (proyecto.lower(), agente.lower()))]
    if not filas:
        print("  No encuentro identidades con el nombre del proyecto o del agente. Búscalas en Entra → Agent ID.")
    for i in filas:
        print(f"  {i['id']}  {i.get('displayName')}  (blueprint {i.get('agentIdentityBlueprintId')})")
    print("\n  Copia la del proyecto en FOUNDRY_SHARED_IDENTITY_ID y la del agente en FOUNDRY_AGENT_IDENTITY_ID.")


def identidad_agente(ctx: Ctx) -> str:
    if ctx.s.foundry_agent_identity_id:
        return ctx.s.foundry_agent_identity_id
    nombre = ctx.esc["agentes"]["foundry"]["nombre"]
    res = agentes.buscar_identidad(ctx, nombre)
    if len(res) != 1:
        raise RuntimeError(f"Encuentro {len(res)} identidades para «{nombre}». Pon la buena en FOUNDRY_AGENT_IDENTITY_ID "
                           "(`agentid foundry identidades`).")
    return res[0]["id"]


def conexion(ctx: Ctx) -> None:
    f = ctx.esc["foundry"]
    url = (ctx.estado.get("apps") or {}).get("mcpUrl")
    if not url:
        raise RuntimeError("Falta la URL del servidor MCP: ejecuta antes `agentid apps`.")
    try:
        azd("ai", "project", "set", endpoint(ctx))
        azd("ai", "connection", "create", f["conexion"], "--kind", "remote-tool", "--target", url,
            "--auth-type", "agentic-identity", "--audience", AUDIENCE)
        print(f"  + conexión {f['conexion']} → {url} (identidad de agente, audience {AUDIENCE})")
    except AzError as e:
        print(f"  ⚠ azd no ha podido crear la conexión: {e}\n"
              "  Créala en el portal de Foundry → proyecto → Management center → Connected resources → New → "
              f"Remote tool (MCP):\n    nombre {f['conexion']} · endpoint {url}\n"
              f"    autenticación: Agent identity · audience {AUDIENCE}")
    ctx.estado.poner("foundry_conexion", {"nombre": f["conexion"], "url": url})


def agente(ctx: Ctx) -> None:
    try:
        from azure.ai.projects.models import MCPTool, PromptAgentDefinition
    except ImportError as e:
        raise RuntimeError('Faltan los paquetes de Foundry: pip install -e ".[foundry]"') from e

    f, a = ctx.esc["foundry"], ctx.esc["agentes"]["foundry"]
    url = (ctx.estado.get("apps") or {}).get("mcpUrl")
    with _cliente(ctx) as proyecto:
        version = proyecto.agents.create_version(
            agent_name=a["nombre"],
            definition=PromptAgentDefinition(
                model=ctx.s.foundry_model, instructions=f["instrucciones"],
                tools=[MCPTool(server_label=f["server_label"], server_url=url, require_approval="never",
                               project_connection_id=f["conexion"])]))
    ctx.estado.poner("foundry_agente", {"nombre": version.name, "version": version.version})
    print(f"  + agente {version.name} v{version.version} · modelo {ctx.s.foundry_model} · MCP {f['server_label']}")


def preguntar(ctx: Ctx, pregunta: str | None = None) -> None:
    pregunta = pregunta or ctx.esc["foundry"]["pregunta_demo"]
    nombre = ctx.esc["agentes"]["foundry"]["nombre"]
    with _cliente(ctx) as proyecto, proyecto.get_openai_client(agent_name=nombre) as openai:
        conv = openai.conversations.create()
        r = openai.responses.create(conversation=conv.id, input=pregunta)
        for item in r.output:
            if item.type == "mcp_call":
                estado = "ERROR " + str(item.error) if getattr(item, "error", None) else "ok"
                print(f"  · MCP {item.server_label}.{item.name} → {estado}")
                if getattr(item, "output", None):
                    print("    " + str(item.output).replace("\n", "\n    "))
        print(f"\n  {nombre}: {r.output_text}\n")
        openai.conversations.delete(conversation_id=conv.id)


def _ambito(ctx: Ctx) -> str:
    return ambito_contenedor((ctx.estado.get("infra") or {})["storageAccountId"], CONTENEDOR)


def antes(ctx: Ctx) -> None:
    """Estado de partida de la demo 2: el rol lo tiene la identidad compartida del proyecto; el agente, nada."""
    compartida = ctx.s.foundry_shared_identity_id
    if not compartida:
        raise RuntimeError("Pon la identidad compartida del proyecto en FOUNDRY_SHARED_IDENTITY_ID "
                           "(`agentid foundry identidades`).")
    propia = identidad_agente(ctx)
    asignar_rol(compartida, ROL, _ambito(ctx))
    quitado = quitar_rol(propia, ROL, _ambito(ctx))
    try:
        agentes.fijar_sponsors(ctx, propia, ctx.esc["agentes"]["foundry"]["sponsors"])
        atributos.asignar(ctx, propia, ctx.esc["agentes"]["foundry"]["carril"])
    except Exception as e:  # noqa: BLE001 — no bloquea la demo 2
        print(f"  ⚠ sponsors/atributo de {propia} no aplicados: {e}")
    ctx.estado.registrar("identidad:foundry", propia, creado=False, compartida=compartida)
    print(f"  = {ROL} sobre «{CONTENEDOR}» → identidad compartida {compartida}")
    print(f"  {'− retirado de' if quitado else '= sin rol en'} la identidad propia {propia}")
