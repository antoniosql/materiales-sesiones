# Bizz Summit 2026 — Madrid

## La sesión

**De la jungla de agentes al control plane: gobierno real de Copilot Studio con Agent 365**

| | |
|---|---|
| Ponente | Antonio José Soto Rodríguez |
| Cuándo | **Sábado 3 de octubre de 2026, 11:00** |
| Duración | **50 minutos, Q&A incluido** |
| Sede | U-tad, Calle Playa de Liencres 2 dupdo., 28290 Las Rozas (Madrid) |
| Nivel | 300 |
| Escenario de demos | FraSoHome — devoluciones omnicanal |

Logística: cena de speakers el **2 de octubre a las 21:00** en el Attica21 Las Rozas.
Código de registro de speaker: `SPEAKERBIZZ26`.

---

## Contenido de la carpeta

### `00_entrada/` — material recibido, no se edita

| Archivo | Qué es |
|---|---|
| `BizzSummit2026_PlantillaSpeakers.pptx` | Plantilla oficial, 38 slides. **La slide 5 (sponsors) no se elimina** |
| `Speakers_Info_2026.pdf` | Info de la organización: sede, hotel, cena, plantilla, Telegram |
| `Recursos.pptx` | Recursos de la organización |
| `banner-sesion.jpg` | Banner promocional de la sesión |
| `qr-sesion.png` | QR a la ficha de la sesión |
| `bizz-summit-2026-gobierno-agentes-indice-v2.md` | Índice v2 de la sesión, con los marcadores `«FraSoHome: …»` sin resolver |
| `enlaces.txt` | Enlaces de referencia |

### `01_trabajo/` — lo que generamos

| Archivo | Qué es |
|---|---|
| `00_escenario-frasohome.md` | **Léelo primero.** Cierra todos los marcadores `«FraSoHome: …»` del índice v2: el proceso, los dos agentes, las personas, el dato sensible, el test set |
| `01_guion-minuto-a-minuto.md` | **El entregable principal.** Minutaje 11:00–11:50 con reloj de pared, frases literales, las cuatro demos beat a beat, planes B, mapa de slides y checkpoints de tiempo |
| `02_guia-montaje-demos.md` | **Sustituida** por `demos/guia-despliegue-manual.html`. Se conserva como referencia del plan original |
| `BizzSummit2026_De_la_jungla_al_control_plane.pptx` | **El deck.** 34 slides sobre la plantilla oficial (30 visibles + 4 planes B ocultos), todas con notas del ponente |
| `_generador/` | Scripts que construyeron el deck a partir de la plantilla. Para regenerarlo: `build_structure.py` y luego `fill.py` |
| `demos/` | **Las cuatro demos.** `guia-despliegue-manual.html` con los escenarios revisados y el montaje manual, el agente de Copilot Studio como código y el agente externo en Claude Agent SDK. Tiene su propio README |

---

## Requisitos del equipo para las demos

El montaje del tenant es manual, desde los portales: no hace falta PowerShell ni módulos.
Solo el agente de Claude de la demo 4 tiene requisitos locales.

| Requisito | Para qué | Versión probada |
|---|---|---|
| Python 3 con el entorno virtual de `demos/agente-externo/fs-triage-devoluciones/.venv` | Ejecutar el agente | 3.14.8 |
| `claude-agent-sdk`, `httpx`, `python-dotenv` (`pip install -r requirements.txt`) | Dependencias del agente | SDK 0.2.163 |
| Un `claude.exe` nativo, indicado en `CLAUDE_CLI_PATH` del `.env` | El SDK lo exige en Windows. Sirve el de la extensión de VS Code | 2.1.287 |
| Claude Code en VS Code | Beat de observabilidad en vivo | |

- Con `BUZON_ORIGEN=local` el agente lee `demos/datos/buzon/correos.json` y no necesita Exchange
- Si se actualiza la extensión de VS Code, cambia la carpeta de `claude.exe`: corrige `CLAUDE_CLI_PATH`

---

## Decisiones tomadas

- **50 minutos totales con Q&A dentro** (44' de contenido + 6' de Q&A), no los 51' + Q&A aparte
  del índice v2. Manda la regla de la organización
- **Proceso único: devoluciones omnicanal.** Las cuatro demos son el mismo proceso a cuatro alturas
- **El agente de Copilot Studio hay que construirlo.** De ahí la guía de montaje
- **2 de octubre: demos rediseñadas.** Un solo tenant, el Default ya es Managed Environment y no hay
  margen para controles que tardan días. Se retiran los scripts de despliegue y se monta a mano.
  Detalle en `demos/guia-despliegue-manual.html`
- **Foco en Microsoft 365 y Agent 365.** Power Platform queda en dos slides, como lo que ya existía
  y no depende de Agent 365 (de cinco slides a dos; 28 visibles en total)
- Demo 1 · ¿Cuántos hay?: All agents con un agente de Agent Builder y el de Copilot Studio
- Demo 2 · ¿Qué hacen?: Purview DSPM for AI con las interacciones de los usuarios, incluido un IBAN
- Demo 3 · ¿Quién decide?: aprobar una solicitud de publicación, bloquear un agente y la política de creación
- Demo 4: el agente de Claude lee un buzón local; el registro en Agent 365 solo si el tenant lo tiene

## Pendiente

- [ ] Construir la checklist 30/60/90 de una página, generar su QR e insertarlo en la slide 31
- [ ] Sustituir las imágenes de relleno de las cuatro slides de plan B por capturas reales
- [ ] Incrustar los cuatro vídeos de plan B dentro del PowerPoint, no enlazados
- [ ] Subir el repositorio final de la presentación al repo público de sesiones
