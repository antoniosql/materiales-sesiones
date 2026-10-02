"""fs-triage-devoluciones — triaje del buzón de devoluciones de FraSoHome.

Construido con el Claude Agent SDK. Lee devoluciones@frasohome.es, clasifica
cada entrada por motivo, detecta patrones anómalos y redacta un resumen diario
para el Store Manager.

Estado en el que arranca la demo 4: funciona, lleva semanas funcionando, y no
aparece en ningún inventario. Sin Entra Agent ID, sin telemetría, sin
propietario declarado. Eso es lo que se enseña primero.

Después, en vivo:

    "añade observabilidad a este agente"      -> instrument-observability
    "conecta Mail y Word a través de Work IQ" -> add-workiq-tools

Las skills son aditivas: no reescriben este archivo, lo instrumentan. Ese diff
es media demo, así que conviene tener el repositorio limpio antes de empezar.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    create_sdk_mcp_server,
    tool,
)

from dotenv import load_dotenv

from buzon import Mensaje, crear_buzon

load_dotenv()

MOTIVOS = {
    "R01": "Arrepentimiento o cambio de opinión",
    "R02": "Producto excluido de devolución",
    "R03": "Producto defectuoso o incompleto",
    "R04": "Daño en transporte",
}

UMBRAL_PATRON = 3  # devoluciones del mismo remitente que ya merecen una mirada

_buzon = crear_buzon()
_cache: dict[str, Mensaje] = {}


# ------------------------------------------------------------------ tools
@tool(
    "listar_bandeja",
    "Lista los mensajes recientes del buzón de devoluciones con su id, remitente y asunto.",
    {"limite": int},
)
async def listar_bandeja(args: dict) -> dict:
    limite = int(args.get("limite") or 25)
    mensajes = _buzon.listar(limite=limite)
    for m in mensajes:
        _cache[m.id] = m
    lineas = [f"{m.id} | {m.resumen_corto()}" for m in mensajes]
    return {
        "content": [
            {"type": "text", "text": f"{len(mensajes)} mensajes:\n" + "\n".join(lineas)}
        ]
    }


@tool(
    "leer_mensaje",
    "Devuelve el cuerpo completo de un mensaje del buzón a partir de su id.",
    {"mensaje_id": str},
)
async def leer_mensaje(args: dict) -> dict:
    mensaje_id = args["mensaje_id"]
    mensaje = _cache.get(mensaje_id) or _buzon.leer(mensaje_id)
    _cache[mensaje_id] = mensaje
    texto = (
        f"De: {mensaje.remitente}\n"
        f"Recibido: {mensaje.recibido:%d/%m/%Y %H:%M}\n"
        f"Asunto: {mensaje.asunto}\n\n"
        f"{mensaje.cuerpo}"
    )
    return {"content": [{"type": "text", "text": texto}]}


@tool(
    "detectar_patrones",
    "Busca remitentes con varias devoluciones en pocos días, que es lo que interesa a Prevención de Pérdidas.",
    {"dias": int},
)
async def detectar_patrones(args: dict) -> dict:
    dias = int(args.get("dias") or 14)
    corte = datetime.now(timezone.utc) - timedelta(days=dias)
    mensajes = _buzon.listar(limite=100)

    por_remitente: dict[str, list[Mensaje]] = defaultdict(list)
    for m in mensajes:
        if m.recibido >= corte:
            por_remitente[m.remitente].append(m)

    sospechosos = {
        remitente: msgs
        for remitente, msgs in por_remitente.items()
        if len(msgs) >= UMBRAL_PATRON
    }
    if not sospechosos:
        return {
            "content": [
                {"type": "text", "text": f"Sin patrones por encima de {UMBRAL_PATRON} en {dias} días."}
            ]
        }

    lineas = []
    for remitente, msgs in sorted(sospechosos.items(), key=lambda kv: -len(kv[1])):
        asuntos = "; ".join(m.asunto for m in msgs[:4])
        lineas.append(f"- {remitente}: {len(msgs)} mensajes en {dias} días. {asuntos}")
    return {"content": [{"type": "text", "text": "\n".join(lineas)}]}


@tool(
    "guardar_resumen",
    "Guarda el resumen diario en disco para el Store Manager.",
    {"contenido": str},
)
async def guardar_resumen(args: dict) -> dict:
    destino = Path("salida") / f"resumen-{datetime.now():%Y-%m-%d}.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(args["contenido"], encoding="utf-8")
    return {"content": [{"type": "text", "text": f"Resumen guardado en {destino}"}]}


herramientas = create_sdk_mcp_server(
    name="frasohome-devoluciones",
    version="1.0.0",
    tools=[listar_bandeja, leer_mensaje, detectar_patrones, guardar_resumen],
)


INSTRUCCIONES = f"""Eres el agente de triaje de devoluciones de FraSoHome.

Tu trabajo diario, en este orden:

1. Lista la bandeja del buzón de devoluciones.
2. Lee cada mensaje que no hayas clasificado todavía.
3. Clasifica cada uno con uno de estos motivos:
{chr(10).join(f"   {k} — {v}" for k, v in MOTIVOS.items())}
4. Ejecuta la detección de patrones.
5. Redacta un resumen para el Store Manager y guárdalo.

El resumen tiene tres partes y ninguna más:

**Hoy**: cuántas solicitudes han entrado y su reparto por motivo.
**Requiere decisión**: los casos que no puede resolver el flujo estándar
(producto excluido, fuera de plazo, sin ticket, importe alto).
**Prevención de Pérdidas**: los patrones detectados, con el remitente y el
número de mensajes. No propongas tú la resolución: solo señala.

Reglas:

- No inventes números de pedido ni de devolución. Si un mensaje no lo da, dilo.
- No incluyas cuentas bancarias, teléfonos ni direcciones postales en el resumen.
- Sé escueto. El Store Manager lo lee entre cliente y cliente.
"""


async def ejecutar(prompt: str, verbose: bool = False) -> int:
    opciones = ClaudeAgentOptions(
        system_prompt=INSTRUCCIONES,
        mcp_servers={"devoluciones": herramientas},
        allowed_tools=[
            "mcp__devoluciones__listar_bandeja",
            "mcp__devoluciones__leer_mensaje",
            "mcp__devoluciones__detectar_patrones",
            "mcp__devoluciones__guardar_resumen",
        ],
        max_turns=30,
        # En Windows el SDK necesita un claude.exe nativo; el de la extensión de VS Code sirve.
        cli_path=os.environ.get("CLAUDE_CLI_PATH") or None,
    )

    async with ClaudeSDKClient(options=opciones) as cliente:
        await cliente.query(prompt)
        async for mensaje in cliente.receive_response():
            for bloque in getattr(mensaje, "content", []) or []:
                texto = getattr(bloque, "text", None)
                if texto:
                    print(texto, end="", flush=True)
                elif verbose and getattr(bloque, "name", None):
                    print(f"\n  [tool] {bloque.name}", file=sys.stderr)
    print()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Triaje del buzón de devoluciones de FraSoHome"
    )
    parser.add_argument(
        "--prompt",
        default="Haz el triaje de hoy y guarda el resumen.",
        help="Instrucción para esta ejecución.",
    )
    parser.add_argument("--verbose", action="store_true", help="Muestra las llamadas a herramientas.")
    args = parser.parse_args()
    return asyncio.run(ejecutar(args.prompt, verbose=args.verbose))


if __name__ == "__main__":
    raise SystemExit(main())
