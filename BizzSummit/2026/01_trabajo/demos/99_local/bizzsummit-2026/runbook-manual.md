# Runbook manual — demos Bizz Summit 2026

Pasos que el despliegue no pudo completar. Cada uno lleva el comando exacto,
ya relleno con los valores de tu configuración, para quien tenga el rol necesario.

Generado: 2026-10-02 06:24

## 1. Crear el grupo de entornos 'FraSoHome-Produccion' y meter el entorno de plataforma

**Por qué quedó pendiente:** Los environment groups se crean desde el Power Platform Admin Center; no hay cmdlet estable en el módulo de administración.

```powershell
# Power Platform Admin Center > Manage > Environment groups > New group
#   Nombre: FraSoHome-Produccion
#   Añadir: FraSoHome-Plataforma
#   Reglas de grupo: Managed Environments ON, sharing limitado, Settings Enforcer ON
# Deja el entorno Default FUERA del grupo: la demo 1 necesita que siga sin gobernar.
```

## 2. Crear el sitio de SharePoint 'FraSoHome-KB-Operaciones'

**Por qué quedó pendiente:** No se pudo crear automáticamente: Response status code does not indicate success: 401 (Unauthorized).

```powershell
# SharePoint admin center > Sitios activos > Crear > Sitio de comunicación
#   Nombre:      FraSoHome · KB Operaciones
#   Dirección:   https://vernedev.sharepoint.com/sites/FraSoHome-KB-Operaciones
#   Descripción: Conocimiento vigente del asistente de devoluciones
```

## 3. Crear el sitio de SharePoint 'FraSoHome-PrevencionPerdidas'

**Por qué quedó pendiente:** No se pudo crear automáticamente: Response status code does not indicate success: 401 (Unauthorized).

```powershell
# SharePoint admin center > Sitios activos > Crear > Sitio de comunicación
#   Nombre:      FraSoHome · Prevención de Pérdidas
#   Dirección:   https://vernedev.sharepoint.com/sites/FraSoHome-PrevencionPerdidas
#   Descripción: Documentación restringida. Fuera del alcance del asistente
```


