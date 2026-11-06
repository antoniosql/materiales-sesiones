# Propuestas Sessionize — Azure Cloud Lab 2026

El evento es de **infraestructura Azure**: el público son sysadmins, arquitectos cloud, DevOps/SRE y
seguridad. Las propuestas no van de "cómo se usa Fabric o Foundry", sino de lo que a ese público le
toca cuando le llega Fabric o un agente a producción: red, identidad, IaC, observabilidad y coste.
Ese ángulo es el hueco: en una agenda de AKS, redes y Bicep habrá poca gente hablando de datos e IA
con mirada de plataforma.

**Recomendación (actualizada):** enviar la **5**, la **2** y la **3**. La 5 sustituye a la 1: aprovecha
el trabajo de Agent 365 del Bizz Summit y no depende del AI gateway. La 1 queda como alternativa y la 4
como reserva (o si quieres cubrir el track FinOps, que suele ir corto de propuestas).

| # | Título corto | Nivel | Tracks del CFS | FraSoHome |
|---|---|---|---|---|
| 1 | Foundry Agent Service en producción *(alternativa)* | 300 | IA · Seguridad e identidad · Integración (APIM) · Observabilidad | Agentes de `frasohome-agents-foundry` |
| 2 | Fabric para equipos de infraestructura | 300 | Networking · Seguridad · Data Platform | Workspace de producción blindado |
| 3 | Fabric como código | 300 | DevOps / IaC · Data Platform | Despliegue dev → prod del caso |
| 4 | FinOps para Fabric | 200 | FinOps · Data Platform | Cargas del caso en una F-SKU |
| **5** | **Entra Agent ID** | 300 | Seguridad e identidad · IA · Casos reales | Los agentes del Bizz Summit + uno de Foundry |

---

## 5 · Entra Agent ID (recomendada en lugar de la 1)

Es la otra cara de la sesión del Bizz Summit. Allí el público era de Power Platform y M365, y la
pregunta era *quién gobierna los agentes*. Aquí el público es de identidad e infraestructura, y la
pregunta es *qué es un agente para Entra y para Azure*. Mismo escenario (Marta, David, el Asistente
de Devoluciones, `fs-triage-devoluciones`), mismo control plane, distinta capa.

### Título

**Tu próximo service principal piensa por sí mismo: identidad, acceso y ciclo de vida de agentes con Microsoft Entra Agent ID**

Alternativas:

- *Agentes con DNI: Microsoft Entra Agent ID y Agent 365 para equipos de identidad*
- *Un agente sin propietario es una incidencia esperando fecha: gobierno de identidades de agentes en Entra*

### Descripción

Durante años, dar acceso a una automatización en Azure era crear un service principal, darle un rol y olvidarse. Con los agentes de IA ese modelo no aguanta: deciden qué herramientas usan, actúan en nombre de usuarios, se crean por cientos desde Copilot Studio o Foundry y sobreviven a la persona que los construyó.

Microsoft Entra Agent ID convierte al agente en una identidad de primera clase, con su propio modelo: blueprints que actúan como plantilla de una familia de agentes, identidades de agente en runtime, cuentas de usuario de agente y la figura del sponsor, la persona que responde por él.

En esta sesión lo aterrizamos en FraSoHome, una cadena de retail de hogar con tres agentes que llegan al directorio por tres puertas distintas:

- Un agente de Copilot Studio que ya tiene Agent ID, pero cuya creadora cambió de equipo hace meses.
- Un agente de Foundry que funciona en desarrollo y pierde los permisos al publicarse, porque la identidad compartida del proyecto y la identidad propia no son la misma.
- Un agente propio en un contenedor de Azure, sin secretos, con federated credentials sobre un blueprint aprobado por IT.

Y sobre ellos, los controles que ya conoces aplicados a un sujeto nuevo: RBAC mínimo sobre recursos de Azure, acceso condicional dirigido a blueprints y atributos de seguridad, bloqueo de agentes de alto riesgo, lifecycle workflows cuando el sponsor se va, revisiones de acceso y logs de inicio de sesión. Con Agent 365 como registro donde verlos todos juntos.

Saldrás con un modelo de blueprints y sponsors para tu tenant y una checklist de lo que revisar antes de que el primer agente reciba un rol en producción.

### Metadatos

| Campo | Valor |
|---|---|
| Nivel | 300 |
| Tracks | Seguridad, identidad, cumplimiento y gobierno · Data Platform, Analytics, IA y ML · Casos reales |
| Formato | Sesión con demo, 50 min |

### Arco de demos propuesto (4 demos, mismo escenario del Bizz Summit)

| Demo | Agente | Qué se ve | Control |
|---|---|---|---|
| 1 · ¿Quién es? | `FS-Copilot-Devoluciones` (Copilot Studio) | Su Agent ID en Entra: blueprint, identidad, sponsor vacío; sign-in logs | Inventario e identidad |
| 2 · El rol que no viaja | Agente de Foundry de `frasohome-agents-foundry` | Funciona con la identidad compartida del proyecto; se publica y la tool MCP contra Storage falla. Se asigna RBAC al `agentIdentityId` con el *audience* correcto | RBAC mínimo |
| 3 · Sin secretos | `fs-triage-devoluciones` en Container Apps | Blueprint aprobado por IT + federated credential con la managed identity; aparece en Agent 365 junto al de Copilot Studio | Onboarding de agentes externos |
| 4 · Cuando Marta se va | Los tres | CA sobre el blueprint vía custom security attribute; lifecycle workflow que avisa y reasigna sponsor al cambiar de equipo | Acceso condicional y ciclo de vida |

### Notas internas

- **Diferencia con el Bizz Summit:** allí *All agents* en el M365 Admin Center y el PPAC; aquí el portal de Entra, Graph / az CLI y recursos de Azure. Reaprovechar personas, agentes y la frase ancla; no repetir demos.
- **Estado (Learn, 18 oct 2026):** Entra Agent ID es GA. El asistente para crear blueprints e identidades de agente sale como preview. Hay plantillas nuevas de CA (bloquear identidades de agente de alto riesgo, acceso autónomo, acceso on-behalf-of), lifecycle workflows de sponsor y access packages para agentes. El registro de agentes está convergiendo hacia Agent 365; Entra sigue siendo la base de identidad.
- **Copilot Studio:** crea Agent ID automáticamente para agentes nuevos desde julio de 2026 (lo contaste en el Bizz Summit). Para los antiguos existe una guía de migración a Agent ID: buen momento para la demo 1.
- **Foundry:** identidad compartida del proyecto para agentes sin publicar e identidad propia al publicar; los roles **no se heredan** y hay que reasignarlos. Solo MCP y A2A soportan auth `AgenticIdentityToken`. El *audience* debe ser el del recurso (`https://storage.azure.com`), no la URL del MCP. Es el fallo de demo más didáctico.
- **Limitaciones de CA que dan juego en la charla:** con OBO el sujeto es el usuario, no el agente; las políticas de "All users" no incluyen cuentas de usuario de agente; las políticas de blueprint no cubren esas cuentas; los agentes con API keys se saltan CA (otra razón para federated credentials).
- **Licencias:** CA para agentes requiere Entra ID P1/P2 y licencia de Agent 365 por usuario (la exigencia de esta última se anunciaba como "coming soon"). Repetir el aviso del Bizz Summit: E3 + Copilot no es elegible para Agent 365.
- **Agente externo:** en el Bizz Summit `fs-triage-devoluciones` se onboardaba con el Agent 365 SDK desde Claude Code. Aquí el foco es el blueprint y la federated credential, no el SDK. Learn tiene guías de federación para AWS, GCP y n8n si quieres un guiño multicloud.
- Sin AI gateway ni APIM, a propósito.

---

## 1 · Foundry Agent Service en producción

### Título

**Del notebook a la landing zone: agentes de Microsoft Foundry en producción con red privada, Agent ID y AI gateway**

Alternativa: *Tu agente funciona en la demo. ¿Y en tu red? Foundry Agent Service con mirada de plataforma*

### Descripción

Construir un agente en Microsoft Foundry lleva una tarde. Pasarlo a producción en una empresa lleva semanas, y casi todo ese tiempo no tiene nada que ver con prompts: tiene que ver con red, identidad, coste y trazabilidad. Es el trabajo que acaba en manos de los equipos de infraestructura.

En esta sesión cogemos los agentes de FraSoHome, una cadena de retail de hogar con datos de ventas, devoluciones y políticas internas, y los llevamos del playground a una landing zone:

- Standard setup con VNet propia: sin salida pública, con subnet injection y endpoints privados hacia AI Search, Storage, Cosmos DB y los servidores MCP.
- Identidad: el agente como identidad propia con Entra Agent ID, managed identities y RBAC mínimo sobre cada herramienta.
- API Management como AI gateway: límites de tokens por agente, métricas de consumo y reparto de carga entre despliegues de modelos.
- Observabilidad: trazas en Application Insights, evaluaciones continuas sobre tráfico real y alertas en Azure Monitor.

Todo en demo y desplegado con IaC. Saldrás con una arquitectura de referencia y una checklist de lo que hay que resolver antes de que un agente toque datos de negocio.

### Metadatos

| Campo | Valor |
|---|---|
| Nivel | 300 |
| Tracks | Data Platform, Analytics, IA y ML · Seguridad, identidad y gobierno · Integración (API Management) · Observabilidad |
| Formato | Sesión con demo, 50 min |

### Notas internas

- Foundry Agent Service es GA desde el 16 mar 2026 (BYO VNet, Entra Agent Identity para MCP, evaluaciones continuas y trazas en App Insights). Hosted agents seguía en preview.
- Comprobar el estado de las conexiones de Foundry a un AI gateway propio (APIM) antes de prometerlo en demo; si sigue en preview, se cuenta igual, el texto no dice "GA".
- Reaprovecha `frasohome-agents-foundry/` y el trabajo del Bizz Summit (gobierno de agentes), pero esta es la cara de plataforma, no la de Copilot Studio / Agent 365.
- Riesgo de demo: el standard setup con VNet tarda en desplegar. Llevar el entorno desplegado y enseñar el Bicep/Terraform, no lanzarlo en vivo.

---

## 2 · Microsoft Fabric para equipos de infraestructura

### Título

**Te han dado Microsoft Fabric y eres el de redes: private links, outbound protection y aislamiento de workspaces**

Alternativa: *Microsoft Fabric visto desde la infraestructura: red, identidad y aislamiento de datos*

### Descripción

Microsoft Fabric llega a las empresas por el lado de datos, pero la primera reunión seria es con infraestructura y seguridad: ¿por dónde sale el tráfico?, ¿cómo llega a un storage con firewall?, ¿puedo impedir que un notebook copie datos a cualquier sitio? Fabric es SaaS y no tiene VNet, así que las respuestas no son las de siempre.

En esta sesión montamos el workspace de producción de FraSoHome, una cadena de retail de hogar, con los controles de red que hoy ofrece la plataforma:

- Entrada: private link a nivel de tenant frente a nivel de workspace, y qué rompe cada uno.
- Salida: workspace outbound access protection, con managed private endpoints para Spark y OneLake y reglas de conexión para pipelines, dataflows y modelos semánticos.
- Acceso a recursos de Azure detrás de firewall: trusted workspace access, workspace identity y el VNet data gateway.
- Gobierno: cómo auditar qué workspaces están protegidos y qué políticas tienen, desde las APIs de administración.

Con una demo de un intento de exfiltración bloqueado y otro permitido, y las limitaciones que conviene conocer antes de activar nada en un tenant con historia.

### Metadatos

| Campo | Valor |
|---|---|
| Nivel | 300 |
| Tracks | Networking y conectividad · Seguridad, identidad y gobierno · Data Platform |
| Formato | Sesión con demo, 50 min |

### Notas internas

- Limitaciones que dan juego en la charla (Learn, oct 2026): solo F-SKU (no trial), no se puede activar si el workspace tiene items no soportados (p. ej. informes de Power BI: solo modelos semánticos), incompatible con external data sharing, y con private link activo las reglas de conexión solo se configuran por REST API.
- Auditoría: admin API *Workspaces – List Networking Communication Policies*.
- Encaja con el proyecto greenfield en Fabric: si puedes contar lecciones reales (sin nombrar cliente), súmalas a la descripción; el CFS lo valora mucho.
- Mucho solape conceptual con la sesión de Fabric Policies del Christmas Power Data Platform: aquí red, allí gobierno de items. Se complementan.

---

## 3 · Fabric como código

### Título

**Microsoft Fabric como código: Terraform, fabric-cicd y GitHub Actions de dev a producción**

Alternativa: *Nadie hace clic en producción: despliegue de Microsoft Fabric con Terraform y fabric-cicd*

### Descripción

En Azure hace años que nadie serio crea recursos de producción a mano. En Microsoft Fabric sigue siendo habitual: capacidades, workspaces, permisos, conexiones y lakehouses creados desde el portal, y despliegues que consisten en copiar y pegar.

Ya no hay excusa. En esta sesión desplegamos la plataforma de datos de FraSoHome, una cadena de retail de hogar con arquitectura medallón, sin tocar el portal:

- Terraform para la plataforma: capacidades, workspaces, asignación de roles, conexiones, managed private endpoints y workspace identities.
- fabric-cicd para el contenido: notebooks, lakehouses, pipelines y modelos semánticos desde Git, con parametrización por entorno.
- GitHub Actions con identidad federada: plan, aprobación y despliegue de dev a producción.
- Qué va en cada capa, qué sigue sin poder automatizarse y cómo detectar la deriva cuando alguien hace clic igualmente.

Saldrás con un repositorio de referencia listo para clonar y una regla clara de qué gestiona Terraform y qué gestiona el pipeline de contenido.

### Metadatos

| Campo | Valor |
|---|---|
| Nivel | 300 |
| Tracks | DevOps, IaC y automatización · Data Platform |
| Formato | Sesión con demo, 50 min |

### Notas internas

- El provider de Terraform para Fabric es GA. Revisar qué recursos cubre a fecha de la charla (en especial private endpoints, workspace identity y conexiones) y ajustar la lista de la descripción.
- Las Fabric Policies son items versionables en Git: guiño a la sesión del Christmas Power Data Platform.
- El repositorio de referencia puede salir del scaffold OpenSpec-analytics; código en `c:\dev\azure-cloud-lab\2026`, no en este repo.

---

## 4 · FinOps para Microsoft Fabric (reserva)

### Título

**Una capacidad de Fabric no es una VM: FinOps para Microsoft Fabric**

Alternativa: *¿Por qué se ha frenado Fabric otra vez? Capacidad, throttling y coste explicados para quien paga la factura*

### Descripción

Fabric se paga por capacidad, no por consumo, y eso desconcierta a quien viene de gestionar costes en Azure: la factura es plana, pero el rendimiento no. Un notebook mal escrito el martes puede frenar los informes del miércoles por la mañana, y el instinto de subir de SKU suele ser la respuesta cara.

En esta sesión, con las cargas de FraSoHome, una cadena de retail de hogar, explicamos cómo se comporta de verdad una capacidad y cómo gobernarla:

- Capacity Units, smoothing, bursting y las fases de throttling, vistas en la Capacity Metrics app.
- Surge protection y límites para que un trabajo de fondo no tumbe al resto.
- Pausa y reanudación automatizadas, reservas y cuándo compensa separar cargas en varias capacidades.
- Showback y chargeback por workspace, etiquetas y presupuestos en Azure Cost Management.

Saldrás con un modelo de operación mensual y los criterios para decidir entre optimizar, escalar o aislar antes de pedir más presupuesto.

### Metadatos

| Campo | Valor |
|---|---|
| Nivel | 200 |
| Tracks | FinOps y optimización de costes · Observabilidad · Data Platform |
| Formato | Sesión con demo, 50 min |

### Notas internas

- Surge protection para operaciones de fondo es GA; revisar si ya existe también a nivel de workspace antes de concretar el texto.
- Para la demo de throttling hace falta una F-SKU pequeña y una carga provocada; grabarla por si acaso.

---

## Fuentes

- [Convocatoria Azure Cloud Lab 2026 en Sessionize](https://sessionize.com/azurecloudlab2026)
- [Foundry Agent Service GA (Microsoft Foundry Blog, 16 mar 2026)](https://devblogs.microsoft.com/foundry/foundry-agent-service-ga/)
- [Microsoft Foundry – BYO AI Gateway – Part 2](https://journeyofthegeek.com/2026/03/09/microsoft-foundry-apim-and-model-gateway-connections-part-2/)
- [Workspace outbound access protection overview (Microsoft Learn)](https://learn.microsoft.com/en-ca/Fabric/security/workspace-outbound-access-protection-overview)
- [Terraform Provider for Microsoft Fabric now generally available](https://blog.fabric.microsoft.com/en-us/blog/terraform-provider-for-microsoft-fabric-now-generally-available)
- [What's new in Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/whats-new-agent-id)
- [Conditional Access for agents (Microsoft Learn)](https://learn.microsoft.com/sr-latn-rs/entra/identity/conditional-access/agent-id)
- [Agent identities in Microsoft Foundry (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-identity)
- [Surge protection for background operations is GA](https://blog.fabric.microsoft.com/en/blog/announcing-surge-protection-for-background-operation-is-generally-available-ga)
