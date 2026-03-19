# Phase 1: Foundation + Discovery - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver shared infrastructure (HTTP client, caching, static data files, format detector) and registry node discovery capabilities (DISC-01 through DISC-05). Users can discover trending/new/rising/popular/random nodes, search by name/category/type, filter by media category, inspect node packs, and get random suggestions for ideation. Also extract template creation guidelines from Notion export into machine-readable format as a data task.

</domain>

<decisions>
## Implementation Decisions

### Skill Interface
- **Multiple separate skills**, not one monolithic command — each task does something different
- Skills accept **both natural language and explicit flags** — "find me trending video nodes" works, so does explicit arguments
- **Progressive detail**: summary cards by default (name, author, description, downloads/stars, repo link), user can ask for detailed specs on specific nodes
- Claude picks the naming prefix (recommendation: `/comfy-*` for consistency with existing comfy-tip)
- **Random mode offers both options**: weighted random (biased toward quality) AND truly random, user picks

### Registry Coverage
- **Hybrid fetch strategy**: bulk fetch for trending/popular modes (needs breadth for scoring), search endpoint for targeted queries
- Claude picks appropriate **cache TTLs per query type** (trending can be longer, search should be fresher)

### Category Filtering
- **Map registry tags to template library categories** (Image, Video, Audio, 3D Model, LLM, Utility) so discovery results align with the template library structure
- Support both registry tags and template categories in queries

### Node Pack Info
- Claude decides the best data source for node-level specs (registry API first, GitHub scrape as fallback if needed)

### Cross-Skill Context
- **Skills share session context** so discovery results carry forward — "I found this node, now check if it's in a template" works without copy-pasting IDs
- Node IDs also shown in output for manual use

### Project Structure
- **GSD-informed structure** — take the formulaic thinking and best practices from GSD, but make it feel specific to ComfyUI template work, not a generic copy
- Claude decides package layout (recommendation: proper Python package with CLI entry points, referencing GSD's structured approach)
- Claude designs the install flow for team members
- **Full pytest from Phase 1** — tests for registry client, caching, scoring, CLI interface
- Claude decides config approach (env vars vs config file)

### Data Sources
- **Core node whitelist**: Claude investigates the best extraction method (ComfyUI repo parse vs registry API filter vs manual curation) and picks what works
- **Template guidelines extraction**: Do in Phase 1 as a data task — extract Notion guidelines into `data/guidelines.json`
- **Keep 6 key images** from the Notion export that illustrate visual rules hard to capture in text:
  - image.png — custom node usage vs core node (rule 1)
  - image 2.png — thumbnail content types & hover effects grid
  - image 3.png — API node provider badge placement (avoid top-left)
  - image 4.png — anti-pattern: identically-named subgraphs with different internals
  - image 7.png — correct pattern: settings outside subgraphs
  - image 8.png — anti-pattern: Preview/Save nodes inside subgraphs
  - image 10.png — Note node color convention (black) vs API node color (yellow)
- Text-only descriptions sufficient for remaining images

### Format Detector
- Claude decides whether standalone utility or built into validation (recommendation: standalone shared function since it's used by multiple modules)

### Claude's Discretion
- Package layout specifics (flat scripts vs proper package with entry points)
- HTTP client library choice (httpx recommended by research)
- Cache implementation details
- Config management approach
- Naming prefix for skills
- Format detector integration pattern

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### ComfyUI Registry API
- `C:/Users/minta/Projects/comfy-tip/highlights.py` — Working registry client with trending/rising/popular/random scoring heuristics. Port and adapt, don't rewrite from scratch
- `C:/Users/minta/Projects/comfy-tip/mcp_integration.py` — MCP tool definition pattern for node discovery
- `C:/Users/minta/Projects/comfy-tip/skill/SKILL.md` — Existing Claude Code skill for comfy-tip

### ComfyUI Template Format
- GitHub `Comfy-Org/workflow_templates` — 400+ templates, `templates/index.json` defines metadata schema (name, title, description, mediaType, models, tags, io, requiresCustomNodes, etc.)
- `C:/Users/minta/Projects/comfyui/REPORT-COMFYUI-MCP.md` — API node auth detection, silent failure patterns, MCP server architecture
- `C:/Users/minta/Projects/comfyui/HANDOFF-MCP-IMPROVEMENTS.md` — Firebase JWT auth flow, API node hidden inputs

### Template Creation Guidelines (Notion export)
- `/tmp/notion-export/ComfyUI Template Creation Guidelines 3036d73d36508065828bd336f51ba3eb.md` — Full guidelines text: core node preference, subgraph rules, thumbnail specs, color/note conventions, submission process
- Key images to keep in `data/guidelines/`: image.png, image 2.png, image 3.png, image 4.png, image 7.png, image 8.png, image 10.png

### Research
- `.planning/research/STACK.md` — 3-dep stack recommendation (httpx, Pydantic, jsonschema)
- `.planning/research/ARCHITECTURE.md` — Six-component architecture, build order
- `.planning/research/PITFALLS.md` — Format confusion, LLM hallucination, widget mapping risks

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `comfy-tip/highlights.py` — Complete registry client: fetch, score, format. ~190 lines. Uses urllib (upgrade to httpx). Scoring heuristics for trending/rising/popular/random are production-ready
- `comfy-tip/mcp_integration.py` — Drop-in MCP tool handler pattern
- `comfyui/REPORT-COMFYUI-MCP.md` — API node list (Gemini, BFL, Bria, ByteDance, ElevenLabs, Recraft, Luma) with auth detection patterns

### Established Patterns
- comfy-tip uses 1hr cache TTL with JSON file caching — simple, works
- Registry API: `GET /nodes?page={N}&limit=50` returns paginated node list with status, downloads, stars, tags, repository fields
- Template index.json: 8 categories (Use Cases, Image, Video, Audio, 3D Model, LLM, Utility, Getting Started) with detailed per-template metadata

### Integration Points
- Skills will live in this repo's `skills/` directory, symlinked to `~/.claude/skills/` on install
- Python modules invoked via `python3 -m comfy_agent <subcommand>` from SKILL.md instructions
- Existing comfyui-cloud MCP server provides `search_models`, `search_nodes`, `submit_workflow` — these complement but don't replace what we're building

</code_context>

<specifics>
## Specific Ideas

- "Use GSD as an abstract structural reference — not copying exactly, but pulling best practices and formulaic thinking. It should feel more structured but specific to this work"
- Skills should feel natural language promptable — "find me trending video nodes" just works
- Discovery results should carry forward in conversation context for cross-skill workflows

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-foundation-discovery*
*Context gathered: 2026-03-18*
