# LAB 1 – IntakeAgent (Clasificador de Solicitudes)

## Descripción General

Este notebook introduce el desarrollo del primer agente del taller sobre **Microsoft Agent Framework** aplicado a un escenario de Service Desk interno. El objetivo principal es crear un agente inteligente que pueda clasificar y estructurar solicitudes en lenguaje natural.

## Objetivos del LAB

1. **Configurar el acceso a GitHub Models**: Conectar con el modelo `gpt-4o` mediante la API compatible con OpenAI
2. **Instalar Microsoft Agent Framework**: Configurar el framework para Python
3. **Crear IntakeAgent**: Desarrollar un agente basado en `ChatAgent` que clasifique solicitudes
4. **Generar salida estructurada**: Hacer que el agente devuelva JSON con la información clasificada

## Escenario Funcional

El agente trabaja en un **Service Desk interno** que recibe peticiones como:
- "Necesito un portátil nuevo con 16 GB de RAM para teletrabajar 3 días a la semana"
- "Quiero pedir mis vacaciones de agosto"
- "No puedo conectarme a la VPN de la empresa"

## Estructura JSON de Salida

El agente clasifica las solicitudes en el siguiente formato:

```json
{
  "departamento": "IT | RRHH | Facilities | Otro",
  "categoria": "nuevo_equipo | incidencia | vacaciones | certificado | mantenimiento | otro",
  "prioridad": "alta | media | baja",
  "resumen": "Texto corto que resuma la solicitud",
  "detalle": "Texto con más contexto, si es necesario"
}
```

## Componentes Clave

### 1. Configuración del Modelo
- **Endpoint**: GitHub Models (`https://models.inference.ai.azure.com`)
- **Autenticación**: GitHub Personal Access Token (PAT)
- **Modelo**: `gpt-4o`

### 2. Agente IntakeAgent
- Basado en `ChatAgent` de Microsoft Agent Framework
- Utiliza `OpenAIChatClient` para la comunicación con el modelo
- Dos versiones implementadas:
  - **Versión básica**: Responde en texto libre
  - **Versión JSON**: Devuelve estructura JSON consistente

### 3. Instrucciones del Agente

El agente recibe instrucciones específicas para:
- Clasificar solicitudes por departamento (IT, RRHH, Facilities)
- Determinar la categoría de la petición
- Asignar prioridad según urgencia e impacto
- Generar resúmenes concisos y detalles relevantes

## Flujo de Trabajo

1. Usuario envía una solicitud en lenguaje natural
2. IntakeAgent procesa el texto
3. El agente clasifica la información según las categorías definidas
4. Devuelve un JSON estructurado con la clasificación
5. El JSON puede ser usado posteriormente para crear tickets

## Tecnologías Utilizadas

- **Microsoft Agent Framework**: Framework para desarrollo de agentes
- **OpenAI API**: Interfaz compatible para GitHub Models
- **Python**: Lenguaje de programación
- **Asyncio**: Programación asíncrona
- **Python-dotenv**: Gestión de variables de entorno

## Resultados Esperados

Al finalizar este laboratorio, se obtiene:
- Un agente funcional que entiende solicitudes en español
- Clasificación automática de peticiones en formato estructurado
- Base para la creación de un sistema de ticketing automatizado
- Comprensión de cómo usar Microsoft Agent Framework con GitHub Models

## Próximos Pasos

Este laboratorio sienta las bases para LAB 2, donde se implementarán herramientas (tools) para crear tickets reales en un sistema de archivos CSV y se integrará el agente con operaciones CRUD.
