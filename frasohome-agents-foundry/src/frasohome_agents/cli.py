from __future__ import annotations

import typer
from rich.console import Console

from .assets import assert_assets, csv_files, knowledge_files
from .create_agents import create_all_agents
from .local_data_quality import profile_all
from .orchestrator import run_orchestrator
from .prompts import DATA_QUALITY_PROMPT, KNOWLEDGE_PROMPT, MULTI_AGENT_PROMPT
from .run_agents import run_agent, run_data_quality, run_knowledge
from .settings import Settings

app = typer.Typer(help="FraSoHome Microsoft Foundry agents demo CLI.")
console = Console()


@app.command()
def check_assets() -> None:
    """Validate local case, KB and CSV assets."""
    settings = Settings.load()
    assert_assets(settings)
    console.print("[green]Assets OK[/green]")
    console.print("[bold]Knowledge files[/bold]")
    for path in knowledge_files(settings):
        console.print(f"- {path}")
    console.print("[bold]CSV files[/bold]")
    for path in csv_files(settings):
        console.print(f"- {path}")


@app.command()
def local_profile() -> None:
    """Create a local pandas Data Quality Report without calling Azure."""
    report = profile_all()
    console.print_json(data=report)


@app.command()
def create_agents(dry_run: bool = typer.Option(False, help="Print agent definitions without calling Foundry.")) -> None:
    """Create Foundry prompt agents and attach File Search / Code Interpreter tools."""
    create_all_agents(dry_run=dry_run)


@app.command()
def demo_knowledge() -> None:
    """Run the canonical Knowledge demo prompt."""
    run_knowledge()


@app.command()
def demo_data_quality() -> None:
    """Run the canonical Data Quality demo prompt."""
    run_data_quality()


@app.command()
def demo_orchestrator(
    question: str = typer.Option(MULTI_AGENT_PROMPT, help="Business question for the coded orchestrator."),
) -> None:
    """Run the coded multi-agent orchestrator."""
    run_orchestrator(question)


@app.command()
def ask(
    agent_name: str = typer.Argument(..., help="Existing Foundry agent name."),
    prompt: str = typer.Argument(..., help="Prompt to send."),
) -> None:
    """Ask an arbitrary existing Foundry agent."""
    run_agent(agent_name, prompt)


@app.command()
def prompts() -> None:
    """Print canonical demo prompts."""
    console.print("[bold]Knowledge[/bold]\n" + KNOWLEDGE_PROMPT)
    console.print("[bold]Data Quality[/bold]\n" + DATA_QUALITY_PROMPT)
    console.print("[bold]Multi-agent[/bold]\n" + MULTI_AGENT_PROMPT)


if __name__ == "__main__":
    app()
