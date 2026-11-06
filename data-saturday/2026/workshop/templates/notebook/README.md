# Plantilla de notebook

1. Copia `nb_NN_capa_proposito.Notebook/` a `fabric/ingenieria/` con el nombre definitivo (`nb_30_gold_ventas_diarias.Notebook`)
2. En `.platform`: cambia `displayName` y pon un `logicalId` nuevo (`python -c "import uuid; print(uuid.uuid4())"`)
3. Rellena los `<...>` de `notebook-content.py`. Mantén la celda de parámetros tal cual: `parameter.yml` sustituye `entorno` y `workspace_datos`
4. La lógica va a `src/datafwk/` con su test. El notebook solo la llama
