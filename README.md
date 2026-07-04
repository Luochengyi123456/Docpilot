# DocPilot

一个很小的文档生成与提交工具，用来在当前项目中快速生成 `README.md` 并可选提交到 Git。

## 功能

- 扫描当前项目，生成基础 README
- 支持模板模式，适合小项目快速使用
- 支持 OpenAI 兼容 LLM 模式，可选生成更自然的文档
- 支持 DeepSeek API 接入
- 支持生成后自动 `git commit`
- 可选 `git push`

## 安装

在项目根目录执行：

```bash
pip install -e .
```

如果你想运行测试：

```bash
pip install -e .[test]
```

如果你要使用 OpenAI 或 DeepSeek LLM 模式：

```bash
pip install -e .
```

如果你的环境里还没装 `openai`，也可以单独安装：

```bash
pip install openai
```

> 说明：当前版本已把 `openai` 纳入基础依赖，因此只要安装项目本身即可直接使用 OpenAI 兼容接口和 DeepSeek。

## 使用方式

### 1. 在当前项目生成 README

进入目标项目目录后执行：

```bash
docpilot generate
```

这会在**当前目录**生成或覆盖 `README.md`。

### 2. 使用 DeepSeek 生成 README

```bash
export DEEPSEEK_API_KEY=your_api_key
export DEEPSEEK_BASE_URL=https://api.deepseek.com
export DOCPILOT_LLM_MODEL=deepseek-chat

docpilot generate
```

如果你想显式指定，也可以：

```bash
docpilot generate --provider deepseek
```

### 3. 使用 OpenAI 兼容接口生成 README

```bash
export OPENAI_API_KEY=your_api_key
export OPENAI_BASE_URL=https://api.openai.com/v1
export DOCPILOT_LLM_MODEL=gpt-4o-mini

docpilot generate
```

如果你想显式指定，也可以：

```bash
docpilot generate --provider openai
```

### 4. 生成并提交

```bash
docpilot run
```

默认会使用提交信息 `docs: update README`。

### 5. 生成、提交并推送

```bash
docpilot run --auto-push
```

执行到 push 前会询问是否继续，输入 `y` / `n` 确认。

## LLM 模式

默认情况下，DocPilot 会优先使用你已经配置好的大模型生成 README；如果没有检测到可用 API Key，才会退回模板模式。

`openai` 和 `deepseek` 都走 OpenAI 兼容协议，只需要配置不同的 API Key 和 Base URL。

### DeepSeek 示例

```bash
export DOCPILOT_LLM_PROVIDER=deepseek
export DEEPSEEK_API_KEY=your_api_key
export DEEPSEEK_BASE_URL=https://api.deepseek.com
export DOCPILOT_LLM_MODEL=deepseek-chat

python -m docpilot generate --provider deepseek
```

### OpenAI 示例

```bash
export DOCPILOT_LLM_PROVIDER=openai
export OPENAI_API_KEY=your_api_key
export OPENAI_BASE_URL=https://api.openai.com/v1
export DOCPILOT_LLM_MODEL=gpt-4o-mini

python -m docpilot generate --provider openai
```

## 在别的项目里怎么用

这个工具是“当前目录驱动”的。

你在哪个项目目录里执行，它就作用于哪个项目：

```bash
cd /path/to/another-project
docpilot generate
```

它会直接生成：

```bash
/path/to/another-project/README.md
```

## 命令说明

- `docpilot generate`：只生成 README
- `docpilot generate --commit`：生成后自动提交
- `docpilot generate --commit --auto-push`：生成后提交并推送
- `docpilot commit --msg "..."`：提交当前仓库变更
- `docpilot run`：先生成 README，再提交，默认提交信息为 `docs: update README`
- `docpilot run --auto-push`：提交后询问是否 push
- `--template <file>`：使用自定义模板文件生成 README
- `--provider template|openai|deepseek`：指定生成器

## 开发

```bash
pytest
```

## 行业价值说明

DocPilot 面向的是“文档产出成本高、更新频率高、但工程资源有限”的真实场景，尤其适合以下类型团队：

- **ToB 软件团队**：产品迭代快，README、部署说明、接口说明容易滞后，DocPilot 可以把“写文档”变成一次可复用的标准动作。
- **内部平台与基础设施团队**：项目数量多、成员流动快，自动生成基础文档可以显著降低新人上手和交接成本。
- **开源维护者**：可以快速补齐项目说明、使用方式与示例，提升仓库可读性和社区参与度。
- **AI 工程实践团队**：当团队已经在用 LLM 处理代码、测试或客服时，DocPilot 让 LLM 进一步进入文档环节，形成完整的工程自动化链路。

它的核心价值不只是“自动写 README”，而是把文档生成这件事标准化、低门槛化、可集成化：

1. **降低文档维护成本**：减少人工整理项目结构、命令、配置说明的时间。
2. **提升项目可交付性**：新项目、演示项目、PoC 项目可以更快具备对外展示能力。
3. **改善知识沉淀**：将散落在代码与口头交流中的信息沉淀到 README 中，降低知识丢失风险。
4. **支持自动化工作流**：生成、提交、推送可以串成一条流水线，适合接入脚本、CI 或开发者日常工具链。
5. **兼顾成本与效果**：既支持模板模式保证稳定性，也支持 OpenAI / DeepSeek 等 LLM 模式提升文档自然度。

从行业趋势来看，代码生成已经逐渐普及，而“文档生成自动化”仍然是很多团队的空白地带。DocPilot 的价值就在于用很低的接入成本，补上工程协作中最容易被忽略、却直接影响交付效率的一环。

## 说明

这是一个轻量工具，目标是满足小项目的基础文档自动化需求，而不是做成复杂平台。
# Docpilot
