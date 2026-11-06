# Preparación del instructor · Edición Fabric propio + CSV

Este recorrido reemplaza la preparación anterior que entregaba bases SQL o una modalidad guiada a alumnos.
Cada alumno trae su propia capacidad/suscripción Fabric, tenant, workspaces y Environment. Los datos se distribuyen
como CSV; el acceso a los orígenes Azure solo es necesario para que el instructor renueve el volcado.

## 1. Configuración privada

En la copia del instructor hay `.env.instructor` (local, ignorado por Git) y `.env.instructor.example` (distribuible).
El fichero local se ha rellenado con tenant, suscripción, grupo de recursos, servidor/base SQL y cuenta/endpoint/base
Cosmos del despliegue existente. Incluye tres contraseñas aleatorias para los usuarios SQL propuestos del laboratorio.
Son valores de preparación: **no se han creado esos usuarios, bases ni recursos**.

Completa los marcadores de capacidad Fabric, IDs de workspaces, Environment y recursos opcionales. No publiques el fichero.
Si preparas otro equipo, copia el `.example` y cumpliméntalo localmente; no distribuyas el fichero privado a alumnos.

| Grupo de variables | Uso |
|---|---|
| `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP` | Identidad y ubicación lógica de los orígenes |
| `SQL_SOURCE_*` | Servidor, base y cadena de conexión SQL de origen; exportación mediante Entra |
| `SQL_SOURCE_USER`, `SQL_SOURCE_PASSWORD` | Reserva para inventario de una identidad SQL; el exportador actual usa Entra |
| `COSMOS_SOURCE_*` | Cuenta, endpoint, base y clave de **solo lectura**; si se omite, Azure CLI la obtiene en memoria |
| `COSMOS_SOURCE_CONNECTION_STRING` | Reserva para guardar una conexión; el exportador usa endpoint + clave de solo lectura |
| `SQL_LAB_*` | Servidor/base opcionales y nombres/contraseñas de administrador, lector y editor por crear |
| `COSMOS_LAB_*` | Cuenta, endpoint, base y cadena opcionales por crear; Cosmos no utiliza usuarios/contraseñas SQL |
| `FABRIC_CAPACITY_ID`, `WS_*`, `ENV_FWK_ID` | Recursos de tu ensayo; IDs pendientes deben completarse antes de publicar |
| `PROYECTO`, `WORKSPACE_*_NOMBRE`, `LAKEHOUSE_ESQUEMA`, `DATA_ROOT` | Nombres, esquema y carpeta de datos de tu ejecución |

Los nombres propuestos son `frasohome-workshop-instructor`, `fsh_lab_admin`, `fsh_lab_lector` y `fsh_lab_editor`.
Para SQL opcional, el lector solo necesita SELECT en las tablas docentes y el editor UPDATE de las filas de la demo;
la cuenta administrativa se reserva a preparación. No uses esas identidades contra la base viva de la aplicación.
Si provisionas esos recursos posteriormente, compón `SQL_LAB_CONNECTION_STRING` con el servidor, base y usuario
correspondientes, y la contraseña local. Los alumnos no necesitan estos recursos.

No hacen falta secretos Fabric: se usa la sesión Entra de Azure CLI. `.env.instructor` nunca se interpreta como código.
`crear_proyecto.py` excluye ambos dotenv privados y el ejemplo del instructor; solo conserva `.env.alumno.example`.

## 2. Comprobar o renovar el volcado

El volcado incluido fue leído el 2 de noviembre de 2026 entre 07:28:38 y 07:45:25 UTC:
49 tablas SQL, 41.454 filas; diez contenedores Cosmos, 18.665 documentos. Es una extracción secuencial,
no un snapshot transaccional entre servicios. `data/original/manifest.json` es la referencia verificable.

```powershell
py -3.12 -m venv .venv
$Python = Join-Path (Get-Location).Path '.venv\Scripts\python.exe'
& $Python -m pip install -e '.[dev,deploy,export]' build
& $Python -m scripts.modificar_csv verificar
```

Solo si quieres actualizar los datos, inicia sesión en el tenant y suscripción de los orígenes, comprueba SELECT en SQL
y permiso para leer claves Cosmos, y ejecuta el exportador hacia **una carpeta nueva**:

```powershell
az login --tenant '<tenant-del-instructor>'
az account set --subscription '<suscripcion-del-origen>'
& $Python -m scripts.exportar_datos --env-file .env.instructor --destino data/renovacion/original
& $Python -m scripts.modificar_csv verificar --data data/renovacion
```

La base SQL serverless puede necesitar reanudarse; hay reintentos. Una extracción fallida queda sin manifiesto final
y no debe distribuirse. No se cambian firewall, usuarios ni datos de origen. La clave Cosmos se obtiene con
`--type read-only-keys`, queda en memoria y no se escribe al log ni al manifiesto. SQL usa token Entra temporal.
Las cadenas de origen SQL personalizadas deben ser compatibles con token Entra y no incluir UID/PWD/Authentication.

Antes de sustituir el paquete distribuido, revisa recuentos, tipos esperados, datos sintéticos y exclusiones declaradas:
`app.*` (autenticación y sesiones) y `lab.identity_ground_truth` (solución). Distribuye solo `data/original`,
`data/README.md` y los scripts; no `data/laboratorio`, ficheros dotenv privados ni logs del instructor.
Si el origen cambia, recalcula los resultados de calidad; los números de la guía corresponden al manifiesto incluido.

## 3. Preparar tu ensayo y la entrega a alumnos

1. Envía al alumno `docs/workshop/01_antes-de-la-sesion.md`. Exige capacidad propia activa y preparación previa;
   no hay modalidad sin Fabric ni asignación de cuentas del instructor.
2. Completa tu `.env.instructor` para los tres workspaces de ensayo y `env_fwk`, vacíos de datos del workshop.
3. Para seguir literalmente los comandos de la guía común, crea un `.env.alumno` **con solo tus campos Fabric**.
   Copia `.env.alumno.example` y cumpliméntalo: nunca copies en él el fichero privado completo.
4. Sigue `02_seguir-las-demos.md` de principio a fin. Greenfield crea un producto nuevo y nuevos logicalId;
   los recursos cloud se asignan desde tu fichero local. La publicación del Environment debe terminar antes de notebooks.
5. Tras publicar, vincula todos los notebooks a `env_fwk`, detén sesiones anteriores y comprueba `datafwk 0.3.0`.
6. Comprueba acceso entre workspaces, esquema de lakehouses, subida de CSV y YAML y la primera carga CRM.
7. Reserva otra pareja de workspaces vacíos y otro producto para el día del taller; conserva tu ensayo como referencia.
   Un `restaurar` no borra historia ni reinicia marcas.

Los CSV de trabajo proyectan los nombres SQL a las columnas contractuales españolas, sin alterar valores originales.
Las modificaciones posteriores se aplican a esos CSV antes de la ingesta. Cosmos conserva sus documentos completos
en `documento_json`; no se promete un pipeline Cosmos silver sin sus contratos.

## 4. Ensayo de aceptación

| Punto | Resultado de este paquete |
|---|---|
| Integridad | Todos los hashes, recuentos y JSON del volcado correctos |
| Greenfield | Destino nuevo, GUID distintos, ningún dotenv privado ni CSV mutado copiado |
| CRM completa | 100 clientes; C0001 Sevilla; marca confirmada |
| Defectos + Q1 | 397 observaciones, 387 válidas, 10 rechazos |
| Q2 revalidación | 358 válidas, 39 rechazos; marca sin avance |
| Q3 fallar | Error previo a publicación; lote pendiente; silver sigue en 358 |
| Q4 recuperación | Mismo lote termina; 358 válidas, 39 rechazos |
| Incremental | Una modificación CRM, sin duplicar claves; siguiente ventana vacía tras esperar |
| SCD2 | Barcelona → Valencia → Barcelona; tres versiones del cliente y una vigente |
| Restauración | Cliente vuelve a Sevilla con cuarta versión; Q4 revalidada deja 362 devoluciones válidas |

No incluyas un ensayo remoto como realizado si solo has ejecutado los tests locales. Registra runtime, capacidad,
commit y resultados de tu ensayo en `00_ficha-laboratorio.md`. Los IDs y contraseñas se guardan exclusivamente en dotenv.

## 5. Incidencias que debes ensayar

- `403` de OneLake: tenant incorrecto, permisos o workspace equivocado; verifica el propio `.env`, no otro alumno.
- Paquete antiguo: publicación pendiente del Environment o sesión Spark anterior; publicar, asociar y reiniciar sesión.
- Incremental sin baseline: completar bronze/silver en completa; no inventar ni adelantar marcas.
- Cero cambios tras editar ciudad: publicar CSV, esperar estabilización, comprobar reloj UTC y usar un lote nuevo.
- Lote pendiente: recuperar su contrato/operación y repetir ese ID antes de iniciar otro.
- Resultados de calidad distintos: comprobar el manifiesto y que los cuatro defectos se sembraron antes del primer lote
  de devoluciones. Un merge posterior conserva la última fila válida; la revalidación reconstruye el conjunto actual.

El calendario y los contenidos teóricos están en `02_plan-sesion-4-horas.md`; los comandos reproducibles y resultados
de cada demo están en `02_seguir-las-demos.md`.
