# Tests de integración

Se ejecutan **solo en el pipeline de despliegue**, después de desplegar en Test, contra el workspace real:

1. Copiar a `Files/landing/` de Test un juego de datos de prueba pequeño y conocido (`tests/integration/datos/`)
2. Lanzar `nb_10_bronze_ingesta` y `nb_20_silver_estandarizar` con la API de *Job Scheduler* de Fabric
3. Comprobar en `fwk_ejecuciones` que todas las ejecuciones del batch están en `ok` y reconcilian
4. Comprobar conteos esperados en silver y en cuarentena

Se marcan con `@pytest.mark.integration` y por defecto se excluyen (`addopts` en `pyproject.toml`).
Para lanzarlos: `pytest -m integration`.
