<p align="center">
  <img src="docs/banner.svg" width="100%" alt="ComfyUI Template Agent">
</p>

<p align="center">
  <a href="https://github.com/alvdansen/comfyui-template-agent/actions/workflows/ci.yml"><img src="https://github.com/alvdansen/comfyui-template-agent/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-2E7D32" alt="License">
  <img src="https://img.shields.io/badge/Claude_Code-Agent_Toolkit-7C3AED" alt="Claude Code">
</p>

<p align="center">
  <strong>From "what is this?" to "I just made my first image" — and from "what should we build?" to a submission-ready template — in a single conversation.</strong>
</p>

---

**ComfyUI Template Agent v2** is a Claude Code toolkit with eight agent skills spanning two audiences. The original **creator** pack (v1) handles node discovery, gap analysis, workflow validation, composition, and submission docs. The new **first-run** pack (v2) closes the cold-start cliff: new users go from zero ComfyUI experience to a validated, running workflow in one conversation, with every node explained in plain language along the way.

> You talk to Claude. Claude talks to the ComfyUI ecosystem. You get either your first working image or a tested, validated, submission-ready template -- depending on which skill you invoke.

<br>

<table>
<tr>
<td align="center"><strong>4</strong><br><sub>Production Templates</sub></td>
<td align="center"><strong>8</strong><br><sub>Agent Skills (v2)</sub></td>
<td align="center"><strong>4</strong><br><sub>First-Run Starters</sub></td>
<td align="center"><strong>&lt;2min</strong><br><sub>Zero to First Image (Cloud)</sub></td>
</tr>
</table>

<br>

## How It Works

You invoke a skill. The agent researches the ComfyUI registry, analyzes template coverage, builds workflows, validates against submission guidelines, and generates all required documentation. One conversation, start to finish.

```
You:    /comfy-flow "Let's make a new template"
Claude: Scanning registry... 47 trending packs this week.
        Running gap analysis against 200+ existing templates.
        Found 3 uncovered categories. Top opportunity:
        > MelBandRoFormer audio separation (2.1M downloads, 0 templates)
        Want me to scaffold this one?

You:    Yes, build it.
Claude: [scaffolds workflow, validates against guidelines, generates submission docs]
        Done. Created workflow.json, index.json, submission.md, and thumbnail spec.
        All 12 guideline checks passing. Ready for submission.
```

<br>

## Demo

![Demo](docs/demo.gif)

<br>

## Quick Start

```bash
git clone https://github.com/alvdansen/comfyui-template-agent.git
cd comfyui-template-agent
./setup.sh         # Creates .venv, installs deps, links skills, runs tests
```

Then open Claude Code and run:

```
/comfy-flow
```

That's it. The agent walks you through the entire process.

**Prerequisites:** Python 3.12+, [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with skills support. [ComfyUI MCP server](https://github.com/comfy-org/comfyui-mcp) required for compose and flow skills.

<br>

## Skills

### For creators (v1)

| Command | What It Does |
|---------|-------------|
| `/comfy-discover` | Browse trending, new, and popular nodes from the ComfyUI registry |
| `/comfy-template-audit` | Search templates, check coverage, find gaps worth filling |
| `/comfy-validate` | Check workflow JSON against submission guidelines and cloud compatibility |
| `/comfy-compose` | Build workflows from scratch, from scaffolds, or modify existing ones |
| `/comfy-document` | Generate index.json, Notion markdown, and thumbnail specs |
| `/comfy-flow` | **Guided end-to-end**: discover nodes to submission-ready docs in one session |

### For new users (v2 — new)

| Command | What It Does |
|---------|-------------|
| `/comfy-onboard` | **Guided first-run**: intent → scaffold → validate → run a working workflow, start to finish |
| `/comfy-explain` | Plain-language explanations of any node, parameter, error message, or guideline rule |

Start with `/comfy-onboard` if you've never used ComfyUI before — it takes you from "what do I even do here" to a running image in about two minutes on Comfy Cloud. Use `/comfy-flow` if you already know ComfyUI and want to build a submission-quality template.

<br>

## Architecture

<p align="center">
  <img src="docs/architecture.svg" width="90%" alt="Architecture">
</p>

| Layer | Modules | Purpose |
|-------|---------|---------|
| **Agent Skills** | `.claude/skills/comfy-*` | Natural language interface -- slash commands that Claude Code responds to |
| **Python Core** | `src/registry/`, `src/templates/`, `src/validator/`, `src/composer/`, `src/document/` | Business logic -- registry API, template analysis, validation rules, graph composition, doc generation |
| **Shared** | `src/shared/` | HTTP client (httpx), disk caching, format detection |
| **Data** | `data/` | Static reference -- core nodes, submission guidelines, API node mappings |

<br>

## Templates

Four templates built with this toolkit as proof-of-concept:

| Template | Node Pack | Type |
|----------|-----------|------|
| [MelBandRoFormer Audio Separation](templates/melbandroformer-audio-separation/) | `comfyui-melbandroformer` | Audio stem separation (5 nodes, linear) |
| [Florence2 Vision AI](templates/florence2-vision-ai/) | `comfyui-florence2` | Captioning + detection (6 nodes, multi-output) |
| [GGUF Quantized txt2img](templates/gguf-quantized-txt2img/) | `ComfyUI-GGUF` | FLUX.1-schnell generation (9 nodes, GGUF loaders) |
| [Impact Pack Face Detailer](templates/impact-pack-face-detailer/) | `comfyui-impact-pack` | Face detection + auto-detail (11 nodes, fan-out) |

Each directory contains `workflow.json`, `index.json`, `submission.md`, and `build.py`.

**Cloud (recommended):** API node auth is automatic with MCP server v0.2.0+. No token management needed.

<br>

## Development

```bash
pytest                         # Run all tests (~0.5s)
ruff check src/                # Lint
```

CLI tools for standalone use:

```bash
python -m src.registry.highlights --mode trending --limit 10
python -m src.templates.coverage gap --limit 20
python -m src.validator.validate --file workflow.json
python -m src.composer.compose --scaffold <name> --output w.json
python -m src.document.generate --file workflow.json --name tpl
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for code style (Pydantic, httpx, ruff), PR process, and skill authoring guide.

<br>

## License

[MIT](LICENSE)

---

<p align="center">
  <sub>Built by <a href="https://github.com/alvdansen">Alvdansen Labs</a> for the <a href="https://comfy.org">Comfy-Org</a> ecosystem</sub>
</p>
