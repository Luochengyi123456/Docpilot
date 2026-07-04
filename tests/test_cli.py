from pathlib import Path

from click.testing import CliRunner

from docpilot.cli import main


def test_generate_creates_readme(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "main.py").write_text("def run():\n    return True\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["generate"])

    assert result.exit_code == 0
    assert (tmp_path / "README.md").exists()


def test_generate_with_template(tmp_path: Path, monkeypatch) -> None:
    template = tmp_path / "template.md"
    template.write_text("# Template", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["generate", "--template", str(template)])

    assert result.exit_code == 0
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "# Template"
