# FraSoHome Foundry Agents por código

Este scaffold crea y ejecuta la demo FraSoHome desde Python en lugar de usar el diseñador del portal.

## 1. Preparar entorno

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
copy .env.example .env
```

Edita `.env`:

```powershell
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
MODEL_DEPLOYMENT=<deployment-name>
```

Autentica con Azure:

```powershell
az login
az account show
```

## 2. Validar assets locales

```powershell
frasohome-agents check-assets
```

Esto comprueba:

- `case/fraso_home_caso.md`
- `case/fraso_home_storytelling_foundry.md`
- `case/kb/README.md`
- `case/kb/FS-KB-*.md`
- `case/data/*.csv`

## 3. Validar datos sin Azure

```powershell
frasohome-agents local-profile
```

Salidas:

- `outputs/local_data_quality_report.json`
- `outputs/local_data_quality_report.md`

## 4. Previsualizar creación de agentes

```powershell
frasohome-agents create-agents --dry-run
```

## 5. Crear agentes en Microsoft Foundry

```powershell
frasohome-agents create-agents
```

El comando intenta:

1. Subir Markdown del caso y KB.
2. Crear un vector store `frasohome-knowledge-kb`, salvo que definas `FRASOHOME_VECTOR_STORE_ID`.
3. Crear `frasohome-knowledge` con File Search.
4. Subir CSVs.
5. Crear `frasohome-data-quality` con Code Interpreter.
6. Crear `frasohome-returns` y `frasohome-operations` con File Search.
7. Crear `frasohome-storyteller` sin herramientas.

Si tu versión del SDK no expone todavía creación de vector store desde `AIProjectClient`, crea el vector store en el portal o con el SDK equivalente y pon su id en `.env`:

```powershell
FRASOHOME_VECTOR_STORE_ID=<vector-store-id>
```

## 6. Ejecutar demos

Knowledge:

```powershell
frasohome-agents demo-knowledge
```

Data Quality:

```powershell
frasohome-agents demo-data-quality
```

Orquestador multiagente en código:

```powershell
frasohome-agents demo-orchestrator
```

Salida del orquestador:

- `outputs/orchestrator_response.json`

## 7. Preguntar a cualquier agente existente

```powershell
frasohome-agents ask frasohome-knowledge "¿Cuál es el plazo de devolución online?"
```

## 8. Estructura

```text
src/frasohome_agents/
  assets.py              # Localiza caso, KB y CSVs
  cli.py                 # CLI principal
  contracts.py           # Contratos Pydantic
  create_agents.py       # Creación de agentes y herramientas
  foundry.py             # Cliente Foundry y helpers SDK
  local_data_quality.py  # Perfilado local con pandas
  orchestrator.py        # Workflow multiagente en código
  prompts.py             # Instrucciones y prompts canónicos
  run_agents.py          # Ejecución de agentes existentes
  settings.py            # Configuración .env
```

## 9. Notas de producción

- Usa Entra ID/RBAC; no guardes secretos en el repo.
- Revisa trazas, tool calls, latencia y costes en Foundry/Application Insights.
- Trata trazas como telemetría de producción: minimiza PII y controla retención.
- Versiona prompts e instrucciones.
- Añade evaluación automática antes de publicar o promover agentes.

