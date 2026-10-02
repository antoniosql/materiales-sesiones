# De la jungla de agentes al control plane
## Guion minuto a minuto — Bizz Summit Madrid 2026

| | |
|---|---|
| **Sesión** | De la jungla de agentes al control plane: gobierno real de Copilot Studio con Agent 365 |
| **Cuándo** | Sábado 3 de octubre de 2026, **11:00** |
| **Dónde** | U-tad, Calle Playa de Liencres 2 dupdo., Las Rozas (Madrid) |
| **Slot** | **50 minutos, Q&A incluido** (regla de la organización) |
| **Reparto** | 44' de contenido + 6' de Q&A |
| **Nivel** | 300 |
| **Escenario** | FraSoHome — ver `00_escenario-frasohome.md` |

---

## Cómo leer este guion

- **Min** = minuto de sesión. **Reloj** = hora de pared, para que puedas mirar el móvil y saber si vas bien.
- Lo que va *en cursiva y entre comillas* se dice **literal**. Son las frases que sostienen el arco;
  el resto lo cuentas con tus palabras.
- Los **`⏱ CHECKPOINT`** son los cuatro puntos de control de tiempo. Si llegas tarde a uno,
  la columna «qué recortar» dice qué sacrificar. No improvises el recorte en la sala.

**La frase ancla, que se repite tres veces** (min 5, min 20, min 41):

> *"Un agente sin propietario nombrado no es un agente: es una incidencia esperando fecha."*

---

## Mapa de tiempos de un vistazo

| Min | Reloj | Bloque | Dura |
|---|---|---|---|
| 0:00 | 11:00 | Título + sponsors | 0:40 |
| 0:00.40 | 11:01 | Apertura y gancho | 1:50 |
| 0:02.30 | 11:02 | **1 · La jungla** | 4:30 |
| 0:07 | 11:07 | **2 · Las tres capas** | 3:00 |
| 0:10 | 11:10 | **3 · Inventario e identidad** | 3:00 |
| 0:13 | 11:13 | 🎬 **DEMO 1** — ¿quién es este agente? | 3:30 |
| 0:16.30 | 11:16 | **4 · Los cuatro carriles** ⭐ | 7:30 |
| 0:24 | 11:24 | **5 · Control de datos** | 2:00 |
| 0:26 | 11:26 | 🎬 **DEMO 2** — ¿qué puede leer? | 3:30 |
| 0:29.30 | 11:29 | **6 · Ciclo de vida y calidad** | 2:30 |
| 0:32 | 11:32 | 🎬 **DEMO 3** — ¿sigue funcionando? | 2:30 |
| 0:34.30 | 11:34 | **7 · El agente que no es de Microsoft** | 2:00 |
| 0:36.30 | 11:36 | 🎬 **DEMO 4** — control plane transversal | 4:00 |
| 0:40.30 | 11:40 | **8 · Operación y cierre** | 2:30 |
| 0:43 | 11:43 | Recursos + QR de la checklist | 1:00 |
| 0:44 | 11:44 | **Q&A** | 6:00 |
| 0:50 | 11:50 | Fin | |

Demos: **13'30"** sobre 44' de contenido (31%). Ese ratio es el que hace que una sesión de nivel 300
no parezca una lectura de documentación.

---

# BLOQUE 0 — Apertura · 0:00 → 0:02.30 · (11:00–11:02)

### 0:00 – 0:00.40 · Slides 1 y 2 (título y sponsors)

La slide de sponsors es **obligatoria** y no se puede eliminar. No la leas: la dejas puesta
mientras te conectas y dices la primera frase. Cuarenta segundos, ni uno más.

> *"Gracias a los patrocinadores, que son los que hacen que esto exista. Vamos al grano,
> porque tengo cincuenta minutos y cuatro demos."*

### 0:00.40 – 0:01.30 · Slide 3 — el gancho. **Sin slide de «quién soy»**

Dos preguntas a mano alzada, seguidas, sin dejar respirar entre ellas:

> *"Manos arriba: ¿cuántos de vosotros tenéis agentes en vuestro tenant ahora mismo?"*

*(se levantan casi todas)*

> *"Bajad la mano los que no podríais demostrarlo con una captura en los próximos dos minutos."*

*(se quedan cuatro)*

> *"Esa diferencia entre las manos que se levantaron y las que se quedaron arriba
> es de lo que va esta sesión."*

**Nota de sala:** si el público es tímido y no levanta la mano, no insistas. Cuenta tú las manos que
imaginabas y sigue: *"lo pregunto en todas las sesiones y el resultado es siempre el mismo".*

### 0:01.30 – 0:02 · Slide 4 — el dato de contraste

> *"En los primeros meses de preview de Agent 365 aparecieron decenas de millones de agentes en el
> registry. No eran proyecciones de adopción. Eran agentes ya activos, que ya existían."*

### 0:02 – 0:02.30 · Slide 5 — el contrato de la sesión + FraSoHome

Una slide con tres líneas: **qué te vas a poder hacer el lunes**.

1. Saber cuántos agentes tienes y de quién son
2. Tener cuatro carriles definidos en vez de un comité
3. Saber qué haces con los agentes que no son de Microsoft

Y el pitch de FraSoHome, **20 segundos, se dice una vez y no se vuelve a explicar**:

> *"Todo lo que veáis hoy pasa en FraSoHome: retail de muebles y decoración, tres tiendas,
> e-commerce, fidelización. Y un proceso: devoluciones. Un solo proceso, cuatro demos,
> cuatro alturas de gobierno."*

---

# BLOQUE 1 — La jungla: diagnóstico honesto · 0:02.30 → 0:07 · (11:02–11:07)

### 0:02.30 – 0:04 · Por qué esto no es la Shadow IT de siempre

Slide de contraste, dos columnas.

| Una app de Power Apps | Un agente |
|---|---|
| Expone datos | **Lee datos, decide, ejecuta acciones y gasta dinero** |
| Actúa como la app | **Actúa en nombre del usuario** |

> *"La Shadow IT clásica era un problema de exposición. Esto es un problema de agencia.
> La diferencia no es de grado, es de naturaleza."*

Los cuatro riesgos de runtime, uno por línea y rápido:
exposición de datos · abuso de privilegio · ejecución autónoma no supervisada · tráfico saliente no controlado.

### 0:04 – 0:05.30 · Los cinco síntomas · **la audiencia se autodiagnostica**

Slide numerada. Los lees en voz alta y dejas medio segundo entre cada uno. Esto funciona
mejor si vas contando con los dedos.

1. El entorno **Default** es donde vive todo y nadie lo mira
2. Agentes publicados **sin autenticación de Entra ID**
3. Knowledge sources apuntando a sitios de SharePoint con alcance abierto
4. Nadie sabe quién paga los créditos de un agente concreto
5. El maker que lo creó cambió de equipo hace seis meses

> *"Si habéis marcado tres o más, no tenéis un problema de tecnología. Tenéis una jungla."*

**Primera repetición de la frase ancla:**

> *"Y el quinto síntoma es el que más duele, porque un agente sin propietario nombrado
> no es un agente: es una incidencia esperando fecha."*

### 0:05.30 – 0:07 · El error de reacción típico

> *"La reacción habitual es bloquear connectors y cerrar la creación de entornos.
> Funciona exactamente seis semanas. Luego los makers se van a otras herramientas
> y el problema no desaparece: se vuelve invisible."*

Postura de la sesión, en una slide con cuatro palabras:

## **La visibilidad va antes que el control.**

**Transición literal:**

> *"Si el control sin visibilidad no funciona, ¿por dónde se empieza?
> Por saber quién es cada agente."*

`⏱ CHECKPOINT 1 — deberías estar en 11:07.`
Si vas por encima de 11:08: recorta el bloque 1.1 a una sola frase y ve directo a los cinco síntomas.

---

# BLOQUE 2 — El modelo mental: tres capas · 0:07 → 0:10 · (11:07–11:10)

**Esta es la slide central de la sesión.** Todo lo que viene después cuelga de aquí.
Déjala puesta mientras hablas y vuelve a ella con el puntero en cada demo.

| Capa | Pregunta que responde | Dónde se administra |
|---|---|---|
| **Identidad** | ¿Quién es este agente y de quién es? | Entra Agent ID · Agent 365 Registry · M365 Admin Center |
| **Plataforma** | ¿Dónde vive, qué toca, cómo se promociona? | Power Platform Admin Center |
| **Datos y runtime** | ¿Qué lee, qué devuelve, qué hace mientras corre? | Purview · Defender |

### 0:08.30 – 0:10 · Los tres mensajes que no pueden faltar

1. > *"Agent 365 **no sustituye** al Power Platform Admin Center. Es identidad y observabilidad.
   > La capa de plataforma sigue siendo donde vive el maker."*

2. > *"La capa de datos **ya la tenéis** si tenéis E5. Lo que falta casi nunca es licencia:
   > es configuración."*

3. **Licenciamiento sin rodeos** — dilo rápido y sin disculparte, porque es la pregunta nº1 del Q&A:
   - Agent 365 se licencia **por usuario** (quien interactúa, posee, gestiona o patrocina agentes)
   - Requiere base **E5** o **Defender + Purview Suite FLW**; va incluido en **M365 E7**
   - **E3 + Copilot no es elegible**
   - El licenciamiento cubre **gobierno, no ejecución**: los créditos de Copilot Studio se facturan aparte

> *"Apuntad esta última línea, porque es la que os va a salvar de prometer algo
> que luego no podéis entregar."*

---

# BLOQUE 3 — Inventario e identidad · 0:10 → 0:13 · (11:10–11:13)

### 0:10 – 0:11 · Entra Agent ID: la identidad dejó de ser opcional

> *"Desde julio de 2026, Copilot Studio crea automáticamente un Entra Agent ID para cada agente
> nuevo. Y ya no se puede desactivar a nivel de entorno."*

> *"La consecuencia es más interesante de lo que parece: vuestro inventario ya existe.
> La pregunta no es «cómo lo construyo». Es «quién lo mira, y con qué cadencia»."*

### 0:11 – 0:12.15 · Agent 365 Registry y la página *All agents*

Las cinco capacidades, una línea cada una, sin detenerse:
**Registry · Access Control · Visualization · Interoperability · Security**

Lo que sí merece detenerse:

- **La columna `Risks`** consolida señales de Defender, Entra y Purview donde estén licenciadas y
  configuradas. *"Cierra la brecha de tener que abrir tres portales para responder una pregunta."*
- **Flujo de aprobación y publicación**: revisar capacidades, accesos y permisos antes de que el
  agente llegue a los usuarios, y publicar o rechazar en un solo workflow.
- **Registry Sync multicloud**, en preview desde mayo de 2026.

**El matiz honesto — que es lo que planta la semilla de la demo 4:**

> *"Lo que no se onboarde vía Agent 365, Agent ID, integración de partner o registry sync,
> solo aparece como detección de Shadow AI. Lo detectas y lo restringes por dispositivo,
> app o sesión. Pero no lo gobiernas como identidad. Guardad esa frase, que volvemos a ella
> en la última demo."*

### 0:12.15 – 0:13 · La cara Power Platform del inventario

- **Inventory, Usage, Monitor y Actions** en el PPAC ya sustituyen al inventario del CoE Starter Kit.
  > *"Si mantenéis el CoE Starter Kit solo para inventariar: dejadlo. Ya no hace falta."*
- **Copilot Studio Monitor**: qué features y connectors se usan de verdad, **antes** de bloquear nada.

---

# 🎬 DEMO 1 — «¿Quién es este agente?» · 0:13 → 0:16.30 · (11:13–11:16)

**Duración:** 3:30 · **Riesgo:** bajo · **Plan B:** capturas anotadas (slides 26–29)

### El montaje

Dos ventanas preparadas y **maximizadas antes de empezar**, con zoom del navegador al 125%:

- Ventana A: Teams con el chat del **Asistente de Devoluciones FraSoHome**, historial limpio
- Ventana B: M365 Admin Center → *All agents*, ya filtrado
- Ventana C: PPAC → Inventory, con el agente ya buscado

### El guion, beat a beat

**Beat 1 · 45" · Todo funciona** *(ventana A)*

Escribes en Teams, como Álvaro, Store Manager de Gran Vía:

```
Un cliente Oro compró un sofá online el 20 de agosto y quiere devolverlo.
¿Está en plazo?
```

El agente responde bien: 45 días naturales desde la entrega, y la excepción por tier Oro.
Con citación a FS-KB-01 v1.3.

> *"Respuesta correcta. Citada. En Teams. Cuarenta personas de tienda usan esto todos los días
> y funciona. Todo el mundo contento."*

**Beat 2 · 1:15" · El giro** *(ventana B)*

Cortas a *All agents*. **No busques nada en vivo**: llega con el filtro ya aplicado.

- Ordena por la columna **`Risks`**. El Asistente de Devoluciones está arriba.
- Abre el agente. Enseña, en este orden y sin desviarte:
  1. **Identidad** — su Entra Agent ID
  2. **Propietario** — vacío
  3. **Permisos y accesos a datos** — el sitio de SharePoint y las tools de Dataverse
  4. **Usuarios** — ~40

**Beat 3 · 45" · La misma cosa desde la otra capa** *(ventana C)*

Saltas al PPAC → Inventory y buscas el mismo agente. Aquí se ve otra cosa: vive en **Default**,
sin Managed Environment, y con un consumo de créditos que no está asignado a nadie.

> *"Mismo agente, dos capas, dos conversaciones distintas. Arriba hablo de identidad y riesgo.
> Abajo hablo de entorno, connectors y factura."*

**Beat 4 · 45" · El remate**

> *"Y lo creó Marta, de Operaciones de Tienda, el 17 de marzo de 2026.
> Marta pasó a e-commerce en julio. Nadie se lo dijo a este agente."*

*(pausa)*

> *"Cuarenta personas dependen todos los días de una respuesta que nadie mantiene."*

**Si algo falla:** pasa a las capturas anotadas sin anunciarlo. Di *"lo tengo capturado, que esto
tarda"* y sigue exactamente con los mismos cuatro beats. La audiencia no notará la diferencia.

**Transición:**

> *"Ya sabemos quién es. Ahora la siguiente pregunta:
> no todos los agentes merecen las mismas reglas."*

`⏱ CHECKPOINT 2 — deberías estar en 11:16.30.`
Si vas por encima de 11:18: entra a carriles saltándote el 4.1 y ve directo a la tabla.

---

# BLOQUE 4 — Los cuatro carriles · 0:16.30 → 0:24 · (11:16–11:24) ⭐ NÚCLEO

**Este es el bloque que la gente se lleva a casa. Protégelo. Si hay que recortar, se recorta
de cualquier otro sitio antes que de aquí.**

### 0:16.30 – 0:18 · Por qué carriles y no comités

> *"Lo primero que hace todo el mundo es montar un comité de aprobación por agente.
> No escala a trescientos agentes, y convierte a IT en el cuello de botella
> del que luego todos se quejan."*

La idea, en una frase:

> *"Los carriles son **preconfiguración**. El control ya está aplicado por el entorno donde nace
> el agente. El maker no pide permiso: **elige carril**."*

Y la honestidad de siempre:

> *"Esto mapea con las zonas de Microsoft — Citizen, Partnered, Professional —
> pero con cuatro escalones en vez de tres, porque el playground merece existir formalmente."*

### 0:18 – 0:21.30 · La tabla de carriles

**Slide horizontal, la más densa de la sesión.** No la leas entera: **se lee columna a columna**.
Recorre solo cinco filas en voz alta —Entorno, Datos, Connectors, Agentes externos, Propietario—
y di:

> *"El resto está en la checklist que os lleváis. Esta slide no es para leerla aquí:
> es para hacerle una foto."*

*(Deja tres segundos de silencio para que hagan la foto. Lo van a hacer.)*

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

### 0:21.30 – 0:22 · Dónde cae cada agente de FraSoHome

Slide de aterrizaje. **Treinta segundos**, ni uno más.

- `FS-Copilot-Devoluciones` → carril **Producción**. Hoy vive en el Default. Ese es el trabajo.
- `fs-triage-devoluciones` → carril **Producción** también, pero con un camino de onboarding distinto.

> *"Fijaos que los dos van al mismo carril. Lo que cambia no es el destino: es la puerta por la que entran."*

### 0:22 – 0:23.15 · Las tres reglas duras

**1. El Default es un carril, no un vertedero.**
Managed Environment, bloquear el connector de *Chat sin autenticación de Entra ID*, bloquear HTTP y
HTTP con Entra ID, limitar quién publica.

> *"Pero no lo apaguéis. Si cerráis el playground, la experimentación no desaparece:
> se va fuera del tenant, donde no la veis."*

**2. Sin propietario nombrado no se promociona.** Campo obligatorio, no campo bonito.

**Segunda repetición de la frase ancla:**

> *"Porque, insisto, un agente sin propietario nombrado no es un agente:
> es una incidencia esperando fecha."*

**3. Subir de carril es un evento, no un ajuste.**
Revisión de datos, connectors, evaluaciones y coste.

> *"Y eso es exactamente lo que el flujo de aprobación de Agent 365 automatiza.
> No os estoy pidiendo un proceso nuevo: os estoy pidiendo que useis el que ya viene."*

### 0:23.15 – 0:24 · Cómo se implanta sin un proyecto de seis meses

- **Environment groups + reglas de grupo**, no configuración entorno a entorno
- **Settings Enforcer** contra la deriva de configuración
- Y la verdad incómoda, dicha abiertamente:

> *"La mayoría de estos controles requieren Managed Environments, o funcionan mucho mejor con ellos.
> Eso tiene coste de licencia, y alguien lo va a tener que defender ante finanzas.
> Prefiero que salgáis de aquí sabiéndolo."*

---

# BLOQUE 5 — Control de datos · 0:24 → 0:26 · (11:24–11:26)

Dos minutos. Es teoría de apoyo para la demo: **no te enamores de esta parte.**

### DLP de Power Platform en Copilot Studio — 30"

Gobierna autenticación, canales, connectors específicos de Copilot Studio, y **endpoint filtering**
en HTTP, SharePoint y el connector de sitios web públicos.

> *"Y el punto fino que casi nadie aplica: endpoint filtering **sobre el connector de knowledge
> source de SharePoint**. Es el que vais a ver en un minuto."*

### Advanced Connector Policies — 40"

> *"Aquí hay un cambio de modelo, no una feature más: **allowlist en lugar de clasificación**.
> Con una ACP activa, lo que no está explícitamente permitido está bloqueado.
> Se acabó el business / non-business."*

- Pueden **bloquear servidores MCP out-of-the-box**, algunos de los cuales la DLP clásica no bloquea.
  Con MCP entrando como herramienta de primera clase, esto deja de ser un detalle.
- **Limitación real:** hoy solo por **environment group**, no por entorno individual.
  Y requieren Managed Environments.
- **Recomendación:** *"aunque siga en preview, diseñad ya vuestra política pensando en allowlist."*

### Purview y Defender, en tres controles — 50"

- **Etiquetas de confidencialidad con cifrado** — el agente no extrae contenido salvo que el usuario
  tenga derechos EXTRACT y VIEW. *"El control que más gente ignora que ya tiene."*
- **DLP de Purview** — bloquea la respuesta cuando hay coincidencia de tipos de información sensible
  en el prompt o en la respuesta.
- **DSPM for AI y auditoría unificada.** Y el prerrequisito operativo que hunde proyectos:
  > *"Auditoría unificada activada y el connector de M365 en Defender for Cloud Apps fluyendo datos.
  > Sin eso, la protección de runtime no existe aunque la licencia sí."*
- **Defender en runtime:** para agentes de Copilot Studio, Defender for Cloud Apps puede inspeccionar
  invocaciones de herramientas **antes de que se ejecuten**, bloquear la acción y alertar.

---

# 🎬 DEMO 2 — «¿Qué puede leer?» · 0:26 → 0:29.30 · (11:26–11:29)

**Duración:** 3:30 · **Riesgo: ALTO** (propagación de políticas) · **Plan B: vídeo de 60" pregrabado**

> ⚠️ **Regla de escenario: en un summit, esta demo va grabada por defecto.**
> Solo se hace en vivo si la has probado **en la sala, con la red de la sala, esa misma mañana.**
> El vídeo de 60" cuenta exactamente los mismos dos beats y no rompe el ritmo.

### El guion, beat a beat

**Beat 1 · 1:15" · El agente solo ve lo que le dejamos ver**

Enseña la data policy con **endpoint filtering sobre el knowledge source de SharePoint**:

| Sitio | Estado |
|---|---|
| `FraSoHome-KB-Operaciones` | ✅ Permitido |
| `FraSoHome-PrevencionPerdidas` | ❌ No permitido |

Vuelves a Teams y, como Álvaro, preguntas:

```
Dame el listado de clientes con devoluciones anómalas de este trimestre.
```

El agente responde que no tiene información sobre eso y propone el siguiente paso
(escalar a Prevención de Pérdidas, tal y como manda FS-KB-08).

> *"Fijaos en lo que **no** ha pasado. No ha dicho «no tienes permiso». No ha habido un error.
> Ese documento, para este agente, sencillamente no existe. El alcance se decidió en la política,
> no en la conversación."*

**Beat 2 · 1:30" · El bloqueo en vivo**

Segunda pregunta, esta sí con datos a los que el agente **sí** tiene acceso:

```
¿A qué cuenta se reembolsó la devolución DEV-2026-0418?
```

El agente llama a la tool, recupera el registro de `FS_DevolucionesFact`… y **la respuesta se bloquea**:
contiene un IBAN español y coincide con el tipo de información sensible de Purview.

*(Deja que el bloqueo se quede en pantalla dos segundos antes de hablar.)*

**Beat 3 · 45" · El remate**

> *"Este agente lo creó Marta hace seis meses. Marta no sabe lo que es un tipo de información
> sensible, y no tiene por qué saberlo."*

> *"**Nadie ha tenido que revisar este agente para que esto pase. El control estaba en la capa,
> no en el agente.** Y eso es la única forma de que esto escale a trescientos agentes."*

---

# BLOQUE 6 — Ciclo de vida y calidad · 0:29.30 → 0:32 · (11:29–11:32)

### ALM sin ceremonia — 40"

Soluciones, **pipelines de Power Platform**, integración con Git. Dev → Test → Prod,
gestionadas en Prod y solo gestionadas.

La regla operativa, que es lo que hay que apuntar:

> *"Todo cambio en instrucciones, prompts, tools, knowledge sources o connectors
> es un **cambio de producción**. No es «editar un texto»."*

### Component collections: gobierno por reutilización — 1:00"

**El giro conceptual de la sesión**, y probablemente la idea más rentable que se llevan:

> *"No gobernáis trescientos agentes. Gobernáis **veinte componentes**
> que esos trescientos reutilizan."*

Qué mete el equipo de plataforma en la colección: disclaimers obligatorios, tono e instrucciones
corporativas, tools autorizadas, patrones de escalado a humano, patrones de manejo de datos sensibles.

En FraSoHome, eso es **`FS-Guardarrail-Devoluciones`**, con cinco piezas. Y una de ellas
es la regla de versionado: *prioriza VIGENTE, ignora OBSOLETA.*

> *"Acordaos de esa regla, que en cuarenta segundos vais a ver lo que pasa cuando no está
> en el componente sino en el agente."*

Y el argumento que convence a negocio, que **no es el de seguridad**:

> *"El maker va más rápido **porque** usa lo gobernado. Ese es el argumento.
> El de seguridad no le ha convencido nunca a nadie que no sea de seguridad."*

### Evaluaciones y el Copilot Agent Kit — 50"

- **Agent evaluations en GA**: test sets personalizables y tests conversacionales multi-turno
- **General Quality Grader en el panel de pruebas** (GA desde el 30 de abril de 2026)
- **API REST de Power Platform** para lanzar evaluaciones programáticamente → regresión en CI/CD
- El aviso necesario:
  > *"Las evaluaciones miden rendimiento y precisión. **No miden ética ni seguridad.**
  > Un agente puede pasar todos los tests y aun así responder mal."*
- **Umbral recomendado:** ningún agente entra en Producción sin un test set de ~20 casos reales
  y una regresión que no baje de línea base.
- **Copilot Agent Kit** (antes Power CAT Copilot Studio Kit): Agent Review Tool,
  **Agent Change Tracker**, Agent Debugger, test automation, Agent Value Summary.

---

# 🎬 DEMO 3 — «¿Sigue funcionando?» · 0:32 → 0:34.30 · (11:32–11:34)

**Duración:** 2:30 · **Riesgo:** medio · **Plan B:** resultados pregrabados

### El guion, beat a beat

**Beat 1 · 1:00" · El test set en rojo**

Lanzas la evaluación contra el Asistente de Devoluciones. **20 casos**:
10 documentales, 6 métricos, 4 de seguridad.

Resultado: **19 en verde, 1 en rojo.**

El que falla:

| | |
|---|---|
| Pregunta | *¿Cuál es el plazo de devolución para compras online?* |
| Esperado | **45 días naturales** |
| Devuelto | **30 días** |
| Fuente citada | FS-KB-02 v1.2 — **obsoleta** |

> *"Treinta días en vez de cuarenta y cinco. Si un Store Manager le dice eso a un cliente,
> FraSoHome acaba de rechazar una devolución que era legítima. Eso es una reclamación,
> y con suerte solo una."*

**Beat 2 · 1:00" · Quién lo rompió, y cuándo**

Abres el **Agent Change Tracker**. Línea base + timeline versionado.

El 12 de septiembre, **Marta R.** editó la instrucción del sistema. Diff visible, antes y después:

```diff
- Prioriza siempre la versión VIGENTE de la política.
- Ignora documentos marcados OBSOLETA.
```

> *"No hizo nada malo. Estaba limpiando instrucciones que le parecían redundantes.
> Y no lo era: era el único sitio donde vivía esa regla."*

**Beat 3 · 30" · El remate**

> *"**Sé qué cambió y sé si sigue funcionando. Eso es un servicio. Lo otro era un piloto.**"*

> *"Y fijaos en la moraleja real: esa regla no debería haber estado en el agente.
> Debería haber estado en el componente. Marta no habría podido borrarla."*

**Transición:**

> *"Todo esto que habéis visto es Copilot Studio. Pero en FraSoHome no todos los agentes
> van a ser de Microsoft. Y en vuestra empresa tampoco."*

`⏱ CHECKPOINT 3 — deberías estar en 11:34.30.`
Si vas por encima de 11:36: entra a la demo 4 saltándote el 7.2 (el detalle del SDK)
y explícalo dentro de la propia demo.

---

# BLOQUE 7 — El agente que no es de Microsoft · 0:34.30 → 0:36.30 · (11:34–11:36)

### Por qué este bloque existe — 40"

> *"Ninguna organización real va a construir el cien por cien de sus agentes en Copilot Studio.
> Va a haber agentes en otros frameworks, en otros clouds, y en el portátil de un desarrollador."*

> *"Y la pregunta de gobierno no es «¿cómo evito que existan?». Es **«¿cómo entran en el mismo
> control plane?»**."*

### Qué es y qué no es el Agent 365 SDK — 50"

Conecta un agente **que tú ya tienes y ya ejecutas** con Agent 365, cuando necesita acceso a nivel
de código a identidad, observabilidad, tooling o notificaciones.

> *"Y ahora lo que **no** es, que es donde se confunde todo el mundo:
> **no construye agentes, no los hospeda, no orquesta pasos, no ejecuta herramientas.**
> Vosotros seguís siendo dueños de las tres capas: modelo, framework y host."*

Cuatro capacidades: **Identidad** (Entra) · **Observabilidad** (OpenTelemetry) ·
**Tooling** (MCP de Work IQ gobernados: Mail, Calendar, Word, SharePoint, Teams) · **Notificaciones**.
Paquetes en Python, JavaScript y .NET. Flujo en cuatro etapas:
**Register → Extend → Validate → Operate**.

### El mensaje de gobierno, que es lo que importa — 30"

> *"El mecanismo clave es el **blueprint de identidad**: una definición aprobada por IT
> de la que heredan todos los agentes creados a partir de ella."*

> *"Es exactamente la misma idea que las component collections de hace tres minutos,
> aplicada a la capa de identidad. Gobiernas la plantilla, no la instancia."*

Y la consecuencia para el modelo de carriles:

> *"Un agente externo **puede** llegar al carril Producción. Pero solo con blueprint, identidad,
> telemetría y propietario. **No hay atajo.**"*

---

# 🎬 DEMO 4 — «El agente que no es de Microsoft» · 0:36.30 → 0:40.30 · (11:36–11:40)

**Duración:** 4:00 · **Riesgo:** medio-alto · **Es el cierre de la sesión**
**Plan B:** beats 1 y 2 pregrabados en terminal, **beat 3 en vivo sí o sí**

> **El único beat que debe ocurrir en vivo es ver los dos agentes juntos en *All agents*.**
> Todo lo demás puede ir grabado sin que la sesión pierda nada.

### La precondición, que es media demo

Abres el repo de `fs-triage-devoluciones` en Claude Code. Enseñas que funciona: lee
`devoluciones@frasohome.es`, clasifica por motivo, redacta el resumen para el Store Manager.

> *"Esto ya existe en FraSoHome. Lo escribió David, de e-commerce, con el Agent SDK de Claude.
> Funciona. Lleva semanas funcionando."*

*(Cambias a All agents. El agente no está.)*

> *"Y no aparece en ningún inventario. Ni aquí, ni en el PPAC, ni en la factura de nadie.
> Esto es lo que hace una hora llamábamos detección de Shadow AI: lo veo, lo restrinjo,
> pero no lo gobierno."*

### Beat 1 · 1:00" · Observabilidad

En Claude Code, escribes literalmente:

```
añade observabilidad a este agente
```

Se ejecuta la skill **`instrument-observability`**: cablea OpenTelemetry y el exportador de trazas
para que los spans lleguen a Defender, Purview y el admin center.

**Enseña el diff.** Es lo importante:

> *"Mirad lo que ha hecho: **añadir**. No ha reescrito el agente, no ha cambiado el framework,
> no ha tocado la lógica de negocio. Las skills son aditivas, idempotentes y con guardarraíles:
> detectan lo que ya está cableado y verifican que el build sigue pasando."*

### Beat 2 · 1:15" · Tooling gobernado

```
conecta este agente a Mail y Word a través de Work IQ
```

Se ejecuta **`add-workiq-tools`**. El agente deja de leer el buzón con sus propias credenciales
y pasa a leerlo **a través de servidores MCP gobernados, bajo control del admin**.

> *"Antes, David tenía unas credenciales en un `.env`. Ahora el acceso al correo de FraSoHome
> pasa por un MCP que el administrador puede ver, auditar y cortar."*

⚠️ **Aviso técnico que debes decir, porque es la trampa más común:**

> *"`add-workiq-tools` requiere modelo de permisos **delegados**. Si vuestro agente usa
> autenticación S2S, la skill se salta sola y no os dice por qué.
> Es una decisión que hay que tomar **antes** de escribir el agente, no después."*

### Beat 3 · 1:15" · Los dos juntos · **EN VIVO**

Vuelves a *All agents*. Refrescas.

**Los dos agentes de FraSoHome están en la misma lista.** Con propietario, identidad y telemetría.
Uno es de Copilot Studio. El otro no.

*(Silencio. Deja que lo lean.)*

### Beat 4 · 30" · El remate — cierre de toda la sesión

> *"**El control plane no pregunta con qué lo construiste.
> Pregunta quién eres, qué tocas y quién responde por ti.**"*

---

# BLOQUE 8 — Operación, consumo y cierre · 0:40.30 → 0:43 · (11:40–11:43)

### FinOps de agentes, en tres líneas — 40"

- Los créditos de Copilot Studio se facturan **aparte** del gobierno (capacity packs o pay-as-you-go)
- Cada agente de Producción necesita **centro de coste**
- > *"Un agente sin sponsor de negocio que pague es un agente que se apaga. Y es sano que se apague."*

### La cadencia operativa — 50"

**Es lo que sostiene todo el modelo.** Sin esto, los carriles son un PowerPoint.

| Cadencia | Qué se mira | Quién |
|---|---|---|
| **Semanal** | Columna `Risks` + agentes nuevos sin propietario | Admin de plataforma |
| **Mensual** | Consumo por carril, agentes sin uso | CoE + finanzas |
| **Trimestral** | Regresión de evaluaciones en Producción, revisión de allowlist | Plataforma + seguridad |
| **Anual** | Revalidación de carril y de propietario | Owners de negocio |

### El modelo de soporte L1/L2/L3 — 25"

> *"¿Quién responde cuando un agente le da una respuesta mala a un cliente?
> Casi nadie lo tiene definido, y es la primera crisis real que vais a tener.
> No la segunda: la primera."*

**Tercera y última repetición de la frase ancla:**

> *"Porque, como llevo cincuenta minutos diciendo: un agente sin propietario nombrado
> no es un agente. Es una incidencia esperando fecha."*

### El cierre, volviendo al gancho — 35"

> *"Volved a vuestro tenant el lunes. Abrid *All agents*. Y contad."*

> *"La cifra os va a sorprender. Y eso es una buena noticia — porque significa
> que el inventario ya lo tenéis. Lo que falta es decidir los carriles."*

---

# RECURSOS · 0:43 → 0:44 · (11:43–11:44)

Slide final con el **QR a la checklist 30/60/90**. Esto es lo que se llevan.

- Copilot Studio Governance and Security Guide — `aka.ms/mcs_sg`
- ALM con Power Platform — `aka.ms/powerplatform/alm`
- Power CAT AI Webinars — `aka.ms/PowerCAT/AIWebinars`
- Copilot Agent Kit — GitHub: `microsoft/Power-CAT-Copilot-Studio-Kit`
- Microsoft Agent 365 — página de producto y Licensing FAQ
- Agent 365 SDK overview, Agent 365 Skills y Quickstart *Connect an existing agent to Agent 365*
- Copilot Studio: automatizar evaluaciones con la API de Power Platform
- Análisis de referencia: `https://blue16.nl/microsoft-agent-365-control-plane.html`

> *"El QR lleva a la checklist de primeros treinta, sesenta y noventa días. Es una página.
> No hace falta que apuntéis nada de lo que ha salido en la tabla de carriles."*

---

# Q&A · 0:44 → 0:50 · (11:44–11:50)

`⏱ CHECKPOINT 4 — a las 11:44 debes estar en Q&A, hayas terminado o no.`
Si a las 11:43 sigues en el bloque 8: salta el modelo L1/L2/L3 y ve directo al cierre.

### Las ocho que van a caer, con la respuesta en una línea

| Pregunta | Respuesta |
|---|---|
| *"Estamos en E3 + Copilot, ¿podemos usar Agent 365?"* | No sois elegibles. Pero el 70% de este modelo se hace solo con Power Platform y carriles |
| *"¿Esto sustituye al CoE Starter Kit?"* | Para inventario, sí: Inventory/Usage/Monitor/Actions ya lo cubren |
| *"¿Y los agentes de terceros y de otros clouds?"* | Registry Sync multicloud en preview, o el SDK. Lo no onboardado solo se ve como Shadow AI |
| *"¿El SDK me obliga a cambiar de framework?"* | No. No construye ni hospeda agentes: se acopla al que ya tienes |
| *"¿Puedo gobernar un agente que corre en el portátil de un dev?"* | Con identidad y telemetría, sí. Sin onboarding, solo detección en endpoint |
| *"¿Cuánto cuesta esto realmente?"* | Gobierno por usuario + ejecución por créditos. Facturas distintas. No hay un TCO end-to-end oficial |
| *"¿Advanced Connector Policies está listo para producción?"* | Preview, y solo por environment group. Diseñad en allowlist ya, aplicad cuando salga |
| *"¿Podemos bloquear que la gente cree agentes?"* | Podéis, y es el error más caro. Dadles playground con límites |

**Si no hay preguntas** (pasa, sobre todo a las 11 de un sábado), ten una preparada tú:

> *"Os hago yo la que siempre me hacen: ¿por dónde empiezo el lunes si solo tengo una hora?
> Abrís All agents, exportáis el inventario y filtráis por «sin propietario».
> Esa lista es vuestro backlog. Con eso ya habéis hecho más que el 90% de las empresas."*

**Si alguien se enroca** con un caso muy particular: *"esto lo vemos fuera, que hay gente esperando
la siguiente sesión"*. No dejes que una pregunta se coma los seis minutos.

---

# Anexos operativos

## A. Mapa de slides — deck ya montado

El deck está construido:
`01_trabajo/BizzSummit2026_De_la_jungla_al_control_plane.pptx`

**34 slides, de las cuales 30 visibles y 4 ocultas** (los planes B, que no salen en presentación
pero están ahí si las necesitas: `Ctrl` + clic derecho → *Ir a la diapositiva*, o quítales la
marca de oculta antes de empezar si decides usarlas).
**Todas las slides visibles llevan notas del ponente** con su minutaje, sus frases literales y,
en los separadores de demo, los beats completos.

| # | Contenido | Bloque | Maqueta de origen |
|---|---|---|---|
| 1 | Título de la sesión | 0 | plantilla 1 |
| 2 | Sponsors — **intacta, no se toca** | 0 | **plantilla 5** |
| 3 | El gancho: «¿cuántos agentes tenéis ahora mismo?» | 0 | plantilla 8 |
| 4 | MILLONES — el dato de contraste | 0 | plantilla 31 |
| 5 | Lo que te llevas el lunes | 0 | plantilla 13 |
| 6 | FraSoHome en una frase | 0 | plantilla 16 |
| 7 | No es Shadow IT de siempre | 1 | plantilla 12 |
| 8 | Cuatro riesgos de runtime | 1 | plantilla 27 |
| 9 | Los cinco síntomas de la jungla | 1 | plantilla 7 |
| 10 | Visibilidad antes que control | 1 | plantilla 28 |
| 11 | **Tres capas de gobierno** ⭐ | 2 | plantilla 13 |
| 12 | Tres mensajes + licenciamiento | 2 | plantilla 14 |
| 13 | El inventario ya existe | 3 | plantilla 12 |
| 14 | **DEMO 1 — ¿Quién es?** | 3 | plantilla 9 |
| *15* | *Plan B demo 1 — oculta* | — | plantilla 25 |
| 16 | Carriles, no comités | 4 | plantilla 12 |
| 17 | **Los cuatro carriles** ⭐ tabla | 4 | plantilla 34 |
| 18 | Las tres reglas duras | 4 | plantilla 20 |
| 19 | Qué puede leer y qué devuelve | 5 | plantilla 12 |
| 20 | **DEMO 2 — ¿Qué lee?** | 5 | plantilla 10 |
| *21* | *Plan B demo 2 — oculta* | — | plantilla 25 |
| 22 | Ciclo de vida y calidad | 6 | plantilla 13 |
| 23 | **DEMO 3 — ¿Funciona?** | 6 | plantilla 9 |
| *24* | *Plan B demo 3 — oculta* | — | plantilla 25 |
| 25 | El Agent 365 SDK: qué es, qué no | 7 | plantilla 12 |
| 26 | El blueprint de identidad | 7 | plantilla 16 |
| 27 | **DEMO 4 — El otro agente** | 7 | plantilla 10 |
| *28* | *Plan B demo 4 — oculta* | — | plantilla 25 |
| 29 | La cadencia operativa | 8 | plantilla 27 |
| 30 | Cierre: «Volved y contad» | 8 | plantilla 28 |
| 31 | Recursos | — | plantilla 12 |
| 32 | Q&A | — | plantilla 36 |
| 33 | ¡Gracias! + QR de feedback | — | plantilla 37 |
| 34 | Bizz Summit 2026 — contacto | — | plantilla 38 |

**30 slides visibles para 44 minutos.** Descontando los cuatro separadores de demo y las tres
slides de cierre institucional, hablas sobre ~23 slides en ~30 minutos: unos 78 segundos por
slide. Es un ritmo cómodo para nivel 300.

### Lo que queda por hacer sobre el deck

- [ ] Insertar el **QR de la checklist 30/60/90** en el hueco derecho de la slide 31
- [ ] Sustituir las imágenes de relleno de las cuatro slides de plan B por las capturas reales
- [ ] Incrustar los cuatro vídeos de plan B **dentro** del PowerPoint, no enlazados
- [ ] Si tu handle público es distinto de tu nombre, ajustarlo en la portada

## B. Orden de ventanas en la pantalla

Ten **todo abierto antes de empezar**. No abras nada durante la sesión.

| Ventana | Qué | Para |
|---|---|---|
| 1 | PowerPoint en modo presentador | Todo |
| 2 | Teams — chat del Asistente de Devoluciones | Demos 1 y 2 |
| 3 | M365 Admin Center → *All agents* | Demos 1 y 4 |
| 4 | PPAC → Inventory | Demo 1 |
| 5 | PPAC → Data policies | Demo 2 |
| 6 | Copilot Studio → pestaña Evaluation | Demo 3 |
| 7 | Copilot Agent Kit → Agent Change Tracker | Demo 3 |
| 8 | Claude Code con el repo de `fs-triage-devoluciones` | Demo 4 |
| 9 | Carpeta con los vídeos de plan B | Emergencias |

Zoom del navegador al **125%** en todas. Fuente del terminal a **18pt como mínimo**.
Notificaciones silenciadas. Modo no molestar. Segundo monitor con las notas.

## C. Qué recortar, en orden, si vas tarde

1. Bloque 1.1 (app vs agente) → una frase
2. Bloque 5 (teoría de datos) → solo endpoint filtering y Purview DLP, fuera ACP
3. Bloque 3.3 (cara Power Platform del inventario) → entero
4. Bloque 8, modelo L1/L2/L3 → entero
5. Demo 3 → solo el beat 2 (el Change Tracker), enseñando el resultado del test set en captura

**Nunca se recortan:** el bloque 4 (carriles), la demo 4 y el cierre.

## D. Variantes de duración

**30 minutos** — Bloques 0, 1 (solo los cinco síntomas), 2, 4 entero, 8.
Dos demos: la **2** y la **4**. Se sacrifican inventario en profundidad, ALM y evaluaciones,
que quedan en la checklist.

**75 minutos** — Se añade:
- Ejercicio interactivo de 8': las mesas clasifican tres agentes de FraSoHome en carriles y lo justifican
- Profundizar en multiagente y component collections
- Ampliar la demo 4 con `a365-code-validator` y la vista de telemetría en Defender
- Caso real con cifras de antes/después
