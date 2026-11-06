# Runbook · Carga fallida o que no reconcilia

## 1. Localizar la ejecución
Consulta `sql/ops/ejecuciones_con_problemas.sql` (últimos 7 días, estado distinto de `ok`).
Para comprobar que no se han perdido filas: `sql/ops/reconciliacion.sql`, que debe devolver 0 filas.

## 2. Según el estado
| Estado | Qué significa | Qué hacer |
|---|---|---|
| `error` | Excepción en la carga. El mensaje está en `mensaje` | Leer el mensaje; si es de origen (fichero ausente, formato), avisar al propietario de la fuente |
| `no_reconcilia` | Leídas ≠ escritas + rechazadas: se han perdido filas | **Parar consumos de esa tabla.** Abrir incidencia: es un bug del framework |
| Contrato incumplido con política `fallar` | Datos inválidos en una tabla crítica | Revisar las filas en origen; no relajar el contrato sin el propietario |

## 3. Revisar la cuarentena
`sql/ops/cuarentena_por_motivo.sql`, con el `batch_id` como parámetro:
```python
spark.sql(open("sql/ops/cuarentena_por_motivo.sql").read(), args={"batch_id": "<batch_id>"}).show()
```

## 4. Reprocesar
Lanzar `nb_20_silver_estandarizar` con el mismo `batch_id`. El merge por clave hace la recarga idempotente.

> Prompt de ayuda: `.github/prompts/investigar-incidencia.prompt.md`
