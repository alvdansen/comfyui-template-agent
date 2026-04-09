# Feature Landscape: v3.0 Publish & Present

**Domain:** Open-source AI agent toolkit publishing + async engineering demo creation
**Researched:** 2026-04-08
**Overall confidence:** MEDIUM-HIGH

---

## Domain A: Open-Source Repo Publishing

### Table Stakes

Features developers expect when evaluating an open-source AI agent toolkit. Missing = repo looks amateur or abandoned.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Polished README with hero section** | First thing visitors see. Sets tone within 5 seconds. Best repos (CrewAI at 100K+ stars, Anthropic skills at 113K stars) open with centered logo/banner + shields.io badges + one-line value prop. Current README is functional but plain text only. | Medium | Need: banner image, badges (Python version, license, tests passing), one-liner tagline. CrewAI pattern: centered logo, then badges row, then "Why X?" section. |
| **Demo GIF or terminal recording** | Developers want to see the tool in action before reading. 90%+ of high-star AI repos include animated demos. Current README has zero visual content. | Medium | Use VHS (Charm.sh, scriptable, CI-friendly) or asciinema+agg to record a `/comfy-flow` guided session. Target: 15-30s GIF showing discovery through validation. |
| **Quick Start section (under 60 seconds)** | Developers expect copy-paste install + first visible result. Current README has install but no "see it work in 30 seconds" moment. | Low | 3-step quick start: clone, `./setup.sh`, first command with expected output snippet. Show what success looks like. |
| **LICENSE file** | No LICENSE = legally ambiguous = nobody will fork or use it. Standard open-source requirement. Currently missing from repo. | Low | MIT license. Matches CrewAI, most Claude skills repos, and Anthropic's own examples. |
| **Skill installation that works first try** | setup.sh exists but symlinks can fail silently on some systems. No Windows parity (setup.ps1 exists but less tested). Anthropic's official skills repo uses marketplace install pattern. | Medium | End-to-end test setup.sh on clean machine. Add troubleshooting section. Document the symlink approach vs marketplace if available. |
| **pyproject.toml with complete metadata** | Package metadata (author, homepage, repository, classifiers) must be filled for credible publishing. Current pyproject.toml is minimal -- lacks URLs, keywords, author info. | Low | Add: homepage URL, repository URL, Alvdansen Labs author, Python classifiers, "comfyui" and "claude-code" keywords. |
| **CONTRIBUTING.md** | Standard file that signals the project welcomes contributions. Current README has only 3 lines about contributing. | Low | Coding standards (Pydantic models, httpx, DiskCache pattern), PR process, skill creation guide, test expectations, ruff check requirement. |
| **Clean .gitignore and repo hygiene** | No .venv, __pycache__, .egg-info visible. Currently .venv/ and egg-info/ show as untracked in git status. | Low | Verify .gitignore covers all build artifacts. Run cleanup before publish. Ensure no committed secrets or large files. |
| **Standardized skill documentation** | Each of the 6 skills needs consistent description, example invocations, gotchas. SKILL.md files exist but vary in depth. | Medium | Standardize all 6 SKILL.md files with: trigger, capabilities, 2-3 example sessions, known gotchas section. |
| **Architecture diagram** | Visual showing how 6 skills + Python modules + external APIs connect. Text-only architecture list in current README is insufficient for a toolkit this complex. | Medium | Excalidraw diagram exported as SVG/PNG embedded in README. Three layers: Skills -> Python modules -> External APIs (Registry, GitHub, ComfyUI MCP). |

### Differentiators

Features that set this repo apart. Not expected, but create a "this is professional" impression.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **4 production templates as worked examples** | Most AI agent repos ship toy examples. This has 4 real templates that went through the full skill chain and target high-download node packs. Evidence of the toolkit working at production scale. | Low | Already built in templates/. Just add a README per template explaining what was created, which skills were used, and what the output looks like. |
| **Quantified results section** | "42 requirements fulfilled", "4 templates shipped in 2 milestones", "0.5s test suite", "covers 5.5M+ combined node pack downloads". Rare for agent toolkit repos to show measurable outcomes. | Low | Add a "Results" or "What This Built" section to README with concrete numbers from PROJECT.md. |
| **Video walkthrough embedded in README** | 2-5 min Loom or YouTube video linked from README. CrewAI does this with clickable YouTube thumbnail images. Only ~10% of Claude Code skill repos include video. | Medium | Record after all other polish is done. Embed as clickable thumbnail linking to video. Keep under 5 min. |
| **AGENTS.md file** | Emerging 2026 standard backed by the Linux Foundation for giving AI coding agents project context. Already have CLAUDE.md; adding AGENTS.md signals forward-thinking awareness and makes the repo AI-agent-friendly. | Low | Create AGENTS.md following the open standard spec alongside existing CLAUDE.md. |
| **CI/CD with GitHub Actions** | Automated pytest + ruff on PR, green badge in README. Standard for polished repos but most Claude skills repos skip this. | Medium | Simple workflow: checkout, setup Python 3.12, pip install, pytest, ruff check. Add passing badge to README hero section. |
| **CHANGELOG.md** | Tracks v1.0, v2.0, v3.0 milestones with what shipped in each. Shows active development trajectory and scope. | Low | Create retroactively from git history + PROJECT.md validated requirements. |
| **Skill creation guide** | Teaching others how to build their own comfy-* skills. Most Claude skills repos are consume-only. Showing the SKILL.md + gotchas.md authoring pattern is valuable. | Medium | Document the skill creation pattern with a template. Could be a section in CONTRIBUTING.md or standalone doc. |

### Anti-Features

Features to explicitly NOT build for v3.0.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **PyPI package distribution** | Unnecessary for a Claude Code skills toolkit. Nobody pip-installs agent skills -- they clone repos and run setup. Packaging adds maintenance burden with no user benefit. | Keep git clone + setup.sh as the install path. |
| **Web UI or dashboard** | Out of scope entirely. This is a CLI/agent toolkit, not a web app. Adding UI would distract from core value and create maintenance burden. | Skills run inside Claude Code. That IS the interface. |
| **Docker containerization** | Overkill for a Python skills toolkit. Skills need to be in the user's Claude Code environment, not isolated in a container. | setup.sh + venv is the correct abstraction level for this use case. |
| **Anthropic marketplace submission** | The skills marketplace is still maturing. Submitting now adds process overhead and version lock-in risk during a research phase. | Document marketplace install path if available, but primary path stays git clone + setup.sh. |
| **Multi-language support / i18n** | English-only is correct for a developer toolkit targeting the Comfy Org engineering team. i18n adds maintenance for no audience. | Keep English throughout. |
| **Notion API integration** | Explicitly out of scope since v1. Markdown output + human paste is the validated workflow per PROJECT.md. | Continue existing markdown generation. |
| **Template PR auto-submission** | Creating PRs against Comfy-Org/workflow_templates is a separate effort per PROJECT.md. Bundling it would complicate the publish boundary. | Keep templates as examples. Submitting to workflow_templates is a separate workflow. |
| **Exhaustive test coverage push** | Current tests run in 0.5s and cover the critical paths. Chasing 90%+ coverage for a research-phase toolkit adds effort without proportional value. | Keep existing test suite healthy. Add tests only for new code. |

---

## Domain B: Async Engineering Demo / Presentation

### Table Stakes

What the Comfy Agent Research Phase audience needs. Missing = they cannot evaluate the toolkit properly.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Recorded screen walkthrough (2-5 min)** | Core async deliverable. Comfy Org team needs to see the tool working end-to-end. Research consensus: open with the problem, walk through the solution, close with next step. Engagement drops sharply after 5 min. | Medium | Record with Loom or OBS. Show a real `/comfy-flow` session creating a template from scratch. Problem (30s) -> Solution demo (2-3 min) -> Results/next steps (30s). |
| **Architecture overview diagram** | Viewers need a mental model before diving into details. Excalidraw hand-drawn style preferred -- encourages discussion over false precision. | Medium | Three layers: Skills (6 skills) -> Python modules (6 packages) -> External APIs (Registry, GitHub, MCP). Export as PNG for slides, SVG for README. |
| **Problem statement (why this exists)** | Without context, the demo is just "look what I built." Must establish: what was manual, how painful, what this automates. | Low | 1-2 slides or 30s of video. "Template creators manually hunt for nodes, trial-and-error workflow composition, hand-write JSON metadata. This toolkit automates the entire pipeline." |
| **Slide deck (8-12 slides)** | Async viewers need a self-contained skimmable artifact. Not everyone watches video. Slides serve as the "skim in 2 minutes" version. | Medium | Structure: Problem (1) -> Solution overview (1) -> Architecture (1) -> Skill walkthrough (2-3) -> Demo highlights (1-2) -> Metrics/templates shipped (1) -> What's next (1). |
| **Concrete metrics and evidence** | Engineering audience wants proof, not just feature lists. "4 templates across 4 domains" and "42 requirements in 2 milestones" are compelling data points. | Low | Include in both slides and video. If possible, compare: estimated manual template creation time vs agent-assisted time. |

### Differentiators

Features that make the demo memorable and distinguish it from a routine engineering update.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Manim workflow pipeline animation** | Animated visualization of the discover -> audit -> validate -> compose -> document pipeline. 3Blue1Brown-style animations are attention-grabbing and clarify sequential flows better than static diagrams. | High | Manim Community v0.20.x. Create Scene classes showing nodes appearing, connections forming, data flowing through pipeline stages. Hermes can generate Manim Python code from descriptions. Target: 30-60s animation for the pipeline overview. |
| **Before/after comparison** | Side-by-side: manual template creation (scattered docs, trial-and-error, hand-written JSON) vs agent-guided (structured phases, validated output, generated metadata). Visual contrast is powerful for async audiences. | Low | 1 slide or short video segment. Split-screen showing the pain vs the solution. |
| **Template showcase gallery** | Visual grid showing all 4 templates with ComfyUI workflow graph screenshots. Demonstrates breadth (vision, image gen, post-processing, audio) and production quality. | Low | Can be a slide in the deck or a section in README. Screenshot each template's workflow graph from ComfyUI UI. |
| **"Try it yourself" interactive link** | Instead of passive watching, viewers can clone the repo and try the skills. Research shows async demos with interactivity get significantly higher engagement. | Low | Clear "Try it yourself" CTA in slides and video linking to the polished GitHub repo with quick start instructions. |
| **Chaptered/timestamped video** | Async videos over 3 min need chapters so viewers can jump to relevant sections. Both Loom and YouTube support timestamps. | Low | Add timestamps in video description: 0:00 Problem, 0:30 Architecture, 1:00 Live demo, 3:00 Results, 4:00 Next steps. |
| **Narrated architecture deep-dive (separate)** | For the subset of the audience that wants to understand internals. Separate from the main demo. Focus on validation engine and type-safe composer as most technically interesting. | Medium | Optional. Only record if time allows after main deliverables ship. 5-10 min max. |

### Anti-Features for Demo

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Live presentation / roundtable** | Explicitly out of scope per PROJECT.md. Async delivery is the constraint for the Research Phase (Apr 7-17). | Record everything. Provide async-friendly artifacts: slides + video + repo link. |
| **Feature-complete product walkthrough** | Engineering research demo, not a product launch. Walking through every feature dilutes the core message. | Show ONE complete `/comfy-flow` session end-to-end. Mention other 5 skills exist. Let the repo speak for depth. |
| **Over-produced marketing video** | Engineering audience expects authenticity. Over-polished videos feel like sales pitches and undermine technical credibility. | Screen recording with optional face cam (Loom style). Clean but not cinematic. Technical substance over production value. |
| **Line-by-line code walkthrough** | Too long, too detailed, loses async audience. Architecture diagram + one interesting module is enough. | Show architecture diagram, then zoom into validator or composer as the "technically interesting bit" if doing a deep-dive. |
| **Manim animations for every concept** | Manim is high-effort per animation. Animating what a static diagram explains equally well wastes time. | Reserve Manim for the one thing that benefits most from animation: the pipeline flow. Use static Excalidraw for architecture, component boundaries, data flow. |
| **Custom slide template design** | Time spent on slide aesthetics beyond basic readability is wasted for an engineering audience. | Use a clean default template (dark theme, large text, code-friendly). Content over cosmetics. |

---

## Feature Dependencies

```
Foundation (no dependencies, do first):
  LICENSE file
  pyproject.toml metadata
  .gitignore cleanup
  CHANGELOG.md

Content creation (parallel tracks):
  Track A: README overhaul
    ├── Architecture diagram (Excalidraw) ── needed by README AND slides
    ├── Demo GIF (VHS/asciinema) ── requires tested setup.sh working
    ├── Quick Start section ── requires tested setup.sh
    ├── Badges ── requires CI/CD GitHub Action + LICENSE
    ├── Results/metrics section
    └── Template showcase READMEs per template/

  Track B: Presentation materials
    ├── Slide deck ── uses architecture diagram from Track A
    ├── Manim pipeline animation ── independent, high effort
    └── Recorded walkthrough ── MUST BE LAST (records polished state)

  Track C: Community files
    ├── CONTRIBUTING.md
    ├── AGENTS.md
    └── Standardized SKILL.md files (6 skills)

  Track D: CI/CD
    └── GitHub Actions workflow (pytest + ruff)
```

Key ordering constraints:
1. Foundation files (LICENSE, .gitignore, pyproject.toml) -- do first, 30 min total
2. Architecture diagram -- shared dependency between README and slides, do early
3. Demo GIF -- requires clean install working, needs setup.sh validated first
4. Manim animations -- longest lead time, start in parallel via Hermes
5. Video walkthrough -- LAST item (records the polished state of everything else)
6. Slide deck -- can start with architecture diagram, finalize after video

---

## MVP Recommendation

### Must Ship (table stakes for credible public release + Comfy Research Phase demo)

Priority order:

1. **LICENSE file** -- 5 min, unlocks legal usability
2. **Clean repo** -- .gitignore, pyproject.toml metadata, remove untracked artifacts
3. **Architecture diagram** (Excalidraw) -- shared dependency for README and slides
4. **README overhaul** -- hero section, badges, quick start, architecture embed, results section
5. **Demo GIF** (VHS or asciinema) -- 15-30s animated terminal recording of /comfy-flow
6. **CONTRIBUTING.md** -- standard community file
7. **Slide deck** (8-12 slides) -- the async-skimmable deliverable
8. **Recorded walkthrough** (2-5 min) -- the main async demo, recorded last

### Should Ship (low-effort differentiators)

9. **CHANGELOG.md** -- retroactive from git history, 30 min
10. **AGENTS.md** -- following the 2026 Linux Foundation standard, 15 min
11. **Template showcase READMEs** -- per-template README in templates/, 1 hr
12. **Metrics section** in README and slides -- already have the data
13. **CI/CD GitHub Action** -- pytest + ruff check, 30 min

### Stretch (high-effort, defer if time-constrained)

14. **Manim pipeline animation** -- impressive but high effort. Attempt ONE animation (the 6-phase pipeline flow) via Hermes. If it works in < 2 hrs, include. If not, static Excalidraw is sufficient for the research phase. Do not block the milestone on this.
15. **Video walkthrough embedded in README** -- YouTube thumbnail linking to recorded demo
16. **Narrated architecture deep-dive** -- separate 5-10 min video, only if main demo is solid
17. **Skill creation guide** -- valuable long-term but Comfy Org audience will consume skills, not author them

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Repo publishing conventions | HIGH | Verified against Anthropic skills repo (113K stars), CrewAI (100K+ stars), awesome-claude-skills, open-source checklists. Patterns are well-established. |
| Demo GIF tooling | HIGH | VHS and asciinema are mature, widely used. VHS is scriptable and CI-friendly. |
| Async demo best practices | MEDIUM | Best practices sourced from Loom, DEV Community, Navattic. Consistent consensus on 2-5 min max, problem/solution/next structure. Specific engagement stats (35% improvement) from single source. |
| Manim feasibility | MEDIUM | Manim Community v0.20.x is stable and well-documented. Generative Manim (AI code gen) exists but maturity is uncertain. Hermes assistance may reduce effort significantly or may require iteration. Flag for phase-specific validation. |
| Excalidraw for architecture | HIGH | Well-established tool for engineering diagrams. MCP integration available for AI-assisted generation. Export to SVG/PNG is straightforward. |
| Slide deck conventions | MEDIUM | Engineering slide conventions are well-known but specific to audience. Comfy Org research phase expectations are not publicly documented -- adapting general async demo best practices. |

---

## Sources

### Open-Source Repo Conventions
- [Anthropic official skills repo](https://github.com/anthropics/skills) -- canonical skill structure, 113K stars, skill folder conventions (HIGH confidence)
- [awesome-claude-skills (travisvn)](https://github.com/travisvn/awesome-claude-skills) -- awesome list conventions, badges, progressive disclosure pattern (HIGH confidence)
- [awesome-claude-code (hesreallyhim)](https://github.com/hesreallyhim/awesome-claude-code) -- skills/hooks/commands organization, emoji conventions (HIGH confidence)
- [CrewAI README](https://github.com/crewAIInc/crewAI) -- hero section, badge row, YouTube embeds, quick start, "Why X?" pattern (HIGH confidence)
- [Open source checklist (libresource)](https://github.com/libresource/open-source-checklist) -- comprehensive publishing checklist: LICENSE, CONTRIBUTING, SECURITY, issue templates (MEDIUM confidence)
- [Make a README](https://www.makeareadme.com/) -- README structure best practices (MEDIUM confidence)
- [AGENTS.md standard](https://github.com/agentsmd/agents.md) -- Linux Foundation backed 2026 standard for AI agent repo context (MEDIUM confidence)
- [How to Create the Perfect README (GitHub/DEV)](https://dev.to/github/how-to-create-the-perfect-readme-for-your-open-source-project-1k69) -- audience-aware README design (MEDIUM confidence)

### Demo GIF / Terminal Recording
- [VHS (Charm.sh)](https://github.com/charmbracelet/vhs) -- scriptable terminal recording, CI-friendly, higher frame rates (HIGH confidence)
- [asciinema + agg](https://github.com/asciinema/agg) -- terminal session recording to animated GIF pipeline, v3.0 rewritten in Rust (HIGH confidence)
- [awesome-terminal-recorder](https://github.com/orangekame3/awesome-terminal-recorder) -- comparison of recording tools (MEDIUM confidence)

### Async Demo / Presentation
- [Loom async demo practices](https://www.atlassian.com/software/loom/resources/guides/use-cases/product-demo) -- 2-5 min target, problem/solution/next-step structure (MEDIUM confidence)
- [Async work playbook (DEV)](https://dev.to/jennifer_simonazzi_280748/async-work-for-dev-teams-a-practical-playbook-for-fewer-meetings-1gho) -- video structure: what changed, why, where in codebase (MEDIUM confidence)
- [Using async video for product demos (Reflow)](https://www.reflow.ai/public/using-async-video-for-product-demos-a-step-by-step-guide-47c10) -- step-by-step demo recording guide (MEDIUM confidence)
- [Interactive demo stats (Navattic)](https://www.navattic.com/blog/interactive-demos) -- engagement improvement with interactivity (LOW confidence, single source)

### Manim
- [Manim Community v0.20.1 docs](https://docs.manim.community/en/stable/) -- scene-based architecture, construct() pattern, .animate API (HIGH confidence)
- [Generative Manim](https://www.blog.brightcoding.dev/2026/02/22/generative-manim-ai-powered-video-creation-revolution) -- AI-powered Manim code generation from text descriptions (MEDIUM confidence)
- [ManimML](https://github.com/helblazer811/ManimML) -- ML-specific visualization patterns for Manim (MEDIUM confidence)
- [Manim for STEM Education (arXiv)](https://arxiv.org/html/2510.01187v1) -- broader applications of Manim beyond math (MEDIUM confidence)

### Excalidraw
- [Excalidraw architecture diagrams](https://plus.excalidraw.com/use-cases/software-architecture-diagram) -- hand-drawn style best practices, color conventions (HIGH confidence)
- [MCP + Excalidraw for architecture](https://atalupadhyay.wordpress.com/2026/03/15/create-architecture-diagrams-with-mcp-claude-draw-io-excalidraw/) -- AI-assisted diagram generation with Claude MCP (MEDIUM confidence)
