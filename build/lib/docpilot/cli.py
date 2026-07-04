from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import click

from .config import DEFAULT_CONFIG, DocPilotConfig
from .llm import create_llm_client
from .scanner import ProjectScanner

MAX_TEMPLATE_SIZE = 5 * 1024 * 1024
MAX_BULLET_ITEMS = 5


class DocPilotError(RuntimeError):
    pass


def _project_root() -> Path:
    return Path.cwd()


def _load_template(template: Path) -> str:
    if template.stat().st_size > MAX_TEMPLATE_SIZE:
        raise DocPilotError("模板文件过大")
    return template.read_text(encoding="utf-8")


def _format_bullets(items: list[str]) -> str:
    limited = items[:MAX_BULLET_ITEMS]
    return "\n".join(f"- `{item}`" for item in limited)


def _render_readme(scanner: ProjectScanner, config: DocPilotConfig, template: Optional[Path] = None) -> str:
    if template is not None:
        return _load_template(template)
    client = create_llm_client(config)
    project = scanner.analyze()
    return client.generate_readme(project)


def _write_readme(root: Path, content: str) -> Path:
    target = root / "README.md"
    target.write_text(content, encoding="utf-8")
    return target


def _run_git_command(args: list[str]) -> None:
    subprocess.run(args, check=True)


@dataclass
class GitCommitResult:
    commit_created: bool = False
    push_attempted: bool = False


def _rollback_last_commit() -> None:
    _run_git_command(["git", "reset", "--hard", "HEAD~1"])


def _build_config(provider: Optional[str]) -> DocPilotConfig:
    if provider is None:
        return DEFAULT_CONFIG
    return DocPilotConfig(
        llm_provider=provider,
        llm_model=os.getenv("DOCPILOT_LLM_MODEL", DEFAULT_CONFIG.llm_model),
        openai_api_key=os.getenv("OPENAI_API_KEY", DEFAULT_CONFIG.openai_api_key),
        openai_base_url=os.getenv("OPENAI_BASE_URL", DEFAULT_CONFIG.openai_base_url),
    )


def _commit_and_maybe_push(message: str, auto_push: bool) -> GitCommitResult:
    result = GitCommitResult()
    _run_git_command(["git", "add", "."])
    _run_git_command(["git", "commit", "-m", message])
    result.commit_created = True
    if auto_push:
        result.push_attempted = True
        try:
            _run_git_command(["git", "push"])
        except subprocess.CalledProcessError:
            if result.commit_created:
                _rollback_last_commit()
            raise
    return result


@click.group()
def main() -> None:
    """DocPilot CLI."""


@main.command()
@click.option("--template", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None, help="使用本地模板文件直接生成 README")
@click.option("--provider", type=click.Choice(["template", "openai"]), default=None, help="指定 README 生成器")
def generate(template: Optional[Path], provider: Optional[str]) -> None:
    config = _build_config(provider)
    root = _project_root()
    scanner = ProjectScanner(root, config)
    readme = _render_readme(scanner, config, template)
    path = _write_readme(root, readme)
    click.echo(f"README 已生成：{path}")


@main.command()
@click.option("--msg", required=True, help="Git 提交信息")
@click.option("--auto-push", is_flag=True, default=False, help="提交后自动 push")
def commit(msg: str, auto_push: bool) -> None:
    try:
        _commit_and_maybe_push(msg, auto_push)
    except subprocess.CalledProcessError as exc:
        raise DocPilotError(f"Git 提交失败：{exc}") from exc
    click.echo("Git 提交已完成")


@main.command()
@click.option("--msg", required=True, help="Git 提交信息")
@click.option("--template", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None, help="使用本地模板文件直接生成 README")
@click.option("--provider", type=click.Choice(["template", "openai"]), default=None, help="指定 README 生成器")
@click.option("--auto-push", is_flag=True, default=False, help="提交后自动 push")
def run(msg: str, template: Optional[Path], provider: Optional[str], auto_push: bool) -> None:
    config = _build_config(provider)
    root = _project_root()
    scanner = ProjectScanner(root, config)
    readme = _render_readme(scanner, config, template)
    _write_readme(root, readme)
    try:
        _commit_and_maybe_push(msg, auto_push)
    except subprocess.CalledProcessError as exc:
        raise DocPilotError(f"DocPilot 流程失败并已尝试回滚：{exc}") from exc
    click.echo("DocPilot 流程已完成")
