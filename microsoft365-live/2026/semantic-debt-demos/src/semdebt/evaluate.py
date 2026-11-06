"""Paso 3 del diagnóstico: lo que Copilot ve de verdad. Mide la TRC con el test set.

Objetivos:
  retrieval → Retrieval API (v1.0): qué documentos recupera Copilot y en qué orden (sin LLM).
  chat      → Copilot Chat como Laura (estado ANTES, demos 0–3).
  agent     → Agente de Copilot Studio como Laura (estado DESPUÉS, demo 4).

TRC = preguntas con respuesta correcta y que citan la fuente canónica ÷ total.
Las abstenciones (tácitas, inexistentes) se informan aparte: son honestas, pero no suman.
"""
from __future__ import annotations

import asyncio
import csv
import logging
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

from . import auth
from .config import ROOT
from .http import GRAPH, GRAPH_BETA, Api

log = logging.getLogger(__name__)
TESTSET = ROOT / "testset" / "testset_frasohome.csv"

ABSTENTION = ["no hay un procedimiento", "no esta documentado", "no he encontrado", "no encuentro",
              "no dispongo", "no tengo informacion", "no se ha definido", "no esta definido", "no esta decidido",
              "no puedo confirmar", "contacta", "consulta con", "no existe documentacion", "no hay informacion"]


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    text = text.lower().replace(" ", " ")
    return re.sub(r"\s+", " ", text)


def keywords_ok(answer: str, spec: str) -> bool:
    """spec: grupos separados por ';' (todos obligatorios), alternativas por '|'."""
    if not spec:
        return False
    a = norm(answer)
    return all(any(norm(alt) in a for alt in group.split("|")) for group in spec.split(";"))


def cites(sources: list[str], canonical_spec: str) -> bool:
    if not canonical_spec:
        return False
    blob = norm(" ".join(unquote(s) for s in sources))
    return any(norm(c) in blob for c in canonical_spec.split("|"))


def abstains(answer: str) -> bool:
    a = norm(answer)
    return any(m in a for m in ABSTENTION)


@dataclass
class Row:
    id: str
    estado: str
    pregunta: str
    respuesta: str = ""
    fuentes: list[str] = field(default_factory=list)
    correcta: bool = False
    cita_canonica: bool = False
    abstencion: bool = False
    cuenta_trc: bool = False
    error: str = ""


def load_testset(path: Path = TESTSET) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def score(case: dict, answer: str, sources: list[str]) -> Row:
    r = Row(case["id"], case["estado"], case["pregunta"], answer, sources)
    r.correcta = keywords_ok(answer, case["palabras_clave"])
    r.cita_canonica = cites(sources, case["fuente_canonica"])
    r.abstencion = abstains(answer)
    r.cuenta_trc = bool(case["fuente_canonica"]) and r.correcta and r.cita_canonica
    return r


# ------------------------------------------------------------------ objetivos
def ask_chat(ctx, token: str, question: str) -> tuple[str, list[str]]:
    s = ctx.settings
    if s.copilot_chat_endpoint == "workiq":
        api = Api(lambda: token, "https://workiq.svc.cloud.microsoft/rest", s.dry_run)
    else:
        api = Api(lambda: token, GRAPH_BETA + "/copilot", s.dry_run)
    conv = api.post("conversations", {})
    resp = api.post(f"conversations/{conv['id']}/chat", {
        "message": {"text": question}, "locationHint": {"timeZone": s.timezone}})
    msgs = resp.get("messages") or []
    last = msgs[-1] if msgs else {}
    sources = []
    for a in last.get("attributions") or []:
        sources += [a.get("seeMoreWebUrl") or "", a.get("providerDisplayName") or ""]
    return last.get("text", ""), [x for x in sources if x]


def ask_retrieval(ctx, token: str, question: str, site_url: str | None) -> tuple[str, list[str]]:
    api = Api(lambda: token, GRAPH, ctx.settings.dry_run)
    body = {"queryString": question[:1500], "dataSource": "sharePoint",
            "resourceMetadata": ["title"], "maximumNumberOfResults": 5}
    if site_url:
        body["filterExpression"] = f'Path:"{site_url}"'
    resp = api.post("copilot/retrieval", body)
    hits = resp.get("retrievalHits") or []
    urls = [h.get("webUrl", "") for h in hits]
    text = " ".join(e.get("text", "") for h in hits[:3] for e in (h.get("extracts") or []))
    return text, urls


async def _agent_session(ctx, token: str, questions: list[str]) -> list[tuple[str, list[str]]]:
    from microsoft_agents.copilotstudio.client import ConnectionSettings, CopilotClient  # dependencia opcional

    settings = ConnectionSettings(environment_id=ctx.settings.pp_environment_id,
                                  agent_identifier=ctx.settings.agent_schema_name,
                                  cloud=None, copilot_agent_type=None, custom_power_platform_cloud=None)
    client = CopilotClient(settings, token)
    out = []
    for q in questions:   # una conversación por pregunta: sin contexto arrastrado
        conv_id = None
        async for act in client.start_conversation(True):
            conv_id = getattr(getattr(act, "conversation", None), "id", None) or conv_id
        texts, sources = [], []
        async for reply in client.ask_question(q, conv_id):
            if getattr(reply, "type", "") == "message":
                texts.append(reply.text or "")
                raw = reply.model_dump() if hasattr(reply, "model_dump") else {}
                sources += re.findall(r"https?://[^\s\"')\]]+", str(raw))
                sources += [str(e) for e in (raw.get("entities") or [])]
        out.append(("\n".join(texts), sources))
    return out


# ------------------------------------------------------------------ orquestación
def run(ctx, target: str, only: list[str] | None = None, allow_admin: bool = False, sitio: str = "comercial") -> Path:
    s = ctx.settings
    laura = ctx.upn("laura")
    cases = [c for c in load_testset() if not only or c["id"] in only]
    rows: list[Row] = []

    if target == "chat":
        if ctx.state.get("site", "kb_oficial"):
            print("⚠ Laura tiene acceso a FraSoHome-KB-Oficial: Copilot Chat mezcla el ANTES y el DESPUÉS. "
                  "Para medir el antes usa `--target retrieval --sitio comercial`.")
        scopes = [s.workiq_scope] if s.copilot_chat_endpoint == "workiq" and s.workiq_scope else auth.COPILOT_CHAT_SCOPES
        token = auth.user_token(s, scopes, laura, allow_admin)
        for c in cases:
            try:
                rows.append(score(c, *ask_chat(ctx, token, c["pregunta"])))
            except Exception as e:  # noqa: BLE001 — seguimos con el resto del test set
                rows.append(Row(c["id"], c["estado"], c["pregunta"], error=str(e)[:300]))
    elif target == "retrieval":
        token = auth.user_token(s, auth.RETRIEVAL_SCOPES, laura, allow_admin)
        site = ctx.state.get("site", sitio)
        for c in cases:
            try:
                rows.append(score(c, *ask_retrieval(ctx, token, c["pregunta"], site["webUrl"] if site else None)))
            except Exception as e:  # noqa: BLE001
                rows.append(Row(c["id"], c["estado"], c["pregunta"], error=str(e)[:300]))
    elif target == "agent":
        if not s.pp_environment_id and not s.dry_run:
            raise RuntimeError("Falta PP_ENVIRONMENT_ID en .env")
        token = auth.user_token(s, auth.POWER_PLATFORM_SCOPES, laura, allow_admin)
        if s.dry_run:
            answers = [("", [])] * len(cases)
        else:
            answers = asyncio.run(_agent_session(ctx, token, [c["pregunta"] for c in cases]))
        rows = [score(c, a, src) for c, (a, src) in zip(cases, answers)]
    else:
        raise ValueError("target debe ser chat, retrieval o agent")

    return report(ctx, f"{target}-{sitio}" if target == "retrieval" else target, rows)


def report(ctx, target: str, rows: list[Row]) -> Path:
    out_dir = ctx.settings.reports_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    csv_path = out_dir / f"trc-{target}-{stamp}.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()) if rows else ["id"])
        w.writeheader()
        for r in rows:
            d = asdict(r)
            d["fuentes"] = " | ".join(r.fuentes)
            w.writerow(d)
    trc = sum(r.cuenta_trc for r in rows)
    abst = [r.id for r in rows if r.estado in ("Tacita", "Inexistente") and r.abstencion]
    errors = [r.id for r in rows if r.error]
    md = out_dir / f"trc-{target}-{stamp}.md"
    lines = [f"# TRC · {target} · {stamp}", "",
             f"**TRC = {trc} / {len(rows)} = {trc / len(rows) * 100:.0f} %**" if rows else "Sin filas", "",
             f"Abstenciones correctas (tácitas/inexistentes): {len(abst)} {abst}",
             f"Errores: {errors}" if errors else "", "",
             "| id | estado | correcta | cita canónica | cuenta | fuentes |", "|---|---|---|---|---|---|"]
    for r in rows:
        src = ", ".join(Path(unquote(x)).name for x in r.fuentes[:3] if x)
        lines.append(f"| {r.id} | {r.estado} | {'✔' if r.correcta else '✘'} | {'✔' if r.cita_canonica else '✘'} "
                     f"| {'✔' if r.cuenta_trc else ''} | {src} |")
    md.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nTRC {target}: {trc}/{len(rows)}" + (f" = {trc / len(rows) * 100:.0f} %" if rows else ""))
    print(f"  Informe: {md}")
    if target in ("chat", "retrieval-comercial"):
        print("  Slides: 7/20 (35 %) antes. Si sale otra cifra, cambia las slides 29 y 38.")
    if target == "agent":
        print("  Slides: 15/20 (75 %) después.")
    return md
