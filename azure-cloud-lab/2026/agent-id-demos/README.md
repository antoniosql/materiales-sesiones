# entra-agent-id-demos

Demos reproducibles de la sesión **«Identidad, acceso y ciclo de vida de agentes con Microsoft Entra Agent ID»**
(Azure Cloud Lab 2026), sobre **FraSoHome**, una cadena ficticia de retail de hogar con tres agentes que llegan al
directorio por tres puertas distintas:

| Puerta | Agente | Plataforma | Qué demuestra |
|---|---|---|---|
| 1 | `FS-Copilot-Devoluciones` | Copilot Studio | Agent ID automático, sponsor que cambió de equipo, flujo en nombre de usuario |
| 2 | `frasohome-returns` | Foundry Agent Service + servidor MCP | Identidad compartida frente a identidad propia: los roles no viajan |
| 3 | `fs-triage-devoluciones` | Python en Container Apps | Blueprint de IT con federated credential: sin secretos |

Sobre ellos: RBAC mínimo, acceso condicional por atributo de seguridad y riesgo del agente, ID Protection,
Lifecycle Workflows para sponsors y rastro en los logs.

## Contenido

```
entra-agent-id-demos/
├── setup.ps1 · setup.sh          entorno virtual, dependencias, .env, Git y comprobaciones
├── .env.example                  todas las variables, explicadas (setup copia a .env)
├── requirements*.txt             dependencias, por si no usas pyproject
├── config/escenario.yaml         personas, grupos, carriles, agentes, políticas y workflow
├── config/vscode/                ajustes de VS Code (setup los copia a .vscode)
├── infra/                        Bicep: main.bicep (base + Foundry opcional) y apps.bicep (Container Apps)
├── apps/
│   ├── fs-devoluciones-mcp/      servidor MCP (demo 2): usa el token del agente que le pasa Foundry
│   └── fs-triage-devoluciones/   agente propio (demo 3): identity.py tiene el flujo de token sin secretos
├── src/agentid/                  CLI `agentid`: Microsoft Graph (Entra) + Azure CLI
├── copilot-studio/               el Asistente de Devoluciones (instrucciones, conocimiento, topics) y cómo montarlo
├── datos/                        CSV del caso (devoluciones y productos) y 18 correos del buzón
├── kql/consultas.kql             inicios de sesión y auditoría de agentes en Log Analytics
└── tests/                        pruebas sin red (pytest)
```

## Puesta en marcha

Requisitos: Windows con PowerShell, Python 3.10+, Azure CLI con Bicep y, opcionalmente, Azure Developer CLI.

```powershell
cd C:\repos\entra-agent-id-demos
powershell -ExecutionPolicy Bypass -File .\setup.ps1
.\.venv\Scripts\Activate.ps1
notepad .env                       # rellena lo marcado con «←»: TENANT_ID, SUBSCRIPTION_ID, NAME_SUFFIX
az login --tenant <TENANT_ID>
agentid check
agentid desplegar
```

`setup.ps1` crea `.venv`, instala el CLI con sus dependencias, crea `.env` (desde `.env.example`) y `.vscode`
si no existen, inicializa Git, comprueba las herramientas de Azure y ejecuta las pruebas. En macOS o Linux, `./setup.sh`.

`agentid desplegar` monta todo lo que tiene API, en orden. Lo que queda a mano (agente de Copilot Studio,
licencias y política de inactividad por defecto), los permisos necesarios, el ensayo y la limpieza están en
**[DESPLIEGUE.md](DESPLIEGUE.md)**.

## Comandos

| Comando | Qué hace |
|---|---|
| `agentid check` | Requisitos: variables, herramientas, sesión de Azure y de Graph |
| `agentid desplegar` | Todo, en orden: infra → personas → atributo → datos → blueprint → identidad → RBAC → imágenes → apps → Foundry → acceso condicional → ciclo de vida |
| `agentid infra` · `personas` · `atributos` · `datos` · `blueprint` · `identidad` · `rbac` · `imagenes` · `apps` | Cada paso por separado |
| `agentid copilot` | Puerta 1: sponsor Marta R. y carril del Asistente de Devoluciones |
| `agentid foundry identidades` · `conexion` · `agente` · `antes` · `preguntar` | Puerta 2 |
| `agentid acceso` · `ciclo` | CA-AG-01, CA-AG-02 y LW-Mover-Sponsors |
| `agentid demo2 comando` · `arreglar` · `deshacer` | Demo 2 en directo |
| `agentid demo4 comprometer` · `reiniciar` · `logs` · `mover` · `sponsors` · `descartar` | Demo 4 en directo |
| `agentid ensayo estado` · `reiniciar` | Foto del escenario y vuelta al estado de partida |
| `agentid cleanup --si` | Borra solo lo que crearon estos scripts |

> ⚠️ Varias APIs de Agent ID están en beta. Donde una llamada falla, el comando no se detiene: indica cómo
> hacer ese paso en el portal. La lista de comprobaciones está en DESPLIEGUE.md, §8.
