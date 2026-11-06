# Propuesta Sessionize — Fabric Policies

## Título (recomendado)

**Solo lo que está en la lista: gobierna Microsoft Fabric con las nuevas Fabric Policies**

Por qué este: describe exactamente cómo funcionan las políticas (son una lista de permitidos)
y guiña a la Navidad sin caer en el chiste. En una agenda de 24 h con decenas de sesiones,
se distingue y se entiende.

Alternativas, por si el tono no encaja:

- *Fabric Policies: quién crea qué, quién cambia qué y con quién se comparte* (más sobria, descriptiva)
- *La lista de Papá Noel de tu tenant: Fabric Policies en 20 minutos* (más navideña, menos seria)

## Descripción

Hasta ahora, gobernar Microsoft Fabric era una mezcla de tenant settings de todo o nada, grupos de seguridad y buena fe. Cualquier contributor podía crear cualquier tipo de item en una capacidad de producción, y compartir datos fuera de la organización era una decisión binaria.

Las nuevas Fabric Policies cambian el modelo: reglas basadas en condiciones (grupos de Entra, workspaces, etiquetas de sensibilidad de Purview, tipo de item o dominio del destinatario) que se evalúan como una lista de permitidos. Lo que no está en la lista, no pasa.

En 20 minutos, y sobre el caso de FraSoHome, una cadena de retail de hogar, montaremos las tres políticas disponibles:

- Qué items se pueden crear en la capacidad de producción y quién puede crearlos.
- Qué ajustes de workspace pueden cambiar sus administradores.
- Con qué dominios externos se comparten datos, y nunca si llevan la etiqueta Confidencial.

Y veremos lo que conviene saber antes de activarlas: que una política es un item de Fabric que puedes versionar en Git y desplegar con CI/CD (gobierno como código), por qué una regla demasiado estrecha bloquea todo lo demás y cómo validar con los audit logs cuando no hay modo simulación.

Saldrás con un patrón de políticas listo para adaptar a tu tenant y una checklist para activarlas sin romper el trabajo de nadie.

## Metadatos para el formulario

| Campo | Valor |
|---|---|
| Nivel | Intermedio (200–300) |
| Área | Data Platform — Microsoft Fabric / Gobierno |
| Formato | Sesión con demo, 20 min |
| Idioma | Español |
| Franja preferida | Tarde del 11 de diciembre (hora peninsular) |

## Notas internas (no van en Sessionize)

- **Estado de la feature:** preview a 18 oct 2026. Revisar antes de diciembre; si llega a GA no hace falta tocar el texto, que no menciona "preview" a propósito.
- **Regiones:** la documentación dice que no está soportada en capacidades de **West Europe, North Europe y West US**. Muchos tenants españoles están en West Europe: es un buen momento de la charla, y la capacidad de la demo tiene que estar en otra región.
- **Etiqueta Confidencial en compartición externa:** comprobar al montar la demo que la condición de sensitivity label con `Is none of` aplica a la política de compartición externa tal como la contamos.
- Las políticas no consumen CU ni tienen coste adicional; activar requiere Fabric admin (tenant) o capacity admin (capacidad); propagación hasta 15 min, así que la demo en vivo debe activarse antes de empezar o grabarse.
- Una sola política activa por ámbito; los ámbitos de dominio y workspace no existen todavía.

## Fuentes

- [Microsoft Fabric policies: Centralized governance](https://learn.microsoft.com/en-us/fabric/governance/fabric-policies-overview)
- [Create and activate a Fabric policy](https://learn.microsoft.com/en-us/fabric/governance/fabric-policies-get-started)
- [Redmondmag: Microsoft Fabric updates bring more control over security, deployment and costs](https://redmondmag.com/articles/2026/10/02/microsoft-fabric-updates-bring-more-control-over-security.aspx)
- [Bitmetric: FabCon Europe 2026, the key Microsoft Fabric updates](https://www.bitmetric.nl/blog/fabcon-europe-2026-microsoft-fabric-updates/)
