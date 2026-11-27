# Slides — Identidad, acceso y ciclo de vida de agentes con Microsoft Entra Agent ID

Descripción slide a slide de las **36 slides + 4 de plan B** del guion (`02_guion-sesion.md`). Cada ficha dice qué texto va en pantalla, qué visualización lleva, cómo se construye y cuánto tiempo está a la vista. Lo que se *dice* está en el guion; aquí solo lo que se *ve*.

> **Plantilla (actualizado 22 nov):** el deck `05_presentacion-entra-agent-id.pptx` está construido sobre la plantilla oficial del evento (`entrada/plantilla/AzureCloudLab2026.pptx`), que es **oscura en todas las slides**. Se aplican tres ajustes sobre lo que describe este documento:
> 1. Las slides de contenido van sobre el fondo oscuro de la plantilla, con tarjetas `#1B244C`; los colores semánticos se aclaran para que contrasten (puerta 1 `#2BB3A0`, puerta 2 `#A38BF5`, puerta 3 `#F08A4B`, Entra `#2F7FE0`, ok `#34C98B`, aviso `#F5A623`, bloqueo `#E0364A`, que coinciden con los acentos de la plantilla).
> 2. Los diagramas van en su **variante oscura** (`diagramas/oscuro/`), sin título dentro de la imagen.
> 3. **Sin miniaturas del mapa de controles** en las slides 23–29: la esquina superior derecha la ocupa el logo del evento y abajo está el pie de la plantilla. Portada y slide final (36, Q&A) reutilizan las slides de la plantilla; separadores y frases ancla usan su layout *Encabezado de sección*.

---

> **Notas del orador (27 nov):** el deck lleva en las notas contenido técnico desarrollado por slide (modelo de objetos, flujos de token, controles, pasos técnicos de cada demo), sin tiempos ni referencias. Los tiempos y frases literales siguen en `02_guion-sesion.md`.

## Sistema visual

### Formato

- **16:9**, 1920 × 1080. Online: el público lo ve en una ventana pequeña, así que **ningún texto por debajo de 24 pt** salvo las notas al pie (18 pt).
- **Un mensaje por slide.** Si una slide necesita leerse, es una tabla para hacer captura y se dice en voz alta.

### Tipografía

| Uso | Fuente | Tamaño |
|---|---|---|
| Títulos | Segoe UI Semibold | 40–48 pt |
| Frases ancla y slides de una frase | Segoe UI Light | 54–66 pt |
| Cuerpo y tablas | Segoe UI | 24–28 pt |
| Código, IDs y nombres técnicos | Cascadia Code | 22–24 pt |

### Colores semánticos

Cada puerta tiene un color fijo que se repite en **todas** las slides, diagramas y capturas anotadas. Es lo que permite seguir a cada agente sin leer.

| Token | Hex | Uso |
|---|---|---|
| `entra` | `#0078D4` | Todo lo que es Entra: blueprint, identidad, acceso condicional |
| `puerta-1` | `#0F7B6C` | Copilot Studio · `FS-Copilot-Devoluciones` |
| `puerta-2` | `#6B4FBB` | Foundry · `frasohome-returns` |
| `puerta-3` | `#CA5010` | Agente propio · `fs-triage-devoluciones` |
| `ok` | `#107C10` | Funciona o permitido |
| `aviso` | `#C19C00` | Técnicamente válido pero mal (el sponsor de Marta) |
| `bloqueo` | `#C4314B` | Bloqueado, error o 403 |
| `fondo-claro` | `#FFFFFF` / texto `#1B1B1B` | Slides de contenido |
| `fondo-oscuro` | `#0B1F33` / texto `#FFFFFF` | Apertura, separadores de demo, frases ancla y cierre |

### Iconos

- **Solo iconos oficiales de producto**, de la librería *Azure* de draw.io (iconos oficiales de Azure, Entra y Power Platform). Las rutas exactas están en `04_diagramas-drawio.md`.
- **Agent 365 no tiene icono oficial** en esa librería. Va como texto en una caja con el color `entra`, sin inventar logo. Ver `04_diagramas-drawio.md`.
- Personas: iniciales en un círculo (`MR`, `NS`, `DL`, `LM`, `JP`, `AG`) con el color de la puerta del agente con el que se relacionan. Sin fotos de stock.

### Capturas de portal

- Siempre **recortadas** al panel que importa, nunca la pantalla completa.
- Anotaciones con un rectángulo de 4 px del color semántico y una etiqueta corta. Como máximo, tres por captura.
- Datos sensibles del tenant de demo (IDs reales, correos) **difuminados**, salvo el nombre del agente.

### Separadores de demo

Mismo layout para las cuatro: `fondo-oscuro`, número grande de la demo, la pregunta de la demo y una línea con el color de la puerta. Se ven 3 segundos.

---

## Apertura

### Slide 1 · Título

| | |
|---|---|
| Tiempo | 0:00–0:10 |
| Layout | `fondo-oscuro` |

**En pantalla:**
- **Identidad, acceso y ciclo de vida de agentes**
- con Microsoft Entra Agent ID
- Antonio Soto · Azure Cloud Lab 2026

**Visualización:** a la derecha, el icono oficial de Entra ID grande (`other/Entra_Identity.svg`) y, detrás, tres líneas finas de los colores de las puertas que convergen en el icono. Es un adelanto del diagrama D2.

---

### Slide 2 · La primera pregunta

| | |
|---|---|
| Tiempo | 0:10–1:00 |
| Layout | `fondo-oscuro`, una frase |

**En pantalla:**
> **¿Cuántos service principals hay en tu tenant?**

Pregunta retórica: no se pide respuesta en el chat.

**Visualización:** ninguna. Solo la frase, centrada, en Segoe UI Light a 60 pt.

---

### Slide 3 · La segunda pregunta

| | |
|---|---|
| Tiempo | 1:00–2:00 |
| Layout | `fondo-oscuro`, una frase |

**En pantalla:**
> **¿Y de cuántos sabes quién responde?**

**Construcción:** aparece primero la pregunta de la slide 2 en gris, pequeña, arriba. Después, esta en blanco y grande. El salto visual es el mensaje.

---

### Slide 4 · Quién soy y qué te llevas

| | |
|---|---|
| Tiempo | 2:00–3:00 |
| Layout | Dos columnas 1:2 |

**En pantalla:**
- Columna izquierda: **Antonio Soto** · MVP Fabric & Foundry · Dataging.
- Columna derecha, **Te llevas:**
  1. El modelo, lo bastante bien como para diseñarlo
  2. Qué controles cambian con un agente
  3. Una checklist para el lunes

**Visualización:** sin foto grande; avatar circular de 160 px. Los tres puntos con números grandes en `entra`.

---

### Slide 5 · FraSoHome en 20 segundos

| | |
|---|---|
| Tiempo | 3:00–3:30 |
| Layout | Franja superior + tres tarjetas |

**En pantalla:**
- Franja: **FraSoHome** · retail de hogar · 3 tiendas · e-commerce · fidelización · *un proceso: devoluciones*
- Tres tarjetas, una por puerta, con su color:
  - **Puerta 1** · icono de Copilot Studio · `FS-Copilot-Devoluciones`
  - **Puerta 2** · icono de Foundry Agent Service · `frasohome-returns`
  - **Puerta 3** · icono de Container Apps · `fs-triage-devoluciones`

**Visualización:** iconos oficiales (`power_platform/CopilotStudio.svg`, `ai_machine_learning/Foundry_Agent_Service.svg`, `other/Worker_Container_App.svg`). Las tarjetas aparecen una a una.

---

## Bloque 1 · Por qué el service principal no aguanta

### Slide 6 · La llave y el que tiene llaves

| | |
|---|---|
| Tiempo | 3:30–5:00 |
| Layout | Dos columnas de contraste |

**En pantalla:**
- Título: **Un service principal es una llave. Un agente es alguien con llaves.**
- Tabla de cuatro filas:

| Service principal | Agente |
|---|---|
| Hace siempre lo mismo | **Decide qué hace** |
| Actúa como sí mismo | **Como sí mismo o como un usuario** |
| Lo crea IT, de uno en uno | **Se crea por cientos** |
| Vive lo que la aplicación | **Sobrevive a quien lo creó** |

**Visualización:** encima de la columna izquierda, el icono `identity/Enterprise_Applications.svg` en gris. Encima de la derecha, `ai_machine_learning/Foundry_Agent_Service.svg` en color. La columna derecha va en negrita y aparece fila a fila.

---

### Slide 7 · Las cuatro cosas que rompen el modelo

| | |
|---|---|
| Tiempo | 5:00–7:00 |
| Layout | Cuatro filas numeradas |

**En pantalla:**

| # | Rompe | Consecuencia |
|---|---|---|
| 1 | Decide qué herramientas usa | El mínimo privilegio es lo único que lo acota |
| 2 | Actúa en nombre de usuarios | Cambia a quién se le aplica el acceso condicional |
| 3 | Se crea por cientos | El inventario ya existe: ¿quién lo mira? |
| 4 | Sobrevive a quien lo construyó | El problema de la app registration de 2019, en meses |

**Construcción:** una fila por clic. La columna "Consecuencia" en `entra`.

---

### Slide 8 · Frase ancla (1.ª vez)

| | |
|---|---|
| Tiempo | 7:00–8:00 |
| Layout | `fondo-oscuro`, una frase |

**En pantalla:**
> **Un agente sin sponsor no es un agente:**
> **es una incidencia esperando fecha.**

**Visualización:** la palabra **sponsor** en `aviso`. Nada más. Esta misma slide, idéntica, reaparece como fondo de la frase al final de las slides 28 y 33. Es una slide maestra.

---

## Bloque 2 · El modelo de Agent ID

### Slide 9 · El modelo ⭐

| | |
|---|---|
| Tiempo | 8:00–9:30 |
| Layout | Diagrama a pantalla completa |
| Diagrama | **D1 · El modelo de Agent ID** (`diagramas/D1-modelo-agent-id.drawio`) |

**En pantalla:**
- Título: **Blueprint → identidad de agente → usuario de agente**
- El diagrama D1: el blueprint a la izquierda, con su credencial; tres identidades de agente heredando de él; una de ellas con su cuenta de usuario de agente; los tres papeles humanos (owner, sponsor y manager) a un lado.

**Construcción en tres clics:**
1. Blueprint + credencial.
2. Las tres identidades, con la flecha "hereda políticas" resaltada.
3. Cuenta de usuario de agente + los papeles humanos.

**Detalle visual:** las dos flechas que se mencionan en el guion (credenciales en el blueprint y políticas heredadas) van en `entra` y con 3 px; el resto, en gris y con 1,5 px.

---

### Slide 10 · Tres flujos, tres sujetos

| | |
|---|---|
| Tiempo | 9:30–11:00 |
| Layout | Tabla de tres filas + ilustración |

**En pantalla:**

| Flujo | Sujeto del token | El acceso condicional se aplica a… |
|---|---|---|
| Autónomo | Identidad de agente | **El agente** |
| En nombre de usuario (OBO) | **El usuario** | **El usuario** |
| Como usuario de agente | Cuenta de usuario del agente | La cuenta de usuario del agente |

**Visualización:** a la derecha de cada fila, un mini-esquema de tres iconos: *quién pide → token → recurso*. En la fila OBO, la persona `AG` (Álvaro) en `puerta-1` delante del icono de Copilot Studio, para que se vea que el token es suyo. **La fila OBO va resaltada** con un fondo `aviso` al 10 %.

---

### Slide 11 · Owner, sponsor, manager

| | |
|---|---|
| Tiempo | 11:00–12:15 |
| Layout | Tabla de tres columnas |

**En pantalla:** la tabla del guion (para qué, obligatorio, puede, no puede, grupo). Encima de cada columna, un icono:
- Owner: `identity/App_Registrations.svg` (lo técnico)
- Sponsor: `identity/Users.svg` en `aviso` (la persona que responde)
- Manager: `identity/Groups.svg` (la jerarquía)

**Resaltado:** la celda "Sponsor · No puede: **rehabilitar ni restaurar**" en `bloqueo`, con una etiqueta: *freno de emergencia, no interruptor*.

---

### Slide 12 · Se gobierna la plantilla, se responde por la instancia

| | |
|---|---|
| Tiempo | 12:15–13:00 |
| Layout | Una frase + mini-diagrama |

**En pantalla:**
> **IT gobierna la plantilla. El negocio responde por la instancia.**

**Visualización:** un blueprint arriba con la etiqueta "IT · credencial + políticas" y tres identidades debajo con una persona-sponsor distinta cada una. Es la versión reducida de D1, sin texto adicional.

---

### Slide 13 · Las tres puertas

| | |
|---|---|
| Tiempo | 13:00–13:30 |
| Layout | Diagrama a pantalla completa |
| Diagrama | **D2 · Tres puertas, un directorio** (`diagramas/D2-tres-puertas.drawio`) |

**En pantalla:** el diagrama D2. Tres columnas (Copilot Studio, Foundry y Container Apps), cada una con su blueprint, que convergen en Entra Agent ID y, debajo, en el registro de Agent 365.

**Construcción:** las tres puertas aparecen a la vez, atenuadas al 40 %. En el resto de la sesión, esta misma slide se reutiliza con **una sola puerta encendida** en los separadores de las demos 1, 2 y 3 (slides 14, 17 y 21).

---

### Slide 14 · Separador · Demo 1

| | |
|---|---|
| Tiempo | 13:30 (3 segundos) |
| Layout | Separador de demo, línea `puerta-1` |

**En pantalla:**
- **DEMO 1**
- ¿Quién responde por este agente?
- Puerta 1 · Copilot Studio

**Visualización:** a la derecha, D2 reducido con solo la puerta 1 encendida.

---

### Slide 15 · Lo que Entra no ve

| | |
|---|---|
| Tiempo | 16:30–17:00 (remate de la demo 1) |
| Layout | Ficha centrada |

**En pantalla:** la ficha de `FS-Copilot-Devoluciones` simplificada, como una tarjeta de identidad:

| | |
|---|---|
| Agente | `FS-Copilot-Devoluciones` |
| Blueprint | Copilot Studio (global) |
| Actividad | ✅ cientos de inicios de sesión / semana |
| Sponsor | ✅ **Marta R.** · cuenta activa |
| Departamento del sponsor | ⚠️ **e-commerce** (desde julio) |
| Área del agente | Tiendas |

**Pie, grande:** *Todo en verde. Nadie respondiendo.*

**Visualización:** borde de la tarjeta en `puerta-1`. Las dos filas ⚠️ con fondo `aviso` al 15 %.

---

## Bloque 3 · Puerta 2: Foundry

### Slide 16 · Identidad compartida frente a identidad propia

| | |
|---|---|
| Tiempo | 17:00–19:00 |
| Layout | Dos columnas + nota al pie |

**En pantalla:**
- Título: **Foundry: los roles no viajan**
- Dos columnas:

| Identidad compartida del proyecto | Identidad propia del agente |
|---|---|
| Un blueprint por proyecto | Un blueprint por agente |
| Los roles los comparten todos los agentes | **Los roles hay que asignarlos de nuevo** |
| Agentes del modelo anterior y sin publicar | Modelo actual · agentes publicados |

- Nota al pie, en código: `audience = https://storage.azure.com` ✅ · `audience = https://<mcp-server>` ❌

**Visualización:** encima de cada columna, el icono `ai_machine_learning/Foundry_Project.svg` (compartida) y `ai_machine_learning/Foundry_Agent_Service.svg` (propia), con el color `puerta-2`. Entre las dos columnas, una flecha con la etiqueta "publicar / migrar" y un candado roto en `bloqueo`.

---

### Slide 17 · Separador · Demo 2

| | |
|---|---|
| Tiempo | 19:00 (3 segundos) |
| Layout | Separador de demo, línea `puerta-2` |

**En pantalla:**
- **DEMO 2**
- El rol que no viaja
- Puerta 2 · Foundry

**Visualización:** a la derecha, D2 reducido con solo la puerta 2 encendida.

---

### Slide 18 · La lección

| | |
|---|---|
| Tiempo | 22:00–22:30 |
| Layout | Diagrama a la izquierda (60 %) + checklist a la derecha |
| Diagrama | **D3 · El rol que no viaja** (`diagramas/D3-rol-que-no-viaja.drawio`) |

**En pantalla:**
- D3: la identidad compartida con el rol sobre el Storage (flecha `ok`) y la identidad propia sin rol (flecha discontinua `bloqueo`, etiqueta **403**).
- Checklist:
  1. Exporta los roles de la identidad compartida
  2. Reasígnalos al `agentIdentityId`, con scope de recurso y roles de datos
  3. Comprueba el **audience** de cada conexión MCP

---

## Bloque 4 · Puerta 3: el agente propio

### Slide 19 · El flujo sin secretos

| | |
|---|---|
| Tiempo | 22:30–23:45 |
| Layout | Diagrama a pantalla completa |
| Diagrama | **D4 · Sin secretos** (`diagramas/D4-flujo-sin-secretos.drawio`) |

**En pantalla:** D4 con los cinco pasos numerados: Container App → managed identity → blueprint (federated credential) → token de intercambio con `fmi_path` → token de la identidad de agente → Storage. En el paso 5, un escudo de acceso condicional y el icono de ID Protection sobre Entra, con la etiqueta **"aquí Entra puede decir que no"**.

**Construcción:** un paso por clic, en el orden del guion. El paso 5 aparece con un ligero zoom.

---

### Slide 20 · Qué credencial para el blueprint

| | |
|---|---|
| Tiempo | 23:45–24:30 |
| Layout | Tabla de cuatro filas |

**En pantalla:**

| Credencial | Producción |
|---|---|
| Managed identity (federated credential) | ✅ La recomendada |
| Certificado | ✅ Fuera de Azure |
| Secreto | ❌ Solo desarrollo |
| API key del servicio | ❌ Se salta Entra |

**Visualización:** icono `identity/Entra_Managed_Identities.svg` junto a la primera fila. Las filas ❌ en gris con el texto tachado al 50 %. Debajo, en pequeño: *AWS y GCP: también con federación.*

---

### Slide 21 · Separador · Demo 3

| | |
|---|---|
| Tiempo | 24:30 (3 segundos) |
| Layout | Separador de demo, línea `puerta-3` |

**En pantalla:**
- **DEMO 3**
- Sin secretos
- Puerta 3 · Agente propio en Container Apps

**Visualización:** a la derecha, D2 reducido con solo la puerta 3 encendida.

---

## Bloque 5 · Los controles de siempre, sobre un sujeto nuevo

### Slide 22 · El mapa de controles

| | |
|---|---|
| Tiempo | 28:30–29:00 |
| Layout | Diagrama radial |
| Diagrama | **D5 · Mapa de controles** (`diagramas/D5-mapa-controles.drawio`) |

**En pantalla:** la identidad del agente en el centro y cinco controles alrededor, cada uno con su icono oficial:
- RBAC → `identity/Custom_Azure_AD_Roles.svg`
- Acceso condicional → `security/Conditional_Access.svg`
- ID Protection → `identity/Entra_ID_Protection.svg`
- Ciclo de vida → `identity/Identity_Governance.svg`
- Rastro → `analytics/Log_Analytics_Workspaces.svg`

**Uso:** esta slide se reutiliza en miniatura (esquina superior derecha, 200 px) en las slides 23–29, con el control del que se habla resaltado. Así el público sabe en qué punto está.

---

### Slide 23 · RBAC: tres reglas

| | |
|---|---|
| Tiempo | 29:00–29:45 |
| Layout | Tres filas grandes |

**En pantalla:**
1. **Al `agentIdentityId`**, no a la MI ni a la identidad compartida
2. **Scope de recurso**, no de suscripción
3. **Roles de datos**, no `Contributor`

**Visualización:** a la derecha de la regla 2, una escalera de scopes (suscripción → grupo de recursos → cuenta → **contenedor**) con el último peldaño en `ok`. Miniatura de D5 con RBAC resaltado.

---

### Slide 24 · Acceso condicional para agentes ⭐

| | |
|---|---|
| Tiempo | 29:45–31:15 |
| Layout | Tabla arriba + cuatro trampas abajo |

**En pantalla:**
- Tabla (identidades de agente frente a cuentas de usuario de agente: cómo se seleccionan, condiciones y controles), como en el guion.
- Abajo, cuatro "trampas" en tarjetas pequeñas con borde `bloqueo`:
  1. **Solo bloquear**
  2. **OBO → el sujeto es el usuario**
  3. **"Todos los usuarios" ≠ usuarios de agente**
  4. **API keys → fuera de Entra**

**Visualización:** icono `security/Conditional_Access.svg` junto al título. Las trampas aparecen una por clic. Esta es la slide para hacer captura: dilo.

---

### Slide 25 · Los carriles, convertidos en política

| | |
|---|---|
| Tiempo | 31:15–32:00 |
| Layout | Atributo a la izquierda + dos políticas a la derecha |

**En pantalla:**
- Izquierda: el atributo como una etiqueta grande:
  `FraSoHome.Carril` = `Playground` · `Equipo` · **`Produccion`** · `Enterprise`
- Derecha, dos tarjetas de política:
  - **CA-AG-01** · Carril = Produccion · riesgo **alto** → 🛑 bloquear
  - **CA-AG-02** · Carril = Playground → 🛑 bloquear recursos de producción

**Visualización:** las cuatro etiquetas del carril con un gradiente de gris (Playground) a `entra` (Enterprise), en guiño a la tabla de carriles del Bizz Summit. Pie: *Un agente nuevo con el atributo correcto queda cubierto el primer día.*

---

### Slide 26 · ID Protection para agentes

| | |
|---|---|
| Tiempo | 32:00–32:45 |
| Layout | Dos columnas: detecciones y acciones |

**En pantalla:**
- **Detecta:** reconocimiento del directorio · picos de inicio de sesión · recursos fuera de lo habitual · credenciales nuevas en el blueprint
- **Actúa:** confirmar comprometido · confirmar seguro · descartar · deshabilitar
- Nota: *En OBO, el riesgo es del usuario.*

**Visualización:** icono `identity/Entra_ID_Protection.svg`. **"Confirmar comprometido"** resaltado en `bloqueo`, con una flecha hacia una miniatura de CA-AG-01: el puente con la demo 4.

---

### Slide 27 · El ciclo de vida

| | |
|---|---|
| Tiempo | 32:45–33:45 |
| Layout | Línea temporal horizontal a todo el ancho + bloque inferior |

**En pantalla:**
- Línea temporal grande, con cuatro hitos:
  - **Día 0** · último token
  - **Día 60** · ✉️ aviso a sponsors y owners (`aviso`)
  - **Día 90** · ⏸ deshabilitado (`bloqueo`)
  - **Día 455** · 🗑 borrado
- Encima: *Política por defecto · sin licencia · inactividad = sin tokens*
- Debajo, **Políticas personalizadas:** reconfirmación del sponsor cada 30–730 días · mínimo de sponsors · deshabilitar o borrar

**Visualización:** esta línea temporal es **nativa de PowerPoint**, no draw.io: se anima mejor. La escala no es lineal (los días 90 a 455 van comprimidos con un corte ⫽), para que se lean los tres primeros hitos. Icono `identity/Identity_Governance.svg`.

---

### Slide 28 · Cuando el sponsor se mueve

| | |
|---|---|
| Tiempo | 33:45–34:30 |
| Layout | Tabla + recomendación |

**En pantalla:**

| Tarea de Lifecycle Workflows | Mover | Leaver |
|---|---|---|
| Avisar al manager | ✅ | ✅ |
| Avisar a los co-sponsors | ✅ | ✅ |
| Transferir sponsorships al manager | ⚠️ **No** | ✅ |

- Recomendación, grande: **Leaver: transfiere. Mover: avisa.**

**Visualización:** mini-esquema a la derecha: Marta `MR` se mueve de la caja "Tiendas" a la caja "e-commerce"; el agente se queda en "Tiendas"; una flecha discontinua de transferencia hacia "e-commerce" tachada en `bloqueo`. Al terminar, la slide 8 (frase ancla) en transición de fundido.

---

### Slide 29 · Caducidad y rastro

| | |
|---|---|
| Tiempo | 34:30–35:00 |
| Layout | Dos mitades |

**En pantalla:**
- Izquierda, **Access packages para agentes:** lo pide el agente, el sponsor o un admin → aprobación → **fecha de fin** → aviso al sponsor.
- Derecha, **Rastro:** sign-in logs → filtro *Agent type* · audit logs → `agentType`, `blueprintId` → Log Analytics.

**Visualización:** a la izquierda, una barra de duración con un reloj al final. A la derecha, el icono `analytics/Log_Analytics_Workspaces.svg` y un recorte de la columna *Agent type* del portal (captura real, anotada).

---

### Slide 30 · Separador · Demo 4

| | |
|---|---|
| Tiempo | 35:00 (3 segundos) |
| Layout | Separador de demo, línea `entra` |

**En pantalla:**
- **DEMO 4**
- Cuando el agente se tuerce, y cuando Marta se va
- Controles

**Visualización:** D5 en miniatura con acceso condicional y ciclo de vida resaltados.

---

## Bloque 6 · Licencias, lo que llega y el lunes

### Slide 31 · Licencias

| | |
|---|---|
| Tiempo | 39:30–40:15 |
| Layout | Tabla de cuatro filas |

**En pantalla:** la tabla del guion (funcionalidad → qué hace falta). Pie: *Fuente: Microsoft Learn, noviembre de 2026. Gobierno y ejecución se facturan por separado.*

**Visualización:** la fila "Política de inactividad por defecto · **ninguna licencia**" en `ok`. Sin logos de licencias.

---

### Slide 32 · Lo que llega (Ignite 2026)

| | |
|---|---|
| Tiempo | 40:15–41:00 |
| Layout | Lista de cinco con etiqueta de estado |

**En pantalla:** las cinco novedades del guion, cada una con una etiqueta a la derecha: **PREVIEW** en gris o **DICIEMBRE** en `aviso`. Encabezado: *Diseña con lo que es GA. Prueba lo demás.*

**Visualización:** si en la demo 3 se saltó el beat 4, aquí va una captura del registro de Agent 365 con los tres agentes. Si no, no.

---

### Slide 33 · La checklist del lunes

| | |
|---|---|
| Tiempo | 41:00–42:00 |
| Layout | Cinco casillas grandes |

**En pantalla:**
- ☐ Revisa la política de inactividad y su buzón de fallback
- ☐ Exporta los agentes con un solo sponsor o con un sponsor que cambió de departamento
- ☐ Un blueprint por familia, con federated credential
- ☐ Antes de migrar en Foundry, exporta los roles de la identidad compartida
- ☐ Plantilla de CA: bloquear agentes de riesgo alto

**Construcción:** todas a la vez (es para hacer captura). Al terminar la frase ancla, transición a la slide 8 como fondo durante 3 segundos.

---

## Cierre

### Slide 34 · La frase

| | |
|---|---|
| Tiempo | 42:00–42:30 |
| Layout | `fondo-oscuro`, una frase |

**En pantalla:**
> **El control plane no pregunta con qué construiste el agente.**
> **Pregunta quién es, qué toca y quién responde por él.**

**Visualización:** las tres palabras **quién es**, **qué toca** y **quién responde** con los colores `entra`, `puerta-2` y `aviso`.

---

### Slide 35 · Recursos y QR

| | |
|---|---|
| Tiempo | 42:30–43:00 |
| Layout | QR grande a la izquierda + lista a la derecha |

**En pantalla:**
- QR de 400 px → página con la checklist, los cinco diagramas y el repositorio de `fs-triage-devoluciones`.
- Lista: Agent ID (Learn) · Acceso condicional para agentes · ID Protection: risky agents · Gobierno de identidades de agente · Identidad de agentes en Foundry · Agent ID en Copilot Studio.
- Contacto: LinkedIn · dataging.com

---

### Slide 36 · Q&A

| | |
|---|---|
| Tiempo | 43:00–50:00 |
| Layout | `fondo-oscuro` |

**En pantalla:** **Preguntas** · *Escríbelas en el chat*. En pequeño, abajo, el QR de la slide 35 para quien llegue tarde.

---

## Plan B (ocultas, al final del deck)

| Slide | Demo | Contenido |
|---|---|---|
| 37 | Demo 1 | 4 capturas anotadas: ficha del agente (blueprint, sponsor, owners vacíos) · sign-in logs con *Agent type* · Marta con *Department = e-commerce* · la tarjeta de la slide 15 |
| 38 | Demo 2 | 3 capturas: traza con el 403 · IAM con el rol solo en la identidad compartida · respuesta correcta tras el RBAC |
| 39 | Demo 3 | 4 capturas: blueprint con la federated credential · las tres líneas de `identity.py` · inicio de sesión con el blueprint padre · registro de Agent 365 con los tres agentes |
| 40 | Demo 4 | 4 capturas: CA-AG-01 · *Risky agents* con riesgo High · sign-in fallido con CA-AG-01 · correo del workflow de mover |

Cada slide de plan B lleva las capturas en cuadrícula 2 × 2, con las anotaciones en el color de la puerta correspondiente.
