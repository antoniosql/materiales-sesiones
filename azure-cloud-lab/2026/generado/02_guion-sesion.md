# Identidad, acceso y ciclo de vida de agentes con Microsoft Entra Agent ID — Guion

| | |
|---|---|
| Evento | Azure Cloud Lab 2026 · online · **jueves 3 de diciembre de 2026, 17:00 (hora peninsular)** |
| Formato | **50 minutos en directo, con demos y Q&A dentro** |
| Reparto | 43' de contenido + 7' de Q&A |
| Nivel | 300 |
| Público | Identidad y seguridad, arquitectos cloud, administradores de sistemas, DevOps |
| Idioma | Español |
| Escenario | FraSoHome, los mismos personajes del Bizz Summit (ver *Escenario* más abajo) |
| Slides | 36 + 4 de plan B. Detalle en `03_slides.md` · deck: `05_presentacion-entra-agent-id.pptx` |
| Diagramas | 5, en `diagramas/`. Instrucciones en `04_diagramas-drawio.md` |

> ⚠️ **Lee el Anexo C (*Por verificar*) antes de montar las demos.** Desde que se escribió el abstract (octubre) han cambiado dos cosas que afectan al guion. **Foundry:** en el modelo actual de agentes, cada agente nuevo nace con su propio blueprint y su propia identidad. La historia de "pierde permisos al publicarse" ahora se cuenta como lo que es: un agente que pasa de la identidad compartida del proyecto a una identidad propia. **Ignite 2026 (17 nov):** ha movido varias piezas de preview a GA y ha anunciado otras en preview. El guion ya lo incorpora, pero hay matices que conviene comprobar en el tenant la semana de la sesión.

## La tesis en una frase

> **"Un service principal es una llave. Un agente es alguien con llaves. Y alguien con llaves necesita a alguien que responda por él."**

## Los tres mensajes que tienen que sobrevivir a la sesión

1. **El modelo es nuevo y conviene aprenderlo bien.** Blueprint (la familia), identidad de agente (la instancia), cuenta de usuario de agente (cuando necesita ser "alguien" en M365). Y tres papeles humanos distintos: owner, sponsor y manager. **Se gobierna la plantilla; se responde por la instancia.**
2. **Los controles son los de siempre, pero con reglas distintas.** Los roles no viajan entre identidades. El acceso condicional para agentes solo bloquea. En un flujo en nombre de usuario, el sujeto es el usuario y no el agente. Un agente con API key se salta todo.
3. **El control más rentable es el ciclo de vida, no el acceso.** Sponsor obligatorio, política por inactividad, transferencia de sponsor y accesos con caducidad. Y la trampa: **un sponsor que cambió de equipo no dispara ninguna alarma**.

## La frase ancla

Es la misma del Bizz Summit, ahora con la palabra que Entra le pone. Se dice tres veces (min 7, min 34 y min 41):

> *"Un agente sin sponsor no es un agente: es una incidencia esperando fecha."*

Y la variante del cierre:

> *"Y un sponsor que cambió de equipo es una incidencia con la fecha ya pasada."*

---

## Escaleta

| Min | Bloque | Qué pasa | Slides | Demo |
|---|---|---|---|---|
| 00:00–02:00 | Apertura | Dos preguntas retóricas | 1–3 | — |
| 02:00–03:30 | Contrato | Quién soy, qué te llevas, FraSoHome en 20" | 4–5 | — |
| 03:30–08:00 | **1 · Por qué el service principal no aguanta** | Cuatro cosas que rompen el modelo | 6–8 | — |
| 08:00–13:30 | **2 · El modelo de Agent ID** | Blueprint, identidad, agent user, flujos y papeles humanos | 9–13 | — |
| 13:30–17:00 | 🎬 **Demo 1 · ¿Quién responde por este agente?** | Puerta 1: Copilot Studio | 14–15 | En vivo |
| 17:00–19:00 | **3 · Puerta 2: Foundry** | Identidad compartida frente a identidad propia | 16 | — |
| 19:00–22:30 | 🎬 **Demo 2 · El rol que no viaja** | 403 en directo, arreglo con RBAC | 17–18 | En vivo + clip de 20" |
| 22:30–24:30 | **4 · Puerta 3: el agente propio** | Blueprint de IT y federated credential | 19–20 | — |
| 24:30–28:30 | 🎬 **Demo 3 · Sin secretos** | Container Apps → token → Storage · los tres en Agent 365 | 21 | En vivo |
| 28:30–35:00 | **5 · Los controles de siempre, sobre un sujeto nuevo** | RBAC, acceso condicional, ID Protection, ciclo de vida, rastro | 22–29 | — |
| 35:00–39:30 | 🎬 **Demo 4 · Cuando el agente se tuerce y cuando Marta se va** | Bloqueo por riesgo · workflow de mover | 30 | Clip + en vivo |
| 39:30–42:00 | **6 · Licencias, lo que llega y el lunes** | Tabla de licencias, Ignite, checklist | 31–33 | — |
| 42:00–43:00 | Cierre | Frase final, recursos y QR | 34–35 | — |
| 43:00–50:00 | Q&A | Preguntas del chat | 36 | — |

Demos: **15'30"** sobre 43' de contenido (36 %). En una sesión online de nivel 300 ese es el ratio que mantiene a la gente: el chat se anima durante las demos, no durante las tablas.

### Puntos de control

| Checkpoint | Dónde debes estar | Si vas tarde |
|---|---|---|
| ⏱ **13:30** | Empezando la demo 1 | Recorta la slide 12 (plantilla frente a instancia) a una frase: ya sale en la demo 3 |
| ⏱ **24:30** | Empezando la demo 3 | Salta el beat 4 de la demo 3 (Agent 365): lo cuentas en la slide 32 |
| ⏱ **35:00** | Empezando la demo 4 | Fusiona las slides 25 y 26 (atributos e ID Protection) en una sola frase y entra en la demo |
| ⏱ **43:00** | En Q&A, hayas terminado o no | A las 42:00, ve directo a la frase de cierre y al QR. La checklist está en el QR |

---

## Antes de entrar (online)

- [x] Franja (jueves 3 dic, 17:00), formato en directo y plantilla del evento (`entrada/plantilla/AzureCloudLab2026.pptx`) confirmados.
- [ ] **Confirmar con la organización** la plataforma (Teams, StreamYard, YouTube…) y si hay moderador que lea el chat.
- [ ] **Tenant FraSoHome** con licencias de Agent 365 y Entra ID P1 o superior. Sin ellas no hay acceso condicional ni gobierno de agentes (ver slide 31). Vale una trial de M365 E7 o de Agent 365.
- [ ] **Montaje de las tres puertas** (Anexo B) terminado y probado **48 horas antes**, como mínimo. La política de inactividad y los workflows necesitan tiempo para enseñar algo.
- [ ] **Clips grabados:** demo 2 (éxito tras el RBAC, 20") y demo 4, beat 1 (bloqueo por riesgo, 60"). Con subtítulos quemados.
- [ ] **Capturas de plan B** para las cuatro demos (slides 37–40).
- [ ] **Perfiles de navegador separados:** *Nuria (admin)*, *Lucía (sponsor)* y *Marta*. Así no hay que cerrar sesión en directo.
- [ ] Zoom del navegador al **125 %**, terminal a **18 pt** como mínimo, notificaciones silenciadas y modo no molestar.
- [ ] **Una sola pantalla compartida**, con las ventanas abiertas en el orden del Anexo A. En online, cambiar de pantalla compartida a mitad de demo es lo que más ritmo se come.
- [ ] Al moderador, el **enlace del QR** (checklist + repositorio) para que lo pegue en el chat en el minuto 42.
- [ ] Revisar el **Anexo C** el lunes de la semana del evento.

---

# Apertura · 00:00 → 03:30

## 00:00–01:00 · Slide 1 → Slide 2 · El gancho, primera pregunta

Diez segundos con el título y pasas a la slide 2 sin presentarte.

Pregunta lanzada al aire: no se espera respuesta en el chat.

> *"Antes de presentarme, una pregunta. ¿Cuántos service principals hay en vuestro tenant? No hace falta que lo escribáis: haced la cuenta de cabeza. En la mayoría de tenants que veo, la cifra tiene cuatro dígitos, y casi nadie la sabe sin mirar."*

*(Pausa de dos segundos y sigue.)*

## 01:00–02:00 · Slide 3 · La segunda pregunta

> *"Segunda pregunta, y esta duele más: ¿de cuántos de esos sabéis quién responde? No quién los creó: quién responde hoy si mañana uno hace algo raro."*

*(Pausa de dos segundos. Tampoco se espera respuesta.)*

> *"Ese silencio lo llevamos arrastrando diez años con automatizaciones que hacían siempre lo mismo. Ahora multiplicad esa cifra por diez y dadle a cada uno la capacidad de decidir qué hace. Eso es lo que está pasando con los agentes. Y de eso va esta sesión."*

## 02:00–03:00 · Slide 4 · Quién soy y qué te llevas

Treinta segundos de quién soy, sin currículum:

> *"Soy Antonio Soto. Llevo veinticinco años con datos en empresa, soy MVP de Fabric y de Foundry y doy clase en universidades y escuelas de negocio. Hoy vengo como el que tiene que explicar en el comité por qué el agente de devoluciones tenía acceso a lo que no debía."*

Y el contrato, tres líneas:

1. Entender el modelo de identidad de agentes **lo bastante bien como para diseñarlo**, no solo para hacer clic.
2. Saber qué controles de los que ya tienes funcionan con agentes, **y cuáles se comportan distinto**.
3. Una checklist para el lunes.

## 03:00–03:30 · Slide 5 · FraSoHome en 20 segundos

> *"Todo lo que veáis hoy pasa en FraSoHome: retail de muebles y decoración, tres tiendas, e-commerce y fidelización. Y tres agentes que llegaron al directorio por tres puertas distintas: uno de Copilot Studio, uno de Foundry y uno que escribió un desarrollador y vive en un contenedor. Los tres tocan el mismo proceso: devoluciones."*

**Nota:** si en el chat hay gente del Bizz Summit, di *"algunos ya conocéis a Marta y a David; hoy los vemos desde Entra"*. Si no, no lo menciones.

---

# Bloque 1 · Por qué el service principal no aguanta · 03:30 → 08:00

## 03:30–05:00 · Slide 6 · La llave y el que tiene llaves

Slide de contraste, dos columnas:

| Service principal de siempre | Agente |
|---|---|
| Hace siempre lo mismo | **Decide qué hace** en cada ejecución |
| Actúa como sí mismo | **Actúa como sí mismo o en nombre de un usuario** |
| Lo crea IT, de uno en uno | **Se crea por cientos**, desde Copilot Studio, Foundry o un portátil |
| Vive lo que vive la aplicación | **Sobrevive a quien lo construyó** |

> *"Un service principal es una llave. Le das un rol, la metes en un pipeline y hace siempre lo mismo. Si algo va mal, miras qué hace el código.
> Un agente es alguien con llaves. Y con 'alguien' me refiero a que decide."*

## 05:00–07:00 · Slide 7 · Las cuatro cosas que rompen el modelo

Una fila por cosa, con la consecuencia práctica. **Este es el contenido; la slide 6 solo lo presenta.**

1. **Decide qué herramientas usa.** Los permisos ya no describen lo que hace, sino lo que *podría* hacer. *"El mínimo privilegio deja de ser una buena práctica y pasa a ser lo único que acota a un sistema que no controlas línea a línea."*
2. **Actúa en nombre de usuarios.** El mismo agente es dos sujetos distintos según el flujo: él mismo, o Álvaro, el Store Manager que le pregunta en Teams. *"Y eso cambia a quién se le aplica el acceso condicional, como veremos."*
3. **Se crea por cientos.** Copilot Studio le da identidad a cada agente nuevo. Foundry, a cada agente nuevo. *"El inventario ya no lo haces tú: te lo hace la plataforma. La pregunta es quién lo mira."*
4. **Sobrevive a quien lo construyó.** La app registration de 2019 que nadie se atreve a borrar es el precedente. *"Con agentes, ese problema llega en meses, no en años."*

## 07:00–08:00 · Slide 8 · Frase ancla (1.ª vez)

> *"Por eso Entra no se ha limitado a añadir un tipo de service principal. Ha añadido una figura humana obligatoria: el sponsor. Porque un agente sin sponsor no es un agente: es una incidencia esperando fecha."*

**Transición:**

> *"Vamos a ver el modelo. Cinco minutos de teoría que os van a ahorrar meses de malos diseños."*

---

# Bloque 2 · El modelo de Agent ID · 08:00 → 13:30

## 08:00–09:30 · Slide 9 · Blueprint → identidad → agent user ⭐

**La slide central de la sesión.** Es el diagrama D1. Vuelve a ella con el puntero en cada demo.

| Pieza | Qué es | Analogía para la sala |
|---|---|---|
| **Blueprint** (agent identity blueprint) | La plantilla de una familia de agentes. Tiene las credenciales, define permisos heredables y es donde se aplican políticas a toda la familia | La "clase" |
| **Blueprint principal** | Su representación en el tenant | — |
| **Identidad de agente** (agent identity) | La instancia en runtime. Es la que pide tokens y la que recibe roles de Azure | El "objeto" |
| **Cuenta de usuario de agente** (agent user) | Opcional. Cuando el agente tiene que *ser alguien* en M365: buzón, Teams, licencia | El "empleado digital" |

> *"Lo importante de esta slide son dos flechas. La primera: las credenciales viven en el blueprint, no en cada agente. La segunda: las políticas que pones sobre el blueprint las heredan todas sus identidades, incluidas las que todavía no existen."*

## 09:30–11:00 · Slide 10 · Tres flujos, tres sujetos distintos

| Flujo | Quién es el sujeto del token | A quién se le aplica el acceso condicional |
|---|---|---|
| **Autónomo** (app-only) | La identidad de agente | Al agente (o a su blueprint) |
| **En nombre de usuario** (OBO) | El usuario | **Al usuario**, no al agente |
| **Como usuario de agente** | La cuenta de usuario del agente | A la cuenta de usuario del agente |

> *"Apuntad la segunda fila, porque es la que más confunde. Cuando el Asistente de Devoluciones le responde a Álvaro en Teams, el token es de Álvaro. Si queréis controlar eso, la política va sobre Álvaro. La política del agente ahí no pinta nada."*

## 11:00–12:15 · Slide 11 · Owner, sponsor, manager

| | Owner | Sponsor | Manager |
|---|---|---|---|
| Para qué | Administración técnica | **Responsabilidad de negocio** | Jerarquía |
| ¿Obligatorio? | No | **Sí, al crear** identidades y blueprints | No |
| Puede | Cambiar credenciales y configuración, rehabilitar y restaurar | Deshabilitar, decidir renovaciones, pedir accesos | Pedir accesos para sus agentes |
| No puede | — | **Rehabilitar ni restaurar** lo que deshabilita | Modificar ni borrar |
| Puede ser un grupo | No | **Sí** (grupos de M365 o dinámicos, hasta 5) | No |

> *"El sponsor es la persona a la que llaman cuando el agente hace algo raro. Y fijaos en un detalle de diseño muy fino: el sponsor puede apagarlo, pero no puede volver a encenderlo. Para eso hace falta un owner o un administrador. Es un freno de emergencia, no un interruptor."*

## 12:15–13:00 · Slide 12 · Se gobierna la plantilla, se responde por la instancia

> *"Si os quedáis con una idea de diseño, que sea esta: un blueprint por familia de agentes, aprobado por IT, con su credencial y sus políticas. Y un sponsor por cada instancia. IT gobierna la plantilla; el negocio responde por la instancia."*

**Si vas tarde (checkpoint 13:30):** esta slide se dice en una frase y se pasa.

## 13:00–13:30 · Slide 13 · Las tres puertas

Diagrama D2. Las tres puertas al mismo directorio. **No lo expliques entero**: señala cada puerta y di que vamos a cruzarlas una a una.

> *"Copilot Studio usa un blueprint global de Microsoft. Foundry crea los suyos. Y para el agente propio, el blueprint lo hacemos nosotros. Tres puertas distintas que llevan a la misma lista. Empezamos por la primera."*

`⏱ CHECKPOINT 1 — 13:30, demo 1.`

---

# 🎬 Demo 1 · ¿Quién responde por este agente? · 13:30 → 17:00

**Puerta 1 · Copilot Studio** · Duración 3'30" · Riesgo bajo · Plan B: capturas (slide 37)

Slide 14 de separador durante 3 segundos, y a la ventana.

### Montaje

- Ventana 2: **Entra admin center** → *Agent ID* → *All agent identities*, ya filtrado por `FS-Copilot-Devoluciones`.
- Ventana 3: **Entra admin center** → *Users* → **Marta R.**, en la pestaña de propiedades.
- Ventana 4: **Sign-in logs**, filtrados por *Agent type = Agent Identity* y las últimas 24 h.

### Beat 1 · 1'00" · La ficha

Abres la identidad del Asistente de Devoluciones. Enseña, en este orden y sin desviarte:

1. **Blueprint:** *Microsoft Copilot Studio agent identity blueprint*, el blueprint global que Copilot Studio usa para todos sus agentes.
2. **Sponsor:** Marta R.
3. **Owners:** ninguno.
4. **Permisos:** los conectores aparecen como permisos de API sobre la identidad.

> *"Este agente se creó en marzo, cuando Copilot Studio todavía usaba app registrations. Desde mayo, todo agente nuevo nace con Agent ID y no hay forma de desactivarlo. Este lo migró Nuria en octubre. Y en la migración hizo lo razonable: puso a la creadora como sponsor."*

### Beat 2 · 1'00" · El rastro

Ventana 4. Sign-in logs con el filtro **Agent type**.

> *"Los agentes tienen su propio filtro en los logs de inicio de sesión: Agent Identity, Agent ID user, Blueprint. Aquí está el Asistente, pidiendo tokens cada vez que alguien le pregunta algo. Activo. Muy activo."*

Abre un evento y señala el blueprint padre. Sin más.

### Beat 3 · 1'00" · El giro

Ventana 3. Marta R. → **Department: e-commerce**. Manager: el responsable de e-commerce.

> *"Marta sigue en la empresa. Su cuenta está activa. Para Entra, este agente tiene sponsor y todo está en verde. Pero Marta pasó a e-commerce en julio. Nadie le dijo a este agente que su sponsor ya no trabaja en tiendas."*

### Beat 4 · 30" · El remate · Slide 15

Vuelves a PowerPoint: slide 15, la ficha resumida (sponsor activo ✅, departamento distinto ⚠️).

> *"Cuarenta personas de tienda usan este agente cada día. Y la persona que debe responder por él no sabe que lo es. Esto no lo detecta ninguna alerta, porque técnicamente no hay nada roto."*

*(Pausa.)*

> *"Guardad esto: lo arreglamos en la demo 4."*

**Si algo falla:** pasa a las capturas de la slide 37 sin anunciarlo y sigue los mismos cuatro beats.

---

# Bloque 3 · Puerta 2: Foundry · 17:00 → 19:00

## 17:00–19:00 · Slide 16 · Identidad compartida frente a identidad propia

| | Identidad compartida del proyecto | Identidad propia del agente |
|---|---|---|
| Cuándo | Agentes del modelo anterior y agentes sin publicar | Modelo actual: cada agente nace con la suya · Agentes publicados |
| Blueprint | Uno por proyecto | Uno por agente |
| Roles | **Los comparten todos los agentes del proyecto** | **Hay que asignarlos de nuevo** |

> *"Foundry tenía un atajo muy cómodo para desarrollar: todos los agentes de un proyecto compartían una identidad. Le dabas un rol una vez y funcionaban todos. El problema llega cuando el agente pasa a tener su propia identidad, al publicarlo o al migrarlo al modelo nuevo. La documentación lo dice con todas las letras: los roles no se transfieren."*

Y el segundo detalle, que es el que más horas cuesta:

> *"Solo dos tipos de herramienta se autentican con la identidad del agente: MCP y agente a agente. Y el audience del token es el del recurso final, storage.azure.com, no la URL del servidor MCP. Si os equivocáis ahí, el RBAC puede estar perfecto y aun así fallar."*

---

# 🎬 Demo 2 · El rol que no viaja · 19:00 → 22:30

**Puerta 2 · Foundry** · Duración 3'00" + 30" de slide · Riesgo medio · Plan B: capturas (slide 38) + clip de éxito

Slide 17 de separador.

### Montaje

- Ventana 5: **Foundry portal** → proyecto `fs-agentes-prj` → agente **`frasohome-returns`**, en el playground. Lleva la herramienta MCP `fs-devoluciones-mcp`, que lee las devoluciones online de un Storage Account.
- Ventana 6: **Azure portal** → `stfrasohomeops` → contenedor `devoluciones` → *Access control (IAM)* → *Role assignments*.
- Ventana 7: terminal con `az` ya autenticado como Nuria.
- Clip de 20": la misma pregunta respondida correctamente, con el reloj visible.

### Beat 1 · 40" · Funcionaba

> *"Este es frasohome-returns. En desarrollo contestaba perfectamente a cuántas devoluciones online hubo en iluminación la semana pasada. Lo hemos pasado a su identidad propia, que es lo que se hace antes de producción."*

Haces la pregunta en el playground:

```
¿Cuántas devoluciones online de iluminación tenemos registradas y por qué motivo?
```

La llamada a la herramienta falla: **403 AuthorizationPermissionMismatch** en la traza.

### Beat 2 · 50" · Por qué

Ventana 6. IAM del contenedor `devoluciones`:

- `Storage Blob Data Reader` → **la identidad compartida del proyecto** ✅
- La identidad nueva del agente → **nada**

> *"El rol está, pero asignado a otra identidad. Para Azure son dos sujetos distintos que no tienen nada que ver. El agente no ha perdido sus permisos: es que nunca fueron suyos."*

### Beat 3 · 1'00" · El arreglo, con mínimo privilegio

Ventana 7. Copias el `agentIdentityId` desde la ficha del agente en Foundry y lanzas:

```bash
az role assignment create \
  --assignee-object-id "<agentIdentityId>" \
  --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Reader" \
  --scope "/subscriptions/<sub>/resourceGroups/rg-frasohome-agents/providers/Microsoft.Storage/storageAccounts/stfrasohome<sufijo>/blobServices/default/containers/devoluciones"
```

> *"Fijaos en el scope: el contenedor, no la cuenta ni el grupo de recursos. Y un rol de datos, no de control. Ya que estamos asignando roles desde cero, hagámoslo bien."*

### Beat 4 · 30" · El resultado (clip)

> *"La propagación de RBAC no es instantánea, así que aquí tenéis la misma pregunta hace diez minutos, con el rol ya propagado."*

Pones el clip de 20". Responde bien.

## 22:00–22:30 · Slide 18 · La lección

Diagrama D3 (el rol que no viaja) con la checklist en tres líneas:

1. Antes de migrar o publicar, **exporta los roles de la identidad compartida**.
2. Reasígnalos al `agentIdentityId`, **con scope de recurso y roles de datos**.
3. Comprueba el **audience** de cada conexión MCP.

---

# Bloque 4 · Puerta 3: el agente propio · 22:30 → 24:30

## 22:30–23:45 · Slide 19 · El flujo sin secretos

Diagrama D4. Recórrelo con el puntero, en cinco pasos:

1. El contenedor tiene una **managed identity**.
2. La managed identity es la **credencial del blueprint** (federated credential). No hay secreto en ningún sitio.
3. El blueprint pide un token de intercambio **en nombre de una identidad concreta** (el parámetro `fmi_path`).
4. Con ese token, la identidad de agente pide **su** token para el recurso: Storage.
5. **En ese momento**, Entra evalúa el acceso condicional y el riesgo, y deja rastro en los logs.

> *"El paso cinco es la razón de todo. Cada vez que el agente pide un token, Entra puede decir que no. Con una API key, nadie puede decir que no."*

## 23:45–24:30 · Slide 20 · Qué credencial para el blueprint

| Credencial | ¿Producción? |
|---|---|
| Managed identity como federated credential | ✅ **La recomendada** |
| Certificado | ✅ Si el agente no corre en Azure |
| Secreto | ❌ **Solo desarrollo**, lo dice la propia documentación |
| API key del servicio | ❌ Se salta Entra entero |

> *"Y si el agente corre en AWS o GCP, también hay federación: la documentación tiene guías para los dos. Sin secretos no es solo para Azure."*

`⏱ CHECKPOINT 2 — 24:30, demo 3.`

---

# 🎬 Demo 3 · Sin secretos · 24:30 → 28:30

**Puerta 3 · Agente propio en Container Apps** · Duración 4'00" · Riesgo medio · Plan B: capturas (slide 39)

Slide 21 de separador.

### Montaje

- Ventana 8: **Entra admin center** → *Agent ID* → *Agent identity blueprints* → **`bp-frasohome-operaciones`**.
- Ventana 9: **VS Code** con `fs-triage-devoluciones/identity.py` (las 25 líneas que piden el token).
- Ventana 10: **Azure portal** → Container App `ca-fs-triage` → *Log stream*.
- Ventana 11: **Microsoft 365 admin center** → *Agents* → registro de agentes.

### Beat 1 · 1'00" · El blueprint de IT

Ventana 8. Enseña:

- Nombre: **FraSoHome · Agentes de operaciones**, creado por Nuria (IT).
- **Credenciales:** cero secretos, cero certificados. Una federated credential que confía en la managed identity `id-fs-triage`.
- **Sponsors:** el grupo *FraSoHome · Plataforma de agentes*.
- **Identidades hijas:** `fs-triage-devoluciones`, con **Lucía M.** (responsable de atención al cliente de e-commerce) como sponsor y **David L.** como owner.

> *"Fijaos en el reparto: David es owner porque es quien sabe cambiarlo; Lucía es sponsor porque es a quien le importa que funcione. Owner técnico, sponsor de negocio. Si son la misma persona, tenéis un problema cuando esa persona se vaya."*

### Beat 2 · 1'00" · El código

Ventana 9. Sin leerlo entero: señala tres líneas.

1. La petición del token de la managed identity (IMDS).
2. El `fmi_path` con el client ID de la identidad de agente.
3. El `scope` final: `https://storage.azure.com/.default`.

> *"No hay ningún secreto en este fichero, ni en variables de entorno ni en Key Vault. La credencial es la propia infraestructura."*

### Beat 3 · 1'00" · Funciona, y queda rastro

Ventana 10. *Log stream*: el agente procesa un correo del buzón de devoluciones y escribe la clasificación.

Cambia a los **Sign-in logs** (ventana 4): el inicio de sesión de `fs-triage-devoluciones`, con *Agent type = Agent Identity* y su **blueprint padre**.

### Beat 4 · 1'00" · Los tres juntos

Ventana 11. Registro de agentes de Agent 365.

**Los tres agentes de FraSoHome en la misma lista:** el de Copilot Studio, el de Foundry y el del contenedor. Con su identidad y su sponsor.

> *"Tres puertas distintas, una sola lista. Esto es lo que le enseñáis al CISO."*

*(Si vas tarde, este beat se salta y se cuenta en la slide 32.)*

---

# Bloque 5 · Los controles de siempre, sobre un sujeto nuevo · 28:30 → 35:00

## 28:30–29:00 · Slide 22 · El mapa

Diagrama D5. Cinco controles alrededor de la identidad del agente: RBAC, acceso condicional, ID Protection, ciclo de vida y rastro.

> *"Ninguno de estos controles es nuevo. Lo nuevo es que el sujeto se comporta distinto. Vamos uno a uno, centrándonos en lo que cambia."*

## 29:00–29:45 · Slide 23 · RBAC: tres reglas

1. **Asigna al `agentIdentityId`**, nunca a la identidad compartida ni a la managed identity del contenedor. La MI es la credencial; el sujeto es el agente.
2. **Scope de recurso**, no de suscripción.
3. **Roles de datos** (`Storage Blob Data Reader`, `Cosmos DB Built-in Data Reader`…), no `Contributor`. Y ojo: los de Cosmos DB se asignan con su propio comando.

## 29:45–31:15 · Slide 24 · Acceso condicional para agentes: lo que cambia ⭐

| | Identidades de agente | Cuentas de usuario de agente |
|---|---|---|
| Cómo se seleccionan | Todas · Seleccionadas · Por **atributo de seguridad** · Por **blueprint** | Todas · Seleccionadas · Por atributo (preview) |
| Condiciones | Solo **riesgo del agente** (preview) | Riesgo, entorno de ejecución, dispositivo, red (preview) |
| Controles | **Solo bloquear** | Bloquear, o exigir dispositivo compatible |

Y las cuatro trampas, en voz alta:

1. *"Solo bloquear. No hay MFA para un agente: no hay nadie al otro lado para resolverlo."*
2. *"En un flujo en nombre de usuario, el sujeto es el usuario. La política del agente no se aplica."*
3. *"Las políticas de 'Todos los usuarios' no incluyen las cuentas de usuario de agente. Si las queréis cubrir, hay que hacerlo de forma explícita."*
4. *"Un agente que usa API keys en lugar de tokens de Entra se salta todo esto. Es la mejor razón para el flujo sin secretos de antes."*

## 31:15–32:00 · Slide 25 · Atributos de seguridad: los carriles, convertidos en política

> *"En el Bizz Summit hablamos de carriles: Playground, Equipo, Producción, Enterprise. Aquí los convertimos en un atributo de seguridad personalizado sobre la identidad del agente. Y el acceso condicional se escribe contra el atributo, no contra cada agente."*

Dos políticas de ejemplo:

- **CA-AG-01** · Agentes con `FraSoHome.Carril = Produccion` y riesgo **alto** → **bloquear**.
- **CA-AG-02** · Agentes con `FraSoHome.Carril = Playground` → **bloquear** el acceso a los recursos de producción.

> *"Un agente nuevo que nace con el atributo correcto queda cubierto el primer día. Nadie tiene que acordarse de añadirlo a la política."*

## 32:00–32:45 · Slide 26 · ID Protection para agentes

- **Detecciones:** reconocimiento del directorio, picos de inicio de sesión, acceso a recursos fuera de lo habitual, credenciales nuevas añadidas al blueprint y usadas…
- **Learning mode** para los agentes recién creados, para no ahogarte en falsos positivos.
- **Acciones:** confirmar comprometido, confirmar seguro, descartar o deshabilitar.
- **En OBO**, el riesgo se atribuye al usuario, no al agente.

> *"La acción que más vais a usar al principio es 'confirmar comprometido'. Sube el riesgo a alto al momento. Y si tenéis la política CA-AG-01, el agente se queda fuera en su siguiente petición de token. Lo vais a ver en dos minutos."*

## 32:45–33:45 · Slide 27 · El ciclo de vida: el control más rentable

Línea temporal grande:

> **Día 0** · sin tokens → **Día 60** · aviso a sponsors y owners → **Día 90** · se deshabilita → **Día 455** · se borra

> *"Esta es la política por defecto. Inactividad significa que no ha pedido tokens, no que no haya consumido modelo. Y no necesita licencia."*

Y por encima, las políticas personalizadas:

- El sponsor **reconfirma** cada N días (entre 30 y 730) que el agente sigue haciendo falta.
- **Mínimo de sponsors**: un agente con un solo sponsor queda marcado.
- Acción: deshabilitar, borrar o las dos.

> *"Para mí, la reconfirmación periódica del sponsor es la revisión de acceso de un agente. No es una campaña de revisión de accesos al uso: es alguien con nombre y apellidos diciendo cada seis meses 'sí, esto sigue haciendo falta'."*

## 33:45–34:30 · Slide 28 · Cuando el sponsor se mueve (frase ancla, 2.ª vez)

Tareas de Lifecycle Workflows para sponsors, disponibles en workflows de **mover** y de **leaver**:

| Tarea | Mover | Leaver |
|---|---|---|
| Avisar al manager | ✅ | ✅ |
| Avisar a los co-sponsors | ✅ | ✅ |
| Transferir los sponsorships al manager | ⚠️ Mi opinión: no | ✅ |

> *"Mi recomendación es concreta: en un leaver, transferid al manager. En un mover, no: avisad. Si Marta pasa a e-commerce y transferís, el agente de tiendas acaba con el jefe de e-commerce como sponsor. Habéis cambiado una incidencia por otra."*

> *"Porque, insisto, un agente sin sponsor no es un agente: es una incidencia esperando fecha."*

## 34:30–35:00 · Slide 29 · Caducidad y rastro

Dos cosas en una slide:

- **Access packages para agentes:** los accesos se piden con justificación (lo hace el propio agente por Graph, el sponsor o un administrador), con aprobación y **fecha de fin**. El sponsor recibe el aviso antes de que caduque.
- **Rastro:** en los logs de inicio de sesión, el filtro *Agent type*; en los de auditoría, `agentType` y `blueprintId`. Todo con destino a Log Analytics.

`⏱ CHECKPOINT 3 — 35:00, demo 4.`

---

# 🎬 Demo 4 · Cuando el agente se tuerce y cuando Marta se va · 35:00 → 39:30

**Controles** · Duración 4'30" · Riesgo alto en el beat 1 (propagación) → **beat 1 grabado** · Plan B: capturas (slide 40)

Slide 30 de separador.

### Montaje

- Clip de 60" del beat 1 (grabado con el reloj visible).
- Ventana 12: **Entra** → *Conditional Access* → política **CA-AG-01**, abierta.
- Ventana 13: **Entra** → *ID Governance* → *Lifecycle Workflows* → workflow **LW-Mover-Sponsors**.
- Ventana 14: **Outlook web**, perfil de navegador del manager de Marta (Jorge P., director de operaciones de tienda) **o** del co-sponsor.
- Ventana 15: **Entra** → identidad `FS-Copilot-Devoluciones` → *Sponsors*.

### Beat 1 · 1'30" · El agente se tuerce (clip)

Primero, ventana 12 en directo, 20 segundos: CA-AG-01. Agentes con `Carril = Produccion` · riesgo alto · **bloquear**.

Luego, el clip de 60":

1. Nuria abre *Risky agents* → `fs-triage-devoluciones` → **Confirm compromised**.
2. Riesgo: **High**.
3. Reinicio de la revisión del Container App, para forzar un token nuevo.
4. El log stream muestra el error al pedir el token.
5. Sign-in logs: **Failure**, con CA-AG-01 aplicada.

> *"Nadie ha tocado el agente, ni su código, ni su contenedor. Se ha quedado fuera porque la identidad dijo que no. Y para volver a dejarlo entrar hace falta una decisión explícita: confirmar seguro o rehabilitarlo."*

### Beat 2 · 1'30" · Marta se va de tiendas

Ventana 13. **LW-Mover-Sponsors**: disparador por cambio de *Department*. Tareas: avisar al manager y avisar a los co-sponsors. **Sin transferencia**, como decíamos en la slide 28.

*Run on demand* para Marta R.

Ventana 14. Llega el correo: *"Se ha producido un cambio en el sponsor del agente FS-Copilot-Devoluciones…"*.

> *"El correo llega a alguien de tiendas que puede decidir. Que es exactamente lo que no pasó en julio."*

### Beat 3 · 1'00" · El arreglo de verdad

Ventana 15. Sponsors de `FS-Copilot-Devoluciones`:

- Quitas a Marta R.
- Añades a **Jorge P.** (persona) y al grupo **FraSoHome · Responsables de tienda** (grupo de M365).

> *"Persona más grupo. La persona da la cara; el grupo hace que el sponsor sobreviva al siguiente cambio de organigrama."*

### Beat 4 · 30" · El remate

> *"Recapitulemos: la demo 1 empezó con un agente activo, con sponsor, todo en verde, y nadie respondiendo por él. Ahora tiene sponsor de verdad, un workflow que avisa cuando alguien se mueve y una política que lo deja fuera si se tuerce. Nada de esto requiere tocar el agente."*

---

# Bloque 6 · Licencias, lo que llega y el lunes · 39:30 → 42:00

## 39:30–40:15 · Slide 31 · Licencias, sin rodeos

| Funcionalidad | Qué hace falta (Learn, nov 2026) |
|---|---|
| Política de inactividad por defecto | **Ninguna licencia** |
| Acceso condicional para agentes | M365 E7, **o** Agent 365 + Entra ID P1 (o M365 E3) |
| Tareas de sponsor, access packages, políticas de ciclo de vida personalizadas | M365 E7, **o** Agent 365 + Entra ID P1 (o M365 E3) |
| ID Protection para agentes | Requerirá Agent 365 ("pronto", según Learn) |

> *"Gobierno y ejecución se facturan por separado. Que no os pillen prometiendo lo que la licencia no cubre."*

## 40:15–41:00 · Slide 32 · Lo que llega (Ignite, 17 de noviembre)

Cinco líneas, todas con su estado:

- **Descubrimiento de agentes locales** (Claude Code, Codex, GitHub Copilot CLI… hasta 60 tipos) con Agent ID asignado · *preview*
- **Agent ID para plataformas conectadas** (Bedrock AgentCore, Vertex AI, Databricks, Snowflake, Salesforce…) · *preview*, con despliegue hasta diciembre
- **Riesgo dinámico del agente** en Agent 365 · *preview*
- **Acceso condicional para agentes asistivos**: separar a la persona del agente local que actúa por ella · *preview*
- **Action Center** en Agent 365 para agentes inactivos y sin propietario · *preview en diciembre*

> *"El agente de David nació en su portátil. Con el descubrimiento de agentes locales, ya entonces habría aparecido en el inventario. Pero es preview: diseñad con lo que es GA y probad lo demás."*

## 41:00–42:00 · Slide 33 · La checklist del lunes (frase ancla, 3.ª vez)

1. **Revisa la política de inactividad** y a quién notifica cuando no hay sponsor.
2. **Exporta las identidades de agente con un solo sponsor**, o con un sponsor que haya cambiado de departamento en los últimos seis meses. Esa lista es tu backlog.
3. **Un blueprint por familia** de agentes propios, con federated credential. Ningún secreto.
4. **Antes de migrar un agente de Foundry**, exporta los roles de la identidad compartida.
5. **Activa la plantilla de acceso condicional** que bloquea agentes de riesgo alto.

> *"Porque, como llevo cuarenta minutos diciendo, un agente sin sponsor no es un agente: es una incidencia esperando fecha. Y un sponsor que cambió de equipo es una incidencia con la fecha ya pasada."*

---

# Cierre · 42:00 → 43:00

## Slide 34 · La frase

> **"El control plane no pregunta con qué construiste el agente. Pregunta quién es, qué toca y quién responde por él."**

*(Es la frase del cierre del Bizz Summit. Si alguien del chat la reconoce, mejor: es la continuación.)*

## Slide 35 · Recursos y QR

> *"En el QR tenéis la checklist, los diagramas y el repositorio con el agente del contenedor. Lo pega ahora el moderador en el chat."*

`⏱ CHECKPOINT 4 — 43:00, Q&A.`

---

# Q&A · 43:00 → 50:00 · Slide 36

En online, las preguntas llegan por el chat a lo largo de toda la sesión. **Pide al moderador que las agrupe** y que te lea primero las que más se repiten.

### Las que van a caer

| Pregunta | Respuesta en una línea |
|---|---|
| *"¿Agent ID sustituye a las managed identities?"* | No. La managed identity es la **credencial** del blueprint; la identidad de agente es el **sujeto** que recibe los roles |
| *"¿Tengo que migrar mis service principals de automatizaciones?"* | No. Un pipeline que hace siempre lo mismo sigue siendo una workload identity. Agent ID es para lo que decide |
| *"¿Puedo exigir MFA o dispositivo a un agente?"* | A una identidad de agente, no: solo bloquear. A una cuenta de usuario de agente, dispositivo compatible si corre en un endpoint gestionado (p. ej. Windows 365 for Agents) |
| *"¿Y los agentes de Copilot Studio antiguos?"* | Usan app registrations. Se migran desde el Power Platform admin center, con PowerShell o por API. Revisad el sponsor al migrar |
| *"¿Funciona con agentes en AWS o GCP?"* | Sí, con federación (hay guías para los dos). Y desde Ignite, en preview, identidad automática para varias plataformas conectadas |
| *"¿ID Protection ya detecta riesgo en agentes?"* | Las detecciones existen, pero comprobad su estado en vuestro tenant. "Confirmar comprometido" funciona siempre y es lo que habéis visto en la demo |
| *"¿Cuánto cuesta?"* | La política por defecto, nada. Acceso condicional y gobierno: Agent 365 + P1, o E7 (slide 31) |
| *"¿Hay modo report-only para las políticas de agentes?"* | *(Comprobar antes; ver Anexo C)*. Si no lo hay, empezad por un atributo que solo tengan dos agentes de prueba |

**Si no hay preguntas**, haz tú esta:

> *"Os hago la que me hacen siempre: si solo tengo una hora el lunes, ¿qué hago? Exportad las identidades de agente y cruzad sus sponsors con los cambios de departamento de los últimos seis meses. Esa lista os va a sorprender."*

**Si alguien se enroca** con un caso muy particular: *"te contesto por LinkedIn, que es muy específico y hay más preguntas en el chat"*.

---

# Plan B por demo

| Demo | Qué falla típicamente | Plan B |
|---|---|---|
| 1 | Nada; es solo lectura | Capturas en la slide 37, mismos cuatro beats |
| 2 | El playground tarda o la traza no se ve | Capturas en la slide 38 + el clip de 20" |
| 3 | El contenedor está parado o el registro de Agent 365 tarda | Capturas en la slide 39. Arranca el contenedor 30' antes |
| 4 | La propagación del riesgo o del workflow | El beat 1 ya va grabado. Beat 2: captura del correo. Beat 3 siempre en directo |

# Recortes si vas tarde, por orden

1. Slide 12 (plantilla frente a instancia) → una frase.
2. Demo 3, beat 4 (Agent 365) → se cuenta en la slide 32.
3. Slides 25 y 26 (atributos e ID Protection) → una frase cada una; la demo 4 las enseña.
4. Slide 32 (Ignite) → solo la primera línea.
5. Demo 4, beat 3 → contado, sin ejecutarlo.

**Nunca se recortan:** la slide 9 (el modelo), la demo 1, la slide 24 (acceso condicional) ni la frase de cierre.

---

# Escenario FraSoHome de esta sesión

Hereda el del Bizz Summit (`bizz-summit-2026/escenario-frasohome.md`). Lo que cambia o se añade está marcado como **NUEVO**.

## Personas

| Persona | Rol | Aparece en |
|---|---|---|
| **Álvaro G.** | Store Manager de MAD01 (Gran Vía) | Slide 10: el usuario del flujo OBO |
| **Marta R.** | Operaciones de Tienda → e-commerce (julio de 2026). Sponsor del Asistente de Devoluciones | Demos 1 y 4 |
| **Nuria S.** | Administradora de Entra y M365 | Todas las demos (es quien opera) |
| **David L.** | Desarrollador de e-commerce. **Owner** de `fs-triage-devoluciones` | Demo 3 |
| **Lucía M.** · **NUEVO** | Responsable de Atención al Cliente de e-commerce. **Sponsor** de `fs-triage-devoluciones` | Demo 3 |
| **Jorge P.** · **NUEVO** | Director de Operaciones de Tienda. Antiguo manager de Marta y nuevo sponsor del Asistente | Demo 4 |

## Los tres agentes

| | Puerta 1 · Copilot Studio | Puerta 2 · Foundry | Puerta 3 · Agente propio |
|---|---|---|---|
| Nombre | `FS-Copilot-Devoluciones` (Asistente de Devoluciones FraSoHome) | `frasohome-returns` (del repo `frasohome-agents-foundry`) | `fs-triage-devoluciones` |
| Blueprint | *Microsoft Copilot Studio agent identity blueprint* (global) | El del agente, creado por Foundry | **`bp-frasohome-operaciones`** · *FraSoHome · Agentes de operaciones* (de IT) · **NUEVO** |
| Credencial | La gestiona Microsoft | La gestiona Foundry (federada con la MI del proyecto) | **Federated credential** sobre la MI `id-fs-triage` |
| Sponsor | Marta R. → Jorge P. + grupo *Responsables de tienda* | Grupo *FraSoHome · Plataforma de agentes* | Lucía M. |
| Owner | — | — | David L. |
| Flujo principal | **OBO** (responde a usuarios en Teams) | **Autónomo**, vía MCP | **Autónomo** |
| Recursos de Azure | — | `stfrasohomeops/devoluciones` (lectura) | `stfrasohomeops/buzon-devoluciones` (lectura) y `triage-resultados` (escritura) |
| Atributo `FraSoHome.Carril` | `Produccion` | `Produccion` | `Produccion` |
| Demo | 1 y 4 | 2 | 3 y 4 |

**Por qué el Asistente se migró y no nació con Agent ID:** se creó el 17 de marzo de 2026, cuando Copilot Studio aún usaba app registrations. Copilot Studio da Agent ID automático a los agentes nuevos **desde mayo de 2026**. Nuria lo migró en octubre desde el Power Platform admin center y puso a la creadora como sponsor.

---

# Anexo A · Orden de ventanas (una sola pantalla compartida)

| # | Ventana | Perfil | Demo |
|---|---|---|---|
| 1 | PowerPoint en modo presentador | — | Todas |
| 2 | Entra → Agent ID → `FS-Copilot-Devoluciones` | Nuria | 1 |
| 3 | Entra → Users → Marta R. | Nuria | 1 |
| 4 | Entra → Sign-in logs (filtro Agent type) | Nuria | 1 y 3 |
| 5 | Foundry → `fs-agentes-prj` → `frasohome-returns` | Nuria | 2 |
| 6 | Azure → `stfrasohomeops` → IAM del contenedor | Nuria | 2 |
| 7 | Terminal `az` (18 pt) | Nuria | 2 |
| 8 | Entra → Blueprints → `bp-frasohome-operaciones` | Nuria | 3 |
| 9 | VS Code → `identity.py` | — | 3 |
| 10 | Azure → `ca-fs-triage` → Log stream | Nuria | 3 |
| 11 | M365 admin center → Agents | Nuria | 3 |
| 12 | Entra → Conditional Access → CA-AG-01 | Nuria | 4 |
| 13 | Entra → Lifecycle Workflows → LW-Mover-Sponsors | Nuria | 4 |
| 14 | Outlook web | Jorge P. | 4 |
| 15 | Entra → `FS-Copilot-Devoluciones` → Sponsors | Nuria | 4 |
| 16 | Carpeta con clips y capturas | — | Emergencias |

# Anexo B · Montaje del tenant (resumen)

> Los scripts están en [`../agent-id-demos/`](../agent-id-demos/) (Bicep + CLI `agentid`), con la guía completa en `agent-id-demos/DESPLIEGUE.md`. `agentid demo2 comando` imprime este comando con los IDs reales, y `agentid ensayo reiniciar` deja las cuatro demos como al principio. Los nombres reales de los recursos son los de `config/escenario.yaml` (p. ej. `rg-frasohome-agents` y `stfrasohome<sufijo>` en lugar de `stfrasohomeops`).

1. **Licencias:** Agent 365 + Entra ID P1 (o trial de M365 E7) para Nuria, Lucía, Jorge y Marta.
2. **Usuarios y grupos:** las seis personas, con *Department* y *Manager* coherentes con el escenario. Grupos de M365 *FraSoHome · Plataforma de agentes* y *FraSoHome · Responsables de tienda*.
3. **Atributo de seguridad personalizado:** conjunto `FraSoHome`, atributo `Carril` con los valores `Playground`, `Equipo`, `Produccion` y `Enterprise`. Asignarlo a las tres identidades.
4. **Puerta 1:** `FS-Copilot-Devoluciones` creado **antes** de que Copilot Studio active Agent ID para agentes nuevos, o directamente con Agent ID (y entonces se cuenta la migración en la slide, sin enseñarla). Sponsor: Marta R. Ejecutar el Asistente en Teams varias veces el día anterior para que haya inicios de sesión.
5. **Puerta 2:** proyecto `fs-agentes-prj`, agente `frasohome-returns` con la herramienta MCP `fs-devoluciones-mcp` (Container App) y auth `AgenticIdentityToken`, con audience `https://storage.azure.com`. `Storage Blob Data Reader` sobre el contenedor `devoluciones` **asignado solo a la identidad compartida del proyecto**. Ver el punto 1 del Anexo C.
6. **Puerta 3:** blueprint `bp-frasohome-operaciones` con federated credential sobre la MI `id-fs-triage`. Identidad `fs-triage-devoluciones` con Lucía como sponsor y David como owner. Container App `ca-fs-triage` con esa MI. Roles de datos sobre los dos contenedores. El código del flujo de token sigue la documentación del flujo autónomo de Agent ID.
7. **Acceso condicional:** CA-AG-01 y CA-AG-02 activas. Comprobar el bloqueo con un agente de prueba **antes** de grabar el clip.
8. **Lifecycle Workflows:** LW-Mover-Sponsors (disparador: cambio de *Department*; tareas: avisar al manager y avisar a los co-sponsors). Política de inactividad por defecto activa, con buzón de fallback.
9. **Grabar** los dos clips y las capturas de plan B.

# Anexo C · Por verificar (la semana del evento)

| # | Qué | Por qué importa | Fuente |
|---|---|---|---|
| 1 | **Foundry:** en el modelo actual, crear un agente le da blueprint e identidad propios. El salto "identidad compartida → identidad propia" ocurre con agentes del modelo anterior (o al publicarlos). Comprobar si todavía se puede crear un agente con la identidad compartida del proyecto. | Es la demo 2. Si ya no se puede reproducir, se cuenta con el agente legacy de `frasohome-agents-foundry` o se monta un "antes" en capturas | Learn: *Agent identities in Foundry* (actualizado en nov 2026) |
| 2 | **Copilot Studio:** Agent ID automático para agentes nuevos **desde mayo de 2026** (Learn). El guion del Bizz Summit decía julio | Coherencia con lo que dijiste en el Bizz Summit | Learn: *Entra Agent IDs for Copilot Studio agents* |
| 3 | **Tarea "Transferir sponsorships al manager" en un mover:** ¿al manager antiguo o al nuevo? | Sostiene la recomendación de la slide 28 | Learn: *Agent sponsor tasks* (no lo aclara) |
| 4 | **Política de inactividad:** GA según el blog de Ignite (17 nov); Learn seguía diciendo preview el 19 nov. Confirmar también si viene activada por defecto o hay que activarla | Slide 27 y checklist | Blog de Entra en Ignite · Learn |
| 5 | **ID Protection para agentes:** Learn decía que las detecciones estaban "offline". Comprobar que "Confirm compromised" sube el riesgo y que CA-AG-01 bloquea | Es el beat 1 de la demo 4 | Learn: *Risky agents* |
| 6 | **Report-only** en políticas de acceso condicional para agentes | Respuesta del Q&A | Learn no lo documenta |
| 7 | Que el **registro de Agent 365** muestre un agente de blueprint propio sin onboarding adicional | Demo 3, beat 4 | — |
| 8 | **Revisiones de acceso (access reviews)** sobre identidades de agente: Learn no las documenta para agentes. El guion las sustituye por la reconfirmación del sponsor y la caducidad de los access packages | El abstract menciona "revisiones de acceso" | Learn: *Agent ID governance overview* |
| 9 | Si `agentType` y `blueprintId` llegan a las tablas `SigninLogs` y `AuditLogs` de Log Analytics, para dar una consulta KQL en el handout | Slide 29 | Learn: *Sign-in and audit logs for agents* |
| 10 | Que se pueda seleccionar **Azure Storage** como recurso en CA-AG-02 (necesita enterprise app en el tenant) | Slide 25 | Learn: *Target agent identities in CA* |
| 11 | **Licencias** de ID Protection para agentes ("pronto requerirá Agent 365") | Slide 31 | Learn: *Risky agents* |

# Referencias para las notas del orador

- [Microsoft Entra Agent ID — What's new](https://learn.microsoft.com/en-us/entra/agent-id/whats-new-agent-id)
- [Owners, sponsors and managers for agents](https://learn.microsoft.com/en-us/entra/agent-id/agent-owners-sponsors-managers)
- [Autonomous agent authentication and authorization flow](https://learn.microsoft.com/entra/agent-id/autonomous-agent-authentication-authorization-flow)
- [Conditional Access for agents](https://learn.microsoft.com/entra/identity/conditional-access/agent-id) · [Target agent identities in Conditional Access](https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-target-agent-identities)
- [ID Protection: risky agents](https://learn.microsoft.com/en-us/entra/id-protection/concept-risky-agents)
- [Agent ID governance overview](https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview) · [Agent sponsor tasks in Lifecycle Workflows](https://learn.microsoft.com/en-us/entra/id-governance/agent-sponsor-tasks) · [Access packages for agents](https://learn.microsoft.com/en-au/Entra/agent-id/agent-access-packages)
- [Sign-in and audit logs for agents](https://learn.microsoft.com/th-th/entra/agent-id/sign-in-audit-logs-agents)
- [Agent identities in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-identity)
- [Entra Agent IDs for Copilot Studio agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-use-entra-agent-identities)
- [Microsoft Entra en Ignite 2026](https://techcommunity.microsoft.com/blog/microsoft-entra-blog/ai-is-changing-access-see-how-microsoft-entra-helps-you-stay-ahead-/4556456) · [What's new in Agent 365: Ignite 2026](https://techcommunity.microsoft.com/blog/agent-365-blog/whats-new-in-microsoft-agent-365-ignite-2026/4571753)
- [Política de inactividad: 60 / 90 / 455 días](https://www.beri.net/article/microsoft-entra-ignite-2026-agent-id-lifecycle-policy-60-day-inactivity-notice-90-day-disable-local-agent-discovery-claude-code-codex-mcp-firewall-preview)
