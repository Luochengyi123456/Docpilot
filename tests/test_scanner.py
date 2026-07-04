from pathlib import Path

from docpilot.scanner import ProjectScanner


def test_detect_package_manager_poetry_over_requirements(tmp_path: Path) -> None:
    (tmp_path / "poetry.lock").write_text("", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("click", encoding="utf-8")

    scanner = ProjectScanner(tmp_path)

    assert scanner.detect_package_manager() == "poetry"


def test_analyze_skips_large_python_file(tmp_path: Path) -> None:
    large_file = tmp_path / "big.py"
    large_file.write_bytes(b"x" * (5 * 1024 * 1024 + 1))
    (tmp_path / "main.py").write_text("def run():\n    return True\n", encoding="utf-8")

    scanner = ProjectScanner(tmp_path)
    info = scanner.analyze()

    assert "main.py" in info.entry_files
    assert "run" in info.public_python_symbols
    assert "big.py" in info.source_files
