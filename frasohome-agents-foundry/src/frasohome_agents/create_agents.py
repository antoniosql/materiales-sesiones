from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

from .assets import assert_assets, csv_files, knowledge_files
from .foundry import FoundryRuntime
from .prompts import (
    DATA_QUALITY_INSTRUCTIONS,
    KNOWLEDGE_INSTRUCTIONS,
    OPERATIONS_INSTRUCTIONS,
    RETURNS_INSTRUCTIONS,
    STORYTELLER_INSTRUCTIONS,
)
from .settings import Settings, ensure_output_dir

console = Console()


def _id_from_upload(uploaded: object) -> str:
    value = getattr(uploaded, "id", None)
    if not value:
        raise RuntimeError(f"Upload response does not expose an id: {uploaded!r}")
    return str(value)


def prepare_knowledge_vector_store(runtime: FoundryRuntime, settings: Settings) -> str:
    if settings.vector_store_id:
        console.print(f"[green]Using existing vector store[/green] {settings.vector_store_id}")
        return settings.vector_store_id

    uploads = []
    for path in knowledge_files(settings):
        uploaded = runtime.upload_file(path)
        uploads.append(_id_from_upload(uploaded))
        console.print(f"Uploaded KB file: {path.name}")

    vector_store = runtime.create_vector_store("frasohome-knowledge-kb", uploads)
    vector_store_id = _id_from_upload(vector_store)
    console.print(f"[green]Created vector store[/green] {vector_store_id}")
    return vector_store_id


def create_all_agents(*, dry_run: bool = False) -> dict[str, object]:
    settings = Settings.load()
    assert_assets(settings)
    ensure_output_dir(settings)

    if dry_run:
        definitions = {
            settings.knowledge_agent: {"tool": "FileSearchTool", "files": [str(p) for p in knowledge_files(settings)]},
            settings.data_quality_agent: {"tool": "CodeInterpreterTool", "files": [str(p) for p in csv_files(settings)]},
            settings.returns_agent: {"tool": "FileSearchTool optional", "instructions": RETURNS_INSTRUCTIONS},
            settings.operations_agent: {"tool": "FileSearchTool optional", "instructions": OPERATIONS_INSTRUCTIONS},
            settings.storyteller_agent: {"tool": "none", "instructions": STORYTELLER_INSTRUCTIONS},
        }
        console.print_json(json.dumps(definitions, ensure_ascii=False, indent=2))
        return definitions

    runtime = FoundryRuntime(settings)

    from azure.ai.projects.models import CodeInterpreterTool, FileSearchTool

    vector_store_id = prepare_knowledge_vector_store(runtime, settings)
    knowledge_tool = FileSearchTool(vector_store_ids=[vector_store_id])
    knowledge = runtime.create_prompt_agent(settings.knowledge_agent, KNOWLEDGE_INSTRUCTIONS, [knowledge_tool])

    csv_file_ids = []
    for path in csv_files(settings):
        uploaded = runtime.upload_file(path)
        csv_file_ids.append(_id_from_upload(uploaded))
        console.print(f"Uploaded CSV: {path.name}")

    data_quality_tool = CodeInterpreterTool(container={"file_ids": csv_file_ids, "type": "auto"})
    data_quality = runtime.create_prompt_agent(settings.data_quality_agent, DATA_QUALITY_INSTRUCTIONS, [data_quality_tool])

    # These specialists can operate from orchestrated context. Attach File Search too so they can query KB directly.
    returns = runtime.create_prompt_agent(settings.returns_agent, RETURNS_INSTRUCTIONS, [knowledge_tool])
    operations = runtime.create_prompt_agent(settings.operations_agent, OPERATIONS_INSTRUCTIONS, [knowledge_tool])
    storyteller = runtime.create_prompt_agent(settings.storyteller_agent, STORYTELLER_INSTRUCTIONS, [])

    result = {
        settings.knowledge_agent: knowledge,
        settings.data_quality_agent: data_quality,
        settings.returns_agent: returns,
        settings.operations_agent: operations,
        settings.storyteller_agent: storyteller,
        "vector_store_id": vector_store_id,
    }

    metadata = {
        "agents": list(result.keys()),
        "vector_store_id": vector_store_id,
        "csv_files": [p.name for p in csv_files(settings)],
        "knowledge_files": [p.name for p in knowledge_files(settings)],
    }
    out = settings.output_dir / "foundry_created_agents.json"
    out.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    console.print(f"[green]Wrote[/green] {out}")
    return result
