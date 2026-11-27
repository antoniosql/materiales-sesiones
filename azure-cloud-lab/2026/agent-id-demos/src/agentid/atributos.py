"""Atributo de seguridad personalizado FraSoHome.Carril: los carriles del Bizz Summit, como dato."""

from __future__ import annotations

from agentid.contexto import Ctx
from agentid.graph import GraphError

SCOPES_DEF = ("CustomSecAttributeDefinition.ReadWrite.All",)
SCOPES_ASIG = ("CustomSecAttributeAssignment.ReadWrite.All", "AgentIdentity.ReadWrite.All")


def definicion_id(ctx: Ctx) -> str:
    a = ctx.esc["atributo"]
    return f"{a['conjunto']}_{a['nombre']}"


def regla_filtro(ctx: Ctx, valor: str) -> str:
    """Regla para el filtro de acceso condicional (agentIdServicePrincipalFilter)."""
    return f'CustomSecurityAttribute.{definicion_id(ctx)} -eq "{valor}"'


def desplegar(ctx: Ctx) -> None:
    g = ctx.graph(*SCOPES_DEF)
    a = ctx.esc["atributo"]
    try:
        if not g.existe(f"directory/attributeSets/{a['conjunto']}"):
            g.post("directory/attributeSets", {"id": a["conjunto"], "maxAttributesPerSet": 25,
                                               "description": "Escenario FraSoHome · Azure Cloud Lab 2026"})
            print(f"  + conjunto de atributos {a['conjunto']}")
        did = definicion_id(ctx)
        if not g.existe(f"directory/customSecurityAttributeDefinitions/{did}"):
            g.post("directory/customSecurityAttributeDefinitions", {
                "attributeSet": a["conjunto"], "name": a["nombre"], "description": a["descripcion"],
                "type": "String", "status": "Available", "isCollection": False, "isSearchable": True,
                "usePreDefinedValuesOnly": True})
            print(f"  + atributo {did}")
        existentes = {v["id"] for v in g.todos(f"directory/customSecurityAttributeDefinitions/{did}/allowedValues")}
        for v in a["valores"]:
            if v not in existentes:
                g.post(f"directory/customSecurityAttributeDefinitions/{did}/allowedValues", {"id": v, "isActive": True})
        print(f"  = valores: {', '.join(a['valores'])}")
    except GraphError as e:
        if e.status == 403:
            raise RuntimeError("403 en atributos: Nuria necesita los roles «Attribute Definition Administrator» y "
                               "«Attribute Assignment Administrator» (ni Global Administrator los tiene por defecto).") from e
        raise
    ctx.estado.poner("atributo", {"id": definicion_id(ctx)})


def asignar(ctx: Ctx, sp_id: str, valor: str) -> None:
    g = ctx.graph(*SCOPES_ASIG)
    a = ctx.esc["atributo"]
    cuerpo = {"customSecurityAttributes": {a["conjunto"]: {
        "@odata.type": "#Microsoft.DirectoryServices.CustomSecurityAttributeValue", a["nombre"]: valor}}}
    try:
        g.patch(f"servicePrincipals/{sp_id}", cuerpo, version="beta", reintentos_404=6)
    except GraphError:
        g.patch(f"servicePrincipals/{sp_id}/microsoft.graph.agentIdentity", cuerpo, version="beta")


def leer(ctx: Ctx, sp_id: str) -> str | None:
    g = ctx.graph("CustomSecAttributeAssignment.ReadWrite.All")
    a = ctx.esc["atributo"]
    d = g.get(f"servicePrincipals/{sp_id}?$select=customSecurityAttributes", version="beta")
    return ((d.get("customSecurityAttributes") or {}).get(a["conjunto"]) or {}).get(a["nombre"])
