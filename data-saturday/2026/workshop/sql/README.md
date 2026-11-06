# SQL

Consultas versionadas y revisadas por SQLFluff (configuración en `.sqlfluff`, dialecto Spark SQL).

| Carpeta | Contenido |
|---|---|
| `ops/` | Consultas de operación del framework: ejecuciones, reconciliación, cuarentena. Las usa el runbook |
| `gold/` | (cuando haga falta) transformaciones gold que se prefiera expresar en SQL en lugar de PySpark |

Se ejecutan desde un notebook con `spark.sql(open(ruta).read(), args={...})` o pegándolas en una celda `%%sql`.
Los parámetros usan la sintaxis `:nombre` de Spark SQL.
