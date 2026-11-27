"""Personas y grupos del escenario: Jorge, Álvaro, Lucía, Marta y David, y los dos grupos de M365."""

from __future__ import annotations

import secrets
import string

from agentid.contexto import Ctx
from agentid.graph import GraphError, odata_id

SCOPES = ("User.ReadWrite.All", "Group.ReadWrite.All")


def _password() -> str:
    alfabeto = string.ascii_letters + string.digits + "!#%+-_"
    while True:
        p = "".join(secrets.choice(alfabeto) for _ in range(18))
        if any(c.islower() for c in p) and any(c.isupper() for c in p) and any(c.isdigit() for c in p):
            return p


def desplegar(ctx: Ctx) -> None:
    g = ctx.graph(*SCOPES)
    esc = ctx.esc
    for clave, p in esc["personas"].items():
        upn = ctx.s.upn(p["alias"])
        cuerpo = {"displayName": p["nombre"], "jobTitle": p["puesto"], "department": p["departamento"],
                  "companyName": esc["empresa"], "usageLocation": ctx.s.usage_location}
        existente = g.existe(f"users/{upn}?$select=id")
        if existente:
            g.patch(f"users/{existente['id']}", cuerpo)
            ctx.estado.registrar(f"usuario:{clave}", existente["id"], creado=False, upn=upn)
            print(f"  = {p['nombre']:<12} {upn} (ya existía, actualizado)")
            continue
        password = ctx.s.demo_user_password or _password()
        nuevo = g.post("users", {**cuerpo, "accountEnabled": True, "userPrincipalName": upn,
                                 "mailNickname": p["alias"].replace(".", ""),
                                 "passwordProfile": {"password": password,
                                                     "forceChangePasswordNextSignIn": False}})
        ctx.estado.registrar(f"usuario:{clave}", nuevo["id"], creado=True, upn=upn)
        aviso = "" if ctx.s.demo_user_password else f" · contraseña: {password}"
        print(f"  + {p['nombre']:<12} {upn}{aviso}")

    for clave, p in esc["personas"].items():
        if p.get("manager"):
            uid, mid = ctx.usuario_id(clave), ctx.usuario_id(p["manager"])
            g.put(f"users/{uid}/manager/$ref", {"@odata.id": odata_id("users", mid)}, reintentos_404=6)
            print(f"  → manager de {p['nombre']}: {esc['personas'][p['manager']]['nombre']}")

    admin = ctx.usuario_id("admin")
    for clave, gr in esc["grupos"].items():
        miembros = [ctx.usuario_id(m) for m in gr["miembros"]]
        res = g.get(f"groups?$filter=mailNickname eq '{gr['alias']}'&$select=id")["value"]
        if res:
            gid, creado = res[0]["id"], False
        else:
            nuevo = g.post("groups", {
                "displayName": gr["nombre"], "mailNickname": gr["alias"], "mailEnabled": True,
                "securityEnabled": False, "groupTypes": ["Unified"], "visibility": "Private",
                "owners@odata.bind": [odata_id("users", admin)],
                "members@odata.bind": [odata_id("users", m) for m in miembros]})
            gid, creado = nuevo["id"], True
        ctx.estado.registrar(f"grupo:{clave}", gid, creado=creado, nombre=gr["nombre"])
        actuales = {m["id"] for m in g.todos(f"groups/{gid}/members?$select=id", reintentos_404=6)}
        for m in miembros:
            if m not in actuales:
                try:
                    g.post(f"groups/{gid}/members/$ref", {"@odata.id": odata_id("directoryObjects", m)})
                except GraphError as e:
                    if "already exist" not in e.mensaje:
                        raise
        print(f"  {'+' if creado else '='} grupo {gr['nombre']} ({len(miembros)} miembros)")
    print("\n⚠ Licencias: asigna a Lucía y a Jorge una licencia con Exchange Online (correos de la demo 4)\n"
          "  y a todos los usuarios de Agent ID que lo necesiten la licencia de Agent 365. Ver DESPLIEGUE.md.")


def eliminar(ctx: Ctx) -> None:
    g = ctx.graph(*SCOPES)
    for clave in list(ctx.estado.datos):
        if clave.startswith(("usuario:", "grupo:")) and ctx.estado.datos[clave].get("creado"):
            tipo = "users" if clave.startswith("usuario:") else "groups"
            try:
                g.delete(f"{tipo}/{ctx.estado.id(clave)}")
                print(f"  − {clave}")
            except GraphError as e:
                if e.status != 404:
                    raise
            ctx.estado.quitar(clave)
