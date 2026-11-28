# Despliegue de las demos · Entra Agent ID (Azure Cloud Lab 2026)

Guía de principio a fin: requisitos, despliegue, pasos manuales, ensayo, día de la sesión y limpieza.

---

## 1 · Requisitos

### Herramientas

| Herramienta | Para qué |
|---|---|
| Python 3.10+ | CLI `agentid` |
| Azure CLI (`az`) 2.67+ con Bicep | Infraestructura, imágenes (`az acr build`), RBAC, Storage, Container Apps |
| Navegador con tres perfiles | *Nuria (admin)*, *Lucía* y *Jorge*, para las demos |

No hace falta Docker local: las imágenes se construyen en ACR.

### Tenant y licencias

- Tenant de demo con **Microsoft 365 E7**, o **Agent 365 + Entra ID P1 (o M365 E3)**. Sin eso no hay acceso
  condicional para agentes ni tareas de sponsor en Lifecycle Workflows (slide 31). Vale una trial.
- **Lucía y Jorge** necesitan buzón (licencia con Exchange Online): reciben el correo del workflow en la demo 4.
- Las licencias se asignan **a mano** (los scripts no compran ni asignan licencias).

### Roles de Nuria (`ADMIN_UPN`)

| Rol de Entra | Para |
|---|---|
| Agent ID Administrator | Blueprints, identidades de agente, sponsors y owners |
| Conditional Access Administrator | CA-AG-01 y CA-AG-02 |
| Lifecycle Workflows Administrator | LW-Mover-Sponsors y la política de inactividad |
| Attribute Definition Administrator y Attribute Assignment Administrator | `FraSoHome.Carril`. **Ni Global Administrator los tiene por defecto** |
| Security Operator | Confirmar comprometido y limpiar el riesgo del agente |
| User Administrator y Groups Administrator | Personas y grupos de M365 |

En Azure: **Owner** (o Contributor + User Access Administrator) del grupo de recursos o de la suscripción.

### Permisos de Graph (delegados)

El CLI inicia sesión como Nuria con código de dispositivo en la app pública *Microsoft Graph Command Line Tools*
(`GRAPH_CLIENT_ID`). La primera vez pide consentimiento para todo de una vez:

`User.ReadWrite.All` · `Group.ReadWrite.All` · `Directory.Read.All` · `Application.Read.All` ·
`AgentIdentityBlueprint.Create` · `AgentIdentityBlueprint.ReadWrite.All` · `AgentIdentityBlueprint.AddRemoveCreds.All` ·
`AgentIdentityBlueprintPrincipal.Create` · `AgentIdentity.Create.All` · `AgentIdentity.ReadWrite.All` ·
`CustomSecAttributeDefinition.ReadWrite.All` · `CustomSecAttributeAssignment.ReadWrite.All` · `Policy.Read.All` ·
`Policy.ReadWrite.ConditionalAccess` · `LifecycleWorkflows.ReadWrite.All` · `IdentityRiskyAgent.ReadWrite.All` ·
`AuditLog.Read.All`

Si el tenant rechaza alguno (`invalid_scope`), el CLI reintenta solo con los que pide cada comando.

### Región

`LOCATION=swedencentral` por defecto: tiene Foundry Agent Service, el modelo `gpt-4.1-mini` y Container Apps.
Si cambias de región, comprueba las tres cosas.

---

## 2 · Instalación

```powershell
cd C:\repos\entra-agent-id-demos
powershell -ExecutionPolicy Bypass -File .\setup.ps1   # .venv, dependencias, .env, Git, herramientas y pruebas
.\.venv\Scripts\Activate.ps1
notepad .env                                            # TENANT_ID, SUBSCRIPTION_ID, NAME_SUFFIX (marcadas con «←»)
az login --tenant <TENANT_ID>
az account set --subscription <SUBSCRIPTION_ID>
agentid check
```

Sin el script: `python -m venv .venv`, `.\.venv\Scripts\Activate.ps1` y `pip install -r requirements-dev.txt` seguido de
`pip install -e . --no-deps`. Todas las variables están explicadas en `.env.example`.

---

## 3 · Despliegue

`agentid desplegar` ejecuta los pasos 1–13 en orden. Paso a paso, por si uno falla o quieres repetirlo:

| # | Comando | Qué hace | Notas |
|---|---|---|---|
| 1 | `agentid infra` | `infra/main.bicep`: Storage `stfrasohome<sufijo>` (sin claves), contenedores `devoluciones`, `buzon-devoluciones` y `triage-resultados`, Log Analytics, entorno de Container Apps, ACR, MIs `id-fs-triage` e `id-frasohome-acrpull` y, si `DEPLOY_FOUNDRY=true`, cuenta + proyecto `fs-agentes-prj` + modelo | 5–10 min. Nuria recibe *Storage Blob Data Contributor* y *Foundry User* |
| 2 | `agentid personas` | Jorge, Álvaro, Lucía, Marta y David con departamento y manager; grupos de M365 *Plataforma de agentes* y *Responsables de tienda* | Las contraseñas se muestran **una vez**. Usuarios que ya existan se reutilizan |
| 3 | `agentid atributos` | Conjunto `FraSoHome`, atributo `Carril` con valores `Playground`, `Equipo`, `Produccion`, `Enterprise` | 403 = faltan los roles de atributos |
| 4 | `agentid datos` | `devoluciones_online.csv` y `productos.csv` a `devoluciones`; 18 correos a `buzon-devoluciones` | Usa `--auth-mode login` (no hay claves) |
| 5 | `agentid blueprint` | Blueprint **FraSoHome · Agentes de operaciones** (sponsor: grupo Plataforma; owners: Nuria y David), su principal y la **federated credential** sobre `id-fs-triage` | Sin secretos ni certificados |
| 6 | `agentid identidad` | Identidad **fs-triage-devoluciones** hija del blueprint · sponsor Lucía · owner David · `Carril = Produccion` | |
| 7 | `agentid rbac` | *Storage Blob Data Reader* en `buzon-devoluciones` y *Contributor* en `triage-resultados`, **a la identidad de agente** | Nunca a la MI |
| 8 | `agentid imagenes` | `az acr build` de las dos apps | 2–4 min |
| 9 | `agentid apps` | `infra/apps.bicep`: `ca-fs-devoluciones-mcp` (ingress público, `/mcp`) y `ca-fs-triage` (sin ingress) | Guarda la URL del MCP en el estado |
| 10 | `agentid foundry conexion` | Conexión **fs-devoluciones-mcp**: *remote tool*, auth **identidad de agente**, audience `https://storage.azure.com` | Va por ARM (`az rest`): no necesita azd. Si falla, imprime los valores para el portal |
| 11 | `agentid foundry agente` | Agente **frasohome-returns** con la herramienta MCP | Nace con identidad propia (modelo actual de Foundry) |
| 12 | `agentid acceso` | **CA-AG-01** (activa) y **CA-AG-02** (report-only) | Estados en `.env` |
| 13 | `agentid ciclo` | **LW-Mover-Sponsors**: mover por cambio de *department*, avisa al manager (cc Jorge) y a los co-sponsors | No transfiere: es la recomendación de la slide 28 |

### Pasos manuales

1. **Copilot Studio (puerta 1):** crea el Asistente de Devoluciones siguiendo [copilot-studio/README.md](copilot-studio/README.md)
   y después `agentid copilot`.
2. **Identidad compartida de Foundry (demo 2):** `agentid foundry identidades`, copia la identidad del proyecto en
   `FOUNDRY_SHARED_IDENTITY_ID` y ejecuta `agentid foundry antes`. Deja el rol solo en la identidad compartida.
   > Con el modelo actual de Foundry, el agente nace con su propia identidad. La identidad compartida del proyecto
   > existe para los agentes del modelo anterior. Si en tu proyecto no aparece, crea un agente del modelo anterior
   > y usa su identidad como «la de desarrollo».
3. **Política de inactividad por defecto:** Entra → ID Governance → Lifecycle Workflows → Lifecycle policies →
   Agent ID → *Enable policy*, con un buzón de fallback. No tiene licencia y no hay API documentada.
4. **Licencias** (ver §1) y **diagnostic settings** de Entra hacia Log Analytics si vas a usar `kql/consultas.kql`.

---

## 4 · Comprobar que todo funciona (antes del primer ensayo)

| Qué | Cómo | Resultado esperado |
|---|---|---|
| El agente propio pide token sin secretos | `agentid demo4 logs` | `✔ correo-00X.json → R04 Daño en transporte`… y «Resumen diario actualizado» |
| Inicio de sesión del agente | Entra → Sign-in logs → filtro *Agent type = Agent Identity* | `fs-triage-devoluciones` con su blueprint padre |
| Demo 2 falla como debe | `agentid foundry preguntar` | `MCP fs-devoluciones.devoluciones_online → ERROR 403 AuthorizationPermissionMismatch` |
| Demo 2 se arregla | `agentid demo2 arreglar`, esperar ~5 min, `agentid foundry preguntar` | Recuento de devoluciones de iluminación por motivo |
| Demo 4 bloquea | `agentid demo4 comprometer`, esperar, `agentid demo4 reiniciar`, `agentid demo4 logs` | `🛑 Entra ha denegado el token del agente: … 53003` |
| Workflow | `agentid demo4 mover` | Correo en el buzón de Lucía (manager de Marta) y de Jorge (en copia) |
| Todo vuelve al principio | `agentid ensayo reiniciar` | Marta sponsor, rol solo en la identidad compartida, sin riesgo |

---

## 5 · El día de la sesión (jueves 3 de diciembre, 17:00)

| Cuándo | Qué |
|---|---|
| **Martes** | Grabar los dos clips: éxito de la demo 2 tras el RBAC (20") y bloqueo de la demo 4 (60"). Capturas de plan B (slides 37–40) |
| **Jueves, 12:00** | `agentid ensayo reiniciar` y comprobar con `agentid ensayo estado` |
| **Jueves, 15:30** | Asistente de Devoluciones: dos o tres preguntas en Teams como Álvaro (inicios de sesión recientes para la demo 1). `agentid demo4 logs`: el agente procesa correos |
| **Jueves, 16:30** | Ventanas de portal abiertas en el orden de las demos. Terminal con el venv activado y la fuente a 18 pt |

### Comandos en directo

| Demo · beat | Comando |
|---|---|
| 2 · beat 1 | `agentid foundry preguntar` (o la pregunta en el playground) |
| 2 · beat 3 | `agentid demo2 comando` imprime el `az role assignment create` con los IDs reales para teclearlo; `agentid demo2 arreglar` lo ejecuta |
| 3 · beat 3 | `agentid demo4 logs` o el *Log stream* del portal |
| 4 · beat 1 | Va grabado. Para grabarlo: `demo4 comprometer` → esperar → `demo4 reiniciar` → `demo4 logs` |
| 4 · beat 2 | `agentid demo4 mover` |
| 4 · beat 3 | En el portal, o `agentid demo4 sponsors` |

Después de la sesión: `agentid ensayo reiniciar` si vas a reutilizar el tenant, o `agentid cleanup --si`.

---

### Entre ensayos: sin coste

Las dos Container Apps tienen una réplica siempre encendida, y es casi todo el coste fijo (en torno a 1 € al día entre las dos).
Páralas cuando no estés ensayando:

```powershell
agentid pausa parar      # detiene ca-fs-devoluciones-mcp y ca-fs-triage
agentid pausa estado     # Running / Stopped
agentid pausa arrancar   # las vuelve a arrancar (la URL del MCP no cambia)
```

`agentid ensayo reiniciar` las arranca si están paradas, así que el jueves a las 12:00 no hay que acordarse.
Lo demás apenas cuesta parado: ACR Basic (~0,15 €/día), Storage y Log Analytics. Foundry solo cobra por uso.

## 6 · Limpieza

```powershell
agentid cleanup        # explica qué va a borrar
agentid cleanup --si   # borra políticas, workflow, identidad, blueprint, usuarios y grupos creados, y el grupo de recursos
```

No se borran: el atributo `FraSoHome.Carril` (Entra solo deja desactivarlo), los agentes de Copilot Studio y de
Foundry (se borran en sus portales; al borrar el de Copilot Studio se borra su Agent ID) ni nada que ya existiera.

---

## 7 · Problemas conocidos

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `AADSTS700016` / `AADSTS7000112` al pedir T1 | La federated credential no apunta al `principalId` de `id-fs-triage`, o el blueprint está deshabilitado | `agentid blueprint` la revisa y la crea si falta |
| `AADSTS70021` en el paso 2 del token | El `subject` de la federated credential no coincide con la MI que usa el contenedor | Comprueba `AZURE_CLIENT_ID` de `ca-fs-triage` = client id de `id-fs-triage` |
| 403 en Storage con el agente bien configurado | Propagación de RBAC | Espera 5–10 min. Por eso el éxito de la demo 2 va en clip |
| CA-AG-01 no bloquea | El riesgo aún no ha llegado al acceso condicional: los primeros minutos alterna bloqueo y éxito | Compromete **al menos 10 min antes** de enseñarlo. `ca-fs-triage` renueva el token cada 120 s, no hace falta reiniciar |
| `confirmCompromised` devuelve error | API beta de riesgo de agentes | Entra → ID Protection → Risky agents → Confirm compromised |
| Sponsors: 403 al añadir | La API de sponsors para identidades de agente pide Agent ID Administrator | Comprueba el rol de Nuria o hazlo en el portal |
| `403 … not licensed` / `Insufficient license` en `acceso`, `ciclo` o `demo4` | Faltan licencias (ver §1) | El CLI lo dice y sigue; activa la trial y repite el comando |
| `python: can't open file '/app/main.py': Permission denied` en `ca-fs-triage` | Imagen construida desde un disco que deja los ficheros en modo 700 | Corregido: los Dockerfile hacen `chmod -R a+rX /app` |
| `RequestConflict` en `aif-…/fs-agentes-prj` al desplegar | Modelo y proyecto a la vez sobre la misma cuenta | Corregido: el proyecto depende del modelo en `foundry.bicep` |
| `agentid foundry …` encuentra 2 identidades | Hay otro agente con el mismo nombre en otro proyecto del tenant | Corregido: filtra por `<cuenta>-<proyecto>-`; si no, `FOUNDRY_AGENT_IDENTITY_ID` |
| `invalid_scope` en el login | El tenant no conoce algún permiso de Agent ID | El CLI reintenta con los mínimos; revisa la licencia de Agent 365 |

---

## 8 · Verificado en tenants reales (27/11/2026)

Dos pruebas completas con `agentid`: un tenant sin licencias de pago (suscripción Visual Studio) y un tenant de
desarrollo con **Agent 365 + Microsoft 365 E5 (developer)** y suscripción de pago por uso. Región `swedencentral`.

### Lo que funciona

| Pieza | Resultado |
|---|---|
| Login de Graph con *Microsoft Graph Command Line Tools* y los 17 permisos | ✅ Consentimiento de una vez; el token trae todos los `scp` |
| `infra/main.bicep` (base + Foundry) | ✅ Tras corregir la carrera modelo/proyecto. En suscripciones nuevas hay que registrar `Microsoft.App` (ahora lo hace `agentid infra`) |
| `personas` · `atributos` · `datos` | ✅ Atributos solo con los roles de atributos asignados al admin (un Global Admin no los tiene) |
| `blueprint` (v1.0 `POST /applications` + principal + federated credential) | ✅ |
| `identidad` (beta `POST servicePrincipals/microsoft.graph.agentIdentity`) · owners · `Carril` | ✅ El `appId` de la identidad es su propio `id` |
| Sponsors delegados: añadir usuario y grupo, quitar | ✅ |
| RBAC a la identidad de agente con `--assignee-object-id` + `ServicePrincipal` | ✅ |
| **Demo 3**: MI → T1 (`fmi_path`) → token del agente → Storage | ✅ Sin secretos. En los sign-in logs salen **dos** inicios de sesión: el blueprint contra *AAD Token Exchange Endpoint* y la identidad de agente contra *Azure Storage* (`agent.agentType = agenticAppInstance`, `parentAppId` = blueprint) |
| Conexión de Foundry *remote tool* `authType: AgenticIdentityToken` + `audience` | ✅ Por ARM (`2025-06-01`), sin azd |
| **Demo 2**: rol en la identidad del proyecto → `403 AuthorizationPermissionMismatch`; rol en la del agente → datos | ✅ El cambio tarda **1–3 min** en notarse |
| Foundry crea **dos** identidades al crear el primer agente: `<cuenta>-<proyecto>-AgentIdentity` y `<cuenta>-<proyecto>-<agente>-AgentIdentity`, **cada una con su blueprint** | ✅ |
| **Puerta 1**: identidad automática del agente de Copilot Studio (blueprint global *Microsoft Copilot Studio agent identity blueprint*), cambio de sponsor y `Carril` | ✅ |
| **CA-AG-01 / CA-AG-02** con `agentIdServicePrincipalFilter` + `agentIdRiskLevels` · report-only aceptado | ✅ Con `includeAgentIdServicePrincipals: []` (ver abajo) |
| **Demo 4**: `confirmCompromised` → riesgo alto → `AADSTS53003` *blocked by Conditional Access* | ✅ El riesgo aparece en `riskyAgents` a los **~3 min** y el bloqueo llega a los **~6 min**. `confirmSafe` lo devuelve a la normalidad en **~4 min** |
| `LW-Mover-Sponsors` (`attributeChangeTrigger`, `locale es-es`) · ejecución bajo demanda | ✅ Correo al manager enviado. La tarea de co-sponsors falla si el agente tiene **un solo sponsor** («co-sponsor did not exist»): es lo esperado |

### Lo que cambió en el repo tras la prueba

- **Filtro de CA**: con `includeAgentIdServicePrincipals: ["All"]` el filtro por atributo **se suma** a «todos»: los
  sign-in logs mostraban CA-AG-02 (*Playground*) evaluándose sobre agentes de *Produccion*. Con la lista vacía solo
  entran los que cumplen la regla (comprobado en los dos sentidos: Producción → `reportOnlyNotApplied`,
  Playground → `reportOnlyFailure`).
- `ca-fs-triage` renueva el token cada `TOKEN_TTL_SECONDS` (120 s por defecto en `apps.bicep`): el bloqueo se ve
  **sin reiniciar el contenedor**. Y el cliente de Storage va sin reintentos (`retry_total=0`): el reintento del SDK
  repetía la petición de token y tapaba el 53003 en el log.
- Limpieza: borrar el blueprint se lleva su principal (borrar el principal directamente da 403); `cleanup` borra
  también las identidades y blueprints que Foundry creó para el proyecto, y sigue aunque un paso falle.

### Tiempos para el ensayo

| Acción | Se nota en |
|---|---|
| Rol a la identidad del agente (demo 2) | 1–3 min |
| `demo4 comprometer` → bloqueo en el log | ~6 min |
| `demo4 descartar` → el agente vuelve a funcionar | ~4 min |
| `demo4 mover` → correo a Lucía | ~1 min |

### Sigue por verificar

- Que el registro de Agent 365 muestra la identidad `fs-triage-devoluciones` sin onboarding adicional.
- La política de inactividad por defecto (se activa a mano en el portal).
- KQL de `kql/consultas.kql` contra el Log Analytics con los diagnósticos de Entra.
