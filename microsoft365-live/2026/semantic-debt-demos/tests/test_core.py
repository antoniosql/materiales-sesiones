"""Tests sin tenant: puntuación del test set, derivación de FS-KB-02, conversión md→docx y cifras."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from docx import Document

from semdebt import documents, evaluate, figures
from semdebt.config import load_scenario

KB01_SAMPLE = """# Política de devoluciones (omnichannel) - FraSoHome

Fuente: `FS-KB-01_Politica_Devoluciones_v1.3_Vigente.docx`.

## 2. Plazos

| Canal | Plazo | Observaciones |
| --- | --- | --- |
| E-commerce | 45 días naturales | Debe solicitarse por el portal. |
| Tienda física | 30 días naturales | Requiere ticket. |

## 11. Escalado y casos especiales

- Cliente VIP (Oro/Platino): se puede conceder excepción una vez por semestre (aprobación de Store Manager).

| ID documento | FS-KB-01 |
| --- | --- |
| Versión | 1.3 |
| Estado | VIGENTE |
| Vigente desde | 15/01/2026 |

| Versión | Fecha | Cambios |
| --- | --- | --- |
| 1.2 | 01/06/2025 | Revisión de excepciones. |
| 1.3 | 15/01/2026 | Se amplía plazo online a 45 días; se clarifica reembolso en pagos mixtos. |
"""


def test_keywords_and_alternatives():
    assert evaluate.keywords_ok("El plazo es de 45 días naturales.", "45 dias")
    assert evaluate.keywords_ok("Crecieron un +2.5 %", "2,5|2.5")
    assert not evaluate.keywords_ok("Crecieron un 2 %", "2,5|2.5")
    assert evaluate.keywords_ok("reservado y bloqueado", "reservado;bloqueado")
    assert not evaluate.keywords_ok("solo reservado", "reservado;bloqueado")
    assert not evaluate.keywords_ok("cualquier cosa", "")


def test_cites_and_abstains():
    urls = ["https://frasohome.sharepoint.com/sites/X/Documentos%20compartidos/Definitivos/FS-KB-01_Politica.docx"]
    assert evaluate.cites(urls, "FS-KB-01")
    assert evaluate.cites(urls, "FS-KB-03|FS-KB-01")
    assert not evaluate.cites(urls, "FS-KB-03")
    assert evaluate.abstains("No hay un procedimiento documentado. Contacta con Atención al Cliente.")
    assert not evaluate.abstains("Reembolsa el importe total a la tarjeta.")


def test_score_trc_rules():
    cases = {c["id"]: c for c in evaluate.load_testset()}
    assert len(cases) == 20
    ok = evaluate.score(cases["X1"], "Son 45 días naturales.", ["…/FS-KB-01_Politica_Devoluciones_v1.3_Vigente.docx"])
    assert ok.cuenta_trc
    wrong_source = evaluate.score(cases["X1"], "Son 45 días naturales.", ["…/Informe_Comercial_Q4_2025_FINAL.pptx"])
    assert wrong_source.correcta and not wrong_source.cuenta_trc
    tacit = evaluate.score(cases["T1"], "No está documentado: contacta con Atención al Cliente.", [])
    assert tacit.abstencion and not tacit.cuenta_trc
    estados = [c["estado"] for c in cases.values()]
    assert estados.count("Canonica") == 8 and estados.count("Duplicada") == 3
    assert estados.count("Contradictoria") == 4 and estados.count("Tacita") == 3 and estados.count("Inexistente") == 2


def test_derive_kb02_from_markdown():
    text, counts = documents.derive_kb02_text(KB01_SAMPLE)
    assert "| E-commerce | 30 días naturales |" in text
    assert "45 días" not in text
    assert "| Versión | 1.2 |" in text and "| Estado | OBSOLETA |" in text
    assert "| ID documento | FS-KB-02 |" in text
    assert "15/01/2026" not in text
    assert counts["historial_v1.3_eliminado"] == 2   # fila 1.3 del historial + línea VIP
    assert "Cliente VIP" not in text
    assert "| Vigente desde | 01/09/2025 |" in text


def test_derive_kb02_requires_pattern():
    with pytest.raises(ValueError):
        documents.derive_kb02_text("# Sin la fila de e-commerce")


def test_md_to_docx_roundtrip(tmp_path: Path):
    out = tmp_path / "kb01.docx"
    documents.md_to_docx(KB01_SAMPLE, out, title="kb01")
    doc = Document(out)
    assert len(doc.tables) == 3
    assert any("Cliente VIP" in p.text for p in doc.paragraphs)
    assert doc.tables[0].cell(1, 1).text == "45 días naturales"
    kb02 = tmp_path / "kb02.docx"
    counts = documents.derive_kb02_docx(out, kb02)
    d2 = Document(kb02)
    assert d2.tables[0].cell(1, 1).text == "30 días naturales"
    assert d2.tables[1].cell(1, 1).text == "1.2" and d2.tables[1].cell(2, 1).text == "OBSOLETA"
    assert all(r.cells[0].text != "1.3" for r in d2.tables[2].rows)
    assert not any("Cliente VIP" in p.text for p in d2.paragraphs)
    assert d2.tables[1].cell(3, 1).text == "01/09/2025"
    assert counts["45→30"] >= 1


def test_scenario_is_consistent():
    sc = load_scenario()
    needed = documents.required_files(sc)
    produced = set(documents.KB_SOURCES) | {"FS-KB-02_Politica_Devoluciones_v1.2.docx", "Informe_Comercial_Q4_2025_FINAL.pptx",
                                            "Cuadro_mando_tiendas_v3_bueno.xlsx", "Cierre_mensual_2025-12_Finanzas.xlsx",
                                            "Manual_caja_2023.docx", "KPI_Cierre_2025_Oficial.docx",
                                            "FS-KB-00_Mapa_Dominios_y_Responsables_v1.0.docx"}
    assert needed <= produced, needed - produced
    dominios = set(sc["termstore"]["sets"]["dominio"]["terms"])
    assert {f["dominio"] for f in sc["sites"]["kb_oficial"]["files"]} <= dominios
    estados = set(sc["columns"]["estado"]["choices"])
    assert {f["estado"] for f in sc["sites"]["kb_oficial"]["files"]} <= estados


def test_documents_folder_is_complete():
    from semdebt.config import ROOT
    missing = [n for n in documents.required_files(load_scenario()) if not (ROOT / "documentos" / n).exists()]
    assert not missing, f"Faltan en documentos/: {missing}"


def test_tacit_questions_route_to_owner():
    cases = {c["id"]: c for c in evaluate.load_testset()}
    r = evaluate.score(cases["T1"], "No está documentado. Contacta con Jorge T. (Atención al cliente).", [])
    assert r.abstencion and r.correcta and not r.cuenta_trc


@pytest.mark.skipif(not os.environ.get("CASE_DATA_DIR"), reason="Define CASE_DATA_DIR para validar las cifras reales")
def test_real_figures_match_slides():
    fig = figures.compute(Path(os.environ["CASE_DATA_DIR"]))
    assert figures.compare(fig, load_scenario()["expected_figures"]) == []
