# Roadmap: ComfyUI Template Agent

## Overview

This project delivers a Claude Code agent toolkit that guides template creators through the full workflow: discovering trending nodes, browsing existing templates for gaps, validating workflows against guidelines, composing valid workflow JSON, and generating submission documentation. The build order follows hard data dependencies -- discovery feeds template intelligence, template intelligence informs validation rules, validation must exist before composition makes sense, and documentation consumes outputs from all prior phases. The orchestrator ties everything together last.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation + Discovery** - Shared infrastructure and registry node discovery skill
- [ ] **Phase 2: Template Intelligence** - Template library browsing, cross-referencing, and gap analysis
- [ ] **Phase 3: Validation Engine** - Guideline compliance checks and compatibility validation
- [ ] **Phase 4: Composition** - Type-safe workflow building and template scaffolding
- [ ] **Phase 5: Documentation + Orchestration** - Submission doc generation and guided end-to-end flow

## Phase Details

### Phase 1: Foundation + Discovery
**Goal**: Users can discover and explore ComfyUI nodes from the registry with full metadata
**Depends on**: Nothing (first phase)
**Requirements**: DISC-01, DISC-02, DISC-03, DISC-04, DISC-05
**Success Criteria** (what must be TRUE):
  1. User can query trending, new, rising, popular, and random nodes and see results with download counts and descriptions
  2. User can search nodes by name, category, or input/output type and get relevant results
  3. User can filter discovery results by media category (video, image, audio, 3D)
  4. User can inspect a custom node pack to see all nodes it includes with their input/output specs
  5. Project infrastructure exists: HTTP client with caching, core node whitelist data file, format detector utility
**Plans**: 2 plans

Plans:
- [ ] 01-01-PLAN.md — Project scaffolding, shared infrastructure, data models, and data extraction
- [ ] 01-02-PLAN.md — Discovery modules (highlights, search, spec), skill definition, and tests

### Phase 2: Template Intelligence
**Goal**: Users can browse existing templates, cross-reference nodes against the template library, and identify gaps worth filling
**Depends on**: Phase 1
**Requirements**: TMPL-01, TMPL-02, TMPL-03, TMPL-04, TMPL-05
**Success Criteria** (what must be TRUE):
  1. User can search the 400+ template library by name, category, or model and find matching templates
  2. User can view full details of any template including nodes used, models required, and custom node dependencies
  3. User can check whether a specific node or node pack is already used in any existing template
  4. User can generate a gap analysis showing popular/trending nodes that have no template coverage
  5. User can view a coverage report showing template counts per category and identifying thin areas
**Plans**: 2 plans

Plans:
- [ ] 02-01-PLAN.md — Template data layer (models, fetch, search) and cross-reference module with tests
- [ ] 02-02-PLAN.md — Gap analysis engine, coverage reporting, and Claude Code skill definition

### Phase 3: Validation Engine
**Goal**: Users can validate any workflow against template creation guidelines and get actionable fix suggestions
**Depends on**: Phase 1, Phase 2
**Requirements**: VALD-01, VALD-02, VALD-03, VALD-04
**Success Criteria** (what must be TRUE):
  1. User can check a workflow for custom node usage and see suggested core node alternatives where they exist
  2. User can detect API nodes (Gemini, BFL, ElevenLabs, etc.) in a workflow and see which ones require auth credentials
  3. User can run a full guideline compliance check that reports violations for set/get node usage, subgraph rules, color/note conventions, and naming standards
  4. User can validate a workflow for Comfy Cloud compatibility and see a pass/fail report with specific issues listed
**Plans**: 2 plans

Plans:
- [ ] 03-01-PLAN.md — Validation models, rule functions, API node detection, engine with strict/lenient modes and tests
- [ ] 03-02-PLAN.md — CLI entry point, report formatter, and Claude Code skill definition

### Phase 4: Composition
**Goal**: Users can build valid ComfyUI workflow JSON through a type-safe builder or by scaffolding from existing templates
**Depends on**: Phase 1, Phase 2, Phase 3
**Requirements**: COMP-01, COMP-02, COMP-03, COMP-04
**Success Criteria** (what must be TRUE):
  1. User can pick an existing template and scaffold a new workflow from it with modifications (e.g., txt2img to img2img)
  2. User can compose a new workflow from scratch by adding nodes and connecting them, with type checking on every connection
  3. User can build workflows incrementally with validation feedback after each step (add node, connect, set parameter)
  4. All composed workflows output correct workflow format (nodes[] + links[] structure), never API format
**Plans**: 3 plans

Plans:
- [ ] 04-01-PLAN.md — Composition models (NodeSpec, GraphNode, GraphLink), node spec cache, and WorkflowGraph builder core
- [ ] 04-02-PLAN.md — Scaffold operations (from_json, from_template, from_file, swap_node) and auto-layout algorithm
- [ ] 04-03-PLAN.md — CLI entry point, save with validation, public API exports, and Claude Code skill definition

### Phase 5: Documentation + Orchestration
**Goal**: Users can generate submission-ready documentation and run the full discover-to-document workflow as a guided session
**Depends on**: Phase 1, Phase 2, Phase 3, Phase 4
**Requirements**: DOCS-01, DOCS-02, DOCS-03, DOCS-04, ORCH-01, ORCH-02
**Success Criteria** (what must be TRUE):
  1. User can auto-generate a complete index.json metadata entry from a workflow file (name, title, description, models, io, tags)
  2. User can generate Notion-friendly markdown for the submission process, ready to paste
  3. User can auto-extract the IO spec (inputs and outputs) from workflow JSON without manual inspection
  4. User gets prompted about thumbnail/screenshot requirements with exact format specs at the right point in the flow
  5. User can run a guided session that walks through discover, ideate, compose, validate, and document phases with context carried between steps
**Plans**: 2 plans

Plans:
- [ ] 05-01-PLAN.md — Documentation module: models, metadata extraction, IO spec, Notion markdown, thumbnail reminders, CLI, tests, and skill definition
- [ ] 05-02-PLAN.md — Orchestrator: session state, phase transitions, context-aware suggestions, and comfy-flow skill definition

## Progress

**Execution Order:**
Phases execute in numeric order: 1 > 2 > 3 > 4 > 5 > 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation + Discovery | 1/2 | In Progress|  |
| 2. Template Intelligence | 1/2 | In Progress|  |
| 3. Validation Engine | 0/2 | Not started | - |
| 4. Composition | 0/3 | Not started | - |
| 5. Documentation + Orchestration | 0/2 | Not started | - |

### Phase 6: Testing & Distribution
**Goal**: End-to-end testing with real workflows, install script for team onboarding, README, and prep for sharing with colleagues
**Depends on**: Phase 5
**Requirements**: TEST-01, TEST-02, TEST-03, TEST-04
**Success Criteria** (what must be TRUE):
  1. All skills tested end-to-end with real ComfyUI workflows (not just mocked data)
  2. Install script sets up skills, symlinks, and dependencies for a new team member
  3. README documents all skills, setup instructions, and usage examples
  4. Repo is clean, .gitignore correct, no secrets or temp files committed
**Plans**: TBD

Plans:
- [ ] 06-01: TBD
- [ ] 06-02: TBD
