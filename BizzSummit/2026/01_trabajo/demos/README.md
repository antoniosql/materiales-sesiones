# Demos · Bizz Summit 2026

Guía vigente: [guia-despliegue-manual.html](guia-despliegue-manual.html). Guion de toda la sesión: [01_guion-minuto-a-minuto.md](../01_guion-minuto-a-minuto.md). La presentación tiene 36 diapositivas: 30 visibles y 6 de respaldo ocultas.

| Demo | Diapositiva | Respaldo | Evidencia principal |
|---|---|---|---|
| Inventario | 13 | 31 | All agents, previa comprobación |
| Actividad | 16 | 32 | Audit; DSPM solo si se verificó |
| Decisión | 18 | 33 | Estado de Calculadora / Requests si existe |
| Claude | 23 | 34 | Diff ya hecho + búsqueda de Audit guardada |

## Estado de referencia y límites de la evidencia

Actualizado el 2 de octubre de 2026 a partir de `demos/agente-externo/fs-triage-devoluciones/instrucciones.md` y del código del repositorio. Esta revisión documental no ejecuta agentes ni comprueba el tenant en directo.

- 41 identidades en Entra; no equivale a 41 agentes visibles en All agents.
- Atajo, Calculadora, Asistente y fs-triage existen. Dev Admin creó los recursos de FraSoHome y es sponsor de Asistente y fs-triage. Las personas del relato son ficticias.
- Audit tiene conversaciones de los agentes Microsoft y, para Claude, 2 InvokeAgent, 46 ExecuteToolBySDK y 2 InferenceCall según el informe.
- La política DLP de IBAN está activa, pero el caso probado no disparó. La causa y la evidencia en DSPM no están verificadas.
- Calculadora no bloqueada en el ensayo. Solicitud pendiente del Asistente no confirmada. Verificar ambos estados antes de decidir el recorrido.
- La KB contiene FS-KB-02 obsoleta y FS-KB-10 de prompt injection: evitar consultas que puedan recuperarlos en la demo principal. Su retirada o una demo adversarial requieren preparación aparte.
- Work IQ es explicación de arquitectura; no se presenta como integración Mail/Word probada. Con S2S la skill se detiene con mensaje. Python + Claude necesita integración específica.

El montaje antiguo no es el guion de sala. No reconstruir agentes, ejecutar skills o resetear el repositorio para la demo. `agente/` conserva el material de construcción de Copilot Studio. La demo externa tiene su [guion específico](agente-externo/fs-triage-devoluciones/GUION-DEMO-4.md).
