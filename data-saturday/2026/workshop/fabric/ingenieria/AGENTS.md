# Reglas para notebooks y pipelines (workspace de ingeniería)

- Formato Git de Fabric: cada notebook es una carpeta `nb_<nn>_<capa>_<proposito>.Notebook/` con `notebook-content.py` y `.platform`.
- Numeración: `10` bronze, `20` silver, `30` gold, `90` operación y mantenimiento.
- Un notebook tiene como máximo: una celda de parámetros, una de arranque (`cargar_contexto`) y una o dos llamadas a la librería. Si necesitas más de ~15 líneas de lógica, esa lógica va a `src/datafwk/` con su test.
- La celda de parámetros siempre incluye `entorno = "dev"` y `workspace_datos = "proyecto-datos-dev"` literalmente: `parameter.yml` los sustituye en cada entorno.
- Prohibido `%pip install` y `!pip`: las dependencias van en el Environment `env_fwk`.
- Prohibido `display()` de tablas completas y `collect()` sin límite.
- Los pipelines (`pl_<proposito>.DataPipeline/`) se diseñan en Fabric y se sincronizan desde el workspace: no generes su JSON a mano.
