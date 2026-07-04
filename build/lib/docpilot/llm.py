from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .config import DocPilotConfig
from .scanner import ProjectInfo


class LLMClient(Protocol):
    def generate_readme(self, project: ProjectInfo) -> str:
        ...


@dataclass
class TemplateLLMClient:
    config: DocPilotConfig

    def generate_readme(self, project: ProjectInfo) -> str:
        return _build_readme(project)


@dataclass
class OpenAILLMClient:
    config: DocPilotConfig

    def generate_readme(self, project: ProjectInfo) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("未安装 openai 依赖，请安装 openai 后再使用 LLM 模式") from exc

        if not self.config.openai_api_key:
            raise RuntimeError("未配置 OPENAI_API_KEY")

        client = OpenAI(api_key=self.config.openai_api_key, base_url=self.config.openai_base_url)
        prompt = _build_prompt(project)
        response = client.chat.completions.create(
            model=self.config.llm_model,
            messages=[
                {"role": "system", "content": "你是一个资深技术文档助手，请生成高质量中文 README。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise RuntimeError("LLM 未返回有效内容")
        return content.strip()


def create_llm_client(config: DocPilotConfig) -> LLMClient:
    if config.llm_provider == "openai":
        return OpenAILLMClient(config)
    return TemplateLLMClient(config)


def _build_prompt(project: ProjectInfo) -> str:
    return f"""项目名称：{project.name}
包管理器：{project.package_manager}
入口文件：{', '.join(project.entry_files) or '无'}
公开符号：{', '.join(project.public_python_symbols) or '无'}
源文件示例：{', '.join(project.source_files[:20])}

请输出完整 README，包含：项目简介、安装、使用、项目结构、API/配置、贡献指南、许可证。"""


def _build_readme(project: ProjectInfo) -> str:
    entry_files = project.entry_files or ["暂未检测到明确入口文件"]
    symbols = project.public_python_symbols or ["暂未检测到可公开导出的 Python 接口"]
    return f"""# {project.name}

> 由 DocPilot AI 自动生成

## 安装

```bash
pip install -r requirements.txt
```

## 项目入口

{chr(10).join(f'- `{item}`' for item in entry_files)}

## API / 公共符号

{chr(10).join(f'- `{item}`' for item in symbols)}

## 许可证

MIT
"""
