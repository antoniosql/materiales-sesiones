from __future__ import annotations

import json
import re
from typing import Any

from rich.console import Console

from .contracts import OrchestratorResult, SpecialistResult
from .foundry import FoundryRuntime, response_text
from .prompts import MULTI_AGENT_PROMPT
from .settings import Settings, ensure_output_dir

console = Console()


def _json_from_text(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def _specialist_payload(agent: str, text: str) -> SpecialistResult:
    try:
        return SpecialistResult.model_validate(_json_from_text(text))
    except Exception:
        return SpecialistResult(
            agent=agent,
            hallazgos=[text],
            evidencias=[],
            riesgos=["La salida del especialista no era JSON válido."],
            confianza=0.5,
        )


def run_orchestrator(question: str = MULTI_AGENT_PROMPT) -> OrchestratorResult:
    settings = Settings.load()
    ensure_output_dir(settings)
    runtime = FoundryRuntime(settings)

    knowledge_prompt = (
        f"Pregunta: {question}\n\n"
        "Aporta contexto normativo desde la KB. Prioriza política de devoluciones, KPIs, tienda/pagos, "
        "conciliación ecommerce, taxonomía SKU, fidelización y FAQ según la pregunta. Devuelve hallazgos, evidencias, riesgos y confianza."
    )
    knowledge_text = response_text(runtime.run_agent(settings.knowledge_agent, knowledge_prompt))

    data_quality_prompt = (
        f"Pregunta: {question}\n\n"
        "Comprueba si los datos disponibles permiten responder. Calcula o resume evidencias relevantes sobre ventas, "
        "devoluciones, categoría iluminación, canal online, nulos, duplicados y fiabilidad. Devuelve JSON con hallazgos, evidencias, riesgos y confianza."
    )
    data_quality_text = response_text(runtime.run_agent(settings.data_quality_agent, data_quality_prompt))
    data_quality = _specialist_payload("data_quality", data_quality_text)

    returns_prompt = (
        f"Pregunta: {question}\n"
        f"Contexto normativo de Knowledge:\n{knowledge_text}\n\n"
        f"Evidencia de calidad de datos:\n{data_quality_text}\n\n"
        "Analiza la hipótesis de devoluciones online en iluminación. No inventes cifras. Usa la política de devoluciones y evidencias recibidas."
    )
    returns_text = response_text(runtime.run_agent(settings.returns_agent, returns_prompt))
    returns = _specialist_payload("returns", returns_text)

    operations_prompt = (
        f"Pregunta: {question}\n"
        f"Contexto normativo de Knowledge:\n{knowledge_text}\n\n"
        f"Evidencia de calidad de datos:\n{data_quality_text}\n\n"
        f"Evidencia de devoluciones:\n{returns_text}\n\n"
        "Evalúa causas operativas posibles: stock irregular, logística, disponibilidad, tienda, pedidos, canal, pagos, conciliación, taxonomía SKU y experiencia de devolución."
    )
    operations_text = response_text(runtime.run_agent(settings.operations_agent, operations_prompt))
    operations = _specialist_payload("operations", operations_text)

    confidence = min(data_quality.confianza, returns.confianza, operations.confianza)
    synthesis = {
        "question": question,
        "knowledge": knowledge_text,
        "data_quality": data_quality.model_dump(),
        "returns": returns.model_dump(),
        "operations": operations.model_dump(),
        "confidence": confidence,
        "requires_human_validation": confidence < settings.confidence_threshold,
        "required_output": "JSON con causa probable, evidencias, riesgos, acción de 7 días y métrica de seguimiento.",
    }
    storyteller_text = response_text(runtime.run_agent(settings.storyteller_agent, json.dumps(synthesis, ensure_ascii=False)))
    try:
        result = OrchestratorResult.model_validate(_json_from_text(storyteller_text))
    except Exception:
        result = OrchestratorResult(
            pregunta=question,
            causa_probable="No se pudo validar la salida JSON del agente Storyteller.",
            evidencias=[],
            riesgos=["Revisar salida del Storyteller.", storyteller_text],
            accion_7_dias="Repetir ejecución con contrato JSON reforzado y validar manualmente.",
            metrica_seguimiento="Porcentaje de respuestas con JSON válido.",
            requiere_validacion_humana=True,
        )

    out = settings.output_dir / "orchestrator_response.json"
    out.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    console.print_json(result.model_dump_json(indent=2))
    console.print(f"[green]Wrote[/green] {out}")
    return result
