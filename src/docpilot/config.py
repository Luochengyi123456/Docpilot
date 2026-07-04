from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DocPilotConfig:
    skip_dirs: frozenset[str] = frozenset({".git", "node_modules", "__pycache__", ".venv", ".mypy_cache", ".pytest_cache", "dist", "build"})
    supported_suffixes: frozenset[str] = frozenset({".py", ".js", ".ts", ".tsx", ".json", ".md", ".yaml", ".yml", ".toml", ".java", ".kt", ".go", ".rs", ".cs", ".php", ".rb"})
    entry_filenames: tuple[str, ...] = ("main.py", "app.py", "index.js", "index.ts", "cli.py", "pom.xml", "build.gradle", "build.gradle.kts", "go.mod", "Cargo.toml", "Program.cs")
    llm_provider: str = os.getenv("DOCPILOT_LLM_PROVIDER", "template")
    llm_model: str = os.getenv("DOCPILOT_LLM_MODEL", "gpt-4o-mini")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


DEFAULT_CONFIG = DocPilotConfig()
