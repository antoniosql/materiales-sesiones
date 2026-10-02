# De la jungla de agentes al control plane
## Gobierno real de Copilot Studio con Agent 365 — Bizz Summit Madrid 2026
### Versión 2 — demos encadenadas sobre un único escenario de negocio

> **Pendiente de completar:** todos los marcadores `«FraSoHome: …»` se rellenan con el material de `Materiales\FraSoHome`. Hasta entonces el guion es correcto pero genérico.

---

## 0. Ficha de sesión

| | |
|---|---|
| **Duración objetivo** | 51 min de contenido + Q&A. Variantes de 30' y 75' al final |
| **Nivel** | 300 |
| **Audiencia** | Arquitectos, admins de Power Platform / M365, responsables de IA, CoE leads. Secundaria: makers avanzados |
| **Prerrequisitos del asistente** | Saber qué es un agente de Copilot Studio. No hace falta saber administrar |
| **Lo que se lleva** | Un modelo de 4 carriles + checklist 30/60/90 en una página |
| **Lo que NO es** | No es una sesión de "cómo crear un agente" ni un recorrido de features de Agent 365 |

---

## 1. Tesis y arco narrativo

**Tesis:** el problema no es crear agentes, es que ya existen cientos y nadie los inventarió. El gobierno no se implanta bloqueando; se implanta dando carriles con permisos, controles y coste distintos, y moviendo agentes entre carriles según lo que tocan.

**Arco en cuatro movimientos:**

1. **Choque** — "ya tienes agentes que no sabes que tienes"
2. **Marco** — tres capas (identidad · plataforma · datos) y cuatro carriles
3. **Prueba** — cuatro demos sobre **un mismo proceso de negocio**, a cuatro alturas
4. **Acción** — checklist y primeros 30 días

**Frase ancla que se repite tres veces:** *"Un agente sin propietario nombrado no es un agente: es una incidencia esperando fecha."*

---

## 1 bis. El hilo de demos — decisión de diseño

La versión anterior tenía tres demos independientes. Esta versión usa **un solo proceso de FraSoHome atravesando las cuatro demos**. La audiencia no aprende cuatro features: ve el mismo agente subir por las capas de gobierno, y en la última descubre que el control plane también cubre lo que no es de Microsoft.

| Demo | Pregunta que responde | Capa que demuestra | Producto |
|---|---|---|---|
| 1 | ¿Quién es este agente y de quién es? | Identidad e inventario | Copilot + Agent 365 Registry + PPAC |
| 2 | ¿Qué puede leer y qué no puede devolver? | Datos | Copilot Studio + DLP + Purview |
| 3 | ¿Sigue funcionando después del último cambio? | Ciclo de vida y calidad | Copilot Studio evaluations + Copilot Agent Kit |
| 4 | ¿Y el agente que no es de Microsoft? | Control plane transversal | Claude Agent SDK + Agent 365 SDK/CLI/Skills + Work IQ |

**Escenario base a definir:**
- `«FraSoHome: sector y tamaño»`
- `«FraSoHome: proceso de negocio elegido»` — debe ser un proceso donde ya tenga sentido un agente y donde haya un dato sensible identificable
- `«FraSoHome: agente de Copilot Studio existente»` — nombre, propietario ficticio, fecha de creación
- `«FraSoHome: dato sensible»` — el documento con etiqueta de confidencialidad que activará el bloqueo en la demo 2
- `«FraSoHome: buzón o cola de entrada»` — la fuente que consumirá el agente externo de la demo 4

**Criterio de selección de los agentes:** capacidades demostrables, no complejidad. Un agente que responde consultas sobre documentación interna y un agente que triaja una bandeja de entrada son suficientes para enseñar las cuatro capas. Un sistema multiagente sofisticado roba tiempo y no añade ni un argumento de gobierno.

---

## 2. Índice detallado con minutaje

### Bloque 0 — Apertura (0:00 – 0:03)

- **Gancho, sin slide de "quién soy"**: pregunta a mano alzada — *"¿cuántos agentes hay en vuestro tenant ahora mismo?"* → segunda pregunta: *"¿cuántos podríais demostrarlo con una captura?"*
- Dato de contraste: en los primeros meses de preview de Agent 365 aparecieron decenas de millones de agentes en el registry. No eran proyecciones: eran agentes ya activos.
- Contrato de la sesión en una slide: **qué vas a poder hacer el lunes**.
- Presentación de FraSoHome en 20 segundos: `«FraSoHome: pitch de una frase»`. Se menciona una sola vez y ya no se vuelve a explicar.

---

### Bloque 1 — La jungla: diagnóstico honesto (0:03 – 0:09)

**1.1 · Por qué esto es distinto a la Shadow IT de siempre**
- Una app de Power Apps expone datos. Un agente **lee datos, decide, ejecuta acciones y gasta dinero**, y lo hace en nombre del usuario.
- Los cuatro riesgos de runtime: exposición de datos, abuso de privilegio, ejecución autónoma no supervisada, tráfico saliente no controlado.

**1.2 · Los cinco síntomas de la jungla** (la audiencia se autodiagnostica)
1. El entorno **Default** es donde vive todo y nadie lo mira
2. Agentes publicados **sin autenticación de Entra ID**
3. Knowledge sources apuntando a sitios de SharePoint con alcance abierto
4. Nadie sabe quién paga los créditos de un agente concreto
5. El maker que lo creó cambió de equipo hace seis meses

**1.3 · El error de reacción típico**
- Reacción habitual: bloquear connectors y cerrar la creación de entornos → los makers se van a otras herramientas y el problema se vuelve invisible.
- Postura de la sesión: **la visibilidad va antes que el control**.

*Transición:* "Si el control sin visibilidad no funciona, ¿por dónde se empieza? Por saber quién es cada agente."

---

### Bloque 2 — El modelo mental: tres capas de gobierno (0:09 – 0:13)

Slide central. Todo lo que viene después cuelga de aquí.

| Capa | Pregunta que responde | Dónde se administra |
|---|---|---|
| **Identidad** | ¿Quién es este agente y de quién es? | Entra Agent ID · Agent 365 Registry · M365 Admin Center |
| **Plataforma** | ¿Dónde vive, qué puede tocar, cómo se promociona? | Power Platform Admin Center · entornos, environment groups, Managed Environments, DLP/ACP, pipelines |
| **Datos y runtime** | ¿Qué lee, qué devuelve, qué hace mientras corre? | Purview (etiquetas, DLP, DSPM for AI, auditoría) · Defender (detección y protección en runtime) |

**Los tres mensajes:**
- Agent 365 **no sustituye** al Power Platform Admin Center. Es identidad y observabilidad; la capa de plataforma sigue siendo donde vive el maker.
- La capa de datos **ya la tienes** si tienes E5. Lo que falta casi siempre no es licencia, es configuración.
- Licenciamiento sin rodeos: Agent 365 se licencia **por usuario** (quien interactúa, posee, gestiona o patrocina agentes), requiere base **E5** o **Defender + Purview Suite FLW**, y va incluido en **M365 E7**. **E3 + Copilot no es elegible.** El licenciamiento cubre gobierno, **no ejecución**: los créditos de Copilot Studio se facturan aparte.

---

### Bloque 3 — Inventario e identidad (0:13 – 0:21) · **DEMO 1**

**3.1 · Entra Agent ID: la identidad dejó de ser opcional**
- Desde julio de 2026, Copilot Studio crea automáticamente un Entra Agent ID para cada agente nuevo, y ya **no se puede desactivar a nivel de entorno**.
- Consecuencia: tu inventario ya existe. La pregunta no es "¿cómo lo construyo?" sino "¿quién lo mira y con qué cadencia?"

**3.2 · Agent 365 Registry y la página *All agents***
- Las cinco capacidades en una línea cada una: **Registry · Access Control · Visualization · Interoperability · Security**.
- La columna **Risks** consolida señales de Defender, Entra y Purview donde estén licenciadas y configuradas. Cierra la brecha de consultar tres portales.
- **Flujo de aprobación y publicación**: revisar capacidades, accesos y permisos antes de que el agente llegue a los usuarios, y publicar o rechazar en un solo workflow.
- **Registry Sync multicloud** (preview desde mayo de 2026).
- Matiz honesto: lo que no se onboarde vía Agent 365, Agent ID, integración de partner o registry sync solo aparece como **detección de Shadow AI**. Lo detectas y lo restringes por dispositivo, app o sesión, pero **no lo gobiernas como identidad**. *(Esto planta la semilla de la demo 4.)*

**3.3 · La cara Power Platform del inventario**
- **Inventory, Usage, Monitor y Actions** en el PPAC ya sustituyen al inventario del CoE Starter Kit. Si lo mantienes solo para inventariar, déjalo.
- **Copilot Studio Monitor**: qué features y connectors se usan de verdad, antes de bloquear nada.

> ### DEMO 1 — "¿Quién es este agente?" (3-4 min)
> **Escenario:** `«FraSoHome: usuario»` usa `«FraSoHome: agente de Copilot Studio»` en Teams para `«FraSoHome: consulta típica del proceso»`. Respuesta correcta, todo el mundo contento.
> **Giro:** corte a *All agents* en el M365 Admin Center. Filtrar por riesgo, abrir ese agente, enseñar identidad, propietario, permisos y accesos a datos. Saltar al PPAC → Inventory y enseñar el mismo agente desde la capa de plataforma.
> **Frase de remate:** *"Mismo agente, dos capas, dos conversaciones distintas. Y lo creó alguien en `«FraSoHome: fecha»` que ya no está en ese equipo."*
> **Riesgo:** bajo. **Plan B:** capturas anotadas.

*Transición:* "Ya sabemos quién es. Ahora: no todos los agentes merecen las mismas reglas."

---

### Bloque 4 — Los cuatro carriles (0:21 – 0:30) · **NÚCLEO DE LA SESIÓN**

**4.1 · Por qué carriles y no comités**
- Un comité de aprobación por agente no escala a 300 agentes y convierte a IT en cuello de botella.
- Los carriles son **preconfiguración**: el control ya está aplicado por el entorno donde nace el agente. El maker no pide permiso, elige carril.
- Mapean con las zonas de Microsoft (**Citizen / Partnered / Professional**), pero con cuatro escalones porque el playground merece existir formalmente.

**4.2 · Tabla de carriles** *(slide horizontal, la más densa — se lee columna a columna)*

| | **Playground** | **Equipo** | **Producción** | **Enterprise** |
|---|---|---|---|---|
| **Quién crea** | Cualquier usuario licenciado | Maker del área | Maker + IT | Equipo de plataforma |
| **Entorno** | Default, endurecido | Dev por área, en environment group | Dev/Test/Prod dedicados | Dev/Test/Prod + DR |
| **Managed Environments** | Sí | Sí | Sí | Sí |
| **Datos** | Solo datos del propio usuario | Datos del área, sin categorías sensibles | Datos de negocio con etiquetas | Datos regulados |
| **Connectors** | Allowlist mínima, sin HTTP | Allowlist de área | Allowlist revisada + endpoint filtering | Allowlist explícita, revisión por cambio |
| **Autenticación** | Entra ID obligatoria, sin canal anónimo | Entra ID | Entra ID + Conditional Access | Entra ID + CA + Information Barriers |
| **Canales** | Solo Teams / Copilot chat | Teams | Teams + canales aprobados | Todos, con revisión de seguridad |
| **Knowledge sources** | Solo lo que ya ve el usuario | Sitios acotados | Sitios acotados + etiquetas de confidencialidad | Acotados + DSPM for AI |
| **Compartición** | Solo el creador | Equipo (límite de sharing) | Grupo de seguridad | Grupo de seguridad |
| **ALM** | Ninguno, se trabaja en vivo | Solución no gestionada | Pipelines, solución gestionada | Pipelines con aprobaciones + Git |
| **Evaluaciones** | Opcional | Test set mínimo | Test set obligatorio + regresión | Regresión en CI/CD vía API |
| **Agentes externos** | No permitidos | No permitidos | Onboarding vía Agent 365 SDK obligatorio | SDK + revisión de seguridad del host |
| **Propietario** | El creador | Maker nombrado | Owner de negocio + owner técnico | Owner + backup + on-call |
| **Coste** | Cuota compartida | Presupuesto de área | Centro de coste asignado | Centro de coste + forecast |
| **Caducidad** | 90 días sin uso → archivado | 180 días | Revisión anual | Revisión anual |

**Dónde cae cada agente de FraSoHome** (slide de aterrizaje, 30 segundos):
- `«FraSoHome: agente de Copilot Studio»` → carril **Producción**
- `«FraSoHome: agente externo de la demo 4»` → carril **Producción**, camino de onboarding distinto

**4.3 · Las tres reglas duras**
1. **El Default es un carril, no un vertedero.** Managed Environment, bloquear el connector de *Chat sin autenticación de Entra ID*, bloquear HTTP y HTTP con Entra ID, limitar quién publica. Pero **no lo apagues**: si cierras el playground, la experimentación se va fuera del tenant.
2. **Sin propietario nombrado no se promociona.** Campo obligatorio, no campo bonito.
3. **Subir de carril es un evento, no un ajuste.** Revisión de datos, connectors, evaluaciones y coste. Es lo que el flujo de aprobación de Agent 365 automatiza.

**4.4 · Cómo se implanta sin un proyecto de seis meses**
- Environment groups + reglas de grupo, no configuración entorno a entorno.
- **Settings Enforcer** contra la deriva de configuración.
- La mayoría de estos controles **requieren Managed Environments o funcionan mucho mejor con ellos**. Decirlo abiertamente: tiene coste de licencia y hay que defenderlo.

---

### Bloque 5 — Control de datos (0:30 – 0:36) · **DEMO 2**

**5.1 · Lo que la DLP de Power Platform gobierna en Copilot Studio**
- Autenticación, canales, connectors específicos de Copilot Studio, y **endpoint filtering** en HTTP, SharePoint y el connector de sitios web públicos.
- Punto fino que casi nadie aplica: endpoint filtering **sobre el connector de knowledge source de SharePoint**.

**5.2 · Advanced Connector Policies: el cambio de modelo**
- **Allowlist en lugar de clasificación.** Con una ACP activa, lo que no está explícitamente permitido está bloqueado. Se acabó business / non-business.
- Pueden **bloquear servidores MCP out-of-the-box**, algunos de los cuales la DLP clásica no bloquea. Con MCP entrando como herramienta de primera clase, deja de ser un detalle.
- Limitación real: hoy solo por **environment group**, no por entorno individual, y requieren Managed Environments.
- **Recomendación:** aunque siga en preview, diseña ya tu política **pensando en allowlist**.

**5.3 · Purview, en tres controles**
- **Etiquetas de confidencialidad con cifrado**: el agente no extrae contenido salvo que el usuario tenga derechos EXTRACT y VIEW. El control que más gente ignora que ya tiene.
- **DLP de Purview**: bloquea la respuesta cuando hay coincidencia de tipos de información sensible en prompt o respuesta.
- **DSPM for AI** y auditoría unificada. Prerrequisito operativo: auditoría unificada activada y connector de M365 en Defender for Cloud Apps fluyendo datos. Sin eso, la protección de runtime no existe aunque la licencia sí.

**5.4 · Defender en runtime**
- Para agentes de Copilot Studio, Defender for Cloud Apps puede inspeccionar invocaciones de herramientas **antes de que se ejecuten**, bloquear la acción, notificar y alertar. Requiere onboarding con el admin de Power Platform.

> ### DEMO 2 — "¿Qué puede leer?" (3-4 min)
> **Escenario:** el mismo agente de la demo 1. `«FraSoHome: usuario»` le pide `«FraSoHome: consulta que roza el dato sensible»`.
> **Beat 1:** enseñar la data policy con endpoint filtering sobre el knowledge source de SharePoint — el agente solo ve `«FraSoHome: sitio permitido»`.
> **Beat 2:** el agente intenta devolver contenido de `«FraSoHome: documento con etiqueta de confidencialidad»` y es bloqueado en vivo.
> **Frase de remate:** *"Nadie ha tenido que revisar este agente para que esto pase. El control estaba en la capa, no en el agente."*
> **Riesgo:** **alto** (propagación de políticas). **Plan B: vídeo de 60 segundos pregrabado.** En un summit, esta demo se graba por defecto salvo que la hayas probado en la sala.

---

### Bloque 6 — Ciclo de vida y calidad (0:36 – 0:42) · **DEMO 3**

**6.1 · ALM sin ceremonia**
- Soluciones, **pipelines de Power Platform**, integración con Git. Dev → Test → Prod, gestionadas en Prod y solo gestionadas.
- Regla operativa: **todo cambio en instrucciones, prompts, tools, knowledge sources o connectors es un cambio de producción.** No es "editar un texto".

**6.2 · Component collections: gobierno por reutilización**
- El giro conceptual: no gobiernas 300 agentes, gobiernas **20 componentes** que esos 300 reutilizan.
- Qué mete el equipo de plataforma: disclaimers obligatorios, tono e instrucciones corporativas, tools autorizadas, patrones de escalado a humano, patrones de manejo de datos sensibles.
- `«FraSoHome: ejemplo de componente corporativo reutilizable»`
- Efecto real: el maker va más rápido *porque* usa lo gobernado. Este es el argumento que convence a negocio, no el de seguridad.

**6.3 · Evaluaciones: de "parece que funciona" a evidencia**
- **Agent evaluations en GA**: test sets personalizables, y **tests conversacionales multi-turno** además de single-turn.
- **General Quality Grader en el panel de pruebas** (GA desde el 30 de abril de 2026): evaluación automática de cada interacción durante el testing, con feedback en tiempo real y sin ejecución manual.
- **API REST de Power Platform** para lanzar evaluaciones programáticamente: validación tras cambios, chequeos recurrentes contra staging o producción, integración en CI/CD y **detección temprana de regresiones**.
- Aviso necesario: las evaluaciones miden **rendimiento y precisión, no ética ni seguridad**. Un agente puede pasar todos los tests y aun así responder mal.
- **Umbral recomendado:** ningún agente entra en Producción sin un test set de ~20 casos reales y una regresión que no baje de línea base.

**6.4 · El Copilot Agent Kit** (antes Power CAT Copilot Studio Kit)
- **Agent Review Tool**, **Agent Change Tracker** (línea base + timeline versionado: qué cambió, quién y cuándo, con valores antes/después y detalle YAML), **Agent Debugger**, test automation y **Agent Value Summary**.
- Requisito previo: habilitar code components y code apps en el entorno antes de instalarlo.

> ### DEMO 3 — "¿Sigue funcionando?" (2-3 min)
> **Escenario:** test set de `«FraSoHome: 20 preguntas reales del proceso»` ejecutándose contra el mismo agente.
> **Beat 2:** Agent Change Tracker mostrando que `«FraSoHome: maker»` cambió la instrucción del sistema ayer — diff visible, antes y después.
> **Frase de remate:** *"Sé qué cambió y sé si sigue funcionando. Eso es un servicio. Lo otro era un piloto."*
> **Riesgo:** medio. **Plan B:** resultados pregrabados.

*Transición:* "Todo esto es Copilot Studio. Pero en FraSoHome no todos los agentes van a ser de Microsoft."

---

### Bloque 7 — El agente que no es de Microsoft (0:42 – 0:48) · **DEMO 4**

**7.1 · Por qué este bloque existe**
- Ninguna organización real va a construir el 100% de sus agentes en Copilot Studio. Habrá agentes en otros frameworks, en otros clouds y en el portátil de un desarrollador.
- La pregunta de gobierno no es *"¿cómo evito que existan?"*, es *"¿cómo entran en el mismo control plane?"*.

**7.2 · Qué es (y qué no es) el Agent 365 SDK**
- Conecta un agente **que tú ya tienes y ejecutas** con Agent 365, cuando necesita acceso a nivel de código a identidad, observabilidad, tooling o notificaciones.
- **No construye agentes, no los hospeda, no orquesta pasos ni ejecuta herramientas.** Tú sigues siendo dueño de las tres capas: modelo, framework/runtime y host.
- Cuatro capacidades: **Identidad** (Entra), **Observabilidad** (OpenTelemetry), **Tooling** (servidores MCP de Work IQ gobernados: Mail, Calendar, Word, SharePoint, Teams) y **Notificaciones** (Teams, Outlook, comentarios de Word — requiere cuenta de usuario del agente, solo en Frontier preview).
- Paquetes en Python, JavaScript y .NET.
- Flujo de onboarding en cuatro etapas: **Register → Extend → Validate → Operate**.

**7.3 · Agent 365 Skills: el onboarding lo hace un agente de código**
- Las Skills corren en todos los agentes de código, **incluido Claude Code**, además de GitHub Copilot CLI y VS Code agent mode.
- `a365-setup` es el punto de entrada: instala el CLI, valida prerrequisitos de Azure, detecta el stack y delega. Camino standard → `make-a365-agent` (registra el blueprint de identidad en Entra, crea la identidad, configura permisos). Camino AI teammate → `make-ai-teammate` (**requiere Frontier preview**, no usar en esta sesión).
- `instrument-observability` cablea OpenTelemetry y el exportador de trazas para que los spans lleguen a Defender, Purview y el admin center.
- `add-workiq-tools` conecta los MCP de Work IQ (Mail, Calendar, Word). **Requiere modelo de permisos delegados y se salta automáticamente si la autenticación es S2S** — decisión a tomar antes de escribir el agente.
- `a365-code-validator` valida y diagnostica la integración, read-only por defecto.
- Las Skills son **aditivas, idempotentes y con guardarraíles**: no borran ni reestructuran código, detectan lo ya cableado y verifican que el build sigue pasando.
- **Claude Agent SDK figura como stack detectado**, en Node.js y en Python.

**7.4 · El mensaje de gobierno, que es lo que importa**
- El blueprint de identidad es el mecanismo clave: una definición aprobada por IT de la que heredan todos los agentes creados a partir de ella. Es exactamente la misma idea que las component collections del bloque 6, aplicada a la capa de identidad.
- Consecuencia para el modelo de carriles: un agente externo **puede** llegar al carril Producción, pero solo con blueprint, identidad, telemetría y propietario. No hay atajo.

> ### DEMO 4 — "El agente que no es de Microsoft" (4 min)
> **Escenario de negocio:** `«FraSoHome: proceso de bandeja de entrada»` — por ejemplo, triaje del buzón de `«FraSoHome: buzón»`, clasificando lo que entra y redactando un resumen. Es un caso que Copilot Studio no cubre bien y que no necesita un agente complejo para ser convincente.
> **Precondición:** agente ya escrito con **Claude Agent SDK**, en el repo, funcionando pero completamente invisible para IT. Enseñarlo así primero: *"esto ya existe en FraSoHome y no aparece en ningún inventario."*
> **Beat 1 (en Claude Code):** *"añade observabilidad a este agente"* → corre `instrument-observability`. Enseñar el diff: es aditivo, no reescribe nada.
> **Beat 2:** `add-workiq-tools` para Mail y Word — el agente pasa a leer `«FraSoHome: buzón»` a través de MCP gobernado, bajo control del admin.
> **Beat 3:** volver a *All agents*. Los **dos** agentes de FraSoHome están en la misma lista, con propietario, identidad y telemetría. Uno es de Copilot Studio, el otro no.
> **Frase de remate — cierre de toda la sesión:** *"El control plane no pregunta con qué lo construiste. Pregunta quién eres, qué tocas y quién responde por ti."*
> **Riesgo:** medio-alto (consentimiento de admin para scopes de Graph, tiempo de propagación). **Plan B:** los beats 1 y 2 pregrabados en terminal, beat 3 en vivo — el admin center es lo que hay que ver ocurrir.
>
> **Checklist de preparación de la demo 4:**
> - [ ] Consentimiento de admin al Agent 365 CLI para los scopes de Microsoft Graph, hecho con días de antelación
> - [ ] Decidir modelo de autenticación **delegado** (no S2S) o `add-workiq-tools` se saltará
> - [ ] Quedarse en el camino **standard agent**, no AI teammate (Frontier preview)
> - [ ] Verificar que la telemetría llega: si Defender advanced hunting no devuelve filas, revisar invocación, licencia, connector de M365 y formato de la telemetría
> - [ ] Ensayar los tres beats con el repo en estado limpio y volver a dejarlo limpio

---

### Bloque 8 — Operación, consumo y cierre (0:48 – 0:51)

- **FinOps de agentes en tres líneas:** los créditos de Copilot Studio se facturan aparte del gobierno (capacity packs o pay-as-you-go). Cada agente de Producción necesita centro de coste. Un agente sin sponsor de negocio que pague es un agente que se apaga.
- **La cadencia operativa**, que es lo que sostiene el modelo:

| Cadencia | Qué se mira | Quién |
|---|---|---|
| Semanal | Columna Risks + agentes nuevos sin propietario | Admin de plataforma |
| Mensual | Consumo por carril, agentes sin uso | CoE + finanzas |
| Trimestral | Regresión de evaluaciones en Producción, revisión de allowlist | Plataforma + seguridad |
| Anual | Revalidación de carril y de propietario | Owners de negocio |

- **Modelo de soporte L1/L2/L3:** quién responde cuando un agente da una respuesta mala a un cliente. Casi nadie lo tiene definido y es la primera crisis real.
- Slide final con **QR a la checklist**.
- Cierre volviendo al gancho: *"Volved a vuestro tenant, abrid All agents, y contad. La cifra os va a sorprender — y eso es una buena noticia, porque significa que ya tenéis el inventario. Lo que falta es decidir los carriles."*

---

## 3. Checklist accionable (entregable de la sesión)

### Primeros 30 días — ver
- [ ] Abrir *All agents* en el M365 Admin Center y exportar el inventario completo
- [ ] Listar los agentes **sin propietario identificable** → backlog número uno
- [ ] Activar el registro de auditoría unificado en Purview
- [ ] Comprobar que el connector de M365 en Defender for Cloud Apps está fluyendo datos
- [ ] Ejecutar Copilot Studio Monitor: qué features y connectors se usan **de verdad**
- [ ] Verificar elegibilidad de licencias (E5 / Defender+Purview FLW / E7) antes de prometer nada
- [ ] Preguntar a desarrollo qué agentes tienen corriendo **fuera** de Copilot Studio

### Días 30-60 — acotar
- [ ] Convertir el entorno Default en Managed Environment
- [ ] Bloquear en DLP: chat sin autenticación de Entra ID, HTTP y HTTP con Entra ID
- [ ] Crear environment groups y definir los cuatro carriles con sus reglas
- [ ] Aplicar Settings Enforcer contra la deriva de configuración
- [ ] Diseñar la allowlist de connectors por carril, pensando ya en Advanced Connector Policies
- [ ] Endpoint filtering en el knowledge source de SharePoint
- [ ] Activar el flujo de aprobación y publicación de agentes en Agent 365
- [ ] Escribir la política de agentes con HR, legal y un líder de negocio en la cadena de aprobación

### Días 60-90 — sostener
- [ ] Publicar la primera component collection corporativa
- [ ] Pipelines Dev → Test → Prod con aprobaciones para el carril Producción
- [ ] Test set mínimo por agente de Producción + regresión vía API REST en el pipeline
- [ ] Instalar el Copilot Agent Kit y activar Change Tracker en los agentes críticos
- [ ] Onboardar el primer agente externo con Agent 365 SDK y publicar el blueprint aprobado
- [ ] Asignar centro de coste por agente de Producción
- [ ] Publicar la cadencia de revisión y el modelo de soporte L1/L2/L3
- [ ] Definir la regla de caducidad por inactividad y ejecutarla la primera vez

---

## 4. Mensajes clave (los cinco que deben sobrevivir)

1. Ya tienes agentes. La identidad se crea sola desde julio de 2026; lo que falta es que alguien mire el inventario.
2. Visibilidad antes que control. Bloquear a ciegas rompe lo que funcionaba y empuja la innovación fuera del tenant.
3. Carriles, no comités. El control va preconfigurado en el entorno; el maker elige carril, no pide permiso.
4. Gobierna componentes y blueprints, no agentes. Veinte piezas gobernadas escalan; trescientos agentes revisados uno a uno, no.
5. El control plane es transversal. Si tu gobierno solo cubre lo que se construye en Microsoft, no es gobierno: es una política de producto.

---

## 5. Preguntas difíciles que van a caer

| Pregunta | Respuesta en una línea |
|---|---|
| "Estamos en E3 + Copilot, ¿podemos usar Agent 365?" | No sois elegibles; el 70% del modelo se hace solo con Power Platform y carriles |
| "¿Esto sustituye al CoE Starter Kit?" | Para inventario, sí: Inventory/Usage/Monitor/Actions ya lo cubren |
| "¿Y los agentes de terceros y de otros clouds?" | Registry Sync multicloud en preview, o SDK; lo no onboardado solo se ve como Shadow AI |
| "¿El SDK me obliga a cambiar de framework?" | No. No construye ni hospeda agentes; se acopla al que ya tienes |
| "¿Puedo gobernar un agente que corre en el portátil de un dev?" | Con identidad y telemetría, sí; sin onboarding, solo detección en endpoint |
| "¿Cuánto cuesta esto realmente?" | Gobierno por usuario + ejecución por créditos, facturas distintas. No hay TCO end-to-end oficial |
| "¿Advanced Connector Policies está listo para producción?" | Preview y solo por environment group. Diseña en allowlist ya, aplica cuando salga |
| "¿Podemos bloquear que la gente cree agentes?" | Puedes, y es el error más caro. Dale playground con límites |

---

## 6. Cuadro resumen de demos

| # | Demo | Min | Producto | Riesgo | Plan B |
|---|---|---|---|---|---|
| 1 | ¿Quién es este agente? | 3-4' | Copilot + Agent 365 + PPAC | Bajo | Capturas anotadas |
| 2 | ¿Qué puede leer? | 3-4' | Copilot Studio + DLP + Purview | **Alto** | Vídeo de 60" |
| 3 | ¿Sigue funcionando? | 2-3' | Evaluations + Copilot Agent Kit | Medio | Resultados pregrabados |
| 4 | El agente que no es de Microsoft | 4' | Claude Agent SDK + Agent 365 SDK/Skills + Work IQ | Medio-alto | Beats 1-2 pregrabados, beat 3 en vivo |

**Regla de escenario:** las demos 2 y 4 se preparan asumiendo que fallará la red. La 4 es el cierre de la sesión, así que el único beat que debe ocurrir sí o sí en vivo es ver los dos agentes juntos en *All agents*.

---

## 7. Variantes de duración

**30 minutos** — Bloques 0, 1 (recortado a los cinco síntomas), 2, 4 (carriles, entero), 8. Dos demos: la 2 y la 4. Se sacrifican inventario en profundidad, ALM y evaluaciones, que quedan en la checklist.

**75 minutos** — Añadir: ejercicio interactivo de 8' donde las mesas clasifican tres agentes de FraSoHome en carriles y lo justifican; profundizar en multiagente y component collections; ampliar la demo 4 con `a365-code-validator` y con la vista de telemetría en Defender; caso real con cifras de antes/después.

---

## 8. Recursos para la slide final

- Copilot Studio Governance and Security Guide — `aka.ms/mcs_sg`
- ALM con Power Platform — `aka.ms/powerplatform/alm`
- Power CAT AI Webinars — `aka.ms/PowerCAT/AIWebinars`
- Copilot Agent Kit (GitHub: microsoft/Power-CAT-Copilot-Studio-Kit)
- Microsoft Agent 365 — página de producto y Licensing FAQ
- Agent 365 SDK overview, Agent 365 Skills y Quickstart *Connect an existing agent to Agent 365* (Microsoft Learn)
- Copilot Studio: automatizar evaluaciones con la API de Power Platform (Microsoft Learn)
