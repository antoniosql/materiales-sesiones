# Evolución de cargas

Procedimientos para poner en marcha un proyecto y cambiar cómo se extrae, valida e historifica una fuente.
La librería es genérica: cada cambio se hace en contratos y configuración. El porqué está en
`docs/adr/0002-evolucion-cargas-calidad-historia.md`.

Publicar la configuración y ejecutar notebooks son pasos separados: cambiar un YAML en Git no cambia por sí solo
el comportamiento de un workspace.

## Proyecto nuevo

1. Desde la plantilla, ejecutar `python scripts/crear_proyecto.py <carpeta_nueva> --proyecto <nombre-proyecto>`.
   El destino debe ser nuevo y estar fuera de la plantilla. Se copian código, instrucciones, tests e infraestructura;
   se excluyen Git, entornos virtuales, herramientas y ficheros `.env`. Cada item recibe un nuevo `logicalId`.
2. En la carpeta generada: `git init -b main`, instalar `pip install -e '.[dev]'`, ejecutar los checks y hacer
   el commit de partida. Crear una rama de trabajo. El generador no conecta ni despliega recursos.
3. Crear primero los contratos en `contracts/` y después las fuentes y modelos en `config/`, partiendo de `templates/`.
4. Si hay fuentes SQL, añadir en cada `config/entornos/<entorno>.yml` la conexión `conexiones_sql.<conexion>` con
   `servidor` y `base`. Estos dos campos contienen nombres, nunca contraseñas. La identidad del notebook necesita
   lectura en SQL y escritura en los lakehouses, con Microsoft Entra configurado.
5. Ejecutar `python scripts/validar_contratos.py`, `python scripts/generar_catalogo.py`,
   `pre-commit run --all-files` y `pytest --delta`. En Windows, Java 17 y las bibliotecas nativas de Hadoop deben
   estar disponibles en el proceso. El devcontainer y CI usan Linux.
6. Crear o desplegar workspaces y lakehouses; publicar después `config/` y `contracts/` con `scripts/publicar_config.py`.
   Crear el Environment en Fabric, construir el wheel, subirlo con `scripts/publicar_libreria.py` y esperar su publicación.
   Asociar los notebooks al Environment. Reiniciar la sesión Spark después de actualizar la biblioteca.
7. Crear el pipeline en Fabric y sincronizarlo por Git. No se genera JSON de pipeline a mano.
   Secuencia por fuente: bronze → silver → gold (cuando tenga modelo). Pasar la salida `batch_id` de bronze a silver y gold.
   **Concurrencia máxima 1 por fuente y por modelo**, también para operaciones y reintentos manuales.

## Primera carga

1. Ejecutar `nb_10_bronze_ingesta` con `dominio`, `fuente` y un `batch_id` nuevo.
2. Ejecutar `nb_20_silver_estandarizar` con ese mismo lote. Revisar `fwk_lotes`, `fwk_marcas` y `fwk_ejecuciones`.
3. Si la fuente tiene modelo, ejecutar `nb_30_gold_dimension` con `modelo`.

Repetir bronze y silver con el mismo identificador es seguro: bronze reutiliza los datos persistidos, silver responde
`reutilizado`, el origen no se vuelve a extraer y la marca no retrocede.

Una carga completa con `columna_marca` fija un límite superior con el reloj del origen y excluye el margen de
estabilización. La marca se confirma al finalizar silver, también cuando la ventana está vacía.

## Cambiar las condiciones de calidad

Prompt: `cambiar-cuarentena`.

1. Incrementar `version` en el contrato y revisar qué filas ya aceptadas pueden pasar a rechazarse.
2. Validar y publicar el contrato.
3. Ejecutar `nb_90_ops_revalidar` con un identificador de lote nuevo. Lee la última observación de cada clave desde
   bronze, incluidas las aceptadas por la versión anterior, y reconstruye silver. No avanza la marca del origen.
4. Revisar `fwk_cuarentena`: dato bruto JSON, todos los motivos y versión del contrato. Cada versión conserva sus
   evidencias y repetir el mismo lote no las duplica. El total histórico de esa tabla no equivale a rechazos pendientes:
   `resuelta_en` queda reservado y el framework no implementa resolución automática.

Con `politica_rechazo: fallar`, la revalidación se detiene **antes** de cambiar silver o cuarentena. Para continuar,
corregir el contrato en una versión posterior y reintentar el lote fallido; no iniciar otro mientras siga pendiente.

La revalidación reconstruye el estado actual, así que su coste crece con la tabla. En una carga normal con `merge`,
un cambio inválido se aparta y se conserva la última fila válida en silver; la revalidación estricta puede retirarla.

## Pasar de extracción completa a incremental

Prompt: `pasar-a-incremental`.

1. Confirmar que el origen mantiene una marca UTC no nula en INSERT y UPDATE, que la carga completa terminó con marca
   y que no hay lotes pendientes. No inicializar una marca a mano ni usar una fecha de creación para detectar cambios.
2. Cambiar solo `extraccion.modo` a `incremental`, validar y publicar. `modo_carga: merge` no cambia: extraer de forma
   incremental y escribir con merge son decisiones diferentes.
3. Ejecutar bronze, silver y gold con un lote nuevo. La consulta usa un límite inferior con solape y un límite superior
   fijo. Repetir el mismo lote y después ejecutar uno sin cambios: las claves no se duplican.

Límites: no detecta borrados físicos ni cambios intermedios entre lecturas, y no garantiza commits tardíos fuera del
solape. Si se necesitan, diseñar CDC o Change Tracking con su retención; no ampliar las promesas de la marca temporal.

## Activar SCD2 sobre una dimensión tipo1

Prompt: `activar-scd2`.

1. Los cambios anteriores a la activación ya sobrescribieron el valor tipo1: no hay historia recuperable.
2. Crear **primero** el contrato histórico y el de proyección actual, y después actualizar el modelo. Anunciar el cambio
   de grano: la clave pasa a `id_version` y la clave de negocio se declara aparte. La tabla `<dimension>_actual`
   conserva una fila por entidad para las relaciones de consumo.
3. Validar y publicar. Congelar las modificaciones de origen durante la activación y completar un nuevo lote bronze y
   silver. No ejecutar todavía el notebook gold ordinario para ese lote.
4. Ejecutar `nb_90_ops_activar_scd2` con ese lote. Conserva el estado gold tipo1, lo inicia en el instante de activación
   y registra la versión Delta anterior. Repetir la activación con **el mismo lote** es inocuo.
5. Los lotes siguientes usan el pipeline normal: una única operación MERGE cierra la versión anterior y abre la nueva.
   Verificar un único `es_actual = true` por entidad y que los intervalos `[vigente_desde, vigente_hasta)` no se solapan.

Un cambio solo en un atributo de `columnas_tipo1` actualiza la versión vigente sin abrir otra. Cambiar después la lista de
atributos de una dimensión ya historificada requiere una migración acordada; no consiste en repetir la activación.
No se implementa vigencia de negocio retroactiva.

## Consumo de dimensiones SCD2

Las relaciones de consumo usan la tabla `<dimension>_actual`. Conectar el histórico por la clave de negocio multiplicaría
las filas. La unión temporal de hechos a versiones necesita la fecha del hecho y una definición de negocio aprobada.

## Operación

- `a_silver` exige lote explícito; para reprocesar con reglas nuevas se usa `nb_90_ops_revalidar`.
- `filas_escritas` de `fwk_ejecuciones` cuenta claves aceptadas, incluidas las que no cambian.
  La identidad de auditoría `fuente` tiene la forma `dominio.fuente`.
- `fwk_modelos` guarda el último estado por modelo; el historial se consulta en auditoría y Delta.
  No hay transacción distribuida entre tablas: el pipeline debe esperar a que gold confirme antes de habilitar consumo.
- Para recuperar una activación: detener escritores, conservar registro y versión previa, y reintentar el mismo lote.
  Volver a tipo1 exige restaurar explícitamente la versión previa junto a su contrato y configuración, y resolver el
  registro de control; no basta con cambiar el YAML. Preparar ese rollback en una copia antes de tocar un entorno real.
- No ejecutar VACUUM sobre versiones necesarias para reintentos o para una migración pendiente.
- Las reglas y las rutas de contratos son configuración versionada de confianza, revisada en Git; no aceptar YAML
  arbitrario de usuarios finales. El SQL de extracción solo interpola identificadores validados y límites datetime tipados.

Referencias: [conector SQL nativo de Fabric](https://learn.microsoft.com/en-us/fabric/data-engineering/spark-sql-connector),
[MERGE Delta](https://docs.delta.io/delta-update/) y
[subida de bibliotecas al Environment](https://learn.microsoft.com/en-us/rest/api/fabric/environment/staging/upload-custom-library).
