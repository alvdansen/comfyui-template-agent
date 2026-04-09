# AGENTS.md

Instructions for coding agents working with this repository.

## Project Overview

ComfyUI Template Agent is a Python toolkit that provides 6 agent skills for ComfyUI template creation. Skills cover node discovery, template auditing, workflow validation, workflow composition, documentation generation, and guided end-to-end template creation.

- **Language:** Python 3.12+
- **Dependencies:** httpx, pydantic (core); pytest, ruff (dev)
- **Distribution:** Claude Code skills in `.claude/skills/comfy-*/`

## Build & Test

```bash
./setup.sh                    # Full setup (venv, deps, skill links, tests)
pip install -e ".[dev]"       # Manual install
pytest                         # All tests (~0.5s)
pytest -x -q                  # Quick check
ruff check src/                # Lint
```

## Code Style

- Pydantic models for all data structures
- httpx with `follow_redirects=True`
- Module-level `DiskCache()` singletons for HTTP caching
- Tests in `tests/` mirroring `src/` structure
- CLI entry points: `python -m src.{module}.{script}`
- Workflow format: `nodes[]` + `links[]` arrays, never API format with string keys
- Line length: 100 (ruff enforced)

## Architecture

```
src/
  shared/     HTTP client, caching, format detection
  registry/   Node discovery (highlights, search, spec)
  templates/  Template library (fetch, search, cross_ref, coverage)
  validator/  Validation engine (rules, engine, validate CLI)
  composer/   Workflow composition (graph, scaffold, layout, compose CLI)
  document/   Documentation generation (metadata, notion, generate CLI)
data/         Static data (core_nodes.json, guidelines.json, api_nodes.json)
```

## Skills

Skills live in `.claude/skills/comfy-*/`. Each skill has `SKILL.md` (trigger, capabilities, commands, example session) and `gotchas.md` (failure points). Do not create additional subdirectories in skill folders.

| Skill | Purpose |
|-------|---------|
| comfy-discover | Browse trending/new nodes from the registry |
| comfy-template-audit | Search templates, check coverage, find gaps |
| comfy-validate | Check workflow JSON against submission guidelines |
| comfy-compose | Build workflows from scratch, scaffold, or modify |
| comfy-document | Generate index.json, Notion markdown, thumbnail specs |
| comfy-flow | Guided end-to-end template creation |

## Security

- No secrets or credentials in code
- `.env` files excluded via `.gitignore`
- External API calls: ComfyUI Registry (public, no auth), GitHub raw CDN (public, optional `GITHUB_TOKEN`)
- MCP server connections handled by the host environment, not by this codebase
