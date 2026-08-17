# 🐍 Paso a paso: demo con notebook y módulos Python

Esta guía explica cómo ejecutar la sesión desde código usando el notebook:

👉 [notebooks/frasohome_foundry_agents_demo.ipynb](notebooks/frasohome_foundry_agents_demo.ipynb)

El notebook está pensado para una sesión técnica: permite ejecutar módulos del repo celda a celda, enseñar outputs intermedios y activar llamadas a Microsoft Foundry solo cuando el entorno esté listo.

## 🎯 Objetivo

Mostrar cómo pasar del diseño visual a una implementación reproducible:

- validar assets,
- perfilar datos localmente,
- revisar prompts e instrucciones,
- crear agentes con SDK,
- ejecutar agentes,
- reproducir el workflow multiagente desde Python.

## 1. Preparar entorno ⚙️

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
copy .env.example .env
az login
```

Edita `.env`:

```text
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
MODEL_DEPLOYMENT=<deployment-name>
```

La demo se puede ensayar sin Azure usando:

```powershell
frasohome-agents check-assets
frasohome-agents local-profile
frasohome-agents create-agents --dry-run
```

## 2. Abrir el notebook 📓

Abre:

```text
notebooks/frasohome_foundry_agents_demo.ipynb
```

La primera parte del notebook:

- detecta la raíz del repo,
- añade `src` al `PYTHONPATH`,
- carga `.env`,
- define `RUN_LIVE_FOUNDRY = False`.

Mantén ese valor en `False` para ensayar sin coste ni llamadas a Azure.

Actívalo solo cuando quieras ejecutar Foundry:

```python
RUN_LIVE_FOUNDRY = True
```

## 3. Recorrido recomendado del notebook 🧭

### Bloque 1 · Validar assets

Módulos usados:

- `settings.py`
- `assets.py`

Qué hace:

- carga configuración,
- comprueba rutas,
- lista documentos Knowledge,
- lista CSVs para Code Interpreter.

Mensaje para la sesión:

> “Antes de crear agentes, validamos que sabemos qué conocimiento y datos va a consumir el sistema.”

### Bloque 2 · Mostrar caso y KB

Módulos usados:

- lectura directa de Markdown,
- `IPython.display.Markdown`.

Qué enseña:

- storytelling del caso,
- índice de políticas,
- documentos que gobernarán respuestas normativas.

### Bloque 3 · Perfilado local

Módulo usado:

- `local_data_quality.py`

Qué hace:

- lee todos los CSV con pandas,
- calcula filas, columnas, nulos y duplicados,
- detecta columnas numéricas sospechosas,
- intenta parsear fechas,
- genera salidas en `outputs/`.

Salidas:

- `outputs/local_data_quality_report.json`
- `outputs/local_data_quality_report.md`

Mensaje para la sesión:

> “Code Interpreter hará esto dentro de Foundry, pero primero podemos validar el caso localmente y enseñar el problema de datos.”

### Bloque 4 · Prompts e instrucciones

Módulo usado:

- `prompts.py`

Contiene:

- instrucciones de `Knowledge`,
- instrucciones de `Data Quality`,
- instrucciones de `Returns`,
- instrucciones de `Operations`,
- instrucciones de `Storyteller`,
- prompts canónicos.

Mensaje para la sesión:

> “El diseño del sistema vive tanto en herramientas como en contratos e instrucciones.”

### Bloque 5 · Dry-run de creación

Módulo usado:

- `create_agents.py`

Ejecuta:

```python
create_all_agents(dry_run=True)
```

Qué enseña:

- qué agentes se crearían,
- qué archivos irían a File Search,
- qué CSVs irían a Code Interpreter,
- qué instrucciones usaría cada especialista.

No llama a Azure.

### Bloque 6 · Crear agentes en Foundry

Módulos usados:

- `create_agents.py`
- `foundry.py`

Ejecuta, solo si `RUN_LIVE_FOUNDRY = True`:

```python
create_all_agents(dry_run=False)
```

Qué intenta crear:

- vector store de conocimiento,
- `frasohome-knowledge` con File Search,
- uploads de CSV,
- `frasohome-data-quality` con Code Interpreter,
- `frasohome-returns`,
- `frasohome-operations`,
- `frasohome-storyteller`.

Nota:

Si tu versión del SDK no permite crear vector store desde `AIProjectClient`, crea el vector store en portal y configura:

```text
FRASOHOME_VECTOR_STORE_ID=<vector-store-id>
```

### Bloque 7 · Demo Knowledge

Módulo usado:

- `run_agents.py`

Ejecuta:

```python
run_knowledge()
```

Salida:

- respuesta en pantalla,
- `outputs/knowledge_response.md`.

### Bloque 8 · Demo Data Quality

Módulo usado:

- `run_agents.py`

Ejecuta:

```python
run_data_quality()
```

Salida:

- respuesta en pantalla,
- `outputs/data_quality_report.md`.

### Bloque 9 · Orquestador multiagente

Módulo usado:

- `orchestrator.py`

Ejecuta:

```python
run_orchestrator()
```

Qué hace:

1. llama a `frasohome-knowledge`,
2. llama a `frasohome-data-quality`,
3. llama a `frasohome-returns`,
4. llama a `frasohome-operations`,
5. envía todo a `frasohome-storyteller`,
6. valida la salida con Pydantic,
7. guarda JSON final.

Salida:

- `outputs/orchestrator_response.json`.

## 4. Módulos Python explicados 🧱

| Módulo | Papel en la demo |
|---|---|
| `settings.py` | Carga `.env`, nombres de agentes, rutas y umbral de confianza |
| `assets.py` | Localiza caso, KB y CSVs; valida que existan |
| `prompts.py` | Centraliza instrucciones y prompts canónicos |
| `contracts.py` | Define contratos Pydantic para especialistas y orquestador |
| `local_data_quality.py` | Perfilado local con pandas, sin Azure |
| `foundry.py` | Cliente Foundry, creación/ejecución y extracción de respuestas |
| `create_agents.py` | Crea agentes, sube archivos y configura herramientas |
| `run_agents.py` | Ejecuta demos Knowledge y Data Quality |
| `orchestrator.py` | Reproduce el workflow multiagente en Python |
| `cli.py` | Expone comandos `frasohome-agents` |

## 5. Comandos equivalentes por CLI 💻

Validar assets:

```powershell
frasohome-agents check-assets
```

Perfilado local:

```powershell
frasohome-agents local-profile
```

Previsualizar agentes:

```powershell
frasohome-agents create-agents --dry-run
```

Crear agentes:

```powershell
frasohome-agents create-agents
```

Ejecutar demos:

```powershell
frasohome-agents demo-knowledge
frasohome-agents demo-data-quality
frasohome-agents demo-orchestrator
```

## ✅ Checklist antes de presentar

- [ ] `.env` configurado.
- [ ] `az login` ejecutado.
- [ ] `frasohome-agents check-assets` correcto.
- [ ] `frasohome-agents local-profile` genera reportes.
- [ ] Notebook abre con kernel correcto.
- [ ] `RUN_LIVE_FOUNDRY` está en el valor deseado.
- [ ] Si hay demo live, agentes creados o permisos verificados.
- [ ] `outputs/` contiene resultados de respaldo.

## 🧠 Mensaje final para la sesión

> “El portal ayuda a explicar y diseñar. El notebook ayuda a reproducir, versionar y evolucionar. La buena demo enseña ambos mundos conectados.”
