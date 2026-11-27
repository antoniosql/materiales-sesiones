"""Pruebas sin red: escenario, cuerpos de Graph, clasificador, servidor MCP y flujo de token."""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from agentid import acceso, atributos, ciclo, config
from agentid.az import ambito_contenedor, comando_rol

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture()
def ctx(monkeypatch):
    monkeypatch.setenv("TENANT_ID", "11111111-1111-1111-1111-111111111111")
    monkeypatch.setenv("TENANT_DOMAIN", "frasohome.onmicrosoft.com")
    s = config.cargar(env_file=str(RAIZ / "no-existe.env"))
    return SimpleNamespace(s=s, esc=s.escenario)


def test_escenario_coherente(ctx):
    esc = ctx.esc
    personas = set(esc["personas"]) | {"admin"}
    for p in esc["personas"].values():
        assert p.get("manager") in (None, *personas)
    for g in esc["grupos"].values():
        assert set(g["miembros"]) <= personas
    for agente in esc["agentes"].values():
        assert agente["carril"] in esc["atributo"]["valores"]
    assert esc["personas"]["marta"]["departamento"] != esc["personas"]["marta"]["departamento_anterior"]


def test_regla_de_filtro(ctx):
    assert atributos.regla_filtro(ctx, "Produccion") == 'CustomSecurityAttribute.FraSoHome_Carril -eq "Produccion"'


def test_ca_ag_01_bloquea_riesgo_alto_en_produccion(ctx):
    c = acceso.cuerpo(ctx, "CA-AG-01")
    assert c["grantControls"]["builtInControls"] == ["block"]
    assert c["conditions"]["agentIdRiskLevels"] == "high"
    filtro = c["conditions"]["clientApplications"]["agentIdServicePrincipalFilter"]
    assert filtro["mode"] == "include" and "Produccion" in filtro["rule"]
    assert c["state"] == "enabled"


def test_ca_ag_02_en_report_only(ctx):
    c = acceso.cuerpo(ctx, "CA-AG-02")
    assert "agentIdRiskLevels" not in c["conditions"]
    assert c["state"] == "enabledForReportingButNotEnforced"


def test_workflow_avisa_y_no_transfiere(ctx):
    w = ciclo.cuerpo(ctx, ["jorge-id"])
    ids = {t["taskDefinitionId"] for t in w["tasks"]}
    assert ciclo.TAREA_TRANSFERIR not in ids
    assert {ciclo.TAREA_AVISO_MANAGER, ciclo.TAREA_AVISO_COSPONSORS} == ids
    assert w["category"] == "mover"
    assert any(a == {"name": "cc", "value": "jorge-id"} for a in w["tasks"][0]["arguments"])


def test_comando_de_la_demo2():
    ambito = ambito_contenedor("/subscriptions/s/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/st",
                               "devoluciones")
    cmd = comando_rol("agente-id", "Storage Blob Data Reader", ambito)
    assert ambito.endswith("/blobServices/default/containers/devoluciones")
    assert '--assignee-object-id "agente-id"' in cmd and "Storage Blob Data Reader" in cmd


def test_clasificador():
    from triage import clasificar, patrones
    assert clasificar("Lámpara llegó rota", "la pantalla partida")[0] == "R04"
    assert clasificar("Estantería", "falta el herraje central")[0] == "R05"
    assert clasificar("Sofá", "no encaja en el salón")[0] == "R02"
    assert clasificar("Tarjeta regalo", "quiero el dinero")[0] == "R00"
    assert patrones(["a", "a", "a", "b"]) == ["a"]


def test_correos_del_buzon():
    import json
    from triage import clasificar
    correos = json.loads((RAIZ / "datos" / "buzon" / "correos.json").read_text(encoding="utf-8"))
    codigos = [clasificar(c["asunto"], c["cuerpo"])[0] for c in correos]
    assert len(correos) == 18 and codigos.count("R04") >= 2


def test_resumen_mcp(monkeypatch):
    pytest.importorskip("mcp")
    monkeypatch.setenv("STORAGE_ACCOUNT", "stprueba")
    import server
    devs = [{"product_id": "P1", "fecha_devolucion": "2025-04-04 16:59:55", "motivo_devolucion": "Defectuoso",
             "importe_reembolsado": "103,00"},
            {"product_id": "P2", "fecha_devolucion": "20/03/2024 09:20", "motivo_devolucion": "",
             "importe_reembolsado": "1.234,50"}]
    prods = {"P1": {"categoria": "Iluminación", "subcategoria": "Bombillas"},
             "P2": {"categoria": "Muebles", "subcategoria": "Sofás"}}
    assert "Devoluciones online de Iluminación: 1" in server.resumir(devs, prods, "Iluminación")
    assert "1,337.50 EUR" in server.resumir(devs, prods)
    assert "- (ninguna)" in server.resumir(devs, prods, "", "2026-01-01")


def test_flujo_de_token_sin_secretos(monkeypatch):
    pytest.importorskip("azure.identity")
    import identity

    monkeypatch.setenv("AZURE_TENANT_ID", "t")
    monkeypatch.setenv("BLUEPRINT_APP_ID", "bp")
    monkeypatch.setenv("AGENT_IDENTITY_CLIENT_ID", "ag")
    monkeypatch.setenv("AZURE_CLIENT_ID", "mi")

    class MI:
        def __init__(self, client_id):
            assert client_id == "mi"

        def get_token(self, scope):
            assert scope == "api://AzureADTokenExchange/.default"
            return SimpleNamespace(token="token-mi")

    llamadas = []

    def post(url, data, timeout):
        llamadas.append(data)
        token = "t1" if data["client_id"] == "bp" else "final"
        return SimpleNamespace(status_code=200, json=lambda: {"access_token": token, "expires_in": 3600})

    monkeypatch.setattr(identity, "ManagedIdentityCredential", MI)
    monkeypatch.setattr(identity.requests, "post", post)
    tok = identity.TokenDelAgente().get_token("https://storage.azure.com/.default")
    assert tok.token == "final"
    assert llamadas[0]["fmi_path"] == "ag" and llamadas[0]["client_assertion"] == "token-mi"
    assert llamadas[1]["client_id"] == "ag" and llamadas[1]["client_assertion"] == "t1"
    assert "client_secret" not in llamadas[0] and "client_secret" not in llamadas[1]


def test_denegacion_de_entra(monkeypatch):
    pytest.importorskip("azure.identity")
    import identity
    for k, v in {"AZURE_TENANT_ID": "t", "BLUEPRINT_APP_ID": "bp", "AGENT_IDENTITY_CLIENT_ID": "ag",
                 "AZURE_CLIENT_ID": "mi"}.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setattr(identity, "ManagedIdentityCredential",
                        lambda client_id: SimpleNamespace(get_token=lambda s: SimpleNamespace(token="x")))
    respuesta = {"error": "invalid_grant", "error_codes": [53003],
                 "error_description": "AADSTS53003: Access has been blocked by Conditional Access policies."}
    monkeypatch.setattr(identity.requests, "post",
                        lambda url, data, timeout: SimpleNamespace(status_code=400, json=lambda: respuesta))
    with pytest.raises(identity.DenegadoPorEntra, match="53003"):
        identity.TokenDelAgente().get_token("https://storage.azure.com/.default")


def test_bicep_presente():
    for f in ("infra/main.bicep", "infra/apps.bicep", "infra/modules/foundry.bicep"):
        assert (RAIZ / f).exists()
    assert os.path.exists(RAIZ / "apps" / "fs-triage-devoluciones" / "Dockerfile")


def test_env_example_cubre_todas_las_variables():
    """Cada variable que lee el CLI está documentada en .env.example."""
    import re
    leidas = set(re.findall(r'e\("([A-Z0-9_]+)"', (RAIZ / "src" / "agentid" / "config.py").read_text(encoding="utf-8")))
    documentadas = set(re.findall(r"^([A-Z0-9_]+)=", (RAIZ / ".env.example").read_text(encoding="utf-8"), re.M))
    assert leidas <= documentadas, leidas - documentadas


def test_datos_del_caso_incluidos():
    for f in ("datos/caso/devoluciones_online.csv", "datos/caso/productos.csv", "datos/buzon/correos.json",
              "copilot-studio/agente/instrucciones.md"):
        assert (RAIZ / f).exists(), f
