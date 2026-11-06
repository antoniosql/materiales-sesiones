---
mode: agent
description: Cambia la extraccion completa de una fuente SQL a incremental
---

Lee fuente, contrato y runbook. Comprueba marca UTC no nula mantenida en INSERT y UPDATE del origen, completa
confirmada y ausencia de lotes pendientes. No uses created_at para detectar modificaciones. Cambia solo extraccion.modo
y conserva modo_carga merge. Explica solape, estabilización y ausencia de borrados físicos. Prueba ventana vacía,
reintento y actualización tardía dentro del solape. No prometas CDC con una marca timestamp.
