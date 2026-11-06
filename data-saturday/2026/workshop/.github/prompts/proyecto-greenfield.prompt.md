---
mode: agent
description: Genera un proyecto independiente a partir de la plantilla
---

Lee AGENTS.md, convenciones y el runbook del workshop. Ejecuta `scripts/crear_proyecto.py` con la carpeta nueva
y nombre de proyecto indicados por el usuario. No sobrescribas un destino existente. Comprueba GUID nuevos,
parametrización y exclusión de secretos/cachés. Incorpora primero contratos y después fuentes/modelos.
Ejecuta agente_lint, regenera catálogo, pre-commit y pytest. No despliegues recursos por inferencia.
