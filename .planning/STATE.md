---
gsd_state_version: 1.0
milestone: v2.0
milestone_name: Template Batch — Trending Node Coverage
status: defining_requirements
stopped_at: null
last_updated: "2026-03-25T00:00:00.000Z"
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-25)

**Core value:** Template creators can go from "what should we build next?" to "here's a cloud-tested workflow with submission docs" in a single guided session
**Current focus:** Milestone v2.0 — Defining requirements

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-03-25 — Milestone v2.0 started

## Performance Metrics

**Velocity:**

- Total plans completed: 1
- Average duration: 5min
- Total execution time: 0.08 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-foundation-discovery | 1/2 | 5min | 5min |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
| Phase 01 P02 | 7min | 3 tasks | 7 files |
| Phase 02 P01 | 4min | 3 tasks | 10 files |
| Phase 02 P02 | 3min | 3 tasks | 3 files |
| Phase 03 P01 | 3min | 2 tasks | 7 files |
| Phase 03 P02 | 2min | 2 tasks | 3 files |
| Phase 04 P01 | 4min | 2 tasks | 6 files |
| Phase 04 P02 | 12min | 2 tasks | 4 files |
| Phase 04 P03 | 6min | 2 tasks | 4 files |
| Phase 05 P01 | 3min | 2 tasks | 7 files |
| Phase 05 P02 | 3min | 2 tasks | 4 files |
| Phase 06 P01 | 2min | 2 tasks | 3 files |
| Phase 06 P03 | 3min | 2 tasks | 4 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: Split TMPL and VALD into separate phases (research suggested combining) -- keeps each phase delivering one coherent capability
- [Roadmap]: Combined DOCS and ORCH into one phase -- both are "cap it off" work that consumes all prior outputs
- [Roadmap]: Phase 4 (Composition) placed after Validation -- research confirms this is the hardest phase with genuine technical uncertainty, benefits from having validation available during development
- [01-01]: Used tempfile.gettempdir() for cross-platform /tmp path resolution in extraction scripts
- [01-01]: Structured guidelines as hand-crafted rule objects for reliable programmatic access
- [01-01]: httpx follow_redirects=True needed for GitHub API (301 on /contents endpoint)
- [Phase 01]: Module-level DiskCache singletons for simplicity in registry modules
- [Phase 01]: search_by_type uses two-step approach: search packs then verify I/O via comfy-nodes
- [02-01]: get_github_client() added to http.py for GitHub CDN requests (per CONTEXT.md locked decision)
- [02-01]: Pack-level cross-ref from requiresCustomNodes (fast), node-level from workflow JSONs (thorough)
- [02-01]: Fuzzy matching on index keys when exact match returns nothing
- [Phase 02]: fetch_all_nodes uses pages param -- adapted gap_analysis to match actual API
- [Phase 02]: Gap scoring: log10(downloads) * (1 + log2(stars) * 0.5) balances volume with community signal
- [Phase 02]: Coverage % is pack-level (unique packs in requiresCustomNodes / total registry packs)
- [03-01]: UUID-style node types (>30 chars with hyphens) skipped in custom node detection to avoid false positives on subgraph references
- [03-01]: API node detection runs as separate RuleResult outside RULE_REGISTRY to keep auth concerns distinct
- [03-01]: Note color darkness check uses #0 prefix heuristic
- [03-02]: Used lenient mode in pass-report test since info-level rules always fire on minimal workflows
- [Phase 04]: NodeSpecCache is pass-through: Claude fetches MCP specs and passes raw dicts in
- [04-02]: from_json supports both array and object link formats for maximum compatibility
- [04-02]: swap_node only removes connections when spec is provided (graceful degradation)
- [04-02]: auto_layout uses DFS longest-path layer assignment with cycle detection
- [Phase 04]: save_workflow uses lenient validation by default since composed workflows are drafts
- [Phase 04]: CLI prints guidance message (not error) when no --scaffold/--file given, directing to Claude Code skill
- [Phase 05-01]: Reused extract_node_types from src.templates.fetch for custom node detection consistency
- [Phase 05-01]: Model detection uses Load substring in node type plus file extension heuristic
- [Phase 05]: Phase transitions are pure functions (advance_phase returns next phase without mutating session)
- [Phase 05]: Validation gate blocks advancement to document phase -- must pass before proceeding
- [Phase 06]: Skills already well-structured from prior phases -- applied refinements, not rewrites
- [06-03]: Fixed skill name: comfy-template-audit (not comfy-templates) in setup scripts
- [06-03]: README documents slash commands prominently -- skills require explicit invocation
- [06-03]: Editable pip install (pip install -e .[dev]) enables python -m src.* from any directory

### Roadmap Evolution

- Phase 6 added: Testing & Distribution — E2E testing with real workflows, install script, README, prep for sharing

### Pending Todos

None yet.

### Blockers/Concerns

- Phase 3 needs Notion guidelines extracted to structured JSON before planning (human data task, should happen during Phase 1-2 execution)
- Phase 4 needs research-phase during planning: widget-to-position mapping, type-safe link construction API design. **UPDATE (2026-03-19): MCP Server v0.2.0 released — `search_nodes` now returns field names, defaults, COMBO options, min/max ranges. This replaces the need for /object_info caching. Also `search_templates` available. Phase 4 should use MCP tools for node specs instead of building custom caching. Fold MCP integration into Phase 4, no separate phase needed.**
- GitHub API rate limits (60 req/hr unauthenticated) -- GITHUB_TOKEN env var support needed in Phase 1 HTTP client

## Session Continuity

Last session: 2026-03-19T19:05:56Z
Stopped at: Completed 06-03-PLAN.md
