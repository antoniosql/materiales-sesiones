# Datos reproducibles del workshop

`original/manifest.json` registra la extracción real de SQL y Cosmos, los recuentos, las partes CSV y sus SHA-256.
No es una copia transaccional coordinada entre tablas o servicios: los orígenes pueden cambiar durante la lectura.

- `original/sql/<esquema>/<tabla>/part-*.csv`: columnas originales, cabecera en cada parte, UTF-8 y coma.
- `original/cosmos/<contenedor>/part-*.csv`: `id` y `documento_json`. JSON conserva arrays, objetos, números,
  propiedades de sistema y la clave de partición. Las rutas de partición están en el manifiesto.
- `laboratorio/`: copia de trabajo generada localmente, ignorada por Git. Contiene las dos proyecciones de las demos
  y `escenario.json` con las claves elegidas. No contiene credenciales.

Se excluyen `app.*` (autenticación/sesiones) y `lab.identity_ground_truth` (solución del ejercicio de identidad).
Es un paquete de datos docentes, no un backup para restaurar toda la aplicación. El exportador no crea DDL,
constraints, índices ni procedimientos. Los nombres de base se conservan en el manifiesto, sin endpoints ni claves.

NULL se representa con `\N`; una celda vacía sigue siendo cadena vacía. Importes mantienen su precisión decimal;
fechas usan ISO 8601; binarios, hexadecimal con prefijo `0x`. CSV no transporta tipos: las demos los aplican con
sus contratos silver. No abrir y volver a guardar con Excel: puede convertir IDs y fechas.

Desde la raíz del repositorio, después de instalar el proyecto:

```powershell
python -m scripts.modificar_csv verificar
python -m scripts.modificar_csv preparar
python -m scripts.modificar_csv defectos
python -m scripts.modificar_csv ciudad --valor Barcelona
python -m scripts.modificar_csv restaurar
```

`preparar` exige una carpeta de trabajo inexistente. `defectos` es idempotente: aplica un importe negativo,
un importe NULL y dos motivos NULL a cuatro filas inicialmente válidas. `ciudad` cambia un cliente y su marca UTC.
`restaurar` recupera los datos de negocio originales y actualiza la marca del cliente para que el incremental observe
la restauración. No borra bronze, cuarentena, historial, lotes ni marcas de Fabric. Para repetir desde cero, usa otro
proyecto/workspaces vacíos y genera otra copia greenfield.

Después de modificar: `python -m scripts.laboratorio datos --env-file .env.alumno`, esperar seis segundos y ejecutar
los notebooks con un lote nuevo. Un reintento del mismo lote reutiliza bronze y no vuelve a leer el CSV mutable.

Los diez contenedores Cosmos están disponibles para ejercicios adicionales. Para leerlos localmente sin perder estructura:

```python
import csv
import json
from pathlib import Path

for parte in sorted(Path("data/original/cosmos/eventos_web").glob("part-*.csv")):
    with parte.open(encoding="utf-8", newline="") as fichero:
        documentos = [json.loads(fila["documento_json"]) for fila in csv.DictReader(fichero)]
```

El recorrido de cuatro horas procesa CRM y devoluciones. No crea tablas silver de Cosmos sin definir antes sus contratos.
