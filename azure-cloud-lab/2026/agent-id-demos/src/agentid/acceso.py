"""Acceso condicional para agentes: CA-AG-01 (riesgo alto en Producción) y CA-AG-02 (Playground)."""

from __future__ import annotations

from agentid import atributos
from agentid.contexto import Ctx
from agentid.graph import GraphError

SCOPES = ("Policy.Read.All", "Policy.ReadWrite.ConditionalAccess", "Application.Read.All")


def cuerpo(ctx: Ctx, clave: str) -> dict:
    p = ctx.esc["acceso_condicional"][clave]
    condiciones = {
        "clientApplications": {
            "includeAgentIdServicePrincipals": ["All"],
            "excludeAgentIdServicePrincipals": [],
            "agentIdServicePrincipalFilter": {"mode": "include", "rule": atributos.regla_filtro(ctx, p["carril"])},
        },
        "applications": {"includeApplications": p["recursos"], "excludeApplications": []},
    }
    if p.get("riesgo"):
        condiciones["agentIdRiskLevels"] = p["riesgo"]
    return {"displayName": p["nombre"], "state": ctx.s.ca_states.get(clave, "enabledForReportingButNotEnforced"),
            "conditions": condiciones, "grantControls": {"operator": "AND", "builtInControls": ["block"]}}


def desplegar(ctx: Ctx) -> None:
    g = ctx.graph(*SCOPES)
    existentes = {p["displayName"]: p["id"] for p in
                  g.todos("identity/conditionalAccess/policies?$select=id,displayName", version="beta")}
    for clave in ctx.esc["acceso_condicional"]:
        c = cuerpo(ctx, clave)
        try:
            if c["displayName"] in existentes:
                pid = existentes[c["displayName"]]
                g.patch(f"identity/conditionalAccess/policies/{pid}", c, version="beta")
                creado = False
            else:
                pid = g.post("identity/conditionalAccess/policies", c, version="beta")["id"]
                creado = True
        except GraphError as e:
            print(f"  ⚠ {clave}: {e}\n    Créala en el portal (Entra → Conditional Access → New policy → Agents) "
                  "con los valores de config/escenario.yaml.")
            continue
        ctx.estado.registrar(f"ca:{clave}", pid, creado=creado, nombre=c["displayName"])
        print(f"  {'+' if creado else '='} {c['displayName']} · {c['state']}")


def eliminar(ctx: Ctx) -> None:
    g = ctx.graph(*SCOPES)
    for clave in [k for k in list(ctx.estado.datos) if k.startswith("ca:")]:
        if ctx.estado.datos[clave].get("creado"):
            try:
                g.delete(f"identity/conditionalAccess/policies/{ctx.estado.id(clave)}", version="beta")
                print(f"  − {clave}")
            except GraphError as e:
                if e.status != 404:
                    raise
        ctx.estado.quitar(clave)
