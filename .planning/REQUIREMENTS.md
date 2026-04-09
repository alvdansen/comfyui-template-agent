# Requirements: ComfyUI Template Agent

**Defined:** 2026-04-08
**Core Value:** Template creators can go from "what should we build next?" to "here's a cloud-tested workflow with submission docs" in a single guided session

## v3.0 Requirements

Requirements for the Publish & Present milestone. Each maps to roadmap phases.

### Repo Foundation

- [ ] **REPO-01**: Repo has MIT LICENSE file in root
- [ ] **REPO-02**: pyproject.toml has complete metadata (version 3.0.0, author, license, URLs, classifiers, keywords)
- [ ] **REPO-03**: .gitignore covers all build artifacts (.venv/, *.egg-info/, __pycache__/, .planning/)
- [ ] **REPO-04**: CHANGELOG.md documents v1.0, v2.0, and v3.0 milestones retroactively

### Content & Documentation

- [x] **CONTENT-01**: README has hero section with banner, shields.io badges, and one-line value prop
- [x] **CONTENT-02**: README has quick start section (clone → setup → first command) under 60 seconds
- [x] **CONTENT-03**: README has embedded architecture diagram (from Excalidraw SVG/PNG)
- [x] **CONTENT-04**: README has quantified results section (4 templates, 42 requirements, node pack downloads)
- [x] **CONTENT-05**: CLAUDE.md trimmed of GSD enforcement, developer profile placeholder, and template node documentation
- [ ] **CONTENT-06**: CONTRIBUTING.md with dev setup, code style (pydantic, httpx, ruff), PR process, skill authoring guide
- [ ] **CONTENT-07**: AGENTS.md following 2026 Linux Foundation standard
- [x] **CONTENT-08**: All 6 SKILL.md files standardized with trigger, capabilities, example sessions, gotchas
- [ ] **CONTENT-09**: Each of 4 templates has a README explaining what was built, which skills were used, and outputs

### Presentation Materials

- [ ] **PRESENT-01**: Excalidraw architecture diagram showing skills → Python modules → external APIs (SVG + PNG)
- [ ] **PRESENT-02**: Slide deck (8-12 slides): problem, solution, architecture, skill walkthrough, demo highlights, metrics, next steps
- [ ] **PRESENT-03**: Recorded async walkthrough (2-5 min) showing end-to-end /comfy-flow session
- [ ] **PRESENT-04**: Demo GIF (15-30s terminal recording of skill invocation) embedded in README
- [ ] **PRESENT-05**: Manim pipeline animation showing discover → audit → validate → compose → document flow (stretch — don't block milestone)

### CI/CD & Infrastructure

- [ ] **INFRA-01**: GitHub Actions workflow with parallel lint (ruff) and test (pytest) jobs
- [ ] **INFRA-02**: GitHub issue templates (bug report, feature request)
- [ ] **INFRA-03**: CI badge displayed in README hero section

### Publish & Handoff

- [ ] **PUBLISH-01**: Fresh repo created under alvdansen GitHub org (no internal git history)
- [ ] **PUBLISH-02**: v3.0.0 git tag on published repo
- [ ] **PUBLISH-03**: Clean clone verification passes (clone → setup.sh → pytest → skill invocation)
- [ ] **PUBLISH-04**: HANDOFF.md with test scenarios and evaluation guide for Comfy-Org devs
- [ ] **PUBLISH-05**: Presentation materials shared with Comfy-Org (#proj-comfy-agent or Notion)

## Future Requirements

Deferred to post-v3.0. Tracked but not in current roadmap.

### Distribution

- **DIST-01**: Anthropic skills marketplace submission
- **DIST-02**: PyPI package distribution

### Advanced Features

- **ADV-01**: Notion API integration for direct page creation
- **ADV-02**: Template PR auto-submission to workflow_templates repo
- **ADV-03**: Skill creation guide for external authors (standalone doc)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Template PR submissions | Separate effort per user decision — presentation only for v3.0 |
| Live roundtable presentation | Async delivery constraint for Research Phase |
| PyPI package | git clone + setup.sh is the correct install path for Claude Code skills |
| Docker containerization | Skills need to be in user's Claude Code environment |
| Web UI or dashboard | CLI/agent toolkit — Claude Code IS the interface |
| Multi-language support | English-only for engineering team audience |
| Exhaustive test coverage push | Existing 0.5s test suite covers critical paths |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| REPO-01 | Phase 12 | Pending |
| REPO-02 | Phase 12 | Pending |
| REPO-03 | Phase 12 | Pending |
| REPO-04 | Phase 12 | Pending |
| CONTENT-01 | Phase 13 | Complete |
| CONTENT-02 | Phase 13 | Complete |
| CONTENT-03 | Phase 13 | Complete |
| CONTENT-04 | Phase 13 | Complete |
| CONTENT-05 | Phase 13 | Complete |
| CONTENT-06 | Phase 13 | Pending |
| CONTENT-07 | Phase 13 | Pending |
| CONTENT-08 | Phase 13 | Complete |
| CONTENT-09 | Phase 13 | Pending |
| PRESENT-01 | Phase 14 | Pending |
| PRESENT-02 | Phase 14 | Pending |
| PRESENT-03 | Phase 16 | Pending |
| PRESENT-04 | Phase 15 | Pending |
| PRESENT-05 | Phase 14 | Pending |
| INFRA-01 | Phase 15 | Pending |
| INFRA-02 | Phase 15 | Pending |
| INFRA-03 | Phase 15 | Pending |
| PUBLISH-01 | Phase 16 | Pending |
| PUBLISH-02 | Phase 16 | Pending |
| PUBLISH-03 | Phase 16 | Pending |
| PUBLISH-04 | Phase 16 | Pending |
| PUBLISH-05 | Phase 16 | Pending |

**Coverage:**
- v3.0 requirements: 26 total
- Mapped to phases: 26
- Unmapped: 0

---
*Requirements defined: 2026-04-08*
*Last updated: 2026-04-08 after roadmap creation*
