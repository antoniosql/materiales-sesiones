# Azure Cloud Lab 2026

## La sesión

**Identidad, acceso y ciclo de vida de agentes con Microsoft Entra Agent ID**

| | |
|---|---|
| Ponente | Antonio Soto |
| Cuándo | **Jueves 3 de diciembre de 2026, 17:00 (hora peninsular)** |
| Formato | Online, en directo · ~50 min con demos y Q&A dentro |
| Idioma | Español |
| Nivel | 300 |
| CFS | https://sessionize.com/azurecloudlab2026 |
| Escenario de demos | FraSoHome (mismos personajes que el Bizz Summit 2026) |

## Estructura

- `entrada/cfp/convocatoria.md` — datos de la convocatoria
- `entrada/plantilla/AzureCloudLab2026.pptx` — plantilla oficial del evento
- `generado/01_propuestas-sessionize.md` — las propuestas enviadas (la seleccionada es la 5)
- `generado/02_guion-sesion.md` — guion minuto a minuto, escenario, montaje (Anexo B) y lista *Por verificar* (Anexo C)
- `generado/03_slides.md` — descripción de las 36 slides + 4 de plan B y sistema visual
- `generado/04_diagramas-drawio.md` — cómo están hechos los 5 diagramas e iconos oficiales que usan
- `generado/diagramas/` — D1–D5 en `.drawio` editable y `.png` de referencia; `oscuro/` con las variantes que usa el deck
- `generado/05_presentacion-entra-agent-id.pptx` — el deck (36 + 4 de plan B ocultas), con notas del orador. Copia en OneDrive: `Presentaciones\Eventos\Azure Cloud Lab\2026\AzureCloudLab2026-EntraAgentID.pptx`

- `agent-id-demos/` — **scripts de las demos** (autocontenido): Bicep, CLI `agentid` (Graph + az), servidor MCP, agente `fs-triage-devoluciones`, agente de Copilot Studio, datos del caso, `setup.ps1` y `.env.example`. Guía en `agent-id-demos/DESPLIEGUE.md`; probado en tenant real el 27/11/2026

## Estado

- [x] Propuesta aceptada
- [x] Guion v1
- [x] Descripción de slides v1
- [x] Diagramas D1–D5 v1
- [x] Franja, formato (directo) y plantilla
- [ ] Confirmar plataforma y moderador
- [ ] Revisar el Anexo C del guion (Foundry, sponsor tasks en mover, ID Protection, report-only…)
- [x] Scripts de las demos (`agent-id-demos/`)
- [x] Prueba completa en tenant real (27/11/2026): las 4 demos funcionan; ver Anexo C del guion
- [x] Montar el tenant (vernedev) con `agentid` — falta solo la política de inactividad, a mano
- [ ] Grabar los dos clips (demo 2 y demo 4, beat 1) y las capturas de plan B
- [x] Deck en PowerPoint v1
- [ ] Capturas de plan B (slides 37–40) y QR apuntando al repositorio final
- [ ] QR: checklist + diagramas + repositorio de `fs-triage-devoluciones`
