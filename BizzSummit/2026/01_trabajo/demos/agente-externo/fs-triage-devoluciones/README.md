# fs-triage-devoluciones

Agente de triaje del buzón `devoluciones@frasohome.es`, construido con **Claude Agent SDK**.
Lee la bandeja, clasifica por motivo, detecta patrones anómalos y redacta el resumen diario
para el Store Manager.

Es el protagonista de la **demo 4**. Su gracia no es lo que hace: es lo que le falta.

## Estado de partida — importante

Este repositorio arranca la demo **deliberadamente sin gobernar**:

- Sin Entra Agent ID: no existe como identidad
- Sin telemetría: no aparece en Defender ni en el admin center
- Sin propietario declarado: nadie responde por él
- Con credenciales propias en un `.env`: el acceso al correo de FraSoHome no lo ve ningún admin

Eso es lo que se enseña primero, y por eso el `.env.example` lo dice en su primera línea.

## Puesta en marcha

Instrucciones completas, paso a paso y con el código: [`GUIA-PASO-A-PASO.md`](GUIA-PASO-A-PASO.md)
(también en HTML: [`guia-paso-a-paso.html`](guia-paso-a-paso.html)). Resumen:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env        # y rellena CLAUDE_CLI_PATH
.\.venv\Scripts\python src\agent.py --verbose
```

Dos modos de buzón, según `BUZON_ORIGEN` en el `.env`:

| Valor | Qué lee | Qué necesita |
|---|---|---|
| `local` (por defecto) | Las 18 reclamaciones de `demos/datos/buzon/correos.json`, repartidas en la última semana | Nada del tenant. **Es el que se usa en la sala** |
| `graph` | El buzón compartido real de Exchange | Registro de aplicación con permiso `Mail.Read` y consentimiento de administrador |

En Windows el SDK exige un `claude.exe` nativo. El de la extensión de VS Code sirve:
`C:\Users\<usuario>\.vscode\extensions\anthropic.claude-code-<versión>-win32-x64\resources\native-binary\claude.exe`.

## Los tres beats de la demo

### Beat 1 — observabilidad

En Claude Code, sobre este repositorio:

```
añade observabilidad a este agente
```

Corre `instrument-observability`, que cablea OpenTelemetry y el exportador de trazas.
**Enseña el diff**: es aditivo. No reescribe la lógica, no cambia el framework.

### Beat 2 — tooling gobernado

```
conecta este agente a Mail y Word a través de Work IQ
```

Corre `add-workiq-tools`. El agente deja de leer el buzón con las credenciales del `.env`
y pasa a leerlo por servidores MCP que el administrador ve, audita y puede cortar.

> ⚠️ `add-workiq-tools` **requiere modelo de permisos delegados**. Con autenticación S2S
> la skill se salta sola y en silencio. Es una decisión que se toma antes de escribir el
> agente, no después.

### Beat 3 — en vivo, sí o sí

Volver a *All agents*. Los dos agentes de FraSoHome en la misma lista, con propietario,
identidad y telemetría. Uno es de Copilot Studio; el otro es este.

## Preparación previa

Las skills de Agent 365 son un plugin de Claude Code (en el equipo de la sesión ya están instaladas).
En una sesión de Claude Code:

```text
/plugin marketplace add https://github.com/microsoft/agent365-skills
/plugin install agent365@agent365-skills
```

`gh skill add` las instala para GitHub Copilot, no para Claude Code. Detalle en el paso 14 de la guía.

```text
# En Claude Code, sobre este repositorio:
#   "añade observabilidad con OpenTelemetry"  -> instrument-observability (beat 1, sin tenant)
#   "set up this project for Agent 365"      -> a365-setup
#   "register this agent with Agent 365"     -> make-a365-agent   (camino standard)
#   "validate this Agent 365 integration"    -> a365-code-validator
```

No uses `make-ai-teammate`: requiere Frontier preview y no entra en esta sesión.

**Ensaya los tres beats y luego deja el repositorio limpio** (`git reset --hard`).
Si llegas al escenario con el agente ya instrumentado, la demo 4 no tiene nada que enseñar.

## Estructura

| Archivo | Qué hace |
|---|---|
| `src/agent.py` | El agente: instrucciones, las cuatro herramientas y el bucle |
| `src/buzon.py` | Cliente de Graph para el buzón compartido. Es lo que el beat 2 sustituye |
| `.env.example` | Las credenciales que no debería tener |
| `salida/` | Los resúmenes diarios generados (fuera de control de versiones) |

## Comprobar que la telemetría llega

Después del beat 1, en Defender advanced hunting. Si no devuelve filas, revisa en este
orden: invocación → licencia → connector de M365 → formato de la telemetría.
