# LAB 2 – Tools y CRUD de Tickets

## Descripción General

Este notebook amplía el trabajo del LAB 1 introduciendo **function calling** y herramientas (tools) para gestionar tickets de forma persistente. El agente IntakeAgent evoluciona para no solo clasificar solicitudes, sino también crear y gestionar tickets en un sistema de archivos.

## Objetivos del LAB

1. **Gestión de configuración**: Cargar variables desde archivos `.env`
2. **Implementar herramientas CRUD**: Crear, leer, actualizar tickets
3. **Persistencia de datos**: Almacenar tickets en CSV y JSON
4. **Function calling**: Registrar herramientas que el agente puede invocar
5. **Flujo completo**: Texto libre → JSON → Ticket guardado

## Estructura de Datos

### Tickets (`data/tickets.csv`)
Campos del ticket:
- `id`: Identificador único
- `fecha`: Fecha de creación
- `solicitante`: Email del usuario
- `departamento`: IT, RRHH, Facilities, Otro
- `categoria`: nuevo_equipo, incidencia, vacaciones, etc.
- `prioridad`: alta, media, baja
- `estado`: pendiente, en_progreso, resuelto_auto, resuelto_humano, cancelado
- `resumen`: Descripción corta
- `detalle`: Información extendida

### Almacenamiento Dual
- **CSV**: `data/tickets.csv` - Base de datos simple en texto
- **JSON**: `out/ticket_{id}.json` - Archivos individuales por ticket

## Herramientas Implementadas

### 1. Crear Ticket (`crear_ticket_fc`)
Crea un nuevo ticket con parámetros estructurados:
- Email del solicitante
- Departamento destino
- Categoría de solicitud
- Prioridad
- Resumen y detalle

Guarda automáticamente en CSV y genera JSON individual.

### 2. Actualizar Estado (`actualizar_estado_ticket_fc`)
Modifica el estado de un ticket existente:
- Busca por ID
- Actualiza el campo estado
- Sincroniza CSV y JSON

### 3. Listar y Buscar Tickets
- `listar_tickets_por_email`: Filtra tickets de un usuario
- `buscar_tickets_por_texto`: Búsqueda por contenido en resumen/detalle

## Agentes Implementados

### IntakeAgentJSON
- Versión mejorada del LAB 1
- Devuelve clasificación en formato JSON
- Sin capacidad de function calling

### ServiceDeskAgent
- **Agente con function calling habilitado**
- Registra herramientas como tools disponibles
- Decide automáticamente cuándo usar cada herramienta
- Puede preguntar por información faltante (como email)
- Responde en lenguaje natural confirmando acciones

## Flujos de Trabajo

### Flujo 1: Creación Manual de Ticket
1. IntakeAgentJSON clasifica la solicitud
2. Se parsea el JSON devuelto
3. Se llama manualmente a `crear_ticket()`
4. Se guarda en CSV y JSON

### Flujo 2: Creación Automática con Function Calling
1. Usuario envía solicitud en lenguaje natural
2. ServiceDeskAgent analiza el texto
3. El agente decide llamar a `crear_ticket_fc` con los parámetros apropiados
4. El framework ejecuta la función automáticamente
5. El agente confirma la creación al usuario

### Flujo 3: Gestión Completa
1. Usuario puede crear tickets
2. Usuario puede actualizar estados
3. Agente pregunta por información faltante
4. Todo queda persistido automáticamente

## Instrucciones del ServiceDeskAgent

El agente está instruido para:
- Entender solicitudes en lenguaje natural
- Decidir si crear un ticket o actualizar uno existente
- Solicitar el email del usuario si no está disponible
- Usar estados coherentes del ciclo de vida del ticket
- Responder confirmando las acciones realizadas
- NO inventar IDs ni emails

## Ejemplo de Interacción

```
Usuario: "Mi email es antonio.soto@empresa.local. 
         Necesito un portátil nuevo con 16GB de RAM para teletrabajar."

ServiceDeskAgent:
1. Extrae el email
2. Identifica: departamento=IT, categoria=nuevo_equipo, prioridad=media
3. Llama a crear_ticket_fc(...)
4. Responde: "✅ He creado el ticket #123 para tu solicitud de portátil..."
```

## Tecnologías y Conceptos

- **Function Calling**: El LLM decide cuándo y cómo invocar funciones
- **Pydantic**: Validación de tipos y documentación de parámetros
- **Type Annotations**: Descripciones legibles para el modelo
- **Pandas**: Manipulación de datos en CSV
- **Persistencia dual**: CSV para tablas, JSON para documentos

## Ventajas del Enfoque

1. **Automatización**: El agente decide qué herramientas usar
2. **Conversacional**: Interacción en lenguaje natural
3. **Robusto**: Validación de datos con Pydantic
4. **Trazable**: Tickets guardados en múltiples formatos
5. **Escalable**: Fácil agregar nuevas herramientas

## Próximos Pasos

En LAB 3 se añadirá **memoria persistente** del usuario (perfiles, preferencias) y se mejorará la personalización de las respuestas y tickets creados.
