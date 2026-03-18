# Technology Stack

**Project:** ComfyUI Template Agent
**Researched:** 2026-03-18
**Overall confidence:** HIGH

## Recommended Stack

This is a Claude Code agent toolkit, not a web app. The deliverable is a set of Claude Code skills (SKILL.md files) backed by Python modules that call ComfyUI's registry API, parse workflow JSON, and generate documentation. No framework needed -- just Python, HTTP, and schema validation.

### Core Runtime

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Python | 3.12+ | Runtime | Already on system (3.12.10). Matches comfy-tip. MCP SDK requires >=3.10. | HIGH |
| Claude Code Skills | SKILL.md v1 | Agent interface | This IS the distribution format. Skills = YAML frontmatter + markdown instructions. Team already uses Claude Code. No alternative. | HIGH |

### HTTP & API Client

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| httpx | 0.28.1 | HTTP client for api.comfy.org and GitHub API | Sync + async in one lib. Better timeout handling, connection pooling, and error types than urllib. Modern Python standard for HTTP. | HIGH |

**Dependency trade-off note:** An alternative v1 approach is stdlib-only (`urllib.request`) to keep installation trivial (zero deps, just clone and go). comfy-tip already uses urllib successfully. httpx is better DX but adds a dependency. **Recommendation:** Start with httpx. The `pip install httpx` cost is negligible vs. the DX improvement (proper timeout objects, JSON auto-parsing, response status checking). If zero-dep distribution becomes important later, urllib is a viable fallback.

### Data Validation & Schema

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Pydantic | 2.12+ | Workflow JSON models, template metadata models, validation | Type-safe models for ComfyUI workflow JSON (nodes, links, widgets), index.json template entries, and validation error reporting. Core to the "validate" phase. 5-50x faster than v1 with Rust core. | HIGH |
| jsonschema | 4.26+ | Validate against ComfyUI's official JSON Schema | ComfyUI publishes an official `index.schema.json` for templates and a workflow JSON schema. Pydantic models the data; jsonschema validates against the official spec. Both needed. | MEDIUM |

### MCP Server (optional, Phase 2+)

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| mcp (FastMCP) | 1.26+ | MCP tool server if skills need tool-callable endpoints | Comfy-tip already has an MCP integration pattern. FastMCP decorator syntax is clean. BUT: v1 should be pure skills + Python modules. MCP server only if tools need to be callable from other agents. Pin to `mcp>=1.26,<2` since v2 is pre-alpha. | MEDIUM |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pathlib | stdlib | File paths, template directory traversal | Always -- cross-platform path handling |
| json | stdlib | Workflow JSON read/write | Always |
| datetime | stdlib | Timestamp handling for registry data | Node freshness scoring |
| re | stdlib | Pattern matching in workflow validation | Detecting node naming patterns, set/get nodes |
| textwrap / string.Template | stdlib | Markdown template generation | Notion doc output formatting |
| typing / dataclasses | stdlib | Type hints | Everywhere |
| math | stdlib | Scoring heuristics | Trending/rising node scoring (log, sqrt) |
| argparse | stdlib | CLI interfaces for modules | Every src/ module's `__main__` block |

### Development

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| pytest | 8.x | Testing | Standard. Validate workflow JSON parsing, template metadata generation, validation rules |
| ruff | 0.9+ | Linting + formatting | Single tool replaces flake8 + black + isort. 10-100x faster. |

## Architecture Decision: Skills + Modules, Not a Server

The key stack decision: **this is NOT an MCP server**. It is a collection of Claude Code skills backed by importable Python modules.

```
comfyui-template-agent/
  .claude/skills/
    comfy-discover/SKILL.md     # Node discovery & trend surfacing
    comfy-ideate/SKILL.md       # Template gap analysis & concept generation
    comfy-compose/SKILL.md      # Workflow JSON creation
    comfy-validate/SKILL.md     # Guideline compliance checking
    comfy-document/SKILL.md     # Metadata + Notion markdown generation
    comfy-flow/SKILL.md         # Guided end-to-end orchestrator
  src/
    registry/                   # api.comfy.org client
      highlights.py             # Adapted from comfy-tip
      search.py                 # Node pack search
      spec.py                   # Node I/O spec retrieval
      cache.py                  # Shared HTTP + disk caching
    templates/                  # workflow_templates repo interface
      browser.py                # Browse/search templates
      coverage.py               # Gap analysis
      loader.py                 # Fetch template JSON
    composer/                   # Workflow construction
      graph.py                  # Node graph data model
      builder.py                # Fluent API for building workflows
      scaffold.py               # Clone + modify existing templates
      types.py                  # ComfyUI type system
    validator/                  # Validation engine
      rules.py                  # Individual validation rules
      checker.py                # Run all rules, produce report
      guidelines.py             # Encoded template guidelines
    metadata/                   # Template metadata
      index_entry.py            # Build index.json entries
      schema.py                 # index.json schema validation
    document/                   # Output generation
      notion.py                 # Notion markdown formatter
      submission.py             # Full submission package
    shared/                     # Cross-cutting concerns
      http.py                   # HTTP client wrapper
      cache.py                  # Disk cache with TTL
      config.py                 # API URLs, cache paths
  data/
    core_nodes.json             # Core node whitelist (for validation)
    guidelines.json             # Machine-readable template rules
    index_schema.json           # index.json JSON Schema
  tests/
  pyproject.toml
```

**Why skills, not MCP server:**
1. Claude Code skills are the native interface -- the team already uses Claude Code
2. Skills can call Python modules directly via allowed-tools (Bash, Read, Write)
3. No server process to manage, no transport protocol overhead
4. MCP server adds complexity without benefit for a single-user agent toolkit
5. comfy-tip already demonstrates the skill pattern works

**When to add MCP:** Only if other agents/clients need to call these tools programmatically (Phase 2+ consideration).

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| HTTP client | httpx | urllib (stdlib) | urllib works (comfy-tip uses it) but lacks timeout config, connection pooling, proper error types. httpx is minimal overhead for much better DX. Acceptable fallback if zero-dep is critical. |
| HTTP client | httpx | requests | No async support, no HTTP/2. httpx is strictly better for new projects. |
| HTTP client | httpx | aiohttp | Async-only. We need sync for skill scripts. httpx does both. |
| Validation | Pydantic + jsonschema | Pydantic alone | ComfyUI publishes official JSON Schema files. Need jsonschema lib to validate against those. Pydantic models our internal types. |
| Validation | Pydantic + jsonschema | dataclasses + jsonschema | Pydantic's validation, serialization, and error messages are far superior. Worth the dependency. |
| Agent interface | Claude Code Skills | Custom MCP server | Unnecessary complexity. Skills are the right abstraction for guided workflows. |
| Agent interface | Claude Code Skills | LangChain / CrewAI | Massive overkill. This is one agent (Claude Code) with structured skills, not a multi-agent framework. |
| Formatting | stdlib string.Template | Jinja2 | Markdown output is simple enough. Jinja2 adds a dependency for templates that are mostly string concatenation. |
| Linting | ruff | flake8 + black | ruff replaces both, 10-100x faster. No reason to use the old stack. |

## What NOT to Use

| Technology | Why Not |
|------------|---------|
| LangChain / LlamaIndex | This is a Claude Code skill toolkit, not an LLM orchestration framework. Claude Code IS the orchestrator. |
| FastAPI / Flask | No web server needed. Skills run as CLI scripts inside Claude Code. |
| SQLite / any database | JSON file cache is sufficient. Template data is read from GitHub repo + registry API. ~400 templates and ~8,400 nodes both fit in memory. |
| Docker | Skills run in the user's Python environment alongside Claude Code. Containerization adds friction for zero benefit. |
| CrewAI / AutoGen / multi-agent frameworks | Wrong abstraction. One agent (Claude), multiple skills. |
| comfyui-mcp-server (Comfy-Org) | That's for workflow execution/submission to Comfy Cloud. This agent is for template creation/validation. Different concern. Complement, not replace. |
| RL/GRPO training pipelines | ComfySearch/ComfyGPT use GRPO for workflow generation. Overkill for internal tooling with human-in-the-loop. Borrow their decomposition patterns, not their training infrastructure. |

## Existing Code to Reuse

| Source | What to Reuse | How |
|--------|---------------|-----|
| comfy-tip/highlights.py | Registry API client, trending/scoring heuristics, cache pattern | Adapt into src/registry/highlights.py. Upgrade urllib to httpx. Keep scoring logic intact. |
| comfy-tip/mcp_integration.py | MCP tool definition pattern | Reference for future MCP server phase, not v1. |
| comfy-tip/skill/SKILL.md | SKILL.md format, frontmatter structure | Template for new skills. |
| comfyui/ MCP improvements | API node auth detection, silent failure patterns | Inform the validation rules -- detect API nodes, warn about auth requirements. |

## External APIs

| API | Base URL | Auth | Rate Limits | Purpose |
|-----|----------|------|-------------|---------|
| ComfyUI Registry | api.comfy.org | None (public) | Generous, unknown exact limits | Node discovery, metadata, downloads, stars |
| GitHub API | api.github.com | Optional (GITHUB_TOKEN raises limit from 60/hr to 5000/hr) | 60/hr unauthenticated | Read workflow_templates repo, browse existing templates |
| GitHub Raw | raw.githubusercontent.com | None | No known limits | Fetch template JSON files, index.json, schema files directly |

## Installation

```bash
# Core dependencies (3 packages)
pip install httpx pydantic "jsonschema>=4.26"

# Dev dependencies
pip install pytest ruff

# Optional: MCP server (Phase 2+)
pip install "mcp>=1.26,<2"
```

Minimal: 3 production dependencies (httpx, pydantic, jsonschema). Everything else is stdlib.

**pyproject.toml approach:**
```toml
[project]
name = "comfyui-template-agent"
requires-python = ">=3.12"
dependencies = [
    "httpx>=0.28",
    "pydantic>=2.12",
    "jsonschema>=4.26",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.9"]
mcp = ["mcp>=1.26,<2"]
```

## ComfyUI-Specific Schema Knowledge

The workflow JSON schema (v1.0, from docs.comfy.org) has these key structures that Pydantic models must cover:

- **Top-level**: `version` (always 1), `state` (ID tracking), `nodes` (array), optional `links`, `groups`, `reroutes`, `extra`, `models`
- **Node**: `id`, `type`, `pos`, `size`, `flags`, `order`, `mode`, `properties`, optional `inputs`/`outputs`/`widgets_values`/`color`/`bgcolor`
- **Link**: 6-element array: `[link_id, origin_id, origin_slot, target_id, target_slot, type]`
- **Template index.json**: `moduleName`, `title`, `type` (image/video/audio), `templates[]` with `name`, `description`, `mediaType`, `mediaSubtype`, `models[]`, `tags[]`, `io`, `thumbnailVariant`, `requiresCustomNodes[]`
- **Blueprint format**: Native ComfyUI subgraph JSON -- same node/link structure but in `definitions.subgraphs`

**Two JSON formats (critical pitfall):** Workflow format (UI, has nodes/links/pos/size) vs API format (execution, has class_type/inputs with connection refs). Templates use WORKFLOW format. Format detection must be the first validation step.

## Sources

- [ComfyUI Workflow JSON Schema](https://docs.comfy.org/specs/workflow_json) -- Official spec, v1.0 (HIGH confidence)
- [ComfyUI Registry API](https://docs.comfy.org/registry/api-reference/overview) -- Node search, metadata (HIGH confidence)
- [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates) -- Template repo structure, index.json schema (HIGH confidence)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) -- v1.26.0, FastMCP pattern (HIGH confidence, verified on PyPI)
- [Claude Code Skills docs](https://code.claude.com/docs/en/skills) -- SKILL.md format specification (HIGH confidence)
- [anthropics/skills](https://github.com/anthropics/skills) -- Official skills repo, format reference (HIGH confidence)
- [httpx on PyPI](https://pypi.org/project/httpx/) -- v0.28.1, verified (HIGH confidence)
- [pydantic on PyPI](https://pypi.org/project/pydantic/) -- v2.12.5, requires Python >=3.9 (HIGH confidence)
- [jsonschema on PyPI](https://pypi.org/project/jsonschema/) -- v4.26.0, requires Python >=3.10 (HIGH confidence)
- [FastMCP tools docs](https://gofastmcp.com/servers/tools) -- Decorator pattern reference (HIGH confidence)
- [SKILL.md Format Specification](https://deepwiki.com/anthropics/skills/2.2-skill.md-format-specification) -- Frontmatter fields (MEDIUM confidence)
