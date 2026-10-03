# LAB 4 – Knowledge Base + MCP Filesystem

## Descripción General

Este notebook introduce una **base de conocimiento (KB)** local y el uso del **Model Context Protocol (MCP)** para que los agentes puedan consultar documentación de políticas y FAQs. Se implementa un nuevo agente especializado en consultar documentación y se integra con el Service Desk.

## Objetivos del LAB

1. **Crear base de conocimiento**: Documentos markdown con políticas internas
2. **Implementar herramientas de KB**: Funciones para listar y leer documentos
3. **Agente KnowledgeAgent**: Especializado en consultar documentación
4. **Orquestación multiagente**: KB + Service Desk trabajando juntos
5. **MCP integration**: Usar Model Context Protocol con filesystem

## Estructura de la Base de Conocimiento

### Carpeta `kb/`
Contiene documentos markdown con información corporativa:

```
kb/
├── politica_portatiles.md    # Política de asignación de equipos
├── politica_vacaciones.md    # Política de días libres
├── faq_it.md                  # Preguntas frecuentes IT
└── faq_rrhh.md                # Preguntas frecuentes RRHH
```

### Ejemplo de Contenido

**politica_vacaciones.md**:
```markdown
# Política de Vacaciones

- Días base: 23 laborables
- +1 día si antigüedad > 5 años
- +2 días si antigüedad > 10 años
```

**politica_portatiles.md**:
```markdown
# Política de Portátiles

- Un portátil por persona
- Segundo portátil solo en casos excepcionales aprobados por IT
```

## Herramientas de Knowledge Base

### Versión Simple (sin MCP)

#### `kb_list_files()`
Lista todos los archivos `.md` disponibles en la carpeta KB.

```python
def kb_list_files() -> List[str]:
    return [f.name for f in KB_DIR.glob("*.md")]
```

#### `kb_read_file(filename)`
Lee el contenido completo de un documento específico.

```python
def kb_read_file(filename: str) -> str:
    path = KB_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"No se encontró {filename}")
    return path.read_text(encoding="utf-8")
```

## Agente: KnowledgeAgent

### Propósito
Agente especializado en consultar y responder desde la documentación interna.

### Instrucciones
```
- Leer la pregunta del usuario
- Decidir qué documentos pueden contener la respuesta
- Usar kb_list_files y kb_read_file solo en documentos relevantes
- Responder citando solo información de la documentación
- Si no encuentra respuesta, sugerir crear un ticket
- NO inventar políticas que no estén documentadas
```

### Herramientas Registradas
- `kb_list_files` - Explorar documentos disponibles
- `kb_read_file` - Leer contenido específico

### Ejemplo de Uso

```python
agent = await create_knowledge_agent()
pregunta = "¿Puedo pedir un segundo portátil según la política?"

# El agente:
# 1. Lista archivos con kb_list_files()
# 2. Identifica politica_portatiles.md como relevante
# 3. Lee el contenido con kb_read_file("politica_portatiles.md")
# 4. Responde citando la política encontrada
```

## Orquestación: KB + Service Desk

### Función: `responder_con_kb_y_service_desk`

Flujo de decisión inteligente:

```python
async def responder_con_kb_y_service_desk(email_usuario, texto_usuario):
    # Paso 1: Intentar con KnowledgeAgent
    kb_result = await knowledge_agent.run(texto_usuario)
    
    # Paso 2: Analizar si KB fue suficiente
    if "no encuentro" in kb_result.lower():
        # KB no tiene la respuesta -> Delegar al Service Desk
        sd_result = await service_desk_agent.run(...)
        return sd_result
    else:
        # KB resolvió la consulta
        return kb_result
```

### Heurística de Decisión
El sistema considera que la KB no es suficiente si la respuesta contiene:
- "no encuentro"
- "no aparece en la documentación"
- "no está en la base de conocimiento"

En estos casos, automáticamente se delega al ServiceDeskAgentMemory para crear un ticket.

## Model Context Protocol (MCP)

### ¿Qué es MCP?
Protocolo estándar para que agentes accedan a recursos externos (filesystems, bases de datos, APIs) de forma estructurada.

### Implementación con Filesystem

#### `create_filesystem_mcp_tool()`
Crea un servidor MCP para acceso al filesystem:

```python
async def create_filesystem_mcp_tool():
    mcp_tool = MCPStdioTool(
        name="filesystem",
        command="uvx",
        args=["mcp-server-filesystem"]
    )
    await mcp_tool.connect()
    return mcp_tool
```

#### Requisitos
- `uv` / `uvx` instalado
- Paquete `mcp-server-filesystem`

### KnowledgeAgent con MCP

Versión mejorada que usa MCP en lugar de funciones locales:

```python
async def create_knowledge_agent_mcp():
    # 1. Crear y conectar servidor MCP
    filesystem_mcp = await create_filesystem_mcp_tool()
    
    # 2. Obtener funciones expuestas por MCP
    mcp_tools = [*filesystem_mcp.functions]
    
    # 3. Crear agente con tools MCP
    agent = ChatAgent(
        chat_client=chat_client,
        instructions=KNOWLEDGE_INSTRUCTIONS,
        tools=mcp_tools
    )
    
    return agent, filesystem_mcp
```

### Ventajas de MCP

1. **Estandarización**: Protocolo común para recursos externos
2. **Seguridad**: Control de acceso centralizado
3. **Escalabilidad**: Fácil agregar nuevos servidores MCP
4. **Interoperabilidad**: Misma interfaz para diferentes recursos

## Casos de Uso Completos

### Caso 1: Consulta de Política (resuelto por KB)
```
Usuario: "¿Cuántos días de vacaciones tengo?"

Flujo:
1. KnowledgeAgent lista archivos
2. Identifica politica_vacaciones.md
3. Lee el contenido
4. Responde: "Según la política, tienes 23 días base..."
5. NO se crea ticket
```

### Caso 2: Solicitud de Acción (delegado a Service Desk)
```
Usuario: "Quiero pedir mis vacaciones del 1 al 15 de agosto"

Flujo:
1. KnowledgeAgent intenta responder
2. Detecta que requiere acción, no solo información
3. Delega a ServiceDeskAgentMemory
4. Se crea ticket de vacaciones
5. Usuario recibe confirmación con ID de ticket
```

### Caso 3: Información No Documentada
```
Usuario: "¿Cuál es el proceso para solicitar software especializado?"

Flujo:
1. KnowledgeAgent busca en KB
2. No encuentra documentación relevante
3. Responde: "No encuentro esta información en la KB"
4. Sugiere: "Te recomiendo crear un ticket al Service Desk"
5. Sistema delega a ServiceDeskAgentMemory si usuario confirma
```

## Arquitectura del Sistema

```
┌─────────────────────────────────────────┐
│         Usuario                         │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Orquestador (responder_con_kb_y_sd)   │
└────┬────────────────────────────────┬───┘
     │                                │
     ▼                                ▼
┌────────────────┐          ┌──────────────────────┐
│ KnowledgeAgent │          │ ServiceDeskAgent     │
│  (con MCP)     │          │  (con Memory)        │
└────┬───────────┘          └──────────┬───────────┘
     │                                  │
     ▼                                  ▼
┌────────────────┐          ┌──────────────────────┐
│  MCP Filesystem│          │ tickets.csv          │
│  kb/*.md       │          │ profiles.json        │
└────────────────┘          └──────────────────────┘
```

## Tecnologías y Conceptos

- **Model Context Protocol (MCP)**: Estándar para recursos externos
- **MCPStdioTool**: Implementación MCP sobre stdio
- **Multi-Agent Orchestration**: Coordinación entre agentes especializados
- **Decision Heuristics**: Lógica para determinar flujo apropiado
- **Knowledge Base**: Repositorio de documentación estructurada

## Próximos Pasos

En LAB 5 se implementará:
- **RouterAgent**: Agente de enrutamiento que decide el flujo
- **Workflow estructurado**: Flujo multiagente completo
- **Decisiones basadas en clasificación**: Router → KB o Service Desk
- **Integración completa**: Todos los componentes trabajando juntos
