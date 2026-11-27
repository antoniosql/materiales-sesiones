# Despliegue de las demos · Entra Agent ID (Azure Cloud Lab 2026)

Guía de principio a fin: requisitos, despliegue, pasos manuales, ensayo, día de la sesión y limpieza.

---

## 1 · Requisitos

### Herramientas

| Herramienta | Para qué |
|---|---|
| Python 3.10+ | CLI `agentid` |
| Azure CLI (`az`) 2.67+ con Bicep | Infraestructura, imágenes (`az acr build`), RBAC, Storage, Container Apps |
| Azure Developer CLI (`azd`) con la extensión de IA | Solo para crear la conexión MCP de Foundry. Si falla, se crea en el portal |
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
| 10 | `agentid foundry conexion` | Conexión **fs-devoluciones-mcp**: *remote tool*, auth **identidad de agente**, audience `https://storage.azure.com` | Si `azd` falla, imprime los valores para el portal |
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
| CA-AG-01 no bloquea | El token anterior sigue vivo, o el riesgo no ha propagado | `agentid demo4 reiniciar` fuerza un token nuevo. Graba el clip con margen |
| `confirmCompromised` devuelve error | API beta de riesgo de agentes | Entra → ID Protection → Risky agents → Confirm compromised |
| Sponsors: 403 al añadir | La API de sponsors para identidades de agente pide Agent ID Administrator | Comprueba el rol de Nuria o hazlo en el portal |
| `azd ai connection create` no existe | Falta la extensión de IA de azd | Crea la conexión en el portal con los valores que imprime el comando |
| `invalid_scope` en el login | El tenant no conoce algún permiso de Agent ID | El CLI reintenta con los mínimos; revisa la licencia de Agent 365 |

---

## 8 · Por verificar en el tenant

- Nombres de los permisos de Graph de Agent ID y que la API de sponsors admite llamadas delegadas.
- Que el filtro `CustomSecurityAttribute.FraSoHome_Carril -eq "Produccion"` y `agentIdRiskLevels` se aceptan en beta
  (vienen de los ejemplos de *Create conditionalAccessPolicy*).
- `riskyAgents/confirmSafe` o `dismiss` para limpiar el riesgo (el CLI prueba los dos).
- El disparador `attributeChangeTrigger` sobre `department` para workflows de mover y el `locale` `es-es`.
- Que el registro de Agent 365 muestra la identidad `fs-triage-devoluciones` sin onboarding adicional.
