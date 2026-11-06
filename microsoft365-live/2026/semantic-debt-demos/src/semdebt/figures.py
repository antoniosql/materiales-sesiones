"""Cifras de la sesión calculadas con los datos del caso FraSoHome.

Reglas (las mismas que el escenario y las slides):
- Año de referencia 2025. Q3 = jul–sep, Q4 = oct–dic. Fechas fuera de rango quedan fuera por el filtro de periodo.
- Duplicados: (doc_id_std, line_id_std, tipo_movimiento).
- El descuento por puntos no está en el dataset: la cifra oficial no lo resta.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

ENTREGADO = ["Entregado", "Devuelto Parcial", "Devuelto Total", "Aceptada", "Reembolsada"]
Q3 = ("2025-07-01", "2025-10-01")
Q4 = ("2025-10-01", "2026-01-01")
YEAR = ("2025-01-01", "2026-01-01")


@dataclass
class Figures:
    clientes: dict[str, int]
    ventas: dict[str, dict[str, float]]
    ids_fuera_crm: int
    tasa_devolucion_pedidos_q4: float
    mensual_tiendas: pd.DataFrame
    mensual_finanzas: pd.DataFrame
    ticket_medio_pos: dict


def load_case(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not data_dir or not data_dir.exists():
        raise FileNotFoundError(f"CASE_DATA_DIR no existe: {data_dir}")
    fact = pd.read_csv(data_dir / "fact_transacciones.csv")
    crm = pd.read_csv(data_dir / "crm.csv")
    fact["fecha"] = pd.to_datetime(fact["fecha_movimiento"], errors="coerce")
    fact["iva"] = fact["iva_pct"].fillna(21)
    fact["sin_iva"] = fact["importe_signed_num"] / (1 + fact["iva"] / 100)
    return fact, crm


def _period(df: pd.DataFrame, rng: tuple[str, str]) -> pd.DataFrame:
    return df[(df["fecha"] >= rng[0]) & (df["fecha"] < rng[1])]


def _var(q3: float, q4: float) -> float:
    return round((q4 / q3 - 1) * 100, 1) if q3 else float("nan")


def compute(data_dir: Path) -> Figures:
    fact, crm = load_case(data_dir)
    dedup = fact.drop_duplicates(["doc_id_std", "line_id_std", "tipo_movimiento"])
    crm_ids = set(crm["customer_id"])
    year = _period(fact, YEAR)
    ventas_y = year[year["tipo_movimiento"] == "VENTA"]

    oficial_any = ventas_y["customer_id_std"].dropna().nunique()
    oficial_crm = ventas_y[ventas_y["customer_id_std"].isin(crm_ids)]["customer_id_std"].nunique()
    clientes = {
        "crm_estado_activo": int((crm["estado_cliente"] == "Activo").sum()),
        "marketing_socios_sin_baja": int((crm["tier_fidelizacion"].notna() & crm["fecha_baja"].isna()).sum()),
        "ecommerce_compradores": int(ventas_y[(ventas_y["canal_origen"] == "ONLINE")
                                              & (ventas_y["estado_pedido"] != "Cancelado")]["customer_id_std"].dropna().nunique()),
        "oficial_kb03": int(oficial_crm),
        "tiendas_compradores": int(ventas_y[ventas_y["canal_origen"] == "POS"]["customer_id_std"].dropna().nunique()),
        "kb03_literal_cualquier_id": int(oficial_any),
    }

    rules = {
        "marketing": (fact, lambda d: d[d["tipo_movimiento"] == "VENTA"]["importe_abs_num"].sum()),
        "oficial": (dedup, lambda d: d[d["estado_pedido"] != "Cancelado"]["importe_signed_num"].sum()),
        "tiendas": (fact, lambda d: d[d["canal_origen"] == "POS"]["sin_iva"].sum()),
        "finanzas": (dedup, lambda d: d[d["estado_pedido"].isna() | d["estado_pedido"].isin(ENTREGADO)]["sin_iva"].sum()),
    }
    ventas = {}
    for name, (src, fn) in rules.items():
        q3, q4 = float(fn(_period(src, Q3))), float(fn(_period(src, Q4)))
        ventas[name] = {"q3": round(q3), "q4": round(q4), "var_pct": _var(q3, q4)}

    # Tasa de devolución "de marketing": pedidos online devueltos / pedidos online (Q4)
    q4_online = _period(fact, Q4)
    q4_online = q4_online[(q4_online["canal_origen"] == "ONLINE") & (q4_online["tipo_movimiento"] == "VENTA")]
    pedidos = q4_online.groupby("doc_id_std")["estado_pedido"].first()
    tasa = float(pedidos.isin(["Devuelto Parcial", "Devuelto Total"]).mean() * 100) if len(pedidos) else 0.0

    ticket = {}
    for name, rng in (("q3", Q3), ("q4", Q4)):
        pos = _period(fact, rng)
        pos = pos[pos["canal_origen"] == "POS"]
        n = pos[pos["tipo_movimiento"] == "VENTA"]["doc_id_std"].nunique()
        ticket[name] = round(float(pos["sin_iva"].sum()) / n, 2) if n else 0.0
    ticket["var_pct"] = _var(ticket["q3"], ticket["q4"])

    s2 = _period(fact, ("2025-07-01", "2026-01-01")).copy()
    s2["mes"] = s2["fecha"].dt.to_period("M").astype(str)
    tiendas = (s2[s2["canal_origen"] == "POS"].groupby(["mes", "store_id_std"])["sin_iva"].sum()
               .unstack(fill_value=0).round(2))
    d2 = _period(dedup, ("2025-07-01", "2026-01-01")).copy()
    d2["mes"] = d2["fecha"].dt.to_period("M").astype(str)
    d2 = d2[d2["estado_pedido"].isna() | d2["estado_pedido"].isin(ENTREGADO)]
    finanzas = d2.groupby(["mes", "canal_origen"])["sin_iva"].sum().unstack(fill_value=0).round(2)

    return Figures(clientes=clientes, ventas=ventas, ids_fuera_crm=int(oficial_any - oficial_crm),
                   tasa_devolucion_pedidos_q4=round(tasa, 1), mensual_tiendas=tiendas, mensual_finanzas=finanzas,
                   ticket_medio_pos=ticket)


def compare(fig: Figures, expected: dict) -> list[str]:
    """Devuelve las discrepancias con las cifras de las slides (lista vacía = todo cuadra)."""
    issues = []
    for k, v in expected["clientes_activos"].items():
        if fig.clientes.get(k) != v:
            issues.append(f"clientes_activos.{k}: slides={v} datos={fig.clientes.get(k)}")
    for k, exp in expected["ventas_netas"].items():
        got = fig.ventas[k]
        for f in ("q3", "q4"):
            if abs(got[f] - exp[f]) > 1:
                issues.append(f"ventas_netas.{k}.{f}: slides={exp[f]} datos={got[f]}")
        if abs(got["var_pct"] - exp["var_pct"]) > 0.05:
            issues.append(f"ventas_netas.{k}.var_pct: slides={exp['var_pct']} datos={got['var_pct']}")
    return issues


def eur(x: float) -> str:
    return f"{x:,.0f} €".replace(",", ".")


def pct(x: float) -> str:
    sign = "+" if x > 0 else ("−" if x < 0 else "")
    return f"{sign}{abs(x):.1f} %".replace(".", ",")


def run(ctx) -> Figures:
    fig = compute(ctx.settings.case_data_dir)
    print("\nClientes activos 2025 según definición:")
    for k, v in fig.clientes.items():
        print(f"  {k:<28} {v:>5}")
    print(f"  IDs de ventas fuera del CRM: {fig.ids_fuera_crm}")
    print("\nVentas netas Q4 vs Q3 2025:")
    for k, v in fig.ventas.items():
        print(f"  {k:<10} Q3 {eur(v['q3']):>12}  Q4 {eur(v['q4']):>12}  {pct(v['var_pct']):>8}")
    issues = compare(fig, ctx.scenario["expected_figures"])
    if issues:
        print("\n⚠ Las cifras no coinciden con las slides (cambia las slides, no el código):")
        for i in issues:
            print("   -", i)
    else:
        print("\n✔ Las cifras coinciden con las slides.")
    return fig
