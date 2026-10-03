# Agente externo · guía vigente de preparación y sala

Revisión del 2 de octubre de 2026. La guía anterior describía la construcción de un agente sin instrumentar; ya no corresponde al código actual. El código y `requirements.txt` son la referencia de implementación.

## Estado de referencia y límites de la evidencia

Actualizado el 2 de octubre de 2026 a partir de `demos/agente-externo/fs-triage-devoluciones/instrucciones.md` y del código del repositorio. Esta revisión documental no ejecuta agentes ni comprueba el tenant en directo.

- 41 identidades en Entra; no equivale a 41 agentes visibles en All agents.
- Atajo, Calculadora, Asistente y fs-triage existen. Dev Admin creó los recursos de FraSoHome y es sponsor de Asistente y fs-triage. Las personas del relato son ficticias.
- Audit tiene conversaciones de los agentes Microsoft y, para Claude, 2 InvokeAgent, 46 ExecuteToolBySDK y 2 InferenceCall según el informe.
- La política DLP de IBAN está activa, pero el caso probado no disparó. La causa y la evidencia en DSPM no están verificadas.
- Calculadora no bloqueada en el ensayo. Solicitud pendiente del Asistente no confirmada. Verificar ambos estados antes de decidir el recorrido.
- La KB contiene FS-KB-02 obsoleta y FS-KB-10 de prompt injection: evitar consultas que puedan recuperarlos en la demo principal. Su retirada o una demo adversarial requieren preparación aparte.
- Work IQ es explicación de arquitectura; no se presenta como integración Mail/Word probada. Con S2S la skill se detiene con mensaje. Python + Claude necesita integración específica.

## 1. Revisar el material local

Abrir `src/agent.py`, el resumen previamente generado en `salida/`, `demo4-diff-agent.patch` y `demo-configuracion-segura.txt`. Comprobar que los ficheros abren y que no muestran credenciales. Esta preparación de sala no requiere instalar dependencias, ejecutar Claude ni consultar Exchange.

## 2. Entender el cambio existente

El commit a7f5f47 integra observabilidad y trabajo de integración con Work IQ. Comparar con 8242e3f mediante el diff guardado. Seguir la configuración de identidad y los ámbitos de invocación, herramientas e inferencia. Distinguir código presente de capacidades probadas de extremo a extremo. No copiar los bloques de código históricos sobre la versión actual.

## 3. Preparar evidencia y alternativas

## Comprobación previa a la sesión

**09:30, sin cambiar configuración:** revisar All agents y filtrar referencias de terceros antes de proyectar; comprobar los cuatro agentes, Requests del Asistente y estado de Calculadora; abrir Audit y, solo si hay evidencia, DSPM Activity explorer. No hacer consultas que recuperen FS-KB-02 o FS-KB-10. No usar el ensayo para borrar ni resetear recursos.

**Antes de las 10:45:** dejar terminadas y guardadas las búsquedas de Audit. Preparar PowerPoint, código, diff y resumen generado. Cerrar `.env`, `instrucciones.md`, pestañas con secretos y resultados ajenos a FraSoHome. Para explicar configuración usar `demo-configuracion-segura.txt`.

**Búsqueda de fs-triage:** Purview → Solutions → Audit → New search; rango que incluya la tarde del 2 de octubre de 2026, con zona horaria comprobada; Keyword search `3ee28114-5ad4-40c2-8d8b-82e0578b50a4`; Record types opcionales `AIInvokeAgent`, `AIExecuteTool`, `AIInferenceCall`. Nombre `fs-triage-devoluciones`. El actor puede ser el sponsor administrador, no un usuario final.

**Búsqueda de cierre:** Record type `AIInvokeAgent`, sin keyword para no excluir los otros dos agentes. Revisar resultados antes de proyectar y limitar la vista a FraSoHome. En los detalles, `PlatformTargetAgentType`: `DeclarativeAgent`, `CopilotStudio`, `CustomBuiltAgentsUsingSDK`. Si la búsqueda no está terminada, usar respaldo 34; no esperar en escena.

## 4. Ejecutar el recorrido de sala

## Demo 4 · 11:33–11:38 · diapositiva 23

**0:00–0:45 · El trabajo útil.** Abrir el resumen de devoluciones ya generado. «Este agente está hecho con Claude Agent SDK y corre fuera de Microsoft. El antes y el después que vais a ver ya están implementados». Usar `demo-configuracion-segura.txt`; nunca abrir `.env`.

**0:45–2:15 · El cambio real.** Abrir `demo4-diff-agent.patch` junto a `src/agent.py`. Es el diff entre 8242e3f y a7f5f47, ya en main. Mostrar identidad/configuración y spans de invocación, herramienta e inferencia. No describirlo como exclusivamente aditivo: el diff también modifica código. No ejecutar skills, no reinstalar dependencias y no hacer reset. El código actual usa microsoft-opentelemetry>=1.3 y microsoft.opentelemetry.a365.core; relacionarlo con Microsoft OpenTelemetry Distro. El módulo local observability.py no es el SDK de observabilidad anterior.

Para volver a obtener el diff, desde la raíz del repositorio, operación de solo lectura:

```powershell
git diff 8242e3f a7f5f47 -- BizzSummit/2026/01_trabajo/demos/agente-externo/fs-triage-devoluciones/src/agent.py
```

**2:15–4:15 · La evidencia.** Abrir los resultados guardados de Audit. Mostrar una invocación de Atajo, una de Asistente y una de fs-triage, si las tres están verificadas. Relacionar identidad, actor, tipo de agente, operación y hora. «El origen cambia; podemos reunir evidencias de actividad de los tres». No deducir idénticos controles para todos a partir de una lista común.

**4:15–5:00 · El límite y el cierre.** «Work IQ permite conectar herramientas con permisos delegados. En este agente la integración requiere trabajo específico; no la estoy presentando como probada». Con S2S la skill se detiene con un mensaje. Registry Sync es una ruta para Managed Agents hospedados en Anthropic, no para descubrir este proceso local. Código propio puede incorporarse mediante las opciones SDK / OpenTelemetry documentadas.

**Plan B: diapositiva 34**, recuentos del informe del 2 de octubre, y diff local. No son una consulta en directo ni una captura de portal. Volver a 24. A las 11:38 cerrar la demo.

## 5. Después de la sesión

Para una nueva integración consultar la documentación vigente del SDK y de Microsoft OpenTelemetry Distro; el antiguo SDK de observabilidad está deprecado. Validar por separado registro, identidad, permisos y llegada de telemetría. Preparar en un entorno de ensayo la integración delegada de Work IQ para Python + Claude y comprobar cada herramienta antes de presentarla como funcional.

Registry Sync para Anthropic requiere Managed Agents hospedados y una plataforma compatible. No encuentra este agente local. Las capacidades de control y observabilidad dependen de la plataforma, disponibilidad y requisitos de preview/Frontier.

## Referencias

- https://learn.microsoft.com/en-us/microsoft-agent-365/developer/agent-365-sdk
- https://learn.microsoft.com/en-us/microsoft-agent-365/developer/choose-integration-option
- https://learn.microsoft.com/en-us/microsoft-agent-365/admin/connected-platforms-anthropic-claude
- https://learn.microsoft.com/en-us/microsoft-agent-365/admin/third-party-agent-observability
