from __future__ import annotations

from pathlib import Path

from .settings import Settings


def case_markdown_files(settings: Settings) -> list[Path]:
    return [
        settings.case_dir / "fraso_home_caso.md",
        settings.case_dir / "fraso_home_storytelling_foundry.md",
        settings.case_dir / "kb" / "README.md",
    ]


def kb_markdown_files(settings: Settings) -> list[Path]:
    kb_dir = settings.case_dir / "kb"
    return sorted(p for p in kb_dir.glob("FS-KB-*.md") if p.is_file())


def knowledge_files(settings: Settings) -> list[Path]:
    return [p for p in [*case_markdown_files(settings), *kb_markdown_files(settings)] if p.exists()]


def csv_files(settings: Settings) -> list[Path]:
    return sorted((settings.case_dir / "data").glob("*.csv"))


def assert_assets(settings: Settings) -> None:
    missing = [p for p in case_markdown_files(settings) if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing case Markdown files: " + ", ".join(str(p) for p in missing))
    if not kb_markdown_files(settings):
        raise FileNotFoundError(f"No KB Markdown files found under {settings.case_dir / 'kb'}")
    if not csv_files(settings):
        raise FileNotFoundError(f"No CSV files found under {settings.case_dir / 'data'}")
