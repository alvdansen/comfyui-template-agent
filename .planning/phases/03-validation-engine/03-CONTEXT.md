# Phase 3: Validation Engine - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can validate any workflow against template creation guidelines and get actionable fix suggestions. Delivers VALD-01 through VALD-04: custom node check with core alternatives, API node detection with auth warnings, full guideline compliance check, and cloud compatibility validation.

</domain>

<decisions>
## Implementation Decisions

### Validation Output
- Claude decides format (recommendation: report card with overall score + per-rule results, plus fix-first issue list)
- Claude decides severity levels (recommendation: error/warning/info — maps well to the strict/lenient modes below)

### Core Node Alternatives
- **Binary classification: core or custom** — if it's not in `data/core_nodes.json`, it's custom. No "approved custom" tier.
- Claude decides how to suggest core alternatives (curated mapping vs name similarity vs just flagging)

### Strictness Levels
- **Two modes: strict + lenient** — strict for final submission (all rules enforced), lenient for drafts (only blockers/errors)
- **Rule suppression via flag** — `--ignore core_node_preference` style flags to suppress specific rules when running validation
- Rules map to severity levels; lenient mode only reports errors, strict reports everything

### Cloud Compatibility
- Claude decides the depth of cloud checks (recommendation: API node auth detection + custom node registry availability check)
- Claude decides API node detection approach (hardcoded list vs pattern-based)

### Claude's Discretion
- Validation report format and severity levels
- Core node alternative suggestion approach
- Cloud compatibility check depth
- API node detection method
- Rule engine architecture (registry pattern, chain of validators, etc.)
- How to load and apply `data/guidelines.json` rules programmatically
- Integration with existing `format_detector.py` as first validation step

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Guidelines Data
- `data/guidelines.json` — 12 structured rules with IDs, descriptions, severity, examples. This is the machine-readable source of truth for validation rules
- `data/guidelines/` — 7 reference images showing visual rule examples (subgraph anti-patterns, note colors, API badge placement)

### Existing Infrastructure
- `src/shared/format_detector.py` — Distinguishes workflow format from API format. Should be the FIRST validation step
- `data/core_nodes.json` — 114 core node class_types. The whitelist for VALD-01 custom node detection
- `src/templates/cross_ref.py` — `build_pack_index()`, `extract_node_types()` for parsing nodes from workflow JSON (handles subgraphs)
- `src/templates/fetch.py` — `fetch_workflow_json()` for loading workflow JSON files
- `src/shared/categories.py` — `classify_node()` for categorizing nodes

### API Node Auth (from Phase 1 research)
- `C:/Users/minta/Projects/comfyui/REPORT-COMFYUI-MCP.md` — Known API nodes (Gemini, BFL, Bria, ByteDance, ElevenLabs, Recraft, Luma), hidden auth inputs (`auth_token_comfy_org`, `api_key_comfy_org`)
- `C:/Users/minta/Projects/comfyui/HANDOFF-MCP-IMPROVEMENTS.md` — Firebase JWT auth flow, how auth tokens are injected

### Research
- `.planning/research/PITFALLS.md` — Format confusion (#1), custom node dependency creep (#5), validation rules in Notion (#6)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/shared/format_detector.py` — `detect_format(json_data)` returns 'workflow' or 'api'. Ready to use as validation gate
- `data/core_nodes.json` — 114 entries, loadable as a set for O(1) lookup
- `data/guidelines.json` — 12 rules with `id`, `description`, `severity`, `examples`. Each rule needs a corresponding validator function
- `src/templates/cross_ref.py` — `extract_node_types()` handles subgraph recursion, returns set of class_types from a workflow JSON
- `src/templates/fetch.py` — `get_template_detail()` already extracts node types from workflow JSON

### Established Patterns
- Modules: Pydantic model → logic functions → format function → CLI entry point with argparse
- Tests: `unittest.mock.patch` for HTTP mocks, fixture data in test files
- Cache: `DiskCache` with configurable TTLs

### Integration Points
- New `src/validator/` module
- Skill definition: `.claude/skills/comfy-validate/SKILL.md`
- Validation takes a workflow JSON file path as input, outputs structured report

</code_context>

<specifics>
## Specific Ideas

- Format detection should be the first check — if it's API format, stop immediately with clear guidance
- Validation should work on both local workflow files and template URLs/names
- The lenient/strict distinction maps naturally to "in-progress draft" vs "ready for submission"

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-validation-engine*
*Context gathered: 2026-03-19*
