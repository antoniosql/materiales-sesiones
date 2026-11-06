# Autopsy of a Fabric migration: what the capacity bill said six months later — Guion

| | |
|---|---|
| Evento | Power BI & Fabric Summit 2027 · online · 22–26 feb 2027 |
| Formato | **45' pregrabados + 15' de Q&A en directo** (las sesiones se repiten por zonas horarias) |
| Idioma | Inglés. Las frases para decir van en inglés; las notas de dirección, en español |
| Caso | Adopción real **anonimizada sobre FraSoHome** (retail de hogar: tiendas, e-commerce, fidelización) |
| Tono | Post-mortem *blameless*, con cifras. No es una sesión de diseño |
| Slides | ≈26 + 5 clips de demo grabados (≤90 s cada uno) |

> ⚠️ **Las cifras del caso.** Las cifras de este guion son una **reconstrucción coherente** que encaja con el abstract (+40 % de factura, un tercio de workspaces sin usuarios activos). Están calculadas con precios de lista en USD (F SKU, East US: 0,18 $/CU-hora PAYG; F64 reservada a 5.002,67 $/mes; OneLake a 0,023 $/GB-mes). **Antes de grabar, sustitúyelas por las de tu caso real** o, si las mantienes, ajusta la frase de la apertura sobre "the ratios are the real ones". Todos los cálculos derivados están en *Anexo C*, así que puedes cambiar los datos de entrada y recalcular.

## La tesis en una frase

> **"The architecture diagram had no box for the organisation. The invoice did."**

## Los tres mensajes que tienen que sobrevivir a la sesión

1. **Con una capacidad reservada, el crecimiento del consumo no aparece en la factura.** Aparece primero como *throttling* y después como una línea nueva que alguien llama "temporal". La factura subió un 40 %, pero el consumo subió un 112 %.
2. **La dispersión no se decide: se acumula.** Cada workspace sin dueño, dominio ni fecha de caducidad fue una decisión razonable que tomó otra persona.
3. **Todas las señales existían antes que la factura.** Lo que faltaba era alguien con la obligación de mirarlas y una reunión donde enseñarlas.

## Escaleta

| Min | Bloque | Qué pasa | Clip |
|---|---|---|---|
| 00:00–02:30 | Apertura | La factura del mes 6 | — |
| 02:30–04:00 | Reglas de la autopsia | Quién soy, *blameless*, qué te llevas | — |
| 04:00–07:00 | 0 · El paciente | FraSoHome y un diseño que era correcto | — |
| 07:00–20:00 | 1 · La cronología M0–M6 | Seis estaciones: decisión → efecto → la señal que ya estaba ahí | **Clips 1, 2 y 3** |
| 20:00–27:00 | 2 · Lo que dice el cuerpo | Dónde fueron las CU · anatomía de la dispersión · artefactos abandonados · el comité frente a la telemetría | — |
| 27:00–35:00 | 3 · La instrumentación | CU, linaje, propiedad y actividad, con el *toolbox* actual | **Clips 4 y 5** |
| 35:00–42:00 | 4 · Las cuatro decisiones | Qué se decidió, qué alternativa había y cuánto habría cambiado | — |
| 42:00–45:00 | Cierre | El kit del día 1 y la frase para el comité | — |
| 45:00–60:00 | Q&A en directo | Respuestas preparadas | — |

**Puntos de control al grabar.** En el 07:00 tienes que estar en la slide de la cronología. En el 20:00, en "Where the CUs went". En el 35:00, en la primera decisión. Como es pregrabada, graba por bloques y monta después. Si un bloque se va de tiempo, consulta *Recortes*.

---

## Antes de grabar

- [ ] **Sustituir o validar las cifras** (ver el aviso de arriba y el *Anexo C*).
- [ ] **Tenant FraSoHome en Fabric** con lo mínimo para los clips (ver *Preparación de los clips*). No hace falta reproducir 147 workspaces: los clips enseñan **dónde está la señal**, y las cifras del caso van en las slides.
- [ ] **Instalar** las dos experiencias de la Capacity Metrics app (GA y la nueva *preview*) y la Chargeback app sobre la capacidad de demo, **con al menos 14 días de actividad** antes de grabar los clips 1 y 4.
- [ ] Activar **workspace monitoring** en el workspace de demo **dos semanas antes**: no rellena el histórico hacia atrás.
- [ ] Grabar a 1080p con el zoom del navegador al 125 %. Cada clip dura ≤90 s y lleva subtítulos quemados, porque el público ve la sesión en zonas horarias y con conexiones muy distintas.
- [ ] **Revisar la lista *Por verificar*** (Anexo D) una semana antes de grabar. Varias funciones están en *preview* o se han anunciado como "GA soon".
- [ ] Preparar el **handout** (checklist del día 1 + catálogo de herramientas) y el enlace del repositorio para que el moderador lo pegue en el chat.

---

## 00:00–02:30 · Apertura: la factura

**Slide 1 — Negra, con dos cifras grandes:**

> **Month 0: $6,148** · **Month 6: $8,607**

> "This is a capacity bill. Same company, same platform, same architecture. Six months apart."
>
> *(pausa)*
>
> "The migration was delivered on time. The architecture diagram was reviewed and approved, and I'd sign it again today. And yet, six months later, the bill was forty percent higher, and one in three workspaces had nobody using it."

**Slide 2 — Tres cifras, una debajo de otra:**

- **+40 %** monthly bill
- **49 of 147** workspaces with no active users in 30 days
- **31 %** of the production capacity spent on items nobody opened

> "That last number is the one that hurt. Almost a third of the capacity was working, every day, for nobody."

**Slide 3 — Título:** *Autopsy of a Fabric migration: what the capacity bill said six months later.*

---

## 02:30–04:00 · Las reglas de la autopsia

> "I'm Antonio Soto. I'm a Microsoft MVP in Fabric and Foundry, and I've spent more than twenty-five years on enterprise data projects. I've been on the side that designs these migrations, and I've been on the side that gets the phone call six months later."

**Slide 4 — Rules of this autopsy**

1. **Blameless.** Every decision you'll see was reasonable when it was taken. That's the point.
2. **Anonymised.** "Names and systems are moved to FraSoHome, a fictional home-and-décor retailer I use in all my sessions. The ratios are the ones we saw." *(ajustar si cambias las cifras)*
3. **Numbers.** CU-hours, dollars and users. Not opinions.

**Slide 5 — What you take away**

1. A **timeline** of how cost and sprawl actually accumulate, month by month.
2. The **instrumentation map**: which signal, in which tool, would have shown each problem, and how many months earlier.
3. **Four decisions** to take differently in *your* migration, before go-live.

---

## 04:00–07:00 · Bloque 0 — El paciente

### Slide 6 — FraSoHome antes de la migración (1')

- Retail omnicanal: tiendas físicas, e-commerce y programa de fidelización. CRM, POS, e-commerce y ERP.
- **Punto de partida:** Power BI Premium P1, SQL Server *on-premises* + SSIS y una carpeta compartida llena de Excel "de cierre".
- **Motivo de la migración:** fin del P1 y un plan de datos con medallion, Direct Lake y algo de IA.

> "A very normal company. That's why I like this case: there's nothing exotic in it."

### Slide 7 — El diagrama que se aprobó (1')

Diagrama limpio: fuentes → *bronze / silver / gold* en lakehouses → modelos semánticos Direct Lake → informes y apps. **Cinco dominios** (Ventas, Supply & Stock, Finanzas, Clientes & Fidelización, Corporativo). Workspaces separados por dominio, capa y entorno.

> "This is a good design. Domains, medallion, environments, Direct Lake. If you showed me this in a review, I'd approve it. I did."

### Slide 8 — El plan de capacidad y lo que se le dijo al comité (1')

| Línea | Plan | $/mes |
|---|---|---|
| Producción | **F64 reservada 1 año** ("equivale a nuestro P1") | 5.003 |
| Dev/Test | F8 PAYG, *"la pausaremos noches y fines de semana"* | 1.051 |
| OneLake | ≈4 TB | 94 |
| **Total** | | **6.148** |

> "Remember three words on this slide: *equivalent to P1*. We'll come back to them. And remember the promise about pausing dev at night. Nobody ever automated it."

---

## 07:00–20:00 · Bloque 1 — La cronología, mes a mes

**Slide 9 — Línea temporal M0 → M6** con seis hitos. En cada estación, la misma estructura de tres casillas en pantalla:

> **The decision** · **What it did to capacity** · **The signal that was already there**

> "For each month I'll tell you what we decided, what it did to the capacity, and where the signal was. Spoiler: the signal was always there before the invoice."

### M0 — Go-live: "migramos todo" (07:30–09:30)

**Decisión.** *Lift & shift* de los **64 workspaces** del P1 y sus **212 informes**, *"para no romper nada"*. La F64 se dimensiona por equivalencia de licencia, no por carga.

**Efecto.** Llegan a Fabric todos los refrescos programados heredados, incluidos los de contenido muerto.

**La señal que ya estaba.** El registro de actividad de los 90 días anteriores a la migración: **81 de 212 informes (38 %) tenían cero visualizaciones**.

> "We migrated the dead. Nobody asked the activity log before moving them, and the activity log would have answered in an afternoon."

**Herramienta (en la slide):** API de *Activity Events* de admin (ventana corta, hay que extraer a diario) · *Unused artifacts API* (preview, 30 días; modelos, informes y paneles) · FUAM para conservar el histórico.

### M1 — Se abre el autoservicio (09:30–11:30)

**Decisión.** El tenant setting *Create workspaces* se habilita para el grupo *Fabric Creators* (380 personas). Hay un curso interno de Fabric y **cada alumno crea su workspace**.

**Efecto.** En un mes nacen **12 workspaces del curso**, más las primeras "copias de trabajo" departamentales. Ninguno tiene dominio asignado, porque la asignación de dominio era manual.

**La señal que ya estaba.** El inventario de workspaces por fecha de creación y el porcentaje sin dominio.

> "Nobody decided to have a hundred and forty-seven workspaces. Three hundred and eighty people each decided to have one."

**Herramientas:** **OneLake catalog → Govern** (inventario, cobertura de curación, filtro por dominio y acciones recomendadas; GA) · *default domain* por grupo de seguridad · restricción del tenant setting a grupos · **Policies in Fabric** (preview: *Item creation* a nivel de capacidad).

### M2 — Las copias del modelo de Ventas (11:30–14:00) · Clip 1

**Decisión.** Cada departamento quiere "su" modelo de Ventas con sus columnas. En lugar de un modelo compartido con perspectivas, se permiten copias en import. Al final hay **14 copias**, cada una con **8 refrescos al día**. Además, los Dataflows Gen2 heredados hacen **recargas completas**, sin incremental.

**Efecto.** La utilización media de la F64 pasa del **41 % al 63 %**. **La factura no se mueve ni un dólar**, porque la capacidad está reservada.

> "This is the most important moment of the whole story, and nobody noticed it. Consumption went up by half, and the invoice was flat. With a reservation, growth is invisible on the bill. It shows up somewhere else first."

**Clip 1 (75 s) — Capacity Metrics app, página *Compute* (nueva experiencia en preview):**
1. Gráfico de utilización en CU-segundos con el **heatmap horario**: se ve la franja de refrescos a las 6:00, 9:00, 12:00…
2. Tabla de **top items por CU** de los últimos 14 días: aparecen varias copias del mismo modelo en la cabeza del ranking.
3. *Item details*: 14 días de historia de un modelo concreto y su impacto en la capacidad.

> "Fourteen copies of the same truth, refreshing eight times a day. The Metrics app ranks them for you. You just have to open it on a Tuesday, not on the day the invoice arrives."

**Herramientas:** Metrics app (Compute, *Timepoint summary/detail* GA, Item details) · Monitor hub (ejecuciones de refresco) · **Chargeback app** (GA: % de capacidad por workspace, item, dominio y usuario, con refresco diario).

### M3 — El cierre de mes (14:00–16:30) · Clip 2

**Decisión, en realidad una reacción.** En el segundo día del cierre contable, los informes de Finanzas tardan, primero con **retrasos de 20 s** y después con **rechazos interactivos**. El CFO escala la incidencia. Solución de urgencia: una **F16 PAYG "temporal" para Finanzas** (+2.102 $/mes). Además se activa la *capacity overage*, que factura 224 CU-h a **3× la tarifa PAYG** (+121 $).

**Efecto.** El problema desaparece de la vista, y la F16 se queda para siempre. En el mes 6 sigue ahí, con la etiqueta de Azure `temporary`, sin fecha de caducidad y sin dueño.

> "There is nothing more permanent than a temporary capacity."

**Explicación técnica (slide, 30 s):** el *background* se suaviza en 24 h y el interactivo en ventanas de 5 a 64 minutos. Cuando el uso suavizado supera los 10 minutos de capacidad futura llegan los retrasos; por encima de 60 minutos, los rechazos interactivos; y por encima de 24 h se rechaza también el background. Las recargas completas de la noche "pre-gastaron" la capacidad del día de cierre.

**Clip 2 (60 s) — Página *Health* de la Metrics app + Capacity events:**
1. **% de tiempo en throttling** por capacidad y periodo, con p95 frente a media.
2. Real-Time hub → **Capacity overview events** (GA) → regla de **Activator** a partir de la plantilla de alertas de capacidad: avisar en Teams cuando el uso suavizado supere el 80 %.

> "The average said sixty-three percent, which looks healthy. The p95 said we were above a hundred percent on four days of that month. Averages are how capacities lie to steering committees."

**Lo que habría cambiado el resultado (se adelanta, 20 s):** *surge protection* a nivel de workspace, con Finanzas marcada como *Mission critical*; esto habría bloqueado antes el workspace del notebook prototipo. Lo desarrollamos en la decisión 1.

### M4 — Los pilotos que nadie apagó (16:30–18:00)

**Decisión.** Tres pilotos en la capacidad de producción "porque ya estaba pagada":
- **POC de Real-Time** (afluencia a tiendas): un Eventstream y un Eventhouse siempre encendidos tras la demo al comité → **8 % de la CU**.
- **Piloto de Copilot y data agents** con 40 usuarios, que se facturan en la capacidad del contenido → junto con las *AI functions* de un notebook de clasificación de devoluciones, **6 % de la CU**.
- **Notebook prototipo de stock cada 15 minutos**, con sesiones que se quedan ociosas hasta el *timeout* de 20 minutos.

> "Every pilot had a sponsor at the start and nobody at the end. Pilots don't fail. They just never stop."

**Herramientas:** **Fabric Copilot capacity**, para separar la factura de Copilot y de los data agents de un grupo de usuarios · *Item details* (14 días) · *timeout* de sesión Spark y orquestación con pipeline · **On-demand billing para Spark** (GA, antes *Autoscale Billing*) · etiquetas de Azure con fecha de caducidad y Azure Policy que las exija.

**Caso público (en la slide, 15 s):** Gilbert Quevauvilliers (FourMoo) midió un notebook con *Run all* que consumía **1.320 s** por la sesión ociosa, frente a **67 s** parando la sesión: **un 95 % menos**.

### M5 — Se va la consultora (18:00–19:15)

**Decisión.** Termina el contrato del partner y se desactivan sus cuentas.

**Efecto.** **11 pipelines y notebooks** fallan porque se ejecutaban con la identidad de cuentas del partner. En **23 de los 49 workspaces inactivos**, el único administrador ya no está en la empresa o ha cambiado de puesto. Para entonces, **el 61 % de los workspaces no tiene dominio**.

> "Ownership is not a field you fill in at go-live. It's a field that decays."

**Caso público (slide):** Sam Debruyn, *Thread by Thread: Lessons from Migrating to Fabric* (feb. 2026). La identidad de ejecución de notebooks y pipelines resultaba ser, a menudo, la de **la última persona que modificó el item**, y abrirlo parecía contar como modificación.

**Herramientas:** **Scanner API** (usuarios y roles por workspace, fuentes de datos, linaje) · **Lineage view** y análisis de impacto · Govern → *My items* para cada dueño · FUAM (inventario histórico).

### M6 — La factura (19:15–20:00)

**Slide 10 — La factura desglosada**

| Línea | M0 | M6 | Δ |
|---|---|---|---|
| F64 reservada | 5.003 | 5.003 | 0 |
| F8 dev (nunca pausada) | 1.051 | 1.051 | 0 |
| F16 "temporal" Finanzas | — | 2.102 | **+2.102** |
| Capacity overage | — | 121 | **+121** |
| OneLake (4 → 14 TB) | 94 | 330 | **+236** |
| **Total** | **6.148** | **8.607** | **+40 %** |

> "Look at the first line. The capacity that did all the work didn't change at all. Everything that grew on this invoice is a *symptom*: the escape valve, the overage and the copies. The disease is in a line that says zero."

**Slide 11 — La frase del bloque:**

> **"The bill said 40 %. The capacity said 112 %."** (utilización media del 41 % → 87 %)

---

## 20:00–27:00 · Bloque 2 — Lo que dice el cuerpo

### Slide 12 — Dónde fueron las CU (2')

Uso de la F64 en el mes 6, con una utilización media del 87 % (≈40.650 CU-h/mes):

| Consumidor | % CU | CU-h/mes | ¿Lo usaba alguien? |
|---|---|---|---|
| Refresco de modelos import (14 copias de Ventas + otros) | 27 % | ≈10.975 | **9 de 14 copias con 0 vistas en 30 días** |
| Notebooks Spark (incluye sesiones ociosas y el prototipo de stock) | 19 % | ≈7.725 | Prototipo de stock: sin consumidores |
| Dataflows Gen2 con recarga completa | 14 % | ≈5.690 | Sí, pero con mucha más CU de la necesaria |
| Interactivo de informes (incluye *fallback* de Direct Lake a DirectQuery) | 11 % | ≈4.470 | Sí |
| POC de Real-Time siempre encendido | 8 % | ≈3.250 | **No** |
| Copilot + data agents + AI functions | 6 % | ≈2.440 | 40 usuarios piloto |
| Resto | 15 % | ≈6.100 | — |

> "Add up what nobody used: nine of the fourteen copies, the Real-Time POC and the stock prototype. Thirty-one percent. Almost a third of the capacity, working for nobody."

**Nota sobre el *fallback* (15 s):** tablas sin mantenimiento, con muchos ficheros pequeños, y algunas vistas SQL hacen que los modelos Direct Lake pasen a DirectQuery. El informe "funciona", pero cada clic cuesta más CU interactiva, que es la cara.

### Slide 13 — Anatomía de la dispersión (1,5')

**147 workspaces en el mes 6. 49 sin usuarios activos en 30 días (33 %).**

| Origen | Workspaces | Inactivos | Por qué |
|---|---|---|---|
| Migrados del P1 tal cual | 64 | 19 | Ya estaban muertos antes de migrar |
| Del diseño (dominio × capa × entorno) | 30 | 4 | Entornos de test que nunca se usaron |
| Creados después del go-live | 53 | 26 | Curso, POCs, copias departamentales |
| **Total** | **147** | **49** | |

> "The design produced four dead workspaces. The organisation produced forty-five. That's the difference between the diagram and what happened."

### Slide 14 — Por qué se abandonan los artefactos: cinco causas de muerte (1,5')

1. **Muerto al llegar.** Se migró sin uso previo (M0).
2. **Huérfano.** Su dueño se fue o cambió de puesto (M5).
3. **Sustituido.** Una copia mejor lo dejó obsoleto, pero nadie retiró la antigua (M2).
4. **Piloto eterno.** Cumplió su función en una demo y nunca se apagó (M4).
5. **Resto de formación.** Nació para aprender y nadie lo borró (M1).

> "Notice that none of these is a technical failure. They're all endings that nobody owned."

### Slide 15 — Lo que se le dijo al comité frente a lo que decía la telemetría (2')

| Lo que vio el comité | Lo que decía la telemetría |
|---|---|
| "212 informes migrados, 100 % en plazo" | 81 tenían 0 vistas en los 90 días anteriores. En el M6, 97 tenían 0 vistas en 30 días |
| "1.450 usuarios con acceso" | **410 usuarios activos al mes (28 %)**. El 62 % de las vistas se concentra en 11 informes |
| "53 workspaces creados por negocio: el autoservicio funciona" | 26 de esos 53 estaban inactivos |
| "Capacidad al 63 % de media: sana" (M2) | p95 por encima del 100 % en 4 días del cierre |
| "Coste en presupuesto" (M2) | El consumo había subido un 54 %, invisible por la reserva |
| "Piloto de Copilot: feedback muy positivo" | 6 % de la CU de producción, facturada a la capacidad equivocada |

> "Nobody lied to the steering committee. We reported what was easy to count: things migrated, things created, people licensed. We never reported what was *used*. Inventory metrics feel like adoption. They're not."

**Slide 16 — El KPI que lo habría contado todo:**

> **Cost per monthly active user: $11.8 → $21.0 (+78 %)**

> "If the committee had seen one number every month, it should have been this one."

---

## 27:00–35:00 · Bloque 3 — La instrumentación

### Slide 17 — Cuatro señales, una pregunta cada una (1')

| Señal | Pregunta | Herramienta principal hoy |
|---|---|---|
| **CU metrics** | ¿Qué consume y cuándo? | Capacity Metrics app (Health, Compute, Item details, Timepoint) |
| **Linaje** | ¿Qué depende de qué y qué se puede apagar? | Lineage view, Scanner API, Purview hub |
| **Propiedad** | ¿Quién responde por esto? | Scanner API (roles), Govern → My items, dominios y etiquetas |
| **Actividad** | ¿Lo usa alguien? | Activity events, Unused artifacts API, Govern, FUAM |

> "Each signal answers one question. The trick is that you need all four together. CU without activity tells you what's expensive, not what's useless. Activity without lineage tells you what's unused, not what's safe to delete."

### Slide 18 — El *toolbox* actual en una slide (2')

Tres columnas, con el detalle en el handout y en el *Anexo A*:

- **Ver** (observabilidad): Metrics app GA + nueva experiencia (preview) · Chargeback app (GA) · OneLake catalog Govern (GA) · Monitor hub renovado + *Capacity Insights & Actions* (preview) · workspace monitoring unificado en un Eventhouse (preview) · Capacity events en el Real-Time hub (overview GA, operation events preview) · Azure Cost Management.
- **Contener** (controles): Surge protection de background (GA) y por workspace (anunciada GA) · Capacity overage (GA, 3× PAYG, umbral de 24 h *que no es un tope duro*) · On-demand billing para Spark (GA) · on-demand en todas las cargas + **F0** (anunciados, preview "en semanas") · Fabric Copilot capacity · pausa/escalado programado · Policies in Fabric (preview).
- **Conservar la historia** (aceleradores no oficiales): **FUAM** y **Fabric Cost Analysis (FCA)** en `microsoft/fabric-toolbox` · Semantic Link Labs.

> "Two things changed this autumn. Overage became GA and is on by default when you create a capacity, so check yours. And on-demand billing is coming for everything, with F0 as a zero-provisioned starting point. Both are good news, and both make the bill *more* elastic, which means the case you just saw gets *easier* to repeat, not harder."

### Clip 4 — Chargeback app + Govern (28:30–31:00, 90 s)

1. **Chargeback app:** % de capacidad por **dominio** → enseñar el cubo **"No domain"**. *"In our case it was thirty-eight percent of the capacity. You can't charge back to 'No domain'."* Profundizar en un workspace → item → usuarios.
2. **OneLake catalog → Govern → All data in Fabric:** *Governance insights* (inventario, cobertura de etiquetas, descripción y certificación, frescura) y **Recommended actions**. Cambiar al filtro por dominio.
3. **Govern → My items:** la vista del dueño. *"This is the view you send every owner once a quarter: 'here's what you own, confirm or kill'."*

> "The Feature usage and adoption report in the admin monitoring workspace is frozen: it won't get new data. Microsoft points you to Govern instead. If your adoption dashboard is built on it, migrate it."

### Clip 5 — Señal en tiempo real + historia larga (31:00–33:00, 90 s)

1. Real-Time hub → **Capacity overview events** → Eventstream → **Activator**: alerta al 80 % del uso suavizado y otra cuando cambia el estado de la capacidad (pausa o reanudación). *"This is the alert that would have fired in month two, not month three."*
2. Monitor hub → **Capacity Insights & Actions** (preview): margen de capacidad junto al estado de los jobs, con ajustes de surge y overage o el movimiento de un workspace desde la misma pantalla.
3. **FUAM** (lakehouse + informes): inventario y actividad **con más de 30 días de historia**. *"The admin APIs forget. FUAM remembers. Without history, you can't do an autopsy."*

### Slide 19 — Cuántos meses antes (1,5')

| Problema | Apareció en la factura | Señal disponible | Herramienta |
|---|---|---|---|
| Contenido muerto migrado | Nunca (estaba en la reserva) | **M−1** | Activity events + Unused artifacts |
| Dispersión de workspaces | Nunca, directamente | **M1** | Govern (inventario, % sin dominio) |
| Copias y refrescos | M3, como F16 | **M2** | Metrics app Compute (top items, heatmap) |
| Throttling en el cierre | M3, como F16 + overage | **M2** (p95) | Health (% en throttling) + Activator |
| Pilotos eternos | M6 | **M4** | Item details + etiquetas de caducidad |
| Huérfanos | M5 (fallos) | **M1** | Scanner API (roles) |

> "On average, the signal was there four months before anyone linked it to cost. Four months of a capacity at three times the waste it needed."

### Slide 20 — Cuidado: instrumentar también cuesta (1')

- Workspace monitoring y FUAM **consumen CU y almacenamiento**. Microsoft recomienda consolidar en pocos Eventhouses, en una capacidad dedicada. Una F4 o F8 dedicada a monitorización es un patrón habitual.
- **Workspace monitoring no rellena el histórico.** Actívalo antes de necesitarlo.
- La Chargeback app sin el setting *Show user data* agrupa a todos los usuarios como *Masked user*.

> "Monitoring is a workload. Budget it like one, or it becomes the next line on the bill."

---

## 35:00–42:00 · Bloque 4 — Las cuatro decisiones

**Slide 21 — Las cuatro, en una slide.** Después, una slide por decisión, con la misma plantilla: *Lo que decidimos · La alternativa · Lo que habría cambiado*.

### Decisión 1 — Dimensionar por licencia, no por carga (1,5')

**Lo que decidimos.** "F64 porque equivale a nuestro P1". Una sola capacidad para ETL, BI, pilotos y aprendizaje.

**La alternativa.**
- Dimensionar con una semana de carga medida en la F64 de prueba, no con una tabla de equivalencias.
- **Aislar sin multiplicar capacidades:** surge protection por workspace con un límite por defecto, Finanzas y los informes de dirección como *Mission critical*, y los pilotos con un límite bajo.
- Spark con **on-demand billing** fuera de la capacidad compartida y con un límite de gasto.
- Pilotos y formación en una **capacidad pequeña que se pausa** (o en F0 cuando esté disponible), nunca en producción.

**Lo que habría cambiado.** No habría habido throttling en el cierre → **no habría F16 "temporal" (−2.102 $/mes) ni overage (−121 $)**.

> "Licence equivalence is a procurement answer to an engineering question."

### Decisión 2 — Migrar a los muertos (1,5')

**Lo que decidimos.** Migrarlo todo "para no romper nada".

**La alternativa.** **Censo previo con 90 días de actividad.** Lo que no se usó se archiva (por ejemplo, en un export a OneLake o el PBIX en Git) y se anuncia con una fecha: *"si lo necesitas, pídelo antes del día X"*.

**Lo que habría cambiado.** 81 informes y **19 de los 49 workspaces inactivos no habrían llegado a nacer en Fabric**, ni sus refrescos programados.

> "A migration is the only moment in the life of a BI estate when deleting is free. Nobody complains about what doesn't arrive."

### Decisión 3 — Workspaces sin contrato (2')

**Lo que decidimos.** Crear workspaces se abrió a 380 personas sin condiciones.

**La alternativa: el workspace como contrato.** Ningún workspace existe sin:
1. **Dos dueños** con nombre (nunca uno solo y nunca una cuenta externa).
2. **Dominio**, asignado por defecto según el grupo de seguridad del creador.
3. **Centro de coste** como etiqueta.
4. **Fecha de caducidad** para sandboxes y pilotos (90 días renovables).
5. **Recertificación trimestral** vía Govern → *My items*: confirmar o retirar.

Con qué se implementa hoy: restringir *Create workspaces* a grupos · solicitud con aprobación (por ejemplo, un formulario + Power Automate + la API de Fabric) · *default domain* · etiquetas · **Policies in Fabric** (preview) para limitar qué items se crean y en qué capacidad.

**Lo que habría cambiado.** 26 workspaces ad hoc inactivos y el **38 % de CU en "No domain"** → con dominios, el chargeback habría sido posible desde el primer mes.

> "Self-service without a contract isn't empowerment. It's deferred cleanup."

### Decisión 4 — Un coste sin dueño (2')

**Lo que decidimos.** La capacidad era una línea fija de IT, reservada. Nadie de negocio veía su consumo.

**La alternativa.**
- **Showback por dominio desde el mes 1** con la Chargeback app. Sin cobrar, solo enseñar: *"Ventas usó el 34 % de la capacidad este mes"*.
- **Revisión mensual de capacidad**, de 30 minutos, con cinco lecturas (Health, Compute top items, Chargeback por dominio, Azure Cost Management por medidor y Govern) y una página de decisiones.
- **Cuatro KPIs de telemetría para el comité**, en lugar de métricas de inventario:
  1. Usuarios activos al mes y su tendencia.
  2. **Coste por usuario activo.**
  3. **% de CU en items con 0 usuarios en 30 días.**
  4. % del tiempo en throttling (p95, no la media).

**Lo que habría cambiado.** La señal habría llegado en el **M2**, no en el M6.

> "Costs that belong to everyone are paid by no one, until the invoice arrives and they belong to the CIO."

### Slide 22 — El contrafactual (1')

| | Real M6 | Con las 4 decisiones (estimación) |
|---|---|---|
| Factura mensual | 8.607 $ | ≈5.800–6.300 $ (sin F16, sin overage, dev pausado, menos almacenamiento duplicado) |
| Workspaces | 147 (49 inactivos) | ≈90–100, todos con dueño y dominio |
| CU para nadie | 31 % | <10 % |
| Coste por usuario activo | 21,0 $ | ≈14–15 $ |

> "I'm giving you a range, not a number, because a counterfactual is an estimate. But even the pessimistic end is below the original budget."

*(Si te preguntan por el cálculo, está en el Anexo C. Pausar dev 60 h a la semana ahorra ≈676 $/mes por sí solo.)*

---

## 42:00–45:00 · Cierre

### Slide 23 — El kit del día 1 (antes del go-live, no después) (1,5')

1. Censo de actividad de 90 días → **no migrar lo muerto**.
2. Metrics app + Chargeback app instaladas **y una persona con nombre que las revisa cada semana**.
3. Alerta de Activator sobre los capacity events (80 % de uso suavizado y cambios de estado).
4. Surge protection por workspace, con la lista *Mission critical* decidida por negocio.
5. Overage **revisado** (viene activado por defecto) con un umbral consciente.
6. *Create workspaces* restringido y el contrato del workspace publicado.
7. *Default domain* por grupo y etiquetas de centro de coste.
8. Copilot y data agents en una **Fabric Copilot capacity**.
9. Pausa programada de dev/test y etiquetas de Azure con caducidad.
10. FUAM (o equivalente) recogiendo historia **desde el día 0**.

### Slide 24 — La frase para el comité (0,5')

> **"We didn't have a capacity problem. We had decisions that nobody linked to cost, and a reservation that hid them for five months."**

### Slide 25 — Gracias + QR (1')

> "The day-one kit, the tool catalogue and the queries are in the repo; the moderator will paste the link in the chat. The architecture diagram had no box for the organisation. The invoice did. Thank you. Let's take your questions live."

---

## 45:00–60:00 · Q&A en directo

Contesta en 30–60 segundos cada una.

| Pregunta | Respuesta corta |
|---|---|
| *"¿Existían estas herramientas cuando pasó?"* | Algunas no: la nueva Metrics app, el Govern en GA, la surge protection por workspace y el overage en GA son de 2026. Pero el registro de actividad, la Scanner API, la Metrics app y los presupuestos de Azure sí existían. Las señales básicas estaban; nadie las miraba. |
| *"¿Reservar o PAYG?"* | Reservar a partir de una utilización sostenida alta (en torno al 75 %, con un descuento de ~41 %). Pero la reserva **oculta el crecimiento**: si reservas, la revisión mensual de consumo es obligatoria. |
| *"¿Overage sí o no?"* | Sí en producción, como seguro, **con un umbral consciente**: es un umbral de gasto, no un tope duro, y se cobra a 3× PAYG. Si salta todos los meses, no es un seguro: es que la capacidad se te ha quedado pequeña. Ojo: bajar de SKU con el overage activado puede generar cargos importantes. |
| *"¿Una capacidad o varias?"* | Menos de las que crees, si usas surge protection por workspace y on-demand para Spark. Al menos separa lo que se pausa (dev, pilotos y formación) de lo que no. |
| *"¿Cómo borro 49 workspaces sin que nadie se queje?"* | No los borres: anúncialo. Avisa a los dueños vía *My items*, retira el acceso y espera 30 días, y después elimina (la retención de workspaces eliminados te da red). Usa el linaje para comprobar que nada depende de ellos. |
| *"¿FUAM o lo nativo?"* | Lo nativo para operar el día a día. FUAM (o FCA para costes) para **conservar la historia** y cruzar datos. No es un producto soportado: trátalo como código propio. |
| *"¿Y con F0 y on-demand para todo, esto deja de pasar?"* | Pasa más rápido. Lo elástico elimina el throttling, que era tu única alarma. Sin límites de gasto ni revisión, la factura crece sin que nadie note nada. |
| *"¿El chargeback real no genera guerra entre departamentos?"* | Por eso se empieza con *showback*. Enseñar el consumo ya cambia comportamientos; cobrar es una decisión posterior de finanzas. |
| *"¿Cuánto cuesta instrumentar?"* | Poco frente a lo que ahorra, pero no es cero: una capacidad pequeña dedicada a la monitorización es un buen patrón. Workspace monitoring y FUAM consumen CU. |
| *"¿Qué haría el primer lunes?"* | Abrir la Chargeback app, mirar el cubo "No domain" y la lista de items con 0 usuarios en 30 días. En una hora sabrás si esta sesión iba de ti. |

---

## Preparación de los clips (tenant FraSoHome)

| Clip | Qué necesita existir | Cómo sembrarlo |
|---|---|---|
| 1 · Compute + heatmap | 3–4 copias de un modelo import con refrescos programados a horas fijas, 14 días de historia | Clonar el modelo de Ventas del caso (`fact_transacciones`, `productos`, `tiendas`) y programar refrescos 6:00/9:00/12:00/15:00 |
| 2 · Health + Activator | Algún episodio de throttling en una F2/F4 de demo | Notebook de carga pesada + varias recargas completas de un Dataflow Gen2 a la misma hora; regla de Activator con plantilla |
| 3 · (opcional) Spark ocioso | Notebook con *Run all* sin parar sesión, frente al mismo notebook orquestado con pipeline | Dos ejecuciones comparadas en *Item details* |
| 4 · Chargeback + Govern | Dominios del caso, algunos workspaces sin dominio, items sin descripción ni etiqueta | 6–8 workspaces: 3 con dominio, 3 sin dominio, 2 "Curso_*" vacíos |
| 5 · Capacity events + FUAM | Stream de capacity events y FUAM desplegado con ≥2 semanas de datos | Desplegar FUAM desde `fabric-toolbox` en un workspace de monitorización |

> Los scripts para sembrar el tenant van en `C:\dev\power-bi-fabric-summit\2027\` (no en este repositorio).

## Recortes si te pasas de tiempo

- **−1,5'**: M4 se reduce a una slide con los tres pilotos, sin el caso FourMoo.
- **−1'**: quitar la slide 20 (instrumentar cuesta) y pasarla al Q&A.
- **−1'**: el clip 5 se queda solo con Activator, sin FUAM.
- **Nunca recortar**: la apertura, la frase "40 % vs 112 %", la tabla del comité frente a la telemetría, las cuatro decisiones y el kit del día 1.

---

## Anexo A — Catálogo de opciones y herramientas (estado a 21 oct 2026)

### A.1 · Coste y capacidad (nativo)

| Herramienta / opción | Estado | Qué responde o controla | Límites y avisos |
|---|---|---|---|
| **Capacity Metrics app** (experiencia actual) | GA | Uso por item y operación, throttling, *Timepoint summary/detail* (hasta el usuario y el ID de operación), almacenamiento | Hay que instalarla; se basa en ventanas de 14 días |
| **Metrics app — nueva experiencia** | Preview (oct. 2026) | *Health* (% de tiempo en throttling, comparable entre capacidades), *Compute* (CU-segundos, heatmap horario, top items), *Item details* (14 días, por usuario), *Storage* | Despliegue regional progresivo |
| **Chargeback app** | GA | % de capacidad por workspace, item, **dominio/subdominio** y usuario; exportación | Refresco diario; los service principals aparecen como "Power BI Service"; *Masked user* si el setting de datos de usuario está desactivado |
| **Capacity overage** | GA (29 sep 2026) | Evita throttling cobrando el exceso | **3× la tarifa PAYG** en un medidor aparte; **activado por defecto** al crear la capacidad; umbral de 24 h móvil que **no es un tope duro**; no da más rendimiento ni limpia la deuda futura; solo para F SKU; bajar de SKU con el overage activado puede salir caro |
| **Surge protection — background** | GA | Rechaza background por encima de un umbral para proteger el interactivo | No detiene los jobs en curso; algunas peticiones de la UI cuentan como background |
| **Surge protection — por workspace** | Preview → "GA soon" (FabCon EU 2026) | Límite de CU por workspace (% de capacidad en 24 h); estados *Available / Mission critical / Blocked* | No limita por usuario ni por item: "más bulldozer que pala de jardín" |
| **On-demand billing para Spark** (antes *Autoscale Billing*) | GA | Spark fuera de la capacidad compartida, pago por uso, con límite máximo de CU | Sin suavizado; cambiar el límite cancela los jobs en curso |
| **On-demand billing para todas las cargas + F0** | Anunciado, preview "en semanas" | Mover categorías de facturación fuera de la capacidad; F0 sin coste provisionado | Multiplicadores y precio de F0 **no publicados**; límite de gasto en una ventana de 24 h |
| **Capacity events (Real-Time hub)** | Overview GA · operation events preview | Eventos cada 30 s (resumen) y de cambio de estado → Eventstream → Activator | Requiere permisos de capacidad; cuidado con OAP y Private Link |
| **Plantillas de alertas de capacidad** | GA | Alertas listas para usar | — |
| **Monitor hub renovado + Capacity Insights & Actions** | Preview | Margen de capacidad junto a los jobs; ajustar surge y overage, mover workspaces o redimensionar desde el hub | — |
| **Fabric Copilot capacity** | Disponible | Factura en una capacidad designada el uso de Copilot y data agents de un grupo de usuarios | Solo en la región *home*; mínimo F2/P1; un usuario solo puede estar en una; no cubre AI functions |
| **Pausa, reanudación y escalado** | GA | Detener o ajustar el cómputo (portal de Azure, API, Azure Automation) | **El almacenamiento sigue facturando**; con la capacidad en pausa, OneLake rechaza transacciones |
| **Reservas F SKU** | GA | ~41 % de descuento a 1 o 3 años | El overage no se beneficia de la reserva; **la reserva oculta el crecimiento del consumo** |
| **Azure Cost Management** | GA | Presupuestos, alertas, desglose por medidor (capacidad, overage, almacenamiento, on-demand) y etiquetas | Usa etiquetas obligatorias con Azure Policy (dueño, centro de coste, caducidad) |
| **OneLake: facturación de almacenamiento** | GA | Pago por GB prorrateado; soft delete de 7 días facturado; con un *shortcut*, el cómputo lo paga la capacidad que consume y el almacenamiento, la dueña | El almacenamiento duplicado (copias en lugar de shortcuts) es crecimiento silencioso |
| **Controles Spark** | GA | *Timeout* de sesión, alta concurrencia, starter pools frente a custom pools, **Custom Live Pools** (GA, preencendidos según horario) | Los live pools cuestan mientras están encendidos |
| **Custom SQL pools (Warehouse)** | GA | Aislar el cómputo del warehouse por porcentajes | — |

### A.2 · Adopción, inventario y propiedad (nativo)

| Herramienta | Estado | Qué responde | Límites |
|---|---|---|---|
| **OneLake catalog → Govern** | GA | Insights del inventario, dominios y capacidades, cobertura de etiquetas, descripción y certificación, frescura, compartición; **acciones recomendadas**; vista *My items* para dueños | Refresco diario (vista admin); no muestra subitems; no disponible con Private Link |
| **Feature usage and adoption report** (Admin monitoring workspace) | Preview **congelada** | Actividad de 30 días e inventario activo/inactivo | **No recibirá datos nuevos**: Microsoft recomienda Govern |
| **Activity events (API de admin)** | GA | Quién hizo qué, dónde y cuándo | Ventana corta: hay que extraer a diario para tener historia |
| **Unused artifacts API** | Preview | Modelos, informes y paneles sin uso en 30 días por workspace | Solo esos tres tipos de item |
| **Scanner API (metadata scanning)** | GA | Workspaces, items, usuarios y roles, fuentes, linaje | Base para detectar huérfanos y cuentas externas como dueñas |
| **Lineage view / análisis de impacto** | GA | Qué se rompe si apago esto | — |
| **Purview hub en Fabric** | GA | Visión de etiquetas, certificación y gobierno | — |
| **Dominios y subdominios** | GA | Agrupación por negocio; *default domain* por grupo de seguridad; delegación | Sin asignación por defecto, la dispersión no tendrá dominio |
| **Etiquetas (tags)** | GA | Centro de coste, entorno, caducidad; filtros en el OneLake catalog | — |
| **Workspace monitoring** (unificado en Eventhouse) | Preview | Telemetría detallada en KQL (queries, pipelines, Copy job, modelos semánticos…) | **Consume CU**; **no rellena el histórico**; un solo Monitoring Item por workspace; retención de 30 días por defecto |
| **Tenant setting *Create workspaces*** | GA | Restringir quién puede crear workspaces | — |
| **Policies in Fabric** | Preview | Controles por atributos: *Item creation* (ámbito de capacidad), *Edit workspace settings*, *External data sharing* | Revisar el estado antes de grabar (ver también la sesión del Christmas Power Data Platform) |
| **Branch workspace admin profile** | Preview | Los desarrolladores crean workspaces de rama sin permisos de creación ni de asignación de capacidad | Útil para que Git no genere dispersión |
| **Fabric Core MCP Server** | GA | Agentes que gestionan workspaces, items y permisos con RBAC y auditoría | Útil para automatizar la recertificación |

### A.3 · Aceleradores no oficiales

| Herramienta | Qué es | Avisos |
|---|---|---|
| **FUAM** (`microsoft/fabric-toolbox`) | Lakehouse + pipelines + informes con inventario, actividad y métricas de capacidad e histórico ilimitado | Sin soporte oficial; consume CU y almacenamiento; contiene telemetría sensible |
| **Fabric Cost Analysis (FCA)** (`fabric-toolbox`) | Análisis de costes de Fabric construido en Fabric, con data agent | Sin soporte oficial |
| **Semantic Link Labs** | Librería Python: funciones de admin, Best Practice Analyzer, VertiPaq Analyzer, utilidades de capacidad | Para automatizar auditorías desde notebooks |

---

## Anexo B — Casos públicos citados

| Caso | Qué enseña | Fuente |
|---|---|---|
| Sam Debruyn, *Lessons from Migrating to Fabric* (Fabric February, Oslo, feb. 2026) | Una consulta larga lanzada un viernes en una F4: ráfaga de 32 CU sobre 4 de base y un overage estimado en ≈413 € a PAYG; pausar y reanudar no canceló la consulta. La identidad de ejecución es la del último que modificó el item | https://debruyn.dev/speaking/fabric-february-2026/ |
| FourMoo, sesiones de notebook | 1.320 s de CU con la sesión ociosa frente a 67 s parándola (−95 %) | https://www.fourmoo.com/2024/01/10/microsoft-fabric-notebook-session-usage-explained-and-how-to-save-cus-or-billed-time/ |
| Microsoft Learn, *Capacity overage* | Umbral que no es tope duro; bajar de SKU con el overage activado puede generar cargos importantes | https://learn.microsoft.com/fabric/enterprise/capacity-overage-overview |

## Anexo C — Cálculos del caso (para recalcular si cambias los datos)

- Precio de lista: **0,18 $/CU-hora PAYG**; 730 h/mes.
- F8 PAYG = 8 × 0,18 × 730 = **1.051,20 $** · F16 PAYG = **2.102,40 $** · F64 reservada = **5.002,67 $**.
- OneLake: 4 TB × 1.024 × 0,023 = **94,21 $**; 14 TB = **329,73 $**.
- Overage: 224 CU-h × 0,18 × 3 = **120,96 $**.
- M0 = 6.148,08 $ · M6 = 8.606,96 $ → **+40,0 %**.
- Capacidad F64 = 64 × 730 = 46.720 CU-h/mes. Utilización 41 % → 19.155 CU-h; 63 % → 29.434; 87 % → 40.646 (**+112 %** entre M0 y M6).
- CU para nadie = 27 % × 9/14 + 8 % + 6 % (prototipo de stock) = **31,4 %** ≈ 12.750 CU-h/mes.
- Coste por usuario activo: 6.148 / 520 = **11,8 $** → 8.607 / 410 = **21,0 $** (+78 %).
- Pausar dev 60 h/semana: 1.051,20 × 60/168 = 375,43 $ → ahorro de **675,77 $/mes**.
- Contrafactual: 8.607 − 2.102 (F16) − 121 (overage) − 676 (dev pausado) − ~150 (almacenamiento duplicado) ≈ **5.560 $**. En la slide se presenta un rango conservador de 5.800–6.300 $ porque Spark on-demand y una capacidad pequeña para pilotos añaden coste.

## Anexo D — Por verificar antes de grabar (enero 2027)

- [ ] **Surge protection por workspace**: ¿ya en GA? ¿Se gestiona desde el OneLake catalog / Monitor hub, como se anunció?
- [ ] **On-demand billing para todas las cargas y F0**: ¿en preview? ¿Se han publicado los multiplicadores y el precio?
- [ ] **Overage activado por defecto**: Learn dice que sí al crear la capacidad, pero hay fuentes que dicen *opt-in*. Comprobarlo en una capacidad nueva.
- [ ] **Nueva Metrics app**: ¿sigue en preview? ¿Han cambiado los nombres de las páginas?
- [ ] **Capacity Insights & Actions** y **workspace monitoring unificado**: estado.
- [ ] **Policies in Fabric**: tipos de política disponibles.
- [ ] Precios de lista F SKU vigentes (y en la región del caso si mencionas euros).
- [ ] Ventana de retención actual de la API de *Activity events*.

## Referencias para las notas del orador

- Evento: https://sessionize.com/power-bi-fabric-summit-2027/
- Nueva experiencia de la Capacity Metrics app (preview): https://community.fabric.microsoft.com/blog/fbc_fabricupdatesblogs/a-new-look-and-new-capabilities-in-the-capacity-metrics-app-preview/5374114
- Health, Timepoint y Chargeback en GA: https://community.fabric.microsoft.com/t5/Fabric-Updates-Blog/Providing-more-insights-amp-tools-Capacity-health-timepoint/ba-p/5176753
- Chargeback app: https://learn.microsoft.com/fabric/enterprise/chargeback-app
- Capacity overage: https://learn.microsoft.com/fabric/enterprise/capacity-overage-overview
- Overage + surge protection (patrón combinado): https://actionablereporting.com/2026/03/24/microsoft-fabric-why-you-should-enable-capacity-overage-and-how-to-combine-it-with-surge-protection/
- Anuncios de FabCon Europe 2026 (governance, monitoring, billing): https://community.fabric.microsoft.com/blog/fbc_fabricupdatesblogs/build-deploy-and-govern-microsoft-fabric-at-scale/5369145
- Resumen de capacidad y coste de FabCon EU 2026: https://solv-systems.com/resources/fabcon-europe-2026-recap
- F0 y on-demand billing: https://solv-systems.com/resources/fabric-f0-on-demand-billing
- Observabilidad y workspace monitoring: https://solv-systems.com/resources/fabric-workspace-monitoring-observability
- Fabric September 2026 Feature Summary (Policies in Fabric, capacity events): https://community.fabric.microsoft.com/blog/fbc_fabricupdatesblogs/fabric-september-2026-feature-summary/5325825
- OneLake catalog Govern: https://learn.microsoft.com/fabric/governance/onelake-catalog-govern
- Feature usage and adoption (congelado): https://learn.microsoft.com/fabric/admin/feature-usage-adoption
- Unused artifacts API: https://community.fabric.microsoft.com/t5/Power-BI-Updates-Blog/Power-BI-Unused-Artifacts-API-preview/ba-p/5175325
- Capacity events en el Real-Time hub: https://learn.microsoft.com/fabric/real-time-hub/create-streams-fabric-capacity-overview-events
- Fabric Copilot capacity: https://learn.microsoft.com/fabric/enterprise/fabric-copilot-capacity
- Consumo de OneLake (shortcuts, pausa, soft delete): https://learn.microsoft.com/fabric/onelake/onelake-capacity-consumption
- On-demand billing para Spark: https://learn.microsoft.com/fabric/data-engineering/autoscale-billing-for-spark-overview
- Surge protection por workspace, visión crítica: https://redmondmag.com/articles/2026/08/26/how-to-keep-microsoft-fabric-workloads-from-overwhelming-capacity.aspx
- FUAM, costes y límites: https://telefonicatech.uk/blog/fabric-unified-admin-monitoring-part3/
- Fabric Cost Analysis: https://blog.crossjoin.co.uk/2025/10/19/monitor-fabric-costs-with-fabric-cost-analysis
- FinOps operativo mensual (sirve para contrastar, es contenido de proveedor): https://www.epcgroup.net/blog/microsoft-fabric-capacity-finops-monthly-operating-model-cu-hours-overage-surge-protection-october-2026
