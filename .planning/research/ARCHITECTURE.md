# Architecture: v3.0 Publish & Present

**Domain:** Public release of a Python + Claude Code skills toolkit with presentation materials
**Researched:** 2026-04-08
**Confidence:** HIGH (existing codebase fully analyzed, target org conventions verified, CI patterns established)

## Current State Assessment

The repo at `aramintak/comfyui-template-agent` is a working internal toolkit with 3,856 lines of source code across 6 modules, 3,887 lines of tests, 4 delivered templates, and 6 Claude Code skills. It works. The architecture is sound. The restructuring for v3.0 is about **packaging and presentation**, not rewriting.

### What Exists Today

```
comfyui-template-agent/
  .claude/skills/comfy-*/          # 6 skill definitions (SKILL.md + gotchas.md)
  .planning/                       # GSD planning artifacts (internal)
  src/
    shared/                        # HTTP client, caching, config, format detection (6 files)
    registry/                      # Node discovery: highlights, search, spec (4 files)
    templates/                     # Template library: fetch, search, cross_ref, coverage (5 files)
    validator/                     # Validation engine: rules, engine, api_nodes (5 files)
    composer/                      # Workflow composition: graph, scaffold, layout (6 files)
    document/                      # Doc generation: metadata, notion, orchestrator (5 files)
  templates/                       # 4 delivered templates (workflow.json + index.json + submission.md + build.py)
  tests/                           # 11 test files + fixtures + conftest
  data/                            # Static data (core_nodes.json, guidelines.json, api_nodes.json, cache/)
  scripts/                         # Maintenance scripts (extract/update core nodes)
  setup.sh / setup.ps1             # Cross-platform setup
  pyproject.toml                   # Package definition
  README.md                        # Current docs
  CLAUDE.md                        # Agent instructions (22.5 KB)
  COMPAT-FIX.md                    # macOS compatibility guide
  comfyui_template_agent.egg-info/ # Build artifact (should be gitignored)
```

### What Needs to Change for Public Release

| Area | Current State | Required State | Effort |
|------|--------------|----------------|--------|
| Git remote | `aramintak/comfyui-template-agent` | `alvdansen/comfyui-template-agent` | Low |
| LICENSE | Missing | MIT (matches alvdansen org convention) | Low |
| `.gitignore` | Missing `.venv/`, has egg-info tracked | Add `.venv/`, `*.egg-info/` | Low |
| `pyproject.toml` | version 0.1.0, no license field | version 1.0.0, add license per PEP 639 | Low |
| README | Internal-facing, references comfy-tip | Public-facing, standalone narrative | Medium |
| CLAUDE.md | Bloated (22.5 KB), internal references | Trimmed for public consumption | Medium |
| Planning artifacts | `.planning/` contains all GSD history | Keep in repo (valuable context), but add to `.gitignore` for clean clone | Low |
| comfy-tip references | 40+ references in planning docs, 2 in public-facing files | Remove from README, CLAUDE.md; planning docs are historical | Low |
| `COMPAT-FIX.md` | Internal dev guide | Move to `docs/` or remove (fixes already applied) | Low |
| `egg-info/` | Tracked in git | Add to `.gitignore`, remove from tracking | Low |
| CI/CD | None | GitHub Actions: test on push/PR | Medium |
| `setup.ps1` | Uses bare `pip` (not venv-aware) | Add venv creation to match `setup.sh` | Low |

## Recommended Architecture for Public Release

### Repository Structure (Target State)

```
comfyui-template-agent/
  .claude/
    skills/
      comfy-compose/               # SKILL.md + gotchas.md
      comfy-discover/              # SKILL.md + gotchas.md
      comfy-document/              # SKILL.md + gotchas.md
      comfy-flow/                  # SKILL.md + gotchas.md
      comfy-template-audit/        # SKILL.md + gotchas.md
      comfy-validate/              # SKILL.md + gotchas.md
  .github/
    workflows/
      test.yml                     # NEW: pytest on push/PR
    ISSUE_TEMPLATE/
      bug_report.md                # NEW: standard bug template
      feature_request.md           # NEW: standard feature template
  src/                             # UNCHANGED — Python modules
    shared/
    registry/
    templates/
    validator/
    composer/
    document/
  templates/                       # UNCHANGED — 4 delivered templates
    florence2-vision-ai/
    gguf-quantized-txt2img/
    impact-pack-face-detailer/
    melbandroformer-audio-separation/
  tests/                           # UNCHANGED — test suite
    fixtures/
    conftest.py
    test_*.py
  data/                            # UNCHANGED — static data
    core_nodes.json
    guidelines.json
    api_nodes.json
  scripts/                         # UNCHANGED — maintenance scripts
  docs/                            # NEW: supplementary documentation
    compatibility.md               # Moved from COMPAT-FIX.md
  LICENSE                          # NEW: MIT license
  README.md                        # REWRITTEN: public-facing
  CLAUDE.md                        # TRIMMED: remove internal references
  pyproject.toml                   # UPDATED: version, license, URLs
  setup.sh                         # UPDATED: minor cleanup
  setup.ps1                        # UPDATED: add venv support
  .gitignore                       # UPDATED: add missing entries
```

### What Stays, What Goes, What Changes

**Keep as-is (no changes):**
- `src/` — All 6 Python modules. Code is clean, tested, production-ready.
- `templates/` — All 4 templates with their build scripts, workflow JSON, index.json, and submission docs.
- `tests/` — Full test suite with fixtures.
- `data/` — Static data files (core_nodes.json, guidelines.json, api_nodes.json).
- `scripts/` — Maintenance scripts for core node extraction.
- `.claude/skills/` — All 6 skill definitions.

**Remove from git tracking (add to .gitignore):**
- `comfyui_template_agent.egg-info/` — Build artifact, should never be tracked.
- `.venv/` — Already gitignored but worth verifying.
- `data/cache/` — Already gitignored, confirmed.

**Modify:**
- `pyproject.toml` — Bump version to 1.0.0, add license = "MIT", add project URLs (homepage, repository, issues).
- `README.md` — Rewrite for public audience. Remove comfy-tip references. Add badge for CI. Structure: hero description, quick start, skills table, architecture diagram (ASCII), CLI reference, contributing, license.
- `CLAUDE.md` — Remove comfy-tip references from constraints section. Remove Windows file paths (C:/Users/minta/...). Trim to essential agent instructions.
- `.gitignore` — Add `*.egg-info/` entry (currently there but `comfyui_template_agent.egg-info/` was committed before the rule existed). Verify `.venv/` is present.
- `setup.ps1` — Add venv creation/activation to match `setup.sh` quality.

**Add (new files):**
- `LICENSE` — MIT license text (matches alvdansen org convention per `flimmer-trainer`).
- `.github/workflows/test.yml` — GitHub Actions CI.
- `docs/compatibility.md` — Relocated from `COMPAT-FIX.md`.

**Decision: .planning/ directory**
Keep `.planning/` in the repository. It contains valuable architectural context and decision history. Do NOT gitignore it. Public consumers benefit from understanding the design decisions. The GSD artifacts serve as project documentation, not private notes.

### Component Boundaries (Unchanged)

The existing architecture is well-bounded and does not need restructuring:

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| `src/shared/` | HTTP client, caching, config, format detection | All other modules (dependency) |
| `src/registry/` | Node discovery from api.comfy.org | `shared/` for HTTP and caching |
| `src/templates/` | Template library from GitHub workflow_templates | `shared/` for HTTP and caching |
| `src/validator/` | Workflow validation against 12 rules | `data/` for guidelines, api_nodes, core_nodes |
| `src/composer/` | Workflow graph construction and layout | `validator/` for inline validation |
| `src/document/` | Metadata and docs generation | `validator/` for validation state |
| `.claude/skills/` | Claude Code skill interface | `src/` modules via CLI (`python -m`) |

Data flow remains the same:
```
User (Claude Code) --> Skill (SKILL.md) --> CLI (python -m src.module.script) --> Python Module --> External API
                                                                                                    |
                                                                                           api.comfy.org (registry)
                                                                                           github.com (templates)
                                                                                           ComfyUI MCP (compose/flow)
```

## Presentation Assets Architecture

### Decision: Separate Directory, Same Repo

Presentation assets live in a `presentation/` directory at the repo root. This keeps the deliverable self-contained (one repo = everything about this project) while maintaining clear separation from the toolkit code.

**Why same repo (not separate):**
- The presentation IS about this codebase. Co-locating makes the repo a complete package.
- Comfy devs cloning the repo get the full story: code + docs + presentation.
- Avoids cross-repo dependency management for a one-time deliverable.
- Single URL to share with the Comfy team.

**Why not in `docs/`:**
- `docs/` is for user-facing documentation (install guides, compatibility).
- Presentation assets are a specific deliverable with their own toolchain (Manim, PowerPoint, Excalidraw).

### Presentation Directory Structure

```
presentation/
  README.md                        # How to render/rebuild assets, Hermes setup
  manim/
    scenes/
      pipeline_flow.py             # Manim scene: discover -> compose -> validate -> document flow
      architecture_overview.py     # Manim scene: module dependency graph
      template_showcase.py         # Manim scene: 4 template workflow visualizations
    media/                         # Rendered output (committed as .mp4/.gif)
      pipeline_flow.mp4
      architecture_overview.mp4
      template_showcase.mp4
  slides/
    comfyui-template-agent.pptx    # PowerPoint deck
    speaker_notes.md               # Speaker notes / async narration script
  diagrams/
    architecture.excalidraw        # Excalidraw source
    architecture.svg               # Exported SVG for embedding
    workflow-pipeline.excalidraw
    workflow-pipeline.svg
  demo/
    walkthrough.md                 # Script for recorded demo
    demo_commands.sh               # Exact commands to run in demo
```

### Hermes Server Role

Hermes (Ubuntu 24.04, RTX 4090) renders the presentation assets. The workflow:

1. **Development:** Write Manim scenes and diagram sources on the Mac, push to repo.
2. **Rendering:** SSH to Hermes, pull repo, run `manim render` for scenes. The RTX 4090 handles Manim rendering efficiently.
3. **Output:** Rendered .mp4/.gif files committed back to `presentation/manim/media/`.
4. **PowerPoint:** Generated on Hermes using the PowerPoint skill, committed to `presentation/slides/`.
5. **Excalidraw:** Created on Hermes using the Excalidraw skill, SVG exports committed.

This is a one-directional build flow. Presentation assets are generated artifacts, not continuously updated. Commit the rendered outputs so consumers do not need Hermes or Manim installed.

### What Goes in the Presentation

| Asset | Content | Tool | Purpose |
|-------|---------|------|---------|
| Pipeline flow animation | Animated 5-phase flow (discover -> ideate -> compose -> validate -> document) | Manim CE 0.20.1 | Show the guided workflow |
| Architecture diagram | Module dependency graph with data flow arrows | Excalidraw | Technical architecture overview |
| Template showcase | Side-by-side of 4 template workflow graphs | Manim CE 0.20.1 | Demonstrate deliverables |
| Slide deck | 15-20 slides: problem, solution, architecture, demo, metrics | PowerPoint | Main presentation |
| Demo walkthrough | Recorded terminal session using comfy-flow | Screen recording | Show the toolkit in action |

## CI/CD Architecture

### GitHub Actions: Test Workflow

A single workflow file that runs on push to master and on PRs:

```yaml
name: Tests
on:
  push:
    branches: [master]
    paths:
      - 'src/**'
      - 'tests/**'
      - 'pyproject.toml'
  pull_request:
    branches: [master]
    paths:
      - 'src/**'
      - 'tests/**'
      - 'pyproject.toml'

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12', '3.13']

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e ".[dev]"

      - name: Lint
        run: ruff check src/

      - name: Test
        run: pytest tests/ -q --tb=short
```

**Design decisions:**
- **Path filtering:** Only triggers when Python source, tests, or dependencies change. Presentation asset commits do not trigger CI.
- **Matrix:** Python 3.12 and 3.13. The project requires 3.12+, and 3.13 is the current stable.
- **No macOS runner:** Tests are pure Python with mocked HTTP (httpx). No platform-specific behavior to test. Ubuntu is cheaper and faster.
- **No Windows runner:** Same reasoning. The setup.ps1 script is manual-install territory.
- **Lint + test in one job:** Small enough project that splitting into parallel jobs adds overhead without benefit.

### What CI Does NOT Cover (And Why)

| Not Covered | Reason |
|-------------|--------|
| Template build scripts (`build.py`) | These require MCP server access for spec fetching. They are one-time build scripts, not runtime code. |
| Presentation rendering | Requires Manim + GPU. Handled manually on Hermes. |
| Integration tests with live APIs | Tests use mocked HTTP responses. Live API tests are manual. |
| PyPI publishing | This is a Claude Code skills repo installed via `git clone + setup.sh`, not a pip-installable library. |

### Future CI Enhancement (Not v3.0)

If the repo gains external contributors, add:
- `claude-code-action` for automated PR review (Anthropic's official GitHub Action).
- `dependabot.yml` for dependency updates (matches flimmer-trainer convention).

## Migration Plan: aramintak -> alvdansen

### Step 1: Create repo on alvdansen org

```bash
gh repo create alvdansen/comfyui-template-agent --public --description "Claude Code agent toolkit for ComfyUI template creation"
```

### Step 2: Update remote and push

```bash
git remote set-url origin https://github.com/alvdansen/comfyui-template-agent.git
git push -u origin master
```

### Step 3: Update internal references

Files with `aramintak` references:
- `.git/config` (handled by remote set-url)
- No source code references found

### Step 4: Archive the original

Either delete `aramintak/comfyui-template-agent` or mark it archived with a redirect note in the README.

## Patterns to Follow

### Pattern 1: Skill as CLI Wrapper
**What:** Each Claude Code skill is a thin SKILL.md that invokes `python -m src.module.script` with CLI arguments.
**When:** Always. Skills are the interface layer; Python modules are the implementation layer.
**Why this matters for v3.0:** Public consumers install skills via symlink (setup.sh). The Python package must be editable-installed for `python -m` to resolve. The setup script handles this correctly.

### Pattern 2: Build Scripts as Template Reproducibility
**What:** Each template includes a `build.py` that reconstructs the workflow from node specs using the composer module.
**When:** Every template. The build script serves as both documentation and reproducibility.
**Why this matters for v3.0:** Build scripts demonstrate the toolkit's value. They show exactly how each template was composed programmatically. Public consumers can study these as usage examples.

### Pattern 3: Static Data Over Live Fetching
**What:** Core node lists, guidelines, and API node data are committed as JSON in `data/`. Scripts in `scripts/` refresh them periodically.
**When:** For any data that changes slowly (node lists, guidelines).
**Why this matters for v3.0:** New users can run the toolkit offline (except for registry browsing and template fetching). No first-run download step for static data.

## Anti-Patterns to Avoid

### Anti-Pattern: Splitting Skills Into a Separate Repo
**What:** Moving `.claude/skills/` into its own repo for "cleaner distribution."
**Why bad:** Skills depend on the Python package being editable-installed. Splitting creates a cross-repo dependency that breaks the setup.sh symlink flow.
**Instead:** Keep everything in one repo. The setup script handles both package install and skill symlinking.

### Anti-Pattern: Gitignoring .planning/
**What:** Hiding the planning artifacts from the public repo.
**Why bad:** The planning directory contains architecture decisions, research findings, and phase summaries that explain WHY the code is structured the way it is. This is valuable documentation.
**Instead:** Keep `.planning/` committed. It demonstrates the GSD methodology and provides architectural context.

### Anti-Pattern: Rendering Presentation Assets in CI
**What:** Adding Manim rendering to the GitHub Actions pipeline.
**Why bad:** Manim requires ffmpeg, LaTeX, and ideally GPU access for fast rendering. CI runners lack GPU. Rendering is slow (~minutes per scene on CPU). Scenes change infrequently.
**Instead:** Render on Hermes, commit the output. Treat rendered videos/images as artifacts, not build outputs.

### Anti-Pattern: Overpolishing the README
**What:** Turning the README into a comprehensive tutorial with screenshots and animated GIFs.
**Why bad:** This is an internal-to-Comfy deliverable, not a public OSS project seeking community adoption. The audience is Comfy developers who will stress-test and absorb the toolkit.
**Instead:** Clear, factual README: what it does, how to install, skills reference, architecture summary. The presentation deck handles the "sell."

## Build Order for v3.0 Changes

Dependencies flow top-to-bottom. Items at the same level can be parallelized.

```
Phase 1: Repo Hygiene (no code changes, no dependencies)
  |- Add LICENSE (MIT)
  |- Update .gitignore (add *.egg-info/, verify .venv/)
  |- Remove comfyui_template_agent.egg-info/ from git tracking
  |- Update pyproject.toml (version 1.0.0, license, URLs)

Phase 2: Content Cleanup (depends on Phase 1 for version)
  |- Rewrite README.md for public audience
  |- Trim CLAUDE.md (remove comfy-tip refs, Windows paths)
  |- Move COMPAT-FIX.md to docs/compatibility.md
  |- Update setup.ps1 with venv support

Phase 3: CI/CD Setup (independent of Phase 2, but logically after repo hygiene)
  |- Create .github/workflows/test.yml
  |- Create .github/ISSUE_TEMPLATE/ (optional, low priority)
  |- Verify tests pass in CI environment

Phase 4: Migration (depends on Phases 1-3 being committed)
  |- Create repo on alvdansen org
  |- Push to new remote
  |- Archive aramintak repo

Phase 5: Presentation Assets (independent of Phases 1-4, runs on Hermes)
  |- Create presentation/ directory structure
  |- Write Manim scenes
  |- Write slide deck
  |- Create Excalidraw diagrams
  |- Record demo walkthrough
  |- Commit rendered outputs
```

**Phase ordering rationale:**
- Phases 1-2 must happen before Phase 4 (migration) so the first push to alvdansen is clean.
- Phase 3 can run in parallel with Phase 2 since CI tests the existing code, not the README.
- Phase 5 is fully independent and runs on Hermes while Phases 1-4 happen on the Mac. This is the key parallelism opportunity.

## Scalability Considerations

| Concern | Current (4 templates, 1 user) | At 20 templates | At external contributors |
|---------|------|------|------|
| Test suite speed | ~0.5s (mocked HTTP) | ~1s (more fixtures) | Same (mocked) |
| Setup script | Symlinks 6 skills | Same 6 skills | Same |
| CI cost | ~1 min per run | ~1 min | Add PR review bot |
| Skill maintenance | 6 x (SKILL.md + gotchas.md) | Same 6 skills | Version skill docs |
| Template discovery | Manual `build.py` per template | Consider template registry script | Template submission guidelines |

## Sources

- [alvdansen/flimmer-trainer](https://github.com/alvdansen/flimmer-trainer) -- Alvdansen org conventions: MIT license, .github/workflows/test.yml, CONTRIBUTING.md, CODE_OF_CONDUCT.md (HIGH confidence, direct inspection)
- [GitHub Best Practices for Repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories) -- Repository naming, branch protection (HIGH confidence, official docs)
- [PEP 639 -- License Metadata](https://peps.python.org/pep-0639/) -- pyproject.toml license field format (HIGH confidence, PEP standard)
- [Python Packaging User Guide -- pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) -- Modern pyproject.toml structure (HIGH confidence, official docs)
- [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) -- Official GitHub Actions for Claude Code CI/CD (HIGH confidence, Anthropic official)
- [Claude Code GitHub Actions Docs](https://code.claude.com/docs/en/github-actions) -- CI integration patterns (HIGH confidence, official docs)
- [Manim Community v0.20.1 Docs](https://docs.manim.community/en/stable/) -- Manim project structure and rendering (HIGH confidence, official docs)
- [Gofore -- Best Practices for Forking](https://gofore.com/en/best-practices-for-forking-a-git-repo/) -- Repo migration patterns (MEDIUM confidence, blog post)
