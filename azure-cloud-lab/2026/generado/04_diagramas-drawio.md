# Diagramas en draw.io — Entra Agent ID · Azure Cloud Lab 2026

Cinco diagramas para las slides 9, 13, 18, 19 y 22 (ver `03_slides.md`). Cada uno tiene su `.drawio` editable y su `.png` de referencia en `diagramas/`, con los iconos oficiales colocados y los colores del sistema visual aplicados. Este documento explica cómo están construidos, para retocarlos o rehacerlos desde cero.

| Diagrama | Fichero | Slide | Qué cuenta |
|---|---|---|---|
| D1 | `D1-modelo-agent-id.drawio` | 9 (y 12 reducido) | Blueprint → identidades → cuenta de usuario de agente, credencial y papeles humanos |
| D2 | `D2-tres-puertas.drawio` | 13 (y separadores 14, 17 y 21) | Los tres agentes de FraSoHome llegan a Entra por puertas distintas |
| D3 | `D3-rol-que-no-viaja.drawio` | 18 | Identidad compartida con rol frente a identidad propia sin rol (403) |
| D4 | `D4-flujo-sin-secretos.drawio` | 19 | Flujo de token del agente propio: MI → blueprint → identidad → Storage |
| D5 | `D5-mapa-controles.drawio` | 22 (y miniatura en 23–30) | Los cinco controles alrededor de la identidad del agente |

La línea temporal del ciclo de vida (slide 27) **no** va en draw.io: se hace nativa en PowerPoint para animarla.

---

## 1. Preparación

### Dónde abrirlos

Funcionan sin instalar nada en **draw.io desktop**, en **app.diagrams.net** y en la extensión **Draw.io Integration** de VS Code. Los iconos se cargan desde la librería que trae draw.io (`img/lib/azure2/...`), así que no hay que importar nada para abrirlos.

### Activar la librería de iconos oficiales

1. Panel izquierdo → **+ Más formas** (*More Shapes*).
2. En **Networking**, marca **Azure** y aplica.
3. Aparecen las categorías *Azure / Identity*, *Azure / Security*, *Azure / AI + Machine Learning*, *Azure / Power Platform*, etc.
4. Atajo: el buscador de formas encuentra los iconos por nombre (`Entra`, `Conditional Access`, `Foundry`, `Copilot`).

Si un icono no aparece en el panel, el método infalible es pegar su estilo: selecciona una forma cualquiera → **Editar estilo** (Ctrl+E) → pega la línea de estilo de la tabla de abajo.

### Fuente

Los ficheros usan **Segoe UI**. Si exportas desde un equipo sin ella, draw.io la sustituye; en Windows no hay problema.

---

## 2. Catálogo de iconos

Todas las rutas están **comprobadas contra el repositorio oficial de draw.io** (`jgraph/drawio`, noviembre de 2026). Son los iconos oficiales de Microsoft que draw.io empaqueta.

Estilo base, al que solo cambia la ruta final:

```
image;aspect=fixed;html=1;points=[];align=center;verticalLabelPosition=bottom;verticalAlign=top;fontSize=13;fontFamily=Segoe UI;image=img/lib/azure2/<RUTA>
```

| Concepto en la sesión | Icono oficial | `<RUTA>` |
|---|---|---|
| Microsoft Entra ID / **identidad de agente** | Microsoft Entra ID | `other/Entra_Identity.svg` |
| **Blueprint** (es un objeto aplicación) | App registrations | `identity/App_Registrations.svg` |
| **Blueprint principal** (service principal) | Enterprise applications | `identity/Enterprise_Applications.svg` |
| **Cuenta de usuario de agente**, sponsor, persona | Users | `identity/Users.svg` |
| Grupo sponsor | Groups | `identity/Groups.svg` |
| **Managed identity** (credencial del blueprint) | Managed Identities (Entra) | `identity/Entra_Managed_Identities.svg` |
| **Acceso condicional** | Conditional Access | `security/Conditional_Access.svg` |
| **ID Protection** | Entra ID Protection | `identity/Entra_ID_Protection.svg` |
| **Ciclo de vida** / ID Governance | Identity Governance | `identity/Identity_Governance.svg` |
| **RBAC** / roles | Custom Azure AD Roles | `identity/Custom_Azure_AD_Roles.svg` |
| **Rastro** / logs | Log Analytics Workspaces | `analytics/Log_Analytics_Workspaces.svg` |
| Global Secure Access (si hablas de Ignite) | Entra Global Secure Access | `identity/Entra_Global_Secure_Access.svg` |
| **Copilot Studio** (puerta 1) | Copilot Studio | `power_platform/CopilotStudio.svg` |
| **Foundry Agent Service** (puerta 2, identidad propia) | Foundry Agent Service | `ai_machine_learning/Foundry_Agent_Service.svg` |
| **Proyecto de Foundry** (identidad compartida) | Foundry Project | `ai_machine_learning/Foundry_Project.svg` |
| **Container Apps** (puerta 3) | Container App | `other/Worker_Container_App.svg` |
| Entorno de Container Apps | Container Apps Environments | `other/Container_App_Environments.svg` |
| **Storage Account** | Storage Accounts | `storage/Storage_Accounts.svg` |
| Key Vault (para decir que *no* se usa) | Key Vaults | `security/Key_Vaults.svg` |

### Lo que no tiene icono oficial

- **Microsoft Agent 365**: no está en la librería de draw.io. **No inventes logo.** Va como caja de texto con borde `#0078D4` y el texto *Registro de agentes · Microsoft Agent 365*. Si quieres un icono, búscalo en los paquetes oficiales de Microsoft: *Azure architecture icons* (learn.microsoft.com/azure/architecture/icons) y *Microsoft 365 architecture icons and templates* (learn.microsoft.com/microsoft-365/solutions/architecture-icons-templates). Impórtalo con **Archivo → Importar → SVG** solo si lo encuentras ahí.
- **Microsoft Teams** y **Outlook**: no hacen falta en ningún diagrama. Si los necesitas, mismo criterio: paquete oficial de Microsoft 365 o texto.

---

## 3. Convenciones comunes

### Colores (los mismos que en las slides)

| Token | Hex | Dónde |
|---|---|---|
| `entra` | `#0078D4` | Contenedores de Entra, flechas de herencia y de token |
| `entra_bg` | `#EAF3FB` | Relleno de contenedores de Entra |
| `puerta-1` | `#0F7B6C` (relleno `#E6F2F0`) | Copilot Studio |
| `puerta-2` | `#6B4FBB` (relleno `#F0ECF9`) | Foundry |
| `puerta-3` | `#CA5010` (relleno `#FBEEE6`) | Agente propio |
| `ok` | `#107C10` | Rol concedido, acceso correcto |
| `aviso` | `#C19C00` (relleno `#FBF5DC`) | Sponsor, cosas técnicamente válidas pero mal |
| `bloqueo` | `#C4314B` | 403, bloqueo, riesgo |
| `gris` | `#605E5C` (relleno `#F3F2F1`) | Secundario, notas, fuentes |

### Formas

- **Contenedores:** rectángulo redondeado (`arcSize=6`), borde de 2 px del color de su ámbito, relleno claro.
- **Icono + etiqueta como grupo:** cada icono va agrupado con su texto debajo (Ctrl+G). **Los conectores se enganchan al grupo** cuando entran o salen por arriba o por abajo, y **al icono** cuando lo hacen por un lado. Así ninguna flecha atraviesa un texto.
- **Conectores:** ortogonales con esquinas redondeadas (`edgeStyle=orthogonalEdgeStyle;rounded=1`). 3 px para la flecha principal del mensaje, 2 px para los flujos y 1,5 px para el resto. Discontinuo (`dashed=1;dashPattern=6 4`) para lo que es *posible*, *futuro* o *roto*.
- **Etiquetas de conector:** fondo blanco (`labelBackgroundColor=#FFFFFF`) y el mismo color que la flecha.
- **Texto:** título de 24 pt en negrita, subtítulo de 14 pt en `gris`, cuerpo de 13 pt y notas de 11 pt.

### Exportar para las slides

- **Archivo → Exportar como → SVG** (para PowerPoint: escala sin perder calidad). Marca **Incluir una copia del diagrama**: así el SVG se puede volver a abrir en draw.io.
- Si PowerPoint da guerra con el SVG: **PNG a 200 %**, con fondo blanco y borde de 20 px.
- **Para las animaciones por pasos** (slides 9 y 19): duplica la página del diagrama (botón derecho en la pestaña → *Duplicar*) y en cada copia oculta lo que no toca todavía. Exporta cada página por separado y apílalas en PowerPoint con transición *Desvanecer*. Es más fiable que animar un SVG.

---

## 4. Los diagramas, uno a uno

Coordenadas en píxeles de draw.io (lienzo con rejilla de 10). Sirven para reconstruirlos o para saber dónde mover algo sin romper el resto.

### D1 · El modelo de Microsoft Entra Agent ID

**Lienzo:** 1500 × 860 · **Slide 9** · Mensaje: *las credenciales viven en el blueprint; las políticas se heredan.*

| Zona | Posición | Contenido |
|---|---|---|
| Título | (40, 20) | *El modelo de Microsoft Entra Agent ID* + subtítulo *Se gobierna la plantilla…* |
| Credencial | caja discontinua `entra` en (60, 110), 400 × 120 | icono **Managed identity** + texto: ✅ MI (federated credential) · ✅ Certificado · ❌ Secreto (solo desarrollo) |
| Blueprint | contenedor `entra_bg` en (60, 290), 400 × 250 | rótulo **BLUEPRINT · lo aprueba IT**; dentro, **App registrations** (*Agent identity blueprint · la «clase»*) y **Enterprise applications** (*Blueprint principal*) |
| Acceso condicional | icono **Conditional Access** en (572, 100) | texto: *cubre a todas sus identidades, también a las que se creen mañana* |
| Identidades | tres **Entra ID** en la columna x = 620–860, y = 250 / 430 / 610 | A: *pide tokens · recibe roles de Azure* · B · C dentro de una caja **discontinua gris** (*se crea mañana*) |
| Cuenta de usuario de agente | **Users** en (1060, 250) | *opcional · buzón, Teams, licencia · cuando el agente tiene que «ser alguien»* |
| Papeles humanos | contenedor `gris_bg` en (1000, 470), 440 × 260 | tres cajas: **Owner** (gris), **Sponsor** (relleno `aviso_bg`, borde `aviso` 2 px), **Manager** (gris) |

**Conectores:**

1. Credencial → blueprint: `entra`, **3 px**, etiqueta *las credenciales viven aquí, no en cada agente*.
2. Acceso condicional → blueprint: `entra` discontinuo.
3. Blueprint → identidades A, B y C: `entra`, con el tramo vertical en x = 580. **A a 3 px**, B y C a 1,5 px. Texto *hereda políticas y permisos delegados* en (446, 300), a la izquierda del tramo vertical.
4. Identidad A → cuenta de usuario: gris, etiqueta *1 : 1*.
5. Identidad B → papeles humanos: `aviso` discontinuo, sin punta.

**Pasos para la animación (3 páginas):** ① credencial + blueprint · ② + identidades y la flecha de herencia · ③ + cuenta de usuario, papeles humanos y acceso condicional.

**Versión reducida (slide 12):** duplica la página, borra credencial, cuenta de usuario y papeles humanos, y pon una persona (**Users**) distinta debajo de cada identidad.

---

### D2 · Tres puertas, un directorio

**Lienzo:** 1600 × 960 · **Slide 13** · Mensaje: *tres caminos, una sola lista.*

Tres columnas idénticas de 480 × 570, en x = 60, 560 y 1060, y = 100. Cada una con:

| Fila | y | Puerta 1 (`puerta-1`) | Puerta 2 (`puerta-2`) | Puerta 3 (`puerta-3`) |
|---|---|---|---|---|
| Cabecera | 100 | Banda de 40 px rellena: **PUERTA 1 · COPILOT STUDIO** | **PUERTA 2 · FOUNDRY** | **PUERTA 3 · AGENTE PROPIO** |
| Plataforma | 160 | **Copilot Studio** · `FS-Copilot-Devoluciones` | **Foundry Agent Service** · `frasohome-returns` | **Container App** · `fs-triage-devoluciones` |
| Blueprint | 310 | **App registrations** · *Blueprint global de Copilot Studio · lo crea Microsoft* | *Blueprint del agente · lo crea Foundry* | *bp-frasohome-operaciones · lo crea IT · federated credential sobre la MI* |
| Identidad | 460 | **Entra ID** · Sponsor: **Marta R.** ⚠️ · *flujo: en nombre de usuario (OBO)* | Sponsor: grupo **Plataforma de agentes** · *flujo: autónomo, vía MCP* | Sponsor: **Lucía M.** · Owner: David L. · *flujo: autónomo* |

Debajo:

- **Banda de Entra:** contenedor `entra_bg` de 1480 × 90 en (60, 700), con el icono **Entra ID** y el texto *Microsoft Entra Agent ID · identidades · sponsors · acceso condicional · ciclo de vida · logs*.
- **Agent 365:** caja de texto de 600 × 64 en (500, 830), borde `entra` de 2 px (sin icono, ver §2).

**Conectores:** plataforma → blueprint (color de la puerta) · blueprint → identidad (`entra`, etiqueta *hereda*) · identidad → banda de Entra (`entra`, 2 px, vertical) · banda → Agent 365 (`entra`, 2 px).

**Variantes para los separadores (slides 14, 17 y 21):** duplica la página tres veces. En cada copia, selecciona las dos columnas que no tocan y ponles **opacidad 25 %** (*Estilo → Opacidad*). Exporta a 800 px de ancho.

---

### D3 · El rol que no viaja

**Lienzo:** 1300 × 720 · **Slide 18** · Mensaje: *dos sujetos distintos para Azure.*

| Elemento | Posición | Detalle |
|---|---|---|
| Identidad compartida | **Foundry Project** (72 px), grupo en (60, 130) | *Identidad compartida del proyecto · fs-agentes-prj · antes (desarrollo)*, texto en `puerta-2` |
| Identidad propia | **Foundry Agent Service** (72 px), grupo en (60, 440) | *Identidad propia de frasohome-returns · agentIdentityId · después* |
| Storage | **Storage Accounts** (80 px), grupo en (900, 270) | *stfrasohomeops · contenedor devoluciones* |
| Nota MCP | texto gris en (380, 300) | *vía la herramienta MCP fs-devoluciones-mcp · token con audience = https://storage.azure.com* |
| El arreglo | caja en (760, 470), 480 × 120, borde `ok` 2 px, relleno `#F1F8F1` | `az role assignment create --assignee <agentIdentityId> --role "Storage Blob Data Reader" --scope …/containers/devoluciones` en Cascadia Code de 12 pt |

**Conectores:**

1. Compartida → propia: `puerta-2` discontinuo, 2 px, etiqueta *publicar / migrar · los roles no se transfieren*.
2. Compartida → Storage: `ok`, **2,5 px**, codo en x = 700, etiqueta *✅ Storage Blob Data Reader*.
3. Propia → Storage: `bloqueo`, **2,5 px, discontinuo**, codo en x = 700, etiqueta *❌ sin rol → 403 AuthorizationPermissionMismatch*.
4. Arreglo → Storage: `ok` discontinuo, hacia la parte de abajo del grupo de Storage.

**Para la slide:** el diagrama ocupa el 60 % izquierdo. Si el arreglo duplica la checklist de la derecha, borra la caja del arreglo en la copia que exportes.

---

### D4 · Sin secretos

**Lienzo:** 1600 × 700 · **Slide 19** · Mensaje: *la infraestructura es la credencial, y en el paso 5 Entra puede decir que no.*

| Elemento | Posición | Detalle |
|---|---|---|
| Container App | **Container App** (80 px), grupo en (60, 250) | *ca-fs-triage · fs-triage-devoluciones*, en `puerta-3` |
| Managed identity | **Managed identity** (64 px), grupo en (60, 500) | *id-fs-triage · managed identity (IMDS)* |
| Entra | contenedor `entra_bg` en (520, 110), 620 × 330 | rótulo *MICROSOFT ENTRA ID · endpoint de tokens* |
| — Blueprint | **App registrations**, grupo en (540, 155) | *bp-frasohome-operaciones · federated credential → confía en la MI* |
| — Identidad | **Entra ID**, grupo en (860, 155) | *Identidad de agente · fs-triage-devoluciones* |
| — Controles | **Conditional Access** y **Entra ID Protection** (48 px) en (560, 340) y (630, 340) | texto: *⑤ al emitir el token del paso ③ se evalúan acceso condicional y riesgo: aquí Entra puede decir que no* |
| Logs | **Log Analytics**, grupo en (1220, 140) | *Sign-in logs · Agent type = Agent Identity · blueprint padre* |
| Storage | **Storage Accounts**, grupo en (1300, 470) | *buzon-devoluciones (lectura) · triage-resultados (escritura)* |
| Pie | texto `bloqueo` en (380, 620) | *❌ Ningún secreto en código, variables de entorno ni Key Vault. Un agente con API key se salta los pasos ② a ⑤.* |

**Conectores** (numerados en las etiquetas, con los caracteres ①–⑤):

1. **①** Container App ↔ MI: gris, doble punta, vertical. *token de la MI*.
2. **②** Container App (sale por arriba) → blueprint (entra por la izquierda): `entra`, 2 px. *client_assertion = token MI · fmi_path = fs-triage → T1*.
3. **③** Container App (sale por la derecha) → identidad (entra por abajo): `entra`, 2 px, codo en x = 990. *client_assertion = T1 · scope = storage.azure.com/.default*.
4. **④** Container App → Storage: `ok`, 2,5 px, baja por x = 330 y cruza por debajo del contenedor de Entra. *Bearer = token del agente → RBAC con roles de datos*.
5. Contenedor de Entra → logs: gris discontinuo. *rastro*.

**Pasos para la animación (5 páginas):** una por número, en el orden ① a ⑤. En la página del ⑤, resalta el acceso condicional y ID Protection con un halo (`shadow=1`) o con un rectángulo `bloqueo` de 3 px alrededor.

---

### D5 · Mapa de controles

**Lienzo:** 1300 × 860 · **Slide 22**, y en miniatura en las slides 23–30 · Mensaje: *lo nuevo es el sujeto, no el control.*

| Elemento | Posición | Detalle |
|---|---|---|
| Centro | contenedor `entra_bg` en (500, 360), 300 × 190, borde de 2,5 px | **Entra ID** (80 px) · *Identidad de agente (y su blueprint)* |
| Arriba | **Custom Azure AD Roles**, grupo en (500, 110) | *RBAC mínimo · al agentIdentityId · scope de recurso · roles de datos* |
| Arriba a la derecha | **Conditional Access**, grupo en (920, 280) | *solo bloquear · por blueprint o atributo · condición: riesgo del agente* |
| Abajo a la derecha | **Entra ID Protection**, grupo en (920, 590) | *detecciones · confirmar comprometido · en OBO, el riesgo es del usuario* |
| Abajo a la izquierda | **Identity Governance**, grupo en (80, 590) | *Ciclo de vida · sponsor · inactividad 60/90/455 · access packages con caducidad* |
| Arriba a la izquierda | **Log Analytics**, grupo en (80, 280) | *Rastro · sign-in: Agent type · audit: agentType, blueprintId* |

**Conectores:** del centro a cada control, `entra`, 2 px, **sin punta** (es un mapa, no un flujo). De ID Protection a acceso condicional, `bloqueo` discontinuo con punta, etiqueta *el riesgo alimenta la política*.

**Miniaturas para las slides 23–30:** duplica la página cinco veces. En cada copia, deja el control del que se habla a opacidad 100 % y el resto a 30 %. Exporta a 400 px de ancho y colócalo en la esquina superior derecha a 200 px.

---

## 5. Comprobación antes de dar por bueno un diagrama

- [ ] Ninguna flecha atraviesa un texto (si pasa, engancha el conector al grupo y no al icono, o mueve el codo).
- [ ] Cada puerta conserva su color en todos los diagramas.
- [ ] Ningún logo inventado: lo que no está en la tabla del §2 va como texto.
- [ ] Los nombres coinciden con el guion: `FS-Copilot-Devoluciones`, `frasohome-returns`, `fs-triage-devoluciones`, `bp-frasohome-operaciones`, `stfrasohomeops`, `id-fs-triage`, `ca-fs-triage`.
- [ ] Exportado en SVG con copia del diagrama, o en PNG a 200 %.
- [ ] Legible en una ventana de 1280 px de ancho: es lo que verá la mayoría del público online.
