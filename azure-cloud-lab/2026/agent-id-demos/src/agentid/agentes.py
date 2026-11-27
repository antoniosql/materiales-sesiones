"""Blueprints, identidades de agente, sponsors y owners (Microsoft Graph · Agent ID)."""

from __future__ import annotations

from agentid import atributos
from agentid.contexto import Ctx
from agentid.graph import Graph, GraphError, odata_id

SCOPES = ("AgentIdentityBlueprint.Create", "AgentIdentityBlueprint.ReadWrite.All",
          "AgentIdentityBlueprint.AddRemoveCreds.All", "AgentIdentityBlueprintPrincipal.Create",
          "AgentIdentity.Create.All", "AgentIdentity.ReadWrite.All", "Application.Read.All", "Directory.Read.All")
CAST = "microsoft.graph.agentIdentity"


def _g(ctx: Ctx) -> Graph:
    return ctx.graph(*SCOPES)


def _binds(ctx: Ctx, refs: list[str]) -> list[str]:
    return [odata_id(*ctx.principal(r)) for r in refs]


# ---------------------------------------------------------------- búsqueda
def listar_identidades(ctx: Ctx) -> list[dict]:
    return _g(ctx).todos(f"servicePrincipals/{CAST}?$select=id,displayName,agentIdentityBlueprintId,"
                         "accountEnabled,createdDateTime&$top=100", version="beta")


def buscar_identidad(ctx: Ctx, nombre: str) -> list[dict]:
    nombre_l = nombre.lower()
    return [i for i in listar_identidades(ctx) if nombre_l in (i.get("displayName") or "").lower()]


def client_id(ctx: Ctx, identidad_id: str) -> str:
    """Client id con el que se pide token como la identidad (appId si Graph lo devuelve; si no, su id)."""
    d = _g(ctx).get(f"servicePrincipals/{identidad_id}?$select=id,appId", version="beta", reintentos_404=6)
    return d.get("appId") or d["id"]


# ---------------------------------------------------------------- sponsors y owners
def sponsors(ctx: Ctx, identidad_id: str) -> list[dict]:
    return _g(ctx).todos(f"servicePrincipals/{identidad_id}/{CAST}/sponsors?$select=id,displayName",
                         version="beta")


def fijar_sponsors(ctx: Ctx, identidad_id: str, refs: list[str]) -> list[str]:
    """Deja exactamente esos sponsors. Primero añade y luego quita: nunca se queda sin sponsor."""
    g = _g(ctx)
    deseados = [ctx.principal(r) for r in refs]
    actuales = {s["id"]: s.get("displayName") for s in sponsors(ctx, identidad_id)}
    for tipo, pid in deseados:
        if pid not in actuales:
            g.post(f"servicePrincipals/{identidad_id}/{CAST}/sponsors/$ref",
                   {"@odata.id": odata_id("directoryObjects", pid)}, version="beta")
    for pid in set(actuales) - {pid for _, pid in deseados}:
        g.delete(f"servicePrincipals/{identidad_id}/{CAST}/sponsors/{pid}/$ref", version="beta")
    return [s.get("displayName") for s in sponsors(ctx, identidad_id)]


def anadir_owners(ctx: Ctx, sp_id: str, refs: list[str], cast: str | None = CAST) -> None:
    g = _g(ctx)
    ruta = f"servicePrincipals/{sp_id}/{cast}/owners" if cast else f"servicePrincipals/{sp_id}/owners"
    actuales = {o["id"] for o in g.todos(f"{ruta}?$select=id", version="beta")}
    for r in refs:
        _, pid = ctx.principal(r)
        if pid not in actuales:
            g.post(f"{ruta}/$ref", {"@odata.id": odata_id("directoryObjects", pid)}, version="beta")


# ---------------------------------------------------------------- puerta 3: blueprint de IT
def blueprint(ctx: Ctx) -> dict:
    """bp-frasohome-operaciones: blueprint + principal + federated credential sobre la MI id-fs-triage."""
    g = _g(ctx)
    t = ctx.esc["agentes"]["triage"]
    infra = ctx.estado.get("infra") or {}
    mi_principal = infra.get("triageIdentityPrincipalId")
    if not mi_principal:
        raise RuntimeError("Falta la managed identity id-fs-triage: ejecuta antes `agentid infra`.")

    existentes = g.get(f"applications/microsoft.graph.agentIdentityBlueprint?$filter=displayName eq "
                       f"'{t['blueprint']}'&$select=id,appId,displayName")["value"]
    if existentes:
        bp, creado = existentes[0], False
    else:
        bp = g.post("applications", {
            "@odata.type": "Microsoft.Graph.AgentIdentityBlueprint", "displayName": t["blueprint"],
            "sponsors@odata.bind": _binds(ctx, t["blueprint_sponsors"]),
            "owners@odata.bind": _binds(ctx, [r for r in t["blueprint_owners"] if not r.startswith("grupo:")])})
        creado = True
    ctx.estado.registrar("blueprint", bp["id"], creado=creado, appId=bp["appId"], nombre=t["blueprint"])
    print(f"  {'+' if creado else '='} blueprint «{t['blueprint']}» · appId {bp['appId']}")

    principales = g.get(f"servicePrincipals?$filter=appId eq '{bp['appId']}'&$select=id")["value"]
    if principales:
        pid, creado_p = principales[0]["id"], False
    else:
        pid = g.post("servicePrincipals/microsoft.graph.agentIdentityBlueprintPrincipal",
                     {"appId": bp["appId"]}, reintentos_404=6)["id"]
        creado_p = True
    ctx.estado.registrar("blueprint_principal", pid, creado=creado_p)
    print(f"  {'+' if creado_p else '='} blueprint principal {pid}")

    fics = g.todos(f"applications/{bp['id']}/federatedIdentityCredentials", reintentos_404=6)
    if not any(f.get("subject") == mi_principal for f in fics):
        g.post(f"applications/{bp['id']}/federatedIdentityCredentials", {
            "name": "id-fs-triage", "issuer": f"https://login.microsoftonline.com/{ctx.s.tenant_id}/v2.0",
            "subject": mi_principal, "audiences": ["api://AzureADTokenExchange"],
            "description": "Managed identity de ca-fs-triage. Sin secretos."})
        print("  + federated credential → managed identity id-fs-triage")
    else:
        print("  = federated credential → managed identity id-fs-triage")
    return {"id": bp["id"], "appId": bp["appId"]}


def identidad_triage(ctx: Ctx) -> dict:
    """fs-triage-devoluciones: identidad hija del blueprint, Lucía sponsor, David owner, carril Producción."""
    g = _g(ctx)
    t = ctx.esc["agentes"]["triage"]
    bp_app = (ctx.estado.get("blueprint") or {}).get("appId")
    if not bp_app:
        raise RuntimeError("Falta el blueprint: ejecuta antes `agentid blueprint`.")
    candidatas = [i for i in buscar_identidad(ctx, t["nombre"]) if i.get("agentIdentityBlueprintId") == bp_app]
    if candidatas:
        ident, creado = candidatas[0], False
    else:
        ident = g.post(f"servicePrincipals/{CAST}", {
            "displayName": t["nombre"], "agentIdentityBlueprintId": bp_app,
            "sponsors@odata.bind": _binds(ctx, t["sponsors"])}, version="beta", reintentos_404=6)
        creado = True
    cid = client_id(ctx, ident["id"])
    ctx.estado.registrar("identidad:triage", ident["id"], creado=creado, clientId=cid, nombre=t["nombre"])
    print(f"  {'+' if creado else '='} identidad de agente {t['nombre']} · {ident['id']}")
    try:
        anadir_owners(ctx, ident["id"], t["owners"])
        print(f"  = owners: {', '.join(t['owners'])}")
    except GraphError as e:
        print(f"  ⚠ owners no asignados ({e.status} {e.codigo}). Hazlo en Entra → Agent ID → {t['nombre']} → Owners.")
    atributos.asignar(ctx, ident["id"], t["carril"])
    print(f"  = {atributos.definicion_id(ctx)} = {t['carril']}")
    return {"id": ident["id"], "clientId": cid}


# ---------------------------------------------------------------- puerta 1: Copilot Studio
def identidad_copilot(ctx: Ctx) -> str:
    if ctx.s.copilot_agent_identity_id:
        return ctx.s.copilot_agent_identity_id
    guardado = ctx.estado.id("identidad:copilot")
    if guardado:
        return guardado
    nombre = ctx.esc["agentes"]["copilot"]["nombre"]
    res = buscar_identidad(ctx, nombre)
    if len(res) != 1:
        nombres = ", ".join(i["displayName"] for i in res) or "ninguna"
        raise RuntimeError(f"Busco la identidad del agente «{nombre}» y encuentro: {nombres}. "
                           "Pon su object ID en COPILOT_AGENT_IDENTITY_ID (Copilot Studio → Settings → Advanced → Metadata).")
    ctx.estado.registrar("identidad:copilot", res[0]["id"], creado=False, nombre=res[0]["displayName"])
    return res[0]["id"]


def preparar_copilot(ctx: Ctx) -> None:
    """Estado de partida de la demo 1: sponsor Marta R. y carril Producción."""
    c = ctx.esc["agentes"]["copilot"]
    iid = identidad_copilot(ctx)
    nombres = fijar_sponsors(ctx, iid, [c["sponsor_inicial"]])
    print(f"  = {c['nombre']} · sponsors: {', '.join(nombres)}")
    atributos.asignar(ctx, iid, c["carril"])
    print(f"  = {atributos.definicion_id(ctx)} = {c['carril']}")


def eliminar(ctx: Ctx) -> None:
    g = _g(ctx)
    pasos = [("identidad:triage", f"servicePrincipals/{{id}}/{CAST}", "beta"),
             ("blueprint_principal", "servicePrincipals/{id}", "v1.0"),
             ("blueprint", "applications/{id}", "v1.0")]
    for clave, ruta, version in pasos:
        dato = ctx.estado.get(clave)
        if not dato or not ruta or not dato.get("creado"):
            continue
        try:
            g.delete(ruta.format(id=dato["id"]), version=version)
            print(f"  − {clave}")
        except GraphError as e:
            if e.status != 404:
                raise
        ctx.estado.quitar(clave)
