"""agentid · CLI de las demos de Entra Agent ID (Azure Cloud Lab 2026)."""

from __future__ import annotations

import argparse
import sys

from agentid import acceso, agentes, atributos, check, ciclo, config, demos, foundry, infra, personas
from agentid.contexto import Ctx
from agentid.graph import AYUDA_LICENCIA, GraphError


def _desplegar(ctx: Ctx) -> None:
    pasos = [
        ("Infraestructura (Bicep)", infra.desplegar),
        ("Personas y grupos", personas.desplegar),
        ("Atributo FraSoHome.Carril", atributos.desplegar),
        ("Datos del caso y buzón", infra.datos),
        ("Puerta 3 · blueprint de IT", agentes.blueprint),
        ("Puerta 3 · identidad de agente", agentes.identidad_triage),
        ("Puerta 3 · RBAC mínimo", infra.rbac_triage),
        ("Imágenes de contenedor", infra.imagenes),
        ("Container Apps", infra.apps),
        ("Puerta 2 · conexión MCP en Foundry", foundry.conexion),
        ("Puerta 2 · agente frasohome-returns", foundry.agente),
        ("Acceso condicional", acceso.desplegar),
        ("Ciclo de vida", ciclo.desplegar),
    ]
    for i, (titulo, paso) in enumerate(pasos, start=1):
        print(f"\n[{i}/{len(pasos)}] {titulo}")
        paso(ctx)
    print("\nQueda a mano (ver DESPLIEGUE.md):\n"
          "  1. Crear el Asistente de Devoluciones en Copilot Studio y luego `agentid copilot`.\n"
          "  2. `agentid foundry identidades` → FOUNDRY_SHARED_IDENTITY_ID en .env → `agentid foundry antes`.\n"
          "  3. Activar la política de inactividad por defecto y las licencias.\n"
          "  4. `agentid ensayo reiniciar` antes de cada ensayo.")


def _cleanup(ctx: Ctx, args) -> None:
    if not args.si:
        print("Esto borra todo lo que crearon estos scripts (usuarios, grupos, blueprint, políticas, grupo de recursos).\n"
              "Repite con --si para confirmar.")
        return
    fallos = 0
    for paso in (acceso.eliminar, ciclo.eliminar, foundry.eliminar, agentes.eliminar, personas.eliminar, infra.eliminar):
        try:
            paso(ctx)
        except Exception as e:  # noqa: BLE001 — sigue con el resto: cada paso solo borra lo suyo
            fallos += 1
            ayuda = f"\n{AYUDA_LICENCIA}" if isinstance(e, GraphError) and e.sin_licencia else ""
            print(f"  ✘ {paso.__module__.split('.')[-1]}: {e}{ayuda}")
    if fallos:
        print(f"\n⚠ {fallos} paso(s) con error. Repite `agentid cleanup --si`: lo ya borrado se salta.")
    print("\nEl atributo FraSoHome.Carril no se puede borrar (Entra solo permite desactivarlo) y el agente de Copilot "
          "Studio y el de Foundry se borran desde sus portales.")


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="agentid", description=__doc__)
    p.add_argument("--env", help="ruta del .env (por defecto, el de la raíz)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="comprueba requisitos").add_argument("--sin-graph", action="store_true")
    sub.add_parser("desplegar", help="todo, en orden")
    sub.add_parser("infra", help="infraestructura Azure (infra/main.bicep)")
    sub.add_parser("personas", help="usuarios y grupos de M365")
    sub.add_parser("atributos", help="atributo de seguridad FraSoHome.Carril")
    sub.add_parser("datos", help="sube CSV del caso y correos del buzón")
    sub.add_parser("blueprint", help="puerta 3: blueprint de IT con federated credential")
    sub.add_parser("identidad", help="puerta 3: identidad fs-triage-devoluciones")
    sub.add_parser("rbac", help="puerta 3: roles de datos de la identidad de agente")
    sub.add_parser("imagenes", help="az acr build de las dos apps")
    sub.add_parser("apps", help="Container Apps (infra/apps.bicep)")
    sub.add_parser("copilot", help="puerta 1: sponsor Marta y carril del Asistente de Devoluciones")
    f = sub.add_parser("foundry", help="puerta 2").add_subparsers(dest="accion", required=True)
    f.add_parser("identidades", help="lista identidades del proyecto y del agente")
    f.add_parser("conexion", help="conexión MCP con identidad de agente")
    f.add_parser("agente", help="crea frasohome-returns con la herramienta MCP")
    f.add_parser("antes", help="estado de partida de la demo 2")
    pr = f.add_parser("preguntar", help="lanza la pregunta de la demo")
    pr.add_argument("pregunta", nargs="?")
    sub.add_parser("acceso", help="CA-AG-01 y CA-AG-02")
    sub.add_parser("ciclo", help="workflow LW-Mover-Sponsors")
    d2 = sub.add_parser("demo2", help="demo 2 en directo").add_subparsers(dest="accion", required=True)
    for a in ("comando", "arreglar", "deshacer"):
        d2.add_parser(a)
    d4 = sub.add_parser("demo4", help="demo 4 en directo").add_subparsers(dest="accion", required=True)
    for a in ("comprometer", "reiniciar", "logs", "mover", "sponsors", "descartar"):
        d4.add_parser(a)
    en = sub.add_parser("ensayo", help="estado y reinicio entre ensayos").add_subparsers(dest="accion", required=True)
    en.add_parser("estado")
    en.add_parser("reiniciar")
    sub.add_parser("cleanup", help="borra lo creado por estos scripts").add_argument("--si", action="store_true")

    for flujo in (sys.stdout, sys.stderr):  # consolas de Windows sin UTF-8
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", errors="replace")
    args = p.parse_args(argv)
    ctx = Ctx.crear(config.cargar(args.env))

    acciones = {
        "desplegar": lambda: _desplegar(ctx),
        "infra": lambda: infra.desplegar(ctx),
        "personas": lambda: personas.desplegar(ctx),
        "atributos": lambda: atributos.desplegar(ctx),
        "datos": lambda: infra.datos(ctx),
        "blueprint": lambda: agentes.blueprint(ctx),
        "identidad": lambda: agentes.identidad_triage(ctx),
        "rbac": lambda: infra.rbac_triage(ctx),
        "imagenes": lambda: infra.imagenes(ctx),
        "apps": lambda: infra.apps(ctx),
        "copilot": lambda: agentes.preparar_copilot(ctx),
        "acceso": lambda: acceso.desplegar(ctx),
        "ciclo": lambda: ciclo.desplegar(ctx),
        "cleanup": lambda: _cleanup(ctx, args),
        "check": lambda: sys.exit(0 if check.comprobar(ctx, graph=not args.sin_graph) else 1),
    }
    sub_acciones = {
        "foundry": {"identidades": foundry.identidades, "conexion": foundry.conexion, "agente": foundry.agente,
                    "antes": foundry.antes, "preguntar": lambda c: foundry.preguntar(c, args.pregunta)},
        "demo2": {"comando": demos.demo2_comando, "arreglar": demos.demo2_arreglar, "deshacer": demos.demo2_deshacer},
        "demo4": {"comprometer": demos.demo4_comprometer, "reiniciar": infra.reiniciar_triage,
                  "logs": infra.logs_triage, "mover": demos.demo4_mover, "sponsors": demos.demo4_arreglar_sponsors,
                  "descartar": demos.demo4_descartar},
        "ensayo": {"estado": demos.estado, "reiniciar": demos.reiniciar_ensayo},
    }
    try:
        if args.cmd in sub_acciones:
            sub_acciones[args.cmd][args.accion](ctx)
        else:
            acciones[args.cmd]()
    except RuntimeError as e:
        print(f"\n✘ {e}", file=sys.stderr)
        if isinstance(e, GraphError) and e.sin_licencia:
            print(AYUDA_LICENCIA, file=sys.stderr)
        sys.exit(1)
