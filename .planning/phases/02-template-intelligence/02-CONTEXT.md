# Phase 2: Template Intelligence - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can browse existing 400+ templates, cross-reference nodes against the template library, and identify gaps worth filling. Delivers TMPL-01 through TMPL-05: template search, template detail view, node cross-reference, gap analysis, and coverage reporting.

</domain>

<decisions>
## Implementation Decisions

### Template Data Source
- **No local clone** — user explicitly rejected cloning as cumbersome
- Claude decides between GitHub API + cache or bundled snapshot approach (recommendation: fetch index.json via GitHub raw CDN, cache individual template JSONs on demand)
- **Daily cache with manual override** — 24hr TTL default, user can force refresh
- Use existing `src/shared/http.py` and `src/shared/cache.py` infrastructure from Phase 1

### Gap Analysis
- Claude decides popularity threshold and pack vs node level granularity
- **Both presentation views**: default ranked list sorted by opportunity score, plus `--by-category` flag for grouped view
- **Node info + suggestion**: when showing a gap, include the node details AND suggest what kind of template could use it (e.g., "Popular video upscaler — could pair with img2vid workflow")

### Cross-Reference UX
- **Exact class_type matching by default** — templates store nodes by class_type in workflow JSON, this is the reliable approach
- Optional fuzzy matching for "related" node discovery (e.g., all KSampler variants)
- **Count + examples**: "Used in 7 templates" + show top 3 examples with template name and category
- Results should carry forward in session context (Phase 1 decision: skills share context)

### Coverage Reporting
- **Four metrics**: templates per category, node coverage %, thin spots, growth trends
- Claude decides format (recommendation: drill-down — summary first, user can ask for category detail)

### Claude's Discretion
- GitHub API strategy (raw CDN for index.json vs API for individual files)
- GITHUB_TOKEN support for authenticated rate limits
- Popularity threshold for gap analysis (tiered approach recommended by research)
- Pack-level vs node-level gap granularity
- Coverage report format (summary vs drill-down)
- Reverse index data structure (node → templates mapping)
- Template search algorithm (substring, regex, or weighted)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Template Repository
- GitHub `Comfy-Org/workflow_templates/templates/index.json` — 400+ templates with full metadata schema (name, title, description, mediaType, models, tags, io, requiresCustomNodes, username, etc.)
- GitHub `Comfy-Org/workflow_templates/README.md` — Template structure, bundles, file naming conventions

### Existing Infrastructure (Phase 1)
- `src/shared/http.py` — HTTP client with `fetch_json()`, `get_client()`, GITHUB_TOKEN support
- `src/shared/cache.py` — `DiskCache` with per-query-type TTLs
- `src/shared/categories.py` — `classify_node()` maps nodes to template library categories (video, image, audio, 3d, llm, utility)
- `src/registry/models.py` — `NodePack`, `ComfyNode`, `SearchResult` Pydantic models
- `src/registry/highlights.py` — `fetch_all_nodes()` for bulk registry data, scoring heuristics
- `data/core_nodes.json` — 114 core node class_types for distinguishing core vs custom

### Research
- `.planning/research/SUMMARY.md` — Gap analysis is the killer differentiator
- `.planning/research/FEATURES.md` — Template intelligence feature landscape
- `.planning/research/ARCHITECTURE.md` — Template browser component design

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/shared/http.py` — `fetch_json()` with httpx, timeout, error handling. Already has User-Agent header. Can fetch from GitHub raw CDN directly
- `src/shared/cache.py` — `DiskCache` with configurable TTLs, JSON serialization. Ready for template data caching
- `src/shared/categories.py` — `classify_node()` with `CATEGORY_KEYWORDS`. Can classify both registry nodes AND template metadata for alignment
- `src/registry/models.py` — Pydantic models. Need new `Template` model for index.json entries
- `src/registry/highlights.py` — `fetch_all_nodes()` returns full registry snapshot. Gap analysis needs this for the "all nodes" side of the equation
- `data/core_nodes.json` — 114 core nodes. Useful for gap analysis to distinguish "popular custom node has no template" from "core node has no template"

### Established Patterns
- Modules follow pattern: Pydantic model → fetch function → format function → CLI entry point with argparse
- Tests use `unittest.mock.patch` to mock HTTP calls, test against fixture data
- Cache uses disk-based JSON files in `~/.cache/comfy-agent/`

### Integration Points
- New `src/templates/` module alongside existing `src/registry/`
- Gap analysis connects registry (Phase 1) to templates (Phase 2) — the cross-cutting feature
- Skill definition goes in `.claude/skills/comfy-templates/SKILL.md`

</code_context>

<specifics>
## Specific Ideas

- Gap analysis should include template suggestions — not just "this node has no template" but "this popular video upscaler could pair with an img2vid workflow"
- Coverage report should show all four metrics: template counts per category, node coverage %, thin spots, and growth trends
- Cross-reference should flow naturally from discovery: "I found this trending node → is it in a template?"

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-template-intelligence*
*Context gathered: 2026-03-19*
