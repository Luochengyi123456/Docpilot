from docpilot.config import DocPilotConfig
from docpilot.llm import TemplateLLMClient, create_llm_client
from docpilot.scanner import ProjectInfo


def test_create_llm_client_defaults_to_template() -> None:
    client = create_llm_client(DocPilotConfig())
    assert isinstance(client, TemplateLLMClient)


def test_template_llm_client_generates_readme() -> None:
    client = TemplateLLMClient(DocPilotConfig())
    project = ProjectInfo(
        name="DocPilot",
        package_manager="pip",
        entry_files=["src/main.py"],
        source_files=["src/main.py"],
        public_python_symbols=["main"],
    )

    readme = client.generate_readme(project)

    assert "# DocPilot" in readme
    assert "src/main.py" in readme
    assert "main" in readme
