# fs-triage-devoluciones

Agente de triaje de devoluciones construido con Claude Agent SDK. Lee mensajes de muestra, clasifica motivos y genera un resumen. La demo 4 presenta un **antes y después ya implementado**; no instala ni instrumenta en directo.

## Estado de referencia y límites de la evidencia

Actualizado el 2 de octubre de 2026 a partir de `demos/agente-externo/fs-triage-devoluciones/instrucciones.md` y del código del repositorio. Esta revisión documental no ejecuta agentes ni comprueba el tenant en directo.

- 41 identidades en Entra; no equivale a 41 agentes visibles en All agents.
- Atajo, Calculadora, Asistente y fs-triage existen. Dev Admin creó los recursos de FraSoHome y es sponsor de Asistente y fs-triage. Las personas del relato son ficticias.
- Audit tiene conversaciones de los agentes Microsoft y, para Claude, 2 InvokeAgent, 46 ExecuteToolBySDK y 2 InferenceCall según el informe.
- La política DLP de IBAN está activa, pero el caso probado no disparó. La causa y la evidencia en DSPM no están verificadas.
- Calculadora no bloqueada en el ensayo. Solicitud pendiente del Asistente no confirmada. Verificar ambos estados antes de decidir el recorrido.
- La KB contiene FS-KB-02 obsoleta y FS-KB-10 de prompt injection: evitar consultas que puedan recuperarlos en la demo principal. Su retirada o una demo adversarial requieren preparación aparte.
- Work IQ es explicación de arquitectura; no se presenta como integración Mail/Word probada. Con S2S la skill se detiene con mensaje. Python + Claude necesita integración específica.

## Material para la sesión

- [GUION-DEMO-4.md](GUION-DEMO-4.md): cinco minutos, frases y alternativa sin portal.
- [demo4-diff-agent.patch](demo4-diff-agent.patch): diff real 8242e3f → a7f5f47, limitado a `src/agent.py`.
- [demo-configuracion-segura.txt](demo-configuracion-segura.txt): valores ficticios para proyección. Nunca abrir `.env`.
- [GUIA-PASO-A-PASO.md](GUIA-PASO-A-PASO.md) y [HTML](guia-paso-a-paso.html): guía vigente de lectura y preparación.
- [instrucciones.md](instrucciones.md): informe de estado del 2 de octubre, conservado como fuente; no es un guion para ejecutar literalmente.

## Código y ejecución fuera de la sesión

`src/agent.py` contiene la lógica e instrumentación; `src/buzon.py`, el acceso al buzón; `requirements.txt`, las dependencias reales. El modo local usa datos de muestra; el modo Graph necesita configuración y permisos propios. No afirmar que Work IQ ha sustituido ese cliente. La preparación local y los secretos se gestionan fuera de la proyección.

No volver a un estado anterior de Git ni borrar cambios para ensayar. El agente ya registrado y su auditoría son el cierre de la demo.
