"""Ciclo de vida: workflow de «mover» que avisa (no transfiere) cuando un sponsor cambia de departamento."""

from __future__ import annotations

from agentid.contexto import Ctx
from agentid.graph import GraphError

SCOPES = ("LifecycleWorkflows.ReadWrite.All", "User.ReadWrite.All")
RUTA = "identityGovernance/lifecycleWorkflows/workflows"

# Learn · Lifecycle Workflow built-in tasks · Agent sponsor tasks
TAREA_AVISO_MANAGER = "b8c4e1f9-3a7d-4b2e-9c5f-8d6a9b1c2e3f"
TAREA_AVISO_COSPONSORS = "ad3b85cd-75b1-43e7-b4b9-0e52faba3944"
TAREA_TRANSFERIR = "b8f4c3d5-9e7a-4b1c-8f2d-6a5e8b9c7f4a"  # no se usa en el mover: ver slide 28


def cuerpo(ctx: Ctx, cc_ids: list[str]) -> dict:
    w = ctx.esc["workflow"]
    cc = [{"name": "cc", "value": ",".join(cc_ids)}] if cc_ids else []
    comunes = [{"name": "locale", "value": "es-es"}]
    return {
        "category": "mover", "displayName": w["nombre"], "description": w["descripcion"],
        "isEnabled": True, "isSchedulingEnabled": False,
        "executionConditions": {
            "@odata.type": "#microsoft.graph.identityGovernance.triggerAndScopeBasedConditions",
            "scope": {"@odata.type": "#microsoft.graph.identityGovernance.ruleBasedSubjectSet",
                      "rule": f"(companyName eq '{ctx.esc['empresa']}')"},
            "trigger": {"@odata.type": "#microsoft.graph.identityGovernance.attributeChangeTrigger",
                        "triggerAttributes": [{"name": "department"}]},
        },
        "tasks": [
            {"category": "mover", "continueOnError": True, "isEnabled": True,
             "displayName": "Avisar al manager del cambio de sponsor",
             "description": "Avisa al manager (con copia a Tiendas) para que decida quién responde por el agente.",
             "taskDefinitionId": TAREA_AVISO_MANAGER,
             "arguments": cc + comunes + [
                 {"name": "customSubject", "value": "{{userDisplayName}} ha cambiado de departamento: revisa sus agentes"},
                 {"name": "customBody", "value": (
                     "Hola {{managerDisplayName}}:\n\n{{userDisplayName}} ha cambiado de departamento y era sponsor "
                     "de uno o más agentes de FraSoHome. Decide quién debe responder por ellos.\n\nPlataforma de agentes")}]},
            {"category": "mover", "continueOnError": True, "isEnabled": True,
             "displayName": "Avisar a los co-sponsors",
             "description": "Avisa a los co-sponsors de los agentes afectados.",
             "taskDefinitionId": TAREA_AVISO_COSPONSORS, "arguments": cc + comunes},
        ],
    }


def desplegar(ctx: Ctx) -> None:
    g = ctx.graph(*SCOPES)
    w = ctx.esc["workflow"]
    cc_ids = [ctx.usuario_id(r) for r in w.get("copia_a", [])]
    existentes = [x for x in g.todos(f"{RUTA}?$select=id,displayName") if x["displayName"] == w["nombre"]]
    if existentes:
        wid, creado = existentes[0]["id"], False
    else:
        try:
            wid = g.post(RUTA, cuerpo(ctx, cc_ids))["id"]
            creado = True
        except GraphError as e:
            print(f"  ⚠ {w['nombre']}: {e}\n    Créalo en Entra → ID Governance → Lifecycle Workflows → Create workflow → "
                  "Mover, con las tareas «Send email to manager about sponsorship changes» y «Send email to "
                  "co-sponsors about sponsor changes» (sin la de transferir).")
            return
    ctx.estado.registrar("workflow", wid, creado=creado, nombre=w["nombre"])
    print(f"  {'+' if creado else '='} {w['nombre']} (mover · avisa, no transfiere)")
    print("\n  ⚠ La política de inactividad por defecto de Agent ID se activa a mano: Entra → ID Governance → "
          "Lifecycle Workflows → Lifecycle policies → Agent ID → Enable policy, con buzón de fallback.")


def ejecutar_para(ctx: Ctx, persona: str) -> None:
    wid = ctx.estado.id("workflow")
    if not wid:
        raise RuntimeError("No hay workflow: ejecuta `agentid ciclo`.")
    uid = ctx.usuario_id(persona)
    ctx.graph(*SCOPES).post(f"{RUTA}/{wid}/activate", {"subjects": [{"id": uid}]})
    print(f"  ▶ {ctx.esc['workflow']['nombre']} ejecutado bajo demanda para {ctx.esc['personas'][persona]['nombre']}")


def eliminar(ctx: Ctx) -> None:
    dato = ctx.estado.get("workflow")
    if dato and dato.get("creado"):
        try:
            ctx.graph(*SCOPES).delete(f"{RUTA}/{dato['id']}")
            print("  − workflow")
        except GraphError as e:
            if e.status != 404:
                raise
    ctx.estado.quitar("workflow")
