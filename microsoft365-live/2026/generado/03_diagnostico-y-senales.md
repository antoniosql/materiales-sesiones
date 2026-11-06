# Deuda semántica — diagnóstico en 4 pasos y señales de alerta

*Material de la sesión "Semantic Debt: why Copilot answers questions nobody asked" · Microsoft 365 Live 2026 · Antonio Soto*

> **Deuda semántica:** el coste acumulado de no haber acordado, escrito y dado dueño al *significado* de lo que la organización sabe.
> Tiene cuatro formas: **de definición** (qué es un cliente), **de versión** (cuál es el bueno), **tácita** (pregúntale a Lucía) y **de gobierno** (etiquetas, permisos y dueños que nadie mantiene).

## El diagnóstico: Preguntar → Rastrear → Recuperar → Asignar

### 1. Preguntar — inventario de preguntas
- Elige **un dominio**, no todo el tenant.
- Reúne **entre 20 y 30 preguntas reales**. Salen de los tickets, de los canales de Teams y de lo que se pregunta en comité.
- Para cada una, que **una persona con nombre** escriba la respuesta esperada.
- Si nadie es capaz de escribirla, ya has encontrado deuda.

### 2. Rastrear — fuente canónica
Clasifica cada pregunta:

| Estado | Significa |
|---|---|
| Canónica | Una sola fuente, vigente y con dueño |
| Duplicada | Varias fuentes que coinciden |
| Contradictoria | Varias fuentes que discrepan |
| Tácita | Solo está en cabezas |
| Inexistente | Nadie lo ha decidido |

### 3. Recuperar — lo que Copilot ve de verdad
- Lanza cada pregunta **como un usuario real de cada perfil**, nunca como admin.
- Anota la respuesta y las citas, y compáralas con la respuesta esperada.
- Busca la causa de cada diferencia: permisos · cifrado sin derechos de extracción · Restricted Content Discovery · contenido no indexado · versiones obsoletas que desplazan a la canónica.

**Tasa de Respuesta Canónica (TRC)** = preguntas respondidas correctamente **y** citando la fuente canónica ÷ total de preguntas.
Mídela antes y después. Es el número que entiende un comité.

### 4. Asignar — dueño y precio
Para cada hueco, rellena:

| Pregunta | Estado | Dueño del significado (negocio) | Frecuencia | Impacto | Acción |
|---|---|---|---|---|---|
| | | | Alta/Media/Baja | Alto/Medio/Bajo | Decidir · Consolidar · Documentar · Re-etiquetar · Retirar |

Negocio es dueño del **significado** e IT es dueña del **contenedor**. Una deuda sin dueño ya no es deuda: es una pérdida que todavía no has contabilizado.

## Ocho señales de alerta antes de desplegar

1. ☐ Nadie es capaz de nombrar en 30 segundos al dueño de "cliente" o del KPI principal.
2. ☐ Los comités empiezan conciliando cifras.
3. ☐ Hay bibliotecas con solo las columnas por defecto y carpetas tipo `Varios`, `Antiguo`, `Final`.
4. ☐ En una misma biblioteca conviven ficheros con `final`, `v2`, `bueno` o `definitivo`.
5. ☐ Una sola etiqueta lo marca casi todo, o hay etiquetas con cifrado que nadie sabe explicar.
6. ☐ Hay sitios sin propietario activo o de personas que ya no están en ese equipo.
7. ☐ El onboarding de un proceso es "siéntate una semana con alguien".
8. ☐ El piloto de Copilot se evalúa con "¿te gusta?" y no con preguntas que tienen respuesta esperada.

**Lectura (heurística):** 0–2 → adelante · 3–5 → diagnostica antes de ampliar · 6–8 → para el despliegue y paga primero.

## Qué arreglar con qué

| Deuda | Herramienta | Lo que no hace |
|---|---|---|
| De definición | Glosario del Unified Catalog de Purview (con dueño y *steward*) · ontología de Fabric IQ (preview) para el dato | Decidir la definición |
| De versión | Term store + columnas *Estado / Dominio / Propietario* · Knowledge Agent (preview) para el atraso · Copilot Studio con filtrado por metadatos | Elegir cuál es el oficial |
| De gobierno | Purview (etiquetas, derechos, DSPM for AI, ciclo de vida) · SharePoint Advanced Management | RCD esconde, pero no cura |
| Tácita | Documentar y nombrar un dueño; después, Work IQ y *skills* | Inventar lo que nadie ha escrito |

## La frase para tu comité

> **"No tenemos un problema de IA. Tenemos treinta años de acuerdos sin firmar, y la IA acaba de leerlos en voz alta."**

No pidas más licencias. Pide **tres dueños, noventa días y un test set**, y mide la TRC antes y después.
