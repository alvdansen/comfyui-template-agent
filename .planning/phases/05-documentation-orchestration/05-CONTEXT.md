# Phase 5: Documentation + Orchestration - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can generate submission-ready documentation and run the full discover-to-document workflow as a guided session. Delivers DOCS-01 through DOCS-04 (index.json metadata, Notion markdown, IO extraction, thumbnail reminders) and ORCH-01, ORCH-02 (guided flow, context-aware suggestions).

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion (all areas)

User gave full discretion for this phase. Recommendations below:

**Metadata Generation (DOCS-01, DOCS-03):**
- Auto-extract from workflow JSON: name, mediaType, io (inputs/outputs), requiresCustomNodes, models (from model loader nodes)
- Prompt user for: title, description, tags (these need human judgment)
- Auto-generate sensible defaults for: size, vram (estimate from model count), date (today), username
- Output as valid index.json entry ready to paste into the template repo

**Notion Markdown (DOCS-02):**
- Generate submission-ready markdown matching the team's Notion format
- Include: workflow link, thumbnail specs reminder, custom node dependencies, model list, description
- Output as copy-pasteable text, not direct Notion API integration (v1 decision from PROJECT.md)

**IO Extraction (DOCS-03):**
- Parse workflow JSON for LoadImage/SaveImage/PreviewImage nodes
- Map to io.inputs[] and io.outputs[] with nodeId, nodeType, file, mediaType fields
- Handle subgraph-wrapped I/O nodes

**Thumbnail Reminders (DOCS-04):**
- At the right point in the flow, remind about: 1:1 ratio, 3-5s video, use workflow output not screenshots
- Reference thumbnail content types (image/video/audio) and hover effects from guidelines
- Remind about API badge top-left avoidance rule

**Guided Flow (ORCH-01, ORCH-02):**
- `/comfy-flow` orchestrator skill that chains: discover → ideate → compose → validate → document
- Each step carries context forward via session state
- Context-aware suggestions: after discovery, suggest templates to scaffold; after composition, auto-run validation; after validation passes, generate docs
- User can enter at any step (not forced to start from discover)
- User can exit and resume at any step

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Template Format
- GitHub `Comfy-Org/workflow_templates/templates/index.json` — metadata schema for template entries (name, title, description, mediaType, models, tags, io, requiresCustomNodes, size, vram, usage, thumbnail, etc.)
- `data/guidelines.json` — 12 rules including thumbnail_specs, naming_conventions

### Existing Infrastructure (all phases)
- `src/registry/` — highlights, search, spec (discovery)
- `src/templates/` — fetch, search, cross_ref, coverage (template intelligence)
- `src/validator/` — engine, rules, validate (validation)
- `src/composer/` — graph, scaffold, layout, compose, node_specs (composition)
- `src/shared/` — http, cache, config, format_detector, categories
- `.claude/skills/comfy-discover/SKILL.md` — discovery skill
- `.claude/skills/comfy-templates/SKILL.md` — template intelligence skill
- `.claude/skills/comfy-validate/SKILL.md` — validation skill
- `.claude/skills/comfy-compose/SKILL.md` — composition skill

### Notion Submission Template
- `/tmp/notion-export/ComfyUI Template Creation Guidelines*.md` — submission process reference

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/templates/fetch.py` — `get_template_detail()` extracts node types from workflow JSON
- `src/templates/cross_ref.py` — `extract_node_types()` with subgraph recursion
- `src/composer/graph.py` — `WorkflowGraph.serialize()` produces valid workflow JSON
- `src/validator/engine.py` — `run_validation()` for post-composition compliance check
- `src/shared/format_detector.py` — format gating
- `data/core_nodes.json` — 114 core nodes for requiresCustomNodes detection
- `data/guidelines.json` — thumbnail_specs rule has dimensions, format, content_types

### Established Patterns
- Pydantic model → logic functions → format function → CLI entry point with argparse
- Skills: SKILL.md with natural language + explicit flags
- All skills share session context

### Integration Points
- New `src/document/` module for metadata + Notion output
- `/comfy-flow` orchestrator skill chains all 4 existing skills + document skill
- CLI: `python -m src.document.metadata` and `python -m src.document.notion`

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches. Full Claude discretion.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-documentation-orchestration*
*Context gathered: 2026-03-19*
