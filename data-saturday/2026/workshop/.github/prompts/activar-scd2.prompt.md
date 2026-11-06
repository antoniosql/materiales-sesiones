---
mode: agent
description: Activa SCD2 sobre una dimension tipo1 existente
---

Lee AGENTS.md, convenciones, glosario, el contrato existente y el runbook del workshop.
Confirma los atributos históricos con la definición aprobada; pregunta si faltan. Crea primero contrato histórico
versionado con clave id_version y contrato de proyección actual por clave de negocio. Declara todos los atributos
tipo1/SCD2 en config/modelos. No inventes historia previa ni cambies la lista de atributos de una dimensión ya SCD2
sin diseñar otra migración. Prueba repetición, A→B→A, nulos e intervalos. Usa nb_90_ops_activar_scd2 para la activación
explícita sobre un lote silver nuevo confirmado. Anuncia el cambio de contrato y grano a quien consume la dimensión.
