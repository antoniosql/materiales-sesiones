# Despliegue en un tenant — guía paso a paso

Guía para montar desde cero las demos de **«Semantic Debt: why Copilot answers questions nobody asked»**
en un tenant de demo, comprobar que cada demo responde lo que esperan las slides y dejarlo limpio después.

> **Tiempo:** unas 2 h de trabajo y **24–48 h de espera** (etiquetas, índice semántico, sincronización del agente).
> **Empieza como muy tarde el martes si presentas el viernes.**

---

## 0. Qué tendrás al final

| Pieza | Para qué demo | Lo crea |
|---|---|---|
| Laura P. (directora comercial, M365 + Copilot) y Paco R. (Finanzas) | Todas | `semdebt identities` |
| Grupo `FS-Finanzas` (único con derechos sobre la etiqueta cifrada) | 2 | `semdebt identities` |
| Etiquetas «Altamente confidencial – Finanzas» (cifrada) e «Interno – Definiciones oficiales» | 2 y 4 | `Deploy-Labels.ps1` |
| Sitio **FraSoHome-Comercial**: carpetas `Definitivos/`, `Comité/`, `Varios/`, `Antiguo/`, sin columnas | 0–3 | `semdebt sharepoint --fase antes` |
| Term store `FraSoHome` (Estado documental, Dominio) | 4 | `semdebt termstore` |
| Sitio **FraSoHome-KB-Oficial**: columnas Estado / Dominio / Propietario / Vigente desde, y FS-KB-00 con los dueños | 4 | `semdebt sharepoint --fase despues` + `Set-DominioTaxonomy.ps1` |
| Término «Cliente activo» en el glosario de Purview | 3 (borrador) y 4 (publicado) | `semdebt glossary` |
| Agente de Copilot Studio «Asistente Comercial FraSoHome» | 4 | a mano la primera vez, luego `semdebt agent create` |

Los **13 documentos** que se suben ya están en [`documentos/`](documentos/). Se generaron con la KB y los datos
reales del caso, y las cifras coinciden con las slides. Solo tienes que regenerarlos (`semdebt documents`) si cambias el caso.

### Dónde se hace cada demo (importante)

Laura tiene acceso a los dos sitios. Si haces las demos 0–3 en **Copilot Chat general**, Copilot también encuentra
la biblioteca oficial (con las cifras buenas) y el «antes» deja de fallar. Por eso:

- **Demos 0–3** → el **Copilot del sitio FraSoHome-Comercial** (el agente que trae el sitio, botón Copilot arriba a la derecha).
  Solo ve el contenido de ese sitio: es exactamente el «antes».
- **Demo 4** → el agente de Copilot Studio, cuyo conocimiento es solo FraSoHome-KB-Oficial.

---

## 1. Requisitos

### 1.1 Tenant

| Requisito | Detalle |
|---|---|
| Tenant de demo | No uses producción. Vale un tenant de desarrollo o de evaluación de Microsoft 365 E5 |
| Licencias | Microsoft 365 E5 (o E3 + complementos de Purview) para Laura y Paco, y **Microsoft 365 Copilot** para Laura |
| Copilot Studio | Un entorno de Power Platform con Dataverse y capacidad para agentes. Comprueba tu licenciamiento: cambia a menudo |
| Purview Unified Catalog | Activado, con un **dominio de gobierno publicado**. Necesitas su id |
| SharePoint | Etiquetado de ficheros de Office habilitado: `Set-SPOTenant -EnableAIPIntegration $true` |
| Opcional | API medidas de Graph habilitadas en la app, para aplicar etiquetas por código. Si no, se aplican a mano |

### 1.2 Tu cuenta de administración (`ADMIN_UPN`)

Lo más simple es Global Administrator en el tenant de demo. Con roles mínimos necesitas:
Privileged Role Administrator (consentimiento), User Administrator, Groups Administrator, SharePoint Administrator,
Compliance Administrator, administrador del dominio de gobierno en Unified Catalog y maker o administrador del entorno de Power Platform.

### 1.3 Tu equipo

| Herramienta | Instalación |
|---|---|
| Python 3.10+ | `winget install Python.Python.3.12` |
| PowerShell 7 | `winget install Microsoft.PowerShell` |
| Módulos | `Install-Module ExchangeOnlineManagement, PnP.PowerShell -Scope CurrentUser` |
| Power Platform CLI | `dotnet tool install --global Microsoft.PowerApps.CLI.Tool` (o la extensión de VS Code) |
| OpenSSL | Viene con Git for Windows (`C:\Program Files\Git\usr\bin\openssl.exe`) |

---

## 2. Registro de aplicación (una sola vez)

> **Atajo sin registro (`AUTH_MODE=delegated`)**: si no puedes o no quieres registrar una aplicación,
> pon `AUTH_MODE=delegated` en `.env` y deja `CLIENT_ID` vacío. Los comandos de Python piden un código de
> dispositivo al admin (una vez para Graph y otra para Purview) y guardan los tokens en `state/`. Lo que
> no cubre: PnP (usa `DOMINIO_COLUMN_MODE=choice`), las etiquetas (créalas en el portal de Purview con
> los nombres de `config/escenario.yaml` y la directiva `FS-Demo-Etiquetas`) y el agente (primer montaje
> en la UI de Copilot Studio). Si el tenant no tiene dominio de gobierno en Unified Catalog, créalo y
> publícalo, y pon su id en `PURVIEW_DOMAIN_ID`; regístralo en `state/deployed.json` como
> `governance_domain` para que la limpieza lo borre.

### 2.1 Certificado

```powershell
$cert = New-SelfSignedCertificate -Subject "CN=semdebt-demos" -CertStoreLocation Cert:\CurrentUser\My `
        -KeyExportPolicy Exportable -KeySpec Signature -KeyLength 2048 -NotAfter (Get-Date).AddYears(1)
$pwd = Read-Host "Contraseña del PFX" -AsSecureString
Export-PfxCertificate -Cert $cert -FilePath .\semdebt.pfx -Password $pwd
Export-Certificate    -Cert $cert -FilePath .\semdebt.cer
openssl pkcs12 -in .\semdebt.pfx -nocerts -nodes -out .\semdebt.key.pem   # clave para Python
$cert.Thumbprint                                                            # → CERT_THUMBPRINT
```

Guarda `semdebt.pfx` y `semdebt.key.pem` fuera del repo (ya están en `.gitignore`, pero mejor fuera).

### 2.2 App en Entra ID

1. **Entra admin center › Identity › Applications › App registrations › New registration**.
   Nombre `semdebt-demos`, *Single tenant*. Copia el **Application (client) ID** → `CLIENT_ID` y el **Directory (tenant) ID** → `TENANT_ID`.
2. **Certificates & secrets › Certificates › Upload** → `semdebt.cer`.
3. **Authentication › Add a platform › Mobile and desktop** → marca `https://login.microsoftonline.com/common/oauth2/nativeclient` y añade `http://localhost`.
   En **Advanced settings**, activa **Allow public client flows = Yes** (lo necesita el login de Laura).
4. **API permissions › Add a permission**:

| API | Tipo | Permisos |
|---|---|---|
| Microsoft Graph | Application | `User.ReadWrite.All`, `Group.ReadWrite.All`, `Sites.FullControl.All`, `Files.ReadWrite.All`, `TermStore.ReadWrite.All`, `Organization.Read.All`, `LicenseAssignment.ReadWrite.All` |
| SharePoint | Application | `Sites.FullControl.All` (para PnP) |
| Microsoft Graph | Delegated | `Sites.Read.All`, `Files.Read.All`, `Mail.Read`, `People.Read.All`, `OnlineMeetingTranscript.Read.All`, `Chat.Read`, `ChannelMessage.Read.All`, `ExternalItem.Read.All` |
| Power Platform API | Delegated | `CopilotStudio.Copilots.Invoke` |

5. **Grant admin consent for <tenant>**.
6. *Opcional (etiquetas sin login interactivo)*: permiso de aplicación **Office 365 Exchange Online › Exchange.ManageAsApp**,
   y asigna a la app el rol **Compliance Administrator**. Después pon `PURVIEW_PS_AUTH=app`.

> Si «Power Platform API» no aparece en *APIs my organization uses*, regístrala una vez:
> `New-MgServicePrincipal -AppId 8578e004-a5c6-46e7-913e-12f58912df43`.

### 2.3 Purview Unified Catalog

En **Purview › Unified Catalog › Catalog management › Governance domains**, abre (o crea y **publica**) el dominio
`FraSoHome Comercial`. Copia su id de la URL → `PURVIEW_DOMAIN_ID`. En **Roles**, añade la app `semdebt-demos` con un rol que pueda
crear y publicar términos (propietario del dominio o *data steward*).

### 2.4 Power Platform

```powershell
pac auth create --environment <id-del-entorno>   # PP_ENVIRONMENT_ID
pac solution list                                  # comprueba que existe la solución AGENT_SOLUTION o créala en make.powerapps.com
```

---

## 3. Configuración

```powershell
cd C:\repos\materiales-sesiones\microsoft365-live\2026\semantic-debt-demos
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[agent,dev]"
Copy-Item .env.example .env
notepad .env
```

Lo mínimo que tienes que rellenar en `.env`:

| Variable | Valor |
|---|---|
| `TENANT_ID`, `TENANT_DOMAIN`, `SP_HOST`, `ADMIN_UPN` | tu tenant de demo |
| `CLIENT_ID`, `CERT_THUMBPRINT`, `CERT_PEM_KEY_PATH`, `CERT_PFX_PATH`, `CERT_PFX_PASSWORD` | paso 2 |
| `LAURA_UPN`, `PACO_UPN` | si ya existen, se reutilizan y no se borran al limpiar |
| `LAURA_LICENSE_SKUS`, `PACO_LICENSE_SKUS` | `skuPartNumber` reales (los lista `semdebt check`) |
| `PURVIEW_DOMAIN_ID` | paso 2.3 |
| `PP_ENVIRONMENT_ID` | paso 2.4 |
| `LABEL_APPLY_METHOD` | `graph` si tienes las API medidas; si no, `manual` |

```powershell
semdebt check            # todo en ✔ antes de seguir
pytest                   # 10 tests sin tenant
```

---

## 4. Despliegue

### Día −3 (o antes): identidades y etiquetas

```powershell
semdebt figures                                   # ✔ Las cifras coinciden con las slides
semdebt identities                                # apunta las contraseñas iniciales que se muestran
pwsh scripts/powershell/Deploy-Labels.ps1         # crea etiquetas + directiva; escribe state/labels.json
```

**Comprueba:** en Purview › Information Protection › Labels aparecen las dos etiquetas y la directiva `FS-Demo-Etiquetas`.
Inicia sesión una vez como Laura en Office.com (registra MFA si te lo pide). **Las etiquetas tardan hasta 24 h.**

### Día −2: SharePoint, term store y glosario

```powershell
semdebt sharepoint --fase antes                   # FraSoHome-Comercial (tarda unos minutos en aprovisionarse)
semdebt termstore
semdebt sharepoint --fase despues                 # FraSoHome-KB-Oficial con metadatos
pwsh scripts/powershell/Set-DominioTaxonomy.ps1   # columna Dominio enlazada al term store
semdebt glossary --estado borrador
```

Si no tienes las API medidas, los comandos listan **qué fichero etiquetar a mano**:
FS-KB-03 en Comercial con «Altamente confidencial – Finanzas» y FS-KB-03 en KB-Oficial con «Interno – Definiciones oficiales».

**Comprueba:**

| Dónde | Qué deberías ver |
|---|---|
| FraSoHome-Comercial › Documentos | 4 carpetas; solo columnas Nombre / Modificado / Modificado por; `Antiguo/FS-KB-02…` es el último modificado |
| FS-KB-03 en Comercial | Candado (cifrado). Como Laura: **no se puede abrir** |
| FraSoHome-KB-Oficial › Documentos | 9 ficheros con Estado, Dominio, Propietario y Vigente desde; FS-KB-02 = Obsoleta |
| Term store › FraSoHome | Conjuntos «Estado documental» y «Dominio» |
| Unified Catalog › glosario | «Cliente activo» en **Borrador**, sin dueño de negocio |

`semdebt status` lista todo lo creado.

### Día −2: el agente (primera vez, a mano)

Sigue [copilot-studio/README.md](copilot-studio/README.md): la fuente de conocimiento es **solo** la biblioteca
de FraSoHome-KB-Oficial, con filtrado por metadatos **Estado = Vigente** e instrucciones de
[`copilot-studio/instrucciones.md`](copilot-studio/instrucciones.md). Publícalo y exporta la plantilla:

```powershell
semdebt agent extract-template --bot <id o schema name>
```

En los siguientes despliegues basta con `semdebt agent create`.

### Día −1: medir y ensayar

```powershell
semdebt evaluate --target retrieval --sitio comercial    # qué recupera Copilot en el ANTES
semdebt evaluate --target retrieval --sitio kb_oficial   # y en el DESPUÉS
semdebt evaluate --target agent                          # TRC del agente (slides: 15/20)
```

Los informes van a `output/evaluaciones/`. **Si la TRC real no es 7/20 (antes) y 15/20 (después), cambia las
slides 29 y 38 a la cifra real.** No digas en directo un número que no puedas enseñar.

---

## 5. Validación demo a demo (como Laura)

Para las demos 0–3, abre FraSoHome-Comercial como Laura y pulsa **Copilot**. La demo 4 va en el agente.

| Demo | Prompt | Debe responder | Si no |
|---|---|---|---|
| 0 | ¿Cuántos clientes activos tenía FraSoHome al cierre de 2025 y cómo evolucionaron las ventas netas en el Q4 respecto al Q3? | 49 clientes y −2,6 %, citando `Informe_Comercial_Q4_2025_FINAL.pptx` | Repite. Si da cifras de los Excel (+4,4 % / +6,9 %), también vale: es otra pregunta que nadie hizo |
| 1 | ¿Cuál es el plazo de devolución para compras online? | 30 días, citando `Antiguo/FS-KB-02…v1.2` | Puede dar 45 (la v1.3 está en Definitivos). Es aleatorio: graba la ejecución que falle |
| 2 (comparar) | Compara cómo definen y calculan las «ventas netas» los documentos de este sitio | Discrepancias entre PPT y los dos Excel; **no menciona FS-KB-03** | — |
| 2 | ¿Cuál es la definición oficial de ventas netas en FraSoHome? | La del PPT o una mezcla; **nunca cita FS-KB-03** | Si cita FS-KB-03: Laura está en FS-Finanzas o la etiqueta no se aplicó |
| 3 | ¿Qué es un cliente activo en FraSoHome? | Definición elocuente que mezcla CRM, PPT y 12 meses | — |
| 3 (tres cabezas) | Un cliente devuelve en Gran Vía un pedido online que pagó con tarjeta y con puntos. ¿Cómo hago el reembolso? | Un procedimiento inventado a partir de FS-KB-01/04/07 | — |
| 4 | Las cuatro preguntas de la slide 37 | 45 días · pregunta qué definición quieres → 100 · +2,5 % con fórmula · «no está documentado, consulta a Jorge T.» | Ver plan B del guion |

---

## 6. Día de la demo

```powershell
semdebt glossary --estado borrador     # antes de empezar (demo 3)
semdebt glossary --estado publicado    # justo antes de la demo 4 (o enséñalo ya publicado en el vídeo)
semdebt glossary --estado borrador     # al terminar, para el siguiente ensayo
```

Pre-run de los prompts 30 minutos antes y vídeos de respaldo abiertos.

---

## 7. Limpieza

```powershell
semdebt cleanup                                   # enseña la lista y pide confirmación
pwsh scripts/powershell/Remove-Labels.ps1
pwsh scripts/powershell/Remove-DeletedSites.ps1   # si vas a redeplegar con los mismos alias
```

Opciones de `semdebt cleanup`:
- `--keep-identities`: conserva a Laura, Paco y FS-Finanzas entre ensayos.
- `--purge`: los elimina también de la papelera de Entra.

Solo se borra lo que estos scripts crearon. Los documentos de `documentos/` no se tocan.
Si el despliegue pasó la única licencia de Copilot del admin a Laura (nota `restaurar_copilot_admin`
en el estado), la limpieza se la devuelve al admin al borrar a Laura.

---

## 8. Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `check` falla en Term store | Falta `TermStore.ReadWrite.All` o el consentimiento | Paso 2.2, puntos 4–5 |
| El sitio no aparece en 15 min | Aprovisionamiento lento del grupo | Repite `semdebt sharepoint --fase …`: es idempotente |
| `assignSensitivityLabel` devuelve 402 o 403 | API medidas sin habilitar | `LABEL_APPLY_METHOD=manual` y etiquétalo a mano |
| `New-Label` falla con el correo de FS-Finanzas | El grupo aún no tiene buzón | Espera 10 min tras `identities` y repite |
| El Copilot del sitio responde 45 días siempre | El índice ya prefiere la v1.3 | Es el comportamiento correcto del producto: usa el vídeo y cuenta que la respuesta varía |
| El agente cita FS-KB-02 | El filtrado por metadatos no está activo o la columna aún no se ha sincronizado | Revisa la fuente en Copilot Studio y espera a la sincronización (4–6 h) |
| `Set-DominioTaxonomy.ps1` no conecta | PnP necesita el PFX o el certificado en el almacén | Revisa `CERT_PFX_PATH` y `CERT_PFX_PASSWORD` |
| `evaluate` dice que no se hace como admin | Has iniciado sesión con `ADMIN_UPN` | Borra `state/msal_user_cache.bin` y entra como Laura |
| Glosario: 400 al publicar | El dominio de gobierno no está publicado | Publica el dominio en Unified Catalog |
