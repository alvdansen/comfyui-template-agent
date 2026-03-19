# Phase 4: Composition - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can build valid ComfyUI workflow JSON through a type-safe builder or by scaffolding from existing templates. Delivers COMP-01 through COMP-04: scaffold from template, compose from scratch, incremental building with per-step validation, and correct workflow format output. MCP v0.2.0's `search_nodes` (with full input specs) replaces the need for custom /object_info caching.

</domain>

<decisions>
## Implementation Decisions

### Builder Interaction
- Claude decides interaction model (recommendation: hybrid — conversational intent translated to programmatic calls)
- Claude decides validation granularity for incremental building
- **Full graph complexity** — support any valid ComfyUI graph including branching, multi-path, and basic subgraphs
- **Ask for key params** — auto-default most parameters (using MCP search_nodes defaults), but prompt for important ones (model, resolution, steps)
- **Both starting paths**: goal-based for common patterns ("I want a Flux img2img workflow"), node-first for custom builds
- **Best available nodes** — suggest whatever works best regardless of core/custom, flag custom nodes for awareness (don't force core-only)
- **Auto-layout with human polish** — builder auto-places nodes in logical flow, user does a polish pass in ComfyUI UI
- **Auto-generate titles/descriptions** — Claude generates based on nodes used
- **Basic subgraph support** — wrapping a set of nodes into a named subgraph
- **Output path**: default to current directory, `--output` flag for custom path

### MCP Integration
- **MCP server required** for composition — error if comfyui-mcp not available
- Claude decides whether to call MCP search_nodes directly or through a cached wrapper
- **Cloud submission via MCP** — offer to submit composed workflow to Comfy Cloud for testing via submit_workflow
- **Cloud-first option** — user can also START by using Comfy Cloud to test/iterate, not just submit at the end

### Scaffold Workflow
- **All operations supported**: swap nodes, change parameters, add/remove nodes, rewire connections
- **Both sources**: pick from 400+ template library (Phase 2 search) OR load local workflow JSON file
- Scaffold is a deep copy + modification, not in-place editing

### Output + Validation
- Claude decides validation timing (recommendation: light type-check per step, full guideline validation on save)
- **Always workflow format** (nodes[] + links[]), never API format (COMP-04)
- Use Phase 3 validator engine for guideline compliance check on final output

### Claude's Discretion
- Interaction model specifics (conversational vs programmatic vs hybrid)
- Validation granularity during incremental composition
- MCP integration approach (direct calls vs cached wrapper)
- Auto-layout algorithm
- Type checking implementation for node connections
- How to handle connection type mismatches during composition

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### ComfyUI Workflow Format
- ComfyUI Workflow JSON Spec: https://docs.comfy.org/specs/workflow_json — workflow format v1.0, node/link structure, schema fields
- `.planning/research/PITFALLS.md` — Format confusion (#1), widget positional mapping (#2), link type mismatches (#4)

### MCP v0.2.0 (Critical for this phase)
- ComfyUI MCP Server v0.2.0 — `search_nodes` returns field names, defaults, COMBO options, min/max ranges. `search_templates` for template discovery. `submit_workflow` for cloud testing.
- Existing comfyui-cloud MCP in Claude Code session — provides search_models, search_nodes, submit_workflow tools

### Existing Infrastructure
- `src/shared/format_detector.py` — `detect_format()` returns 'workflow' or 'api'. Composer MUST output workflow format.
- `src/templates/fetch.py` — `fetch_workflow_json()`, `get_template_detail()` for loading scaffold base templates
- `src/templates/search.py` — `search_templates()` for finding scaffold candidates
- `src/templates/cross_ref.py` — `extract_node_types()` with subgraph recursion for parsing existing templates
- `src/validator/engine.py` — `run_validation()` for guideline compliance on composed output
- `src/registry/models.py` — `NodePack`, `ComfyNode` Pydantic models
- `data/core_nodes.json` — 114 core nodes for flagging custom node usage

### Research
- `.planning/research/SUMMARY.md` — Composition is highest-risk phase, incremental graph edits recommended
- `.planning/research/PITFALLS.md` — LLMs achieve 12-15% pass rate on raw workflow generation; type-safe builder essential

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/shared/format_detector.py` — Gate: reject API format, ensure workflow format output
- `src/templates/fetch.py` — `fetch_workflow_json(template_name)` for loading scaffold bases
- `src/templates/search.py` — `search_templates()` for finding templates to scaffold from
- `src/validator/engine.py` — `run_validation()` for post-composition guideline check
- `src/validator/rules.py` — `check_core_node_preference()` for flagging custom nodes in composed output
- MCP tools: `search_nodes` (node specs with inputs/outputs/defaults), `search_models` (model discovery), `submit_workflow` (cloud test)

### Established Patterns
- Pydantic model → logic functions → format function → CLI entry point with argparse
- Tests: unittest.mock.patch, fixture data
- Skills: SKILL.md with natural language + explicit flags

### Integration Points
- New `src/composer/` module
- Skill: `.claude/skills/comfy-compose/SKILL.md`
- Uses MCP tools (search_nodes, submit_workflow) from Claude Code session
- Feeds composed JSON into validator for compliance check
- Scaffold sources from template fetch/search modules

</code_context>

<specifics>
## Specific Ideas

- Cloud-first option: user can start by submitting a draft workflow to Comfy Cloud to test, iterate on results, then polish
- Builder should flag custom node usage proactively ("this node is custom — are you sure? Template guidelines prefer core nodes")
- Auto-layout should be "good enough to work" — user does the visual polish pass in ComfyUI Desktop UI
- The research flagged that LLMs achieve only 12-15% pass rate on raw JSON generation — the type-safe builder is non-negotiable

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-composition*
*Context gathered: 2026-03-19*
