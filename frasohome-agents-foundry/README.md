# 🏠 FraSoHome Agents Foundry

## Una sesión práctica para aterrizar agentes de IA en Microsoft Foundry

**FraSoHome** es un retailer ficticio de hogar y decoración que tiene un problema muy real: vende en tienda y online, gestiona clientes en CRM, opera stock y devoluciones, tiene políticas internas... pero sus datos y decisiones viven repartidos entre sistemas.

Esta sesión convierte ese caos operativo en una demo guiada de **Microsoft Foundry Agent Service**, mostrando cómo diseñar agentes con conocimiento, herramientas, workflows, trazabilidad y código.

> 🎯 La promesa de la sesión: salir sabiendo explicar, diseñar y construir una solución multiagente realista, no solo un chatbot bonito.

## 🚀 Qué vas a construir

Durante la sesión se construye un sistema de agentes para responder preguntas como:

- 🧾 “Un cliente compró un sofá online, quiere devolverlo en tienda y usó un cupón. ¿Qué pasos debe seguir atención al cliente?”
- 📊 “¿Qué problemas de calidad tienen los CSV antes de crear dashboards o modelos?”
- 🔁 “¿Por qué están subiendo las devoluciones online en iluminación y qué hacemos esta semana?”

La demo enseña dos formas de llegar al mismo resultado:

| Ruta | Qué muestra | Para quién brilla |
|---|---|---|
| 🖱️ **Interfaz gráfica de Foundry** | Agent Designer, File Search, Code Interpreter, Workflows, Playground y trazas | Perfiles de negocio, preventa, arquitectura, formación |
| 🐍 **Python + Notebook** | SDK, creación de agentes, perfilado local, orquestador multiagente y ejecución reproducible | Desarrolladores, data/AI engineers, hackathons |

## 🧩 El caso FraSoHome

FraSoHome opera como muchas empresas reales:

- 🛒 **E-commerce:** pedidos, líneas de pedido, pagos y devoluciones online.
- 🏬 **Tiendas físicas:** ventas POS, caja, pagos mixtos y devoluciones en tienda.
- 👤 **CRM:** clientes, fidelización, preferencias y segmentación.
- 📦 **ERP / inventario:** productos, SKUs, catálogo y stock diario.
- 📚 **Políticas internas:** devoluciones, KPIs, caja, conciliación, catálogo y atención.

El reto no es “preguntarle cosas a una IA”. El reto es diseñar un sistema que:

- encuentre la política correcta,
- calcule evidencias con datos,
- separe hipótesis de hechos,
- proponga acciones medibles,
- y deje trazabilidad para revisar qué ha pasado.

## 🤖 Agentes de la demo

| Agente | Responsabilidad | Herramienta |
|---|---|---|
| 🧠 `frasohome-knowledge` | Responde con grounding sobre caso y políticas internas | File Search |
| 🔎 `frasohome-data-quality` | Analiza CSVs y genera Data Quality Report | Code Interpreter |
| 🔁 `frasohome-returns` | Interpreta devoluciones, motivos, reglas y riesgos | File Search / contexto |
| ⚙️ `frasohome-operations` | Revisa stock, tienda, pagos, conciliación, pedidos y SKUs | File Search / contexto |
| ✍️ `frasohome-storyteller` | Convierte evidencias en recomendación ejecutiva | Síntesis |
| 🧭 `frasohome-orchestrator` | Coordina especialistas y activa validación humana | Workflow / Python |

## 🎬 Storytelling de la sesión

### Escena 1 · “Preguntamos a FraSoHome” 🧠

Creamos un agente de conocimiento que responde usando documentos, no memoria del modelo. El público ve cómo File Search convierte políticas internas en respuestas operativas trazables.

### Escena 2 · “Miramos los datos” 📊

Creamos un agente con Code Interpreter que lee los CSV, ejecuta Python y genera un informe de calidad: nulos, duplicados, formatos, anomalías y acciones priorizadas.

### Escena 3 · “Orquestamos especialistas” 🧭

Lanzamos una pregunta ambigua sobre devoluciones online. El sistema reparte trabajo entre agentes y devuelve causa probable, evidencias, riesgos, acción de 7 días y métrica de seguimiento.

## 📦 Qué incluye este repositorio

```text
.
├── README.md                         # Esta presentación del repo
├── README_PORTAL.md                  # Paso a paso con interfaz gráfica
├── README_NOTEBOOK.md                # Paso a paso con notebook y código
├── README_CODE.md                    # Guía técnica del scaffold Python
├── agents.md                         # Playbook de agentes y buenas prácticas
├── notebooks/
│   └── frasohome_foundry_agents_demo.ipynb
├── case/
│   ├── fraso_home_caso.md
│   ├── fraso_home_storytelling_foundry.md
│   ├── data/                         # CSVs sintéticos
│   └── kb/                           # Políticas DOCX + Markdown
└── src/frasohome_agents/             # Código Python de la demo
```

## 🧠 Base de conocimiento

La carpeta [`case/kb`](case/kb) incluye políticas y guías internas:

- 📦 Política de devoluciones omnicanal.
- 📐 Diccionario de KPIs y reglas de cálculo.
- 🏬 Manual de tienda, caja y pagos mixtos.
- 💳 Guía de conciliación de pagos e-commerce.
- 🏷️ Taxonomía de catálogo y reglas SKU.
- ⭐ Guía de fidelización CRM.
- 🙋 FAQ interna de operaciones y atención.

Estos documentos se cargan en File Search para que el agente `frasohome-knowledge` responda con evidencia.

## 📊 Datos sintéticos

La carpeta [`case/data`](case/data) contiene CSVs de CRM, pedidos, POS, pagos, devoluciones, productos, stock y fact table.

Incluyen problemas intencionados para la demo:

- valores nulos,
- duplicados,
- claves inconsistentes,
- formatos de fecha heterogéneos,
- importes/cantidades anómalas,
- stock irregular.

## 🛣️ Elige tu ruta

### 🖱️ Ruta 1: diseñador gráfico de Foundry

Ideal para enseñar la demo en vivo desde el portal.

👉 [README_PORTAL.md](README_PORTAL.md)

Incluye:

- creación de agentes,
- configuración de File Search,
- configuración de Code Interpreter,
- creación de especialistas,
- diseño del workflow visual,
- prompts de prueba,
- checklist de sesión.

### 🐍 Ruta 2: notebook + Python

Ideal para una sesión hands-on técnica o hackathon.

👉 [README_NOTEBOOK.md](README_NOTEBOOK.md)

Incluye:

- preparación del entorno,
- ejecución del notebook,
- explicación de cada módulo Python,
- perfilado local con pandas,
- creación de agentes por SDK,
- ejecución del orquestador multiagente.

## ⚡ Quickstart código

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
copy .env.example .env
az login
```

Configura `.env`:

```text
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
MODEL_DEPLOYMENT=<deployment-name>
```

Prueba sin llamar a Azure:

```powershell
frasohome-agents check-assets
frasohome-agents local-profile
frasohome-agents create-agents --dry-run
```

## 🧪 Prompts canónicos

```text
Un cliente compró un sofá online, quiere devolverlo en tienda y usó un cupón. ¿Qué pasos debe seguir atención al cliente?
```

```text
Analiza los CSV de FraSoHome. Genera un Data Quality Report con tabla resumen y cinco acciones de limpieza priorizadas antes de crear features o dashboards.
```

```text
¿Por qué están subiendo las devoluciones online en iluminación y qué haríamos esta semana?
```

## ✅ Lo que se aprende

- Cuándo usar prompt agents, workflow agents o código.
- Cómo hacer grounding documental con File Search.
- Cómo usar Code Interpreter para análisis real de datos.
- Cómo diseñar contratos JSON entre agentes.
- Cómo separar reglas, cálculo, razonamiento y síntesis.
- Cómo mostrar trazabilidad, tool calls y validación humana.
- Cómo pasar de una demo visual a una implementación reproducible.

## 🧭 Material de apoyo

- [README_PORTAL.md](README_PORTAL.md): paso a paso con interfaz gráfica.
- [README_NOTEBOOK.md](README_NOTEBOOK.md): paso a paso con notebook y módulos Python.
- [README_CODE.md](README_CODE.md): guía técnica de ejecución por código.
- [agents.md](agents.md): playbook de desarrollo de agentes.
- [case/plan_sesion_practica_foundry_frasohome.md](case/plan_sesion_practica_foundry_frasohome.md): plan de sesión.
- [case/paso_a_paso_portal_foundry_agents_workflows.md](case/paso_a_paso_portal_foundry_agents_workflows.md): guía portal extendida.

## 📝 Nota

FraSoHome es un caso ficticio con datos sintéticos. Está diseñado para formación, demos y hackathons sobre Microsoft Foundry, agentes, grounding, workflows, análisis de datos y evaluación.
