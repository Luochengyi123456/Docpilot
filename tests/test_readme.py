from pathlib import Path


def test_readme_mentions_current_directory_usage() -> None:
    readme = Path(__file__).resolve().parents[1] / "README.md"
    content = readme.read_text(encoding="utf-8")

    assert "当前目录" in content
    assert "docpilot generate" in content
    assert "README.md" in content
