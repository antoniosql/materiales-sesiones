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

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env               # y rellénalo
python src/agent.py --verbose
```

El registro de aplicación de Entra necesita permiso de aplicación `Mail.Read`
sobre el buzón compartido, con consentimiento de administrador.

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

```bash
gh skill add microsoft/agent365-skills

# En Claude Code, sobre este repositorio:
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
