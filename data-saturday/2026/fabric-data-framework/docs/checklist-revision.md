# Checklist de revisión (definition of done)

La aplica quien revisa el PR. La aplica también el asistente de IA sobre su propio trabajo antes de entregarlo.

## Datos
- [ ] Toda tabla nueva o modificada tiene contrato en `contracts/` y está en `docs/catalogo.md` (regenerado)
- [ ] La clave de negocio de la fuente coincide con la del contrato
- [ ] Hay política de rechazo explícita y está justificada (cuarentena o fallar)
- [ ] Las definiciones de negocio usadas están en `docs/glosario.md`

## Código
- [ ] La lógica está en `src/datafwk/`, no en el notebook
- [ ] Toda función nueva tiene test unitario en `tests/unit/`
- [ ] No hay rutas `abfss://`, IDs ni nombres de entorno escritos a mano
- [ ] El notebook nuevo parte de `templates/notebook/` y tiene un `logicalId` nuevo

## Operación
- [ ] La ejecución deja rastro en `fwk_ejecuciones` y reconcilia
- [ ] Si cambia un contrato existente, se ha avisado a quien consume la tabla
- [ ] Si se ha tomado una decisión de arquitectura, hay un ADR

## Automático (lo comprueba CI, no se revisa a mano)
- Linters de `.pre-commit-config.yaml`: gitleaks, Ruff, mypy, reglas del framework (FW001–FW010), contratos,
  catálogo, yamllint, esquemas, SQLFluff, actionlint, zizmor, Terraform y tflint
- `pytest` y gitleaks sobre todo el historial
- Best Practice Analyzer y Fab Inspector cuando hay modelos o informes
- Si un PR silencia una regla (`# noqa`, `# fwk: ignore`, `# type: ignore`), la revisión humana valida el motivo
