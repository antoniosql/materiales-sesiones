# Crear el agente externo `fs-triage-devoluciones`, paso a paso

Agente de triaje del buzón de devoluciones de FraSoHome, construido con **Claude Agent SDK** en
Python. Es el protagonista de la **demo 4**: funciona, hace un trabajo útil y no aparece en ningún
inventario de Microsoft 365.

Esta guía sirve para dos cosas:

- **Ponerlo en marcha** en un equipo nuevo a partir del repositorio (pasos 1, 7 a 11).
- **Construirlo desde cero**, fichero a fichero (pasos 1 a 11).

Tiempo: unos 30 minutos desde cero, 10 si ya tienes el repositorio. Todo está probado en Windows 11
con Python 3.14.8, `claude-agent-sdk` 0.2.163 y Claude Code 2.1.287.

---

## Qué vas a construir

```text
python src/agent.py
   │
   ├─ Claude Agent SDK ──► claude.exe ──► modelo de Claude
   │        │
   │        └─ servidor MCP en el propio proceso con cuatro herramientas:
   │             listar_bandeja · leer_mensaje · detectar_patrones · guardar_resumen
   │
   └─ buzón ──► BUZON_ORIGEN=local  → demos/datos/buzon/correos.json (18 correos)
            └─► BUZON_ORIGEN=graph  → buzón compartido real de Exchange (opcional)
```

El agente lista la bandeja, lee cada correo, lo clasifica con un motivo (R01 a R04), detecta
remitentes con varias devoluciones y guarda un resumen para el Store Manager en `salida/`.

> **Lo que le falta, a propósito:** identidad en Entra, telemetría y propietario declarado. Accede al
> correo con credenciales propias en un `.env`. Eso es lo que la demo 4 enseña primero.

---

## 1. Requisitos

| Necesitas | Para qué | Cómo comprobarlo |
|---|---|---|
| Python 3.10 o superior | Ejecutar el agente | `python --version` |
| Claude Code (extensión de VS Code) con sesión iniciada | Aporta `claude.exe` y las credenciales que usa el SDK | Abre el panel de Claude Code en VS Code y escribe algo |
| Git | Dejar el repositorio limpio antes de la demo | `git --version` |
| VS Code | Enseñar el código y el diff en la sala | |

> **Sin sesión en Claude Code** también funciona: rellena `ANTHROPIC_API_KEY` en el `.env` (paso 8).

---

## 2. Crea la estructura

Si ya tienes el repositorio, salta al paso 7. Si no, crea esto dentro de `demos/agente-externo/`:

```text
demos/
├─ datos/
│  └─ buzon/
│     └─ correos.json            ← los 18 correos de prueba (paso 6)
└─ agente-externo/
   └─ fs-triage-devoluciones/
      ├─ .env.example
      ├─ .gitignore
      ├─ requirements.txt
      └─ src/
         ├─ buzon.py
         └─ agent.py
```

```powershell
New-Item -ItemType Directory -Force demos\agente-externo\fs-triage-devoluciones\src
New-Item -ItemType Directory -Force demos\datos\buzon
Set-Location demos\agente-externo\fs-triage-devoluciones
```

> La ubicación importa: `buzon.py` busca `correos.json` tres carpetas por encima de `src/`, en
> `demos/datos/buzon/`. Si lo pones en otro sitio, indica la ruta en `BUZON_FICHERO` (paso 8).

---

## 3. Dependencias y ficheros ignorados

**`requirements.txt`**: el SDK, un cliente HTTP para Graph y la lectura del `.env`.

```text
claude-agent-sdk>=0.1.0
httpx>=0.27
python-dotenv>=1.0
```

**`.gitignore`**: el `.env` lleva credenciales y nunca se sube.

```text
.env
salida/
__pycache__/
*.pyc
.venv/
```

---

## 4. El buzón: `src/buzon.py`

Un mismo interfaz (`listar` y `leer`) con dos implementaciones:

| Clase | Lee de | Cuándo |
|---|---|---|
| `BuzonLocal` | `correos.json`, repartiendo los correos en la última semana (uno cada 9 horas) para que la detección de patrones encuentre algo | En la sala y en los ensayos |
| `BuzonDevoluciones` | Microsoft Graph, con un registro de aplicación y su secreto | Solo si tienes el buzón real |

`crear_buzon()` elige una u otra según `BUZON_ORIGEN`. Por defecto, `local`.

<details>
<summary>Código completo de <code>src/buzon.py</code></summary>

```python
"""Acceso al buzón de devoluciones.

Ahora mismo, con credenciales propias en un .env. Ese es el punto de partida
de la demo 4: el agente funciona, pero su acceso al correo de FraSoHome no lo
ve, ni lo audita, ni lo puede cortar ningún administrador.

El beat 2 de la demo sustituye esto por los servidores MCP gobernados de
Work IQ, y entonces el mismo acceso pasa a estar bajo control del admin.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

GRAPH = "https://graph.microsoft.com/v1.0"
_RAIZ_DEMOS = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Mensaje:
    id: str
    asunto: str
    remitente: str
    recibido: datetime
    cuerpo: str

    def resumen_corto(self) -> str:
        return f"[{self.recibido:%d/%m %H:%M}] {self.remitente} — {self.asunto}"


class BuzonDevoluciones:
    """Cliente mínimo de Graph para un buzón compartido."""

    def __init__(self) -> None:
        self.tenant_id = _requerido("AZURE_TENANT_ID")
        self.client_id = _requerido("AZURE_CLIENT_ID")
        self.client_secret = _requerido("AZURE_CLIENT_SECRET")
        self.buzon = _requerido("BUZON_DEVOLUCIONES")
        self._token: str | None = None
        self._token_expira = datetime.now(timezone.utc)

    def _acceso(self) -> str:
        if self._token and datetime.now(timezone.utc) < self._token_expira:
            return self._token
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        datos = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }
        respuesta = httpx.post(url, data=datos, timeout=30)
        respuesta.raise_for_status()
        payload = respuesta.json()
        self._token = payload["access_token"]
        self._token_expira = datetime.now(timezone.utc) + timedelta(
            seconds=payload.get("expires_in", 3600) - 120
        )
        return self._token

    def listar(self, limite: int = 25) -> list[Mensaje]:
        url = f"{GRAPH}/users/{self.buzon}/mailFolders/inbox/messages"
        parametros = {
            "$top": str(limite),
            "$select": "id,subject,from,receivedDateTime,bodyPreview",
            "$orderby": "receivedDateTime desc",
        }
        respuesta = httpx.get(
            url,
            params=parametros,
            headers={"Authorization": f"Bearer {self._acceso()}"},
            timeout=30,
        )
        respuesta.raise_for_status()
        return [_a_mensaje(m) for m in respuesta.json().get("value", [])]

    def leer(self, mensaje_id: str) -> Mensaje:
        url = f"{GRAPH}/users/{self.buzon}/messages/{mensaje_id}"
        respuesta = httpx.get(
            url,
            params={"$select": "id,subject,from,receivedDateTime,body"},
            headers={"Authorization": f"Bearer {self._acceso()}"},
            timeout=30,
        )
        respuesta.raise_for_status()
        return _a_mensaje(respuesta.json())


class BuzonLocal:
    """El mismo buzón, servido desde datos/buzon/correos.json.

    Para ensayar y para la sala sin depender de Exchange: mismas 18 reclamaciones
    que se sembrarían en el buzón real, repartidas en los últimos días para que
    la detección de patrones encuentre el caso anómalo.
    """

    def __init__(self, ruta: Path | None = None) -> None:
        ruta = ruta or Path(
            os.environ.get("BUZON_FICHERO") or _RAIZ_DEMOS / "datos" / "buzon" / "correos.json"
        )
        brutos = json.loads(ruta.read_text(encoding="utf-8"))
        ahora = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        self._mensajes = [
            Mensaje(
                id=f"local-{i:03d}",
                asunto=b.get("asunto", "(sin asunto)"),
                remitente=b.get("remitente", "desconocido"),
                # El más reciente primero, uno cada ~9 horas: 18 correos en una semana.
                recibido=ahora - timedelta(hours=9 * i),
                cuerpo=b.get("cuerpo", "").strip(),
            )
            for i, b in enumerate(brutos, start=1)
        ]

    def listar(self, limite: int = 25) -> list[Mensaje]:
        return self._mensajes[:limite]

    def leer(self, mensaje_id: str) -> Mensaje:
        for m in self._mensajes:
            if m.id == mensaje_id:
                return m
        raise KeyError(f"No existe el mensaje {mensaje_id}")


def crear_buzon() -> BuzonDevoluciones | BuzonLocal:
    """BUZON_ORIGEN=graph usa Exchange con las credenciales del .env; cualquier otro valor, el fichero local."""
    if os.environ.get("BUZON_ORIGEN", "local").lower() == "graph":
        return BuzonDevoluciones()
    return BuzonLocal()


def _a_mensaje(bruto: dict) -> Mensaje:
    direccion = (
        bruto.get("from", {}).get("emailAddress", {}).get("address")
        or bruto.get("from", {}).get("emailAddress", {}).get("name")
        or "desconocido"
    )
    cuerpo = bruto.get("bodyPreview") or bruto.get("body", {}).get("content", "")
    return Mensaje(
        id=bruto["id"],
        asunto=bruto.get("subject", "(sin asunto)"),
        remitente=direccion,
        recibido=datetime.fromisoformat(
            bruto["receivedDateTime"].replace("Z", "+00:00")
        ),
        cuerpo=cuerpo.strip(),
    )


def _requerido(nombre: str) -> str:
    valor = os.environ.get(nombre)
    if not valor:
        raise RuntimeError(
            f"Falta la variable de entorno {nombre}. Copia .env.example a .env y rellénalo."
        )
    return valor
```

</details>

---

## 5. El agente: `src/agent.py`

Las piezas, en el orden en que aparecen en el fichero:

1. **Las cuatro herramientas**, cada una con el decorador `@tool(nombre, descripción, esquema)`.
   Devuelven `{"content": [{"type": "text", "text": ...}]}`, que es lo que el SDK espera.
   - `listar_bandeja`: los últimos mensajes con id, fecha, remitente y asunto.
   - `leer_mensaje`: el cuerpo de un mensaje por su id.
   - `detectar_patrones`: remitentes con 3 o más mensajes en los últimos N días (`UMBRAL_PATRON`).
   - `guardar_resumen`: escribe `salida/resumen-AAAA-MM-DD.md`.
2. **`create_sdk_mcp_server`** las publica como un servidor MCP que vive dentro del propio proceso.
   No hay que arrancar nada aparte.
3. **`INSTRUCCIONES`**: el prompt de sistema. Orden de trabajo, los cuatro motivos y el formato del
   resumen (Hoy · Requiere decisión · Prevención de Pérdidas). Prohíbe incluir cuentas, teléfonos o
   direcciones.
4. **`ClaudeAgentOptions`**: prompt de sistema, el servidor MCP, `allowed_tools` (solo esas cuatro
   herramientas, con el prefijo `mcp__devoluciones__`), `max_turns=30` y `cli_path`, la ruta a
   `claude.exe`.
5. **`ClaudeSDKClient`** envía la instrucción y va imprimiendo lo que responde. Con `--verbose`
   muestra también cada llamada a herramienta.

<details>
<summary>Código completo de <code>src/agent.py</code></summary>

```python
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
```

</details>

---

## 6. Los datos del buzón: `demos/datos/buzon/correos.json`

Una lista de 18 correos. Cada uno con estos campos:

```json
{
  "remitente": "lucia.beltran@example.com",
  "nombre": "Lucía Beltrán",
  "asunto": "Devolución sofá Nordic 3 plazas — pedido FS-ON-20418",
  "motivo": "R01",
  "tienda": "Online",
  "cuerpo": "Buenos días. Compré el sofá Nordic de 3 plazas el 20 de agosto..."
}
```

El reparto que trae el fichero: 10 de R01, 4 de R02, 2 de R03 y 2 de R04. Cuatro son del mismo
remitente, `hectorvidal@example.com`: es el patrón anómalo que tiene que encontrar el agente.
El campo `motivo` no se le pasa al agente; está para comprobar su clasificación.

---

## 7. Crea el entorno virtual e instala

Desde la carpeta `fs-triage-devoluciones`:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Comprueba que el SDK está:

```powershell
.\.venv\Scripts\python -c "import claude_agent_sdk; print(claude_agent_sdk.__version__)"
```

---

## 8. Configura el `.env`

**8.1 · Localiza `claude.exe`.** En Windows el SDK necesita un ejecutable nativo y rechaza el
`claude.cmd` que instala npm. El de la extensión de VS Code sirve:

```powershell
Get-ChildItem "$env:USERPROFILE\.vscode\extensions" -Recurse -Filter claude.exe |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
```

**8.2 · Plantilla.** Crea `.env.example` con este contenido:

```text
# Credenciales propias del agente. Este archivo es, literalmente, el problema
# que la demo 4 resuelve: acceso al correo de FraSoHome que ningun administrador
# ve ni puede cortar. Despues del beat 2, el acceso pasa por Work IQ.

# Opcional si Claude Code ya tiene sesion iniciada en este equipo.
ANTHROPIC_API_KEY=

# Windows: ruta a un claude.exe nativo. El de la extensión de VS Code sirve, p. ej.
# C:\Users\<usuario>\.vscode\extensions\anthropic.claude-code-<versión>-win32-x64\resources\native-binary\claude.exe
CLAUDE_CLI_PATH=

# local = lee datos/buzon/correos.json (lo que se usa en la sala)
# graph = lee el buzon real de Exchange con las credenciales de abajo
BUZON_ORIGEN=local

AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=

BUZON_DEVOLUCIONES=devoluciones@frasohome.es
```

**8.3 · Crea tu `.env`** a partir de la plantilla, con la ruta de `claude.exe` ya puesta.
Hazlo con este bloque de PowerShell: editar la ruta a mano con `sed` u otras herramientas suele
estropear las barras invertidas.

```powershell
$ruta = Get-ChildItem "$env:USERPROFILE\.vscode\extensions" -Recurse -Filter claude.exe |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
$lineas = Get-Content .env.example -Encoding UTF8 | ForEach-Object {
    if ($_ -like 'CLAUDE_CLI_PATH=*') { "CLAUDE_CLI_PATH=$ruta" } else { $_ }
}
[IO.File]::WriteAllLines("$PWD\.env", $lineas)
Select-String -Path .env -Pattern 'CLAUDE_CLI_PATH|BUZON_ORIGEN'
```

| Variable | Valor para la sala |
|---|---|
| `CLAUDE_CLI_PATH` | La ruta del paso 8.1 |
| `BUZON_ORIGEN` | `local` |
| `ANTHROPIC_API_KEY` | Vacía si Claude Code tiene sesión; si no, tu clave |
| `BUZON_FICHERO` | Opcional: otra ruta para `correos.json` |
| `AZURE_*`, `BUZON_DEVOLUCIONES` | Solo para el modo `graph` (paso 13) |

---

## 9. Primera prueba, sin llamar al modelo

Comprueba el buzón y la detección de patrones. No gasta nada:

```powershell
Set-Location src
$env:PYTHONIOENCODING = "utf-8"
..\.venv\Scripts\python -c "from buzon import crear_buzon; b = crear_buzon(); m = b.listar(100); print(type(b).__name__, len(m)); print(m[0].resumen_corto())"
Set-Location ..
```

Esperado:

```text
BuzonLocal 18
[02/10 04:00] lucia.beltran@example.com — Devolución sofá Nordic 3 plazas — pedido FS-ON-20418
```

La fecha y la hora cambian: se calculan desde el momento en que lo ejecutas.

---

## 10. Primera ejecución con el modelo

Una tarea corta, para comprobar que el SDK encuentra `claude.exe` y tiene credenciales:

```powershell
.\.venv\Scripts\python src\agent.py --verbose --prompt "Ejecuta solo la detección de patrones de los últimos 14 días y dime en una frase qué remitente destaca. No guardes resumen."
```

Esperado, en menos de un minuto:

```text
  [tool] mcp__devoluciones__detectar_patrones
En los últimos 14 días destaca hectorvidal@example.com, con 4 mensajes de devolución...
```

---

## 11. El triaje completo

```powershell
.\.venv\Scripts\python src\agent.py --verbose
```

Tarda un par de minutos: lee los 18 correos uno a uno. Al terminar, abre
`salida\resumen-AAAA-MM-DD.md`. Debe tener tres partes:

- **Hoy**: 18 solicitudes y su reparto por motivo, cerca del 10 / 4 / 2 / 2 del fichero.
- **Requiere decisión**: productos excluidos, fuera de plazo, sin ticket.
- **Prevención de Pérdidas**: `hectorvidal@example.com` con 4 mensajes.

Y ningún número de cuenta, teléfono ni dirección.

> **Para la sala**, genera este resumen la víspera y enséñalo ya hecho. Ejecutarlo en directo son dos
> minutos de espera.

---

## 12. Prepara la demo 4

**12.1 · Haz commit del agente tal como debe llegar a la sala.** Sin observabilidad ni registro.

```powershell
git add -- .
git commit -m "fs-triage-devoluciones: estado de partida de la demo 4" -- .
```

El `-- .` limita el commit a esta carpeta, aunque haya otros cambios preparados en el repositorio.

**12.2 · Ensaya el beat de observabilidad** en Claude Code, con la carpeta del agente abierta:

```text
añade observabilidad con OpenTelemetry a este agente, sin cambiar su lógica
```

Revisa el diff: debe **añadir** (dependencias, configuración del exportador, spans alrededor de las
herramientas) sin reescribir `agent.py`. Graba la pantalla: es el plan B de la slide 28.

**12.3 · Deja el repositorio limpio.** Si llegas al escenario con el agente ya instrumentado, la demo
no tiene nada que enseñar.

```powershell
git restore -- .
git clean -fd -- src
git status --short -- .
```

`git clean` no borra `.env` ni `.venv`, porque están en `.gitignore`. El último comando no debe
devolver nada.

**12.4 · Ventanas para la sala.** VS Code con `src\agent.py` y `.env` abiertos, el resumen de
`salida\` y el panel de Claude Code. Terminal a 18 pt.

---

## 13. Opcional: leer el buzón real de Exchange

Solo si existe el buzón compartido y quieres enseñar el acceso real.

1. **Entra admin center › App registrations › New registration**: `fs-triage-devoluciones`.
2. **API permissions › Microsoft Graph › Application permissions › `Mail.Read`**, y **Grant admin
   consent**.
3. **Certificates & secrets › New client secret**. Copia el valor.
4. En el `.env`:

   ```text
   BUZON_ORIGEN=graph
   AZURE_TENANT_ID=<id del tenant>
   AZURE_CLIENT_ID=<id de la aplicación>
   AZURE_CLIENT_SECRET=<el secreto>
   BUZON_DEVOLUCIONES=devoluciones@tudominio
   ```

> `Mail.Read` de aplicación da acceso a **todos** los buzones del tenant. Para limitarlo a uno, usa
> una Application Access Policy de Exchange. Ese exceso de permisos es, precisamente, el problema
> que la demo 4 señala.

---

## 14. Opcional: registrarlo en Agent 365

Solo si tu tenant tiene Agent 365. Si algo no sale a la primera, descártalo y cierra la demo con la
slide del blueprint.

```powershell
gh skill add microsoft/agent365-skills
```

Después, en Claude Code sobre esta carpeta:

```text
set up this project for Agent 365
register this agent with Agent 365
validate this Agent 365 integration
```

> Las herramientas de Work IQ (`add-workiq-tools`) necesitan **permisos delegados**. Con el modo
> `graph` de este agente, que usa permisos de aplicación (S2S), la skill se salta sola y sin avisar.

---

## Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `CLINotFoundError: Claude Code not found` | El SDK no encuentra un `claude.exe` nativo | Rellena `CLAUDE_CLI_PATH` (paso 8). Un `claude.cmd` de npm no sirve |
| `CLINotFoundError: ... at: C:SERS...` | La ruta del `.env` perdió las barras invertidas | Regenera el `.env` con el bloque del paso 8.3 |
| `python-dotenv could not parse statement starting at line N` | Una línea rota en el `.env` | Ábrelo y corrige o borra esa línea, o regenéralo |
| `ModuleNotFoundError: No module named 'httpx'` | Ejecutas con el Python del sistema, no con el del entorno virtual | Usa `.\.venv\Scripts\python` |
| `Falta la variable de entorno AZURE_TENANT_ID` | `BUZON_ORIGEN` no es `local` | Pon `BUZON_ORIGEN=local` |
| `FileNotFoundError` sobre `correos.json` | El agente no está en `demos/agente-externo/` | Mueve la carpeta o define `BUZON_FICHERO` |
| Error de autenticación o de cuota del modelo | Claude Code sin sesión | Inicia sesión en el panel de Claude Code o rellena `ANTHROPIC_API_KEY` |
| Funcionaba y deja de funcionar tras actualizar VS Code | La extensión cambió de versión y de carpeta | Repite el paso 8.3 |
