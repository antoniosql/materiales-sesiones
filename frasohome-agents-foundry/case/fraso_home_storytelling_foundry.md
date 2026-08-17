# Caso y storytelling FraSoHome para Microsoft Foundry

Fuente: extracción narrativa de `Global AI Chapter - Agentes_Microsoft_Foundry_FraSoHome.pptx`.

## Hilo conductor

FraSoHome es un retailer omnicanal de hogar y decoración con datos repartidos entre CRM, POS, e-commerce, ERP, devoluciones y stock. La historia de la demo no intenta demostrar que la IA “lo hace todo”, sino que un sistema agentic bien diseñado reduce fricción, mejora trazabilidad y convierte datos desordenados en decisiones accionables.

## Problema de negocio

FraSoHome necesita una vista única y fiable para responder cuatro preguntas sencillas pero difíciles de contestar con datos fragmentados:

- ¿Qué vendemos?
- ¿A quién vendemos?
- ¿En qué canal vendemos?
- ¿Con qué margen y con qué patrón de devolución?

Los dolores visibles en la presentación son nulos, duplicados, fechas y claves inconsistentes, productos sin mapeo, devoluciones cruzadas entre canales, stock negativo o fuera de rango y decisiones poco fiables por falta de integración.

## Tesis de la sesión

El valor de Microsoft Foundry aparece cuando conectamos conocimiento, datos y acción sobre un proceso concreto. El agente no sustituye las reglas de negocio ni las políticas: las hace accesibles, trazables y operativas. La pregunta de diseño es qué debe razonar el agente y qué debe quedar gobernado por reglas, validaciones y herramientas deterministas.

## Arquitectura narrativa

La presentación propone un sistema multiagente coordinado por un orquestador:

- **Orquestador:** enruta la intención, mantiene estado y sintetiza la respuesta final.
- **Knowledge:** responde con grounding sobre documentos, políticas, catálogo y promociones.
- **Data Quality:** perfila CSVs, detecta anomalías y propone limpieza.
- **Customer:** calcula métricas de cliente, RFM, preferencias y experiencia.
- **Operations:** analiza stock, pedidos, tiendas y posibles impactos operativos.
- **Returns:** explica devoluciones, motivos, tasas y patrones por canal/categoría.
- **Storyteller:** convierte evidencias técnicas en una recomendación ejecutiva clara.

El contrato entre agentes se basa en salidas estructuradas:

```json
{
  "hallazgos": [],
  "evidencias": [],
  "riesgos": [],
  "siguiente_accion": "..."
}
```

## Recorrido de demostración

### Escena 1: Preguntamos a FraSoHome

Demo de agente de conocimiento con File Search. El usuario pregunta: “Un cliente compró un sofá online, quiere devolverlo en tienda y usó un cupón. ¿Qué pasos debe seguir atención al cliente?”.

La salida esperada es una respuesta breve con pasos operativos, evidencia del documento y aviso explícito si falta un dato crítico.

### Escena 2: Miramos los datos

Demo de Code Interpreter sobre los CSVs de FraSoHome. El agente lee CRM, pedidos, líneas, devoluciones, POS, stock y productos; perfila datos; detecta anomalías; sugiere limpieza; y resume impacto en un Data Quality Report.

El cierre narrativo es: “Ahora ya tenemos una lista priorizada de problemas antes de construir features o dashboards”.

### Escena 3: Orquestamos especialistas

Demo multiagente con una pregunta ambigua: “¿Por qué están subiendo las devoluciones online en iluminación y qué haríamos esta semana?”.

El router detecta que la intención mezcla calidad de datos, operaciones, cliente y devoluciones. Cada especialista aporta evidencias y Storyteller devuelve una decisión con cinco piezas: causa probable, evidencia, impacto, acción de 7 días y métrica de seguimiento.

## Mensaje final para la audiencia

Foundry aporta un lugar común para pasar de idea a producción: agentes, herramientas, workflows, seguridad, observabilidad, evaluación y despliegue dentro de Azure. La ruta recomendada es empezar con prompt agents y workflows para que el proceso sea visible, y mover a SDK/Agent Framework cuando hagan falta lógica propia, estado, tests, CI/CD o integración avanzada.
