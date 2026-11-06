---
mode: agent
description: Cambia condiciones de calidad con revalidacion del estado actual
---

Lee contrato, glosario y `docs/runbooks/evolucion-de-cargas.md`. No inventes reglas de negocio. Incrementa la versión del contrato y explica
qué filas previamente aceptadas pueden rechazarse. Las correcciones de datos se hacen en el origen, no en Spark.
Prueba aceptación/rechazo y política fallar. Publica contrato antes de ejecutar nb_90_ops_revalidar con lote nuevo.
Comprueba que no avanza la marca SQL y que la revalidación repetida no duplica evidencia. Anuncia el contrato modificado.
