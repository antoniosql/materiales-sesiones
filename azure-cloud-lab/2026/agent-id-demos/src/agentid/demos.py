"""Acciones que se ejecutan en directo (o para grabar los clips) y el reinicio entre ensayos."""

from __future__ import annotations

from agentid import agentes, ciclo, foundry, infra
from agentid.az import ambito_contenedor, asignar_rol, comando_rol, quitar_rol
from agentid.contexto import Ctx
from agentid.graph import GraphError

SCOPES_RIESGO = ("IdentityRiskyAgent.ReadWrite.All",)


# ---------------------------------------------------------------- demo 2 · el rol que no viaja
def _ambito_d2(ctx: Ctx) -> str:
    return ambito_contenedor(ctx.estado.get("infra")["storageAccountId"], foundry.CONTENEDOR)


def demo2_comando(ctx: Ctx) -> None:
    """Imprime el comando que se teclea en directo, con los IDs reales."""
    print(comando_rol(foundry.identidad_agente(ctx), foundry.ROL, _ambito_d2(ctx)))


def demo2_arreglar(ctx: Ctx) -> None:
    asignar_rol(foundry.identidad_agente(ctx), foundry.ROL, _ambito_d2(ctx))
    print(f"  + {foundry.ROL} → identidad propia de {ctx.esc['agentes']['foundry']['nombre']} "
          "(la propagación puede tardar unos minutos)")


def demo2_deshacer(ctx: Ctx) -> None:
    quitado = quitar_rol(foundry.identidad_agente(ctx), foundry.ROL, _ambito_d2(ctx))
    print("  − rol retirado de la identidad propia" if quitado else "  = la identidad propia no tenía el rol")


# ---------------------------------------------------------------- demo 4 · cuando se tuerce y cuando Marta se va
def demo4_comprometer(ctx: Ctx) -> None:
    ident = ctx.estado.id("identidad:triage")
    ctx.graph(*SCOPES_RIESGO).post("identityProtection/riskyAgents/confirmCompromised",
                                   {"agentIds": [ident]}, version="beta")
    print(f"  ⚠ {ctx.esc['agentes']['triage']['nombre']} confirmado como comprometido → riesgo alto")
    print("  Siguiente: `agentid demo4 reiniciar` para que pida un token nuevo y CA-AG-01 lo bloquee.")


def demo4_descartar(ctx: Ctx) -> None:
    """Vuelve a dejar el agente sin riesgo. Endpoint por verificar: si falla, hazlo en Risky agents."""
    ident = ctx.estado.id("identidad:triage")
    g = ctx.graph(*SCOPES_RIESGO)
    for accion in ("confirmSafe", "dismiss"):
        try:
            g.post(f"identityProtection/riskyAgents/{accion}", {"agentIds": [ident]}, version="beta")
            print(f"  ✔ riesgo de {ctx.esc['agentes']['triage']['nombre']} limpiado ({accion})")
            return
        except GraphError:
            continue
    print("  ⚠ No he podido limpiar el riesgo por API. Entra → ID Protection → Risky agents → "
          f"{ctx.esc['agentes']['triage']['nombre']} → Confirm safe.")


def demo4_mover(ctx: Ctx) -> None:
    ciclo.ejecutar_para(ctx, "marta")


def demo4_arreglar_sponsors(ctx: Ctx) -> None:
    c = ctx.esc["agentes"]["copilot"]
    nombres = agentes.fijar_sponsors(ctx, agentes.identidad_copilot(ctx), c["sponsors_arreglo"])
    print(f"  ✔ {c['nombre']} · sponsors: {', '.join(nombres)}")


# ---------------------------------------------------------------- estado de partida y ensayo
def estado(ctx: Ctx) -> None:
    """Foto rápida de lo que se va a enseñar."""
    c = ctx.esc["agentes"]["copilot"]
    try:
        print(f"  Puerta 1 · {c['nombre']}: sponsors = "
              f"{', '.join(s.get('displayName') for s in agentes.sponsors(ctx, agentes.identidad_copilot(ctx)))}")
    except Exception as e:  # noqa: BLE001
        print(f"  Puerta 1 · {e}")
    t = ctx.estado.get("identidad:triage") or {}
    print(f"  Puerta 3 · {ctx.esc['agentes']['triage']['nombre']}: {t.get('id', 'sin desplegar')}")
    print(f"  Servidor MCP: {(ctx.estado.get('apps') or {}).get('mcpUrl', 'sin desplegar')}")


def reiniciar_ensayo(ctx: Ctx) -> None:
    """Deja las cuatro demos como al principio, para ensayar o para la sesión. Sigue aunque un paso falle."""
    pasos = [
        ("Demo 1 · sponsor Marta R.", agentes.preparar_copilot),
        ("Demo 2 · rol solo en la identidad compartida", foundry.antes),
        ("Demo 4 · sin riesgo", demo4_descartar),
        ("Demo 3 · buzón pendiente de procesar", infra.vaciar_resultados),
        ("Demo 3/4 · contenedor reiniciado", infra.reiniciar_triage),
    ]
    fallos = 0
    for titulo, paso in pasos:
        print(titulo)
        try:
            paso(ctx)
        except Exception as e:  # noqa: BLE001
            fallos += 1
            print(f"  ✘ {e}")
    print("\n" + ("✔ Listo." if not fallos else f"⚠ {fallos} paso(s) con error: revísalos antes de ensayar.") +
          " El acceso condicional y el riesgo tardan en propagarse: reinicia al menos 30 min antes de la sesión.")
