# ADR 0001 · Estructura del repositorio y despliegue

- **Estado:** aceptado
- **Fecha:** AAAA-MM-DD

## Contexto
El proyecto necesita que varias personas (y asistentes de IA) trabajen en paralelo sobre Fabric sin pisarse,
con despliegues reproducibles entre entornos y sin depender de que nadie toque Test o Prod a mano.

## Decisión
1. **Tres workspaces por entorno** (`datos`, `ing`, `ana`), cada uno conectado a su carpeta de `fabric/`.
   Separa permisos (quien edita un informe no puede tocar un notebook) y despliegues (un cambio de informe no redespliega la ingesta).
2. **Solo los workspaces de feature se conectan a Git.** Dev, Test y Prod los despliega `fabric-cicd` desde `main`.
3. **La lógica vive en una librería Python versionada** (`src/datafwk/`), publicada como wheel en el Environment `env_fwk`.
4. **La configuración y los contratos se publican en OneLake** (`lh_bronze/Files/_framework/`) en cada despliegue.
5. **Un repositorio por producto de datos.** La librería se separa a su propio repositorio cuando la consuma un segundo producto.

## Consecuencias
- Hay que mantener `parameter.yml` en cada carpeta de workspace
- Crear un workspace de feature por persona tiene coste de capacidad: pausar los que no se usan
- Un cambio en la librería exige nueva versión y despliegue del Environment, que tarda minutos
