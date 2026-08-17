from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

import pandas as pd

from .assets import csv_files
from .settings import Settings, ensure_output_dir


def _suspect_numeric_anomalies(df: pd.DataFrame) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    keywords = ("cantidad", "importe", "precio", "coste", "stock", "descuento")
    for col in df.columns:
        if not any(k in col.lower() for k in keywords):
            continue
        values = pd.to_numeric(df[col], errors="coerce")
        if values.notna().sum() == 0:
            continue
        result[col] = {
            "negativos": int((values < 0).sum()),
            "ceros": int((values == 0).sum()),
            "nulos_o_no_numericos": int(values.isna().sum()),
        }
    return result


def profile_csv(path: Path) -> dict[str, Any]:
    df = pd.read_csv(path)
    nulls = df.isna().sum().sort_values(ascending=False)
    top_nulls = {str(k): int(v) for k, v in nulls[nulls > 0].head(12).items()}
    date_columns = [c for c in df.columns if "fecha" in c.lower() or "date" in c.lower()]
    date_parse = {}
    for col in date_columns:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            parsed = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
        if parsed.notna().sum():
            date_parse[col] = {
                "parseados": int(parsed.notna().sum()),
                "no_parseados": int(parsed.isna().sum()),
                "min": str(parsed.min().date()) if parsed.notna().any() else "",
                "max": str(parsed.max().date()) if parsed.notna().any() else "",
            }
    return {
        "archivo": path.name,
        "filas": int(len(df)),
        "columnas": int(len(df.columns)),
        "duplicados": int(df.duplicated().sum()),
        "nulos_totales": int(df.isna().sum().sum()),
        "campos_con_nulos": top_nulls,
        "fechas": date_parse,
        "anomalias_numericas": _suspect_numeric_anomalies(df),
    }


def profile_all(settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or Settings.load()
    ensure_output_dir(settings)
    profiles = [profile_csv(path) for path in csv_files(settings)]
    report = {
        "resumen": profiles,
        "acciones_priorizadas": [
            "Resolver claves de producto y cliente sin correspondencia antes de integrar la fact table.",
            "Eliminar o consolidar duplicados en ventas POS, stock diario, líneas de pedido, pedidos y CRM.",
            "Estandarizar fechas y revisar registros no parseables o fuera del periodo de operación.",
            "Normalizar importes, cantidades, descuentos y stocks antes de calcular KPIs.",
            "Aplicar reglas de la KB para ventas netas, devoluciones, SKU, pagos y fidelización.",
        ],
    }
    json_path = settings.output_dir / "local_data_quality_report.json"
    md_path = settings.output_dir / "local_data_quality_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(to_markdown(report), encoding="utf-8")
    return report


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Data Quality Report local - FraSoHome",
        "",
        "Este informe se calcula localmente con pandas para validar la demo antes de ejecutar Code Interpreter en Foundry.",
        "",
        "| Archivo | Filas | Columnas | Nulos totales | Duplicados |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in report["resumen"]:
        lines.append(
            f"| {item['archivo']} | {item['filas']} | {item['columnas']} | "
            f"{item['nulos_totales']} | {item['duplicados']} |"
        )
    lines.extend(["", "## Acciones priorizadas", ""])
    for action in report["acciones_priorizadas"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)
