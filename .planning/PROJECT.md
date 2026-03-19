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

### Active

- [ ] Search and browse the existing 400+ template library (Comfy-Org/workflow_templates) to check what's already covered
- [ ] Search and browse the existing 400+ template library (Comfy-Org/workflow_templates) to check what's already covered
- [ ] Cross-reference: given a node or node pack, check if it's already used in an existing template
- [ ] Ideate new template concepts based on community trends, uncovered nodes, and gaps in the current library
- [ ] Compose valid ComfyUI workflow JSON from scratch for novel use cases (node-aware, type-safe connections)
- [ ] Scaffold workflows from existing templates and adapt/extend for new use cases
- [ ] Validate workflows against template creation guidelines (core nodes preferred, no set/get nodes, subgraph rules, color/note conventions)
- [ ] Flag custom node dependencies and document them (requiresCustomNodes field)
- [ ] Detect and flag API node usage with auth requirements
- [ ] Generate template metadata in index.json format (name, title, description, models, io, tags, etc.)
- [ ] Generate Notion-friendly markdown for the workflow submission process
- [ ] Guided phase-based workflow: discover → ideate → compose → validate → document
- [ ] Remind users to capture screenshots/thumbnails where needed

### Out of Scope

- Notion API integration for auto-creating pages — v1 outputs markdown, users paste it (per-user page hierarchy makes API complex)
- Running/testing workflows on Comfy Cloud — users test manually via cloud UI
- Thumbnail generation or image processing
- OAuth/auth management for Comfy.org accounts
- Template review/approval workflow automation

## Context

- **Existing tools to build on:**
  - `comfy-tip` (Projects/comfy-tip/) — node discovery from api.comfy.org with trending heuristic, 5 discovery modes
  - `comfyui-mcp` (comfyui-cloud MCP server) — workflow submission, model search, node search via cloud API
  - Local MCP improvements (Projects/comfyui/) — API node auth detection, silent failure handling
- **Template source of truth:** GitHub repo `Comfy-Org/workflow_templates` — 400 templates across 8 categories, index.json defines metadata schema
- **Template guidelines:** Notion doc covering node usage rules (prefer core nodes, no set/get), subgraph conventions, color/note standards, submission format
- **Team format:** Currently template creators work from existing templates as reference. No formalized "source of truth" format beyond the repo structure itself — this tool can help define one
- **Registry API:** api.comfy.org provides node metadata (8,400+ nodes), used by comfy-tip for discovery

## Constraints

- **Tech stack**: Python + Claude Code skills/agents — matches existing comfy-tip and MCP tooling
- **Distribution**: Lives in this repo (comfyui-template-agent), installable as Claude Code skills
- **API access**: Registry API (api.comfy.org, public), GitHub API (workflow_templates repo, public), ComfyUI Cloud MCP (existing)
- **No Notion API in v1**: Output is markdown, not direct Notion writes
- **Template format**: Must match workflow_templates repo conventions (index.json schema, file naming, bundle structure)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| GSD-inspired phase workflow rather than loose tools | Template creation has a natural flow (discover → ideate → compose → validate → document) that benefits from guided phases | — Pending |
| Python core with Claude Code skill interface | Matches comfy-tip and MCP server patterns, team already uses Claude Code | — Pending |
| Notion markdown output, not API integration | Per-user page hierarchy makes API complex; markdown + human review is fine for v1 | — Pending |
| Build on comfy-tip + MCP rather than from scratch | Proven node discovery and cloud interaction already exist | — Pending |
| Scaffold + compose dual path for workflow creation | Novel use cases need from-scratch composition; variations are faster from templates | — Pending |

---
*Last updated: 2026-03-19 after Phase 1 completion*
