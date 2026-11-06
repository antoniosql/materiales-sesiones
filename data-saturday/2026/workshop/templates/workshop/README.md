# Checkpoints del workshop

Copiar el contenido de cada etapa a la raíz del **proyecto generado**, conservando la estructura. Los contratos van
primero, la configuración después. Validar, regenerar catálogo y publicar antes de ejecutar notebooks.

| Etapa | Cambio que se demuestra |
|---|---|
| 01_base | SQL completo, Q1 y dimensión tipo1 |
| 02_calidad | Q2 exige motivo y revalida también filas aceptadas |
| 03_fallar | Q3 detiene la publicación ante un rechazo |
| 04_incremental | CRM cambia extracción completa por incremental |
| 05_scd2 | Ciudad comienza a historificarse; contrato histórico y proyección actual |

Los contratos parten de `templates/contrato/contrato.yml`. El test `tests/contracts/test_workshop.py` valida
los JSON Schema y las referencias cruzadas de todos los checkpoints. No contienen credenciales ni despliegan recursos.
Las reglas Q1–Q3 son el caso docente del plan del workshop, no una política universal para todas las devoluciones.

Recorrido, parámetros, resultados y límites: [runbook](../../docs/runbooks/workshop-evolutivo.md).
