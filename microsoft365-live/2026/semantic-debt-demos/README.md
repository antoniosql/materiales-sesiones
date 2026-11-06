# Semantic Debt · demos reproducibles

Scripts para montar, medir y limpiar en un tenant de demo las demos de la sesión
**«Semantic Debt: why Copilot answers questions nobody asked»** (Microsoft 365 Live 2026),
sobre el caso ficticio **FraSoHome**.

- **Python** para todo lo que tiene API: usuarios, sitios, bibliotecas, columnas, term store, glosario de Purview, agente (vía `pac`) y la evaluación como Laura.
- **PowerShell** solo donde no hay alternativa: etiquetas de Purview (Security & Compliance) y la columna de metadatos administrados (PnP).
- **Parámetros** en `.env`. **Escenario** (sitios, carpetas, ficheros, metadatos, cifras esperadas) en `config/escenario.yaml`.
- **Documentos listos para indexar** en [`documentos/`](documentos/): 13 ficheros generados con la KB y los datos reales del caso.
- **Guía de despliegue completa, con requisitos**: [DESPLIEGUE.md](DESPLIEGUE.md).
- **Limpieza segura**: cada recurso se registra en `state/deployed.json`. `cleanup` borra solo lo que estos scripts crearon; lo que ya existía se reutiliza y no se toca.

## Qué reproduce

Las demos 0–3 se hacen en el **Copilot del sitio FraSoHome-Comercial** y la 4 en el agente de Copilot Studio.
Copilot Chat general vería también la biblioteca oficial y el «antes» dejaría de fallar.

| Demo | Qué se despliega | Comando |
|---|---|---|
| 0 · La respuesta perfecta | PPT de marketing con «49 clientes activos» y «−2,6 %» en el sitio comercial | `sharepoint --fase antes` |
| 1 · Bibliotecas sin taxonomía | `FraSoHome-Comercial` con carpetas `Antiguo/`, `Comité/`, `Definitivos/`, `Varios/` y sin columnas; FS-KB-02 v1.2 (30 días) junto a FS-KB-01 v1.3 (45 días) | `sharepoint --fase antes` |
| 2 · Etiquetas sin mantener | FS-KB-03 con «Altamente confidencial – Finanzas» (cifrado solo para FS-Finanzas) | `Deploy-Labels.ps1` + `sharepoint --fase antes` |
| 3 · Términos sin dueño | «Cliente activo» en borrador en el glosario, sin dueño de negocio | `glossary --estado borrador` |
| 4 · El «después» | `FraSoHome-KB-Oficial` con Estado / Dominio / Propietario / Vigente desde, FS-KB-03 re-etiquetado, término publicado con dueña y agente de Copilot Studio | `termstore`, `sharepoint --fase despues`, `Set-DominioTaxonomy.ps1`, `glossary --estado publicado`, `agent create` |
| Paso 3 del diagnóstico | TRC del test set de 20 preguntas, como Laura (nunca como admin) | `evaluate --target retrieval\|chat\|agent` |

Las cifras de las slides (47/49/89/100/132/135 clientes; −2,6 % / +2,5 % / +4,4 % / +6,9 %) se recalculan
con los datos del caso (`figures`) y se escriben en los documentos. Si los datos cambian y las cifras no
cuadran, el comando avisa: **cambia las slides, no el código**.

## Requisitos

- Python 3.10+ y PowerShell 7 (`pwsh`) con los módulos `ExchangeOnlineManagement` y `PnP.PowerShell`.
- Power Platform CLI (`pac`), autenticado contra el entorno del agente: `pac auth create --environment <id>`.
- Tenant de demo con licencias Microsoft 365 E5 (o equivalente) y **Microsoft 365 Copilot** para Laura.
- Etiquetado de ficheros de Office en SharePoint habilitado (`Set-SPOTenant -EnableAIPIntegration $true`).
- Purview Unified Catalog con un **dominio de gobierno publicado** (su id va en `PURVIEW_DOMAIN_ID`).
- Opcional: [API medidas de Graph](https://learn.microsoft.com/graph/metered-api-setup) habilitadas para la app, si quieres aplicar las etiquetas por código (`LABEL_APPLY_METHOD=graph`). Si no, `manual`.
- El repo de materiales con los datos del caso (`frasohome-agents-foundry/case/data` y `case/kb`).

## Registro de aplicación en Entra ID

Un solo registro para todo. Mejor con **certificado**: PnP no admite secreto en modo app-only.

**Permisos de aplicación (Microsoft Graph)**: `User.ReadWrite.All`, `Group.ReadWrite.All`,
`Sites.FullControl.All`, `Files.ReadWrite.All`, `TermStore.ReadWrite.All`, `Organization.Read.All`,
`LicenseAssignment.ReadWrite.All`.
**Permisos de aplicación (SharePoint, para PnP)**: `Sites.FullControl.All`.

**Permisos delegados** (evaluación como Laura; activa *Allow public client flows*):
- Microsoft Graph: `Sites.Read.All`, `Files.Read.All`, `Mail.Read`, `People.Read.All`,
  `OnlineMeetingTranscript.Read.All`, `Chat.Read`, `ChannelMessage.Read.All`, `ExternalItem.Read.All`.
- Power Platform API: `CopilotStudio.Copilots.Invoke`.

**Purview**: da a la entidad de servicio un rol de Unified Catalog que permita crear y publicar términos
en el dominio (p. ej., propietario del dominio de gobierno o *data steward*).
**Etiquetas en modo app** (opcional, `PURVIEW_PS_AUTH=app`): `Exchange.ManageAsApp` y el rol Compliance Administrator.

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[agent,dev]"
Copy-Item .env.example .env   # y rellénalo
semdebt check
```

## Orden de despliegue

`semdebt deploy` ejecuta todos los pasos en orden y llama a `pwsh` cuando toca. Paso a paso:

| # | Comando | Notas |
|---|---|---|
| 1 | `semdebt figures` | Recalcula y compara con las slides |
| 2 | `semdebt documents` | Solo si cambias el caso: regenera `documentos/` (ya versionados) |
| 3 | `semdebt identities` | Laura, Paco, licencias y grupo `FS-Finanzas` |
| 4 | `pwsh scripts/powershell/Deploy-Labels.ps1` | Etiquetas y directiva. **Hasta 24 h de propagación** |
| 5 | `semdebt sharepoint --fase antes` | Sitio comercial (el aprovisionamiento tarda unos minutos) |
| 6 | `semdebt termstore` | Grupo `FraSoHome`: «Estado documental» y «Dominio» |
| 7 | `semdebt sharepoint --fase despues` | Biblioteca oficial con metadatos |
| 8 | `pwsh scripts/powershell/Set-DominioTaxonomy.ps1` | Solo con `DOMINIO_COLUMN_MODE=taxonomy` |
| 9 | `semdebt glossary --estado borrador` | Estado de la demo 3 |
| 10 | `semdebt agent create` | Requiere la plantilla: ver [copilot-studio/README.md](copilot-studio/README.md) |
| 11 | `semdebt evaluate --target retrieval --sitio comercial` | Tras la indexación (horas): el ANTES (slides: 7/20) |
| 12 | `semdebt evaluate --target agent` | El DESPUÉS (slides: 15/20) |

**Monta como muy tarde 48 h antes del evento**: etiquetas, índice semántico y sincronización de
Copilot Studio (4–6 h) no son inmediatos. Todo es idempotente: si un paso falla, se puede repetir.

## Día de la demo

```powershell
semdebt glossary --estado borrador     # antes de empezar (demo 3)
semdebt evaluate --target chat         # pre-run 30 min antes: anota si algo cambia
semdebt glossary --estado publicado    # justo antes de la demo 4
```

## Limpieza

```powershell
semdebt cleanup                 # pide confirmación y enseña la lista
pwsh scripts/powershell/Remove-Labels.ps1
pwsh scripts/powershell/Remove-DeletedSites.ps1   # purga la papelera para reutilizar los alias
```

Opciones de `cleanup`:
- `--purge`: purga también los usuarios y grupos de la papelera de Entra.
- `--keep-identities`: conserva a Laura, Paco y FS-Finanzas para el siguiente ensayo.
- `--keep-local`: conserva las salidas locales (`documentos/` nunca se borra).

Si Laura o Paco ya existían, no se borran: solo se les quitan las licencias que estos scripts añadieron.

## Qué no se automatiza (y por qué)

| Pieza | Motivo | Qué hacer |
|---|---|---|
| Primer montaje del agente | Copilot Studio no crea por API una fuente de SharePoint con filtrado por metadatos | Montarlo una vez y exportar la plantilla (`agent extract-template`) |
| Filtrado por metadatos (`Estado = Vigente`) | Opción de la UI de Copilot Studio | Revisarlo tras `agent create` |
| Aplicar etiquetas sin API medida | `assignSensitivityLabel` es de pago por uso | `LABEL_APPLY_METHOD=manual`: el comando te dice qué fichero etiquetar |
| Política de autoetiquetado de 2024 | Es narrativa: la etiqueta se aplica directamente | — |

## Previews y APIs que pueden cambiar

- **Chat API de Copilot**: `graph.microsoft.com/beta/copilot/conversations` (por defecto) o Work IQ (`COPILOT_CHAT_ENDPOINT=workiq`).
- **Retrieval API**: `v1.0/copilot/retrieval`.
- **Unified Catalog API**: `2026-03-20-preview`, configurable en `PURVIEW_API_VERSION`.
- **SDK de Copilot Studio**: `microsoft-agents-copilotstudio-client`. Si cambia la firma, ajusta `evaluate._agent_session`.

## Seguridad y estado

- `.env`, `state/` y `output/` están en `.gitignore`. Las contraseñas generadas se muestran una vez y no se guardan.
- `state/deployed.json` es el registro de lo creado, y `state/labels.json` y `state/dominio_plan.json` son el puente con PowerShell.
- `--dry-run` recorre cualquier comando sin llamar a nada y escribe en `state/dry-run` y `output/dry-run`.
- La evaluación se niega a ejecutarse con la cuenta admin: el admin ve más que Laura y la demo deja de ser verdad.

## Estructura

```
config/escenario.yaml        escenario: sitios, carpetas, metadatos, etiquetas, glosario, cifras
documentos/                  los 13 documentos que se suben (regenerables con `semdebt documents`)
DESPLIEGUE.md                guía de despliegue en un tenant, requisitos y validación demo a demo
testset/testset_frasohome.csv  20 preguntas con estado, palabras clave y fuente canónica
src/semdebt/                 CLI y pasos (figures, documents, identities, sharepoint, termstore,
                             glossary, agent, evaluate, cleanup, check)
scripts/powershell/          Deploy-Labels, Set-DominioTaxonomy, Remove-Labels, Remove-DeletedSites
copilot-studio/              instrucciones del agente y guía de primer montaje
tests/                       tests sin tenant (pytest); define CASE_DATA_DIR para validar las cifras reales
```
