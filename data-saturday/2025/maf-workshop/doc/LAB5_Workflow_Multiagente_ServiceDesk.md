# LAB 5 – Workflow Multiagente con Router

## Descripción General

Este notebook implementa un **workflow multiagente completo** para el Service Desk, introduciendo un **RouterAgent** que actúa como punto de entrada y director de orquestación. El sistema coordina tres agentes especializados trabajando en conjunto para proporcionar una experiencia integrada.

## Objetivos del LAB

1. **RouterAgent**: Agente clasificador que determina el flujo apropiado
2. **Workflow estructurado**: Coordinación automática entre agentes
3. **Decisiones inteligentes**: Enrutamiento basado en tipo de petición
4. **Integración completa**: KB + Memory + Tickets en un sistema unificado
5. **Orquestación avanzada**: Flujo multipasos con decisiones condicionales

## Arquitectura Multiagente

### Tres Agentes Especializados

```
┌──────────────────────────────────────────────────┐
│                  RouterAgent                     │
│         (Clasificador y Orquestador)             │
└────────┬─────────────────────────────────────────┘
         │ Decide el flujo
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌────────────────────────┐
│Knowledge│ │ ServiceDeskAgent       │
│Agent    │ │ (con Memory)           │
└────┬────┘ └───────┬────────────────┘
     │              │
     ▼              ▼
  kb/*.md      tickets.csv
               profiles.json
```

## RouterAgent: El Clasificador

### Propósito
Analiza la solicitud del usuario y determina:
1. **Tipo de petición**: información vs. acción
2. **Flujo apropiado**: KB primero, Service Desk directo, o ambos
3. **Estrategia de respuesta**: Cómo coordinar los agentes

### Estructura de Decisión

```python
@dataclass
class OrchestrationDecision:
    tipo: str               # "informacion" | "accion"
    usar_kb_primero: bool   # ¿Consultar KB antes?
    descripcion: str        # Explicación de la decisión
```

### Instrucciones del Router

```
Tu tarea es analizar la solicitud y devolver JSON:
{
  "tipo": "informacion" | "accion",
  "usar_kb_primero": true | false,
  "descripcion": "Explicación breve"
}

Definiciones:
- "informacion": Se responde con políticas/FAQs
- "accion": Requiere crear/actualizar tickets
- "usar_kb_primero": true si conviene consultar documentación primero
```

### Ejemplos de Clasificación

**Tipo: información**
```json
{
  "tipo": "informacion",
  "usar_kb_primero": true,
  "descripcion": "Pregunta sobre política que puede estar en KB"
}
```
- "¿Cuántos días de vacaciones tengo?"
- "¿Cuál es la política de portátiles?"

**Tipo: acción**
```json
{
  "tipo": "accion",
  "usar_kb_primero": false,
  "descripcion": "Solicitud que requiere crear ticket directamente"
}
```
- "Quiero pedir mis vacaciones del 1 al 15 de agosto"
- "Necesito un portátil nuevo"

**Tipo: mixto**
```json
{
  "tipo": "accion",
  "usar_kb_primero": true,
  "descripcion": "Puede beneficiarse de consultar KB antes de crear ticket"
}
```
- "No puedo conectarme a la VPN" (puede haber FAQ de solución)

## Workflow de Ejecución

### Función Principal: `run_service_workflow`

```python
async def run_service_workflow(email_usuario: str, texto_usuario: str) -> str:
    # Paso 1: RouterAgent analiza y clasifica
    decision = await router_decide(texto_usuario)
    
    # Paso 2: Si conviene, consultar KB
    if decision.tipo == "informacion" or decision.usar_kb_primero:
        kb_result = await knowledge_agent.run(texto_usuario)
        
        # Si KB resuelve y es tipo información -> terminar
        if es_respuesta_util(kb_result) and decision.tipo == "informacion":
            return kb_result
    
    # Paso 3: Si KB no resuelve o es tipo acción -> Service Desk
    sd_result = await service_desk_agent.run_with_profile(...)
    return sd_result
```

### Flujo Detallado

```
┌─────────────────────┐
│   Router decide     │
│   tipo y estrategia │
└──────┬──────────────┘
       │
       ├──── tipo="informacion" + usar_kb_primero=true
       │     │
       │     ▼
       │  ┌──────────────────┐
       │  │ KnowledgeAgent   │
       │  │ consulta KB      │
       │  └────┬─────────────┘
       │       │
       │       ├── Respuesta útil? ──YES──> [FIN]
       │       │
       │       └── NO (o ambigua)
       │           │
       ├──────────┴──── tipo="accion"
       │                │
       ▼                ▼
    ┌────────────────────────────┐
    │ ServiceDeskAgentMemory     │
    │ - Carga perfil usuario     │
    │ - Crea/actualiza ticket    │
    │ - Responde con confirmación│
    └────────────────────────────┘
              │
              ▼
           [FIN]
```

## Casos de Uso Implementados

### Caso 1: Consulta Pura de Información

**Input**: "¿Cuántos días de vacaciones tengo según la política?"

**Flujo**:
1. Router: `tipo="informacion"`, `usar_kb_primero=true`
2. KnowledgeAgent lee `politica_vacaciones.md`
3. Responde con la política encontrada
4. Workflow termina sin crear ticket

**Output**: "Según la política, tienes 23 días base, +1 si antigüedad > 5 años..."

---

### Caso 2: Acción Directa (Crear Ticket)

**Input**: "Quiero pedir mis vacaciones del 1 al 15 de agosto"

**Flujo**:
1. Router: `tipo="accion"`, `usar_kb_primero=false`
2. Va directamente a ServiceDeskAgentMemory
3. Carga perfil del usuario
4. Crea ticket con categoría="vacaciones"
5. Responde con confirmación e ID de ticket

**Output**: "✅ He creado el ticket #15 para tu solicitud de vacaciones del 1-15 agosto"

---

### Caso 3: Consulta + Acción (Flujo Completo)

**Input**: "No puedo conectarme a la VPN y tengo reunión urgente"

**Flujo**:
1. Router: `tipo="accion"`, `usar_kb_primero=true` (puede haber FAQ)
2. KnowledgeAgent intenta responder desde `faq_it.md`
3. Si hay FAQ de solución: responde + sugiere ticket si persiste
4. Si no hay FAQ: "No encuentro solución en KB"
5. ServiceDeskAgentMemory crea ticket con prioridad=alta
6. Responde con pasos inmediatos + confirmación de ticket

**Output**: 
```
He revisado la documentación. Para problemas de VPN:
1. [pasos del FAQ si existen]

He creado el ticket #16 de alta prioridad para que IT te contacte
urgentemente. Te avisaremos en los próximos 30 minutos.
```

---

### Caso 4: Actualizar Perfil + Consulta

**Input**: "Quiero que recuerdes que trabajo en Barcelona y prefiero Lenovo"

**Flujo**:
1. Router: `tipo="accion"` (modificación de datos)
2. ServiceDeskAgentMemory detecta actualización de perfil
3. Llama a `actualizar_perfil_usuario_fc(sede="Barcelona", preferencias_equipo="Lenovo")`
4. Confirma actualización

**Output**: "✅ He guardado tus preferencias: Barcelona, portátiles Lenovo"

## Componentes Técnicos

### Helpers de Soporte

#### `get_knowledge_agent()`
```python
async def get_knowledge_agent():
    agent = await create_knowledge_agent()
    async def cleanup():
        pass  # para compatibilidad con versiones MCP
    return agent, cleanup
```

#### `run_with_user_profile()`
```python
async def run_with_user_profile(agent, email, texto, thread):
    # Carga perfil del usuario
    perfil = get_user_profile(email)
    
    # Inyecta perfil como contexto en el mensaje
    mensaje = f"Perfil: {perfil}\n\nMensaje: {texto}"
    
    result = await agent.run(mensaje, thread=thread)
    return result, thread
```

### Gestión de Estado

- **RouterAgent**: Stateless, cada decisión es independiente
- **KnowledgeAgent**: Stateless, consulta documentación sin memoria
- **ServiceDeskAgentMemory**: Stateful, usa perfiles persistentes

### Persistencia de Datos

```
data/
├── tickets.csv         # Tickets creados por Service Desk
├── profiles.json       # Perfiles con memoria de usuario
kb/
├── politica_*.md       # Políticas corporativas
├── faq_*.md            # FAQs por departamento
out/
└── ticket_*.json       # Tickets individuales con contexto
```

## Ventajas del Sistema Multiagente

1. **Separación de responsabilidades**: Cada agente tiene un rol claro
2. **Escalabilidad**: Fácil agregar nuevos agentes especializados
3. **Inteligencia distribuida**: Cada agente experto en su dominio
4. **Optimización de recursos**: Solo se consulta lo necesario
5. **Trazabilidad**: Flujo claro y auditable
6. **Experiencia mejorada**: Respuestas más rápidas y precisas

## Demo Completo

```python
await demo_workflow_multiagente()

# Ejecuta automáticamente 4 casos:
# 1. "¿Cuántos días de vacaciones tengo?" → KB
# 2. "Quiero pedir vacaciones 1-15 agosto" → Ticket
# 3. "Recuerda: Barcelona, Lenovo" → Perfil
# 4. "No puedo conectarme VPN (urgente)" → KB + Ticket alta prioridad
```

## Tecnologías y Patrones

- **Orchestration Pattern**: Coordinación centralizada por Router
- **Chain of Responsibility**: Flujo secuencial con decisiones
- **Agent Specialization**: Agentes de propósito único
- **Context Injection**: Perfiles inyectados en mensajes
- **Decision Trees**: Lógica de enrutamiento estructurada
- **Dataclasses**: Estructuras tipadas para decisiones

## Próximos Pasos

En LAB 6 se añadirá:
- **Observabilidad**: Tracing con OpenTelemetry
- **Visualización**: Diagramas de workflow
- **Workflow Builder**: Construcción declarativa de flujos
- **Event Streaming**: Procesamiento de eventos en tiempo real
- **Métricas**: Monitoreo de performance de agentes
