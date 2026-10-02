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
| `02_guia-montaje-demos.md` | Qué hay que construir y cuándo, del 13 de septiembre al 3 de octubre |
| `BizzSummit2026_De_la_jungla_al_control_plane.pptx` | **El deck.** 34 slides sobre la plantilla oficial (30 visibles + 4 planes B ocultos), todas con notas del ponente |
| `_generador/` | Scripts que construyeron el deck a partir de la plantilla. Para regenerarlo: `build_structure.py` y luego `fill.py` |
| `demos/` | **El pack de despliegue de las cuatro demos.** Tenant configurable, ocho etapas por CLI, scripts de uso para generar telemetría y el agente externo en Claude Agent SDK. Tiene su propio README |

---

## Requisitos del equipo para las demos

`demos/deploy.ps1` exige **PowerShell 7** (`#requires -Version 7.0`); en Windows PowerShell 5.1 falla
con `ScriptRequiresUnmatchedPSVersion`. Ejecútalo desde `pwsh`, no desde `powershell.exe`.

| Requisito | Instalación | Versión probada |
|---|---|---|
| PowerShell 7 (`pwsh`) | `winget install --id Microsoft.PowerShell --source winget` | 7.6.6 |
| Azure CLI (`az`) | `winget install --id Microsoft.AzureCLI --source winget` | 2.90.0 |
| Power Platform CLI (`pac`) | `winget install --id Microsoft.PowerAppsCLI --source winget` | 2.12.2 |
| Módulo `Microsoft.PowerApps.Administration.PowerShell` | `Install-Module Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser` | 2.0.218 |
| Módulo `Microsoft.Graph.Sites` | `Install-Module Microsoft.Graph.Sites -Scope CurrentUser` | 2.41.0 |
| Módulo `Microsoft.Graph.Files` (etapa de SharePoint) | `Install-Module Microsoft.Graph.Files -RequiredVersion 2.41.0 -Scope CurrentUser` | 2.41.0 |
| Módulo `Microsoft.Graph.Users.Actions` (`uso/Send-CorreosDevolucion.ps1`) | `Install-Module Microsoft.Graph.Users.Actions -RequiredVersion 2.41.0 -Scope CurrentUser` | 2.41.0 |
| Módulo `ExchangeOnlineManagement` | `Install-Module ExchangeOnlineManagement -Scope CurrentUser` | 3.10.1 |

- Los módulos se instalan **desde `pwsh`**: los instalados desde Windows PowerShell 5.1 van a
  `Documents\WindowsPowerShell\Modules`, ruta que PowerShell 7 no carga
- Todos los módulos `Microsoft.Graph.*` en la **misma versión**; mezclar versiones da conflictos de ensamblados
- **Inicio de sesión sin WAM**: desde el terminal integrado de VS Code la ventana de WAM queda oculta y
  la autenticación se cancela. Ejecutar una vez en `pwsh`:
  `Import-Module Microsoft.Graph.Authentication; Set-MgGraphOption -DisableLoginByWAM $true`
  (Exchange y Purview ya llevan `-DisableWAM` en los scripts). Alternativa: `Connect-MgGraph -UseDeviceCode`
  en el mismo terminal antes de lanzar el deploy
- Tras instalar `az` y `pac` hay que **reabrir VS Code o el terminal** para que entren en el PATH
- Terminal de VS Code: perfil por defecto apuntando a `pwsh.exe`
  (`terminal.integrated.defaultProfile.windows`). Si `pwsh` viene de la Microsoft Store, la ruta es
  `${env:LOCALAPPDATA}\Microsoft\WindowsApps\pwsh.exe`, no `C:\Program Files\PowerShell\7\pwsh.exe`
- Comprobación: `./deploy.ps1 -ConfigPath ./config.local.json -ValidateOnly` no debe mostrar ninguna `x`

---

## Decisiones tomadas

- **50 minutos totales con Q&A dentro** (44' de contenido + 6' de Q&A), no los 51' + Q&A aparte
  del índice v2. Manda la regla de la organización
- **Proceso único: devoluciones omnicanal.** Las cuatro demos son el mismo proceso a cuatro alturas
- **El agente de Copilot Studio hay que construirlo.** De ahí la guía de montaje
- La demo 2 (bloqueo por Purview) **se graba por defecto**; solo va en vivo si se prueba
  en la sala esa misma mañana
- El único beat que debe ocurrir en vivo sí o sí es **ver los dos agentes juntos en *All agents***

## Pendiente

- [ ] Construir la checklist 30/60/90 de una página, generar su QR e insertarlo en la slide 31
- [ ] Sustituir las imágenes de relleno de las cuatro slides de plan B por capturas reales
- [ ] Incrustar los cuatro vídeos de plan B dentro del PowerPoint, no enlazados
- [ ] Subir el repositorio final de la presentación al repo público de sesiones
