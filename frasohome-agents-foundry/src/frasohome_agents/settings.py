from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    project_endpoint: str
    model_deployment: str
    vector_store_id: str | None
    case_dir: Path
    output_dir: Path
    confidence_threshold: float
    knowledge_agent: str
    data_quality_agent: str
    returns_agent: str
    operations_agent: str
    storyteller_agent: str

    @classmethod
    def load(cls) -> "Settings":
        load_dotenv()
        case_dir = Path(os.getenv("FRASOHOME_CASE_DIR", "case")).resolve()
        output_dir = Path(os.getenv("FRASOHOME_OUTPUT_DIR", "outputs")).resolve()
        return cls(
            project_endpoint=os.getenv("PROJECT_ENDPOINT", "").strip(),
            model_deployment=os.getenv("MODEL_DEPLOYMENT", "gpt-5-mini").strip(),
            vector_store_id=os.getenv("FRASOHOME_VECTOR_STORE_ID", "").strip() or None,
            case_dir=case_dir,
            output_dir=output_dir,
            confidence_threshold=float(os.getenv("FRASOHOME_CONFIDENCE_THRESHOLD", "0.75")),
            knowledge_agent=os.getenv("FRASOHOME_KNOWLEDGE_AGENT", "frasohome-knowledge"),
            data_quality_agent=os.getenv("FRASOHOME_DATA_QUALITY_AGENT", "frasohome-data-quality"),
            returns_agent=os.getenv("FRASOHOME_RETURNS_AGENT", "frasohome-returns"),
            operations_agent=os.getenv("FRASOHOME_OPERATIONS_AGENT", "frasohome-operations"),
            storyteller_agent=os.getenv("FRASOHOME_STORYTELLER_AGENT", "frasohome-storyteller"),
        )

    def require_foundry(self) -> None:
        if not self.project_endpoint:
            raise RuntimeError("PROJECT_ENDPOINT is required for live Foundry calls.")
        if not self.model_deployment:
            raise RuntimeError("MODEL_DEPLOYMENT is required for live Foundry calls.")


def ensure_output_dir(settings: Settings) -> Path:
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    return settings.output_dir
