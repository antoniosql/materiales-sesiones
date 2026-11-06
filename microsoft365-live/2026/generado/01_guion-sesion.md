# Semantic Debt: why Copilot answers questions nobody asked — Guion

| | |
|---|---|
| Evento | Microsoft 365 Live 2026 · online por Teams |
| Duración | 60 min con Q&A dentro (52' de contenido + 8' de preguntas) |
| Idioma | Español |
| Escenario | FraSoHome — tenant `frasohome.onmicrosoft.com` |
| Persona que pregunta en las demos | **Laura P.**, directora comercial (licencia M365 Copilot, grupo *Comercial*) |
| Slides | ≈22 |

## La tesis en una frase

> **"Copilot no falla por el modelo. Responde con total seguridad a la interpretación que encuentra, porque tu organización nunca acordó cuál era la buena."**

## Los tres mensajes que tienen que sobrevivir a la sesión

1. **La deuda semántica es anterior a la IA. La IA la cobra con intereses**: actúa de amplificador.
2. **Se diagnostica empezando por las preguntas, no por los repositorios.** Son cuatro pasos y una métrica.
3. **Las herramientas pagan los intereses. El principal se paga con decisiones y con dueños.** Por eso la próxima licencia no lo arregla.

## Escaleta

| Min | Bloque | Qué pasa | Demo |
|---|---|---|---|
| 00:00–03:00 | Apertura | La respuesta perfecta… que está mal | **Demo 0** (Copilot Chat) |
| 03:00–05:00 | Quién soy + promesa | Lo que te llevas · lanzar la encuesta | — |
| 05:00–13:00 | 1 · Qué es la deuda semántica | Cuatro formas, treinta años y por qué la IA no la perdona | — |
| 13:00–29:00 | 2 · Cómo aflora en M365 | Cuatro síntomas en el tenant de FraSoHome | **Demos 1, 2 y 3** |
| 29:00–38:00 | 3 · Diagnóstico en 4 pasos | Preguntar → Rastrear → Recuperar → Asignar | — |
| 38:00–41:00 | 4 · Señales de alerta | Ocho señales para contar en el chat | — |
| 41:00–50:00 | 5 · Qué se puede arreglar | Term store, Copilot Studio, Purview, Work IQ (+ Fabric IQ) | **Demo 4** ("después") |
| 50:00–53:00 | 6 · El argumento | Por qué la próxima licencia no lo arregla | — |
| 53:00–60:00 | Q&A | Preguntas del chat | — |

**Puntos de control del reloj.** En el 13:00 tienes que estar abriendo SharePoint. En el 29:00, en la slide del diagnóstico. En el 41:00, en la del term store. Si en el 29:00 vas tarde, recorta el síntoma 4 a solo las cifras y la slide del glosario, sin la parte del procedimiento tácito (ver *Recortes*).

---

## Antes de entrar (online)

- [ ] **Dos perfiles de navegador.** *Laura P.* (Copilot Chat, Copilot Studio en modo prueba y SharePoint) y *admin* (Purview y SharePoint Admin). Nunca hagas las demos como admin: el admin ve más cosas que Laura y la demo deja de ser verdad.
- [ ] **Pre-run 30 minutos antes** de las preguntas de las demos 0–4. Copilot no es determinista. Si una respuesta sale distinta a la del guion, apúntalo: lo vas a usar (ver *Plan B*).
- [ ] **Vídeo de respaldo de cada demo** (≤90 s cada uno), abierto en una pestaña.
- [ ] **Encuesta de Teams/Forms** preparada: *"¿Cuántas definiciones de 'cliente' conviven en tu organización?"* → 1 · 2 · 3 · 4 o más · No lo sé.
- [ ] **Moderador**: acordar que te lea preguntas del chat en el **13:00** (una) y en el **53:00** (todas).
- [ ] Teams: compartir **ventana**, no pantalla. Notificaciones desactivadas. Zoom del navegador al 125 %.

---

## 00:00–03:00 · Apertura: la respuesta perfecta (Demo 0)

**Pantalla:** Copilot Chat ya abierto como Laura. No hay slide de título; el título se enseña después.

> "Hola a todos y gracias por estar aquí. Antes de presentarme os voy a enseñar la mejor respuesta de Copilot que he visto este año."

**Prompt (pegar):**

```
¿Cuántos clientes activos tenía FraSoHome al cierre de 2025 y cómo evolucionaron las ventas netas en el cuarto trimestre respecto al tercero?
```

**Respuesta esperada:** cita `Informe_Comercial_Q4_2025_FINAL.pptx` y dice algo como *"FraSoHome cerró 2025 con 49 clientes activos… las ventas netas del Q4 descendieron un 2,6 % respecto al Q3…"*, con viñetas y tono de consultora.

> "Tiene cifras, cita la fuente y suena a consultora. Si yo fuera Laura, la directora comercial, esto lo pego mañana en el comité."
>
> *(pausa)*
>
> "Las dos cifras están mal. Bueno, no exactamente: son correctas, pero para una pregunta que nadie ha hecho."

**Slide 2 — "La pregunta que hiciste / la pregunta que respondió"**

| Lo que preguntó Laura | Lo que respondió Copilot | Lo oficial (FS-KB-03) |
|---|---|---|
| ¿Cuántos clientes activos? | ¿Cuántos socios del programa siguen sin darse de baja, según el PowerPoint de marketing? → **49** | Clientes con ≥1 compra en los últimos 12 meses → **100** |
| ¿Cómo evolucionan las ventas netas? | ¿Cuánto se facturó en pedidos captados, sin restar devoluciones ni cancelaciones? → **−2,6 %** | Ventas netas de devoluciones y sin cancelados → **+2,5 %** |

> "Ha cambiado hasta el signo. La empresa crece, y Copilot le ha dicho a la directora comercial que cae."

**Slide 3 — Título:** *Semantic Debt: why Copilot answers questions nobody asked.*

---

## 03:00–05:00 · Quién soy y qué te llevas

> "Soy Antonio Soto, MVP en Fabric y Foundry. Llevo más de veinticinco años en proyectos de datos en empresa y doy clase en universidades y escuelas de negocio. Este problema lo he visto en todos los proyectos de BI que he hecho, mucho antes de que existiera Copilot. La diferencia es que ahora el problema habla, y habla muy bien."

**Slide 4 — Lo que te llevas**

1. Un **diagnóstico en cuatro pasos** que puedes empezar el lunes.
2. **Ocho señales de alerta** que aparecen *antes* de desplegar.
3. **Un argumento** para explicar dentro de tu empresa por qué la próxima licencia no va a arreglar esto.

> "Y una cosa más: todo lo que vais a ver es FraSoHome, una empresa ficticia de muebles y decoración. Los datos son inventados, pero los problemas los he visto en clientes reales."

**→ Lanzar la encuesta** ("¿Cuántas definiciones de 'cliente' conviven en tu organización?"). Los resultados se comentan en el minuto 12.

---

## 05:00–13:00 · Bloque 1 — Qué es la deuda semántica

### Slide 5 — De la deuda técnica a la deuda semántica (2')

> "En 1992 Ward Cunningham acuñó la *deuda técnica*: los atajos que tomas hoy en el código y que pagas mañana en mantenimiento. Yo propongo su prima, que es más antigua y más cara: la **deuda semántica**."

**Definición (en la slide, grande):**

> **Deuda semántica:** el coste acumulado de no haber acordado, escrito y dado dueño al *significado* de lo que la organización sabe.

> "La deuda técnica la paga el equipo de desarrollo. La semántica la paga cada persona que tiene que interpretar, cada vez que interpreta. Hasta ahora esa persona era humana."

### Slide 6 — Las cuatro formas (2')

| Forma | Cómo suena en un pasillo | En FraSoHome |
|---|---|---|
| **De definición** | "Depende de lo que entiendas por cliente" | Seis cifras de "cliente activo" |
| **De versión** | "¿Cuál es el bueno?" | Cuatro cálculos de ventas netas; dos plazos de devolución |
| **Tácita** | "Eso pregúntaselo a Lucía" | Devolución en tienda de un pedido online pagado con puntos |
| **De gobierno** | "Esa etiqueta la puso alguien en 2024" | El diccionario oficial de KPI, cifrado para quien lo necesita |

> "Las tres primeras afectan al contenido. La cuarta es la deuda del metadato: etiquetas, permisos y dueños que nadie mantiene. Es la más traicionera, porque esconde las otras tres."

### Slide 7 — Treinta años aplazando la factura (1,5')

Línea temporal: `\\servidor\comercial\Varios` (años 90) → intranet → SharePoint 2007/2010 → migración *lift & shift* a SharePoint Online → explosión de Teams en 2020 → Copilot.

> "En cada migración movimos los ficheros y nunca movimos los acuerdos. Hemos migrado la deuda cinco veces y no la hemos refinanciado ninguna."

### Slide 8 — Por qué la IA no la perdona: el humano era el amortiguador (2')

> "Hasta ahora Laura sabía que el PowerPoint de marketing infla, y sabía a quién llamar para pedir la cifra buena. Saber de qué fuente fiarse era también conocimiento tácito. Copilot no tiene ese conocimiento."

**Diagrama de la cadena:**

`Pregunta → Recuperación (lo más parecido) → Modelo (lo más fluido) → Respuesta (lo más convincente)`

> "En ningún eslabón de esta cadena se optimiza lo *oficial*. Copilot no sabe cuál es el documento oficial: sabe cuál se parece más a tu pregunta. Y el PowerPoint de marketing se parece muchísimo a la pregunta de Laura, porque está escrito precisamente para el comité."

### Slide 9 — Tres efectos de amplificación (0,5' + encuesta)

1. **Fluidez ≠ corrección.** Una respuesta bien redactada nos hace bajar la guardia.
2. **Escala.** El error que antes vivía en un Excel ahora se repite en cientos de chats al día.
3. **Silencio.** Copilot no te avisa de que hay cuatro definiciones: escoge una y responde. *Eso es responder a una pregunta que nadie hizo.*

**→ Resultados de la encuesta.** Comentar en una frase el porcentaje de "4 o más" + "No lo sé":

> "Los que habéis contestado 'no lo sé' sois los más honestos, y también los que más deuda tenéis."

**Transición:** "Vale. ¿Y dónde vive esta deuda en un tenant de Microsoft 365? Vamos al de FraSoHome."

*(13:00 → el moderador lee una pregunta del chat si hay alguna corta; si no, seguimos.)*

---

## 13:00–29:00 · Bloque 2 — Cómo aflora en Microsoft 365

### Slide 10 — FraSoHome en 20 segundos + mapa de síntomas

> "FraSoHome vende muebles y decoración. Tiene tres tiendas, e-commerce y un programa de fidelización. Y como todo el mundo, tiene un sitio de SharePoint del área comercial que nadie ha ordenado desde 2021."

Cuatro iconos: biblioteca sin taxonomía · duplicados contradictorios · etiquetas sin mantener · términos sin dueño.

### Síntoma 1 — Bibliotecas sin taxonomía (13:30–17:00) · Demo 1

**Pantalla:** SharePoint → sitio `FraSoHome-Comercial` → biblioteca *Documentos*.

1. Enseñar la estructura de carpetas: `Varios/`, `Antiguo/`, `Comité/`, `Definitivos/`.
2. Enseñar las columnas. Solo están *Nombre*, *Modificado* y *Modificado por*.
   > "Fijaos en lo que no hay: ni estado, ni dueño, ni 'vigente desde'. Lo único que separa lo bueno de lo malo es el nombre de la carpeta."
3. Ir a Copilot Chat como Laura:
   ```
   ¿Cuál es el plazo de devolución para compras online?
   ```
   **Esperado:** *30 días*, citando `Antiguo/FS-KB-02_Politica_Devoluciones_v1.2.docx`.
4. Abrir los dos documentos uno al lado del otro: FS-KB-01 v1.3 (45 días, VIGENTE) y FS-KB-02 v1.2 (30 días, OBSOLETA).
   > "Para un humano, la carpeta 'Antiguo' es un metadato. Para el índice, 'Antiguo' es una palabra más en la ruta del fichero."

**Frase de cierre del síntoma:** *"Una carpeta no es una taxonomía. Es una opinión de quien la creó."*

### Síntoma 2 — Duplicados con versiones contradictorias (17:00–21:00)

**Slide 11 — Cuatro ficheros, cuatro "ventas netas"**

| Fichero | Área | Cómo calcula "ventas netas" | Q4 vs Q3 2025 |
|---|---|---|---|
| `Informe_Comercial_Q4_2025_FINAL.pptx` | Marketing | Pedidos captados, con IVA, **sin restar devoluciones** | **−2,6 %** |
| `FS-KB-03_Diccionario_KPI_v1.0.docx` | Datos + Finanzas (**oficial**) | Con IVA, neto de devoluciones, sin cancelados ni duplicados | **+2,5 %** |
| `Cuadro_mando_tiendas_v3_bueno.xlsx` | Tiendas | Solo tienda física, sin IVA, neto de devoluciones | **+4,4 %** |
| `Cierre_mensual_2025-12_Finanzas.xlsx` | Finanzas | Sin IVA, solo pedidos entregados, sin duplicados | **+6,9 %** |

> "Son cuatro cálculos y los cuatro se pueden defender. Pero solo uno es oficial, y ese, como veremos ahora, Copilot no lo puede leer."

**Mini-demo (1') — Copilot como detector de deuda.** En Copilot Chat:

```
Compara cómo definen y calculan las "ventas netas" estos cuatro documentos y dime en qué discrepan.
```

(con los cuatro ficheros adjuntos o referenciados con `/`)

> "Ironía del día: Copilot es buenísimo para *encontrar* la deuda semántica. Lo que no puede hacer es decidir cuál de las cuatro es la buena, porque esa decisión no está en ningún documento."

**Dato para el remate (slide):**

> "En Copilot Studio, una fuente de conocimiento de SharePoint genera la respuesta con los **tres primeros resultados** de búsqueda. Si tienes cuatro versiones de un documento, haz la cuenta: puede que la oficial ni siquiera entre."

### Síntoma 3 — Etiquetas de Purview que nadie mantiene (21:00–25:00) · Demo 2

**Pantalla (perfil admin):** Purview → *Information Protection* → etiqueta **`Altamente confidencial – Finanzas`**. Enseñar que tiene cifrado y que los permisos solo los tiene el grupo *Finanzas*. La política de **etiquetado automático de 2024** la aplica a todo documento que contenga "margen" y "coste".

1. Enseñar que `FS-KB-03_Diccionario_KPI_v1.0.docx` lleva esa etiqueta, porque contiene la palabra "margen".
2. Volver a Laura, Copilot Chat:
   ```
   ¿Cuál es la definición oficial de ventas netas en FraSoHome?
   ```
   **Esperado:** responde con la definición del PowerPoint o mezcla varias. **No cita FS-KB-03.**

> "El documento existe, es el oficial y lo aprobó el CFO. Pero para usar contenido cifrado, Copilot necesita que el usuario tenga los derechos de *ver* y *extraer*, y Laura no los tiene. El diccionario es invisible para ella, y el PowerPoint, que no lleva etiqueta, se queda como la única verdad que Copilot ve."

**Frase de cierre del síntoma:** *"La etiqueta protegió el documento justo de quien más lo necesitaba."*

**Slide 12 — La deuda de gobierno en cifras de FraSoHome:** 14 etiquetas publicadas, 3 en uso, ninguna con dueño, y una política de autoetiquetado que nadie revisa desde que se creó.

> "Y el problema contrario también existe: si pones 'General' por defecto a todo, la etiqueta deja de dar señal. Una etiqueta que lo marca todo no distingue nada."

### Síntoma 4 — Términos de negocio sin dueño (25:00–29:00) · Demo 3

**Pantalla:** Copilot Chat como Laura:

```
¿Qué es un cliente activo en FraSoHome?
```

**Esperado:** una definición muy elocuente que mezcla el *estado = Activo* del CRM, la compra en 12 meses y la "actividad en la app" del PowerPoint.

**Slide 13 — Mismos datos, seis números** (calculado sobre el dataset del caso, año 2025):

| Definición | Quién la usa | Clientes |
|---|---|---|
| `estado_cliente = Activo` en el CRM | Atención al cliente | **47** |
| Socios del programa sin fecha de baja | Marketing (PPT) | **49** |
| Compradores online con pedido no cancelado | E-commerce | **89** |
| ≥1 compra en 12 meses y existe en el CRM | **Oficial FS-KB-03** | **100** |
| Compradores identificados en tienda | Tiendas | **132** |
| Cualquier ID con compra en 12 meses | Quien lea FS-KB-03 al pie de la letra | **135** |

> "Mirad la última fila. Hasta la definición oficial tiene deuda: dice `CustomerID` y no dice de qué sistema. Hay 35 identificadores en ventas que no existen en el CRM."

**Pantalla (admin, 30 s):** Purview → *Unified Catalog* → glosario → término **"Cliente activo"**: en borrador; el único propietario es la admin que lo creó, no hay nadie de negocio, y no tiene ningún producto de datos vinculado.

> "Este término lleva más de un año en borrador. No falta tecnología: falta alguien que firme."

**El procedimiento en tres cabezas (1')**

```
Un cliente devuelve en Gran Vía un pedido online que pagó con tarjeta y con puntos. ¿Cómo hago el reembolso?
```

**Esperado:** un procedimiento plausible y bien numerado. Puede decir, por ejemplo, *"reembolsa el importe total a la tarjeta"*. La política FS-KB-01 cubre tarjeta + efectivo y tarjeta regalo, y FS-KB-07 dice que las devoluciones descuentan los puntos *ganados*. **Ningún documento dice qué pasa con los puntos *canjeados*.**

> "Este procedimiento existe. Lo conocen Lucía, en caja de Gran Vía; Jorge, en atención al cliente, y Paco, en conciliación. Copilot no ha hablado con ninguno de los tres. Así que ha cosido tres documentos y se ha inventado el hueco."

**Transición:** "Si os habéis reconocido en dos de estos cuatro síntomas, tenéis deuda semántica. La buena noticia es que se puede medir *antes* de desplegar."

---

## 29:00–38:00 · Bloque 3 — El diagnóstico en cuatro pasos

### Slide 14 — Preguntar → Rastrear → Recuperar → Asignar

> "Casi todos los *assessments* de preparación para Copilot empiezan por los repositorios: cuántos sitios, cuánto se comparte de más, cuántos sitios sin propietario. Todo eso es necesario, pero no es suficiente. Este diagnóstico empieza por el otro extremo: por las preguntas."

### Paso 1 — Preguntar: el inventario de preguntas (2')

- Entre **20 y 30 preguntas reales por dominio.** Salen de los tickets, de los canales de Teams y de lo que se pregunta en comité.
- Cada una lleva una **respuesta esperada escrita por una persona con nombre y apellido.**

> "Si nadie es capaz de escribir la respuesta esperada, ya has encontrado deuda, y todavía no has abierto SharePoint."

FraSoHome: 20 preguntas del área comercial y de devoluciones.

### Paso 2 — Rastrear: la fuente canónica (2')

Para cada pregunta, ¿dónde está la respuesta? Se clasifica en cinco estados:

| Estado | Significa | FraSoHome (20) |
|---|---|---|
| **Canónica** | Una sola fuente, vigente y con dueño | 8 |
| **Duplicada** | Varias fuentes que coinciden | 3 |
| **Contradictoria** | Varias fuentes que discrepan | 4 |
| **Tácita** | Solo está en cabezas | 3 |
| **Inexistente** | Nadie lo ha decidido | 2 |

### Paso 3 — Recuperar: lo que Copilot ve de verdad (2,5')

- Lanzar cada pregunta **como usuarios reales de cada perfil** (comercial, tienda, finanzas), nunca como admin.
- Anotar la respuesta y las **citas**, y compararlas con la respuesta esperada.
- Causas típicas de la diferencia: permisos, cifrado, *Restricted Content Discovery*, contenido no indexado, versiones obsoletas que desplazan a la canónica en el top-N.

**La métrica (slide grande):**

> **Tasa de Respuesta Canónica (TRC)** = preguntas respondidas correctamente *y* citando la fuente canónica ÷ total de preguntas.
>
> FraSoHome hoy: **7 / 20 = 35 %**

> "Fijaos: hay 8 preguntas con fuente canónica, pero Copilot solo acierta 7. Ese uno de diferencia es el diccionario de KPI cifrado. Incluso la deuda que ya habías pagado se te puede escapar por el gobierno."

### Paso 4 — Asignar: dueño y precio (2')

Para cada hueco:

- **Dueño del significado**: alguien de negocio. IT es dueña del contenedor, no del significado.
- **Precio de una respuesta incorrecta** = frecuencia × impacto.
- **Tipo de acción**: *decidir · consolidar · documentar · re-etiquetar · retirar*.

> "Una deuda sin dueño ya no es deuda: es una pérdida que todavía no has contabilizado."

**Slide 15 — La matriz final** (pregunta × estado × dueño × precio × acción). *"Este es el entregable que llevas al comité. No una lista de licencias."*

---

## 38:00–41:00 · Bloque 4 — Señales de alerta antes de desplegar

**Slide 16** — *"Contad cuántas tenéis y escribid el número en el chat."*

1. Nadie es capaz de nombrar en 30 segundos al dueño de "cliente" o del KPI principal.
2. Los comités empiezan conciliando cifras: *"¿de qué número partimos?"*
3. Hay bibliotecas con solo las columnas por defecto y carpetas tipo `Varios`, `Antiguo`, `Final`.
4. En una misma biblioteca conviven nombres con `final`, `v2`, `bueno` o `definitivo`.
5. Una sola etiqueta lo marca casi todo, o hay etiquetas con cifrado que nadie sabe explicar.
6. Hay sitios sin propietario activo o creados por personas que ya no están en ese equipo.
7. El onboarding de un proceso es *"siéntate una semana con Lucía"*.
8. El piloto de Copilot se evalúa con *"¿te gusta?"* y no con preguntas que tienen respuesta esperada.

**Lectura (heurística propia, se dice así):** 0–2 → adelante · 3–5 → diagnostica antes de ampliar · 6–8 → para el despliegue y paga primero.

> *(leer dos o tres números del chat)* "Si alguien ha puesto un 8, que me escriba cuando acabe. Lo digo en serio."

---

## 41:00–50:00 · Bloque 5 — Qué se puede arreglar (y qué no)

### Slide 17 — "Las herramientas pagan intereses. El principal se paga con decisiones."

| Herramienta | Deuda que ataca | Qué hace | Qué **no** hace |
|---|---|---|---|
| **Term store + tipos de contenido + columnas** | Definición, versión | Vocabulario controlado: *Estado (Vigente/Borrador/Obsoleta)*, *Dominio*, *Propietario*, *Vigente desde* | No decide cuál es el oficial |
| **Knowledge Agent de SharePoint** (preview) | Versión (el atraso) | Propone columnas y las rellena a partir del contenido; crea vistas y reglas | No responde preguntas ni elige la versión buena; solo rellena los primeros 20 ficheros de muestra y el resto hay que seleccionarlo |
| **Copilot Studio · fuentes de conocimiento** | Versión, definición | Acota a una biblioteca curada; **filtra por metadatos** antes de buscar, para preferir *Vigente*; instrucciones de ambigüedad y glosario; evaluación con test set | No arregla el contenido de origen; resume con el top-3; sincroniza cada 4–6 h |
| **Purview** | Gobierno | Racionalizar etiquetas y derechos de cifrado; DSPM for AI para ver qué toca Copilot; **glosario del Unified Catalog con dueño y *steward*** vinculado a productos de datos; ciclo de vida para retirar lo obsoleto | No escribe definiciones ni pone de acuerdo a Marketing y Finanzas |
| **SharePoint Advanced Management** | Gobierno | Contenido obsoleto o sin propietario, revisión de accesos, *Restricted Content Discovery* | RCD es un **torniquete**: esconde, pero no cura |
| **Work IQ** | Tácita (en parte) | Capa de contexto: datos (incluidos conectores a sistemas de registro), contexto y memoria, *skills* y herramientas vía MCP | Amplifica lo que hay. Si lo que hay es ruido, amplifica ruido con más contexto |

> "Work IQ merece una frase aparte, porque es lo que más se va a vender este año. Es la capa que hace que Copilot entienda *tu* trabajo, y es muy buena. Pero no crea significado: lo consume. Con señal, amplifica señal. Con deuda, te da respuestas incorrectas mejor contextualizadas."

**Slide 18 — Para los que venís del dato (1')**: **Fabric IQ**, la ontología (en preview). Defines *Cliente* una sola vez, con relaciones, reglas y métricas ligadas a las medidas DAX del modelo semántico. Los agentes reutilizan el cálculo de confianza en lugar de reinventarlo.

> "Es la versión estructurada del mismo acuerdo. Y fijaos en que también hace falta que alguien acuerde qué es un cliente antes de modelarlo."

### Demo 4 — El "después" (44:00–49:00)

**Lo que cambió en el tenant** (slide 19, se enseña durante 15 s):

- Biblioteca `FraSoHome-KB-Oficial` con las columnas *Estado*, *Dominio* y *Propietario* (term store). FS-KB-02 pasa a **Obsoleta**.
- FS-KB-03 se re-etiqueta como `Interno – Definiciones oficiales`, sin cifrado, y queda excluida de la política de autoetiquetado.
- Glosario: **"Cliente activo"** publicado, con dueño (Dirección Comercial) y *steward* (Equipo de Datos).
- Agente de Copilot Studio **"Asistente Comercial FraSoHome"**: su conocimiento es solo esa biblioteca y sus instrucciones dicen *"si un término de negocio es ambiguo, pregunta qué definición quiere el usuario antes de responder; declara siempre la fórmula usada"*.

**Mismas preguntas, en el agente:**

1. `¿Cuál es el plazo de devolución para compras online?` → **45 días naturales**, cita FS-KB-01 v1.3.
2. `¿Cuántos clientes activos tenía FraSoHome al cierre de 2025?` → **pregunta**: *"¿Te refieres a la definición oficial (≥1 compra en 12 meses, FS-KB-03) o a los socios del programa?"* → oficial → **100**.
3. `¿Cómo evolucionaron las ventas netas en el Q4 respecto al Q3?` → **+2,5 %**, *declara la fórmula* (es una regla del propio FS-KB-03).
4. `Devolución en tienda de pedido online pagado con tarjeta y puntos` → **"No hay un procedimiento documentado para el reembolso de puntos canjeados. Contacta con Atención al Cliente (Jorge)."**

> "Fijaos en la última. Para mí es la mejor respuesta del día: 'no lo sé, pregúntale a Jorge'. Abstenerse también es una respuesta correcta. Y esto no lo ha conseguido ninguna licencia: lo ha conseguido alguien que tomó una decisión."

**TRC después:** 15 / 20 = **75 %** (slide). Los cinco fallos que quedan son las 3 tácitas y las 2 inexistentes: no se arreglan configurando nada, se arreglan decidiendo.

### Slide 20 — Lo que ninguna herramienta hace (1')

> "Ninguna herramienta decide qué es un cliente. Eso se resuelve con una reunión, un acta y un dueño. Lo demás es *tooling*."

---

## 50:00–53:00 · Bloque 6 — El argumento: por qué la próxima licencia no lo arregla

**Slide 21 — Tres argumentos para tu comité**

1. **Un modelo mejor lee los mismos documentos.** Lo que consigues son respuestas incorrectas más convincentes.
2. **El coste no está en la licencia, sino en la respuesta incorrecta multiplicada.** En FraSoHome, unas 40 personas de tienda y atención al cliente aplicando 30 días en lugar de 45: devoluciones rechazadas que no tocaba rechazar, reclamaciones y clientes Oro que se van.
3. **No pidas más licencias. Pide tres dueños, noventa días y un test set.** Y mide la TRC antes y después.

**Slide 22 — La frase para el comité:**

> **"No tenemos un problema de IA. Tenemos treinta años de acuerdos sin firmar, y la IA acaba de leerlos en voz alta."**

> "El diagnóstico, las señales y la plantilla de la matriz están en el repositorio. El enlace os lo deja el moderador en el chat. Gracias. Vamos con las preguntas."

---

## 53:00–60:00 · Q&A

Respuestas preparadas para las preguntas previsibles. Contesta en 30–60 s cada una.

| Pregunta | Respuesta corta |
|---|---|
| *"¿Esto no lo arreglan los modelos de razonamiento?"* | Razonan mejor sobre lo que recuperan. Si recuperan el PowerPoint, razonarán muy bien sobre el PowerPoint. |
| *"¿Y si con RCD escondo lo malo?"* | Es un torniquete válido para *ganar tiempo* mientras pagas. Si lo dejas puesto, has escondido la deuda, no la has pagado. |
| *"Tengo 10.000 sitios, ¿por dónde empiezo?"* | Por un dominio y 20 preguntas. Nunca por los 10.000 sitios. |
| *"¿El dueño es IT o negocio?"* | Negocio es dueño del significado. IT, del contenedor y de los controles. |
| *"¿El Knowledge Agent no lo hace solo?"* | Te ayuda a pagar el atraso de metadatos, pero no decide qué documento es el oficial. |
| *"¿Qué licencias necesito para SAM, DSPM for AI, Unified Catalog…?"* | Ha cambiado varias veces. Compruébalo con tu licenciamiento actual; no me la juego con una cifra en directo. |
| *"¿Cómo lo vendo a dirección?"* | Con la TRC: "hoy Copilot acierta 7 de cada 20 preguntas importantes, y en 90 días con tres dueños llegamos a 15". |
| *"¿Esto aplica a agentes, no solo a Copilot?"* | Más todavía. Un agente no se limita a responder: actúa sobre la interpretación equivocada. |

**Cierre (59:30):** *"Gracias. Id a buscar a vuestro dueño de 'cliente'. Si no lo encontráis, ya sabéis por dónde empezar."*

---

## Plan B por demo

| Demo | Si falla… | Qué haces |
|---|---|---|
| 0 | Copilot da por casualidad la cifra oficial | *"Hoy ha acertado. Ahora os enseño la respuesta de esta mañana."* → vídeo. La falta de determinismo es parte del argumento: **una respuesta que a veces acierta no es una respuesta oficial.** |
| 1 | Responde 45 días | Lanza la misma pregunta otra vez y pide que cite. Si sigue acertando, pon el vídeo y di que la respuesta varía entre ejecuciones. |
| 2 | Cita FS-KB-03 | Comprueba si Laura está en el grupo *Finanzas* (error de montaje). Si no hay tiempo, vídeo. |
| 3 | Responde con una definición única y correcta | Slide 13: la cifra cambia según el sistema que se consulte, aunque la frase sea correcta. |
| 4 | El agente no pregunta por la ambigüedad | Pídele que use la definición oficial y señala que la instrucción está en el agente, no en la biblioteca. *"Por eso el acuerdo tiene que vivir en el contenido, no solo en el prompt."* |
| Teams cae | — | El moderador pone el vídeo completo de las demos (≈6'). |

## Recortes si vas tarde

- **−2'**: quitar la mini-demo del síntoma 2 y dejar solo la slide 11.
- **−1'**: quitar la slide 18 (Fabric IQ).
- **−1,5'**: el procedimiento tácito se cuenta solo con la frase de las tres cabezas, sin lanzar la pregunta.
- **Nunca recortar**: la apertura, la TRC, la demo 4 y la frase para el comité.

## Referencias para las notas del orador

- Evento: https://sessionize.com/microsoft365live2026/
- Work IQ (datos, contexto, *skills* y herramientas): https://adoption.microsoft.com/files/microsoft-365-community-conference/2026/pdf/MS40%20-%20Work%20IQ%20Fundamentals.pdf
- Límites de SharePoint como fuente de conocimiento en Copilot Studio (top-3, 25 sitios, sincronización de 4–6 h, cifrado): https://nordflux.de/en/insights/copilot-studio-the-real-limits-of-sharepoint-knowledge-sources
- Filtrado por metadatos en fuentes de SharePoint de Copilot Studio (sept. 2026): https://microsoft.github.io/mcscatblog/posts/sharepoint-metadata-filtering/
- Knowledge Agent de SharePoint (preview, muestra de 20 ficheros, no responde preguntas): https://www.aguidetocloud.com/blog/microsoft-365-knowledge-agent/
- SharePoint Admin Agent / SAM (ciclo de vida, sitios sin propietario, RCD): https://adoption.microsoft.com/files/microsoft-365-community-conference/2026/pdf/MS96%20-%20From%20Chaos%20to%20AI-Ready%20in%2030%20Days_%20Meet%20the%20SharePoint%20Admin%20Agent.pdf
- Unified Catalog de Purview (dominios, términos, productos de datos): https://learn.microsoft.com/purview/unified-catalog-plan
- Fabric IQ y ontología (preview): https://learn.microsoft.com/en-us/fabric/iq/overview
- **Por verificar antes del evento:** (a) que la página de Learn sobre Copilot y cifrado siga exigiendo los derechos VIEW + EXTRACT; (b) que el filtrado por metadatos admita columnas de *managed metadata* (el post solo confirma columnas personalizadas; si no, usa una columna de opción para *Estado*).
