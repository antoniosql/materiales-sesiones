# De la jungla de agentes al control plane
## Guion minuto a minuto — Bizz Summit Madrid 2026

| | |
|---|---|
| **Sesión** | De la jungla de agentes al control plane: gobierno real de Copilot Studio con Agent 365 |
| **Cuándo** | Sábado 3 de octubre de 2026, **11:00** |
| **Dónde** | U-tad, Calle Playa de Liencres 2 dupdo., Las Rozas (Madrid) |
| **Slot** | **50 minutos, Q&A incluido** (regla de la organización) |
| **Reparto** | 43' de contenido + 7' de Q&A |
| **Nivel** | 300 |
| **Escenario** | FraSoHome — ver `00_escenario-frasohome.md` |
| **Montaje de demos** | `demos/guia-despliegue-manual.html` |

> **Versión del 2 de octubre.** El foco pasa a Microsoft 365 y Agent 365: ver todos los agentes
> (también los de Agent Builder), saber qué hacen los usuarios con ellos, decidir desde un solo
> sitio y registrar los externos. Power Platform queda en dos slides, como lo que ya existía
> antes de Agent 365. Las notas del deck ya están alineadas con este guion.

---

## Cómo leer este guion

- **Reloj** = hora de pared, para que mires el móvil y sepas si vas bien.
- Lo que va *en cursiva y entre comillas* se dice **literal**.
- Los **`⏱ CHECKPOINT`** son los cuatro puntos de control. La sección C dice qué recortar.

**La frase ancla, que se repite tres veces** (síntomas, control central y cadencia):

> *"Un agente sin propietario nombrado no es un agente: es una incidencia esperando fecha."*

---

## Mapa de tiempos

| Reloj | Slide | Bloque | Dura |
|---|---|---|---|
| 11:00 | 1–2 | Título + sponsors | 0:40 |
| 11:00:40 | 3–6 | Apertura, contrato y FraSoHome | 1:50 |
| 11:02:30 | 7, 9, 10 | **1 · La jungla** | 4:00 |
| 11:06:30 | 11–12 | **2 · Las tres capas** | 3:00 |
| 11:09:30 | 13 | **3 · El inventario ya existe** | 2:00 |
| 11:11:30 | 14 | 🎬 **DEMO 1** — ¿cuántos hay y de quién son? | 4:00 |
| 11:15:30 | 16–17 | **4 · Lo que ya teníais** (Power Platform) | 4:00 |
| 11:19:30 | 19 | **5 · Qué hacen los usuarios** | 2:00 |
| 11:21:30 | 20 | 🎬 **DEMO 2** — ¿qué hacen con ellos? | 4:00 |
| 11:25:30 | 22 | **6 · Control central** | 2:00 |
| 11:27:30 | 23 | 🎬 **DEMO 3** — ¿quién decide? | 3:30 |
| 11:31 | 25–26 | **7 · El agente que no es de Microsoft** | 2:30 |
| 11:33:30 | 27 | 🎬 **DEMO 4** — el otro agente | 4:30 |
| 11:38 | 29–30 | **8 · Cadencia y cierre** | 4:00 |
| 11:42 | 31 | Recursos + QR | 1:00 |
| 11:43 | 32 | **Q&A** | 7:00 |

Demos: **16 minutos** sobre 43 de contenido. Power Platform baja de once minutos a cuatro.

---

# BLOQUE 0 — Apertura · 11:00 → 11:02:30

### Slides 1 y 2 · 40"
La de sponsors es obligatoria. No la leas.

> *"Gracias a los patrocinadores, que son los que hacen que esto exista. Vamos al grano,
> porque tengo cincuenta minutos y cuatro demos."*

### Slide 3 · el gancho
> *"Manos arriba: ¿cuántos de vosotros tenéis agentes en vuestro tenant ahora mismo?"*
> *"Bajad la mano los que no podríais demostrarlo con una captura en los próximos dos minutos."*
> *"Esa diferencia es de lo que va esta sesión."*

### Slide 4 · el dato
> *"En los primeros meses de preview de Agent 365 aparecieron decenas de millones de agentes en el
> registry. No eran proyecciones: eran agentes que ya existían."*

### Slide 5 · lo que te llevas el lunes
1. **Inventario**: todos los agentes —Agent Builder, Copilot Studio, SharePoint, terceros— y de quién es cada uno
2. **Uso y control**: qué hacen los usuarios con ellos, y aprobar, bloquear o reasignar desde un sitio
3. **Agentes externos**: cómo entran en el mismo control plane

> *"Las tres pasan por el admin center de Microsoft 365. No por Power Platform."*

### Slide 6 · FraSoHome, 20 segundos
> *"Todo lo que veáis hoy pasa en FraSoHome: muebles y decoración, tres tiendas, e-commerce.
> Un proceso, devoluciones, y tres agentes: uno que hizo un jefe de tienda con Agent Builder,
> otro que hizo Operaciones con Copilot Studio, y otro que hizo un desarrollador con el SDK de Claude."*

---

# BLOQUE 1 — La jungla · 11:02:30 → 11:06:30

### Slide 7 · no es la Shadow IT de siempre
> *"La Shadow IT clásica era un problema de exposición. Esto es un problema de agencia."*

> *"Y la diferencia de 2026: crear un agente ya no exige Power Platform. Cualquiera con Copilot
> Chat lo hace con Agent Builder en dos minutos."*

(La slide 8, los cuatro riesgos, queda oculta. Si te sobra un minuto, se puede mostrar.)

### Slide 9 · los cinco síntomas
Cuenta con los dedos:

1. **Agentes que nadie ha contado**, creados con Agent Builder
2. **Compartidos sin control**: un enlace y lo usa media empresa
3. **Nadie sabe qué les preguntan** ni qué datos devuelven
4. **Agentes fuera de Microsoft**, en el portátil de un dev, sin identidad
5. **El maker ya no está**: cambió de equipo hace seis meses

> *"Si habéis marcado tres o más, no tenéis un problema de tecnología. Tenéis una jungla."*

**Primera repetición de la frase ancla**, en el quinto síntoma.

### Slide 10 · visibilidad antes que control
> *"Bloquear la creación de agentes funciona seis semanas. Luego la gente se va a otras herramientas
> y el problema no desaparece: se vuelve invisible."*

**Transición:** *"Si el control sin visibilidad no funciona, ¿por dónde se empieza? Por contar los agentes."*

`⏱ CHECKPOINT 1 — 11:06:30.` Si vas por encima de 11:07:30: slide 7 en una frase.

---

# BLOQUE 2 — Las tres capas · 11:06:30 → 11:09:30

**La slide central (11).** Vuelve a ella con el puntero en cada demo.

| Capa | Pregunta | Dónde |
|---|---|---|
| **Identidad** | ¿Qué agentes hay y de quién son? | Agent 365 Registry · admin center de M365 · Entra Agent ID |
| **Plataforma** | ¿Dónde vive, qué conectores usa, cómo se promociona? | Power Platform Admin Center. Ya existía |
| **Datos y runtime** | ¿Qué preguntan, qué devuelve, qué hace? | Purview DSPM for AI, auditoría y DLP · Defender |

> *"La capa de identidad y la de datos están en Microsoft 365, y ahí es donde aparece Agent 365.
> La de plataforma la veremos rápido, porque ya la conocéis."*

### Slide 12 · tres mensajes y licenciamiento
1. *"Agent 365 no sustituye al PPAC. Es identidad, observabilidad y control."*
2. *"La capa de datos ya la tenéis si tenéis E5. Lo que falta casi nunca es licencia: es configuración."*
3. Licenciamiento, rápido y sin disculparte: por usuario; base E5 o Defender + Purview Suite FLW;
   incluido en M365 E7; **E3 + Copilot no es elegible**; cubre gobierno, no ejecución.

> *"Apuntad la última línea, que es la que os salva de prometer algo que luego no podéis entregar."*

---

# BLOQUE 3 — El inventario ya existe · 11:09:30 → 11:11:30

### Slide 13
- **Todos, en una lista**: admin center de M365 › Agents. Los de Agent Builder, Copilot Studio y
  SharePoint, los de Microsoft y los de terceros.
- Cada agente de Copilot Studio nace con su **Entra Agent ID**.
  > *"La pregunta no es cómo construir el inventario. Es quién lo mira, y con qué cadencia."*
- **Registry y control**: Registry · Access Control · Visualization · Interoperability · Security.
  La columna **Risks** consolida Defender, Entra y Purview.
- Desde la misma lista: **aprobar, bloquear, desplegar y reasignar propietario**.

> *"Si mantenéis el CoE Starter Kit para inventariar, sabed que el inventario que importa ya no está
> ahí: un agente de Agent Builder no vive en ningún entorno."*

**La semilla de la demo 4:**
> *"Lo que no se registra solo aparece como Shadow AI: lo detectas, pero no lo gobiernas como
> identidad. Guardad esa frase, que volvemos a ella en la última demo."*

---

# 🎬 DEMO 1 — «¿Cuántos hay y de quién son?» · 11:11:30 → 11:15:30

**4:00 · riesgo bajo · plan B: slide 15 (oculta), capturas de All agents**

Ventanas abiertas y maximizadas, zoom al 125%: Copilot Chat con el Atajo, y All agents ya filtrado.

**Beat 1 · 45" · Así nace un agente** *(Copilot Chat)*
Abres **«Atajo Devoluciones MAD01»**, que Álvaro, jefe de tienda de Gran Vía, hizo con Agent Builder
y compartió con su equipo. Una pregunta y responde.

> *"Dos minutos. Sin entorno, sin solución, sin pasar por nadie. Así nace un agente en 2026."*

**Beat 2 · 1:30" · Todos en una lista** *(admin center › Agents › All agents)*
Llegas con el filtro aplicado. Están el Atajo, la Calculadora y el **Asistente de Devoluciones** de
Copilot Studio. Abres el Atajo: quién lo creó, con quién está compartido y qué conocimiento usa.

**Beat 3 · 1:00" · La identidad**
Abres el Asistente: **Entra Agent ID**, propietario, usuarios y Risks si hay señal.

> *"Dos herramientas, dos makers, una sola lista. Y ninguno ha pedido permiso a nadie."*

**Beat 4 · 45" · Remate**
> *"El Asistente lo creó Marta, de Operaciones, en marzo. Marta pasó a e-commerce en julio.
> Nadie se lo dijo a este agente."*

**Si algo falla:** pasa a la slide 15 sin anunciarlo: *"lo tengo capturado, que esto tarda"*.

`⏱ CHECKPOINT 2 — 11:15:30.` Si vas por encima de 11:17: la slide 16 en una frase y directo a la tabla.

---

# BLOQUE 4 — Lo que ya teníais · 11:15:30 → 11:19:30

### Slide 16 · Power Platform, en una slide
> *"Todo esto ya existía antes de Agent 365, y nada de esto depende de Agent 365."*

- **Carriles**: entornos por carril con Managed Environments, environment groups y Settings Enforcer.
  El Default endurecido, pero no apagado. *"El maker no pide permiso a un comité: elige carril."*
- **DLP y ACP**: autenticación, canales, conectores y endpoint filtering; las ACP pasan a allowlist y
  bloquean servidores MCP.
- **ALM y calidad**: pipelines y Git, component collections, evaluaciones antes de Producción.

> *"El matiz importante: estos controles solo ven lo que se construye en Power Platform. Un agente de
> Agent Builder o uno externo no vive en ningún entorno, y aquí no aparece."*

### Slide 17 · la tabla de carriles
> *"Esta slide no es para leerla aquí: es para hacerle una foto."* *(tres segundos de silencio)*

Lee solo dos filas: **Agentes externos** y **Propietario**.

> *"Fijaos que las dos filas que más importan son las que no resuelve Power Platform."*

(La slide 18, carriles y comités, queda oculta: su idea está en la 16.)

---

# BLOQUE 5 — Qué hacen los usuarios · 11:19:30 → 11:21:30

### Slide 19
- **Uso**: los informes de uso de agentes del admin center: qué agentes se usan, cuántos usuarios y
  cuáles nadie abre. Agent 365 añade la visualización por agente, también de los externos con telemetría.
  > *"Un agente sin uso es un candidato a archivar. Uno con mucho uso y sin propietario, una urgencia."*
- **Interacciones y datos**: Purview **DSPM for AI** enseña qué preguntan, qué responde y qué datos
  sensibles aparecen. La DLP de Purview bloquea el prompt o la respuesta; las etiquetas con cifrado
  impiden extraer lo que el usuario no puede extraer.
- **El prerrequisito que hunde proyectos**: auditoría unificada activa.

> *"Antes de bloquear nada, mirad qué hacen."*

---

# 🎬 DEMO 2 — «¿Qué hacen con ellos?» · 11:21:30 → 11:25:30

**4:00 · riesgo medio · plan B: slide 21 (oculta), vídeo o capturas**

> ⚠️ Solo va en vivo si a las 9:30 el Activity explorer ya enseña las interacciones de anoche.

**Beat 1 · 1:30" · Las conversaciones** *(Purview › DSPM for AI › Activity explorer)*
Interacciones con los agentes de FraSoHome: usuario, agente, prompt y respuesta. Filtras por
información sensible: aparece un **IBAN**. Álvaro pegó la cuenta de un cliente en un agente.

> *"Nadie ha revisado este agente. Y ya sé que por él ha pasado una cuenta bancaria."*

**Beat 2 · 1:15" · El uso** *(informe de uso de agentes, o Agent 365)*
Qué agentes se usan y cuáles no. Si el informe aún no tiene datos, dilo:

> *"Este informe tarda hasta dos días en llenarse. Por eso la visibilidad se activa el primer día,
> no el día que la necesitas."*

**Beat 3 · 45" · Remate**
> *"La visibilidad estaba en la capa, no en el agente. Y es lo que os deja decidir qué bloquear
> con datos, y no con miedo."*

---

# BLOQUE 6 — Control central · 11:25:30 → 11:27:30

### Slide 22 · tres acciones, un solo sitio
- **Aprobar**: un agente que quiere llegar a toda la organización pide paso. Revisas qué hace, qué toca
  y con quién se comparte antes de publicarlo.
- **Reasignar**: un agente cuyo propietario se fue recibe uno nuevo.
  **Segunda repetición de la frase ancla.**
- **Bloquear**: para toda la organización, venga de Agent Builder, de Copilot Studio o de un tercero.

> *"Quién puede crear y compartir agentes se decide en la configuración de Copilot del admin center.
> No lo cerréis: limitad con quién se comparte. Si cerráis el playground, la experimentación se va
> fuera del tenant, donde no la veis."*

---

# 🎬 DEMO 3 — «¿Quién decide?» · 11:27:30 → 11:31

**3:30 · riesgo medio · plan B: slide 24 (oculta), capturas**

**Beat 1 · 1:15" · Aprobar** *(admin center › Agents › Requests)*
El Asistente de Devoluciones pide publicarse para toda la organización. Abres la solicitud: qué hace,
qué conocimiento usa, quién lo pide. Lo apruebas o lo rechazas con motivo.

**Beat 2 · 1:15" · Bloquear** *(All agents)*
«Calculadora de reembolsos (copia)», un duplicado de Agent Builder. **Bloquear.** Enseñas la captura
de anoche: para el usuario, el agente ya no está.

**Beat 3 · 1:00" · La política** *(admin center › Copilot › Settings)*
Quién puede crear agentes y con quién se pueden compartir.

> *"No os pido que lo cerréis. Os pido que decidáis desde aquí, y no agente a agente."*

`⏱ CHECKPOINT 3 — 11:31.` Si vas por encima de 11:32:30: salta la slide 25 y explícalo en la demo 4.

---

# BLOQUE 7 — El agente que no es de Microsoft · 11:31 → 11:33:30

### Slide 25 · el Agent 365 SDK
> *"Ninguna organización va a construir el cien por cien de sus agentes con herramientas de Microsoft.
> La pregunta no es cómo evitar que existan: es cómo entran en el mismo control plane."*

Qué es: conecta un agente que ya tienes con Agent 365 —identidad en Entra, observabilidad con
OpenTelemetry, tooling con los MCP de Work IQ, notificaciones—. Python, JavaScript y .NET.
Register → Extend → Validate → Operate.

> *"Lo que no es: no construye agentes, no los hospeda, no orquesta pasos. Vosotros seguís siendo
> dueños del modelo, el framework y el host."*

### Slide 26 · el blueprint
> *"Una definición aprobada por IT de la que heredan todos los agentes creados a partir de ella.
> Gobiernas la plantilla, no la instancia."*

> *"Un agente externo puede llegar a Producción. Pero solo con blueprint, identidad, telemetría
> y propietario. No hay atajo."*

---

# 🎬 DEMO 4 — «El agente que no es de Microsoft» · 11:33:30 → 11:38

**4:30 · riesgo medio · es el cierre · plan B: slide 28 (oculta), terminal grabado**

### La precondición, que es media demo
El repo de `fs-triage-devoluciones` en VS Code. Enseñas el resumen del triaje de anoche: reparto por
motivo y el patrón de `hectorvidal@example.com`, cuatro devoluciones en una semana. Y el `.env`.

> *"Esto lo escribió David, de e-commerce, con el Agent SDK de Claude. Funciona. Y no aparece en
> All agents, ni en DSPM, ni en la factura de nadie. Esto es lo que antes llamábamos Shadow AI."*

**Beat 1 · 1:15" · Observabilidad** *(Claude Code)*
```
añade observabilidad con OpenTelemetry a este agente, sin cambiar su lógica
```
Enseña el diff: *"Ha añadido. No ha reescrito el agente ni ha cambiado el framework."*

**Beat 2 · 1:15" · Registro** — **solo si el tenant tiene Agent 365**
Registro con su blueprint y tooling por los MCP de Work IQ.

> *"Work IQ requiere permisos delegados. Con autenticación S2S la skill se salta sola y no os dice
> por qué. Es una decisión de antes de escribir el agente."*

Si no hay Agent 365, vuelve a la slide 26 y cuéntalo sobre el blueprint.

**Beat 3 · 1:00" · Los tres juntos** — **solo si el beat 2 funcionó**
All agents con los tres agentes de FraSoHome. Silencio.

**Beat 4 · 30" · Remate de la sesión**
> *"El control plane no pregunta con qué lo construiste. Pregunta quién eres, qué tocas y quién
> responde por ti."*

---

# BLOQUE 8 — Cadencia y cierre · 11:38 → 11:42

### Slide 29 · la cadencia
| Cadencia | Quién | Qué mira |
|---|---|---|
| Semanal | Admin de plataforma | Nuevos y sin propietario en All agents |
| Mensual | Admin y negocio | Uso por agente y agentes que nadie abre |
| Trimestral | Seguridad | Interacciones con datos sensibles en DSPM |
| Anual | Owners de negocio | Revalidar propietario y quién lo usa |

> *"Sin esto, el inventario es una foto de un día."*

**Tercera repetición de la frase ancla.**

### Slide 30 · volved y contad
> *"Volved a vuestro tenant el lunes. Abrid All agents. Y contad. La cifra os va a sorprender,
> y es una buena noticia: el inventario ya lo tenéis. Lo que falta es decidir quién lo mira cada semana."*

---

# RECURSOS · 11:42 → 11:43
Slide 31 con el QR a la checklist 30/60/90. Documentación del admin center de agentes, Agent Builder,
DSPM for AI, la guía de gobierno de Copilot Studio, Agent 365, el SDK y Entra Agent ID.

---

# Q&A · 11:43 → 11:50

`⏱ CHECKPOINT 4 — a las 11:43 estás en Q&A, hayas terminado o no.`

| Pregunta | Respuesta |
|---|---|
| *"Estamos en E3 + Copilot, ¿podemos usar Agent 365?"* | No sois elegibles. Pero el inventario y el control de agentes del admin center ya los tenéis |
| *"¿Los agentes de Agent Builder salen sin Agent 365?"* | Sí, en el admin center. Agent 365 añade la identidad, la observabilidad y los externos |
| *"¿Esto sustituye al CoE Starter Kit?"* | Para inventariar agentes, sí. Y además ve lo que el CoE no ve |
| *"¿Y los agentes de terceros y de otros clouds?"* | Registry Sync multicloud en preview, o el SDK. Lo no registrado solo se ve como Shadow AI |
| *"¿El SDK me obliga a cambiar de framework?"* | No. No construye ni hospeda: se acopla al que ya tienes |
| *"¿Cuánto cuesta?"* | Gobierno por usuario y ejecución por créditos. Dos facturas |
| *"¿Podemos bloquear que la gente cree agentes?"* | Podéis, y es el error más caro. Limitad con quién se comparten |

**Si nadie pregunta:**
> *"¿Por dónde empiezo el lunes si solo tengo una hora? Abrís All agents y filtráis por sin propietario
> y por compartidos con toda la organización. Esa lista es vuestro backlog."*

---

# Anexos

## A. Mapa de slides

34 slides, **28 visibles**. Las ocultas se muestran con `Ctrl` + clic derecho › *Ir a la diapositiva*.

| # | Contenido | Bloque |
|---|---|---|
| 1–2 | Título y sponsors (intacta) | 0 |
| 3–6 | Gancho, millones, lo que te llevas, FraSoHome | 0 |
| 7 | No es Shadow IT de siempre | 1 |
| *8* | *Cuatro riesgos — oculta* | 1 |
| 9–10 | Cinco síntomas · Visibilidad antes que control | 1 |
| 11–12 | **Tres capas** · Tres mensajes y licenciamiento | 2 |
| 13 | El inventario ya existe | 3 |
| 14 | **DEMO 1 — ¿Cuántos hay?** | 3 |
| *15* | *Plan B demo 1 — oculta* | |
| 16 | **Lo que ya teníais** (Power Platform) | 4 |
| 17 | Los cuatro carriles (tabla) | 4 |
| *18* | *Carriles, no comités — oculta* | 4 |
| 19 | Qué hacen los usuarios | 5 |
| 20 | **DEMO 2 — ¿Qué hacen?** | 5 |
| *21* | *Plan B demo 2 — oculta* | |
| 22 | Control central | 6 |
| 23 | **DEMO 3 — ¿Quién decide?** | 6 |
| *24* | *Plan B demo 3 — oculta* | |
| 25–26 | Agent 365 SDK · Blueprint | 7 |
| 27 | **DEMO 4 — El otro agente** | 7 |
| *28* | *Plan B demo 4 — oculta* | |
| 29–30 | Cadencia · Volved y contad | 8 |
| 31–34 | Recursos, Q&A, gracias, contacto | |

**Pendiente sobre el deck:** el QR de la checklist en la slide 31, y las capturas y vídeos reales
en las cuatro slides de plan B, incrustados y no enlazados.

## B. Ventanas, en este orden
1. PowerPoint en modo presentador
2. Copilot Chat · Atajo Devoluciones MAD01 (demo 1)
3. Admin center de M365 · Agents › All agents, ya filtrado (demos 1 y 3)
4. Purview · DSPM for AI › Activity explorer, ya filtrado (demo 2)
5. Admin center de M365 · Agents › Requests (demo 3)
6. Admin center de M365 · Copilot › Settings (demo 3)
7. Terminal y Claude Code en `fs-triage-devoluciones` (demo 4)

Zoom al 125%, terminal a 18 pt, notificaciones silenciadas.

## C. Qué recortar si vas tarde, en orden
1. Slide 7 → una frase
2. Slide 16 → una frase, y directo a la tabla
3. Slide 25 → se explica dentro de la demo 4
4. Demo 3, beat 3 (la configuración de Copilot) → una frase
5. Demo 2, beat 2 (el informe de uso) → una frase

**Nunca se recortan:** la demo 1, la demo 4 y el cierre.
