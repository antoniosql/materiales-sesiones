from __future__ import annotations

from pathlib import Path
from typing import Any

from azure.identity import DefaultAzureCredential

from .settings import Settings


class FoundryRuntime:
    def __init__(self, settings: Settings):
        settings.require_foundry()
        from azure.ai.projects import AIProjectClient

        self.settings = settings
        self.project = AIProjectClient(
            endpoint=settings.project_endpoint,
            credential=DefaultAzureCredential(),
        )
        self.openai = self.project.get_openai_client()

    def create_prompt_agent(self, name: str, instructions: str, tools: list[Any] | None = None) -> Any:
        from azure.ai.projects.models import PromptAgentDefinition

        return self.project.agents.create_version(
            agent_name=name,
            definition=PromptAgentDefinition(
                model=self.settings.model_deployment,
                instructions=instructions,
                tools=tools or [],
            ),
        )

    def upload_file(self, path: Path, purpose: str = "assistants") -> Any:
        with path.open("rb") as file:
            return self.openai.files.create(file=file, purpose=purpose)

    def create_vector_store(self, name: str, file_ids: list[str]) -> Any:
        return self.openai.vector_stores.create(name=name, file_ids=file_ids)

    def run_agent(self, agent_name: str, prompt: str, *, store: bool = True) -> Any:
        return self.openai.responses.create(
            extra_body={
                "agent_reference": {
                    "name": agent_name,
                    "type": "agent_reference",
                }
            },
            input=prompt,
            store=store,
        )


def response_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if text:
        return text
    output = getattr(response, "output", None) or []
    parts: list[str] = []
    for item in output:
        if getattr(item, "type", None) == "message":
            for content in getattr(item, "content", []) or []:
                value = getattr(content, "text", None)
                if value:
                    parts.append(value)
    return "\n".join(parts).strip()


def print_tool_calls(response: Any) -> list[str]:
    calls: list[str] = []
    for item in getattr(response, "output", []) or []:
        item_type = getattr(item, "type", "")
        if item_type.endswith("_call"):
            status = getattr(item, "status", "")
            calls.append(f"{item_type}: {status}")
    return calls
