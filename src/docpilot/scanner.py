from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .config import DEFAULT_CONFIG, DocPilotConfig

MAX_SOURCE_FILE_SIZE = 5 * 1024 * 1024
MAX_REPORTED_ENTRIES = 5
MAX_REPORTED_SOURCE_FILES = 200
MAX_REPORTED_SYMBOLS = 10


@dataclass(frozen=True)
class ProjectInfo:
    name: str
    package_manager: str
    entry_files: list[str]
    source_files: list[str]
    public_python_symbols: list[str]


class ProjectScanner:
    def __init__(self, root: Path, config: DocPilotConfig = DEFAULT_CONFIG) -> None:
        self.root = root
        self.config = config

    def detect_package_manager(self) -> str:
        root = self.root
        if (root / "package-lock.json").exists() or (root / "node_modules").exists():
            return "npm"
        if (root / "pnpm-lock.yaml").exists():
            return "pnpm"
        if (root / "yarn.lock").exists():
            return "yarn"
        if (root / "poetry.lock").exists():
            return "poetry"
        if (root / "Cargo.toml").exists():
            return "cargo"
        if (root / "requirements.txt").exists() or any(root.glob("*.py")):
            return "pip"
        return "pip"

    def iter_source_files(self) -> Iterable[Path]:
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in self.config.skip_dirs]
            for filename in filenames:
                path = Path(dirpath) / filename
                if path.suffix.lower() in self.config.supported_suffixes:
                    yield path

    def infer_project_name(self) -> str:
        return self.root.name or "DocPilot"

    def _safe_relative_path(self, path: Path) -> str | None:
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return None

    def detect_entry_files(self, files: Iterable[Path]) -> list[str]:
        entries: list[str] = []
        for path in files:
            if path.name in self.config.entry_filenames:
                relative = self._safe_relative_path(path)
                if relative is not None:
                    entries.append(relative)
            if len(entries) >= MAX_REPORTED_ENTRIES:
                break
        return entries

    def detect_python_symbols(self, files: Iterable[Path]) -> list[str]:
        symbols: list[str] = []
        for path in files:
            if path.suffix != ".py":
                continue
            try:
                if path.stat().st_size > MAX_SOURCE_FILE_SIZE:
                    continue
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, SyntaxError):
                continue
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not node.name.startswith("_"):
                    symbols.append(node.name)
                    if len(symbols) >= MAX_REPORTED_SYMBOLS:
                        return symbols
        return symbols

    def analyze(self) -> ProjectInfo:
        source_files: list[str] = []
        files_iter = self.iter_source_files()
        entry_files = self.detect_entry_files(files_iter)
        for path in self.iter_source_files():
            relative = self._safe_relative_path(path)
            if relative is None:
                continue
            source_files.append(relative)
            if len(source_files) >= MAX_REPORTED_SOURCE_FILES:
                break
        return ProjectInfo(
            name=self.infer_project_name(),
            package_manager=self.detect_package_manager(),
            entry_files=entry_files,
            source_files=source_files,
            public_python_symbols=self.detect_python_symbols(self.iter_source_files()),
        )
