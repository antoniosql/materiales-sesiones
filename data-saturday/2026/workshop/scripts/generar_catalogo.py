"""Genera docs/catalogo.md a partir de contracts/. El catálogo NUNCA se edita a mano.

Uso: python scripts/generar_catalogo.py [--comprobar]
Con --comprobar (CI) falla si el catálogo del repo no está al día.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from datafwk.config import Contrato, cargar_yaml  # noqa: E402

DESTINO = RAIZ / "docs" / "catalogo.md"


def generar(raiz: Path = RAIZ) -> str:
    lineas = [
        "# Catálogo de datos",
        "",
        "> Generado por `scripts/generar_catalogo.py` desde `contracts/`. No editar a mano.",
        "",
    ]
    contratos = [Contrato.desde_dict(cargar_yaml(str(p))) for p in sorted((raiz / "contracts").rglob("*.yml"))]
    for capa in ("silver", "gold"):
        de_capa = [c for c in contratos if c.capa == capa]
        if not de_capa:
            continue
        lineas += [f"## {capa}", ""]
        for c in de_capa:
            lineas += [
                f"### `{c.tabla}`",
                "",
                c.descripcion,
                "",
                f"- **Dominio:** {c.dominio} · **Propietario:** {c.propietario}",
                f"- **Clave:** {', '.join(c.clave)} · **Si incumple el contrato:** {c.politica_rechazo}",
                "",
                "| Columna | Tipo | Nulos | Valores | Descripción |",
                "|---|---|---|---|---|",
            ]
            for col in c.columnas:
                valores = ", ".join(map(str, col.valores)) if col.valores else ""
                nulos = "sí" if col.nulo else "no"
                lineas.append(f"| `{col.nombre}` | {col.tipo} | {nulos} | {valores} | {col.descripcion} |")
            if c.reglas:
                lineas += ["", "**Reglas:**", ""]
                for r in c.reglas:
                    detalle = f" — {r.descripcion}" if r.descripcion else ""
                    lineas.append(f"- `{r.nombre}`: `{r.expresion}`{detalle}")
            lineas.append("")
    return "\n".join(lineas)


if __name__ == "__main__":
    contenido = generar()
    if "--comprobar" in sys.argv:
        actual = DESTINO.read_text(encoding="utf-8") if DESTINO.exists() else ""
        if actual != contenido:
            print("docs/catalogo.md no está al día: ejecuta python scripts/generar_catalogo.py")
            sys.exit(1)
        print("Catálogo al día")
    else:
        DESTINO.write_text(contenido, encoding="utf-8")
        print(f"Catálogo generado en {DESTINO.relative_to(RAIZ)}")
