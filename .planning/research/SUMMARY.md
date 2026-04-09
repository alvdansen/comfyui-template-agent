# Project Research Summary

**Project:** ComfyUI Template Agent v3.0 -- Publish & Present
**Domain:** Open-source developer toolkit publishing + async engineering presentation
**Researched:** 2026-04-08
**Confidence:** HIGH

## Executive Summary

The v3.0 milestone transforms an internal Claude Code skills toolkit (6 skills, 6 Python modules, 4 delivered templates) into a public-facing repository under the Alvdansen Labs org, accompanied by async presentation materials for the Comfy-Org Research Phase (Apr 7-17). The existing codebase is architecturally sound and production-tested -- v3.0 is about packaging and presentation, not rewriting. The core toolkit stack (Python 3.12+, httpx, pydantic, pytest, ruff) is unchanged; new technology is limited to CI/CD (GitHub Actions), presentation generation (Manim CE 0.20.1, python-pptx, Excalidraw -- all on Hermes only), and terminal recording (VHS).

The recommended approach is a clean-break publish: create a fresh repository under `alvdansen/comfyui-template-agent` rather than transferring the existing repo, because the 111-commit internal history contains personal identifiers, local machine paths, and comfy-tip heritage references that would require extensive git-filter-repo cleanup. A fresh push with curated history is faster and cleaner. The repo needs foundational files (LICENSE, enriched pyproject.toml, .gitignore fixes), content rewrites (README for external audience, CLAUDE.md trimmed of GSD internals), CI setup (GitHub Actions with ruff + pytest), and a decision on whether to ship or exclude the `.planning/` directory.

The primary risks are: (1) leaking personal data through git history or metadata, (2) the skill symlink installation pattern breaking on fresh machines, and (3) presentation materials (especially Manim renders) bloating the code repository. All are mitigable with the phased approach outlined below. The tightest constraint is the Apr 7-17 Research Phase window -- the presentation materials must ship within that period, which means Hermes rendering should start early and run in parallel with repo cleanup.

## Key Findings

### Recommended Stack

The existing toolkit requires no new dependencies. All v3.0 additions are either repo infrastructure (LICENSE, CI workflow, pyproject.toml fields) or Hermes-only presentation tools that must NOT be added to the project's dependency tree.

**Core technologies (new for v3.0):**
- **GitHub Actions** (checkout@v6, setup-python@v6, ruff-action@v3): CI/CD for lint + test on push/PR -- two parallel jobs, single Python version (3.12), no matrix needed
- **Manim CE 0.20.1** (Hermes only): Animated pipeline/architecture visualizations -- already installed on Hermes, produces MP4/GIF
- **python-pptx 1.0.2** (Hermes only): Programmatic PowerPoint generation for the 10-15 slide async deck
- **Excalidraw JSON** (Hermes only): Hand-drawn architecture diagrams as SVG/PNG -- shared dependency between README and slide deck
- **VHS** (charmbracelet): Scriptable terminal recording via .tape files for demo GIFs -- reproducible, CI-friendly

**Critical boundary:** Manim, python-pptx, and Excalidraw generation run on Hermes only. They must not appear in pyproject.toml. VHS is a Homebrew binary, not a Python dependency.

**Explicitly rejected:** PyPI publishing (git clone is the install path), mkdocs/Sphinx (README is the right doc format for a 6-skill toolkit), Docker (skills need to be in the user's Claude Code environment), multi-version matrix testing (narrow audience, single Python version target).

### Expected Features

**Must have (table stakes for credible public release):**
- LICENSE file (MIT) -- legally required for anyone to use the code
- Polished README with hero section, badges, quick start, architecture diagram
- Demo GIF or terminal recording showing the tool in action (15-30s)
- Complete pyproject.toml metadata (author, license, URLs, classifiers)
- Clean .gitignore and repo hygiene (no .venv, egg-info, internal artifacts)
- CONTRIBUTING.md with dev setup, PR process, code style expectations
- Skill installation that works first try on a fresh machine
- Slide deck (8-12 slides) as the async-skimmable artifact
- Recorded walkthrough (2-5 min) as the main demo deliverable

**Should have (low-effort differentiators):**
- 4 production templates as worked examples (already built -- just add per-template READMEs)
- Quantified results section ("4 templates, 42 requirements, 5.5M+ combined node pack downloads")
- AGENTS.md (2026 Linux Foundation standard for AI agent repo context)
- CI/CD with GitHub Actions green badge in README
- CHANGELOG.md (retroactive from git history)

**Defer (stretch / post-v3.0):**
- Manim pipeline animation -- attempt ONE animation on Hermes; do not block the milestone
- Narrated architecture deep-dive (separate video)
- Skill creation guide for external authors
- Anthropic marketplace submission
- Notion API integration (explicitly out of scope since v1)

### Architecture Approach

The existing architecture is well-bounded and does not need restructuring. Six Python modules (`shared/`, `registry/`, `templates/`, `validator/`, `composer/`, `document/`) communicate through clean interfaces with `shared/` as the common dependency. Six Claude Code skills in `.claude/skills/` serve as the user-facing interface layer, invoking Python modules via `python -m src.module.script`. The v3.0 changes are additive: new `.github/workflows/` for CI, new `presentation/` directory for Hermes-generated assets, enriched pyproject.toml, and new repo health files (LICENSE, CONTRIBUTING.md, issue templates).

**Major structural decisions:**
1. **Fresh repo under alvdansen org** -- clean-break publish, no history baggage
2. **Presentation assets in same repo** (`presentation/` directory) -- keeps the deliverable self-contained, but Manim source only; rendered videos hosted externally or via Git LFS
3. **.planning/ directory** -- conflicting recommendations (ARCHITECTURE says keep, PITFALLS says exclude); recommendation: **exclude from public repo** via .gitignore since the 784 KB of GSD internals adds confusion without value for external consumers
4. **CI: single workflow, two parallel jobs** (lint + test), path-filtered to only trigger on src/tests/pyproject.toml changes

### Critical Pitfalls

1. **Git history leaks personal data** -- 111 commits contain personal emails, local hostnames, Windows paths from comfy-tip heritage. Use fresh repo approach (do not attempt git-filter-repo rewriting). Scan with gitleaks before any public push.
2. **No LICENSE file exists** -- Code is legally "all rights reserved" without one. Add MIT (or Apache 2.0 for patent protection) BEFORE the first public commit. This is a hard blocker.
3. **Skill symlink installation breaks on fresh machines** -- Absolute symlinks tied to filesystem layout; break if repo moves. Document the constraint, test on a clean machine, consider Claude Code's native project skill discovery as an alternative.
4. **Presentation materials bloat the repo** -- A single 1080p 2-minute Manim animation is 50-200 MB. Keep Manim source (.py) in repo, .gitignore rendered media, host videos externally (YouTube/Vimeo) or use a separate presentation repo.
5. **CLAUDE.md contains GSD internals** -- External contributors will be confused by `/gsd:quick`, developer profile placeholders, and 22.5 KB of template node documentation. Strip to essential agent instructions before publishing.

## Implications for Roadmap

Based on combined research, the v3.0 work divides into 5 phases with a clear dependency chain. Phases 3 and 5 can run in parallel with other work since they target different machines (Hermes vs local).

### Phase 1: Repo Foundation
**Rationale:** These are zero-dependency prerequisites that must be done before any public-facing commit. License is a legal blocker; .gitignore and pyproject.toml prevent embarrassing artifacts from leaking.
**Delivers:** LICENSE file, enriched pyproject.toml (version 3.0.0, license, authors, URLs, classifiers), cleaned .gitignore (.venv/, *.egg-info/), egg-info removal from tracking
**Addresses:** Table stakes (LICENSE, pyproject.toml metadata, repo hygiene)
**Avoids:** Pitfall 3 (no license), Pitfall 6 (missing metadata), Pitfall 11 (.venv leakage)

### Phase 2: Content Cleanup
**Rationale:** Depends on Phase 1 for version number. All content must be rewritten for an external audience before the repo goes public. This is the highest-effort phase.
**Delivers:** Rewritten README.md (hero, badges, quick start, architecture diagram, results), trimmed CLAUDE.md (no GSD, no comfy-tip, no developer profile), CONTRIBUTING.md, AGENTS.md, COMPAT-FIX.md relocated to docs/, standardized SKILL.md files, per-template READMEs
**Addresses:** Table stakes (polished README, CONTRIBUTING.md, skill documentation), differentiators (AGENTS.md, template showcases, metrics section)
**Avoids:** Pitfall 5 (comfy-tip references), Pitfall 9 (README not rewritten), Pitfall 15 (CLAUDE.md internals)

### Phase 3: Presentation Materials (Hermes -- parallel with Phase 2)
**Rationale:** Hermes rendering is independent of local repo cleanup. Starting early exploits the parallelism opportunity and de-risks Manim rendering issues. Test ONE render first before building all animations.
**Delivers:** Excalidraw architecture diagram (SVG/PNG -- shared dep for README and slides), slide deck (8-12 slides via python-pptx), Manim pipeline animation (stretch), demo walkthrough script
**Uses:** Manim CE 0.20.1, python-pptx 1.0.2, Excalidraw JSON generation (all Hermes-only)
**Avoids:** Pitfall 7 (Manim headless rendering failures -- test first), Pitfall 8 (binary bloat -- source only in repo), Pitfall 13 (animation pacing)

### Phase 4: CI/CD and Final Polish
**Rationale:** CI depends on repo hygiene (Phase 1) and content being stable (Phase 2). Adding CI last means the green badge is earned, not aspirational.
**Delivers:** .github/workflows/ci.yml (lint + test), issue templates, demo GIF (VHS recording of polished /comfy-flow), CI badge added to README
**Addresses:** Differentiator (CI/CD with green badge), table stakes (demo GIF)
**Avoids:** Pitfall 4 (untested skill installation -- CI validates the install path)

### Phase 5: Publish and Handoff
**Rationale:** Depends on all prior phases. Fresh repo creation under alvdansen org, push curated state, verify everything works from a clean clone.
**Delivers:** Public repo at alvdansen/comfyui-template-agent, v3.0.0 git tag, recorded walkthrough (2-5 min -- must be LAST since it records the polished state), presentation link shared with Comfy-Org
**Addresses:** Migration to org, Comfy-Org handoff
**Avoids:** Pitfall 1 (git history leaks -- fresh repo), Pitfall 10 (wrong remote), Pitfall 14 (unclear handoff expectations)

### Phase Ordering Rationale

- Phase 1 before Phase 2: Version number and license must exist before README references them.
- Phase 3 parallel with Phase 2: Different machines (Hermes vs local), no dependency. Architecture diagram from Phase 3 feeds into README in Phase 2, but the diagram can be created first and embedded later.
- Phase 4 after Phase 2: CI tests the final content state; demo GIF records the polished experience.
- Phase 5 strictly last: The recorded walkthrough captures the finished product; the fresh repo push must include all prior work.

### Research Flags

**Phases needing deeper research during planning:**
- **Phase 3 (Presentation Materials):** Manim rendering on Hermes needs validation before committing to multiple animations. Test one scene first. Excalidraw MCP skill maturity uncertain -- may need manual JSON authoring.
- **Phase 5 (Publish and Handoff):** Comfy-Org's specific absorption expectations are undefined. Clarify before finalizing: do they want to fork, transfer, or just evaluate?

**Phases with standard patterns (skip research):**
- **Phase 1 (Repo Foundation):** LICENSE, pyproject.toml, .gitignore -- fully documented patterns, no unknowns.
- **Phase 4 (CI/CD):** GitHub Actions workflow is templated in STACK.md, ready to copy.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified against PyPI/GitHub. No novel technology -- CI, Manim, python-pptx are mature. Clear boundary between local and Hermes deps. |
| Features | MEDIUM-HIGH | Repo publishing conventions well-established from 100K+ star repos. Async demo best practices from multiple sources but engagement stats from single source. |
| Architecture | HIGH | Existing codebase fully analyzed (3,856 LOC, 6 modules). No restructuring needed. Build order validated against dependency chain. |
| Pitfalls | HIGH | 15 pitfalls identified with concrete detection and prevention steps. Git history leak and license issues verified against actual repo state. Manim rendering risks sourced from GitHub issues. |

**Overall confidence:** HIGH

### Gaps to Address

- **Comfy-Org handoff expectations:** "Stress-test and absorb" is vague. Clarify what they want to receive (code, skills, full toolkit?) and how they will evaluate it. Consider including a HANDOFF.md with specific test scenarios.
- **License choice (MIT vs Apache 2.0):** STACK.md recommends MIT, PITFALLS.md recommends Apache 2.0 for patent protection. Both are compatible with Comfy-Org's GPL-3.0. Decision needed before Phase 1.
- **.planning/ directory disposition:** ARCHITECTURE.md says keep (valuable context), PITFALLS.md says exclude (confusing for external users). Recommendation: exclude via .gitignore, but archive locally. The planning artifacts served development; external consumers need the README, not GSD phase logs.
- **Manim scope:** Whether to attempt Manim animations at all depends on a test render succeeding on Hermes. If the first render fails or takes excessive iteration, fall back to static Excalidraw diagrams entirely.
- **Fresh history vs rewritten history:** Strong recommendation for fresh repo, but this means losing 111 commits of development history. Acceptable since no external consumers exist yet.

## Sources

### Primary (HIGH confidence)
- alvdansen/flimmer-trainer -- Alvdansen org conventions (MIT license, CI, CONTRIBUTING.md)
- GitHub Actions official repos (checkout@v6, setup-python@v6, ruff-action@v3)
- Python Packaging User Guide -- pyproject.toml metadata fields
- Manim Community v0.20.1 official docs -- Scene patterns, rendering flags
- Gitleaks -- secret scanning methodology
- git-filter-repo -- history rewriting (if needed)
- ComfyUI workflow_templates repo -- template format conventions
- python-pptx 1.0.2 on PyPI -- API patterns
- VHS by Charmbracelet -- terminal recording
- Claude Code Skills Documentation -- skill format and distribution

### Secondary (MEDIUM confidence)
- CrewAI (100K+ stars), Anthropic skills repo (113K stars) -- README/publishing conventions
- AGENTS.md standard (Linux Foundation 2026) -- emerging standard for AI agent repos
- Excalidraw MCP integration -- AI-assisted diagram generation
- Async demo best practices (Loom, DEV Community, Navattic)
- Claude Code skills distribution patterns (community guides)

### Tertiary (LOW confidence)
- Interactive demo engagement improvement stats (Navattic, single source)
- Generative Manim AI code generation maturity (blog post, unverified)

---
*Research completed: 2026-04-08*
*Ready for roadmap: yes*
