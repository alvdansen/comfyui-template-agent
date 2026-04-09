# Handoff Guide

Evaluation guide for Comfy-Org developers reviewing the ComfyUI Template Agent toolkit.

## Quick Verification

```bash
git clone https://github.com/alvdansen/comfyui-template-agent.git
cd comfyui-template-agent
./setup.sh        # Creates .venv, installs deps, links skills, runs 212 tests
```

Expected: all tests pass in under 1 second, 6 skill symlinks created.

## Test Scenarios

### 1. Node Discovery (no MCP required)

Open Claude Code in the repo directory and run:

```
/comfy-discover
```

Then ask: "Show me trending nodes this week"

**Expected:** Agent calls `python -m src.registry.highlights` and shows a ranked table of trending node packs with download counts and descriptions.

### 2. Gap Analysis (no MCP required)

```
/comfy-template-audit
```

Then ask: "What node packs don't have templates yet?"

**Expected:** Agent runs coverage analysis and shows high-download node packs that have no existing template in the ComfyUI template library.

### 3. Workflow Validation (no MCP required)

```
/comfy-validate
```

Then point it at a template: "Validate templates/melbandroformer-audio-separation/workflow.json"

**Expected:** Agent checks the workflow against submission guidelines (node types, connections, required fields) and reports pass/fail with specific issues.

### 4. Full Flow (requires ComfyUI MCP server)

```
/comfy-flow "Let's make a new template"
```

**Expected:** Agent walks you through discovery, gap analysis, scaffold selection, workflow composition, validation, and doc generation in sequence.

### 5. CLI Tools (no Claude Code required)

```bash
python -m src.registry.highlights --mode trending --limit 5
python -m src.templates.coverage gap --limit 5
python -m src.validator.validate --file templates/melbandroformer-audio-separation/workflow.json
```

**Expected:** Each command produces formatted terminal output with relevant data.

## What to Look For

- **Skill quality:** Do the 6 skills feel like natural extensions of Claude Code? Do they handle edge cases (empty results, network errors, malformed JSON)?
- **Template quality:** Are the 4 built templates valid workflows that run on ComfyUI Cloud?
- **Code quality:** Pydantic models, httpx with caching, ruff-clean, 212 tests at 0.2s
- **Extensibility:** How easy is it to add a new skill or template?

## Architecture Overview

See the [architecture diagram](docs/architecture.svg) and [slide deck](docs/slides.pdf) for visual walkthroughs.

```
Skills Layer (6 slash commands)
    |
Python Modules (5 packages + shared)
    |
External APIs (ComfyUI Registry, Template Library, MCP Server)
```

Each skill maps to one or more Python modules. The `/comfy-flow` skill orchestrates all modules in sequence.

## Key Files

| File | Purpose |
|------|---------|
| `setup.sh` | One-command install (venv + deps + skill links + tests) |
| `CLAUDE.md` | Agent instructions for Claude Code |
| `CONTRIBUTING.md` | Developer setup, conventions, skill authoring |
| `docs/architecture.svg` | Visual architecture diagram |
| `docs/slides.pdf` | 12-slide async presentation |

## Contact

Timothy -- timothy@promptcrafted.com
