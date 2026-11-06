"""Genera los documentos que se suben al tenant (output/docs).

- Políticas FS-KB-*: desde CASE_KB_DIR (si hay .docx con el mismo prefijo, se usa tal cual;
  si no, se convierte el .md a .docx).
- FS-KB-02 v1.2 (OBSOLETA): se deriva de FS-KB-01 v1.3 cambiando 45 → 30 días online y el control de versiones.
- Activos nuevos de la sesión: PPT de marketing, los dos Excel, el manual de caja de 2023 y la ficha
  con las cifras oficiales de cierre 2025. Las cifras salen de `figures.compute`.
"""
from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from pptx import Presentation
from pptx.util import Inches, Pt as PPt

from .figures import Figures, compute, eur, pct

log = logging.getLogger(__name__)

KB_SOURCES = {
    "FS-KB-01_Politica_Devoluciones_v1.3_Vigente.docx": "FS-KB-01_",
    "FS-KB-03_Diccionario_KPI_v1.0.docx": "FS-KB-03_",
    "FS-KB-04_Manual_Tienda_Caja_y_Pagos_Mixtos_v2.1.docx": "FS-KB-04_",
    "FS-KB-05_Guia_Conciliacion_Pagos_Ecommerce_v1.4.docx": "FS-KB-05_",
    "FS-KB-06_Taxonomia_Catalogo_y_Reglas_SKU_v1.2.docx": "FS-KB-06_",
    "FS-KB-07_Guia_Fidelizacion_CRM_v1.1.docx": "FS-KB-07_",
}

NAVY = RGBColor(0x0E, 0x1F, 0x3D)


# ------------------------------------------------------------------ markdown → docx
_BOLD = re.compile(r"\*\*(.+?)\*\*")


def _add_inline(paragraph, text: str) -> None:
    text = text.replace("`", "")
    pos = 0
    for m in _BOLD.finditer(text):
        if m.start() > pos:
            paragraph.add_run(text[pos:m.start()])
        paragraph.add_run(m.group(1)).bold = True
        pos = m.end()
    if pos < len(text):
        paragraph.add_run(text[pos:])


def _table_rows(block: list[str]) -> list[list[str]]:
    rows = []
    for line in block:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows


def md_to_docx(md_text: str, out: Path, title: str | None = None) -> None:
    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i]); i += 1
            rows = _table_rows(block)
            if rows:
                ncol = max(len(r) for r in rows)
                table = doc.add_table(rows=len(rows), cols=ncol)
                table.style = "Table Grid"
                for r, row in enumerate(rows):
                    for c in range(ncol):
                        cell = table.cell(r, c)
                        cell.text = ""
                        _add_inline(cell.paragraphs[0], row[c] if c < len(row) else "")
                        if r == 0:
                            for run in cell.paragraphs[0].runs:
                                run.bold = True
                doc.add_paragraph()
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            doc.add_heading(m.group(2).strip(), level=min(len(m.group(1)), 3) if len(m.group(1)) > 1 else 0)
        elif re.match(r"^\s*[-*]\s+", line):
            _add_inline(doc.add_paragraph(style="List Bullet"), re.sub(r"^\s*[-*]\s+", "", line))
        elif line.strip():
            _add_inline(doc.add_paragraph(), line.strip())
        i += 1
    if title:
        doc.core_properties.title = title
    doc.save(out)


# ------------------------------------------------------------------ fuentes KB
def find_source(kb_dir: Path, prefix: str) -> Path:
    if not kb_dir or not kb_dir.exists():
        raise FileNotFoundError(f"CASE_KB_DIR no existe: {kb_dir}")
    for ext in (".docx", ".md"):
        hits = sorted(kb_dir.glob(f"{prefix}*{ext}"))
        if hits:
            return hits[0]
    raise FileNotFoundError(f"No encuentro {prefix}*.docx ni .md en {kb_dir}")


def materialize(src: Path, out: Path) -> None:
    if src.suffix.lower() == ".docx":
        shutil.copyfile(src, out)
    else:
        md_to_docx(src.read_text(encoding="utf-8"), out, title=out.stem)


# ------------------------------------------------------------------ FS-KB-02 obsoleta
KB02_RULES = [
    # (patrón, reemplazo, obligatorio)
    (r"(\|\s*E-commerce\s*\|\s*)45 días naturales", r"\g<1>30 días naturales", True),
    (r"(\|\s*Vigente desde\s*\|\s*)15/01/2026", r"\g<1>01/09/2025", False),
    (r"(\|\s*Última revisión\s*\|\s*)10/02/2026", r"\g<1>01/09/2025", False),
    (r"(\|\s*Próxima revisión\s*\|\s*)10/08/2026", r"\g<1>01/03/2026", False),
    (r"(\|\s*1\.2\s*\|\s*01/09/2025\s*\|\s*)Versión anterior \(OBSOLETA\)\.", r"\g<1>Versión vigente.", False),
    (r"45 días", "30 días", False),
    (r"(\|\s*Versión\s*\|\s*)1\.3", r"\g<1>1.2", False),
    (r"(\|\s*Estado\s*\|\s*)VIGENTE", r"\g<1>OBSOLETA", False),
    (r"(\|\s*ID documento\s*\|\s*)FS-KB-01", r"\g<1>FS-KB-02", False),
    (r"FS-KB-01_Politica_Devoluciones_v1\.3_Vigente", "FS-KB-02_Politica_Devoluciones_v1.2", False),
]
KB02_DROP_ROW = re.compile(r"^\|\s*1\.3\s*\|")   # fila del historial que introduce la v1.3
# La excepción VIP la introdujo la v1.3: no puede estar en la v1.2
KB02_DROP_LINE = re.compile(r"^-\s*Cliente VIP", re.I)


def derive_kb02_text(text: str) -> tuple[str, dict]:
    counts = {}
    lines = [l for l in text.splitlines()
             if not KB02_DROP_ROW.match(l.strip()) and not KB02_DROP_LINE.match(l.strip())]
    counts["historial_v1.3_eliminado"] = len(text.splitlines()) - len(lines)
    text = "\n".join(lines)
    for pat, rep, required in KB02_RULES:
        text, n = re.subn(pat, rep, text)
        counts[pat] = n
        if required and n == 0:
            raise ValueError(f"FS-KB-01 no contiene el patrón esperado ({pat}); revisa la fuente.")
    return text, counts


def derive_kb02_docx(src_docx: Path, out: Path) -> dict:
    doc = Document(src_docx)
    counts = {"45→30": 0}

    def fix(paragraph):
        full = "".join(r.text for r in paragraph.runs)
        new = (full.replace("45 días", "30 días")
                   .replace("FS-KB-01_Politica_Devoluciones_v1.3_Vigente", "FS-KB-02_Politica_Devoluciones_v1.2"))
        if new != full and paragraph.runs:
            counts["45→30"] += full.count("45 días")
            paragraph.runs[0].text = new
            for r in paragraph.runs[1:]:
                r.text = ""

    for p in list(doc.paragraphs):
        if KB02_DROP_LINE.match(p.text.strip()) or p.text.strip().lower().startswith("cliente vip"):
            p._p.getparent().remove(p._p)
            continue
        fix(p)
    dates = {"Vigente desde": ("15/01/2026", "01/09/2025"), "Última revisión": ("10/02/2026", "01/09/2025"),
             "Próxima revisión": ("10/08/2026", "01/03/2026")}
    for table in doc.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells]
            if len(cells) >= 2 and cells[0] in dates and cells[1] == dates[cells[0]][0]:
                row.cells[1].text = dates[cells[0]][1]
    for table in doc.tables:
        for row in list(table.rows):
            cells = [c.text.strip() for c in row.cells]
            if cells and cells[0] == "1.3":
                row._tr.getparent().remove(row._tr)
                continue
            if len(cells) >= 2 and cells[0] == "Versión" and cells[1] == "1.3":
                row.cells[1].text = "1.2"
            if len(cells) >= 2 and cells[0] == "Estado" and cells[1].upper() == "VIGENTE":
                row.cells[1].text = "OBSOLETA"
            if len(cells) >= 2 and cells[0] == "ID documento" and cells[1] == "FS-KB-01":
                row.cells[1].text = "FS-KB-02"
            for cell in row.cells:
                for p in cell.paragraphs:
                    fix(p)
    if counts["45→30"] == 0:
        raise ValueError("FS-KB-01 (.docx) no contiene '45 días'; revisa la fuente.")
    doc.save(out)
    return counts


# ------------------------------------------------------------------ activos nuevos
def build_marketing_ppt(fig: Figures, out: Path) -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    m = fig.ventas["marketing"]

    def slide(title: str, bullets: list[str], foot: str | None = None):
        s = prs.slides.add_slide(prs.slide_layouts[1])
        s.shapes.title.text = title
        body = s.placeholders[1].text_frame
        body.text = bullets[0]
        for b in bullets[1:]:
            body.add_paragraph().text = b
        if foot:
            tb = s.shapes.add_textbox(Inches(0.6), Inches(6.7), Inches(12), Inches(0.5)).text_frame
            tb.text = foot
            tb.paragraphs[0].runs[0].font.size = PPt(10)
        return s

    t = prs.slides.add_slide(prs.slide_layouts[0])
    t.shapes.title.text = "Informe comercial Q4 2025 — FINAL"
    t.placeholders[1].text = "Comité de dirección · FraSoHome · Marketing"
    slide("Resumen ejecutivo Q4 2025", [
        f"Cerramos 2025 con {fig.clientes['marketing_socios_sin_baja']} clientes activos en FraSoHome Rewards",
        f"Ventas netas del trimestre: {eur(m['q4'])} ({pct(m['var_pct'])} frente al Q3: {eur(m['q3'])})",
        "Crecen los clientes omnicanal, que compran en tienda y online",
    ], foot="Clientes activos = socios del programa sin baja. Ventas netas = pedidos captados.")
    slide("Devoluciones", [
        f"Tasa de devolución online del Q4: {str(fig.tasa_devolucion_pedidos_q4).replace('.', ',')} % de los pedidos",
        "Plan de acción: revisar la política de devoluciones con Operaciones",
    ], foot="Tasa de devolución = pedidos con devolución / pedidos.")
    slide("Prioridades 2026", ["Crecer en clientes omnicanal", "Campañas de reactivación para clientes activos"])
    prs.core_properties.title = "Informe comercial Q4 2025 FINAL"
    prs.core_properties.author = "Marketing FraSoHome"
    prs.save(out)


def _header(ws, row: int, values: list[str]) -> None:
    for c, v in enumerate(values, 1):
        cell = ws.cell(row=row, column=c, value=v)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="0E1F3D")


def build_tiendas_xlsx(fig: Figures, out: Path) -> None:
    t = fig.ventas["tiendas"]
    wb = Workbook()
    ws = wb.active
    ws.title = "Resumen"
    ws["A1"] = "Cuadro de mando de tiendas — v3 (la buena)"
    ws["A1"].font = Font(bold=True, size=14)
    _header(ws, 3, ["Indicador", "Q3 2025", "Q4 2025", "Var."])
    ws.append(["Ventas netas (solo tienda física, sin IVA, netas de devoluciones)", t["q3"], t["q4"], t["var_pct"] / 100])
    ws.append(["Clientes (compradores identificados en tienda, 2025)", None, fig.clientes["tiendas_compradores"], None])
    ws.append(["Ticket medio (ventas netas / nº de tickets)", fig.ticket_medio_pos["q3"], fig.ticket_medio_pos["q4"],
               fig.ticket_medio_pos["var_pct"] / 100])
    ws["D4"].number_format = "0.0%"
    ws["D6"].number_format = "0.0%"
    ws["A8"] = "Definiciones: ventas netas sin IVA; ticket medio = ventas netas / nº de tickets (igual que FS-KB-03)."
    for col, w in zip("ABCD", (70, 14, 14, 10)):
        ws.column_dimensions[col].width = w
    ws2 = wb.create_sheet("Mensual por tienda")
    df = fig.mensual_tiendas
    _header(ws2, 1, ["Mes", *[str(c) for c in df.columns]])
    for mes, row in df.iterrows():
        ws2.append([mes, *[float(v) for v in row.values]])
    wb.properties.title = "Cuadro de mando tiendas v3"
    wb.save(out)


def build_finanzas_xlsx(fig: Figures, out: Path) -> None:
    f = fig.ventas["finanzas"]
    wb = Workbook()
    ws = wb.active
    ws.title = "Cierre"
    ws["A1"] = "Cierre mensual diciembre 2025 — Finanzas"
    ws["A1"].font = Font(bold=True, size=14)
    _header(ws, 3, ["Indicador", "Q3 2025", "Q4 2025", "Var."])
    ws.append(["Ventas netas (sin IVA, solo pedidos entregados, sin duplicados)", f["q3"], f["q4"], f["var_pct"] / 100])
    ws["D4"].number_format = "0.0%"
    for col, w in zip("ABCD", (70, 14, 14, 10)):
        ws.column_dimensions[col].width = w
    ws2 = wb.create_sheet("Mensual por canal")
    df = fig.mensual_finanzas
    _header(ws2, 1, ["Mes", *[str(c) for c in df.columns]])
    for mes, row in df.iterrows():
        ws2.append([mes, *[float(v) for v in row.values]])
    wb.properties.title = "Cierre mensual 2025-12 Finanzas"
    wb.save(out)


def build_manual_caja_2023(out: Path) -> None:
    doc = Document()
    doc.add_heading("Manual de caja (copia 2023)", 0)
    doc.add_paragraph("Copia de trabajo de las reglas de reembolso en pagos mixtos. Sin control de versiones.")
    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"
    rows = [("Pago", "Regla"),
            ("Tarjeta + efectivo", "Reembolsar primero a tarjeta hasta su importe; el resto en efectivo."),
            ("Tarjeta + tarjeta regalo", "Reembolsar primero a tarjeta regalo hasta su importe; el resto a tarjeta.")]
    for r, (a, b) in enumerate(rows):
        table.cell(r, 0).text, table.cell(r, 1).text = a, b
    doc.save(out)


MAPA_ROWS = [
    ("Dominio", "Documentos", "Dueño del significado", "Contacto operativo"),
    ("Devoluciones", "FS-KB-01", "Dirección de Operaciones", "Jorge T. · Atención al cliente"),
    ("Tienda y caja", "FS-KB-04", "Operaciones Retail", "Lucía M. · Caja, Gran Vía (MAD01)"),
    ("Pagos y conciliación", "FS-KB-05", "Finanzas", "Paco R. · Conciliación"),
    ("KPI y cifras oficiales", "FS-KB-03, KPI_Cierre_2025_Oficial", "Equipo de Datos + Finanzas (aprueba CFO)", "Paco R. · Finanzas"),
    ("Términos de negocio («Cliente activo»)", "Glosario de Purview", "Dirección Comercial", "Laura P."),
    ("Fidelización", "FS-KB-07", "Marketing + CRM", "Equipo CRM"),
    ("Catálogo", "FS-KB-06", "Producto + E-commerce", "Head of Product"),
]
HUECOS_ROWS = [
    ("Hueco conocido (deuda registrada)", "Estado", "Dueño", "Mientras tanto"),
    ("Reembolso de puntos canjeados en una devolución", "Sin documentar", "Atención al cliente", "Consultar a Jorge T."),
    ("Canal al que se imputa una devolución en tienda de un pedido online", "Sin documentar", "Finanzas", "Consultar a Paco R."),
    ("Registro en el informe Z de un reembolso en tienda de un pedido online", "Sin documentar", "Operaciones Retail", "Consultar a Lucía M."),
    ("Definición de «cliente omnicanal»", "Sin decidir", "Dirección Comercial", "No usar el término en informes"),
    ("Objetivo de tasa de devolución 2026", "Sin decidir", "Dirección Comercial", "No dar cifra"),
]


def _table(doc, rows):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            t.cell(r, c).text = v
            if r == 0:
                for run in t.cell(r, c).paragraphs[0].runs:
                    run.bold = True
    return t


def build_mapa_responsables(out: Path) -> None:
    doc = Document()
    doc.add_heading("Mapa de dominios y responsables - FraSoHome", 0)
    _table(doc, [("ID documento", "FS-KB-00"), ("Versión", "1.0"), ("Estado", "VIGENTE"),
                 ("Área propietaria", "Dirección General"), ("Vigente desde", "01/11/2026")])
    doc.add_paragraph()
    doc.add_heading("1. Quién es dueño de qué", 1)
    doc.add_paragraph("Cada dominio tiene un dueño del significado (negocio) y un contacto operativo. "
                      "Ante una duda que la documentación no resuelve, se escala al contacto del dominio.")
    _table(doc, MAPA_ROWS)
    doc.add_paragraph()
    doc.add_heading("2. Huecos conocidos", 1)
    doc.add_paragraph("Procedimientos y definiciones que todavía no están documentados. "
                      "El asistente no debe inventarlos: debe decir que no están documentados y remitir al contacto.")
    _table(doc, HUECOS_ROWS)
    doc.core_properties.title = "FS-KB-00 Mapa de dominios y responsables"
    doc.save(out)


def build_kpi_cierre_oficial(fig: Figures, out: Path) -> None:
    o = fig.ventas["oficial"]
    doc = Document()
    doc.add_heading("Cifras oficiales de cierre 2025", 0)
    doc.add_paragraph("Fuente de definiciones: FS-KB-03 Diccionario de KPI v1.0. Propietario: Finanzas. Estado: VIGENTE.")
    table = doc.add_table(rows=4, cols=3)
    table.style = "Table Grid"
    rows = [("KPI", "Valor", "Definición aplicada"),
            ("Clientes activos (cierre 2025)", str(fig.clientes["oficial_kb03"]),
             "Clientes del CRM con al menos una compra en los últimos 12 meses (FS-KB-03)"),
            ("Ventas netas Q4 2025", eur(o["q4"]), "Con IVA, netas de devoluciones, sin cancelados ni duplicados (FS-KB-03)"),
            ("Variación ventas netas Q4 vs Q3", pct(o["var_pct"]), f"Q3 2025: {eur(o['q3'])}")]
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            table.cell(r, c).text = v
    doc.add_paragraph("Nota: el descuento por puntos no está disponible en el dataset y no se resta.")
    doc.save(out)


# ------------------------------------------------------------------ orquestación
def run(ctx) -> dict[str, Path]:
    s = ctx.settings
    out_dir = s.docs_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    produced: dict[str, Path] = {}

    for name, prefix in KB_SOURCES.items():
        src = find_source(s.case_kb_dir, prefix)
        materialize(src, out_dir / name)
        produced[name] = out_dir / name
        log.info("KB %s ← %s", name, src.name)

    kb01 = find_source(s.case_kb_dir, "FS-KB-01_")
    kb02 = out_dir / "FS-KB-02_Politica_Devoluciones_v1.2.docx"
    if kb01.suffix == ".md":
        text, counts = derive_kb02_text(kb01.read_text(encoding="utf-8"))
        md_to_docx(text, kb02, title=kb02.stem)
    else:
        counts = derive_kb02_docx(kb01, kb02)
    produced[kb02.name] = kb02
    log.info("FS-KB-02 derivada de FS-KB-01: %s", counts)

    fig = compute(s.case_data_dir)
    builders = {
        "Informe_Comercial_Q4_2025_FINAL.pptx": lambda p: build_marketing_ppt(fig, p),
        "Cuadro_mando_tiendas_v3_bueno.xlsx": lambda p: build_tiendas_xlsx(fig, p),
        "Cierre_mensual_2025-12_Finanzas.xlsx": lambda p: build_finanzas_xlsx(fig, p),
        "Manual_caja_2023.docx": build_manual_caja_2023,
        "KPI_Cierre_2025_Oficial.docx": lambda p: build_kpi_cierre_oficial(fig, p),
        "FS-KB-00_Mapa_Dominios_y_Responsables_v1.0.docx": build_mapa_responsables,
    }
    for name, build in builders.items():
        build(out_dir / name)
        produced[name] = out_dir / name

    print(f"\n✔ {len(produced)} documentos en {out_dir}")
    for n in sorted(produced):
        print("  ·", n)
    return produced


def required_files(scenario: dict) -> set[str]:
    names = set()
    for files in scenario["sites"]["comercial"]["folders"].values():
        names.update(f["file"] if isinstance(f, dict) else f for f in files)
    names.update(f["file"] for f in scenario["sites"]["kb_oficial"]["files"])
    return names
