# Guía de fidelización CRM (FraSoHome Rewards)

Fuente: `FS-KB-07_Guia_Fidelizacion_CRM_v1.1.docx`.

## 1. Objetivo

Definir reglas del programa de fidelización FraSoHome Rewards para uso consistente en campañas, reporting y atención al cliente.

## 2. Tiers y reglas de puntos

- Los puntos se calculan sobre ventas netas (ver FS-KB-03).
- Las devoluciones descuentan puntos en la fecha de confirmación del reembolso.
- El canje de puntos genera 'Descuento por puntos' (ver FS-KB-03).
## 3. Segmentación operativa (marketing)

## 4. Datos mínimos en CRM

- CustomerID (clave interna)
- Correo (identificador principal)
- Fecha de alta
- Tier actual y fecha de actualización
- Puntos disponibles
- Consentimiento marketing (Sí/No)
## 5. Privacidad y límites

- El asistente NO debe mostrar datos personales completos (PII) salvo necesidad y permiso explícito del rol.
- En respuestas por defecto, usar métricas agregadas y anonimizadas.
## Tablas extraídas

### Tabla 1

| ID documento | FS-KB-07 |
| --- | --- |
| Título | Guía de fidelización (CRM): tiers, puntos y segmentación |
| Versión | 1.1 |
| Estado | VIGENTE |
| Área propietaria | Marketing + CRM |
| Aprobado por | CMO |
| Vigente desde | 01/01/2026 |
| Última revisión | 18/02/2026 |
| Sensibilidad | Uso interno (marketing) |

### Tabla 2

| Tier | Umbral anual (EUR ventas netas) | Acumulación | Beneficio clave |
| --- | --- | --- | --- |
| Bronce | 0 - 199 | 1 punto por cada 1 EUR de ventas netas | Acceso a promociones generales |
| Plata | 200 - 499 | 1,25 puntos por cada 1 EUR | Envío estándar gratuito (online) |
| Oro | 500 - 999 | 1,5 puntos por cada 1 EUR | Atención prioritaria + 1 excepción de devolución/semestre |
| Platino | >= 1.000 | 2 puntos por cada 1 EUR | Beneficios Oro + acceso anticipado a campañas |

### Tabla 3

| Segmento | Criterio | Uso recomendado |
| --- | --- | --- |
| Activo | >= 1 compra en 12 meses | Campañas de cross-sell |
| En riesgo | Última compra 6-12 meses | Campañas de reactivación suave |
| Dormido | > 12 meses | Campañas de win-back (incentivo mayor) |
| Alto retorno | Tasa de devolución (unidades) > 20% en 90 días | Revisión de fraude/experiencia |
