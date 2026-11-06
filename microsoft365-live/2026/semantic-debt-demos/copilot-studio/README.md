# Agente «Asistente Comercial FraSoHome» (demo 4)

Copilot Studio no permite crear desde cero, por código, un agente con una fuente de SharePoint
y filtrado por metadatos. El flujo reproducible es este:

1. **Primera vez (a mano, 10 minutos)**: monta el agente en el entorno `PP_ENVIRONMENT_ID`.
2. **Exporta la plantilla**: `semdebt agent extract-template --bot <id o schema name>`.
   Se guarda en `AGENT_TEMPLATE_FILE` (por defecto `copilot-studio/asistente-comercial.template.yaml`).
   Súbela al repo para tenerla en el repo.
3. **A partir de ahí**: `semdebt agent create` lo recrea y publica, y `semdebt cleanup` lo borra.

> `extract-template` registra el agente como *reutilizado*: `semdebt cleanup` no borra un agente que
> hayas montado tú a mano. El que crea `semdebt agent create` sí se borra.

## Montaje la primera vez

En el Copilot Studio actual: *Inicio › Otras formas de crear › Agente (Estándar)*. Si la cuenta no tiene
licencia, Conocimiento aparece bloqueado: *Iniciar una prueba* (30 días).

| Paso | Valor |
|---|---|
| Nombre | `Asistente Comercial FraSoHome` (el de `AGENT_DISPLAY_NAME`) |
| Solución | la de `AGENT_SOLUTION` |
| Instrucciones | pega [`instrucciones.md`](instrucciones.md) |
| Conocimiento | SharePoint → `https://<SP_HOST>/sites/FraSoHome-KB-Oficial/Documentos compartidos` (solo esta biblioteca; nunca FraSoHome-Comercial) |
| Conocimiento general | Desactivado, para que no complete con la web |
| Filtrado de la fuente | Conocimiento › la fuente › *Configuración avanzada*: **Incluir solo información › Nombre de archivo › no contiene › `FS-KB-02`**. El filtro solo admite propiedades estándar (autor, nombre, tipo, fechas, título), no columnas propias como `Estado`: la regla «solo Vigente» la refuerzan las instrucciones |
| Orquestación | Configuración › IA generativa › **Sí** (orquestación generativa; si no, las instrucciones no se aplican) |
| Respuestas sin fundamentación / Internet | Desactivados |
| Canales | Teams y Microsoft 365 Copilot |
| Autenticación | Microsoft (Entra ID) para que la evaluación pueda invocarlo como Laura |

Comprueba en el panel de prueba las cuatro preguntas de la demo 4 antes de exportar la plantilla:

1. `¿Cuál es el plazo de devolución para compras online?` → 45 días, cita FS-KB-01 v1.3.
2. `¿Cuántos clientes activos tenía FraSoHome al cierre de 2025?` → pregunta qué definición quieres → 100.
3. `¿Cómo evolucionaron las ventas netas en el Q4 respecto al Q3?` → +2,5 %, declarando la fórmula.
4. `Devolución en tienda de pedido online pagado con tarjeta y puntos` → "no está documentado", remite a Jorge T. (lo saca de FS-KB-00, el mapa de dominios y responsables).

## Evaluación por código

`semdebt evaluate --target agent` invoca el agente como Laura con el SDK de Microsoft 365 Agents
(`microsoft-agents-copilotstudio-client`). Necesita el permiso delegado
`CopilotStudio.Copilots.Invoke` (Power Platform API) en el registro de aplicación.
