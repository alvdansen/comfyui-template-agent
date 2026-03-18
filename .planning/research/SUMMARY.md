# Project Research Summary

**Project:** ComfyUI Template Agent
**Domain:** Claude Code agent toolkit for ComfyUI workflow template creation
**Researched:** 2026-03-18
**Confidence:** HIGH

## Executive Summary

This project is an internal Claude Code agent toolkit — not a web app, not an MCP server, not an LLM orchestration framework. The deliverable is a set of Claude Code skills (SKILL.md files) backed by importable Python modules that cover five phases of ComfyUI template creation: discover, ideate, compose, validate, and document. Research confirms this is the correct abstraction: skills are the native Claude Code interface, the team already uses them, and comfy-tip already demonstrates the pattern working. The stack is intentionally minimal — Python 3.12, httpx, Pydantic, jsonschema — with all other logic in stdlib. No framework needed.

The recommended build order is dictated by hard data dependencies: shared infrastructure first, then registry discovery (porting comfy-tip directly), then template browsing and gap analysis, then the validation engine, then metadata and documentation output, and finally the orchestrator skill that chains everything. Each phase produces artifacts the next phase consumes. The killer differentiator is gap analysis: cross-referencing 8,400+ registry nodes against 400+ existing templates to surface what should be built next. Everything else either exists (comfy-tip discovery) or is table stakes that prevents PR rejections (guideline validation).

The primary risks are all in the composition engine, which is the last and hardest phase. ComfyUI has two incompatible JSON formats (workflow format for templates, API format for execution) that look similar and confuse LLMs. Combined with the widget values positional array problem (positions map to parameters only via `/object_info` node definitions) and the LLM hallucination problem (12–15% baseline pass rate for raw LLM workflow generation per ComfyGPT paper), the Python builder module and format detector must be built before any generation work begins. Mitigation is clear: never let Claude construct raw workflow JSON — route all construction through a type-safe Python graph builder with per-step validation.

## Key Findings

### Recommended Stack

Three production dependencies (httpx, Pydantic, jsonschema) plus stdlib cover everything needed for v1. The MCP server option is deferred — it only adds value if other agents need programmatic access, which is not a v1 requirement. Existing comfy-tip code at `C:/Users/minta/Projects/comfy-tip/` is directly reusable for the registry module (adapt urllib to httpx, keep scoring heuristics). API node auth detection logic exists in `C:/Users/minta/Projects/comfyui/`.

**Core technologies:**
- **Python 3.12+**: Runtime — already on system, matches comfy-tip, required by MCP SDK
- **Claude Code Skills (SKILL.md)**: Agent interface — the native distribution format; no alternative
- **httpx 0.28+**: HTTP client for api.comfy.org + GitHub API — sync/async in one lib, proper timeout handling, better DX than comfy-tip's urllib
- **Pydantic 2.12+**: Workflow JSON models + data validation — type-safe models for nodes/links/widgets, 5-50x faster than v1
- **jsonschema 4.26+**: Validate against ComfyUI's official JSON Schema — distinct from Pydantic; ComfyUI publishes `index.schema.json`
- **pytest + ruff**: Dev tooling — ruff replaces flake8 + black in a single tool

**Not to use:** LangChain, FastAPI, SQLite, Docker, CrewAI, comfyui-mcp-server (that's for cloud workflow execution, not template creation).

### Expected Features

**Must have (table stakes):**
- Registry node discovery — already built via comfy-tip; wrap and integrate immediately
- Template library search + cross-reference lookup — parse index.json, build node-to-template reverse index
- Custom node dependency detection — compare workflow class_types against core node list, populate `requiresCustomNodes`
- API node auth detection — flag Gemini/BFL/ElevenLabs/etc. nodes with hidden auth inputs; logic exists locally
- Guideline validation — core node preference, no set/get nodes, naming conventions, model metadata completeness
- Template metadata generation — auto-extract models, io, tags from workflow JSON for 15+ index.json fields
- Notion-ready submission docs — markdown rendering, saves 15-20 min per submission

**Should have (differentiators):**
- Gap analysis — cross-reference 8,400+ registry nodes vs 400+ templates; the "what to build next" answer; the killer feature
- Guided phase workflow (/comfy-flow) — discover > ideate > compose > validate > document; prevents skipped steps
- Scaffold from existing template — clone + modify for common variations (txt2img -> img2img -> inpaint)
- Workflow composition from scratch — incremental graph edits + per-step validation (ComfySearch pattern); human-in-the-loop tolerates lower automation than academic benchmarks require
- Model requirement analysis — auto-detect models, VRAM estimates, download URLs for `models[]` array

**Defer to v2+:**
- Subgraph/blueprint awareness — ComfyUI 0.3.66+, community adoption still growing
- App Mode readiness check — low urgency until ComfyHub usage patterns are established
- Batch validation — trivial extension once single validation works
- MCP server interface — only if other agents need programmatic access

**Anti-features (never build):**
- Notion API integration — copy-paste is fine for v1
- Workflow execution/testing — requires GPU + model downloads, out of scope
- Auto-PR creation to workflow_templates — too dangerous
- RL/GRPO training infrastructure — overkill; human-in-the-loop makes it unnecessary

### Architecture Approach

Strict layered architecture: Skills (SKILL.md files as LLM instructions) sit on top of Python modules (registry, templates, composer, validator, metadata, document), which call external services (api.comfy.org, GitHub workflow_templates) and reference static data files (core_nodes.json, guidelines.json, index_schema.json). Workflow JSON is the central artifact — created by composer, validated by validator, consumed by metadata and document generators. Skills instruct Claude how to use modules via Bash tool calls; modules handle all data fetching, transformation, and schema validation.

**Major components:**
1. **Skills layer** (`.claude/skills/`) — 6 SKILL.md files: comfy-discover, comfy-ideate, comfy-compose, comfy-validate, comfy-document, comfy-flow (orchestrator)
2. **Registry module** (`src/registry/`) — api.comfy.org client, adapted from comfy-tip; trending/new/rising/search/spec
3. **Template browser** (`src/templates/`) — index.json parser, gap analysis engine, template loader from GitHub
4. **Composer** (`src/composer/`) — type-safe graph builder, scaffold from existing template, ComfyUI type system (IMAGE, LATENT, MODEL, CLIP, VAE, CONDITIONING)
5. **Validator** (`src/validator/`) — rule engine: core node preference, no set/get, subgraph conventions, model metadata, naming, io declaration
6. **Metadata + Document** (`src/metadata/`, `src/document/`) — index.json entry builder, Notion markdown formatter, submission packager
7. **Shared** (`src/shared/`) — HTTP client, disk cache with TTL, config
8. **Static data** (`data/`) — core_nodes.json, guidelines.json, index_schema.json

**Key anti-patterns to avoid:** Monolithic SKILL.md (one per phase instead), Claude constructing raw JSON (use Python builder), hardcoded node specs (fetch from registry at runtime), routing everything through comfyui-mcp (that's for cloud submission).

### Critical Pitfalls

1. **Workflow vs API format confusion** — Templates require workflow format (`nodes[]` + `links[]`); LLMs default to API format (`class_type` + flat node IDs). Prevent by: building a format detector as the first validation step; never generating API format for templates; hardcoding workflow format in all generation prompts. Address in Phase 1.

2. **Widget values positional mapping** — `widgets_values[]` is positional; mapping to parameter names requires loading node definitions from `/object_info`. LLMs guess wrong positions. Prevent by: fetching and caching `/object_info` node definitions; building a node schema registry before composition begins. Address in Phase 1-2.

3. **LLM node hallucination** — Raw LLM workflow generation achieves only 12-15% pass rate (ComfyGPT paper). LLMs fabricate plausible-sounding but non-existent node types. Prevent by: validating every `type` field against live registry; using a core node whitelist (~100 nodes) for template generation. Address in Phase 1.

4. **Link type mismatches** — ComfyUI connections are typed; mismatches compile but fail at execution. Prevent by: type checker resolving output types from node definitions, validating every link's `data_type` bidirectionally. Address in Phase 1-2.

5. **Custom node dependency creep** — Official guidelines require core nodes only; agents prefer custom nodes for convenience. Prevent by: tagging all nodes core/custom, defaulting to core-only mode, auto-populating `requiresCustomNodes`. Address in Phase 2.

6. **Validation rules trapped in Notion** — Guidelines live as unversioned prose; LLM interpretation is non-deterministic. Prevent by: extracting rules to structured `data/guidelines.json` with named validators (rule ID + check logic + severity). Address as data task in Phase 1, validation code in Phase 2.

## Implications for Roadmap

The build order is dictated by hard data dependencies, confirmed by the architecture research's explicit build order. The phases below follow the architecture research exactly, with pitfall prevention mapped to each.

### Phase 1: Foundation + Discovery
**Rationale:** Nothing else works without HTTP infrastructure, static data files, node registry access, and format detection. Registry discovery (comfy-tip port) delivers immediate value with minimal risk. Format detection and node type system must be locked down here — before any composition logic is written.
**Delivers:** Shared infrastructure (http, cache, config), format detector, core node whitelist, `/comfy-discover` skill, working registry queries (trending/new/rising/search/spec)
**Addresses:** Registry node discovery (table stakes), node hallucination prevention, format confusion prevention
**Avoids:** Pitfalls 1 (format confusion) and 3 (node hallucination) — both must be solved before Phase 3
**Research flag:** Standard patterns. comfy-tip code exists and works. Registry API is documented. No research-phase needed.

### Phase 2: Template Intelligence + Validation
**Rationale:** Template library search, gap analysis, and the validation engine form a natural group — gap analysis needs both registry (Phase 1) and template data, and validation builds on the node schema awareness started in Phase 1. Combining these phases avoids a thin "template search only" phase.
**Delivers:** `/comfy-ideate` skill with gap analysis, template browser, node-to-template reverse index, `/comfy-validate` skill with full rule engine (core node preference, no set/get, model metadata, API node auth, naming, io)
**Addresses:** Template library search, cross-reference lookup, gap analysis (killer feature), guideline validation, custom node detection, API node auth detection
**Avoids:** Pitfalls 4 (custom node creep), 5 (link type mismatches), 6 (Notion rules drift)
**Research flag:** Standard patterns for gap analysis (set operations) and rule engine. The Notion guidelines extraction is a manual data task that must happen before this phase can be planned in detail — flag for early action.

### Phase 3: Composition Engine
**Rationale:** The hardest technical challenge. Must come after Phase 1 (needs node registry for specs) and Phase 2 (scaffold mode needs template loader). Widget value mapping and link type checking are the key engineering problems here.
**Delivers:** `/comfy-compose` skill, type-safe graph builder (add node, connect ports, set widget values), scaffold-from-template mode, valid workflow.json output
**Addresses:** Scaffold from existing template, workflow composition from scratch (both differentiators)
**Avoids:** Pitfalls 2 (widget value mapping) and 4 (link type mismatches); anti-pattern of raw JSON generation
**Research flag:** Needs research-phase during planning. Incremental graph edit strategy (ComfySearch pattern), widget-to-position mapping implementation, and type-safe link construction API design all need design work before coding. `/object_info` caching strategy must be resolved (see Gaps).

### Phase 4: Documentation + Submission
**Rationale:** Documentation is last in the core workflow because it consumes outputs from all other phases: workflow JSON (Phase 3), validation report (Phase 2), and registry metadata (Phase 1). Metadata auto-extraction only works accurately after the workflow is validated.
**Delivers:** `/comfy-document` skill, index.json entry builder, Notion markdown output, full submission package (workflow.json + index entry + notion.md + pre-PR checklist)
**Addresses:** Template metadata generation, model requirement analysis, Notion submission docs (all table stakes)
**Avoids:** UX pitfall of generating metadata before validation (metadata would reference a broken workflow)
**Research flag:** Standard patterns. index.json schema is fully documented. Markdown formatting is straightforward.

### Phase 5: Orchestration + Polish
**Rationale:** The guided end-to-end workflow (/comfy-flow) can only be built after all individual phase skills work independently. Subgraph awareness and App Mode checks are forward-looking additions with low urgency.
**Delivers:** `/comfy-flow` orchestrator skill, guided discover-to-submit workflow, batch validation, optional subgraph awareness
**Addresses:** Guided phase workflow (differentiator), subgraph/blueprint support (v2 feature), App Mode readiness checks
**Research flag:** Standard patterns for SKILL.md orchestration. Subgraph format needs research-phase if implemented (new feature, still evolving).

### Phase Ordering Rationale

- **Dependency order is non-negotiable:** Validator needs workflow JSON (composer). Metadata needs validator output. Document needs metadata. This is a hard dependency chain, not stylistic choice.
- **Foundation pitfalls addressed first:** Format confusion and node hallucination corrupt everything downstream. Discovering a format bug in Phase 3 means rewriting the composer.
- **Composition is the only phase with genuine technical uncertainty:** Everything else is well-documented with existing code to reference. The graph builder + widget schema + type system is the only novel engineering in this project. It warrants a research-phase.
- **Reuse before build:** comfy-tip (registry), comfyui-mcp API node detection logic, and existing template index data reduce Phase 1-2 effort substantially.

### Research Flags

Needs research-phase during planning:
- **Phase 3 (Composition Engine):** Incremental graph edit strategy, widget-to-position mapping implementation, `/object_info` caching approach, type-safe link construction API design. ComfySearch paper outlines the pattern but implementation details need design work before coding.
- **Phase 5 (if subgraph support):** Subgraph format (`definitions.subgraphs`) is new (2025-2026) and still evolving; needs current documentation review before planning.

Standard patterns (skip research-phase):
- **Phase 1:** Registry API documented, comfy-tip code exists and works, HTTP caching is standard
- **Phase 2:** index.json schema is public, set operations for gap analysis are straightforward, rule engine pattern is standard
- **Phase 4:** index.json schema + markdown formatting fully specified

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All dependency versions verified on PyPI; comfy-tip confirms the skills + Python modules pattern works; SKILL.md format is documented by Anthropic |
| Features | MEDIUM-HIGH | Table stakes verified from official template repo + ComfyUI docs; differentiators validated by competitive research (3 academic papers); composition complexity backed by ComfyGPT/ComfySearch failure mode analysis |
| Architecture | HIGH | Build order confirmed by dependency analysis; comfy-tip and comfyui-mcp provide working reference implementations; component boundaries map directly to the template creation workflow |
| Pitfalls | MEDIUM-HIGH | Format confusion + hallucination verified against ComfyGPT paper and GitHub issues; widget mapping documented in official spec; other pitfalls are domain-standard with clear mitigations |

**Overall confidence:** HIGH

### Gaps to Address

- **`/object_info` endpoint strategy:** Widget-to-position mapping requires node definitions from a running ComfyUI server. Options: (1) bundle core node definitions as a static snapshot in `data/`, (2) query registry API as fallback, (3) require ComfyUI running for composition. Must decide before Phase 3 design. Recommended: bundle snapshot for core nodes (~100), fetch dynamically for custom nodes.

- **Core node whitelist completeness:** The validation engine needs a complete list of core nodes shipped with vanilla ComfyUI. Must be extracted from the ComfyUI repo and maintained in `data/core_nodes.json`. Establish a sync process at project start before Phase 1 is planned.

- **Notion guidelines extraction:** Team's template creation guidelines live in Notion as prose. Must be converted to structured JSON validators before Phase 2 can be fully planned. This is a human data task, not an engineering problem — needs to happen in parallel with Phase 1 development.

- **GitHub API rate limits:** Unauthenticated rate is 60 req/hr. Template browser fetching individual template JSONs during gap analysis could hit this. Build `GITHUB_TOKEN` env var support into Phase 1's HTTP client; use GitHub raw content CDN for bulk reads.

- **Registry API coverage:** comfy-tip fetches ~300 nodes (6 pages). Full registry is 8,400+. Gap analysis needs broader coverage. The registry API likely supports search/filter endpoints for targeted queries — verify during Phase 2 planning.

## Sources

### Primary (HIGH confidence)
- [ComfyUI Workflow JSON Spec](https://docs.comfy.org/specs/workflow_json) — workflow format v1.0, node/link structure, schema fields
- [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates) — template repo structure, index.json schema, 400+ templates
- [ComfyUI Registry API](https://docs.comfy.org/registry/api-reference/overview) — node search, metadata, 8,400+ nodes
- [ComfyUI Template Documentation](https://docs.comfy.org/interface/features/template) — contribution guidelines, validation rules
- [Claude Code Skills docs](https://code.claude.com/docs/en/skills) — SKILL.md format specification
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) — v1.26.0, FastMCP pattern
- comfy-tip source (`C:/Users/minta/Projects/comfy-tip/`) — working registry discovery implementation
- comfyui-mcp reports (`C:/Users/minta/Projects/comfyui/`) — API node auth detection logic

### Secondary (MEDIUM confidence)
- [ComfySearch paper](https://arxiv.org/html/2601.04060v1) — incremental graph edit pattern, 92.5% pass rate, entropy-adaptive branching
- [ComfyGPT paper](https://arxiv.org/html/2503.17671v1) — 12-15% baseline LLM pass rate, multi-agent decomposition
- [ComfyMind paper](https://arxiv.org/abs/2505.17908) — semantic workflow interface, tree-based planning, 100% pass rate
- [ComfyUI App Mode announcement](https://blog.comfy.org/p/from-workflow-to-app-introducing) — March 2026 launch, ComfyHub marketplace
- [ComfyUI Subgraph Documentation](https://docs.comfy.org/interface/features/subgraph) — blueprint format, new feature still evolving

### Tertiary (MEDIUM confidence, community sources)
- [GitHub Issue #1335](https://github.com/comfyanonymous/ComfyUI/issues/1335) — workflow vs API format confusion, community discussion
- [Discussion #4787](https://github.com/comfyanonymous/ComfyUI/discussions/4787) — widget values positional mapping pain points

---
*Research completed: 2026-03-18*
*Ready for roadmap: yes*
