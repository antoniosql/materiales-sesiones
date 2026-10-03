# FraSoHome · escenario de la sesión

Empresa ficticia de retail y proceso de devoluciones omnicanal. La sesión compara cuatro agentes en un mismo proceso: Atajo y Calculadora (Agent Builder), Asistente (Copilot Studio) y fs-triage (Claude Agent SDK, triaje de un buzón local de muestra).

## Relato y realidad del laboratorio

El maker que cambia de equipo, el responsable de tienda y los nombres Álvaro/Marta son personajes hipotéticos. No atribuirles recursos que en las fichas pertenecen a Dev Admin. Diferenciar propietario técnico, responsable de negocio y sponsor. El cambio de departamento no produce automáticamente un agente sin owner en el portal.

## Estado de referencia y límites de la evidencia

Actualizado el 2 de octubre de 2026 a partir de `demos/agente-externo/fs-triage-devoluciones/instrucciones.md` y del código del repositorio. Esta revisión documental no ejecuta agentes ni comprueba el tenant en directo.

- 41 identidades en Entra; no equivale a 41 agentes visibles en All agents.
- Atajo, Calculadora, Asistente y fs-triage existen. Dev Admin creó los recursos de FraSoHome y es sponsor de Asistente y fs-triage. Las personas del relato son ficticias.
- Audit tiene conversaciones de los agentes Microsoft y, para Claude, 2 InvokeAgent, 46 ExecuteToolBySDK y 2 InferenceCall según el informe.
- La política DLP de IBAN está activa, pero el caso probado no disparó. La causa y la evidencia en DSPM no están verificadas.
- Calculadora no bloqueada en el ensayo. Solicitud pendiente del Asistente no confirmada. Verificar ambos estados antes de decidir el recorrido.
- La KB contiene FS-KB-02 obsoleta y FS-KB-10 de prompt injection: evitar consultas que puedan recuperarlos en la demo principal. Su retirada o una demo adversarial requieren preparación aparte.
- Work IQ es explicación de arquitectura; no se presenta como integración Mail/Word probada. Con S2S la skill se detiene con mensaje. Python + Claude necesita integración específica.

## Qué demostrar

1. Inventario con origen, identidad y responsabilidad; cobertura comprobada.
2. Actividad registrada; diferenciar política configurada, detección y bloqueo.
3. Decisión administrativa y alcance real en el canal del usuario.
4. Antes/después de la instrumentación de Claude, con diff y auditoría ya disponibles.

No introducir una prueba de prompt injection ni regenerar agentes durante la sesión. El IBAN queda como prueba pendiente. La retirada, un test set adversarial y entornos separados son siguientes pasos, no montajes ya realizados en el laboratorio.

Guion vigente: [01_guion-minuto-a-minuto.md](01_guion-minuto-a-minuto.md). Operación de sala: [demos/guia-despliegue-manual.html](demos/guia-despliegue-manual.html).
