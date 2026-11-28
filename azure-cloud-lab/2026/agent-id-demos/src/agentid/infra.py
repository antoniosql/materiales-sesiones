"""Azure: infraestructura (Bicep), imágenes, datos del caso, Container Apps y RBAC de la identidad de agente."""

from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

from agentid.az import AzError, ambito_contenedor, asignar_rol, az
from agentid.config import RAIZ
from agentid.contexto import Ctx


PROVEEDORES = ("Microsoft.App", "Microsoft.ContainerRegistry", "Microsoft.OperationalInsights",
               "Microsoft.CognitiveServices", "Microsoft.Storage", "Microsoft.ManagedIdentity")


def _salidas(despliegue: dict) -> dict:
    return {k: v["value"] for k, v in (despliegue.get("properties", {}).get("outputs") or {}).items()}


def desplegar(ctx: Ctx) -> None:
    s = ctx.s
    if s.subscription_id:
        az("account", "set", "--subscription", s.subscription_id, salida_json=False)
    # Suscripciones nuevas o de pago por uso: Microsoft.App suele venir sin registrar
    for proveedor in PROVEEDORES:
        if az("provider", "show", "--namespace", proveedor, "--query", "registrationState") != "Registered":
            print(f"  · registrando {proveedor}…")
            az("provider", "register", "--namespace", proveedor, "--wait", salida_json=False)
    existia = az("group", "exists", "--name", s.resource_group)
    az("group", "create", "--name", s.resource_group, "--location", s.location,
       "--tags", "evento=azure-cloud-lab-2026", "escenario=frasohome")
    ctx.estado.registrar("resource_group", s.resource_group, creado=not existia)
    yo = az("ad", "signed-in-user", "show", "--query", "id")
    print(f"  · desplegando infra/main.bicep en {s.resource_group} ({s.location})… (5–10 min)")
    d = az("deployment", "group", "create", "--resource-group", s.resource_group, "--name", "agentid-infra",
           "--template-file", str(RAIZ / "infra" / "main.bicep"),
           "--parameters", f"suffix={s.name_suffix}", f"deployerPrincipalId={yo}",
           f"deployFoundry={'true' if s.deploy_foundry else 'false'}", f"foundryProjectName={s.foundry_project_name}",
           f"modelName={s.foundry_model}", f"modelVersion={s.foundry_model_version}",
           f"modelCapacity={s.foundry_model_capacity}")
    salidas = _salidas(d)
    ctx.estado.poner("infra", salidas)
    for k in ("storageAccountName", "acrLoginServer", "foundryProjectEndpoint"):
        if salidas.get(k):
            print(f"  = {k}: {salidas[k]}")


def datos(ctx: Ctx) -> None:
    infra = ctx.estado.get("infra") or {}
    cuenta = infra["storageAccountName"]
    for fichero in ("devoluciones_online.csv", "productos.csv"):
        ruta = ctx.s.case_data_dir / fichero
        if not ruta.exists():
            raise RuntimeError(f"No encuentro {ruta}: revisa CASE_DATA_DIR.")
        az("storage", "blob", "upload", "--auth-mode", "login", "--account-name", cuenta, "--container-name",
           "devoluciones", "--name", fichero, "--file", str(ruta), "--overwrite", salida_json=False)
        print(f"  + devoluciones/{fichero}")
    correos = json.loads(Path(ctx.s.buzon_json).read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        base = time.time() - len(correos) * 3600
        for i, c in enumerate(correos, start=1):
            c = {**c, "id": f"correo-{i:03d}",
                 "recibido": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(base + i * 3600))}
            Path(tmp, f"correo-{i:03d}.json").write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
        az("storage", "blob", "upload-batch", "--auth-mode", "login", "--account-name", cuenta,
           "--destination", "buzon-devoluciones", "--source", tmp, "--overwrite", salida_json=False)
    print(f"  + buzon-devoluciones/ · {len(correos)} correos")


def vaciar_resultados(ctx: Ctx) -> None:
    cuenta = (ctx.estado.get("infra") or {})["storageAccountName"]
    az("storage", "blob", "delete-batch", "--auth-mode", "login", "--account-name", cuenta,
       "--source", "triage-resultados", salida_json=False)
    print("  − triage-resultados vaciado: el agente volverá a procesar el buzón")


def imagenes(ctx: Ctx) -> None:
    infra = ctx.estado.get("infra") or {}
    acr = infra["acrName"]
    etiqueta = time.strftime("%Y%m%d%H%M")
    imgs = {}
    for app, nombre in (("fs-devoluciones-mcp", "mcp"), ("fs-triage-devoluciones", "triage")):
        print(f"  · az acr build {app}:{etiqueta}…")
        az("acr", "build", "--registry", acr, "--image", f"{app}:{etiqueta}", str(RAIZ / "apps" / app),
           "--no-logs", salida_json=False)
        imgs[nombre] = f"{infra['acrLoginServer']}/{app}:{etiqueta}"
        print(f"  + {imgs[nombre]}")
    ctx.estado.poner("imagenes", imgs)


def rbac_triage(ctx: Ctx) -> None:
    infra = ctx.estado.get("infra") or {}
    ident = ctx.estado.id("identidad:triage")
    if not ident:
        raise RuntimeError("Falta la identidad de agente: ejecuta `agentid identidad`.")
    for r in ctx.esc["agentes"]["triage"]["roles"]:
        asignar_rol(ident, r["rol"], ambito_contenedor(infra["storageAccountId"], r["contenedor"]))
        print(f"  = {r['rol']} sobre «{r['contenedor']}» → {ctx.esc['agentes']['triage']['nombre']}")


def apps(ctx: Ctx) -> None:
    s, infra, imgs = ctx.s, ctx.estado.get("infra") or {}, ctx.estado.get("imagenes") or {}
    triage = ctx.estado.get("identidad:triage") or {}
    bp = ctx.estado.get("blueprint") or {}
    if not (imgs and triage and bp):
        raise RuntimeError("Faltan imágenes, blueprint o identidad: `agentid imagenes`, `blueprint`, `identidad`.")
    print("  · desplegando infra/apps.bicep…")
    d = az("deployment", "group", "create", "--resource-group", s.resource_group, "--name", "agentid-apps",
           "--template-file", str(RAIZ / "infra" / "apps.bicep"), "--parameters",
           f"containerAppsEnvironmentId={infra['containerAppsEnvironmentId']}",
           f"acrLoginServer={infra['acrLoginServer']}", f"pullIdentityId={infra['pullIdentityId']}",
           f"triageIdentityId={infra['triageIdentityId']}",
           f"triageIdentityClientId={infra['triageIdentityClientId']}",
           f"storageAccountName={infra['storageAccountName']}", f"mcpImage={imgs['mcp']}",
           f"triageImage={imgs['triage']}", f"tenantId={s.tenant_id}", f"blueprintAppId={bp['appId']}",
           f"agentIdentityClientId={triage['clientId']}", f"pollSeconds={s.triage_poll_seconds}")
    salidas = _salidas(d)
    ctx.estado.poner("apps", salidas)
    print(f"  = servidor MCP: {salidas.get('mcpUrl')}\n  = agente: {salidas.get('triageAppName')}")


def reiniciar_triage(ctx: Ctx) -> None:
    rg = ctx.s.resource_group
    if _estado_app(rg, "ca-fs-triage") == "Stopped":
        print("  · ca-fs-triage estaba parada (`agentid pausa parar`): la arranco")
        arrancar_apps(ctx)
        return
    revisiones = az("containerapp", "revision", "list", "--name", "ca-fs-triage", "--resource-group", rg,
                    "--query", "[?properties.active].name")
    for rev in revisiones or []:
        az("containerapp", "revision", "restart", "--name", "ca-fs-triage", "--resource-group", rg,
           "--revision", rev, salida_json=False)
        print(f"  ↻ revisión {rev} reiniciada: el agente pedirá un token nuevo")


def logs_triage(ctx: Ctx) -> None:
    print(az("containerapp", "logs", "show", "--name", "ca-fs-triage", "--resource-group", ctx.s.resource_group,
             "--tail", "30", "--format", "text", salida_json=False))


def eliminar(ctx: Ctx) -> None:
    rg = ctx.estado.get("resource_group")
    if rg and rg.get("creado"):
        if ctx.s.subscription_id:
            az("account", "set", "--subscription", ctx.s.subscription_id, salida_json=False)
        az("group", "delete", "--name", rg["id"], "--yes", "--no-wait", salida_json=False)
        print(f"  − grupo de recursos {rg['id']} (borrado en segundo plano)")
    for k in ("resource_group", "infra", "imagenes", "apps", "foundry_conexion", "foundry_agente"):
        ctx.estado.quitar(k)


# ---------------------------------------------------------------- pausa: sin coste entre ensayos
APPS = ("ca-fs-devoluciones-mcp", "ca-fs-triage")


def _accion_app(ctx: Ctx, nombre: str, accion: str) -> None:
    """start/stop por ARM: `az containerapp start|stop` solo existe con la extensión containerapp."""
    sub = ctx.s.subscription_id or az("account", "show", "--query", "id")
    az("rest", "--method", "post", "--url",
       f"https://management.azure.com/subscriptions/{sub}/resourceGroups/{ctx.s.resource_group}/providers/"
       f"Microsoft.App/containerApps/{nombre}/{accion}?api-version=2024-03-01", salida_json=False)


def _estado_app(rg: str, nombre: str) -> str:
    try:
        return az("containerapp", "show", "--name", nombre, "--resource-group", rg,
                  "--query", "properties.runningStatus") or "?"
    except AzError as e:
        if "notfound" in str(e).lower().replace(" ", ""):
            return "no existe"
        raise


def estado_apps(ctx: Ctx) -> None:
    rg = ctx.s.resource_group
    for nombre in APPS:
        print(f"  {nombre:<24} {_estado_app(rg, nombre)}")


def parar_apps(ctx: Ctx) -> None:
    """Para las dos Container Apps: sin réplicas no hay coste de cómputo. La URL del MCP no cambia."""
    rg = ctx.s.resource_group
    if ctx.s.subscription_id:
        az("account", "set", "--subscription", ctx.s.subscription_id, salida_json=False)
    for nombre in APPS:
        if _estado_app(rg, nombre) == "Stopped":
            print(f"  = {nombre} ya estaba parada")
            continue
        _accion_app(ctx, nombre, "stop")
        print(f"  ■ {nombre} parada")
    print("\n  Sigue costando poco: ACR Basic (~0,15 €/día), Storage y Log Analytics. Foundry solo cobra por uso.\n"
          "  Para volver: `agentid pausa arrancar` (o `agentid ensayo reiniciar`, que también las arranca).")


def arrancar_apps(ctx: Ctx) -> None:
    rg = ctx.s.resource_group
    if ctx.s.subscription_id:
        az("account", "set", "--subscription", ctx.s.subscription_id, salida_json=False)
    for nombre in APPS:
        estado = _estado_app(rg, nombre)
        if estado == "no existe":
            raise RuntimeError(f"No existe {nombre} en {rg}: ejecuta `agentid apps`.")
        if estado == "Running":
            print(f"  = {nombre} ya estaba en marcha")
            continue
        _accion_app(ctx, nombre, "start")
        print(f"  ▶ {nombre} arrancada")
    print("  El servidor MCP tarda ~30 s en responder y fs-triage pide un token nuevo al arrancar.")
