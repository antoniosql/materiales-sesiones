# 🏢 Escenario de Negocio: Service Desk Inteligente Multiagente
## 🎯 Contexto Organizativo

La empresa ACME Corp., una organización de tamaño medio con más de 450 empleados, gestiona diariamente decenas de solicitudes internas relacionadas con:

* IT (soporte técnico, incidencias, nuevos equipos)
* RRHH (vacaciones, certificados, actualización de datos personales)
* Facilities (mantenimiento, salas, infraestructura física)

Actualmente, estas solicitudes llegan por correo, Microsoft Teams, o mediante formularios dispersos.
El equipo de Service Desk sufre:

* Retrasos por falta de clasificación inicial
* Dudas por falta de unificación de políticas internas
* Carga manual elevada en creación y actualización de tickets
* Necesidad de responder dudas repetidas de empleados
* Contexto perdido entre solicitudes (no hay “memoria” del usuario en interacciones repetidas)

El objetivo estratégico de ACME Corp. es evolucionar hacia un modelo de atención inteligente y unificado, que reduzca carga operativa, mejore los tiempos de respuesta y aumente la satisfacción del empleado.

## 🚀 Visión: Un Service Desk Inteligente Multiagente

Para modernizar el proceso, ACME Corp. decide implementar un sistema multiagente basado en IA generativa capaz de:

✔ Interpretar solicitudes en lenguaje natural

Independientemente del canal (chat web, Teams, etc.), el sistema debe recibir mensajes como:

* “No puedo conectarme a la VPN”
* “¿Cuántos días de vacaciones tengo?”
* “Necesito un portátil nuevo para teletrabajar”

Y entender su intención, urgencia y categoría.

✔ Resolver automáticamente consultas informativas

El sistema debe acceder a la Base de Conocimiento (KB) interna:

* Políticas de vacaciones
* Política de asignación de portátiles
* Preguntas frecuentes de IT y RRHH

## Normativas internas

Cuando la consulta sea puramente informativa, responder sin generar carga para Service Desk.

✔ Crear o actualizar tickets automáticamente

Cuando la petición requiere acción:

* Crear tickets en el sistema corporativo (CSV/DB)
* Actualizar estado
* Asignar prioridad
* Recoger metadatos clave
* Registrar detalle estructurado

✔ Recordar preferencias del empleado

Cada empleado puede tener preferencias como:

* Sede habitual (Madrid / Barcelona)
* Preferencia de marca de portátil (“Lenovo”)
* Idioma de comunicación (“es” / “en”)

El sistema debe recordar esta información y reutilizarla automáticamente.

✔ Coordinar agentes especializados

En lugar de un solo agente monolítico, el diseño se basa en agentes especializados, cada uno con su responsabilidad:

Agente	Rol
RouterAgent	Clasifica la solicitud (información / acción) y decide la ruta
KnowledgeAgent	Usa la KB para responder preguntas basadas en políticas
ServiceDeskAgent	Gestiona tickets, memoria y acción operativa

Estos agentes colaboran mediante un Workflow diseñado con Microsoft Agent Framework.

🧠 Arquitectura Multiagente (visión conceptual)

El flujo operativo es:

Usuario
   ↓
RouterAgent (LLM)
   ├─> Si es información → KnowledgeAgent
   │        │
   │        └─> KB Responde → Respuesta final
   │
   └─> Si es acción (o KB insuficiente) → ServiceDeskAgent
                     │
                     ├─ Tools: crear_ticket, actualizar_estado_ticket
                     ├─ Tools: actualizar_perfil_usuario
                     └─> Respuesta final + ticket generado

## 🧱 Componentes técnicos clave
🔹 1. ChatAgent (LLM)

Los agentes se implementan con ChatAgent, usando modelos de GitHub Models (por ejemplo, GPT-4o).

🔹 2. AgentExecutor

Envuelve un agente para integrarlo en workflows como un nodo ejecutable.

🔹 3. Workflow

Define la orquestación entre agentes:

* RouterExecutor → decide la ruta
* KnowledgeExecutor → responde desde KB
* ServiceDeskExecutor → ejecuta acciones

🔹 4. Tools

Funciones Python expuestas al agente:

* crear_ticket_fc
* actualizar_estado_ticket_fc
* actualizar_perfil_usuario_fc
* kb_list_files
* kb_read_file

🔹 5. Observabilidad (OpenTelemetry)

El sistema emite trazas:

* Inicio y fin de cada executor
* Llamadas a agentes
* Decisiones del router
* Acceso a KB
* Creación de tickets

Permite construir dashboards técnicos y auditoría.

🔹 6. WorkflowViz

Genera diagramas visuales del flujo de agentes:

* En Mermaid para documentación técnica
* En DOT/PNG/SVG para presentaciones

