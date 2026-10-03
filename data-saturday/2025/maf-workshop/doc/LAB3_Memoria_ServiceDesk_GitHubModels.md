# LAB 3 – Memoria y Perfiles de Usuario

## Descripción General

Este notebook extiende el sistema de Service Desk con capacidades de **memoria persistente**. El agente puede recordar preferencias y contexto del usuario entre sesiones, personalizando las interacciones y la creación de tickets.

## Objetivos del LAB

1. **Implementar sistema de perfiles**: Almacenar preferencias de usuario
2. **Persistencia de memoria**: Guardar perfiles en `data/profiles.json`
3. **Contextualización**: Usar información del perfil en la gestión de tickets
4. **Personalización**: Adaptar respuestas según preferencias del usuario
5. **Herramienta de actualización**: Permitir que el agente modifique perfiles

## Estructura de Perfiles

### Archivo `data/profiles.json`
Diccionario indexado por email con estructura:

```json
{
  "antonio.soto@empresa.local": {
    "email": "antonio.soto@empresa.local",
    "sede": "Barcelona",
    "preferencias_equipo": "Lenovo",
    "idioma_respuesta": "es"
  }
}
```

### Campos del Perfil
- **email**: Identificador único del usuario
- **sede**: Ciudad o ubicación de trabajo
- **preferencias_equipo**: Marca preferida de portátil
- **idioma_respuesta**: Idioma para las respuestas (es, en, etc.)

## Funciones de Gestión de Perfiles

### `load_all_profiles()`
Carga todos los perfiles desde el archivo JSON.

### `save_all_profiles(profiles)`
Guarda todos los perfiles de vuelta al archivo JSON.

### `get_user_profile(email)`
Obtiene el perfil de un usuario, creando uno básico si no existe.

### `update_user_profile(email, sede, preferencias_equipo, idioma_respuesta)`
Actualiza campos específicos del perfil de un usuario.

## Herramienta: actualizar_perfil_usuario_fc

Nueva tool registrada en el agente que permite:
- Actualizar sede del usuario
- Guardar preferencias de equipo
- Establecer idioma preferido
- Retornar el perfil completo actualizado

```python
def actualizar_perfil_usuario_fc(
    email: str,
    sede: str = "",
    preferencias_equipo: str = "",
    idioma_respuesta: str = ""
) -> Dict
```

## Agente: ServiceDeskAgentMemory

### Características
Evolución del ServiceDeskAgent del LAB 2 con:
- Acceso al perfil del usuario en cada interacción
- Uso de preferencias para enriquecer tickets
- Capacidad de actualizar perfiles automáticamente
- Respuestas personalizadas según contexto

### Herramientas Registradas
1. `crear_ticket_fc` - Crear tickets
2. `actualizar_estado_ticket_fc` - Cambiar estados
3. `actualizar_perfil_usuario_fc` - **NUEVA** Gestionar perfiles

### Instrucciones Mejoradas
El agente está instruido para:
- Consultar el perfil del usuario antes de actuar
- Detectar cuando el usuario proporciona información de perfil
- Llamar a `actualizar_perfil_usuario_fc` cuando corresponda
- Incluir información del perfil en los detalles de tickets
- Personalizar respuestas según preferencias

## Flujo de Trabajo con Memoria

### Función: `run_with_user_profile`
Inyecta el contexto del perfil en cada mensaje:

```python
async def run_with_user_profile(agent, email_usuario, texto_usuario, thread):
    perfil = get_user_profile(email_usuario)
    perfil_json = json.dumps(perfil)
    
    mensaje = f"""
    Perfil actual del usuario (JSON): {perfil_json}
    
    Mensaje del usuario: {texto_usuario}
    """
    
    result = await agent.run(mensaje, thread=thread)
    return result, thread
```

## Casos de Uso Implementados

### Caso 1: Configuración de Perfil
```
Usuario: "Quiero que recuerdes que trabajo en Barcelona 
         y prefiero portátiles Lenovo."

Agente:
1. Detecta información de perfil
2. Llama a actualizar_perfil_usuario_fc(
     email="antonio.soto@empresa.local",
     sede="Barcelona",
     preferencias_equipo="Lenovo"
   )
3. Confirma: "He guardado tus preferencias: sede Barcelona, 
              portátiles Lenovo"
```

### Caso 2: Uso de Memoria en Tickets
```
Usuario: "Necesito un portátil nuevo, por favor."

Agente:
1. Consulta perfil: sede=Barcelona, preferencias_equipo=Lenovo
2. Crea ticket con detalle enriquecido:
   "Usuario ubicado en Barcelona solicita portátil nuevo.
    Preferencia registrada: Lenovo"
3. Confirma creación con contexto personalizado
```

### Caso 3: Actualización de Estado con Contexto
```
Usuario: "Cambia el estado del ticket 1 a en_progreso."

Agente:
1. Carga perfil del usuario
2. Verifica que el ticket pertenezca al usuario
3. Actualiza estado
4. Responde en el idioma preferido del perfil
```

## Ventajas del Sistema de Memoria

1. **Personalización**: Tickets más ricos en contexto
2. **Eficiencia**: Usuario no repite información
3. **Consistencia**: Preferencias aplicadas automáticamente
4. **Experiencia mejorada**: Interacciones más naturales
5. **Persistencia**: Memoria entre sesiones

## Arquitectura de Datos

```
data/
├── tickets.csv         # Tickets con contexto enriquecido
├── profiles.json       # Perfiles de usuario persistentes
out/
└── ticket_*.json      # Tickets individuales con detalle del perfil
```

## Ejemplos de Interacción Completa

### Demo 1: Configurar Perfil
- Usuario proporciona preferencias
- Agente actualiza profiles.json
- Confirmación personalizada

### Demo 2: Crear Ticket con Memoria
- Usuario solicita equipo sin especificar detalles
- Agente consulta perfil existente
- Ticket incluye sede y preferencias automáticamente

### Demo 3: Actualizar Estado con Contexto
- Usuario cambia estado de ticket
- Agente usa idioma y contexto del perfil
- Respuesta adaptada a preferencias

## Tecnologías Clave

- **JSON**: Almacenamiento de perfiles estructurados
- **Context Injection**: Inyección de perfil en cada mensaje
- **Stateful Agents**: Agentes con memoria entre turnos
- **Enriched Function Calling**: Tools que usan contexto del usuario

## Próximos Pasos

En LAB 4 se introducirá:
- **Base de conocimiento (KB)**: Documentos de políticas y FAQs
- **Model Context Protocol (MCP)**: Acceso a filesystems
- **Agente KnowledgeAgent**: Consulta de documentación
- **Orquestación**: Integración entre KB y Service Desk
