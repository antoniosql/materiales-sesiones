# Paso a paso de las demos · Semantic Debt (M365 Live 2026)

*Tenant **vernedev.onmicrosoft.com** · estado a 7 nov 2026, 09:50 · deck v2 (numeración de slides de la v2)*

Este es el documento que tienes que tener abierto durante la sesión. El **qué decir** está en el guion
(`01_guion-sesion.md`); aquí solo está **dónde hacer clic, qué pegar y qué tiene que salir**.

---

## 0. Estado del tenant ahora mismo

| Pieza | Estado | Consecuencia para la demo |
|---|---|---|
| Laura P. (`laura.p@vernedev.onmicrosoft.com`) con E5 + Copilot | ✔ creada | **Nunca ha iniciado sesión**: hazlo antes (contraseña inicial en el chat; registrará MFA) |
| Sitio FraSoHome-Comercial (el «antes») | ✔ montado | ⚠ **Sin indexar**: el Copilot del sitio no encuentra nada → demos 0–3 **en vídeo** salvo que se indexe antes |
| Sitio FraSoHome-KB-Oficial (el «después») | ✔ montado con Estado / Dominio / Propietario / Vigente desde | Igual: sin indexar |
| Etiquetas | ✔ «Altamente confidencial – Finanzas» en FS-KB-03 de Comercial · «Interno – Definiciones oficiales» en FS-KB-03 de KB-Oficial | Demo 2 se puede **enseñar en directo** (Purview + candado) |
| Glosario «Cliente activo» | ✔ en **Borrador** | Demo 3 en directo |
| Agente «Asistente Comercial FraSoHome» | ✔ publicado · conocimiento = 8 ficheros vigentes + fuente SharePoint | **Demo 4 en directo** (las 4 preguntas validadas hoy) |

**Cómo saber si ya se ha indexado** (2 min antes de empezar): como admin, en el buscador de SharePoint
escribe `FS-KB-00`. Si sale el documento de FraSoHome-KB-Oficial, el índice ya está y puedes intentar las
demos 0–3 en directo (pre-run obligatorio). Si no sale nada, **vídeos**.

---

## 1. Preparación (T −30 min)

1. **Dos perfiles de Chrome**, ambos con zoom al 125 %:
   - **Laura** → `laura.p@vernedev.onmicrosoft.com`. Pestañas:
     - A. FraSoHome-Comercial › Documentos: `https://vernedev.sharepoint.com/sites/FraSoHome-Comercial/Shared%20Documents`
     - B. Teams o Copilot (solo si el índice está listo)
   - **Admin** → `admin@vernedev.onmicrosoft.com`. Pestañas:
     - C. Purview › Etiquetas: `https://purview.microsoft.com/informationprotection/informationprotectionlabels/sensitivitylabels`
     - D. Purview › Unified Catalog › dominio «FraSoHome Comercial» › Términos del glosario
     - E. Copilot Studio › agente: `https://copilotstudio.microsoft.com/environments/Default-c2c0e5ea-f0e8-4934-8f1c-d8260ba230d7/bots/c134a0a8-07da-f111-84e8-000d3a4a5d73/overview`
2. **Vídeos de respaldo** de las demos 0, 1, 2 y 3 abiertos en otra ventana.
3. **Pre-run de la demo 4** en la pestaña E (las 4 preguntas de la sección 6). Pulsa *Nueva sesión de prueba* al terminar para que el panel quede limpio.
4. **Glosario en Borrador** (pestaña D): «Cliente activo» debe decir *Borrador*. Ya lo está.
5. Teams: compartir **ventana** (no pantalla), notificaciones fuera.

---

## 2. Demo 0 · La respuesta perfecta (slides 3–4)

> Tus slides 3 y 4 están **ocultas** en tu versión del deck: muéstralas o salta directamente al navegador.

| Paso | Dónde | Qué haces |
|---|---|---|
| 1 | Laura · pestaña A | Botón **Copilot** (arriba a la derecha del sitio) |
| 2 | Copilot del sitio | Pega el prompt |
| 3 | — | Lee la respuesta en voz alta y pasa a la slide 4 |

```
¿Cuántos clientes activos tenía FraSoHome al cierre de 2025 y cómo evolucionaron las ventas netas en el cuarto trimestre respecto al tercero?
```

**Debe salir:** 49 clientes y −2,6 %, citando `Informe_Comercial_Q4_2025_FINAL.pptx`.
**Si dice «no encuentro información»** → índice aún no listo → vídeo.

---

## 3. Demo 1 · Bibliotecas sin taxonomía (slides 17–18)

| Paso | Dónde | Qué haces / enseñas |
|---|---|---|
| 1 | Laura · pestaña A | Raíz de Documentos: carpetas `Antiguo/`, `Comité/`, `Definitivos/`, `Varios/` |
| 2 | Misma vista | Señala que solo hay columnas **Nombre / Modificado / Modificado por** |
| 3 | Entra en `Definitivos/` | Está `FS-KB-01_Politica_Devoluciones_v1.3.docx` (45 días) |
| 4 | Entra en `Antiguo/` | Está `FS-KB-02_Politica_Devoluciones_v1.2.docx` (30 días) y es el **último modificado** |
| 5 | Copilot del sitio | Pega el prompt |

```
¿Cuál es el plazo de devolución para compras online?
```

**Debe salir:** 30 días citando FS-KB-02 (o 45: es aleatorio).
**Plan B:** si sale 45, repítela pidiendo que cite; si sigue, vídeo y «la respuesta varía entre ejecuciones».

---

## 4. Demo 2 · Etiquetas que nadie mantiene (slides 19–22)

**Parte en directo (admin), funciona hoy:**

| Paso | Dónde | Qué enseñas |
|---|---|---|
| 1 | Admin · pestaña C | Clic en **Altamente confidencial – Finanzas** → panel lateral: *Access control* (cifrado) |
| 2 | Mismo panel › *Edit label* › *Access control* (sin guardar) | Permisos: **FS-Finanzas** como Co-Author. Laura no está. **Cancela** al salir |
| 3 | Laura · pestaña A › `Definitivos/` | FS-KB-03 con el **candado/etiqueta**. Si Laura intenta abrirlo, no puede |

**Mini-demo «comparar» (slide 19) y pregunta (slide 20), Copilot del sitio como Laura (solo con índice):**

```
Compara cómo definen y calculan las "ventas netas" los documentos de este sitio y dime en qué discrepan.
```

```
¿Cuál es la definición oficial de ventas netas en FraSoHome?
```

**Debe salir:** discrepancias entre el PPT y los Excel, y **nunca** FS-KB-03.
**Slide 22**: tus cifras (14 etiquetas / 3 en uso…) son del escenario. En vernedev hay 6 etiquetas. Dilo como «en FraSoHome» y no enseñes el contador del tenant.

---

## 5. Demo 3 · Términos sin dueño (slides 23–25)

**Pregunta (Copilot del sitio como Laura, solo con índice):**

```
¿Qué es un cliente activo en FraSoHome?
```

**Glosario (admin, en directo):**

| Paso | Dónde | Qué enseñas |
|---|---|---|
| 1 | Admin · pestaña D | Término **Cliente activo** → estado **Borrador** |
| 2 | Detalle del término (propietarios / contactos) | Solo figura el admin como propietario; nadie de negocio |

**El procedimiento en tres cabezas (Copilot del sitio, solo con índice):**

```
Un cliente devuelve en Gran Vía un pedido online que pagó con tarjeta y con puntos. ¿Cómo hago el reembolso?
```

**Debe salir:** un procedimiento inventado a partir de FS-KB-01, 04 y 07.

---

## 6. Demo 4 · El después (slides 36–38) — EN DIRECTO

**Antes de la demo (opcional, 20 s, admin · pestaña D):** publica «Cliente activo» (*Publicar*) para enseñarlo con dueño.
Si no quieres arriesgar, cuenta que está publicado y enséñalo en la slide.

| Paso | Dónde | Qué haces |
|---|---|---|
| 1 | Admin · pestaña E | Enseña 10 s **Conocimientos**: FraSoHome-KB-Oficial + los documentos vigentes (FS-KB-02 no está) |
| 2 | Enseña **Información general › Instrucciones** | Señala «pregunta qué definición…» y «remite a FS-KB-00» |
| 3 | Botón **Probar** › *Nueva sesión de prueba* | Lanza las 4 preguntas |

| # | Pega | Debe salir (validado hoy) |
|---|---|---|
| 1 | `¿Cuál es el plazo de devolución para compras online?` | **45 días naturales**, cita FS-KB-01 v1.3 VIGENTE |
| 2 | `¿Cuántos clientes activos tenía FraSoHome al cierre de 2025?` | **100**, declarando periodo y la definición de FS-KB-03. ⚠ Hoy **no preguntó** qué definición querías |
| 3 | `¿Cómo evolucionaron las ventas netas en el Q4 respecto al Q3?` | **+2,5 %** (273.514 € → 280.441 €), con la fórmula oficial |
| 4 | `Un cliente devuelve en tienda un pedido online que pagó con tarjeta y con puntos. ¿Cómo hago el reembolso?` | «No hay un procedimiento documentado… **consulta a Jorge T. (Atención al cliente)**», citando FS-KB-00 |

**Si en la 2 no pregunta** (lo más probable): no lo vendas como que pregunta. Di:
*«Fijaos en que no se inventa la definición: aplica la oficial y te dice cuál ha usado.»*
Si quieres forzar la pregunta, lanza antes: `¿Qué es un cliente activo?`

**Ojo con dos cosas que no debes decir hoy:**
- Que el agente **filtra por la columna Estado = Vigente**: Copilot Studio solo filtra por propiedades estándar y, además, hoy responde con los ficheros subidos porque KB-Oficial no está indexado. Di «solo ve la biblioteca oficial curada».
- Que lo estás usando **como Laura**: el panel de prueba corre como admin. Con ficheros subidos da igual (no hay permisos que recortar), pero no lo afirmes.

**Después de la sesión:** vuelve a dejar «Cliente activo» en Borrador si lo publicaste.

---

## 7. Plan B rápido

| Si… | Haz |
|---|---|
| Copilot del sitio no encuentra nada | Vídeo de esa demo: «el tenant de demo se montó ayer y el índice aún no ha llegado; esto también es deuda: lo que no está indexado no existe para Copilot» |
| El agente tarda >20 s | Espera; si falla, *Nueva sesión de prueba* y repite. Segundo fallo → slide 37 |
| Purview tarda en cargar | Enseña la etiqueta desde el candado de FS-KB-03 en SharePoint |
| Teams cae | El moderador pone el vídeo completo |

## 8. Al terminar (limpieza, cuando quieras)

No hace falta hoy. Cuando quieras desmontar: `DESPLIEGUE.md` › sección 7. La limpieza también devuelve la
licencia de Copilot al admin y borra el agente, el dominio de gobierno y las etiquetas.
