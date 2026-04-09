# ComfyUI Template Agent

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-2E7D32)
![Tests](https://img.shields.io/badge/Tests-passing-brightgreen)
![Claude Code](https://img.shields.io/badge/Claude_Code-Agent_Toolkit-7C3AED)

Claude Code agent toolkit for ComfyUI template creation -- from node discovery to submission-ready docs in a single session.

> **4** production templates | **6** agent skills | **5.5M+** combined node pack downloads

## Quick Start

1. Clone and enter the repo:
   ```bash
   git clone https://github.com/alvdansen/comfyui-template-agent.git && cd comfyui-template-agent
   ```

2. Run setup (creates `.venv`, installs deps, links skills, runs tests):
   ```bash
   ./setup.sh
   ```

3. Open Claude Code and invoke your first skill:
   ```
   /comfy-discover
   ```

Prerequisites: Python 3.12+, Claude Code with skills support. ComfyUI MCP server (`comfyui-cloud` or `comfyui-mcp`) required for compose and flow skills.

## Skills

| Command | Skill | Description |
|---------|-------|-------------|
| `/comfy-discover` | Node Discovery | Browse trending, new, and popular nodes from the ComfyUI registry |
| `/comfy-template-audit` | Template Intelligence | Search templates, check coverage, find gaps worth filling |
| `/comfy-validate` | Workflow Validation | Check workflow JSON against submission guidelines and cloud compatibility |
| `/comfy-compose` | Workflow Composition | Build workflows from scratch, from template scaffolds, or modify existing |
| `/comfy-document` | Submission Docs | Generate index.json, Notion markdown, and thumbnail specs |
| `/comfy-flow` | Guided Flow | End-to-end template creation: discover to submission-ready docs |

Skills require explicit `/slash-command` invocation. Use `/comfy-flow` for the guided end-to-end experience.

### Example: Full Flow

```
You: /comfy-flow "Let's make a new template"
Claude: [shows trending nodes, runs gap analysis]
You: "I like the audio separation nodes, any gaps?"
Claude: [identifies uncovered use case, scaffolds workflow]
You: "Validate and generate submission docs"
Claude: [validates, generates index.json + Notion markdown + thumbnail spec]
```

## Architecture

```
  /comfy-discover ─────┐
  /comfy-template-audit │
  /comfy-validate ──────┤──> src/ modules ──> Registry API (api.comfy.org)
  /comfy-compose ───────┤                ──> GitHub API (workflow_templates)
  /comfy-document ──────┤                ──> ComfyUI Cloud MCP
  /comfy-flow ──────────┘
```

- `src/shared/` -- HTTP client (httpx), caching (DiskCache), format detection
- `src/registry/` -- Node discovery (highlights, search, spec)
- `src/templates/` -- Template library (fetch, search, cross_ref, coverage)
- `src/validator/` -- Validation engine (rules, engine, validate CLI)
- `src/composer/` -- Workflow composition (graph, scaffold, layout, compose CLI)
- `src/document/` -- Documentation generation (metadata, notion, generate CLI)
- `data/` -- Static data (core_nodes.json, guidelines.json, api_nodes.json)

## Templates

Built with this toolkit as proof-of-concept:

| Template | Node Pack | Status |
|----------|-----------|--------|
| [MelBandRoFormer Audio Separation](templates/melbandroformer-audio-separation/) | `comfyui-melbandroformer` | Submitted |
| [Florence2 Vision AI](templates/florence2-vision-ai/) | `comfyui-florence2` | Demo |
| [GGUF Quantized txt2img](templates/gguf-quantized-txt2img/) | `ComfyUI-GGUF` | Demo |
| [Impact Pack Face Detailer](templates/impact-pack-face-detailer/) | `comfyui-impact-pack` | Demo |

Each template directory contains `workflow.json`, `index.json`, `submission.md`, and `build.py`.

### Cloud vs Local

**Cloud (recommended):** API node auth is automatic with MCP server v0.2.0+. No token passing needed.

**Local:** Open ComfyUI at `http://127.0.0.1:8188` and log into Comfy.org. Desktop app auth is separate and may not work for all node types.

## Development

```bash
git clone https://github.com/alvdansen/comfyui-template-agent.git
cd comfyui-template-agent
./setup.sh                    # Creates .venv, installs deps, links skills, runs tests
pytest                         # Run all tests (~0.5s)
ruff check src/                # Lint
```

CLI reference:

```bash
python -m src.registry.highlights --mode trending --limit 10   # Discovery
python -m src.templates.coverage gap --limit 20                # Gap analysis
python -m src.validator.validate --file workflow.json           # Validation
python -m src.composer.compose --scaffold <name> --output w.json  # Composition
python -m src.document.generate --file workflow.json --name tpl   # Documentation
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style conventions (Pydantic, httpx, ruff), PR process, and skill authoring guide.

## License

[MIT](LICENSE)

