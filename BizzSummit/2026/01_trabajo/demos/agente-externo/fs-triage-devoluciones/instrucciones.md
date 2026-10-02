No he cambiado nada ni ejecutado las demos: solo he leído el tenant `vernedev` (Graph, `pac` y la auditoría y las políticas de Purview) y los guiones. La conclusión es que **las cuatro demos se sostienen, pero tres llevan una frase que el tenant ya no respalda, y la demo 4 ha perdido su premisa.**

## Lo que hay en el tenant

| Área | Estado real |
|---|---|
| Licencias | E5 Developer (16 usuarios). Copilot y Agent 365 solo los tiene `admin@`. |
| Agentes | 41 identidades de agente en Entra, 39 de Copilot Studio de otras pruebas («Prueba sin autor», «test», «Agent»…). Ya existen el Asistente (publicado en Default), `FsTriageDevoluciones Identity`, el Atajo y la Calculadora. |
| Creadores | Todo lo de FraSoHome lo creó hoy Dev Admin, que es también el sponsor del Asistente y del agente de Claude. No hay ni Álvaro ni Marta. |
| Auditoría | Activa. Están registradas hoy tus conversaciones con el Atajo, el Asistente y la Calculadora. |
| Agente de Claude | Su telemetría **ya está en la auditoría de Purview**: 2 `InvokeAgent`, 46 `ExecuteToolBySDK` y 2 `InferenceCall`, con el tipo `CustomBuiltAgentsUsingSDK`. |
| DLP | «FraSoHome – Bloqueo IBAN en agentes» está activa sobre los prompts de Copilot. **No ha saltado ninguna vez**: el prompt del IBAN en el Atajo recibió respuesta normal. Probablemente el texto decía «cuenta» y no «IBAN», y la regla exige confianza alta. |
| DSPM | La única política creada es «Detect sensitive info added to AI sites», que vigila sitios de IA de terceros, no Copilot. No he podido comprobar si el IBAN aparece en Activity explorer. |
| Calculadora | **No está bloqueada.** No hay rastro del bloqueo y se usó después. |
| Sitio KB | Además de los documentos previstos, contiene FS-KB-02 (obsoleta) y **FS-KB-10 (prompt injection)**, que la guía decía no subir. |
| Repo | El commit `a7f5f47` metió en `main` la observabilidad y Work IQ. El `instrucciones.md` del agente externo contiene mi respuesta anterior en inglés. |

## Propuesta por demo

**Demo 1 · ¿Cuántos hay?** Usa la jungla real antes que la escenificada. Abre All agents sin filtrar y di algo como: *«Este es mi tenant de pruebas. Más de cuarenta agentes, y no recuerdo la mitad»*. Después filtra por FraSoHome.
- No digas «Marta lo creó en marzo»: la ficha mostrará «Dev Admin, 2 de octubre». Cuéntalo como un caso hipotético («imaginad que quien lo creó cambió de equipo…»).
- Antes de proyectar, revisa nombres como «UPV contabilidad» o «milsa-trillo», y entornos como FENIN o HIJOLUSA. Si alguno es de un cliente, llega a la pantalla ya filtrado.

**Demo 2 · ¿Qué hacen?** Lo seguro son las conversaciones con los tres agentes en DSPM Activity explorer o en Audit. El IBAN no está verificado.
- Si a las 9:30 sale, perfecto.
- Si no sale, no lo busques en vivo. Enseña la política de DLP y di: *«la política está; el prompt de ayer no la disparó porque…»*. Ese también es un mensaje honesto de gobierno.
- El informe de uso casi seguro estará vacío: déjalo en una frase.

**Demo 3 · ¿Quién decide?** El bloqueo de la Calculadora puede ser **real y en vivo**, porque no se ha hecho. No hay captura de anoche, así que avisa de que la vista del usuario tarda en reflejarlo.
- Comprueba a mano que la solicitud del Asistente está en Requests. No he podido verlo por API.
- Reasignar propietario aparece en la slide 22 pero no en la demo. Si te sobra tiempo, el Asistente sin owners en Entra es un buen ejemplo.

**Demo 4 · El otro agente.** La premisa «funciona y nadie lo ve» ya no es cierta: el agente está registrado y emitiendo telemetría. Además, el beat de «el diff solo añade» no funciona en vivo, porque el código ya está en `main`. Propuesta de antes y después, sin ejecutar nada:
1. **Antes:** el resumen ya generado y el `.env` con credenciales propias.
2. **Qué cambió:** `git diff 8242e3f a7f5f47 -- src/agent.py`, el diff real y ya hecho. Sin depender del LLM ni de la red.
3. **Después, el cierre fuerte:** una búsqueda en Purview Audit (`InvokeAgent`) que enseña juntos el Atajo (`DeclarativeAgent`), el Asistente (`CopilotStudio`) y `fs-triage` (`CustomBuiltAgentsUsingSDK`). Eso es literalmente *«el control plane no pregunta con qué lo construiste»*.
4. **Work IQ:** solo contado. Corrige la frase del guion: la skill no se salta en silencio. Con S2S se para con un mensaje, y para Python + Claude no existe un adaptador publicado. La idea a transmitir sigue siendo «delegado, y se decide antes».

## Qué mirar a las 9:30 (sin cambiar nada)

1. All agents: si aparecen el Atajo, la Calculadora, el Asistente y **el de Claude**. Si el de Claude no sale, el paso 3 de la demo 4 se apoya solo en Audit.
2. Que la solicitud del Asistente siga pendiente en Requests.
3. DSPM Activity explorer: si hay interacciones y si alguna lleva el IBAN.
4. Audit filtrado por `InvokeAgent`, guardado como búsqueda para la demo 4.
5. No hagas al Atajo ni al Asistente preguntas que puedan traer FS-KB-10 o FS-KB-02.
6. Cierra `instrucciones.md` y `.env` en VS Code salvo cuando quieras enseñarlos.

Si quieres, lo dejo en una página de chuleta para el móvil.