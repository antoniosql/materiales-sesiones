"""Duplica las slides de plantilla en el orden del guion y deja sldIdLst limpio."""
import re, subprocess, sys, json
from pathlib import Path

SK = "/root/.claude/skills/synced/bdd023d3-0ed7-4a42-96d3-cf1ac9d8b589_fd7a8e53-585a-47c9-8658-60e338c6efde/pptx/scripts/add_slide.py"
UNP = Path("unpacked")

# (clave, slide origen, descripcion)
PLAN = [
    ("portada",        1,  "Portada"),
    ("sponsors",       5,  "Sponsors (intacta)"),
    ("gancho",         8,  "Gancho"),
    ("cifra",         31,  "Dato de contraste"),
    ("contrato",      13,  "Contrato de la sesion"),
    ("frasohome",     16,  "FraSoHome en una frase"),
    ("app_vs_agente", 12,  "App vs agente"),
    ("riesgos",       27,  "Cuatro riesgos de runtime"),
    ("sintomas",       7,  "Cinco sintomas"),
    ("visibilidad",   28,  "La visibilidad va antes que el control"),
    ("tres_capas",    13,  "LAS TRES CAPAS"),
    ("mensajes",      14,  "Tres mensajes + licenciamiento"),
    ("inventario",    12,  "Entra Agent ID / Registry / PPAC"),
    ("sep_demo1",      9,  "SEPARADOR DEMO 1"),
    ("planb_demo1",   25,  "PLAN B demo 1 (oculta)"),
    ("comite",        12,  "Comite vs carril"),
    ("carriles",      34,  "TABLA DE CARRILES"),
    ("reglas",        20,  "Tres reglas duras"),
    ("datos",         12,  "Control de datos"),
    ("sep_demo2",     10,  "SEPARADOR DEMO 2"),
    ("planb_demo2",   25,  "PLAN B demo 2 (oculta)"),
    ("ciclo_vida",    13,  "ALM / componentes / evaluaciones"),
    ("sep_demo3",      9,  "SEPARADOR DEMO 3"),
    ("planb_demo3",   25,  "PLAN B demo 3 (oculta)"),
    ("sdk",           12,  "Agent 365 SDK: que es / que no es"),
    ("blueprint",     16,  "Blueprint de identidad"),
    ("sep_demo4",     10,  "SEPARADOR DEMO 4"),
    ("planb_demo4",   25,  "PLAN B demo 4 (oculta)"),
    ("cadencia",      27,  "Cadencia operativa"),
    ("cierre",        28,  "Cierre: volved y contad"),
    ("recursos",      12,  "Recursos"),
    ("qa",            36,  "Q&A"),
    ("gracias",       37,  "Gracias + QR"),
    ("contacto",      38,  "Contacto Bizz Summit"),
]

created = {}
for key, src, desc in PLAN:
    out = subprocess.run(
        [sys.executable, SK, str(UNP), f"slide{src}.xml"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        print("ERROR", key, out.stderr[-500:]); sys.exit(1)
    m = re.search(r"ppt/slides/(slide\d+\.xml)", out.stdout)
    assert m, out.stdout
    created[key] = m.group(1)
    print(f"{key:16s} slide{src}.xml -> {m.group(1)}  ({desc})")

Path("mapa.json").write_text(json.dumps(
    {"orden": [k for k, _, _ in PLAN], "creado": created,
     "desc": {k: d for k, _, d in PLAN}}, indent=2, ensure_ascii=False))
