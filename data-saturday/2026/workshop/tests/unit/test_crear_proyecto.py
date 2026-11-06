import json

import pytest

from scripts.crear_proyecto import crear


def test_greenfield_copia_config_regenera_ids_y_excluye_secretos(tmp_path):
    origen = tmp_path / "plantilla"
    origen.mkdir()
    (origen / ".env").write_text("NO COPIAR", encoding="utf-8")
    (origen / ".git").mkdir()
    (origen / ".git" / "config").write_text("local", encoding="utf-8")
    item = origen / "fabric" / "datos" / "lh_bronze.Lakehouse"
    item.mkdir(parents=True)
    (item / ".platform").write_text(json.dumps({"config": {"logicalId": "<id_anterior>"}}), encoding="utf-8")
    config = origen / "config" / "entornos"
    config.mkdir(parents=True)
    (config / "dev.yml").write_text("workspace_datos: proyecto-datos-dev\n", encoding="utf-8")
    destino = tmp_path / "nuevo"
    assert crear(destino, "demo-datos", origen) == 2
    assert not (destino / ".env").exists()
    assert not (destino / ".git").exists()
    assert "demo-datos-datos-dev" in (destino / "config/entornos/dev.yml").read_text(encoding="utf-8")
    assert (
        json.loads((destino / item.relative_to(origen) / ".platform").read_text())["config"]["logicalId"]
        != "<id_anterior>"
    )
    with pytest.raises(ValueError, match="nueva"):
        crear(destino, "demo", origen)
    with pytest.raises(ValueError, match="dentro"):
        crear(origen / "anidado", "demo", origen)
