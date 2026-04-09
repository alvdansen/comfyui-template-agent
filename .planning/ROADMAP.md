# Roadmap: ComfyUI Template Agent

## Milestones

- v1.0 MVP - Phases 1-6 (shipped 2026-03-20)
- v2.0 Template Batch - Phases 7-11 (shipped 2026-04-09)
- v3.0 Publish & Present - Phases 12-16 (in progress)

## Phases

<details>
<summary>v1.0 MVP (Phases 1-6) - SHIPPED 2026-03-20</summary>

- [x] **Phase 1: Foundation + Discovery** - Shared infrastructure and registry node discovery skill
- [x] **Phase 2: Template Intelligence** - Template library browsing, cross-referencing, and gap analysis
- [x] **Phase 3: Validation Engine** - Guideline compliance checks and compatibility validation
- [x] **Phase 4: Composition** - Type-safe workflow building and template scaffolding
- [x] **Phase 5: Documentation + Orchestration** - Submission doc generation and guided end-to-end flow
- [x] **Phase 6: Testing & Distribution** - E2E testing, install script, README, repo cleanup

</details>

<details>
<summary>v2.0 Template Batch (Phases 7-11) - SHIPPED 2026-04-09</summary>

- [x] **Phase 7: Tooling Fixes** - Fix core_nodes.json audio gaps and metadata.py GGUF detection
- [x] **Phase 8: MelBandRoFormer Template** - Audio stem separation workflow (5 nodes, linear pipeline)
- [x] **Phase 9: Florence2 Template** - Vision AI captioning/detection workflow (6 nodes, multi-output)
- [x] **Phase 10: GGUF Template** - Quantized FLUX.1-schnell txt2img workflow (9 nodes, GGUF loaders)
- [x] **Phase 11: Impact Pack Template** - Face detection + auto-detailing workflow (11 nodes, fan-out)

Archive: [v2.0-ROADMAP.md](milestones/v2.0-ROADMAP.md) | [v2.0-REQUIREMENTS.md](milestones/v2.0-REQUIREMENTS.md)

</details>

### v3.0 Publish & Present (In Progress)

**Milestone Goal:** Polish the template agent into a production-ready deliverable under Alvdansen Labs, with async presentation materials for the Comfy-Org Research Phase (Apr 7-17).

- [ ] **Phase 12: Repo Foundation** - License, metadata, .gitignore, and changelog for public-ready repo structure
- [ ] **Phase 13: Content Cleanup** - Rewrite all docs for external audience (README, CLAUDE.md, CONTRIBUTING, skills, template READMEs)
- [ ] **Phase 14: Presentation Materials** - Architecture diagram, slide deck, and Manim animation on Hermes (parallel with Phase 13)
- [ ] **Phase 15: CI/CD & Final Polish** - GitHub Actions, issue templates, CI badge, and demo GIF recording
- [ ] **Phase 16: Publish & Handoff** - Fresh repo under alvdansen org, verification, recorded walkthrough, and Comfy-Org delivery

## Phase Details

### Phase 12: Repo Foundation
**Goal**: Repo has all legal and structural prerequisites for public release
**Depends on**: Nothing (first phase of v3.0)
**Requirements**: REPO-01, REPO-02, REPO-03, REPO-04
**Success Criteria** (what must be TRUE):
  1. MIT LICENSE file exists in repo root and is referenced by pyproject.toml
  2. pyproject.toml contains version 3.0.0, author, license, repository URL, classifiers, and keywords
  3. .gitignore covers .venv/, *.egg-info/, __pycache__/, .planning/, and no tracked files match those patterns
  4. CHANGELOG.md documents v1.0 (6 skills, 14 plans), v2.0 (4 templates), and v3.0 (publish) milestones with dates
**Plans:** 2 plans
Plans:
- [ ] 12-01-PLAN.md -- LICENSE, pyproject.toml metadata, and .gitignore
- [ ] 12-02-PLAN.md -- Retroactive CHANGELOG.md with v1.0, v2.0, v3.0 entries

### Phase 13: Content Cleanup
**Goal**: All documentation is written for an external engineering audience, not internal development
**Depends on**: Phase 12 (version number and license must exist before README references them)
**Requirements**: CONTENT-01, CONTENT-02, CONTENT-03, CONTENT-04, CONTENT-05, CONTENT-06, CONTENT-07, CONTENT-08, CONTENT-09
**Success Criteria** (what must be TRUE):
  1. README has hero section with badges, one-line value prop, quick start (clone to first command in under 60s), architecture diagram placeholder, and quantified results
  2. CLAUDE.md contains only agent instructions relevant to external contributors (no GSD enforcement, no developer profile placeholder, no template node documentation blobs)
  3. CONTRIBUTING.md explains dev setup, code style (pydantic/httpx/ruff), PR process, and skill authoring conventions
  4. All 6 SKILL.md files follow a consistent format with trigger, capabilities, example session, and gotchas
  5. Each of the 4 template directories has a README explaining what was built, which skills were used, and the outputs produced
**Plans**: TBD
**UI hint**: yes

### Phase 14: Presentation Materials
**Goal**: Async-consumable visual artifacts exist for the Comfy-Org Research Phase audience
**Depends on**: Phase 12 (needs repo context); can run PARALLEL with Phase 13 (different machine -- Hermes)
**Requirements**: PRESENT-01, PRESENT-02, PRESENT-05
**Success Criteria** (what must be TRUE):
  1. Excalidraw architecture diagram (SVG + PNG) shows skills layer, Python modules, and external API connections
  2. Slide deck (8-12 slides) covers problem, solution, architecture, skill walkthrough, demo highlights, metrics, and next steps
  3. Manim pipeline animation renders the discover-to-document flow (stretch -- not a milestone blocker if it fails)
**Plans**: TBD

### Phase 15: CI/CD & Final Polish
**Goal**: Repo has automated quality gates and a polished demo recording
**Depends on**: Phase 13 (CI tests stable content; demo GIF records polished skill invocation); Phase 14 (architecture diagram embedded in README)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, PRESENT-04
**Success Criteria** (what must be TRUE):
  1. GitHub Actions workflow runs ruff lint and pytest in parallel on push and PR, and passes on current codebase
  2. Repository has bug report and feature request issue templates under .github/ISSUE_TEMPLATE/
  3. CI badge in README hero section shows passing status
  4. Demo GIF (15-30s terminal recording) is embedded in README and shows a skill invocation end-to-end
**Plans**: TBD

### Phase 16: Publish & Handoff
**Goal**: Comfy-Org devs can clone, run, evaluate, and absorb the toolkit from a public repository
**Depends on**: All prior phases (Phase 12-15 must be complete; recorded walkthrough captures finished state)
**Requirements**: PUBLISH-01, PUBLISH-02, PUBLISH-03, PUBLISH-04, PUBLISH-05, PRESENT-03
**Success Criteria** (what must be TRUE):
  1. Public repo exists at alvdansen/comfyui-template-agent with no internal git history or personal identifiers
  2. v3.0.0 git tag exists on the published repo's initial commit
  3. Clean clone verification passes: git clone, setup.sh, pytest, and at least one skill invocation all succeed
  4. HANDOFF.md provides specific test scenarios and an evaluation guide for Comfy-Org devs
  5. Recorded async walkthrough (2-5 min) demonstrates an end-to-end /comfy-flow session on the published repo
**Plans**: TBD

## Progress

**Execution Order:**
Phases 12 through 16, with Phase 14 eligible to run in parallel with Phase 13 (different machine).

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 12. Repo Foundation | v3.0 | 2/2 | Complete | 2026-04-09 |
| 13. Content Cleanup | v3.0 | 3/4 | In Progress|  |
| 14. Presentation Materials | v3.0 | 0/TBD | Not started | - |
| 15. CI/CD & Final Polish | v3.0 | 0/TBD | Not started | - |
| 16. Publish & Handoff | v3.0 | 0/TBD | Not started | - |
