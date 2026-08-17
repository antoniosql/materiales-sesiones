# Durable Agents en Azure (Python)

Este documento explica cómo ejecutar el agente durable del LAB 7 en Azure Functions con estado durable y endpoints HTTP automáticos usando Microsoft Agent Framework.

## 1) Requisitos

- Python 3.10+ (recomendado 3.11/3.12)
- Azure Functions Core Tools (v4)
- Cuenta de Azure y Azure CLI
- Azure OpenAI con un deployment (por ejemplo: `gpt-4o-mini`)

Paquetes Python (local):

```pwsh
pip install -r requirements-azure.txt
```

Opcional: instalar Azure Functions Core Tools si no lo tienes:

```pwsh
npm i -g azure-functions-core-tools@4 --unsafe-perm true
```

## 2) Variables de entorno

Configura las variables necesarias para Azure OpenAI:

```pwsh
$env:AZURE_OPENAI_ENDPOINT = "https://<tu-endpoint>.openai.azure.com"
$env:AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4o-mini"
```

Para autenticación de identidad administrada/CLI en local, basta con iniciar sesión con Azure CLI:

```pwsh
az login
```

## 3) Estructura de un proyecto de Functions (rápido)

Crea un proyecto vacío de Azure Functions (Python) en una carpeta aparte (o subcarpeta `azure-func/`):

```pwsh
mkdir azure-func; cd azure-func
func init --worker-runtime python --docker "false"
```

Crea una función HTTP (el binding lo aporta AgentFunctionApp internamente, pero el proyecto necesita hostear el app):

```pwsh
func new --template "HTTP trigger" --name agentapp
```

Esto te generará algo como `agentapp/__init__.py`. Reemplázalo por un punto de entrada mínimo que haga import del `AgentFunctionApp` que expone tu agente durable.

## 4) Código mínimo del app (ejemplo)

Crea un fichero `function_app.py` en la raíz del proyecto de Functions con el siguiente contenido (adapta a tu modelo):

```python
import os
from agent_framework.azure import AzureOpenAIChatClient, AgentFunctionApp
from azure.identity import DefaultAzureCredential

# Variables
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
if not endpoint:
    raise RuntimeError("AZURE_OPENAI_ENDPOINT no está configurada")
model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")

# Instrucciones del agente
SERVICE_DESK_INSTRUCTIONS = """
Eres un agente de Service Desk interno.
- Entiende solicitudes (vacaciones, incidencias IT, facilities...)
- Llama a tools cuando debas crear/actualizar tickets
- Responde claro y en español (no JSON para el usuario)
Si falta información crítica (email, id), pídela.
"""

# Tools (trae tus funciones desde tu repo; p.ej. import desde un módulo común)
from tickets_tools import crear_ticket_fc, actualizar_estado_ticket_fc  # <-- crea este módulo

# Cliente + agente durable
chat_client = AzureOpenAIChatClient(
    endpoint=endpoint,
    deployment_name=model,
    credential=DefaultAzureCredential(),
)

durable_agent = chat_client.create_agent(
    name="DurableServiceDeskAgent",
    instructions=SERVICE_DESK_INSTRUCTIONS,
    tools=[crear_ticket_fc, actualizar_estado_ticket_fc],
)

# Esta es la aplicación de Functions que hostea el agente y gestiona estado durable
app = AgentFunctionApp(agents=[durable_agent])
```

Luego, crea un pequeño módulo `tickets_tools.py` copiando tus tools del repo (las que ya usas en el LAB 7):

```python
# tickets_tools.py
from typing import Dict, Annotated
from pydantic import Field
from datetime import datetime
import json
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data"); OUT_DIR = Path("out")
DATA_DIR.mkdir(exist_ok=True); OUT_DIR.mkdir(exist_ok=True)
TICKETS_CSV = DATA_DIR / "tickets.csv"
if not TICKETS_CSV.exists():
    import pandas as pd
    pd.DataFrame(columns=["id","fecha","solicitante","departamento","categoria","prioridad","estado","resumen","detalle"]).to_csv(TICKETS_CSV, index=False)

def load_tickets():
    return pd.read_csv(TICKETS_CSV, dtype=str).fillna("") if TICKETS_CSV.exists() else pd.DataFrame(columns=["id","fecha","solicitante","departamento","categoria","prioridad","estado","resumen","detalle"]) 

def crear_ticket_fc(
    desde_email: Annotated[str, Field(description="Correo del solicitante")],
    departamento: Annotated[str, Field(description="IT, RRHH, Facilities u otro")],
    categoria: Annotated[str, Field(description="nuevo_equipo, incidencia, vacaciones, etc.")],
    prioridad: Annotated[str, Field(description="alta, media, baja")],
    resumen: Annotated[str, Field(description="Resumen corto")],
    detalle: Annotated[str, Field(description="Detalle extendido")],
) -> Dict:
    data = load_tickets()
    next_id = 1 if data.empty else int(pd.to_numeric(data['id'], errors='coerce').max() or 0) + 1
    nuevo = {
        'id': str(next_id),
        'fecha': datetime.now().strftime('%Y-%m-%d'),
        'solicitante': desde_email,
        'departamento': departamento or 'Otro',
        'categoria': categoria or 'otro',
        'prioridad': prioridad or 'media',
        'estado': 'pendiente',
        'resumen': (resumen or '')[:200],
        'detalle': detalle or '',
    }
    data = pd.concat([data, pd.DataFrame([nuevo])], ignore_index=True)
    data.to_csv(TICKETS_CSV, index=False, encoding='utf-8')
    (OUT_DIR / f"ticket_{next_id}.json").write_text(json.dumps(nuevo, ensure_ascii=False, indent=2), encoding='utf-8')
    return nuevo


def actualizar_estado_ticket_fc(
    id_ticket: Annotated[int, Field(description="Id del ticket a actualizar")],
    nuevo_estado: Annotated[str, Field(description="pendiente, en_progreso, resuelto_auto, resuelto_humano, cancelado")],
) -> Dict:
    data = load_tickets()
    if data.empty:
        return {"ok": False, "mensaje": "No hay tickets."}
    mask = data['id'] == str(id_ticket)
    if not mask.any():
        return {"ok": False, "mensaje": f"No existe el ticket {id_ticket}"}
    data.loc[mask, 'estado'] = nuevo_estado
    data.to_csv(TICKETS_CSV, index=False, encoding='utf-8')
    actualizado = data.loc[mask].iloc[0].to_dict()
    p = OUT_DIR / f"ticket_{id_ticket}.json"
    if p.exists():
        p.write_text(json.dumps(actualizado, ensure_ascii=False, indent=2), encoding='utf-8')
    return {"ok": True, "ticket": actualizado}
```

> Nota: En producción, es mejor almacenar tickets en una base de datos (Cosmos DB, SQL, etc.) en lugar de CSV/archivos locales.

## 5) Ejecutar en local

Desde la carpeta del proyecto de Functions:

```pwsh
func start
```

Verás los endpoints HTTP generados. El runtime gestionará **conversaciones durables** (threads) por ti.

## 6) Desplegar a Azure

Ejemplo rápido con Azure CLI (reemplaza nombres):

```pwsh
# Login y suscripción
az login
az account set --subscription "<SUBSCRIPTION_ID>"

# Crear grupo de recursos
az group create -n rg-agent-demo -l westeurope

# Crear Function App (consumo) y storage
$storage = "stagent$((Get-Random))"
az storage account create -n $storage -g rg-agent-demo -l westeurope --sku Standard_LRS
az functionapp create -n fa-agent-demo -g rg-agent-demo -s $storage --consumption-plan-location westeurope --runtime python --functions-version 4

# Configurar settings
az functionapp config appsettings set -g rg-agent-demo -n fa-agent-demo --settings \
  AZURE_OPENAI_ENDPOINT=$env:AZURE_OPENAI_ENDPOINT \
  AZURE_OPENAI_DEPLOYMENT_NAME=$env:AZURE_OPENAI_DEPLOYMENT_NAME

# Desplegar (desde la carpeta del proyecto de Functions)
func azure functionapp publish fa-agent-demo
```

Con esto tendrás un agente duradero con estado hospedado en Azure Functions. Ajusta permisos/identidad si usas `DefaultAzureCredential` (por ejemplo, System Assigned Managed Identity) para acceder a Azure OpenAI.
