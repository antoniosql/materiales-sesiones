# Demos — De la jungla de agentes al control plane

Material de las cuatro demos de la sesión del Bizz Summit Madrid 2026, escenario FraSoHome
(devoluciones omnicanal).

**El montaje es manual.** Los scripts de despliegue del tenant se retiraron el 2 de octubre:
el tenant disponible tiene el entorno Default ya gestionado y no había margen para controles
que tardan días en propagar. Siguen en el historial de git (commit `bca9957`) por si se
quieren recuperar.

**Abre [`guia-despliegue-manual.html`](guia-despliegue-manual.html)**: los cuatro escenarios
revisados y el montaje paso a paso, con los valores copiables y casillas de progreso.

## Las cuatro demos, tal como quedan

| Demo | Lo que se enseña | Depende de |
|---|---|---|
| 1 · ¿Cuántos hay? | All agents: un agente de Agent Builder y el de Copilot Studio en la misma lista | Los agentes creados la víspera |
| 2 · ¿Qué hacen? | Purview DSPM for AI: lo que preguntan los usuarios, con un IBAN pegado en un agente | DSPM y auditoría activos antes de generar actividad |
| 3 · ¿Quién decide? | Aprobar una solicitud de publicación, bloquear un agente y la política de creación | La solicitud pendiente y el bloqueo de la víspera |
| 4 · El otro agente | Agente con Claude Agent SDK que funciona y nadie ve; observabilidad en vivo; registro si hay Agent 365 | Nada del tenant: buzón local |

## Contenido

```text
demos/
├─ guia-despliegue-manual.html   escenarios revisados y montaje paso a paso
├─ agente/                       el agente de Copilot Studio como código
│  ├─ instrucciones.md           instrucciones del Asistente de Devoluciones
│  ├─ knowledge/                 fuente de conocimiento de SharePoint
│  └─ topics/                    escalado-fraude se usa; plazo y métricas no
├─ datos/
│  ├─ buzon/correos.json         las 18 reclamaciones que lee el agente de Claude
│  ├─ kb/                        FS-KB-11, el documento confidencial
│  └─ testsets/                  test sets de la versión anterior de la demo 3
└─ agente-externo/
   └─ fs-triage-devoluciones/    el agente de Claude (Python). Tiene su propio README
```

## Agente de Claude en dos líneas

```powershell
cd agente-externo\fs-triage-devoluciones
.\.venv\Scripts\python src\agent.py --verbose
```

Con `BUZON_ORIGEN=local` en el `.env` lee `datos/buzon/correos.json` y no necesita Exchange.
