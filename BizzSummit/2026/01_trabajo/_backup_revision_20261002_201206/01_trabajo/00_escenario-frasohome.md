# Escenario FraSoHome de la sesión — marcadores resueltos

> Este documento cierra todos los `«FraSoHome: …»` que quedaban abiertos en
> `bizz-summit-2026-gobierno-agentes-indice-v2.md`. Todo lo de aquí se apoya en material
> real del repositorio `Materiales\FraSoHome`; lo que se ha añadido está marcado como **NUEVO**.

---

## 1. La empresa (pitch de 20 segundos, se dice una vez)

> *"FraSoHome vende muebles y decoración. Tres tiendas —Gran Vía, Diagonal, Valencia Centro—,
> e-commerce y un programa de fidelización. Y, como todos, datos repartidos entre CRM, POS,
> e-commerce y ERP. Hoy no vamos a hablar de sus datos: vamos a hablar de los agentes que
> alguien construyó encima de ellos sin decírselo a nadie."*

| | |
|---|---|
| Sector y tamaño | Retail omnicanal de hogar y decoración. 3 tiendas físicas (MAD01 Gran Vía, BCN01 Diagonal, VLC01 Centro) + e-commerce + CRM de fidelización |
| Sistemas | CRM, POS, e-commerce, ERP |
| Tenant de demo | `frasohome.onmicrosoft.com` |

---

## 2. El proceso de negocio elegido: **devoluciones omnicanal**

Un solo proceso atraviesa las cuatro demos. Se elige devoluciones porque es el único del caso
que reúne, a la vez, las cuatro cosas que la sesión necesita demostrar:

| Lo que necesita la sesión | Lo que aporta devoluciones |
|---|---|
| Conocimiento documental con versiones | FS-KB-01 v1.3 **vigente** frente a FS-KB-02 v1.2 **obsoleta** — misma política, plazos distintos |
| Dato transaccional | `FS_DevolucionesFact` (motivo, aprobado, importe), `FS_VentasResumenDiario` |
| Dato sensible identificable | Importes de reembolso con **IBAN** del cliente y listado de clientes con patrón anómalo |
| Un caso que Copilot Studio no cubre bien | Triaje del buzón de reclamaciones de devoluciones |

**Frase que lo justifica en sala:** *"Un proceso donde una respuesta mal fundamentada le cuesta
dinero a la empresa, y donde el dato correcto está a un documento de distancia del dato que
no puedes enseñar."*

---

## 3. Los agentes de FraSoHome

> **2 de octubre:** se añade un tercer agente, hecho con **Agent Builder** en Copilot Chat. La
> sesión se centra en Microsoft 365 y Agent 365, y las demos cambian: ver
> `01_guion-minuto-a-minuto.md` y `demos/guia-despliegue-manual.html`. La regresión de versionado,
> el bloqueo por IBAN en Dataverse y el endpoint filtering de este documento ya no se demuestran.

### Agente C — el de Agent Builder (demos 1, 2 y 3) — **NUEVO**

| | |
|---|---|
| Nombre | **Atajo Devoluciones MAD01** |
| Construido con | **Agent Builder**, en Copilot Chat, en dos minutos |
| Creado por | **Álvaro G.**, Store Manager de Gran Vía |
| Conocimiento | El sitio `FraSoHome-KB-Operaciones` |
| Compartido | Con su equipo, por enlace. No pasó por nadie |
| Lo que enseña | Que aparece en *All agents* junto al de Copilot Studio, y que DSPM for AI ve el IBAN que Álvaro pegó en él |

Le acompaña un duplicado, **Calculadora de reembolsos (copia)**, que se bloquea en la demo 3.

### Agente A — el de Copilot Studio (demos 1, 2 y 3)

| | |
|---|---|
| Nombre visible | **Asistente de Devoluciones FraSoHome** |
| Nombre técnico | `FS-Copilot-Devoluciones` |
| Creado por | **Marta R.**, Operaciones de Tienda (maker del área) |
| Fecha de creación | **17 de marzo de 2026** |
| Dónde vive | Entorno **Default** — sin Managed Environment |
| Propietario actual | *Ninguno nombrado.* Marta pasó a e-commerce en **julio de 2026** |
| Publicado en | Teams y Microsoft 365 Copilot chat |
| Knowledge sources | Sitio SharePoint `FraSoHome-KB-Operaciones` (FS-KB-01, 03, 04, 05, 06, 07, 08, 09) |
| Tools | `DV_ListSalesSummary`, `DV_ListReturns` sobre Dataverse |
| Usuarios reales | ~40 personas: tienda, atención al cliente, operaciones |
| Créditos | Facturados al entorno Default. Nadie sabe a qué centro de coste |
| Carril al que pertenece | **Producción** (aunque hoy esté en Default: ese es el problema) |

**La regresión plantada a propósito (para la demo 3):** el 12 de septiembre alguien editó la
instrucción del sistema y borró la línea *"prioriza siempre la versión VIGENTE de la política;
ignora documentos marcados OBSOLETA"*. Desde entonces el agente responde **30 días** de plazo
de devolución online (FS-KB-02 v1.2) en vez de **45 días** (FS-KB-01 v1.3).

### Agente B — el que no es de Microsoft (demo 4) — **NUEVO**

| | |
|---|---|
| Nombre | **`fs-triage-devoluciones`** |
| Construido con | **Claude Agent SDK** (Python), en el portátil de un dev de e-commerce |
| Qué hace | Lee el buzón compartido **`devoluciones@frasohome.es`**, clasifica cada entrada por `ReasonCode` (R01 arrepentimiento … R04 daño en transporte), detecta patrones anómalos y redacta un resumen diario para el Store Manager |
| Estado de partida | Funciona desde hace semanas. **No aparece en ningún inventario.** Sin Entra Agent ID, sin telemetría, sin propietario declarado |
| Dónde se ejecuta | Contenedor en la suscripción de desarrollo de e-commerce |
| Carril de destino | **Producción**, por la vía de onboarding del Agent 365 SDK |

---

## 4. Las personas de la demo

| Persona | Rol | Aparece en |
|---|---|---|
| **Álvaro G.** | Store Manager de MAD01 (Gran Vía) | Demos 1 y 2 — es quien pregunta |
| **Marta R.** | Operaciones de Tienda → e-commerce (julio 2026) | La creadora del agente que ya no está en ese equipo |
| **Nuria S.** | Admin de Power Platform / M365 | Quien mira *All agents* y el PPAC |
| **David L.** | Dev de e-commerce | Autor del agente `fs-triage-devoluciones` |

---

## 5. El dato sensible que activa el bloqueo (demo 2)

Se usan **dos controles distintos** sobre el mismo proceso, y esa es la gracia de la demo:

**Beat 1 — endpoint filtering sobre el knowledge source de SharePoint**

- Sitio permitido: `https://frasohome.sharepoint.com/sites/FraSoHome-KB-Operaciones`
- Sitio **NO** permitido: `https://frasohome.sharepoint.com/sites/FraSoHome-PrevencionPerdidas`
- En ese segundo sitio vive **FS-KB-11_Listado_Clientes_Devoluciones_Anomalas_2026Q1.docx** (**NUEVO**),
  etiquetado **`Confidencial – Prevención de Pérdidas`** con cifrado.
- Resultado: el agente ni siquiera ve el documento. No es que se niegue: es que no existe para él.

**Beat 2 — DLP de Purview sobre la respuesta**

- Pregunta: *"¿A qué cuenta se reembolsó la devolución DEV-2026-0418?"*
- El dato existe en Dataverse (`FS_DevolucionesFact`), el agente tiene la tool y el usuario tiene permisos.
- La respuesta contendría un **IBAN español** → coincide con el tipo de información sensible
  *IBAN / Spain* → **Purview bloquea la respuesta en vivo**.
- Mensaje: el control no estaba en el agente. Estaba en la capa.

**Frase de remate:** *"Nadie ha tenido que revisar este agente para que esto pase.
El control estaba en la capa, no en el agente."*

---

## 6. El test set de la demo 3

Material ya existente en `01_datos/rag_copilot_studio/test_sets/`:

- `FS_TestSet_Documental.csv` — **10 casos** (plazos, exclusiones, pago mixto, ventas netas,
  stock disponible, 72 h de daño en transporte, sin ticket, escalado por fraude, formato de
  respuesta de KPI, excepción por tier)
- `FS_TestSet_Metrico_Mixto.csv` — **6 casos** (ventas netas online, tienda top, tasa de
  devolución, R04 de enero, pedidos en tienda, SKUs con alerta de stockout)
- **NUEVO:** `FS_TestSet_Seguridad.csv` — **4 casos** de regresión de seguridad
  (prompt injection con FS-KB-10, petición de PII, listado masivo, uso de versión obsoleta)

**Total: 20 casos.** Es exactamente el umbral que la sesión recomienda en el bloque 6.3.

**Lo que se ve fallar en vivo:** el caso `¿Cuál es el plazo de devolución para compras online?`
pasa de verde a rojo. Esperado: *45 días naturales*. Devuelto: *30 días*.
Y el Agent Change Tracker enseña el diff de la instrucción borrada, con autor y fecha.

---

## 7. El componente corporativo reutilizable (bloque 6.2)

**`FS-Guardarrail-Devoluciones`** — component collection publicada por el equipo de plataforma.
Cinco piezas, todas sacadas del Canvas de solución del caso:

1. **Disclaimer obligatorio** — *"Respuesta orientativa. La política vigente es FS-KB-01 v1.3."*
2. **Regla de versionado** — prioriza estado *Vigente* y versión mayor; ignora *Obsoleta*
3. **Patrón de abstención** — si no hay evidencia, decirlo y proponer siguiente paso
4. **Patrón de datos sensibles** — nunca devolver PII (email, IBAN, dirección) ni listados masivos; usar agregados
5. **Patrón de escalado a humano** — sospecha de fraude → Prevención de Pérdidas, nunca resolver el agente

**El argumento que convence a negocio:** la regla nº 2 de esta colección es exactamente la
línea que Marta borró en la demo 3. Si hubiera estado en el componente y no en el agente,
el maker no habría podido borrarla.

---

## 8. Dónde cae cada agente en la tabla de carriles

| Agente | Carril | Qué le falta hoy para estar ahí |
|---|---|---|
| `FS-Copilot-Devoluciones` | **Producción** | Sale del Default a entorno dedicado, propietario de negocio + técnico, pipeline Dev→Test→Prod, test set de regresión, centro de coste |
| `fs-triage-devoluciones` | **Producción**, vía onboarding | Blueprint de identidad en Entra, Agent ID, telemetría OpenTelemetry, tools vía Work IQ MCP, propietario nombrado |

---

## 9. Activos que hay que crear antes del evento

| Activo | Estado | Dónde |
|---|---|---|
| `FS-KB-11_Listado_Clientes_Devoluciones_Anomalas_2026Q1.docx` | **NUEVO** | Sitio `FraSoHome-PrevencionPerdidas`, etiqueta `Confidencial – Prevención de Pérdidas` |
| `FS_TestSet_Seguridad.csv` | **NUEVO** | `01_datos/rag_copilot_studio/test_sets/` |
| Buzón compartido `devoluciones@frasohome.es` | **NUEVO** | Exchange Online, con 15–20 correos sembrados |
| Agente `fs-triage-devoluciones` | **NUEVO** | Repo con Claude Agent SDK en Python |
| Component collection `FS-Guardarrail-Devoluciones` | **NUEVO** | Entorno de plataforma |

Los pasos concretos están en `02_guia-montaje-demos.md`.
