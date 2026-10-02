## Lo que hay en el tenant

| Área | Estado real |
|---|---|
| Licencias | E5 Developer (16 usuarios). Copilot y Agent 365 solo los tiene `admin@`. |
| Agentes | 41 identidades de agente en Entra, 39 de Copilot Studio de otras pruebas («Prueba sin autor», «test», «Agent»…). Ya existen el Asistente (publicado en Default), `FsTriageDevoluciones Identity`, el Atajo y la Calculadora. |
| Creadores | Todo lo de FraSoHome lo creó hoy Dev Admin, que es también el sponsor del Asistente y del agente de Claude. No hay ni Álvaro ni Marta. |
| Auditoría | Activa. Están registradas hoy tus conversaciones con el Atajo, el Asistente y la Calculadora. |
| Agente de Claude | Su telemetría **ya está en la auditoría de Purview**: 2 `InvokeAgent`, 46 `ExecuteToolBySDK` y 2 `InferenceCall`, con el tipo `CustomBuiltAgentsUsingSDK`. |
| DLP | «FraSoHome – Bloqueo IBAN en agentes» está activa sobre los prompts de Copilot. **No ha saltado ninguna vez**: el prompt del IBAN en el Atajo recibió respuesta normal. Probablemente el texto decía «cuenta» y no «IBAN», y la regla exige confianza alta. |
| DSPM | La única política creada es «Detect sensitive info added to AI sites», que vigila sitios de IA de terceros, no Copilot. No he podido comprobar si el IBAN aparece en Activity explorer. |
| Calculadora | **No está bloqueada.** No hay rastro del bloqueo y se usó después. |
| Sitio KB | Además de los documentos previstos, contiene FS-KB-02 (obsoleta) y **FS-KB-10 (prompt injection)**, que la guía decía no subir. |
| Repo | El commit `a7f5f47` metió en `main` la observabilidad y Work IQ. El `instrucciones.md` del agente externo contiene mi respuesta anterior en inglés. |

## Propuesta por demo

**Demo 1 · ¿Cuántos hay?** Usa la jungla real antes que la escenificada. Abre All agents sin filtrar y di algo como: *«Este es mi tenant de pruebas. Más de cuarenta agentes, y no recuerdo la mitad»*. Después filtra por FraSoHome.
- No digas «Marta lo creó en marzo»: la ficha mostrará «Dev Admin, 2 de octubre». Cuéntalo como un caso hipotético («imaginad que quien lo creó cambió de equipo…»).
- Antes de proyectar, revisa nombres como «UPV contabilidad» o «milsa-trillo», y entornos como FENIN o HIJOLUSA. Si alguno es de un cliente, llega a la pantalla ya filtrado.

**Demo 2 · ¿Qué hacen?** Lo seguro son las conversaciones con los tres agentes en DSPM Activity explorer o en Audit. El IBAN no está verificado.
- Si a las 9:30 sale, perfecto.
- Si no sale, no lo busques en vivo. Enseña la política de DLP y di: *«la política está; el prompt de ayer no la disparó porque…»*. Ese también es un mensaje honesto de gobierno.
- El informe de uso casi seguro estará vacío: déjalo en una frase.

**Demo 3 · ¿Quién decide?** El bloqueo de la Calculadora puede ser **real y en vivo**, porque no se ha hecho. No hay captura de anoche, así que avisa de que la vista del usuario tarda en reflejarlo.
- Comprueba a mano que la solicitud del Asistente está en Requests. No he podido verlo por API.
- Reasignar propietario aparece en la slide 22 pero no en la demo. Si te sobra tiempo, el Asistente sin owners en Entra es un buen ejemplo.

**Demo 4 · El otro agente.** La premisa «funciona y nadie lo ve» ya no es cierta: el agente está registrado y emitiendo telemetría. Además, el beat de «el diff solo añade» no funciona en vivo, porque el código ya está en `main`. Propuesta de antes y después, sin ejecutar nada:
1. **Antes:** el resumen ya generado y el `.env` con credenciales propias.
2. **Qué cambió:** `git diff 8242e3f a7f5f47 -- src/agent.py`, el diff real y ya hecho. Sin depender del LLM ni de la red.
3. **Después, el cierre fuerte:** una búsqueda en Purview Audit (`InvokeAgent`) que enseña juntos el Atajo (`DeclarativeAgent`), el Asistente (`CopilotStudio`) y `fs-triage` (`CustomBuiltAgentsUsingSDK`). Eso es literalmente *«el control plane no pregunta con qué lo construiste»*.
4. **Work IQ:** solo contado. Corrige la frase del guion: la skill no se salta en silencio. Con S2S se para con un mensaje, y para Python + Claude no existe un adaptador publicado. La idea a transmitir sigue siendo «delegado, y se decide antes».

## Qué mirar a las 9:30 (sin cambiar nada)

1. All agents: si aparecen el Atajo, la Calculadora, el Asistente y **el de Claude**. Si el de Claude no sale, el paso 3 de la demo 4 se apoya solo en Audit.
2. Que la solicitud del Asistente siga pendiente en Requests.
3. DSPM Activity explorer: si hay interacciones y si alguna lleva el IBAN.
4. Audit filtrado por `InvokeAgent`, guardado como búsqueda para la demo 4.
5. No hagas al Atajo ni al Asistente preguntas que puedan traer FS-KB-10 o FS-KB-02.
6. Cierra `instrucciones.md` y `.env` en VS Code salvo cuando quieras enseñarlos.



## Cómo se conecta

Ese panel es **Registry Sync** (Connected platforms). Para Anthropic se necesita esto:

1. **En la consola de Anthropic** (lo hace quien administre la plataforma):
   - Un workspace que **no** sea el Default, porque el Default no expone el ID de workspace que pide la conexión.
   - Dentro de ese workspace, un *environment* y un **Managed Agent**.
   - Una **API key con alcance de workspace**. Para crearla hace falta como mínimo el rol Developer.
   - Una sesión en la que alguien use el agente, para que haya actividad que traer.
2. **En el admin center** (lo que muestra tu captura): *Connect a platform* › **Anthropic Claude**, y después:
   - Introduces el workspace ID y la API key.
   - Pulsas *Verify authentication*.
   - Guardas la conexión.
   - Pulsas **Sync agents**. La sincronización es manual; no corre sola.
3. **Verificación:** el agente aparece en All agents y su pestaña **Activity** muestra sesiones, excepciones y tiempo de ejecución. La actividad tarda entre 5 y 10 minutos en llegar. La columna de usuarios sale como no disponible, porque Anthropic no aporta identidades de Entra.

Ten en cuenta que la API de Managed Agents está en beta, la integración es preview y la parte de observabilidad pertenece a Frontier.

## Diferencia con el agente que hemos creado

**Este conector no encontraría `fs-triage-devoluciones`.** Solo sincroniza Managed Agents, es decir, agentes que corren hospedados en la plataforma de Anthropic. El nuestro está hecho con el Claude Agent SDK y corre en tu portátil o en un contenedor; para Anthropic solo existen las llamadas al modelo, no el agente.

| | Registry Sync (este panel) | Agent 365 SDK (lo que hicimos) |
|---|---|---|
| Dónde vive el agente | En la plataforma de Anthropic (Managed Agents) | Donde quieras: portátil, contenedor, cualquier nube |
| Dirección | **Pull**: Microsoft lee la API de Anthropic | **Push**: el agente se registra y emite telemetría |
| Cambios en el código | Ninguno | Sí: el blueprint, el resolver de tokens y los scopes de OTel |
| Identidad | Una ficha importada en el registro. La documentación no habla de que se cree un Entra Agent ID | Blueprint, **Entra Agent ID** propio y sponsor |
| Credencial | API key de Anthropic guardada en Microsoft | Credencial del blueprint en Entra |
| Telemetría | Sesiones, excepciones y tiempo de ejecución en la pestaña Activity | Spans completos (invocación, inferencia y cada tool) en Purview Audit y Defender. Ya lo hemos comprobado |
| Usuarios | No disponibles | Usuario o sponsor como llamante |
| Acceso a datos de M365 | Ninguno | Work IQ (Mail y Word) con permisos delegados |
| Esfuerzo | Unos 10 minutos de configuración | Trabajo de desarrollo |

En una frase: **Registry Sync te deja ver un agente que vive en otra plataforma; el SDK convierte tu agente en una identidad gobernada dentro de Microsoft.** El primero sirve para inventariar, y el segundo para gobernar lo que haga dentro del tenant.

## Para la sesión (sin cambiar las demos)

Este panel encaja como una mención de 20 segundos en la demo 4, sin conectar nada en vivo: *«Hay dos puertas: si el agente vive en Bedrock, Vertex o los Managed Agents de Anthropic, lo sincronizas desde aquí. Si lo escribió David en su portátil, la única puerta es el SDK»*. Además responde a la pregunta de Q&A sobre agentes de otras nubes, que ya está en el guion.

Conectarlo de verdad mañana obligaría a crear un workspace y un Managed Agent en Anthropic esta noche, y la actividad llega en preview y con retraso. No lo recomiendo para el día.

Fuentes:
- [Connected platforms in Microsoft Agent 365](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/connected-platforms)
- [Connect Anthropic Claude Managed Agents to Microsoft Agent 365](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/connected-platforms-anthropic-claude)
- [Third-party agent observability with Microsoft Agent 365 (Frontier)](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/third-party-agent-observability)

Las ejecuciones del agente de Claude ya están en la auditoría. Las encontré buscando por el ID de su identidad de agente, `3ee28114-5ad4-40c2-8d8b-82e0578b50a4`, y aparecieron 2 `InvokeAgent`, 46 `ExecuteToolBySDK` y 2 `InferenceCall`.

## En el portal de Purview

**purview.microsoft.com › Solutions › Audit › New search**, con estos valores:

| Campo | Valor |
|---|---|
| Date and time range | Desde ayer hasta ahora. Las ejecuciones son del 2 de octubre por la tarde |
| Keyword search | `3ee28114-5ad4-40c2-8d8b-82e0578b50a4` |
| Record types *(opcional)* | `AIInvokeAgent`, `AIExecuteTool` y `AIInferenceCall` |
| Search name | `fs-triage-devoluciones` |

Con eso salen todas las operaciones del agente: la invocación, cada tool y la inferencia. Si filtras por usuario, recuerda que todas aparecen a nombre de `admin@vernedev.onmicrosoft.com`, el sponsor.

**Para el cierre de la demo 4** necesitas otra búsqueda guardada, con los tres agentes juntos:

| Campo | Valor |
|---|---|
| Record types | Solo `AIInvokeAgent` |
| Keyword search | Vacío |

Al abrir cada fila, el campo **PlatformTargetAgentType** distingue el origen:
- `DeclarativeAgent`: el Atajo y la Calculadora (Agent Builder).
- `CopilotStudio`: el Asistente.
- `CustomBuiltAgentsUsingSDK`: `FsTriageDevoluciones Identity`.

La búsqueda tarda unos minutos en completarse, así que lánzala y guárdala antes de las 10:45. Mañana solo tendrás que abrir los resultados.

## Por PowerShell, como plan B

Es lo mismo que usé yo para comprobarlo:

```powershell
Connect-ExchangeOnline -UserPrincipalName admin@vernedev.onmicrosoft.com -DisableWAM
Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-2) -EndDate (Get-Date) `
  -FreeText "3ee28114-5ad4-40c2-8d8b-82e0578b50a4" -ResultSize 200 |
  Group-Object RecordType, Operations | Select-Object Count, Name
```

Si prefieres enseñarlo en Defender Advanced Hunting (tabla `CloudAppEvents`), puede tardar más en indexarse. Compruébalo a las 9:30 antes de contar con ello.