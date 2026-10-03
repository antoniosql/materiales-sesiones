# De la jungla de agentes al control plane

## Guion de sala · Bizz Summit 2026

3 de octubre de 2026, 11:00–11:50 · 43 minutos de contenido + 7 de preguntas. **36 diapositivas: 30 visibles y 6 ocultas (31–36)**. Las notas del PowerPoint siguen este mismo mapa.

## Estado de referencia y límites de la evidencia

Actualizado el 2 de octubre de 2026 a partir de `demos/agente-externo/fs-triage-devoluciones/instrucciones.md` y del código del repositorio. Esta revisión documental no ejecuta agentes ni comprueba el tenant en directo.

- 41 identidades en Entra; no equivale a 41 agentes visibles en All agents.
- Atajo, Calculadora, Asistente y fs-triage existen. Dev Admin creó los recursos de FraSoHome y es sponsor de Asistente y fs-triage. Las personas del relato son ficticias.
- Audit tiene conversaciones de los agentes Microsoft y, para Claude, 2 InvokeAgent, 46 ExecuteToolBySDK y 2 InferenceCall según el informe.
- La política DLP de IBAN está activa, pero el caso probado no disparó. La causa y la evidencia en DSPM no están verificadas.
- Calculadora no bloqueada en el ensayo. Solicitud pendiente del Asistente no confirmada. Verificar ambos estados antes de decidir el recorrido.
- La KB contiene FS-KB-02 obsoleta y FS-KB-10 de prompt injection: evitar consultas que puedan recuperarlos en la demo principal. Su retirada o una demo adversarial requieren preparación aparte.
- Work IQ es explicación de arquitectura; no se presenta como integración Mail/Word probada. Con S2S la skill se detiene con mensaje. Python + Claude necesita integración específica.

## Mapa de tiempos

| Reloj | Diapositivas | Bloque |
|---|---|---|
| 11:00–11:03 | 1–6 | Apertura y FraSoHome |
| 11:03–11:06 | 7–9 | El problema y la evidencia |
| 11:06–11:10 | 10–12 | Capas, licencias e inventario |
| 11:10–11:14 | 13 | Demo 1 |
| 11:14–11:16 | 14 | Power Platform |
| 11:16–11:18 | 15 | Actividad / detección / prevención |
| 11:18–11:22 | 16 | Demo 2 |
| 11:22–11:24 | 17 | Decisiones y alcance |
| 11:24–11:27 | 18 | Demo 3 |
| 11:27–11:33 | 19–22 | SDK, identidad, permisos y rutas |
| 11:33–11:38 | 23 | Demo 4 |
| 11:38–11:41 | 24–25 | Operación y cierre |
| 11:41–11:43 | 26–27 | Checklist y recursos |
| 11:43–11:50 | 28 | Preguntas |
| 11:50 | 29–30 | Gracias y contacto |

## Comprobación previa a la sesión

**09:30, sin cambiar configuración:** revisar All agents y filtrar referencias de terceros antes de proyectar; comprobar los cuatro agentes, Requests del Asistente y estado de Calculadora; abrir Audit y, solo si hay evidencia, DSPM Activity explorer. No hacer consultas que recuperen FS-KB-02 o FS-KB-10. No usar el ensayo para borrar ni resetear recursos.

**Antes de las 10:45:** dejar terminadas y guardadas las búsquedas de Audit. Preparar PowerPoint, código, diff y resumen generado. Cerrar `.env`, `instrucciones.md`, pestañas con secretos y resultados ajenos a FraSoHome. Para explicar configuración usar `demo-configuracion-segura.txt`.

**Búsqueda de fs-triage:** Purview → Solutions → Audit → New search; rango que incluya la tarde del 2 de octubre de 2026, con zona horaria comprobada; Keyword search `3ee28114-5ad4-40c2-8d8b-82e0578b50a4`; Record types opcionales `AIInvokeAgent`, `AIExecuteTool`, `AIInferenceCall`. Nombre `fs-triage-devoluciones`. El actor puede ser el sponsor administrador, no un usuario final.

**Búsqueda de cierre:** Record type `AIInvokeAgent`, sin keyword para no excluir los otros dos agentes. Revisar resultados antes de proyectar y limitar la vista a FraSoHome. En los detalles, `PlatformTargetAgentType`: `DeclarativeAgent`, `CopilotStudio`, `CustomBuiltAgentsUsingSDK`. Si la búsqueda no está terminada, usar respaldo 34; no esperar en escena.

## Narración por diapositiva

### 1. De la jungla de agentes al control plane

11:00. Saludo breve. La sesión dura 50 minutos: 43 de contenido y 7 de preguntas. Promesa: pasar de una lista de agentes a decisiones y evidencias.

### 2. Patrocinadores

Agradecer a los patrocinadores sin leer los logotipos. Diapositiva obligatoria de la organización.

### 3. Antonio Soto

Presentación en diez segundos: más de 25 años trabajando con datos y analítica; hoy, soluciones de inteligencia artificial para empresas.

### 4. ¿Cuántos agentes hay en vuestro tenant?

Manos arriba: ¿cuántos tenéis agentes en vuestro tenant? Bajad la mano quienes no podríais demostrar cuántos hay con una evidencia en dos minutos. Esa diferencia abre la sesión.

### 5. Cuatro preguntas. Cuatro demos.

Contrato con la audiencia: inventario, actividad, decisiones y agente externo. El objetivo es saber dónde mirar y qué decisión tomar, no recorrer todos los portales.

### 6. FraSoHome: un proceso, cuatro agentes

11:02. FraSoHome y sus personas son ficticios. Los cuatro agentes existen en el laboratorio. Los creó Dev Admin, que también es sponsor de Asistente y fs-triage. Álvaro y Marta solo pueden aparecer como hipótesis, nunca como propietarios que la ficha real demostraría.

### 7. Lo que cambia es el margen de decisión

11:03. No contraponer aplicación pasiva y agente activo: ambas pueden actuar. La diferencia útil para gobernar es el margen de decisión, las herramientas y el contexto que puede usar. No todos los agentes son autónomos ni todos usan delegación.

### 8. Cinco síntomas de la jungla

Ancla: un agente sin responsable nombrado es una incidencia esperando fecha. Un cambio de equipo del maker es un riesgo organizativo; no convierte automáticamente al agente en huérfano en el portal.

### 9. Ver → decidir → comprobar

11:05. Una ficha en el inventario no demuestra que la telemetría llegue ni que la política se aplique. El control plane conecta decisiones con evidencias. Cero alertas tampoco equivale a cero riesgo.

### 10. Tres capas que se complementan

11:06. No hay un único interruptor que sustituya las tres capas. El centro de administración ayuda a coordinar; la aplicación de cada control sigue dependiendo del servicio, la plataforma y el canal.

Fuentes: [Microsoft 1](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-agent-365/microsoft-agent-365).

### 11. Registro base y Agent 365

11:07. Diferenciar capacidades base de Microsoft 365 y las añadidas por Agent 365. No atribuir todo el registro a una licencia Agent 365 ni prometer que E5 por sí solo da todos los insights. La documentación de licencia se revisa por función; consultar apéndice 36.

Fuentes: [Microsoft 1](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-agent-365/microsoft-agent-365) · [Microsoft 2](https://www.microsoft.com/licensing/faqs/122).

### 12. Un inventario útil responde a cuatro cosas

11:09. El informe del 2 de octubre cuenta 41 identidades de agente en Entra. No trasladar esa cifra al registro All agents sin comprobarlo: son inventarios de distinta cobertura. Agentes antiguos, conectados y de distintas plataformas pueden tener modelos de identidad diferentes.

Fuentes: [Microsoft 1](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-registry?view=o365-worldwide).

### 13. DEMO 1

11:10–11:14. Abrir All agents con los nombres revisados previamente; si hay referencias a terceros, llegar filtrado por FraSoHome. Mostrar Atajo, Calculadora y Asistente; buscar fs-triage solo si se verificó su presencia. Separar cobertura de All agents y las 41 identidades documentadas en Entra. Mostrar creador real Dev Admin; el cambio de equipo de Marta es hipotético. Abrir responsable, permisos y origen. Si falta una fila, explicar la cobertura sin improvisar. PLAN B: diapositiva 31, inventario documentado. Volver a 14. CHECKPOINT 11:14.

### 14. Power Platform sigue siendo el cimiento

11:14–11:16. Una sola diapositiva. El tenant de laboratorio usa Default; no fingir que existen entornos de desarrollo, prueba y producción separados. La separación es la recomendación para el ciclo de vida. Matriz de cuatro carriles en el apéndice 35.

Fuentes: [Microsoft 1](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-agent-365/microsoft-agent-365).

### 15. Actividad, detección y prevención

11:16–11:18. DLP se explica por ubicación, condición, canal y acción; no como un filtro universal de todos los prompts y respuestas. La auditoría no demuestra por sí sola prevención. En el ensayo, la política de IBAN estaba activa, pero no disparó; su causa está pendiente de diagnóstico. DSPM detect sensitive info added to AI sites cubre sitios de IA de terceros, no prueba cobertura de Copilot.

Fuentes: [Microsoft 1](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about).

### 16. DEMO 2

11:18–11:22. Prioridad: búsqueda de Audit terminada antes de la sesión. Mostrar conversaciones del Atajo, Asistente y Calculadora según resultados disponibles; abrir actor, agente, operación y hora. DSPM Activity explorer solo si se confirmó la evidencia. IBAN: la política existe, pero el prompt de prueba recibió respuesta normal; no se ha validado detección ni bloqueo. No atribuirlo con certeza a confianza o palabras clave. Si falta evidencia, mostrar estado de la política y el siguiente paso de diagnóstico. Informes de uso: una frase si están vacíos. PLAN B: 32. Volver a 17. CHECKPOINT 11:22.

### 17. Una decisión, un responsable y un alcance

11:22–11:24. Las acciones disponibles y el efecto dependen del tipo de agente. Copilot Studio y Agent Builder pueden bloquearse en hosts M365 compatibles; otros tipos tienen alcance diferente. Confirmar la experiencia del usuario tras la propagación. Owner de la ficha, owner de Entra y sponsor no son campos intercambiables.

Fuentes: [Microsoft 1](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-actions?view=o365-worldwide) · [Microsoft 2](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-registry?view=o365-worldwide).

### 18. DEMO 3

11:24–11:27. La Calculadora NO estaba bloqueada en el informe del 2 de octubre. Comprobar estado antes de la sesión. Si está disponible y autorizada para el ensayo, mostrar el bloqueo real y el estado administrativo; el efecto de usuario puede tardar. No prometer verificación instantánea. Requests del Asistente: abrir solo si se comprobó una solicitud pendiente; si no, explicar la decisión con PLAN B 33. Reasignación opcional, distinguiendo owner de Entra, propietario de la ficha y sponsor. PLAN B: 33; es un recorrido propuesto, no un bloqueo ya ejecutado. Volver a 19. CHECKPOINT 11:27.

### 19. SDK y observabilidad: piezas distintas

11:27–11:29. El SDK actual separa identidad, tooling y notificaciones; la observabilidad se ofrece mediante Microsoft OpenTelemetry Distro. El repositorio ya declara microsoft-opentelemetry>=1.3 e importa microsoft.opentelemetry.a365.core: relacionar estos nombres con la Distro. observability.py es un módulo local, no el nombre del SDK de observabilidad deprecado. No cambiar framework ni afirmar que instalar el SDK basta para el gobierno.

Fuentes: [Microsoft 1](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/agent-365-sdk) · [Microsoft 2](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/choose-integration-option).

### 20. Identidad del agente y responsabilidad

11:29–11:30. Blueprint: definición y configuración compartida desde la que se crean identidades de agente. Agent ID: identidad concreta que solicita tokens y se reconoce en el tenant. Owner: mantiene el recurso según el servicio. Sponsor: persona responsable asociada al agente. Responsable de negocio: decisión organizativa que debe quedar documentada; no confundirla automáticamente con un campo del portal. En este laboratorio Dev Admin creó los recursos y es sponsor; las personas del escenario son ficticias.

Fuentes: [Microsoft 1](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/agent-365-sdk).

### 21. Consentimiento: aprobar solo lo necesario

11:30–11:31. La captura de consentimiento muestra lectura/escritura de correo, envío, chats y archivos. Preguntar qué capacidad del caso justifica cada permiso. Este consentimiento amplio sirve para explicar mínimo privilegio; no pedir a la audiencia que acepte todo. La presentación no ha modificado permisos del tenant.

### 22. Tres rutas de incorporación

11:31–11:33. Registry Sync para Anthropic se aplica a Managed Agents hospedados, no descubre este proceso Python local. Su integración y observabilidad tienen condiciones de preview/Frontier; la sincronización es manual. Las acciones de gobierno dependen de lo que expone cada plataforma. Para código propio hay opciones SDK y OpenTelemetry: no decir que el SDK es la única puerta universal. No conectar una plataforma en directo.

Fuentes: [Microsoft 1](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/choose-integration-option) · [Microsoft 2](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/connected-platforms-anthropic-claude) · [Microsoft 3](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/third-party-agent-observability).

### 23. DEMO 4

11:33–11:38. Antes/después del trabajo ya hecho. 1) Abrir un resumen previamente generado y demo-configuracion-segura.txt, nunca .env. 2) Mostrar el diff real 8242e3f..a7f5f47 de src/agent.py; cambios ya integrados en main, no ejecutar skills ni resetear el repositorio. 3) Abrir búsqueda terminada de Audit: AIInvokeAgent, localizar Atajo (DeclarativeAgent), Asistente (CopilotStudio) y fs-triage (CustomBuiltAgentsUsingSDK); revisar únicamente filas de la demo. Resultado documentado: 2 InvokeAgent, 46 ExecuteToolBySDK y 2 InferenceCall. No presentar los recuentos como consulta recién ejecutada si se usa el respaldo. 4) Work IQ: explicación, no demo funcional. Requiere permisos delegados; con S2S la skill se detiene con mensaje; Python + Claude necesita integración específica y no hay adaptador publicado comprobado. No afirmar que se sustituyó el cliente de buzón por Mail/Word ni que Work IQ está validado de extremo a extremo. Cierre: distintos orígenes, una evidencia de actividad comparable. PLAN B: 34. Volver a 24. CHECKPOINT 11:38.

Fuentes: [Microsoft 1](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/agent-365-sdk) · [Microsoft 2](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/choose-integration-option).

### 24. Gobernar también es reaccionar

11:38–11:40. Esta cadencia es una propuesta organizativa, no un calendario impuesto por Microsoft. Definir un responsable de cada revisión. Incidentes, nuevos permisos o bajas disparan revisión inmediata según severidad; la reunión periódica no sustituye la respuesta operativa.

### 25. Mañana: empieza con diez agentes

11:40–11:41. Volver a la pregunta inicial. No se trata de acumular filas: escoger diez agentes y poder responder quién los mantiene, qué pueden hacer, qué han hecho y cómo se retiran. El número diez es una propuesta de alcance inicial, no un requisito.

### 26. Tu checklist de 30 / 60 / 90 días

11:41–11:42. El QR contiene la checklist en texto plano; no abre un servicio externo. Copia ampliada en 01_trabajo/checklist-30-60-90.md. Acordar entregables y responsables, no solo fechas.

### 27. Para llevarte y profundizar

11:42–11:43. Enlaces oficiales de apoyo. Las notas contienen fuentes por tema. Licencias y preview pueden cambiar; confirmar los requisitos del tenant antes de desplegar. No dedicar este minuto a abrir documentación.

### 28. Preguntas

11:43–11:50. Reservar siete minutos. Licencias: apéndice 36. Carriles de gobierno: 35. Agentes externos: nativa, Registry Sync o código instrumentado, según plataforma. E5 no equivale por sí solo a todas las funciones de Agent 365. DLP: especificar ubicación y acción. Bloqueo: explicar alcance y propagación. Work IQ: delegado y no validado extremo a extremo en esta demo.

### 29. Gracias

Cierre a las 11:50. Mostrar el QR de valoración original de la organización; distinto del QR de checklist de la diapositiva 26.

### 30. Contacto

Contacto institucional original. Fin del recorrido visible. Las seis diapositivas siguientes permanecen ocultas y son material de respaldo.

### 31. Plan B · inventario del laboratorio · respaldo oculto

Respaldo de demo 1. Mostrar solo si falla el portal. Estos datos proceden del informe del ensayo; la presencia actual en All agents se comprueba aparte. Dev Admin creó los recursos de FraSoHome. Volver a la diapositiva 14.

### 32. Plan B · qué está demostrado · respaldo oculto

Respaldo de demo 2. No hay prueba de bloqueo de IBAN. No usar el estado Enabled de una política como evidencia de enforcement. Revisar condición, nivel de confianza, ubicación compatible y propagación antes de repetir un caso controlado. Volver a 17.

### 33. Plan B · una decisión verificable · respaldo oculto

Respaldo de demo 3. No representa una captura ni una acción ya ejecutada. La solicitud del Asistente tampoco se ha confirmado. Explicar qué decidiríamos y qué prueba aceptaríamos como éxito. Volver a 19.

### 34. Plan B · Claude ya deja evidencia · respaldo oculto

Respaldo de demo 4. Los recuentos provienen del informe local; no de una consulta realizada durante esta edición. Mostrar demo4-diff-agent.patch como evidencia del cambio de código. Comparar el tipo de agente con DeclarativeAgent y CopilotStudio solo si la búsqueda guardada aporta esas filas. Work IQ se explica como capacidad pendiente de validar. Volver a 24.

### 35. Cuatro carriles de gobierno · respaldo oculto

Apéndice. Ajustar controles a impacto, autonomía y sensibilidad del dato. La plataforma de creación no determina por sí sola el nivel de riesgo. Un agente externo puede requerir controles adicionales sin que todos los externos tengan el mismo riesgo.

### 36. Licencias: validar por capacidad · respaldo oculto

Apéndice de licencias. Agent 365 tiene requisitos de suite y asignación; E7 incluye capacidades según el plan. La documentación consultada contiene formulaciones de requisitos no totalmente uniformes: antes de comprar, confirmar la función concreta con documentación y condiciones del contrato. El laboratorio tiene E5 Developer para 16 usuarios y Copilot + Agent 365 solo asignados al administrador según instrucciones.md. No confundir gobierno con consumo o licencia de ejecución del agente. No dar precios sin revisión.

Fuentes: [Microsoft 1](https://www.microsoft.com/licensing/faqs/122) · [Microsoft 2](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-agent-365/microsoft-agent-365).

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

## Si vas tarde

- A las 11:14 terminar demo 1. Reducir Power Platform a la frase de cierre.
- A las 11:22 terminar demo 2. No perseguir IBAN ni informes vacíos.
- A las 11:27 terminar demo 3. Omitir reasignación opcional y no esperar propagación.
- A las 11:38 terminar demo 4. Si faltan filas, enseñar 34 y cerrar.
- A las 11:43 abrir preguntas. Mantener los siete minutos; no compensar alargando el slot.

## Frases que deben desaparecer del relato

- «Todos nacen con Entra Agent ID», «E5 incluye todo» o «todos requieren SDK».
- «La política del IBAN lo bloqueó»: no hay evidencia que lo sostenga.
- «Marta creó este agente en marzo»: el tenant muestra Dev Admin y creación del 2 de octubre.
- «Claude funciona y nadie lo ve»: ya está registrado y tiene telemetría documentada.
- «La skill se salta en silencio» o «Work IQ ya sustituye el buzón»: no está demostrado.
- «Bloquearlo detiene cualquier ejecución»: explicar tipo, canal y propagación.
