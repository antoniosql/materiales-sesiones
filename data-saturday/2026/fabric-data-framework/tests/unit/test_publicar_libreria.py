import sys
import uuid
from types import SimpleNamespace

import pytest

from scripts.publicar_libreria import main


@pytest.mark.parametrize("status", [200, 202])
def test_sube_binario_con_nombre_y_espera_publicacion(tmp_path, monkeypatch, status):
    wheel = tmp_path / "datafwk-0.2.0-py3-none-any.whl"
    wheel.write_bytes(b"wheel de prueba")
    monkeypatch.setattr(sys, "argv", ["publicar_libreria", "--wheel", str(wheel)])
    monkeypatch.setenv("WS_ING_ID", "<workspace>")
    monkeypatch.setenv("ENV_FWK_ID", "<environment>")
    token_simulado = "<token>"  # noqa: S105 -- marcador sin secreto real para probar la cabecera de autenticación
    credential = SimpleNamespace(get_token=lambda *_: SimpleNamespace(token=token_simulado))
    monkeypatch.setitem(sys.modules, "azure", SimpleNamespace())
    monkeypatch.setitem(sys.modules, "azure.identity", SimpleNamespace(AzureCliCredential=lambda: credential))
    llamadas = []
    consultas = []
    operacion = str(uuid.uuid4())

    def post(url, **kwargs):
        llamadas.append(
            (url, kwargs.get("data").read() if "data" in kwargs else None, kwargs["headers"], kwargs.get("params"))
        )
        return SimpleNamespace(
            raise_for_status=lambda: None, status_code=status, headers={"x-ms-operation-id": operacion}
        )

    respuesta = SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: {"status": "Succeeded", "properties": {"publishDetails": {"state": "Success"}}},
    )

    def get(url, **kwargs):
        consultas.append(url)
        return respuesta

    monkeypatch.setitem(sys.modules, "requests", SimpleNamespace(post=post, get=get))
    main()
    assert llamadas[0][0].endswith("/staging/libraries/datafwk-0.2.0-py3-none-any.whl")
    assert llamadas[0][1] == b"wheel de prueba"
    assert llamadas[0][2]["Content-Type"] == "application/octet-stream"
    assert llamadas[1][0].endswith("/staging/publish")
    assert llamadas[1][3] == {"beta": "false"}
    assert (consultas[0].endswith(f"/operations/{operacion}")) == (status == 202)


def test_patron_sin_wheel_informa_error(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["publicar_libreria", "--wheel", str(tmp_path / "*.whl")])
    monkeypatch.setitem(sys.modules, "azure", SimpleNamespace())
    monkeypatch.setitem(sys.modules, "azure.identity", SimpleNamespace(AzureCliCredential=lambda: None))
    with pytest.raises(SystemExit, match="exactamente un wheel"):
        main()
