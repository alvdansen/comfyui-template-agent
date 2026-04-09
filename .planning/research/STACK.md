# Technology Stack

**Project:** ComfyUI Template Agent v3.0 -- Publish & Present
**Researched:** 2026-04-08
**Overall confidence:** HIGH (versions verified against PyPI, GitHub releases, official docs)

> This STACK.md covers what is NEW for v3.0: repo packaging for public release, CI/CD, and presentation material generation. The existing toolkit stack (Python 3.12+, httpx, pydantic, pytest, ruff, DiskCache) is unchanged and not re-documented here.

---

## Recommended Stack

### Repo Packaging & Public Release

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `pyproject.toml` enhancements | N/A | Add classifiers, URLs, license, authors for public-facing metadata | Required for a professional public repo; pyproject.toml is already the project's config file -- just needs enrichment |
| MIT License | N/A | Permissive license for open source release under Alvdansen Labs | Standard for developer tools; no copyleft friction for Comfy-Org to absorb |

**What NOT to add:** Do not add `build`/`twine`/PyPI publishing infrastructure. This project is a Claude Code skills toolkit installed via `git clone` + `pip install -e .`, not a PyPI package. Adding wheel/sdist publishing adds complexity with zero value for the target audience.

### CI/CD (GitHub Actions)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `actions/checkout` | `@v6` | Checkout repo in CI | Current stable version (upgraded to node24 runtime) |
| `actions/setup-python` | `@v6` | Set up Python 3.12 in CI runner | Current stable; supports pyproject.toml-based version detection |
| `astral-sh/ruff-action` | `@v3` | Run ruff lint + format check | Reads ruff config from existing pyproject.toml; no separate config needed |
| `pytest` (existing) | `>=9.0` | Run test suite in CI | Already a dev dependency; just needs a CI step |

**CI workflow structure:** Two jobs running in parallel -- `lint` (ruff check + ruff format --check) and `test` (pytest). Single Python version (3.12) since the project requires `>=3.12` and doesn't claim broader compatibility. No matrix build needed.

**What NOT to add:** Do not add `codecov`, `tox`, `nox`, or multi-version matrix testing. This is a toolkit with a narrow target audience (ComfyUI template creators running Claude Code), not a library consumed by diverse Python versions.

### Documentation

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Hand-written README.md | N/A | Primary documentation for public repo | The existing README is already solid; it needs polishing, not a docs framework |

**What NOT to add:** Do not add mkdocs, mkdocs-material, Sphinx, or any docs-site generator. The project is a Claude Code skills toolkit -- users interact through slash commands, not API docs. A well-structured README with skills reference, CLI examples, and architecture overview is the correct documentation format. A docs site would be over-engineering for a 6-skill toolkit.

### Presentation Materials -- Manim Animations (Hermes)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Manim Community Edition | 0.20.1 (installed on Hermes) | Animated pipeline/architecture visualizations | Already installed on Hermes (Ubuntu 24.04, RTX 4090); programmatic Python scenes; produces MP4/GIF |

Manim runs on Hermes only -- do NOT add it to pyproject.toml or local dependencies.

**Key Manim patterns for this project:**

| Pattern | Manim Classes | Use Case |
|---------|--------------|----------|
| Pipeline flow | `Rectangle`, `Arrow`, `Text`, `VGroup` | Animate the discover-to-document workflow pipeline |
| Architecture diagram | `RoundedRectangle`, `Arrow`, `Text`, `VGroup.arrange()` | Show src/ module structure and data flow |
| Metrics/stats | `BarChart`, `Text`, `FadeIn` | Template coverage stats, node registry numbers |
| Step-by-step reveal | `Create`, `FadeIn`, `Write`, `AnimationGroup` | Progressive build-up of system components |

**Scene organization:** One Python file per animation (e.g., `scenes/pipeline_flow.py`, `scenes/architecture.py`). Each file contains a single `Scene` subclass with a `construct()` method. Render via `manim -qh scenes/pipeline_flow.py PipelineFlow` on Hermes.

**Key Manim conventions (v0.20.1):**
- PyAV replaces FFmpeg (since v0.19.0) -- no system FFmpeg dependency needed
- Use `VGroup` to group related elements for coordinated animation
- Use `.arrange(RIGHT/DOWN, buff=0.5)` for automatic layout
- Use `SurroundingRectangle(text, corner_radius=0.1)` for labeled boxes
- Render at `-qh` (1080p) for presentations, `-ql` for iteration

### Presentation Materials -- PowerPoint (Hermes)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `python-pptx` | 1.0.2 | Generate PowerPoint deck programmatically | Mature, stable library; generates .pptx without Office installed; available as Hermes Agent skill |

python-pptx runs on Hermes only -- do NOT add it to pyproject.toml.

**Key python-pptx patterns:**

| Pattern | API | Use Case |
|---------|-----|----------|
| Title slide | `slide_layouts[0]`, `title.text`, `subtitle.text` | Deck title, project name |
| Content slide | `slide_layouts[1]`, `body.text`, `add_paragraph()` | Architecture, features, metrics |
| Image slide | `slide.shapes.add_picture()` | Embed Manim renders, screenshots |
| Table slide | `slide.shapes.add_table()` | Feature comparison, template matrix |

**Deck structure recommendation:** 10-15 slides max for async consumption. Title, Problem, Solution, Architecture, Demo Flow, 4 Template Showcases, Metrics, Next Steps.

### Presentation Materials -- Excalidraw (Hermes)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Excalidraw JSON format | Schema v2 | System architecture diagrams with hand-drawn aesthetic | Available as Hermes Agent skill; .excalidraw files are plain JSON; renders in browser |

Excalidraw generation runs on Hermes only -- do NOT add Python dependencies for it.

**Excalidraw JSON element structure (for programmatic generation):**

| Element Type | Key Properties | Use Case |
|-------------|---------------|----------|
| `rectangle` | `x`, `y`, `width`, `height`, `strokeColor`, `backgroundColor`, `roundness` | Module boxes, component boundaries |
| `arrow` | `x`, `y`, `points[][]`, `endArrowhead`, `startArrowhead` | Data flow, dependencies |
| `text` | `x`, `y`, `text`, `fontSize` (min 16px) | Labels, annotations |
| `diamond` | `x`, `y`, `width`, `height` | Decision points |

**File format:** `.excalidraw` files are JSON with top-level keys: `type: "excalidraw"`, `version: 2`, `elements[]`, `appState{}`, `files{}`. Elements render in array order (first = back layer).

### Async Demo Recording

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| VHS (charmbracelet) | 0.9.x | Record terminal demos as GIFs/MP4 from scripted .tape files | Reproducible, scriptable terminal recordings; perfect for Claude Code skill demos; available via Homebrew |
| asciinema | 2.x+ | Alternative: lightweight terminal recording | Lighter weight option if VHS is unavailable; produces .cast files playable in browser |

**Recommendation:** Use VHS for the async demo. Scripted `.tape` files ensure reproducible recordings showing the discover-to-document flow. GIF output embeds directly in README; MP4 for the presentation deck.

**VHS tape example structure:**
```
Output demo.gif
Set FontSize 14
Set Width 1200
Set Height 600

Type "claude"
Enter
Sleep 2s
Type "/comfy-discover trending"
Enter
Sleep 3s
```

---

## Repo Health Files (New)

| File | Purpose | Notes |
|------|---------|-------|
| `LICENSE` | MIT license text | Required for open source; place in repo root |
| `CONTRIBUTING.md` | Contribution guidelines | Keep minimal: dev setup, PR process, code style (ruff) |
| `.github/workflows/ci.yml` | CI pipeline | Lint + test on push/PR to main |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Bug report template | Standard fields: description, steps, expected, actual |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Feature request template | Standard fields: problem, proposed solution |

**What NOT to add:**
- `CODE_OF_CONDUCT.md` -- Overkill for a focused internal-to-external toolkit. Add later if community grows.
- `SECURITY.md` -- No user-facing security surface (no auth, no data storage, no network services).
- `CHANGELOG.md` -- Git history + GitHub releases are sufficient for this project size.
- `.github/FUNDING.yml` -- Not applicable for an Alvdansen Labs project.

---

## pyproject.toml Enhancements

Current pyproject.toml needs these additions for public release:

```toml
[project]
name = "comfyui-template-agent"
version = "3.0.0"
description = "Claude Code agent toolkit for ComfyUI template creation"
requires-python = ">=3.12"
license = {text = "MIT"}
authors = [
    {name = "Timothy", email = "timothy@promptcrafted.com"},
]
readme = "README.md"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Software Development :: Code Generators",
    "Private :: Do Not Upload",
]
dependencies = [
    "httpx>=0.28",
    "pydantic>=2.0",
]

[project.urls]
Homepage = "https://github.com/alvdansen-labs/comfyui-template-agent"
Repository = "https://github.com/alvdansen-labs/comfyui-template-agent"
Issues = "https://github.com/alvdansen-labs/comfyui-template-agent/issues"
```

**Key decisions:**
- `Private :: Do Not Upload` classifier prevents accidental PyPI uploads. Remove when/if PyPI publishing is desired.
- Version bumped to `3.0.0` to match milestone.
- `authors` and `license` fields are required for a proper public repo.
- No `[project.scripts]` entry points -- users invoke via `python -m src.*` or Claude Code skills.

---

## GitHub Actions CI Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/ruff-action@v3
        with:
          args: check
      - uses: astral-sh/ruff-action@v3
        with:
          args: format --check

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -e ".[dev]"
      - run: pytest -q
```

**Why this structure:**
- Two parallel jobs (lint doesn't need pip install; test doesn't need ruff-action)
- `ruff-action@v3` reads version from pyproject.toml automatically
- `cache: pip` speeds up subsequent runs
- Single Python version -- no matrix needed
- Triggers on push to main + all PRs

---

## Publishing to Alvdansen Labs GitHub Org

| Step | Command | Notes |
|------|---------|-------|
| Create repo in org | `gh repo create alvdansen-labs/comfyui-template-agent --public --source=. --remote=origin --push` | Or transfer existing repo via GitHub Settings > Transfer |
| Set default branch | `gh repo edit --default-branch main` | If repo uses `master`, rename first |
| Enable branch protection | Via GitHub UI | Require CI passing before merge to main |

**Transfer vs fresh create:** If the current repo is on Timothy's personal account, transferring preserves git history and stars. Creating fresh in the org and pushing is simpler but loses history attribution. Recommendation: create fresh in org and push (clean slate for public release).

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Docs framework | README.md only | mkdocs-material | Overkill for 6-skill toolkit; README + CLI help is the right UX |
| Docs framework | README.md only | Sphinx | RST syntax adds friction; no API docs to auto-generate |
| CI lint | ruff-action@v3 | Manual ruff in pytest job | Dedicated action is faster (no pip install) and shows inline annotations |
| Terminal recording | VHS | asciinema | VHS produces GIF directly (embeddable in README); tape files are version-controllable |
| Terminal recording | VHS | Screen recording (OBS) | Not reproducible; large file sizes; can't embed in README |
| Slide generation | python-pptx | Google Slides API | Requires OAuth; python-pptx runs offline on Hermes |
| Architecture diagrams | Excalidraw JSON | Mermaid in README | Excalidraw has richer visual output; hand-drawn aesthetic fits presentation context |
| Architecture diagrams | Excalidraw JSON | draw.io | Excalidraw is already a Hermes skill; simpler JSON format |
| Animation | Manim CE 0.20.1 | Motion Canvas | Manim already installed on Hermes; Python native; proven for technical content |
| PyPI publishing | None (Private classifier) | twine + build | Not a library; installed via git clone; PyPI adds maintenance burden with no benefit |

---

## Integration Points

### Local (macOS development machine)
- **pyproject.toml**: Enhanced with public-release metadata (already the project config)
- **README.md**: Polished for public consumption (already exists, needs editing)
- **CI workflow**: New `.github/workflows/ci.yml` file
- **Repo health files**: New `LICENSE`, `CONTRIBUTING.md`, issue templates
- **VHS tape files**: New `demos/*.tape` for terminal recordings (optional, can also run on Hermes)

### Remote (Hermes -- Ubuntu 24.04, RTX 4090)
- **Manim scenes**: `scenes/*.py` files, rendered via `manim -qh` over SSH
- **PowerPoint generation**: Via Hermes Agent python-pptx skill
- **Excalidraw generation**: Via Hermes Agent Excalidraw skill
- **All presentation outputs**: SCP back to local or commit from Hermes

### Dependency boundary
| Scope | Dependencies | Where Declared |
|-------|-------------|----------------|
| Core toolkit | httpx, pydantic | pyproject.toml `[project.dependencies]` |
| Dev/CI | pytest, ruff | pyproject.toml `[project.optional-dependencies.dev]` |
| Presentation (Hermes only) | manim, python-pptx | Hermes environment only -- NOT in pyproject.toml |
| Demo recording | VHS (Go binary) | Homebrew on local OR Hermes -- NOT a Python dep |

This separation is critical: presentation tooling lives on Hermes and must not pollute the project's dependency tree.

---

## Installation Summary

### For toolkit users (public release)
```bash
git clone https://github.com/alvdansen-labs/comfyui-template-agent.git
cd comfyui-template-agent
./setup.sh
```
No changes to the existing install flow.

### For presentation generation (Hermes only)
```bash
ssh hermes
# Manim CE 0.20.1, python-pptx already available
# Run scene renders and slide generation there
```

### For CI (GitHub Actions)
```bash
# Automatic -- triggered by push/PR
# No manual setup needed
```

---

## Sources

- [GitHub Actions setup-python@v6](https://github.com/actions/setup-python) -- action version, Python version support (HIGH confidence)
- [GitHub Actions checkout@v6](https://github.com/actions/checkout) -- action version (HIGH confidence)
- [astral-sh/ruff-action@v3](https://github.com/astral-sh/ruff-action) -- ruff CI integration (HIGH confidence)
- [Manim Community v0.20.1 docs](https://docs.manim.community/en/stable/) -- current stable release, Scene patterns (HIGH confidence)
- [Manim v0.19.0 changelog](https://docs.manim.community/en/stable/changelog/0.19.0-changelog.html) -- PyAV replacing FFmpeg (HIGH confidence)
- [python-pptx 1.0.2 on PyPI](https://pypi.org/project/python-pptx/) -- current stable release (HIGH confidence)
- [python-pptx documentation](https://python-pptx.readthedocs.io/) -- API patterns (HIGH confidence)
- [Excalidraw JSON Schema](https://docs.excalidraw.com/docs/codebase/json-schema) -- file format spec (HIGH confidence)
- [Excalidraw Element Format (DeepWiki)](https://deepwiki.com/excalidraw/excalidraw-mcp/7.2-excalidraw-element-format) -- element properties (MEDIUM confidence)
- [VHS by Charmbracelet](https://github.com/charmbracelet/vhs) -- terminal recording tool (HIGH confidence)
- [Python Packaging Guide -- pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) -- metadata fields (HIGH confidence)
- [PyPI Classifiers](https://pypi.org/classifiers/) -- valid classifier values (HIGH confidence)
- [GitHub Docs -- Transferring a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository) -- org transfer process (HIGH confidence)
