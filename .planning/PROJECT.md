# ComfyUI Template Agent

## What This Is

An internal Claude Code agent toolkit for the ComfyUI templates team that streamlines the entire template creation workflow — from discovering trending nodes and ideating new templates, through composing valid workflow JSON, to generating Notion-ready submission docs. It packages a guided, phase-based workflow (inspired by GSD's structure) that's purpose-built for ComfyUI template creation, with built-in awareness of custom node constraints, API node auth requirements, cloud compatibility, and the team's Notion submission process.

## Core Value

Template creators can go from "what should we build next?" to "here's a cloud-tested workflow with submission docs" in a single guided session, with the agent handling node discovery, compatibility checks, workflow composition, and documentation formatting.

## Requirements

### Validated

- ✓ Discover and surface trending/new/rising/popular/random nodes from the ComfyUI registry — Phase 1
- ✓ Search nodes by name, category, or input/output type — Phase 1
- ✓ Filter discovery by media category (video, image, audio, 3D) — Phase 1
- ✓ View what nodes a custom node pack includes — Phase 1
- ✓ Random node suggestions for idea sparking — Phase 1

- ✓ Search and browse the existing 400+ template library to check what's already covered — Phase 2
- ✓ Cross-reference: given a node or node pack, check if it's already used in an existing template — Phase 2
- ✓ Gap analysis: identify popular nodes not covered by any template — Phase 2
- ✓ Template coverage reporting by category — Phase 2

- ✓ Validate workflows against template creation guidelines (12 rules, strict/lenient modes) — Phase 3
- ✓ Flag custom node dependencies with core node alternative suggestions — Phase 3
- ✓ Detect and flag API node usage with auth requirements (7 providers) — Phase 3
- ✓ Cloud compatibility validation — Phase 3

- ✓ Compose valid ComfyUI workflow JSON from scratch with type-safe connections — Phase 4
- ✓ Scaffold workflows from existing templates and adapt/extend — Phase 4
- ✓ Incremental composition with per-step validation — Phase 4

- ✓ Generate template metadata in index.json format — Phase 5
- ✓ Generate Notion-friendly markdown for submission — Phase 5
- ✓ Auto-extract IO spec from workflow JSON — Phase 5
- ✓ Thumbnail/screenshot requirement reminders — Phase 5
- ✓ Guided phase-based workflow: discover → ideate → compose → validate → document — Phase 5
- ✓ Context-aware suggestions between phases — Phase 5

### Validated (v2.0)

- ✓ ComfyUI-Florence2 template — vision AI captioning workflow with auto-download model — Phase 9
- ✓ ComfyUI-GGUF template — quantized FLUX.1-schnell txt2img for 8 GB VRAM — Phase 10
- ✓ ComfyUI Impact Pack template — face detection + auto-detailing with dual-pack dependency — Phase 11
- ✓ ComfyUI-MelBandRoFormer template — audio stem separation workflow — Phase 8
- ✓ Each template passes validation, includes index.json metadata and Notion submission docs — Phases 8-11
- ✓ Tooling fixes: core_nodes.json audio gaps and .gguf model detection — Phase 7

## Current Milestone: v3.0 — Publish & Present

**Goal:** Polish the template agent into a production-ready deliverable under Alvdansen Labs, with async presentation materials powered by Hermes, aligned with the Comfy Agent Research Phase (Apr 7-17).

### Active

- [ ] Clean repo structure, README, install guide for public release
- [ ] Package as polished deliverable for Comfy devs to stress-test and absorb into Comfy-Org
- [ ] Manim animations: workflow pipeline visualizations (via Hermes)
- [ ] PowerPoint deck: architecture, metrics, demo flow
- [ ] Excalidraw: system architecture diagrams (via Hermes)
- [ ] Recorded async demo walkthrough
- [ ] Publish to Alvdansen Labs GitHub org

### Out of Scope (v3.0)

- Template PR submissions to workflow_templates repo (separate effort)
- Live roundtable presentation (async delivery instead)

## Current State

**Shipped:** v2.0 (2026-04-09)
**Previous:** v1.0 (2026-03-20)

All 6 skills operational. 4 production templates delivered covering high-demand node packs (Florence2, GGUF, Impact Pack, MelBandRoFormer). 42 requirements fulfilled across both milestones.

### Out of Scope

- Notion API integration for auto-creating pages — v1 outputs markdown, users paste it (per-user page hierarchy makes API complex)
- Running/testing workflows on Comfy Cloud — users test manually via cloud UI
- Thumbnail generation or image processing
- OAuth/auth management for Comfy.org accounts
- Template review/approval workflow automation

## Context

- **Codebase:** 6 Claude Code skills (`comfy-discover`, `comfy-template-audit`, `comfy-validate`, `comfy-compose`, `comfy-document`, `comfy-flow`) backed by Python modules in `src/`
- **Templates delivered:** 4 production templates in `templates/` (Florence2, GGUF, Impact Pack, MelBandRoFormer) — each with workflow JSON, index.json, Notion markdown, and build scripts
- **Infrastructure:** Shared HTTP client (httpx), disk caching, format detection in `src/shared/`; validator engine with 12 rules in `src/validator/`; type-safe graph builder in `src/composer/`
- **External dependencies:** Registry API (api.comfy.org, public), GitHub API (workflow_templates repo), ComfyUI Cloud MCP
- **Template source of truth:** GitHub repo `Comfy-Org/workflow_templates` — 400+ templates, index.json schema
- **Registry API:** api.comfy.org provides node metadata (8,400+ nodes)

## Constraints

- **Tech stack**: Python + Claude Code skills/agents — matches existing comfy-tip and MCP tooling
- **Distribution**: Lives in this repo (comfyui-template-agent), installable as Claude Code skills
- **API access**: Registry API (api.comfy.org, public), GitHub API (workflow_templates repo, public), ComfyUI Cloud MCP (existing)
- **No Notion API in v1**: Output is markdown, not direct Notion writes
- **Template format**: Must match workflow_templates repo conventions (index.json schema, file naming, bundle structure)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| GSD-inspired phase workflow rather than loose tools | Template creation has a natural flow (discover → ideate → compose → validate → document) that benefits from guided phases | ✓ Validated — comfy-flow skill guides full workflow, used across all 4 v2.0 templates |
| Python core with Claude Code skill interface | Matches comfy-tip and MCP server patterns, team already uses Claude Code | ✓ Validated — 6 skills delivered, Python modules handle all composition/validation/docs |
| Notion markdown output, not API integration | Per-user page hierarchy makes API complex; markdown + human review is fine for v1 | ✓ Validated — markdown output used for all 4 template submissions |
| Build on comfy-tip + MCP rather than from scratch | Proven node discovery and cloud interaction already exist | ✓ Validated — no new Python code needed for v2.0 templates, existing tools handled all 4 |
| Scaffold + compose dual path for workflow creation | Novel use cases need from-scratch composition; variations are faster from templates | ✓ Validated — v2.0 templates used both paths depending on complexity |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-08 — v3.0 milestone initiated*
