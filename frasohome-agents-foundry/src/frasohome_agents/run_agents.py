from __future__ import annotations

from pathlib import Path

from rich.console import Console

from .foundry import FoundryRuntime, print_tool_calls, response_text
from .prompts import DATA_QUALITY_PROMPT, KNOWLEDGE_PROMPT
from .settings import Settings, ensure_output_dir

console = Console()


def run_agent(agent_name: str, prompt: str, output_name: str | None = None) -> str:
    settings = Settings.load()
    ensure_output_dir(settings)
    runtime = FoundryRuntime(settings)
    response = runtime.run_agent(agent_name, prompt)
    text = response_text(response)
    calls = print_tool_calls(response)
    if calls:
        console.print("[bold]Tool calls[/bold]")
        for call in calls:
            console.print(f"- {call}")
    console.print(text)
    if output_name:
        path = settings.output_dir / output_name
        path.write_text(text, encoding="utf-8")
        console.print(f"[green]Wrote[/green] {path}")
    return text


def run_knowledge() -> str:
    settings = Settings.load()
    return run_agent(settings.knowledge_agent, KNOWLEDGE_PROMPT, "knowledge_response.md")


def run_data_quality() -> str:
    settings = Settings.load()
    return run_agent(settings.data_quality_agent, DATA_QUALITY_PROMPT, "data_quality_report.md")
