# Architecture Research

**Domain:** Claude Code agent toolkit for ComfyUI template creation
**Researched:** 2026-03-18
**Confidence:** HIGH

## System Overview

```
+------------------------------------------------------------------+
|                    Claude Code Session                             |
|  +------------------------------------------------------------+  |
|  |                  Skills Layer (SKILL.md)                    |  |
|  |  /comfy-discover  /comfy-ideate  /comfy-compose             |  |
|  |  /comfy-validate  /comfy-document  /comfy-flow              |  |
|  +------+--------+--------+--------+---------+--------+-------+  |
|         |        |        |        |         |        |          |
|  +------v--------v--------v--------v---------v--------v-------+  |
|  |                    Core Library (Python)                    |  |
|  |  +-----------+  +----------+  +-----------+  +-----------+ |  |
|  |  | registry  |  | template |  | composer  |  | validator | |  |
|  |  | (discover)|  | (browse) |  | (build)   |  | (check)   | |  |
|  |  +-----------+  +----------+  +-----------+  +-----------+ |  |
|  |  +-----------+  +----------+                               |  |
|  |  | metadata  |  | document |                               |  |
|  |  | (index)   |  | (notion) |                               |  |
|  |  +-----------+  +----------+                               |  |
|  +-----+---------------+---------------+---------------------+  |
|        |               |               |                         |
+--------+---------------+---------------+-------------------------+
         |               |               |
   +-----v-----+  +-----v-----+  +------v------+
   | api.comfy  |  | GitHub    |  | comfyui-mcp |
   | .org       |  | workflow_ |  | (Cloud API) |
   | (Registry) |  | templates |  |             |
   +-----------+  +-----------+  +-------------+
```

### Component Responsibilities

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| **Skills (SKILL.md files)** | User-facing entry points. Each skill is a Claude Code slash command with instructions for the LLM | Markdown files with `---` frontmatter, installed in `.claude/skills/` |
| **Registry module** | Node discovery from api.comfy.org -- trending, new, rising, search, node spec lookup | Python, wraps comfy-tip's `highlights.py` + adds `comfy_search`/`comfy_spec` calls |
| **Template browser** | Browse/search the 400+ existing templates, check coverage gaps, find what nodes are already used | Python, parses `index.json` from workflow_templates repo (GitHub API or local clone) |
| **Composer** | Build valid ComfyUI workflow JSON from scratch or by scaffolding from existing templates | Python, node graph builder with type-safe link construction |
| **Validator** | Check workflows against template guidelines (core node preference, no set/get, subgraph rules, color/note conventions) | Python, rule engine applied to workflow JSON |
| **Metadata generator** | Produce `index.json` entries matching the workflow_templates schema | Python, schema-aware builder with field validation |
| **Document formatter** | Generate Notion-friendly markdown for the submission process | Python, template-based markdown output |
| **Orchestrator skill** | `/comfy-flow` -- the guided end-to-end workflow that chains discover > ideate > compose > validate > document | SKILL.md that instructs Claude to run the phases in order |

## Recommended Project Structure

```
comfyui-template-agent/
+-- .claude/
|   +-- skills/
|   |   +-- comfy-discover/
|   |   |   +-- SKILL.md          # Node discovery & trend surfacing
|   |   +-- comfy-ideate/
|   |   |   +-- SKILL.md          # Template gap analysis & concept generation
|   |   +-- comfy-compose/
|   |   |   +-- SKILL.md          # Workflow JSON creation (from scratch or scaffold)
|   |   +-- comfy-validate/
|   |   |   +-- SKILL.md          # Guideline compliance checking
|   |   +-- comfy-document/
|   |   |   +-- SKILL.md          # Metadata + Notion markdown generation
|   |   +-- comfy-flow/
|   |       +-- SKILL.md          # Guided end-to-end orchestrator
|   +-- commands/                  # Optional: Claude Code custom commands
|   +-- settings.local.json
+-- src/
|   +-- registry/
|   |   +-- __init__.py
|   |   +-- highlights.py         # Adapted from comfy-tip (trending/new/rising/popular)
|   |   +-- search.py             # Node pack search + individual node lookup
|   |   +-- spec.py               # Node input/output spec retrieval
|   |   +-- cache.py              # Shared HTTP + disk caching
|   +-- templates/
|   |   +-- __init__.py
|   |   +-- browser.py            # Browse/search existing templates from index.json
|   |   +-- coverage.py           # Gap analysis: what nodes/categories lack templates
|   |   +-- loader.py             # Load template JSON from repo (GitHub API or local)
|   +-- composer/
|   |   +-- __init__.py
|   |   +-- graph.py              # Node graph data model (nodes, links, groups)
|   |   +-- builder.py            # Fluent API for constructing workflows programmatically
|   |   +-- scaffold.py           # Clone + modify existing template as starting point
|   |   +-- types.py              # ComfyUI type system (IMAGE, LATENT, MODEL, CLIP, etc.)
|   +-- validator/
|   |   +-- __init__.py
|   |   +-- rules.py              # Individual validation rules
|   |   +-- checker.py            # Run all rules against a workflow, produce report
|   |   +-- guidelines.py         # Encoded template creation guidelines
|   +-- metadata/
|   |   +-- __init__.py
|   |   +-- index_entry.py        # Build index.json entries from workflow + user input
|   |   +-- schema.py             # index.json schema definition + validation
|   +-- document/
|   |   +-- __init__.py
|   |   +-- notion.py             # Notion-friendly markdown formatter
|   |   +-- submission.py         # Full submission package (metadata + docs + checklist)
|   +-- shared/
|       +-- http.py               # Shared HTTP client (urllib, no deps)
|       +-- cache.py              # Disk cache with TTL
|       +-- config.py             # Configuration (API URLs, cache paths, etc.)
+-- data/
|   +-- core_nodes.json           # List of ComfyUI core nodes (for core-node-preference validation)
|   +-- guidelines.json           # Template creation guidelines in machine-readable form
|   +-- index_schema.json         # index.json JSON Schema for validation
+-- tests/
|   +-- test_registry.py
|   +-- test_composer.py
|   +-- test_validator.py
|   +-- test_metadata.py
+-- .planning/                    # GSD project management
+-- CLAUDE.md                     # Project-level instructions
+-- pyproject.toml                # Python project config (no external deps in v1)
```

### Structure Rationale

- **`.claude/skills/`:** Each skill is a self-contained SKILL.md. Claude Code discovers them automatically. One skill per phase of the template creation workflow, plus the orchestrator.
- **`src/` with domain modules:** Clean separation by responsibility. Each module can be developed and tested independently. The composer doesn't know about validation; the validator doesn't know about Notion docs.
- **`data/`:** Static reference data that changes slowly. Core node lists, guidelines, and schemas are loaded at runtime by the Python modules. These are the "knowledge" the agent uses to make decisions.
- **No external dependencies in v1:** `urllib.request` for HTTP, `json` for parsing, `pathlib` for files. This keeps installation trivial -- just clone the repo and the skills are available.

## Architectural Patterns

### Pattern 1: Skills as LLM Instructions, Not Code Entry Points

**What:** Each SKILL.md is a prompt that tells Claude _how_ to use the Python modules, not a traditional CLI entry point. The skill describes the workflow, the expected inputs/outputs, and when to call which Python function. Claude reads the skill, then executes Python via Bash tool calls.

**When to use:** Always. This is the fundamental pattern for Claude Code skills.

**Trade-offs:** Claude has full flexibility to adapt the workflow to the user's request (good). But the LLM can deviate from the intended flow if instructions aren't precise enough (mitigated by clear, specific SKILL.md content).

**Example SKILL.md structure:**
```markdown
---
name: comfy-discover
description: Discover trending and new ComfyUI nodes for template inspiration
---

# Node Discovery

## What This Does
Surfaces interesting nodes from the ComfyUI registry for template creation.

## How to Use

1. Run the discovery script:
   ```bash
   python3 src/registry/highlights.py --mode trending
   ```

2. For each interesting node, get its spec:
   ```bash
   python3 src/registry/spec.py <node_pack_id>
   ```

3. Cross-reference with existing templates:
   ```bash
   python3 src/templates/coverage.py --check-node <node_pack_id>
   ```

## Output Format
Present findings as a table: Node | Category | Downloads | Already Templated?
```

### Pattern 2: Python Modules as Claude's Toolbox

**What:** Python modules expose simple functions that Claude calls via `python3 -c "..."` or `python3 src/module/script.py --args`. Each function does one thing: fetch data, validate a workflow, generate output. Claude orchestrates the sequence.

**When to use:** For all data fetching, transformation, and validation. Claude should not be constructing raw HTTP requests or parsing JSON schemas inline -- the Python modules handle that.

**Trade-offs:** Requires the Python modules to have clean CLI interfaces or importable functions. Slightly more upfront work than having Claude do everything inline, but dramatically more reliable and testable.

### Pattern 3: Workflow JSON as the Central Artifact

**What:** The ComfyUI workflow JSON is the primary data artifact that flows through the system. It's created by the composer, validated by the validator, and used to generate metadata and documentation. All components accept or produce workflow JSON.

**When to use:** Whenever data moves between components.

**Data flow:**
```
Registry data (nodes, specs)
       |
       v
  [Composer] --> workflow.json --> [Validator] --> validation report
       |                               |
       v                               v
  [Metadata gen] --> index entry    [User fixes issues]
       |
       v
  [Doc formatter] --> notion.md + submission checklist
```

### Pattern 4: Static Data Files as Encoded Knowledge

**What:** Template creation guidelines, core node lists, and the index.json schema are stored as JSON files in `data/`. The Python modules load these at runtime. This separates "what the rules are" from "how to check them."

**When to use:** For any domain knowledge that changes independently of code logic.

**Trade-offs:** Easier to update rules without touching code. But the data files must stay in sync with the upstream workflow_templates repo (manual process for now).

## Data Flow

### Discovery Flow

```
User: "What's trending?"
    |
    v
/comfy-discover skill
    |
    v
registry/highlights.py --> api.comfy.org/nodes?page=N
    |                          |
    |                          v
    |                    Node metadata (name, downloads, stars, created_at)
    |                          |
    v                          v
registry/search.py      Score + rank (trending/rising/new heuristics)
    |                          |
    v                          v
templates/coverage.py   "Already has template?" check against index.json
    |
    v
Formatted discovery report to user
```

### Composition Flow

```
User: "Build a template for [use case]"
    |
    v
/comfy-compose skill
    |
    +---> Option A: From scratch
    |         |
    |         v
    |    registry/spec.py --> get node inputs/outputs/types
    |         |
    |         v
    |    composer/builder.py --> construct node graph
    |         |                    - Add nodes with correct class_type
    |         |                    - Wire links with type-safe connections
    |         |                    - Set widget_values
    |         |                    - Add groups + notes
    |         v
    |    workflow.json
    |
    +---> Option B: Scaffold from existing
              |
              v
         templates/loader.py --> fetch template JSON from repo
              |
              v
         composer/scaffold.py --> clone + modify
              |                    - Swap nodes
              |                    - Adjust connections
              |                    - Update widget values
              v
         workflow.json
```

### Validation Flow

```
workflow.json
    |
    v
/comfy-validate skill
    |
    v
validator/checker.py
    |
    +-- rules.py: core_node_preference (flag custom nodes, suggest core alternatives)
    +-- rules.py: no_set_get_nodes (reject Set/Get nodes in templates)
    +-- rules.py: subgraph_conventions (check subgraph usage rules)
    +-- rules.py: color_note_standards (verify color coding and note nodes)
    +-- rules.py: api_node_auth (flag API nodes, document auth requirements)
    +-- rules.py: model_metadata (check models have url, hash, directory fields)
    +-- rules.py: io_declaration (verify inputs/outputs are properly declared)
    +-- rules.py: naming_convention (snake_case filename, no special chars)
    |
    v
Validation report: PASS/WARN/FAIL per rule, with fix suggestions
```

### Documentation Flow

```
workflow.json + validation report + user input (title, description, tags)
    |
    v
/comfy-document skill
    |
    v
metadata/index_entry.py --> build index.json entry
    |                          - name, title, description
    |                          - mediaType, mediaSubtype
    |                          - models[] (extracted from workflow nodes)
    |                          - requiresCustomNodes[] (from validator)
    |                          - io.inputs/outputs (from workflow LoadImage/SaveImage nodes)
    |                          - tags, date, openSource, size, vram
    |
    v
document/notion.py --> Notion-friendly markdown
    |                    - Template overview
    |                    - Node dependency table
    |                    - Model requirements
    |                    - Screenshot/thumbnail reminder
    |                    - Testing checklist
    |
    v
document/submission.py --> full submission package
                            - workflow.json (the file)
                            - index.json entry (to merge into repo)
                            - notion.md (to paste into Notion)
                            - pre-PR checklist
```

### Key Data Flows Summary

1. **Registry --> Composer:** Node specs (inputs, outputs, types) inform workflow construction. The composer needs to know what a node accepts before wiring it.
2. **Templates --> Composer:** Existing templates serve as scaffolds. The loader provides full workflow JSON that the scaffold module can clone and modify.
3. **Composer --> Validator:** The composed workflow JSON is the input to validation. Every rule operates on the JSON structure.
4. **Validator --> Metadata:** Validation results feed into metadata -- `requiresCustomNodes` comes from the custom node detection rule, API node flags inform documentation.
5. **Everything --> Document:** The doc formatter consumes workflow JSON, index entry, and validation report to produce the complete submission package.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **api.comfy.org** | REST API via `urllib.request` | Public, no auth needed. Rate limit unknown but generous. Cache responses (1hr TTL). |
| **GitHub (workflow_templates)** | `gh api` CLI or raw GitHub API | Public repo. Use `gh api repos/Comfy-Org/workflow_templates/contents/...` for file access. Cache index.json locally. |
| **comfyui-mcp** | MCP tools (`comfy_search`, `comfy_spec`, `submit_workflow`) | Already installed as MCP server. Use for cloud submission and model search. Not needed for template creation itself. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Skill --> Python module | Bash tool (`python3 src/...`) | Skills instruct Claude to run Python. Output is stdout (JSON or formatted text). |
| Registry --> Templates | Python import | `coverage.py` imports from registry to cross-reference. Shared data model for node identifiers. |
| Composer --> Registry | Python import | Builder calls `spec.py` to get node type info for link validation. |
| Validator --> Data files | File read (`json.load`) | Rules load `core_nodes.json` and `guidelines.json` at check time. |
| Metadata --> Workflow JSON | Direct parse | Metadata generator reads the workflow JSON to extract models, nodes, IO declarations. |

## Build Order (Dependency Chain)

The components have clear dependencies that dictate implementation order:

```
Phase 1: Foundation
  src/shared/ (HTTP, cache, config)
  data/ (core_nodes.json, guidelines.json, index_schema.json)
    |
Phase 2: Discovery + Browse
  src/registry/ (adapted from comfy-tip)
  src/templates/browser.py + loader.py
  /comfy-discover skill
    |
Phase 3: Composition
  src/composer/ (graph model, builder, scaffold)
  /comfy-compose skill
    |  (needs registry for node specs)
    |
Phase 4: Validation
  src/validator/ (rules, checker)
  /comfy-validate skill
    |  (needs composer output to validate)
    |
Phase 5: Documentation
  src/metadata/ (index entry builder)
  src/document/ (notion formatter, submission packager)
  /comfy-document skill
    |  (needs validator output for custom node flags)
    |
Phase 6: Orchestration
  /comfy-flow skill (chains all phases)
    |  (needs all other skills working)
```

**Rationale:** Each phase produces artifacts consumed by the next. You can't validate what you haven't composed. You can't document what you haven't validated. Discovery and browsing are independent of each other but both feed into ideation and composition.

## Anti-Patterns

### Anti-Pattern 1: Monolithic Skill

**What people do:** Put all instructions in one giant SKILL.md that handles discovery through documentation.
**Why it's wrong:** Claude loses track of context in long skills. Users can't invoke individual phases. Testing is impossible.
**Do this instead:** One skill per phase. The orchestrator (`/comfy-flow`) chains them but each works independently.

### Anti-Pattern 2: Claude Constructs Raw Workflow JSON

**What people do:** Let Claude build the entire workflow JSON by writing it character by character in a code block.
**Why it's wrong:** ComfyUI workflow JSON is complex (node IDs, link arrays with slot indices, type-safe connections). Claude will get link wiring wrong, miss required fields, or produce invalid type connections. The JSON can be 500+ lines for real workflows.
**Do this instead:** Python builder module that handles graph construction. Claude calls `builder.add_node("KSampler", {...})` and `builder.connect(node_a, "IMAGE", node_b, "image")`. The builder manages IDs, links, and type checking.

### Anti-Pattern 3: Hardcoded Node Knowledge

**What people do:** Encode node specs (inputs, outputs, types) directly in Python code or SKILL.md instructions.
**Why it's wrong:** ComfyUI has 8,400+ custom nodes. New ones appear daily. Core nodes change between versions. Hardcoded specs go stale immediately.
**Do this instead:** Fetch node specs at runtime from `api.comfy.org` (via registry module). Cache for performance. Only hardcode the core node list (which changes rarely and is needed for the "prefer core nodes" validation rule).

### Anti-Pattern 4: Treating MCP as the Primary Interface

**What people do:** Route everything through the comfyui-mcp server tools.
**Why it's wrong:** The MCP server is designed for cloud workflow submission, not template authoring. `search_nodes` is broken on cloud. The MCP server adds latency and abstraction for operations that are simpler done directly (fetching from api.comfy.org, reading from GitHub).
**Do this instead:** Use MCP tools only for cloud-specific operations (submit_workflow, get_job_status). Use direct API calls for registry and GitHub access.

## Scaling Considerations

This is an internal team toolkit, not a public SaaS. "Scaling" means supporting more template creators and more templates.

| Concern | Now (5-10 creators) | Later (20+ creators) |
|---------|---------------------|----------------------|
| Registry API rate limits | Cache with 1hr TTL, no issues | May need longer cache or local mirror |
| Template index size | 400 templates, index.json fits in memory | 1000+ templates: add local SQLite index for search |
| Workflow composition | Claude + builder module, adequate | Could add template "recipes" -- predefined composition patterns |
| Validation rules | JSON config files, easy to update | Could move to a shared rules repo if multiple tools need them |

### First Bottleneck

Registry API response time when cache is cold. Mitigate with aggressive caching and parallel fetches.

### Second Bottleneck

Template coverage analysis on a growing index. Mitigate with local index + search rather than re-parsing the full index.json each time.

## Sources

- [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates) -- template repo structure, index.json schema, submission process (HIGH confidence)
- [ComfyUI Workflow JSON Spec](https://docs.comfy.org/specs/workflow_json) -- workflow format v1.0 (HIGH confidence)
- [Template creation docs](https://docs.comfy.org/custom-nodes/workflow_templates) -- official template authoring guidance (HIGH confidence)
- comfy-tip source (`C:/Users/minta/Projects/comfy-tip/`) -- existing registry discovery code (HIGH confidence, local)
- comfyui-mcp reports (`C:/Users/minta/Projects/comfyui/REPORT-COMFYUI-MCP.md`, `HANDOFF-MCP-IMPROVEMENTS.md`) -- MCP capabilities and limitations (HIGH confidence, local)
- index.json live data via GitHub API -- schema verified against 400+ template entries (HIGH confidence)

---
*Architecture research for: ComfyUI template agent toolkit*
*Researched: 2026-03-18*
