# Escenario FraSoHome — deuda semántica (demos de Microsoft 365 Live 2026)

> Reutiliza el tenant `frasohome.onmicrosoft.com` y los documentos FS-KB del caso. FS-KB-01 v1.3 (vigente, 45 días online) y FS-KB-02 v1.2 (obsoleta, 30 días) son las mismas del Bizz Summit 2026.
> Lo que hay que crear para esta sesión está marcado como **NUEVO**.

## 1. Personas

| Persona | Rol | Papel en la sesión |
|---|---|---|
| **Laura P.** | Directora comercial · grupo *Comercial* · licencia M365 Copilot | Es quien pregunta en todas las demos. En el "después" pasa a ser **dueña** del término "Cliente activo" |
| **Nuria S.** | Admin de M365 / Purview | Perfil admin para Purview y SharePoint Admin |
| **Lucía M.** | Cajera sénior, MAD01 Gran Vía | Una de las tres cabezas del procedimiento tácito |
| **Jorge T.** | Atención al cliente | Otra de las tres cabezas; contacto al que remite el agente cuando se abstiene |
| **Paco R.** | Conciliación, Finanzas | La tercera cabeza |

## 2. Las cifras (calculadas sobre `frasohome-agents-foundry/case/data/fact_transacciones.csv` y `crm.csv`)

**Criterios comunes:** año de referencia 2025 (cierre a 31/12/2025). Q3 = jul–sep 2025 y Q4 = oct–dic 2025. Se excluyen las fechas fuera de rango que el dataset trae a propósito (2017, 2030 y 2031). El descuento por puntos no está en el dataset, así que la cifra oficial no lo resta (dilo si alguien pregunta).

### "Cliente activo" — seis definiciones

| Definición | Regla aplicada | Valor |
|---|---|---|
| CRM, estado | `crm.estado_cliente == "Activo"` | **47** |
| Marketing (PPT) | Socios con tier informado y sin `fecha_baja` | **49** |
| E-commerce | `customer_id` distintos con VENTA online en 2025 y pedido no *Cancelado* | **89** |
| **Oficial FS-KB-03** | `customer_id` distintos con VENTA en 2025 **que existen en el CRM** | **100** |
| Tiendas | `customer_id` distintos con VENTA en POS en 2025 | **132** |
| FS-KB-03 al pie de la letra | Cualquier `customer_id` con VENTA en 2025 (incluye 35 IDs que no están en el CRM) | **135** |

### "Ventas netas" Q4 vs Q3 2025 — cuatro cálculos

| Fichero | Regla aplicada | Q3 | Q4 | Var. |
|---|---|---|---|---|
| `Informe_Comercial_Q4_2025_FINAL.pptx` (Marketing) | Suma de `importe_abs_num` de VENTA, con IVA, sin restar devoluciones, incluye cancelados y duplicados | 323.396 € | 315.112 € | **−2,6 %** |
| **FS-KB-03 (oficial)** | `importe_signed_num` (ventas − devoluciones), con IVA, sin *Cancelado*, sin duplicados | 273.514 € | 280.441 € | **+2,5 %** |
| `Cuadro_mando_tiendas_v3_bueno.xlsx` (Tiendas) | Solo POS, sin IVA, neto de devoluciones | 179.097 € | 186.990 € | **+4,4 %** |
| `Cierre_mensual_2025-12_Finanzas.xlsx` (Finanzas) | Sin IVA, neto de devoluciones, sin duplicados, solo POS + pedidos entregados/aceptados/devueltos/reembolsados | 209.750 € | 224.128 € | **+6,9 %** |

Duplicados por (`doc_id_std`, `line_id_std`, `tipo_movimiento`): 173 filas en el dataset. Si hay que regenerar las cifras, el script va en `C:\dev\microsoft365-live\2026\` (no en este repo).

## 3. Estado "ANTES" del tenant (lo que se ve en las demos 0–3)

### Sitio `FraSoHome-Comercial` — **NUEVO**

Biblioteca *Documentos* **solo con las columnas por defecto**:

```
Documentos/
├── Antiguo/
│   └── FS-KB-02_Politica_Devoluciones_v1.2.docx            (30 días online, OBSOLETA en su tabla de control)
├── Comité/
│   ├── Informe_Comercial_Q4_2025_FINAL.pptx                 NUEVO — 49 clientes activos, −2,6 %
│   └── Cierre_mensual_2025-12_Finanzas.xlsx                 NUEVO — +6,9 %
├── Definitivos/
│   ├── FS-KB-01_Politica_Devoluciones_v1.3_Vigente.docx     (45 días online)
│   └── FS-KB-03_Diccionario_KPI_v1.0.docx                   ⚠ etiqueta "Altamente confidencial – Finanzas"
└── Varios/
    ├── Cuadro_mando_tiendas_v3_bueno.xlsx                   NUEVO — +4,4 %, "clientes" = 132
    └── Manual_caja_2023.docx                                NUEVO — copia antigua de las reglas de pago mixto (coincide con FS-KB-04)
```

**Contenido mínimo del PPT (NUEVO).** Debe quedar redactado para el comité para que se parezca a la pregunta de Laura:

- Diapositiva "Resumen ejecutivo Q4 2025": *"Cerramos 2025 con **49 clientes activos** en FraSoHome Rewards"*. Las *"Ventas netas del trimestre"* son **315.112 €**, un **−2,6 %** frente al Q3 (323.396 €).
- En una nota a pie, en letra pequeña: *"Clientes activos = socios del programa sin baja. Ventas netas = pedidos captados."*
- Una mención a *"clientes omnicanal"*, un término que nadie ha definido (es la pregunta N1 del test set).
- Tasa de devolución calculada como *pedidos devueltos / pedidos* (contradice a FS-KB-03, pregunta X4).

### Purview

- Etiqueta **`Altamente confidencial – Finanzas`**: cifrado con permisos solo para el grupo *Finanzas*. Laura **no** está en *Finanzas* (compruébalo antes de cada ensayo).
- FS-KB-03 lleva esa etiqueta. En la narrativa la puso una política de autoetiquetado de 2024 que buscaba "margen" y "coste". Si el tenant no tiene la política, aplícala a mano y cuéntalo como parte del escenario.
- **Slide 12** ("14 etiquetas publicadas, 3 en uso"): **ajusta las cifras a las reales del tenant** antes del evento. No digas en directo un número que no puedas enseñar.
- **Unified Catalog** → dominio de gobierno *Comercial* → término de glosario **"Cliente activo"** en **borrador**. Sin propietario de negocio: el único propietario es la admin que lo creó. Ningún producto de datos vinculado.

## 4. Estado "DESPUÉS" (demo 4)

### Sitio `FraSoHome-KB-Oficial` — **NUEVO**

- Term store → grupo *FraSoHome* → conjuntos **Estado documental** (Vigente · Borrador · Obsoleta) y **Dominio** (Devoluciones · KPI · Fidelización · Tienda · Catálogo).
- La biblioteca lleva las columnas *Estado*, *Dominio*, *Propietario* (persona) y *Vigente desde* (fecha).
  - **Por verificar:** si el filtrado por metadatos de Copilot Studio no admite columnas de *managed metadata*, crea *Estado* como columna de **opción**. Lo que la demo necesita es el filtro, no la taxonomía.
- Opcional, para enseñar en 30 s: el **Knowledge Agent** (preview) proponiendo la columna *Estado* a partir del contenido de la tabla de control de cada documento.
- Contenido: FS-KB-01, 03, 04, 05, 06 y 07 en estado *Vigente*, y FS-KB-02 en estado *Obsoleta*.
- FS-KB-03 re-etiquetado como **`Interno – Definiciones oficiales`**, sin cifrado y excluido de la política de autoetiquetado.

### Glosario

- "Cliente activo" **publicado**, con dueña **Laura P. (Dirección Comercial)** y *steward* el **Equipo de Datos**. Definición: *"Cliente del CRM con ≥1 compra en los últimos 12 meses, en cualquier canal."* Vinculado al producto de datos *Ventas consolidadas*.

### Agente de Copilot Studio — **"Asistente Comercial FraSoHome"** (NUEVO)

- Conocimiento: **solo** la biblioteca de `FraSoHome-KB-Oficial`. No se desactiva el conocimiento general: la demo no lo necesita.
- Instrucciones:

```
Eres el asistente comercial de FraSoHome.
- Responde solo con documentos cuyo Estado sea "Vigente". Ignora los "Obsoleta" y avisa si solo encuentras uno de esos.
- Si la pregunta usa un término de negocio con más de una definición conocida (cliente, cliente activo, ventas netas, tasa de devolución),
  pregunta qué definición quiere el usuario y propón por defecto la oficial de FS-KB-03.
- Cuando des un KPI, declara siempre periodo, canal, moneda y fórmula usada (regla de FS-KB-03).
- Si no hay un procedimiento documentado, dilo explícitamente y remite al propietario del dominio. No compongas procedimientos a partir de documentos parciales.
- Cita siempre el documento y la versión.
```

- Nota de montaje: si el agente no da las cifras exactas de clientes activos y ventas netas a partir del docx, añade al sitio una ficha `KPI_Cierre_2025_Oficial.docx` (Estado Vigente, dueño Finanzas) con los dos valores oficiales. Es lo que haría una organización real: **publicar la cifra oficial, no solo la fórmula.**

## 5. Test set (20 preguntas) — base de la TRC

| ID | Pregunta | Estado | Respuesta esperada | Antes | Después |
|---|---|---|---|---|---|
| C1 | Plazo de devolución en tienda física | Canónica | 30 días naturales (FS-KB-01) | ✔ | ✔ |
| C2 | Plazo objetivo de reembolso e-commerce | Canónica | 7–10 días laborables (FS-KB-01) | ✔ | ✔ |
| C3 | ¿Se reembolsan los gastos de envío en una devolución voluntaria? | Canónica | No, salvo error de preparación o incidencia (FS-KB-01) | ✔ | ✔ |
| C4 | Puntos por euro según el tier | Canónica | Plata 1,25 · Oro 1,5 · Platino 2 (FS-KB-07) | ✔ | ✔ |
| C5 | Fórmula del stock disponible | Canónica | On hand − reservado − bloqueado (FS-KB-03) | ✘ cifrado | ✔ |
| C6 | Reglas de construcción del SKU | Canónica | Según FS-KB-06 | ✔ | ✔ |
| C7 | Conciliación de pagos e-commerce | Canónica | Según FS-KB-05 | ✔ | ✔ |
| C8 | Beneficio del tier Oro en devoluciones | Canónica | 1 excepción de devolución por semestre (FS-KB-07) | ✔ | ✔ |
| D1 | Reembolso con pago tarjeta + efectivo | Duplicada | Primero a tarjeta, el resto en efectivo | ✘ cita `Manual_caja_2023` | ✔ |
| D2 | Reembolso con tarjeta + tarjeta regalo | Duplicada | Primero a la tarjeta regalo, el resto a tarjeta (FS-KB-04) | ✘ cita copia | ✔ |
| D3 | Definición de ticket medio | Duplicada | Ventas netas / nº de pedidos (FS-KB-03) | ✘ cita el Excel de tiendas | ✔ |
| X1 | Plazo de devolución online | Contradictoria | 45 días naturales (FS-KB-01 v1.3) | ✘ 30 días | ✔ |
| X2 | Clientes activos al cierre de 2025 | Contradictoria | 100 (FS-KB-03) | ✘ 49 | ✔ (pregunta antes) |
| X3 | Ventas netas Q4 vs Q3 | Contradictoria | +2,5 % (FS-KB-03) | ✘ −2,6 % | ✔ |
| X4 | Tasa de devolución | Contradictoria | Unidades devueltas / vendidas o importe / ventas netas (FS-KB-03) | ✘ pedidos / pedidos | ✔ |
| T1 | Devolución en tienda de un pedido online pagado con tarjeta + puntos | Tácita | *No documentado* → Jorge T. | ✘ inventa | ✘ se abstiene (correcto, pero sigue siendo deuda) |
| T2 | ¿Quién aprueba la excepción VIP de devolución? | Tácita | *No documentado* | ✘ | ✘ se abstiene |
| T3 | Cuadre de caja de una devolución omnicanal sin ticket original | Tácita | *No documentado* → Lucía M. | ✘ | ✘ se abstiene |
| N1 | ¿Qué es un "cliente omnicanal"? | Inexistente | Nadie lo ha definido | ✘ inventa | ✘ se abstiene |
| N2 | Objetivo de tasa de devolución para 2026 | Inexistente | No está decidido | ✘ | ✘ se abstiene |

**TRC antes = 7/20 (35 %) · TRC después = 15/20 (75 %).** Las abstenciones no suman a la TRC: son respuestas *honestas*, pero la deuda sigue sin pagar. Este es el argumento del bloque 5: lo que queda solo se arregla decidiendo.

## 6. Checklist de montaje

- [ ] Crear `FraSoHome-Comercial` y subir los ficheros del árbol de la sección 3
- [ ] Crear el PPT y los dos Excel (NUEVO) con las cifras de la sección 2
- [ ] Etiqueta `Altamente confidencial – Finanzas` aplicada a FS-KB-03 en `FraSoHome-Comercial`
- [ ] Glosario: "Cliente activo" en borrador (antes). Preparar el término publicado en otro dominio o publicarlo justo antes de la demo 4
- [ ] Crear `FraSoHome-KB-Oficial` con el term store, las columnas y los estados
- [ ] Crear el agente "Asistente Comercial FraSoHome" y probar las 4 preguntas de la demo 4
- [ ] Esperar a la indexación: entre 4 y 6 h de sincronización en Copilot Studio y hasta que el índice de SharePoint procese los ficheros. **Montar como muy tarde 48 h antes**
- [ ] Pasar el test set completo como Laura y anotar la TRC real. Si no sale 7/20 y 15/20, **cambia las slides para que digan la cifra real**
- [ ] Grabar los vídeos de respaldo de las demos 0–4
