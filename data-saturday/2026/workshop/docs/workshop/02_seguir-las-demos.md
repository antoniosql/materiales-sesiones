# Workshop de cuatro horas · Demos en tu propio Fabric

Trabaja desde PowerShell en la raíz del proyecto generado, salvo el primer bloque. Conserva `$Python`, `$Plantilla` y el fichero `.env.alumno` de la [preparación](01_antes-de-la-sesion.md). Cada persona utiliza sus propios recursos.

## 00:00–00:15 · Arquitectura y reglas

Teoría: un workspace por responsabilidad; bronze conserva observaciones, silver aplica contrato y gold modela consumo.
Separar extracción completa/incremental, escritura `merge` e historificación SCD2. Revisar `AGENTS.md`, convenciones, glosario, contratos, modelos y las funciones de `src/datafwk`. Los notebooks solo orquestan.

Datos: Las exclusiones están en `data/README.md`.

## 00:15–00:50 · Demo 1: generar un proyecto greenfield

Teoría: crear un producto independiente exige nuevos identificadores de items, configuración propia y secretos locales.
El generador no copia `.git`, entornos virtuales, credenciales ni CSV ya mutados.

Desde la copia entregada:

```powershell
$Producto = Join-Path (Split-Path $Plantilla -Parent) 'fsh-alumno01-lab'
& $Python scripts/crear_proyecto.py $Producto --proyecto fsh-alumno01
Copy-Item (Join-Path $Plantilla '.env.alumno') (Join-Path $Producto '.env.alumno')
Set-Location $Producto
& $Python -m pip install -e '.[dev,deploy]'
git init -b main
& $Python -m scripts.laboratorio configurar --env-file .env.alumno
& $Python -m scripts.laboratorio checkpoint --paso base --env-file .env.alumno
& $Python -m scripts.modificar_csv preparar
& $Python scripts/validar_contratos.py
& $Python scripts/generar_catalogo.py
```

Sustituye `fsh-alumno01` por TU proyecto en ambos comandos y en `.env.alumno`. El destino debe ser nuevo.
Resultado: contratos Q1 y tipo1, fuentes CSV en completa, `fecha_cambio` como marca CRM, nombres de tu workspace en configuración y `parameter.yml`, nuevos `logicalId` y dos CSV de trabajo. `escenario.json` indica cliente `C0001` (Sevilla) y cuatro devoluciones elegidas. No apliques `checkpoint base` sobre un laboratorio que ya evolucionó.

Publica los recursos sin eliminar items huérfanos:

```powershell
& $Python -m scripts.laboratorio lakehouses --env-file .env.alumno
& $Python -m build --wheel
& $Python -m scripts.laboratorio wheel --env-file .env.alumno
& $Python -m scripts.laboratorio notebooks --env-file .env.alumno
& $Python -m scripts.laboratorio config --env-file .env.alumno
& $Python -m scripts.laboratorio datos --env-file .env.alumno
```

Resultado: `lh_bronze`, `lh_silver`, `lh_gold` en datos; cinco notebooks en ingeniería; wheel 0.3.0 publicado en
`env_fwk`; YAML en `lh_bronze/Files/_framework` y CSV en `Files/landing`.
En Fabric, vincula **cada notebook** al Environment `env_fwk` publicado y guarda. Detén sesiones anteriores para que carguen el nuevo wheel. Comprueba `LAKEHOUSE_ESQUEMA` contra el tipo real de lakehouse.
No publiques analítica ni ejecutes `desplegar.py` completo: estos ejercicios crean la dimensión del workshop,
no las tablas de ventas de los ejemplos genéricos de la plantilla.

## Cómo ejecutar y comprobar un lote

Abre el notebook en Fabric, cambia su celda de parámetros y usa **Run all**. En todos: `entorno="dev"`, `workspace_datos="<tu nombre exacto de workspace datos>"`.
No cambies lógica ni imports. El Environment ya debe estar seleccionado.

| Operación | Notebook | Parámetros adicionales |
|---|---|---|
| Bronze CRM | `nb_10_bronze_ingesta` | `dominio="crm"`, `fuente="clientes_crm"`, `batch_id` del paso |
| Silver CRM | `nb_20_silver_estandarizar` | Mismos dominio, fuente y lote que bronze |
| Gold CRM | `nb_30_gold_dimension` | Los anteriores y `modelo="dim_cliente"` |
| Bronze/silver devoluciones | Los notebooks 10/20 | `dominio="devoluciones"`, `fuente="lineas_devolucion"` |
| Revalidar devoluciones | `nb_90_ops_revalidar` | Mismo dominio/fuente; lote nuevo excepto al reintentar |
| Activar historia CRM | `nb_90_ops_activar_scd2` | CRM, `modelo="dim_cliente"`, lote silver confirmado |

Ejecuta en orden y espera a que termine cada notebook. Un lote es el mismo identificador en bronze/silver/gold;
cada nueva observación lleva uno nuevo. Reintentar significa repetir el identificador original y su operación.
Usa las salidas de los notebooks y el SQL analytics endpoint del lakehouse correspondiente para comprobar tablas.
El endpoint puede tardar en sincronizar metadatos; refresca antes de interpretar una tabla ausente como fallo.

## 00:50–01:15 · Demo 2: carga completa y dimensión tipo1

Teoría: clave de negocio, tipos contractuales, diferencia entre observación y actualización de origen,
baseline que establece una marca confirmada. `merge` evita duplicar claves; bronze conserva cada lote.

1. Abre `config/fuentes/crm.yml`, contrato silver y modelo gold. Marca `fecha_cambio`, completa, escritura merge, tipo1.
2. Ejecuta bronze → silver → gold CRM con `batch_id="crm-base"`.
3. Esperado: 100 observaciones CRM; 100 clientes silver y 100 filas en `dim_cliente`; `C0001` tiene Sevilla.
4. Repite los tres notebooks con `crm-base`: ni bronze ni silver ni gold deben duplicarse.
5. En silver revisa `fwk_lotes`, `fwk_marcas` y `fwk_ejecuciones`: CRM confirmado, marca UTC registrada.

No cargues devoluciones todavía: la siguiente demo siembra los defectos antes de su primer lote.

## 01:15–01:55 · Demo 3: errores de origen y evolución de cuarentena

Teoría: dato inválido versus regla que cambia, evidencia por versión, revalidación de datos ya aceptados,
política cuarentena frente a fallar y recuperación de lote pendiente. Reglas ya pactadas en los contratos:
reembolso no negativo/no nulo y, desde Q2, motivo no nulo. Cadena vacía no equivale automáticamente a NULL.

```powershell
& $Python -m scripts.modificar_csv defectos
& $Python -m scripts.laboratorio datos --env-file .env.alumno
```

El script cambia **el CSV de origen**: importe negativo, importe NULL y dos motivos NULL, en cuatro claves válidas.
El volcado original se conserva. Ejecuta bronze → silver devoluciones con `batch_id="dev-q1"`.
Esperado con este volcado: 397 leídas, **387 válidas y 10 rechazadas**. Ya existían ocho rechazos Q1 antes de la demo.

```powershell
& $Python -m scripts.laboratorio checkpoint --paso calidad --env-file .env.alumno
& $Python scripts/validar_contratos.py
& $Python scripts/generar_catalogo.py
git diff -- contracts/silver/lineas_devolucion.yml
& $Python -m scripts.laboratorio config --env-file .env.alumno
```

Contrato Q2: `version: 2`, `motivo.nulo: false`. Ejecuta revalidación con `batch_id="dev-q2"`.
Esperado: **358 válidas y 39 rechazadas**, incluidas filas aceptadas con Q1. Se reconstruye silver desde bronze,
sin leer CSV ni avanzar marca. La tabla de cuarentena guarda evidencia histórica; su total acumulado no es el
número de rechazos pendientes. Repite `dev-q2`: no duplica evidencia.

```powershell
& $Python -m scripts.laboratorio checkpoint --paso fallar --env-file .env.alumno
& $Python -m scripts.laboratorio config --env-file .env.alumno
```

Q3 (`version: 3`, política `fallar`): revalidación `batch_id="dev-q3"` debe producir error de contrato.
Silver sigue con 358 filas; cuarentena y marca no cambian por el intento fallido. Revisa auditoría y el lote pendiente.

```powershell
& $Python -m scripts.laboratorio checkpoint --paso recuperar --env-file .env.alumno
& $Python -m scripts.laboratorio config --env-file .env.alumno
```

Q4 mantiene motivo obligatorio y recupera cuarentena con `version: 4`. Reejecuta **el mismo `dev-q3`** en revalidación:
debe confirmar, con 358 válidas y 39 rechazos. El cambio de contrato es explícito; no se salta el lote fallido.

## 01:55–02:10 · Descanso

## 02:10–02:40 · Demo 4: completa → incremental

Teoría: marca confirmada, límite superior fijo, estabilización y solape de cinco segundos; extracción y escritura son decisiones independientes. En CSV se lee el fichero completo y se filtra: no es pushdown, CDC ni ahorro de I/O.

```powershell
& $Python -m scripts.laboratorio checkpoint --paso incremental --env-file .env.alumno
& $Python scripts/validar_contratos.py
& $Python -m scripts.laboratorio config --env-file .env.alumno
& $Python -m scripts.modificar_csv ciudad --valor Barcelona
& $Python -m scripts.laboratorio datos --env-file .env.alumno
Start-Sleep -Seconds 6
```

CRM ahora es incremental y sigue escribiendo merge. El script actualiza ciudad y `fecha_cambio` UTC de `C0001`.
Ejecuta bronze → silver → gold CRM con `batch_id="crm-inc-1"`.
Esperado: una fila dentro de la ventana; silver/gold mantienen 100 clientes; C0001 pasa a Barcelona sin historia tipo1.
Repite el mismo lote: no duplica datos ni cambia la marca. Espera al menos 11 segundos y ejecuta otro lote
`crm-inc-2` sin modificar CSV: se esperan cero filas extraídas y silver conserva 100; el límite puede avanzar.
Si el reloj local está adelantado respecto a Fabric, corrígelo: una marca futura quedará fuera hasta que llegue su ventana.

No se detectan borrados físicos ni ciudades intermedias que cambien dos veces entre lecturas. Devoluciones permanece en completa porque no dispone de una marca de modificación fiable.

## 02:40–03:20 · Demo 5: añadir SCD2 a ciudad, que antes era tipo1

Teoría: historia por observación UTC, nueva clave por versión, intervalos `[desde,hasta)`, proyección vigente y cambio de grano para consumidores. No reconstruir Sevilla anterior a la activación como si se hubiera observado bajo SCD2.

```powershell
& $Python -m scripts.laboratorio checkpoint --paso scd2 --env-file .env.alumno
& $Python scripts/validar_contratos.py
& $Python scripts/generar_catalogo.py
& $Python -m scripts.laboratorio config --env-file .env.alumno
```

El comando copia primero los dos contratos gold y después el modelo. `dim_cliente` pasa a clave `id_version`,
atributo histórico `ciudad`; `dim_cliente_actual` mantiene una fila por `id_cliente` para consumidores.

1. Sin mutaciones, ejecuta bronze → silver CRM con **nuevo** `batch_id="crm-activar"`.
2. Para ese lote ejecuta `nb_90_ops_activar_scd2` en lugar del notebook gold ordinario.
3. Esperado: 100 versiones iniciales, 100 actuales. C0001 comienza con Barcelona en el instante de activación.
4. Repite esa activación con `crm-activar`: no crea versiones adicionales.

```powershell
& $Python -m scripts.modificar_csv ciudad --valor Valencia
& $Python -m scripts.laboratorio datos --env-file .env.alumno
Start-Sleep -Seconds 6
```

Ejecuta bronze → silver → **gold ordinario** con `crm-scd2-b`. Esperado: C0001 tiene Barcelona cerrada y Valencia vigente.
Repite ese lote y comprueba que sigue con dos versiones.

```powershell
& $Python -m scripts.modificar_csv ciudad --valor Barcelona
& $Python -m scripts.laboratorio datos --env-file .env.alumno
Start-Sleep -Seconds 6
```

Nuevo lote completo `crm-scd2-a`: C0001 tiene tres versiones (Barcelona → Valencia → Barcelona), identificadores
distintos y una sola vigente. Total esperado: 102 filas históricas y 100 en la proyección actual.
Consulta en el endpoint de `lh_gold` (cambia `dbo` si usas otro esquema):

```sql
SELECT id_cliente, ciudad, id_version, vigente_desde, vigente_hasta, es_actual
FROM dbo.dim_cliente
WHERE id_cliente = 'C0001'
ORDER BY vigente_desde;

SELECT id_cliente, COUNT(*) AS actuales
FROM dbo.dim_cliente
WHERE es_actual = 1
GROUP BY id_cliente
HAVING COUNT(*) <> 1;
```

La segunda consulta no debe devolver filas. No vuelvas a activar SCD2 para modificar una dimensión que ya tiene historia:
cambiar su lista de atributos históricos requiere otra migración.

## 03:20–03:40 · Demo 6: consumo y documentos Cosmos

Teoría: una dimensión vigente se relaciona por `id_cliente`; relacionar hechos directamente con el histórico por esa clave puede multiplicar filas. Una unión temporal necesita fecha del hecho y definición de negocio acordada.

1. En el endpoint gold consulta `SELECT COUNT(*) FROM dbo.dim_cliente_actual;`: esperado 100.
2. Compara con las 102 versiones históricas y las tres filas de C0001. No crear KPIs no definidos.
3. Abre `data/original/manifest.json`: revisa los diez contenedores Cosmos y sus claves de partición.
4. Abre una parte CSV con un lector CSV o ejecuta el ejemplo de `data/README.md`: `documento_json` se deserializa    sin perder arrays, objetos ni IDs. Ejecuta `python -m scripts.modificar_csv verificar`: todas las partes deben pasar.
5. Explica cómo una nueva fuente Cosmos necesitaría proyección y contrato antes de incorporarse al pipeline.

## 03:40–03:55 · Demo 7: revisión del cambio

Teoría: el contrato es una API; la evidencia para aprobar un cambio incluye reglas, catálogo, pruebas y operación.

```powershell
& $Python scripts/generar_catalogo.py
& $Python scripts/validar_contratos.py
& $Python scripts/agente_lint.py config/fuentes/crm.yml contracts/silver/lineas_devolucion.yml
git status --short
git check-ignore .env.alumno data/laboratorio/clientes_crm.csv
```

Esperado: dotenv y CSV mutables ignorados; contratos Q4/SCD2 y configuración incremental visibles para revisión.
Para el greenfield aún sin commit, revisa también los ficheros no seguidos (un `git diff` vacío no implica ausencia de cambios).
Si preparaste Spark local, ejecuta `python -m pytest --delta` y `pre-commit run --all-files`; ante una limitación de herramientas local, registra cuál y completa la validación en CI. No silencies reglas para conseguir verde.

## 03:55–04:00 · Restauración y cierre

```powershell
& $Python -m scripts.modificar_csv restaurar
& $Python -m scripts.laboratorio datos --env-file .env.alumno
Start-Sleep -Seconds 6
```

Nuevo lote CRM `crm-restaurar`: C0001 vuelve a Sevilla y abre una cuarta versión; no se borra historia.
Para devoluciones, ejecuta bronze → silver con `dev-restaurar` y después revalidación `dev-restaurar-q4` para reconstruir el estado bajo Q4: esperado 362 válidas y 35 rechazos naturales. Restaurar no significa limpiar los defectos originales.
La cuarentena conserva evidencia histórica. Para otro ensayo desde cero, utiliza una copia greenfield y workspaces vacíos.
