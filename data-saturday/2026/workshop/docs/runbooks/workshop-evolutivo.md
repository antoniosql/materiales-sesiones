# Ejecución del workshop evolutivo

Este recorrido implementa las demos del plan de cuatro horas. La biblioteca permanece genérica;
`templates/workshop/` contiene los cambios de configuración y contrato que se aplican durante la sesión.
Los ejemplos leen directamente SQL. No hay paso de exportación a CSV ni alteración artificial de datos en Spark.

## Preparación y proyecto greenfield

1. Desde la plantilla, ejecutar `python scripts/crear_proyecto.py <carpeta_nueva> --proyecto <nombre-proyecto>`.
   El destino debe ser nuevo y estar fuera de la plantilla. Se copian código, instrucciones, tests e infraestructura;
   se excluyen Git, entornos virtuales, herramientas y ficheros `.env`. Cada item recibe un nuevo `logicalId`.
2. En la carpeta generada: `git init -b main`, instalar `pip install -e '.[dev]'`, ejecutar los checks y hacer
   el commit de partida. Crear una rama de trabajo. El generador no conecta ni despliega recursos.
3. Copiar primero los contratos de `templates/workshop/01_base/contracts/` a `contracts/`, conservando carpetas.
   Después copiar `01_base/config/` a `config/`. Los ejemplos originales de ventas pueden conservarse como referencia;
   las demos usan exclusivamente `crm` y `devoluciones`.
4. Añadir en cada `config/entornos/<entorno>.yml` la conexión `conexiones_sql.oltp_workshop` con `servidor` y `base`.
   Estos dos campos contienen nombres, nunca contraseñas. La identidad del notebook necesita lectura en SQL y escritura
   en los lakehouses. Utilizar una base dedicada al workshop, con Microsoft Entra configurado.
5. Ejecutar `python scripts/validar_contratos.py`, `python scripts/generar_catalogo.py`,
   `pre-commit run --all-files` y `pytest --delta`. En Windows, Java 17 y las bibliotecas nativas de Hadoop deben
   estar disponibles en el proceso. El devcontainer y CI usan Linux.
6. Crear/desplegar workspaces y lakehouses; publicar después `config/` y `contracts/` con `scripts/publicar_config.py`.
   Crear el Environment en Fabric, construir el wheel, subirlo con `scripts/publicar_libreria.py` y esperar su publicación.
   Asociar los notebooks al Environment. Reiniciar la sesión Spark después de actualizar la biblioteca.
7. Crear el pipeline en Fabric y sincronizarlo por Git. No se genera JSON de pipeline a mano.
   Secuencia por fuente: bronze → silver → gold (cuando tenga modelo). Pasar la salida `batch_id` de bronze a silver/gold.
   **Concurrencia máxima 1 por fuente y por modelo**, también para operaciones y reintentos manuales.

Los checkpoints no contienen la conexión de un entorno real. Publicar configuración y ejecutar notebooks son pasos
separados: copiar un YAML en Git no cambia por sí solo el comportamiento de un workspace.

## 00:00–00:30 · Contexto y fundamentos

Explicar la separación extracción/escritura/historia, medallón, contratos, clave de negocio, clave de versión,
observación, watermark y cuarentena. Abrir `docs/adr/0002-evolucion-cargas-calidad-historia.md`.
Mostrar que notebooks orquestan, `src/datafwk/` transforma y el catálogo se genera desde contratos.

## 00:30–01:05 · Demo 1: desde cero

Ejecutar los pasos greenfield 1–5 en una carpeta nueva. Mostrar el diff de los nuevos contratos, fuentes y modelo tipo1.
Comparar los GUID de dos `.platform` entre plantilla y proyecto generado. Pasar checks. Los recursos cloud y el
Environment deben estar preparados para evitar dedicar la sesión a esperar su aprovisionamiento.

Resultado: proyecto independiente reproducible, sin datos ni credenciales dentro de Git.

## 01:05–01:30 · Demo 2: extracción SQL completa

1. Mostrar `crm.customer` y `returns.return_line` en la base de origen. La proyección mantiene la semántica de las
   columnas del esquema original: `customer_id→id_cliente`, `city→ciudad`, `updated_at→fecha_cambio`.
2. Ejecutar `nb_10_bronze_ingesta` con `dominio=crm`, `fuente=clientes_crm` y un `batch_id` nuevo.
3. Ejecutar `nb_20_silver_estandarizar` con ese mismo lote. Mostrar `fwk_lotes`, `fwk_marcas` y `fwk_ejecuciones`.
4. Ejecutar `nb_30_gold_dimension` con `modelo=dim_cliente`. Es una dimensión tipo1, una fila por cliente.
5. Repetir bronze y silver con el mismo identificador. Bronze reutiliza los datos persistidos; silver responde
   `reutilizado`. El origen SQL no se vuelve a extraer y la marca no retrocede.

La carga completa del CRM ya lleva `columna_marca: updated_at`. Fija un límite superior usando el reloj de SQL y
excluye los últimos cinco segundos. La marca se confirma al finalizar silver, también cuando la ventana está vacía.

## 01:30–01:55 · Demo 3: cambiar condiciones de cuarentena

1. Sembrar los defectos **en la base SQL dedicada**, antes de bronze. Para la muestra docente de diez líneas:
   una con reembolso negativo, otra con reembolso NULL, dos con motivo NULL e importe válido y seis válidas.
   Son defectos compatibles con la nulabilidad del esquema. No duplicar PK ni saltarse CHECK/FK del origen.
   Si se utiliza toda la base, conservar los mismos cuatro casos y adaptar los conteos al total real.
   Guardar los valores originales para restaurarlos después; ver `templates/workshop/errores-origen.md`.
2. Ejecutar bronze/silver para `dominio=devoluciones`, `fuente=lineas_devolucion` con Q1 (`01_base`).
   Con exactamente la muestra descrita: 10 leídas, 8 aceptadas y 2 rechazadas.
3. Copiar el contrato Q2 de `02_calidad`, revisar el diff de `version: 2` y `motivo.nulo: false`, validar y publicar.
   Ejecutar `nb_90_ops_revalidar` con un identificador nuevo. Lee la última observación de cada clave desde bronze,
   incluidas las aceptadas por Q1: 6 aceptadas y 4 rechazadas. Reconstruye silver; no avanza la marca del origen.
4. Mostrar `fwk_cuarentena`: dato bruto JSON, todos los motivos y versión del contrato. Q1 y Q2 conservan evidencias
   distintas; repetir el mismo lote no duplica evidencias. No interpretar el total histórico de esa tabla como rechazos
   pendientes: `resuelta_en` queda reservado y esta versión no implementa resolución automática.
5. Publicar Q3 de `03_fallar` y lanzar otra revalidación. Debe fallar **antes** de cambiar silver o cuarentena.
   Mostrar auditoría y versiones Delta sin cambio. Para continuar, corregir explícitamente el contrato a una versión
   posterior y reintentar el lote fallido; no iniciar otro mientras siga pendiente.

La revalidación reconstruye el estado actual para cargas pequeñas de demo. En una carga normal con `merge`, un cambio
inválido se aparta y se conserva la última fila válida en silver. La revalidación estricta puede retirarla.

## 01:55–02:10 · Descanso

## 02:10–02:40 · Demo 4: completa → incremental

1. Abrir el YAML del CRM y confirmar que su completa terminó con marca. No inicializar una marca a mano.
2. Copiar `04_incremental/config/fuentes/crm.yml`, revisar el único cambio de modo, validar y publicar.
   `modo_carga: merge` sigue igual: extraer incremental y escribir con merge son decisiones diferentes.
3. En SQL, cambiar una ciudad y asignar **también** `updated_at = sysutcdatetime()`. El DEFAULT del DDL solo cubre
   inserciones. Esperar al margen de estabilización de cinco segundos antes de ejecutar el lote nuevo.
4. Ejecutar bronze/silver/gold. Mostrar la consulta generada: límite inferior con solape y límite superior fijo.
   Repetir el mismo lote y después ejecutar uno sin cambios. Las claves no se duplican.
5. Comentar los límites: sin borrados físicos, sin cambios intermedios entre lecturas y sin garantía para commits
   tardíos fuera del solape. Si se necesitan, diseñar CDC/Change Tracking con su retención; no ampliar promesas del timestamp.

`returns.return_line` permanece en completa: carece de `updated_at`; `created_at` no detecta modificaciones.

## 02:40–03:20 · Demo 5: activar SCD2 en ciudad

1. Mostrar que los cambios de ciudad anteriores sobrescribieron el valor tipo1. No existe historia recuperable anterior.
2. Copiar **primero** ambos contratos de `05_scd2/contracts/gold/` y después el modelo `05_scd2/config/modelos/`.
   Anunciar el cambio de grano de `dim_cliente`: clave `id_version`, clave de negocio `id_cliente`, atributos SCD2 `[ciudad]`.
   `dim_cliente_actual` conserva una fila por cliente para relaciones de consumo.
3. Validar y publicar. Congelar modificaciones de origen durante la activación; completar un nuevo lote bronze/silver.
   No ejecutar todavía el notebook gold ordinario para ese lote.
4. Ejecutar `nb_90_ops_activar_scd2` con ese lote. Conserva el estado gold tipo1, lo inicia en el instante de activación
   y registra la versión Delta anterior. Repetir la activación con **el mismo lote** es inocuo.
5. Cambiar la ciudad A→B en SQL con `updated_at`, esperar el margen, ejecutar un nuevo lote completo de pipeline.
   Una única operación MERGE cierra la versión anterior y abre la nueva. Verificar un único `es_actual=true` por cliente.
6. Repetir lote: misma historia. Cambiar B→A en otro lote: tercera versión y tercer `id_version`.
   Probar NULL→valor si procede. Un cambio solo en un atributo clasificado tipo1 actualiza la versión vigente sin abrir otra;
   la plantilla permite `columnas_tipo1`, aunque el ejemplo mínimo contiene solo ciudad.
7. Mostrar intervalos `[vigente_desde, vigente_hasta)`, sin solapamientos, y `fwk_modelos`.
   Las pruebas Delta simulan fallo después del histórico y antes de la proyección: el reintento completa la proyección
   usando la versión histórica registrada.

Esta activación cubre tipo1→SCD2. Cambiar después la lista de atributos de una dimensión ya historificada requiere una
migración adicional acordada; no consiste en reutilizar el flag de activación. No se implementa vigencia de negocio retroactiva.

## 03:20–03:40 · Demo 6: consumo

En Fabric/Power BI, conectar la dimensión vigente por `id_cliente`. Explicar que conectar el histórico directamente por
esa clave multiplicaría las filas. La unión temporal de hechos a versiones necesita fecha del hecho y una definición
de negocio aprobada; no se implementa por inferencia en esta plantilla. Los informes se crean en Fabric y se sincronizan.

## 03:40–03:55 · Demo 7: calidad del cambio

Mostrar diff de contratos, catálogo regenerado, tests de escenarios y linters. Comparar una regla desconocida o un
modelo que deja atributos sin clasificar con un cambio válido. Preparar PR revisable sin mezclar credenciales ni datos.

## 03:55–04:00 · Cierre y recuperación

Comprobar que no quedan lotes pendientes; restaurar los valores sembrados en SQL usando el respaldo de la demo.
Conservar evidencia y commits. No ejecutar VACUUM sobre versiones necesarias para reintentos o una migración pendiente.

## Operación y compatibilidad

- `a_silver` exige lote explícito. El antiguo batch vacío se sustituye por `nb_90_ops_revalidar`.
- `fwk_ejecuciones` añade `filas_consolidadas`; `filas_escritas` cuenta claves aceptadas, incluidas las que no cambian.
  La identidad de auditoría `fuente` pasa a `dominio.fuente`. Las nuevas cuarentenas están en `fwk_cuarentena`; las
  antiguas `_cuarentena_<tabla>` no se borran ni migran automáticamente.
- `fwk_modelos` guarda el último estado por modelo; el historial de ejecución se consulta en auditoría y Delta.
  No hay transacción distribuida entre tablas. El pipeline debe esperar a que gold confirme antes de habilitar consumo.
- Para recuperar una activación: detener escritores, conservar registro y versión previa, reintentar el mismo lote.
  Una vuelta a tipo1 exige restaurar explícitamente la versión previa junto a su contrato/configuración y resolver el
  registro de control; no basta con cambiar el YAML. Preparar ese rollback en una copia antes de tocar un entorno real.
- Las reglas y las rutas de contratos son configuración versionada de confianza, revisada en Git; no aceptar YAML
  arbitrario de usuarios finales. El SQL de extracción solo interpola identificadores validados y límites datetime tipados.

Referencias de implementación: [conector SQL nativo de Fabric](https://learn.microsoft.com/en-us/fabric/data-engineering/spark-sql-connector),
[MERGE Delta](https://docs.delta.io/delta-update/) y
[subida de bibliotecas al Environment](https://learn.microsoft.com/en-us/rest/api/fabric/environment/staging/upload-custom-library).
