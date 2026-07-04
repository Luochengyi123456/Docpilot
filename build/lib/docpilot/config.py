from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DocPilotConfig:
    skip_dirs: frozenset[str] = frozenset({".git", "node_modules", "__pycache__", ".venv", ".mypy_cache", ".pytest_cache", "dist", "build"})
    supported_suffixes: frozenset[str] = frozenset({".py", ".js", ".ts", ".tsx", ".json", ".md", ".yaml", ".yml", ".toml"})
    entry_filenames: tuple[str, ...] = ("main.py", "app.py", "index.js", "index.ts", "cli.py")
    llm_provider: str = os.getenv("DOCPILOT_LLM_PROVIDER", "template")
    llm_model: str = os.getenv("DOCPILOT_LLM_MODEL", "gpt-4o-mini")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")


DEFAULT_CONFIG = DocPilotConfig()
