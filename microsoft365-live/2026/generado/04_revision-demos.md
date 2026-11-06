# Revisión deck ↔ demos · Microsoft 365 Live 2026

*6 nov 2026 · Deck revisado: `Semantic-Debt_M365Live2026_AntonioSoto.pptx` (tu versión) · Repo: `semantic-debt-demos`*

## Resultado

Las cuatro demos se pueden reproducir con el repo **después de los cambios de esta revisión**. Tal como estaban, tres cosas impedían que salieran como dicen las slides:

1. **El «antes» se contaminaba con el «después».** Laura tiene acceso a los dos sitios: en Copilot Chat general, Copilot también encuentra la KB oficial (45 días, 100 clientes, +2,5 %) y las demos 0–3 no fallarían.
2. **El test set no cuadraba con la KB real.** Dos preguntas «tácitas» sí están documentadas, y en el sitio comercial faltaban las políticas que hacen que la TRC del antes sea 7/20.
3. **El agente no podía decir «pregunta a Jorge».** Ningún documento nombraba a Jorge, Lucía ni Paco.

Las cifras de las slides están **verificadas con los datos reales**: 47 / 49 / 89 / 100 / 132 / 135 clientes, 35 IDs fuera del CRM, y −2,6 % / +2,5 % / +4,4 % / +6,9 % en ventas netas.

## Hallazgos y qué se ha hecho

| # | Gravedad | Hallazgo | Corrección |
|---|---|---|---|
| 1 | Crítico | Copilot Chat ve FraSoHome-KB-Oficial durante las demos 0–3 | Las demos 0–3 pasan al **Copilot del sitio FraSoHome-Comercial**, que solo ve ese sitio. Deck v2: rótulos de las demos 0–3 y notas. RCD no sirve: no garantiza que el agente siga viendo el sitio |
| 2 | Crítico | T2 («¿quién aprueba la excepción VIP?») está en FS-KB-01 §11 (Store Manager). T3 lo cubren en parte FS-KB-04 y FS-KB-09 (sin ticket) | Test set: el VIP pasa a C8 (canónica, FS-KB-01 y FS-KB-07). Nuevas tácitas: T2 imputación por canal (Paco) y T3 informe Z (Lucía) |
| 3 | Alto | En Comercial solo estaban FS-KB-01/02/03: C4, C6, C7 y D2 no tenían fuente, así que la TRC del antes saldría ~3/20, no 7/20 | FS-KB-04 a 07 añadidos a `Comercial/Definitivos/` |
| 4 | Alto | El agente no puede derivar a Jorge, Lucía ni Paco | Nuevo **FS-KB-00 Mapa de dominios y responsables** (solo en KB-Oficial), con dueños y huecos conocidos. Instrucciones del agente y slide 36 actualizadas |
| 5 | Medio | FS-KB-02 v1.2 incluía la excepción VIP y las fechas de 2026 de la v1.3 | Se deriva sin la línea VIP y con fechas de 2025 |
| 6 | Medio | Mini-demo del síntoma 2: Laura no puede adjuntar FS-KB-03 (cifrado) | Notas de la slide 19: «compara los documentos de este sitio». Que falte el oficial es la entrada al síntoma 3 |
| 7 | Medio | Demo 2: el tenant no tiene una directiva de autoetiquetado que enseñar | Notas de la slide 20: es narrativa; enseña la etiqueta y su cifrado |
| 8 | Medio | Demo 1: el nombre `…_v1.3_Vigente.docx` ayudaba a Copilot a acertar los 45 días | En Comercial se sube como `FS-KB-01_Politica_Devoluciones_v1.3.docx` (como en la slide 17) y la v1.2 se sube la última, así que parece la más reciente |
| 9 | Bajo | D3 (ticket medio) no estaba duplicado en ningún documento | El Excel de tiendas incluye ticket medio con la misma definición |
| 10 | Bajo | C6 y C7 tenían palabras clave demasiado débiles («sku», «concilia») | Preguntas concretas: formato FSH-…, conciliación antes de las 12:00 |
| 11 | — | Faltaban los documentos para indexar | **13 documentos** en `semantic-debt-demos/documentos/`, generados con la KB y los datos reales |

## Pendiente de tu decisión

- **Diapositivas 3 y 4 ocultas.** La 3 es el paso a la Demo 0 y la 4 es «No es la pregunta que hiciste». Si las ocultaste para ir directo al navegador, perfecto; pero la 4 es la que explica el título. Te recomiendo enseñarla al volver de la demo.
- **Slide 22**: 14 etiquetas publicadas / 3 en uso / 0 con dueño / 2024 son cifras del escenario. El repo crea 2 etiquetas: ajusta la slide a lo que tenga el tenant.
- **Slides 29 y 38** (TRC 7/20 y 15/20): son el objetivo del diseño. Mídelas con `semdebt evaluate` el día −1 y pon la cifra real.
- **Slide 20** abrevia el fichero como `Informe_Comercial_Q4_FINAL.pptx`; en SharePoint es `Informe_Comercial_Q4_2025_FINAL.pptx`.

## Demo a demo

| Demo | Slides | Dónde | Lo despliega | Estado |
|---|---|---|---|---|
| 0 · La respuesta perfecta | 3–4 | Copilot del sitio Comercial | PPT de marketing (49 / −2,6 %) | ✔ |
| 1 · Bibliotecas sin taxonomía | 17–18 | SharePoint + Copilot del sitio | Carpetas, sin columnas, v1.2 frente a v1.3 | ✔ con aleatoriedad: graba el vídeo de respaldo |
| 2 · Etiquetas | 19–22 | Purview + Copilot del sitio | Etiqueta cifrada solo para FS-Finanzas | ✔ (si no hay API medidas, la etiqueta se aplica a mano) |
| 3 · Términos sin dueño | 23–25 | Copilot del sitio + glosario | «Cliente activo» en borrador | ✔ |
| 4 · El después | 36–38 | Agente de Copilot Studio | KB oficial con metadatos, FS-KB-00, glosario publicado | ✔ el primer montaje del agente es manual (luego, plantilla) |
| TRC | 29, 38 | `semdebt evaluate` | Test set de 20 preguntas | ✔ a medir |

## Ficheros

- `Semantic-Debt_M365Live2026_AntonioSoto_v2.pptx`: tu deck con los cambios de los puntos 1, 4, 6 y 7 (rótulos de las demos 0–3, notas de las slides 3, 17, 19, 20 y 25, y slide 36). El original no se ha tocado.
- `semantic-debt-demos/DESPLIEGUE.md`: guía de despliegue en un tenant con requisitos, registro de la app, calendario de día −3 a día 0, validación demo a demo y problemas frecuentes.
- `semantic-debt-demos/documentos/`: los 13 documentos.
