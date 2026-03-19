# ComfyUI Template Agent

Claude Code agent toolkit for ComfyUI template creation. Six skills guide you from node discovery through validated workflow composition to submission-ready documentation.

## Setup

### Prerequisites

- Python 3.12+
- Claude Code with skills support
- ComfyUI MCP server (`comfyui-cloud` or `comfyui-mcp`) for compose/flow skills

### Install

```bash
git clone <repo-url>
cd comfyui-template-agent
./setup.sh        # macOS/Linux
# or
.\setup.ps1       # Windows (PowerShell, requires Developer Mode or Admin)
```

The setup script installs dependencies with `pip install -e ".[dev]"` (editable mode makes `python -m src.*` commands work from any directory), symlinks skills into `~/.claude/skills/`, and runs the test suite.

## Skills

Skills require explicit invocation via slash commands. They do not auto-trigger from natural language.

| Slash command | Skill | What it does |
|---------------|-------|-------------|
| `/comfy-discover` | comfy-discover | Browse trending/new nodes from the registry |
| `/comfy-template-audit` | comfy-template-audit | Search templates, check coverage, find gaps worth filling |
| `/comfy-validate` | comfy-validate | Check workflow JSON against submission guidelines |
| `/comfy-compose` | comfy-compose | Build workflows from scratch, scaffold, or modify existing |
| `/comfy-document` | comfy-document | Generate index.json, Notion markdown, thumbnail specs |
| `/comfy-flow` | comfy-flow | Guided end-to-end template creation |

> If you have the global `comfy-tip` skill installed alongside this project's `comfy-discover`, use the slash command `/comfy-discover` to avoid ambiguity.

### comfy-template-audit

The audit skill covers the full template library:

- **Search**: `python -m src.templates.search --query "video" --type video`
- **Detail view**: `python -m src.templates.fetch --detail "flux_schnell_simple_generation"`
- **Cross-reference**: `python -m src.templates.cross_ref --query "KSampler" --level node` (which templates use a node)
- **Gap analysis**: `python -m src.templates.coverage gap --limit 20` (popular packs without templates)
- **Coverage report**: `python -m src.templates.coverage coverage`

### Example: Full Flow

```
You: /comfy-flow "Let's make a new template"
Claude: [starts guided flow, shows trending nodes]
You: "I like the Wan 2.1 video nodes, any gaps?"
Claude: [runs gap analysis, identifies uncovered use case]
You: "Let's scaffold from wan-t2v-basic"
Claude: [scaffolds, modifies, validates]
You: "Generate the submission docs"
Claude: [generates index.json, Notion markdown, thumbnail reminder]
```

## Cloud vs Local

**Cloud (recommended)**: API node auth (Gemini, BFL, Bria, Luma) is automatic with MCP server v0.2.0+. No token passing needed. Jobs can take 3-5 minutes for API node workflows -- the agent polls and asks before giving up.

If jobs silently vanish, update the MCP server to v0.2.0+.

**Local**: Open ComfyUI in your browser at `http://127.0.0.1:8188` and log into Comfy.org there. Desktop app auth is separate and may not work for all node types. Local execution is less tested than cloud.

## CLI Reference

```bash
# Discovery
python -m src.registry.highlights --mode trending --limit 10
python -m src.registry.highlights --mode new --category video
python -m src.registry.search --query "upscale" --limit 10

# Templates
python -m src.templates.search --query "flux"
python -m src.templates.coverage gap --limit 20

# Validation
python -m src.validator.validate --file workflow.json --mode strict

# Composition
python -m src.composer.compose --scaffold template-name --output workflow.json

# Documentation
python -m src.document.generate --file workflow.json --name my-template
```

## Development

```bash
pip install -e ".[dev]"       # Install with dev deps
pytest                         # Run all tests (~0.5s)
pytest tests/test_e2e.py       # E2E tests only
ruff check src/                # Lint
```

### Architecture

- `src/shared/` -- HTTP client (httpx), caching (DiskCache), format detection
- `src/registry/` -- Node discovery (highlights, search, spec)
- `src/templates/` -- Template library (fetch, search, cross_ref, coverage)
- `src/validator/` -- Validation engine (rules, engine, validate CLI)
- `src/composer/` -- Workflow composition (graph, scaffold, layout, compose CLI)
- `src/document/` -- Documentation generation (metadata, notion, generate CLI)
- `data/` -- Static data (core_nodes.json, guidelines.json, api_nodes.json)

### Maintenance

- **Core nodes list** may go stale. Run `python scripts/update_core_nodes.py` periodically to refresh from the ComfyUI repo.
- **Notion integration**: comfy-document can create private Notion pages via MCP. Requires Notion MCP server connected.

## Contributing

- Follow existing patterns (Pydantic models, DiskCache, httpx)
- Add tests for new features in `tests/`
- Run `pytest && ruff check src/` before committing
