# Phase 1: Foundation + Discovery - Research

**Researched:** 2026-03-18
**Domain:** ComfyUI Registry API client, node discovery, project infrastructure
**Confidence:** HIGH

## Summary

Phase 1 delivers shared infrastructure (HTTP client with caching, core node whitelist, format detector) and five registry-based discovery capabilities (DISC-01 through DISC-05). The existing `comfy-tip/highlights.py` provides a production-ready registry client with scoring heuristics that should be adapted (upgrade urllib to httpx) rather than rewritten. The ComfyUI Registry API at `api.comfy.org` is public, requires no auth, and has three key endpoints: `/nodes` (paginated node pack listing with search), `/nodes/{id}` (pack detail), and `/comfy-nodes` (individual node specs with input/output types). A critical finding: the registry has no tag-based filtering -- tags and categories are empty on node packs. Category filtering (DISC-03) must use keyword matching on node names, descriptions, and the `category` field from individual comfy_nodes.

The template library uses 4 module types (`image`, `video`, `audio`, `3d`) that serve as the target categories for filtering. The core node whitelist cannot come from the registry (core ComfyUI nodes aren't listed as a pack); it must be extracted from the ComfyUI GitHub source (`nodes.py` + 96 files in `comfy_extras/`). The Notion guidelines export exists at `/tmp/notion-export/` and should be extracted to `data/guidelines.json` as a data task in this phase.

**Primary recommendation:** Adapt comfy-tip's highlights.py with httpx, add search and node-spec modules, implement category filtering via keyword mapping, and extract core nodes from ComfyUI GitHub source.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Multiple separate skills, not one monolithic command
- Skills accept both natural language and explicit flags
- Progressive detail: summary cards by default, detailed specs on request
- Random mode offers both weighted random AND truly random
- Hybrid fetch strategy: bulk fetch for trending/popular, search endpoint for targeted queries
- Map registry tags to template library categories (Image, Video, Audio, 3D Model, LLM, Utility)
- Skills share session context so discovery results carry forward
- Full pytest from Phase 1
- Keep 6 key images from Notion export (image.png, image 2.png, image 3.png, image 4.png, image 7.png, image 8.png, image 10.png)
- Template guidelines extraction to data/guidelines.json in Phase 1

### Claude's Discretion
- Package layout specifics (flat scripts vs proper package with entry points)
- HTTP client library choice (httpx recommended by research)
- Cache implementation details
- Config management approach
- Naming prefix for skills
- Format detector integration pattern
- Node pack info data source (registry API first, GitHub scrape as fallback)
- Core node whitelist extraction method

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DISC-01 | Browse trending/new/rising/popular/random nodes | Directly adapted from comfy-tip/highlights.py scoring heuristics. Registry `/nodes` endpoint confirmed working with pagination. |
| DISC-02 | Search nodes by name, category, or input/output type | Registry `/nodes?search=X` endpoint confirmed working (3928 total nodes). `/comfy-nodes` endpoint provides input_types/return_types for type-based search. |
| DISC-03 | Filter discovery by media category | Registry has NO tag-based filtering (tags empty). Must implement keyword mapping from node names/descriptions/categories to template library types (image, video, audio, 3d). |
| DISC-04 | View nodes a custom node pack includes | Registry `/comfy-nodes?node_id=X` endpoint returns individual nodes with comfy_node_name, category, input_types, return_types. Confirmed working (e.g., VHS has 2024 nodes). |
| DISC-05 | Get random node suggestions | Already implemented in comfy-tip (weighted random from pool). Add truly random option per user decision. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12+ | Runtime | Already installed (3.12.10). Matches comfy-tip. |
| httpx | 0.28.1 | HTTP client | Sync+async, proper timeouts, JSON auto-parsing, connection pooling. Verified on system. |
| pydantic | 2.12.5 | Data models for API responses | Type-safe models for registry nodes, search results, comfy_node specs. Verified on system. |
| pytest | 9.0.2 | Testing | Full test suite from Phase 1 per user decision. Verified on system. |
| ruff | 0.15.4 | Linting + formatting | Replaces flake8+black. Verified on system. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pathlib | stdlib | File paths, cache directory management | Always |
| json | stdlib | JSON parsing/writing | API responses, cache files, data files |
| math | stdlib | Scoring heuristics (log, sqrt) | Trending/rising score calculations |
| datetime | stdlib | Timestamp handling | Node freshness scoring, cache TTL |
| re | stdlib | Pattern matching | Category keyword matching, format detection |
| argparse | stdlib | CLI interfaces | Module entry points |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| httpx | urllib (stdlib) | Zero deps but worse DX. comfy-tip uses urllib successfully. httpx is worth the dep for timeouts/pooling. |
| pydantic | dataclasses | Pydantic gives validation, serialization, better error messages. Worth for API response models. |

**Installation:**
```bash
pip install httpx pydantic
pip install pytest ruff  # dev
```

## Architecture Patterns

### Recommended Project Structure (Phase 1 scope)
```
comfyui-template-agent/
  .claude/
    skills/
      comfy-discover/
        SKILL.md              # Node discovery skill
  src/
    registry/
      __init__.py
      client.py               # Shared httpx client with caching
      highlights.py            # Adapted from comfy-tip (trending/new/rising/popular/random)
      search.py                # Node search by name/category/type
      spec.py                  # Node pack inspection (individual nodes, I/O specs)
      models.py                # Pydantic models for registry API responses
    shared/
      __init__.py
      http.py                  # httpx client wrapper with retry, timeout config
      cache.py                 # Disk cache with per-query-type TTL
      config.py                # API URLs, cache paths, env var config
      format_detector.py       # Workflow vs API format detection (standalone utility)
      categories.py            # Media category keyword mapping
  data/
    core_nodes.json            # Core node whitelist (extracted from ComfyUI source)
    guidelines.json            # Template creation guidelines (extracted from Notion)
    guidelines/                # Key reference images from Notion export
      image.png
      image_2.png
      image_3.png
      image_4.png
      image_7.png
      image_8.png
      image_10.png
  tests/
    conftest.py                # Shared fixtures (mock API responses, sample data)
    test_client.py             # HTTP client + caching tests
    test_highlights.py         # Scoring heuristic tests
    test_search.py             # Search + filter tests
    test_spec.py               # Node pack inspection tests
    test_format_detector.py    # Format detection tests
    test_categories.py         # Category mapping tests
  pyproject.toml
  CLAUDE.md                    # Project-level instructions
```

### Pattern 1: Skills as LLM Instructions
**What:** SKILL.md files instruct Claude how to use Python modules via Bash tool calls. The skill describes the workflow; Claude orchestrates.
**When to use:** Always -- this is the fundamental Claude Code pattern.
**Example:**
```markdown
---
name: comfy-discover
description: Discover trending and new ComfyUI nodes for template inspiration
---

# Node Discovery

## What This Does
Surfaces interesting nodes from the ComfyUI registry for template creation.

## Quick Start
Just describe what you're looking for:
- "What's trending in video nodes?"
- "Show me new audio processing nodes"
- "Find nodes for image upscaling"
- "Surprise me with something random"

## How It Works

1. For browsing modes (trending/new/rising/popular/random):
   ```bash
   python3 -m src.registry.highlights --mode trending --limit 10
   ```

2. For search:
   ```bash
   python3 -m src.registry.search --query "video upscale" --category video
   ```

3. For node pack inspection:
   ```bash
   python3 -m src.registry.spec <node_pack_id>
   ```

## Output Format
Present as summary cards: Name | Author | Downloads | Stars | Description
When user asks for details, show full I/O specs.
```

### Pattern 2: Pydantic Models for API Responses
**What:** Type-safe models for registry API data, used across all registry modules.
**When to use:** Every API response should be parsed through a model.
**Example:**
```python
from pydantic import BaseModel, Field
from typing import Optional

class NodePack(BaseModel):
    id: str
    name: str
    author: str = ""
    description: str = ""
    downloads: int = 0
    github_stars: int = Field(0, alias="github_stars")
    rating: float = 0
    created_at: str = ""
    repository: str = ""
    tags: list[str] = []
    status: str = ""

class ComfyNode(BaseModel):
    comfy_node_name: str
    category: str = ""
    input_types: str = ""  # JSON string, needs parsing
    return_types: str = ""  # JSON string, needs parsing
    return_names: str = ""
    deprecated: bool = False
    experimental: bool = False

class SearchResult(BaseModel):
    nodes: list[NodePack]
    total: int
    page: int
    limit: int
    totalPages: int
```

### Pattern 3: Cache with Per-Query-Type TTL
**What:** Different cache durations for different query types. Trending/popular can be cached longer; search results should be fresher.
**When to use:** All API calls go through the cache layer.
**Example TTLs:**
```python
CACHE_TTLS = {
    "highlights": 3600,    # 1 hour (bulk fetch, scoring doesn't need real-time)
    "search": 900,         # 15 minutes (user expects fresh results)
    "spec": 86400,         # 24 hours (node specs change rarely)
    "core_nodes": 604800,  # 7 days (core nodes change per ComfyUI release)
}
```

### Anti-Patterns to Avoid
- **Monolithic skill:** Don't put all discovery logic in one SKILL.md. Separate concerns.
- **Raw JSON construction:** Don't have Claude write JSON responses inline. Python modules handle formatting.
- **Hardcoded node knowledge:** Don't embed node specs in code. Fetch from API, cache locally.
- **Tags-based filtering on registry:** Registry tags are empty. Don't rely on them.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTP with retry/timeout | Raw urllib with try/except loops | httpx with configured timeouts and transport retry | httpx handles connection pooling, proper timeout objects, HTTP/2 |
| API response validation | Manual dict access with .get() chains | Pydantic models with parse_obj | Automatic validation, type coercion, clear error messages |
| JSON file caching | Custom file lock + timestamp check | Simple TTL cache with json.dump/load + timestamp | comfy-tip pattern works; no need for Redis/SQLite at this scale |
| Format detection | String matching on specific fields | Structural check: has `nodes[]` array = workflow format; has flat keys with `class_type` = API format | Two clear signals, no ambiguity |

## Common Pitfalls

### Pitfall 1: Registry Tags Are Empty
**What goes wrong:** Attempting to filter nodes by tags returns all results (3928 total regardless of tag parameter).
**Why it happens:** Node packs in the registry have empty `tags` and `category` fields. The tag filter parameter appears to be a no-op.
**How to avoid:** Implement category filtering via keyword matching on node names, descriptions, and the `category` field from individual comfy_nodes (via `/comfy-nodes` endpoint). Map to template library types: image, video, audio, 3d.
**Warning signs:** Same result count regardless of tag parameter value.

### Pitfall 2: Core Nodes Not in Registry
**What goes wrong:** Searching the registry for core ComfyUI nodes returns 0 results (no pack with id "comfyui" or similar).
**Why it happens:** Core nodes ship with ComfyUI itself and aren't registered as a separate pack in the registry.
**How to avoid:** Extract core node list from ComfyUI GitHub source: `nodes.py` (64 nodes in NODE_CLASS_MAPPINGS) + 96 files in `comfy_extras/nodes_*.py`. Store as `data/core_nodes.json`. Update periodically by re-running extraction script.
**Warning signs:** Empty results when querying `comfy-nodes?node_id=comfyui`.

### Pitfall 3: Sort Parameters Cause 500 Errors
**What goes wrong:** Using `sort=downloads` or `sort=stars` or `sort=created_at` on the `/nodes` endpoint returns HTTP 500.
**Why it happens:** The registry API's sort functionality appears broken or unsupported for these fields.
**How to avoid:** Fetch data without sort parameters, then sort client-side in Python. The comfy-tip approach of bulk-fetching multiple pages and scoring client-side is correct.
**Warning signs:** HTTP 500 on any request with `sort=` parameter (except `sort=name`).

### Pitfall 4: comfy_nodes input_types is a JSON String
**What goes wrong:** The `input_types` field from `/comfy-nodes` is a JSON-encoded string, not a parsed object. Direct access fails.
**Why it happens:** The registry API serializes the ComfyUI node definition as a string field.
**How to avoid:** Double-parse: first parse the API response, then `json.loads(node.input_types)` to get the actual type dict.
**Warning signs:** Getting `{"required": ...}` as a string instead of a dict.

### Pitfall 5: Notion Export Path is Ephemeral
**What goes wrong:** The Notion guidelines export at `/tmp/notion-export/` may not survive system restarts.
**Why it happens:** `/tmp/` is a temporary directory.
**How to avoid:** Extract guidelines to `data/guidelines.json` and copy key images to `data/guidelines/` early in Phase 1, before the export disappears. This is a data task, not a code task.
**Warning signs:** FileNotFoundError when accessing `/tmp/notion-export/`.

### Pitfall 6: Large Node Pack Spec Responses
**What goes wrong:** Some node packs have thousands of individual nodes (e.g., VideoHelperSuite has 2024 comfy_nodes). Fetching all at once is slow.
**Why it happens:** The `/comfy-nodes` endpoint returns paginated results, but the default limit may return partial data.
**How to avoid:** Use pagination with reasonable limits. For DISC-04 (pack inspection), fetch all pages but cache aggressively (24hr TTL for specs). Show summary first, detailed specs on request.

## Code Examples

### Registry API Client (httpx-based)
```python
# Source: Verified against live api.comfy.org (2026-03-18)
import httpx
from typing import Optional

CLIENT_TIMEOUT = httpx.Timeout(15.0, connect=5.0)
BASE_URL = "https://api.comfy.org"

def get_client() -> httpx.Client:
    return httpx.Client(
        base_url=BASE_URL,
        timeout=CLIENT_TIMEOUT,
        headers={"User-Agent": "ComfyTemplateAgent/1.0"},
    )

def fetch_nodes(client: httpx.Client, page: int = 1, limit: int = 50,
                search: Optional[str] = None) -> dict:
    params = {"page": page, "limit": limit}
    if search:
        params["search"] = search
    resp = client.get("/nodes", params=params)
    resp.raise_for_status()
    return resp.json()

def fetch_comfy_nodes(client: httpx.Client, node_id: str,
                      limit: int = 100) -> dict:
    """Fetch individual nodes for a pack. Returns comfy_nodes with I/O specs."""
    resp = client.get("/comfy-nodes", params={"node_id": node_id, "limit": limit})
    resp.raise_for_status()
    return resp.json()
```

### Scoring Heuristics (from comfy-tip, verified working)
```python
# Source: comfy-tip/highlights.py (production code, adapt don't rewrite)
import math
from datetime import datetime, timezone

def days_since(date_str: str) -> int:
    try:
        created = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return max((datetime.now(timezone.utc) - created).days, 1)
    except (ValueError, TypeError):
        return 365

def score_trending(node: dict) -> float:
    """Trending = high download velocity + star signal, with recency boost."""
    days = days_since(node["created_at"])
    dl_per_day = node["downloads"] / days
    star_bonus = math.log(node["stars"] + 1, 2)
    recency = max(1, 10 - (days / 30))
    return dl_per_day * (1 + star_bonus) * recency

def score_rising(node: dict) -> float:
    """Rising = new nodes (last 90 days) with fast adoption."""
    days = days_since(node["created_at"])
    if days > 90:
        return 0
    dl_per_day = node["downloads"] / days
    return dl_per_day * (90 - days)
```

### Category Keyword Mapping
```python
# Source: Research analysis of template index.json module types + registry node data
CATEGORY_KEYWORDS = {
    "video": ["video", "animation", "animate", "frame", "motion", "film",
              "mp4", "gif", "interpolat", "optical flow", "wan", "hunyuan-video",
              "mochi", "ltx", "svd", "i2v", "t2v", "v2v"],
    "image": ["image", "photo", "picture", "upscale", "denoise", "inpaint",
              "outpaint", "flux", "sdxl", "stable diffusion", "controlnet",
              "img2img", "txt2img", "lora"],
    "audio": ["audio", "sound", "music", "voice", "speech", "tts",
              "whisper", "bark", "elevenlabs"],
    "3d": ["3d", "mesh", "point cloud", "depth", "normal map",
            "hunyuan3d", "stable3d", "triposr"],
}

def classify_node(name: str, description: str, category: str = "") -> list[str]:
    """Return matching media categories for a node."""
    text = f"{name} {description} {category}".lower()
    matches = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            matches.append(cat)
    return matches or ["utility"]
```

### Format Detector
```python
# Source: PITFALLS.md research + ComfyUI workflow JSON spec
def detect_format(data: dict) -> str:
    """Detect whether JSON is workflow format or API format.
    Returns: 'workflow', 'api', or 'unknown'
    """
    # Workflow format: has 'nodes' array and usually 'links'
    if isinstance(data.get("nodes"), list):
        return "workflow"
    # API format: flat dict where values have 'class_type'
    if any(isinstance(v, dict) and "class_type" in v
           for v in data.values() if isinstance(v, dict)):
        return "api"
    return "unknown"
```

### Core Node Extraction Script
```python
# Source: Verified against github.com/comfyanonymous/ComfyUI (2026-03-18)
# nodes.py has 64 core nodes; comfy_extras/ has 96 additional node files
import httpx
import re
import json

def extract_core_nodes() -> list[str]:
    """Extract core node names from ComfyUI GitHub source."""
    client = httpx.Client(timeout=30.0)
    nodes = []

    # Main nodes.py
    resp = client.get("https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/nodes.py")
    match = re.search(r'NODE_CLASS_MAPPINGS\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
                       resp.text, re.DOTALL)
    if match:
        nodes.extend(re.findall(r'"([^"]+)"', match.group(1)))

    # comfy_extras/nodes_*.py files
    resp = client.get("https://api.github.com/repos/comfyanonymous/ComfyUI/contents/comfy_extras")
    for f in resp.json():
        if f["name"].startswith("nodes_") and f["name"].endswith(".py"):
            file_resp = client.get(f["download_url"])
            matches = re.findall(r'NODE_CLASS_MAPPINGS\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
                                  file_resp.text, re.DOTALL)
            for m in matches:
                nodes.extend(re.findall(r'"([^"]+)"', m))

    return sorted(set(nodes))
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| urllib.request for HTTP | httpx with typed client | 2024+ | Better timeouts, connection pooling, error types |
| Manual dict parsing | Pydantic model validation | Standard practice | Type safety, auto-validation, serialization |
| Tags-based API filtering | Client-side keyword classification | N/A (tags never worked) | Must implement category matching ourselves |

## Registry API Reference

### Verified Endpoints (2026-03-18)

| Endpoint | Method | Parameters | Returns | Notes |
|----------|--------|------------|---------|-------|
| `/nodes` | GET | `page`, `limit`, `search` | `{nodes[], total, page, limit, totalPages}` | Search works; `sort` params cause 500 |
| `/nodes/{id}` | GET | - | Full node pack detail | No individual comfy_nodes in response |
| `/comfy-nodes` | GET | `node_id`, `limit` | `{comfy_nodes[], total}` | Individual nodes with I/O specs |
| `/nodes/{id}/versions` | GET | - | Version array | Changelog, dependencies, supported platforms |

### Response Field Notes
- `nodes[].tags`: Always empty array (do not rely on)
- `nodes[].category`: Always empty string (do not rely on)
- `nodes[].status`: Check for `"NodeStatusActive"` to filter dead packs
- `comfy_nodes[].input_types`: JSON-encoded string, needs `json.loads()` to parse
- `comfy_nodes[].return_types`: JSON-encoded string (e.g., `'["IMAGE"]'`)
- Total registry size: ~3928 active node packs, ~308,146 individual comfy_nodes

### Template Library Categories (from index.json)
Module types: `image`, `video`, `audio`, `3d`
Template mediaTypes: `image`, `audio` (only 2 used so far)
Module count: 8 modules (default, flux, video, audio, 3d, llm, utility, getting_started)

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | pyproject.toml (Plan 01 creates) |
| Quick run command | `python -m pytest tests/ -x -q` |
| Full suite command | `python -m pytest tests/ -v --tb=short` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | Plan |
|--------|----------|-----------|-------------------|------|
| DISC-01 | Browse trending/new/rising/popular/random nodes | unit | `python -m pytest tests/test_highlights.py -x` | 01-02 |
| DISC-02 | Search by name/category/type | unit | `python -m pytest tests/test_search.py -x` | 01-02 |
| DISC-03 | Filter by media category | unit | `python -m pytest tests/test_shared.py::test_classify -x` | 01-01 (shared), 01-02 (integration) |
| DISC-04 | View node pack contents | unit | `python -m pytest tests/test_spec.py -x` | 01-02 |
| DISC-05 | Random node suggestions | unit | `python -m pytest tests/test_highlights.py::test_random -x` | 01-02 |
| INFRA | HTTP client + caching + format detector + categories | unit | `python -m pytest tests/test_shared.py -x` | 01-01 |

### Test File Layout
| File | Covers | Created By |
|------|--------|------------|
| `tests/test_shared.py` | HTTP client, cache, format detector, categories, Pydantic models | Plan 01, Task 3 |
| `tests/test_highlights.py` | Scoring heuristics, browse modes, category filter integration | Plan 02, Task 2 |
| `tests/test_search.py` | Name search, type search, category filter | Plan 02, Task 2 |
| `tests/test_spec.py` | Node pack inspection, pagination, I/O parsing | Plan 02, Task 2 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/ -x -q`
- **Per wave merge:** `python -m pytest tests/ -v --tb=short`
- **Phase gate:** Full suite green before `/gsd:verify-work`

## Open Questions

1. **GitHub API rate limits for core node extraction**
   - What we know: 60 req/hr unauthenticated. Extracting from 96+ comfy_extras files needs ~97 requests.
   - What's unclear: Whether to use GITHUB_TOKEN or batch the extraction.
   - Recommendation: Run extraction once with GITHUB_TOKEN, save result to `data/core_nodes.json`. Re-run only on ComfyUI version bumps. Also consider using the GitHub tarball download (1 request) instead of per-file API calls.

2. **Session context sharing between skills**
   - What we know: User wants discovery results to carry forward in conversation.
   - What's unclear: Claude Code skill context isolation -- do skills in the same session share conversation history?
   - Recommendation: Output structured data (JSON with node IDs) so Claude can reference previous discovery results. Skills run in the same Claude Code session, so conversation history naturally carries forward.

3. **Registry API rate limits**
   - What we know: Public API, no documented rate limits. comfy-tip uses 1hr cache successfully.
   - What's unclear: Exact rate limit thresholds.
   - Recommendation: Cache aggressively per the TTL scheme. If rate-limited, implement exponential backoff.

## Sources

### Primary (HIGH confidence)
- ComfyUI Registry API (`api.comfy.org`) -- endpoints verified with live requests (2026-03-18)
- comfy-tip/highlights.py -- working production code, scoring heuristics verified
- ComfyUI GitHub source (`comfyanonymous/ComfyUI`) -- core node count verified (64 in nodes.py + 96 extras files)
- workflow_templates index.json -- module types and template schema verified via GitHub raw

### Secondary (MEDIUM confidence)
- `.planning/research/STACK.md` -- stack decisions cross-verified with installed versions
- `.planning/research/ARCHITECTURE.md` -- project structure validated against phase scope
- `.planning/research/PITFALLS.md` -- pitfalls confirmed by API testing

### Tertiary (LOW confidence)
- Category keyword mapping -- based on analysis of node names and template types, not verified against full registry corpus. May need refinement after testing with real discovery results.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all packages verified installed and version-checked
- Architecture: HIGH -- patterns from existing comfy-tip code + research docs
- Registry API: HIGH -- all endpoints tested with live requests
- Category mapping: MEDIUM -- keyword approach is an educated guess, needs validation
- Core node extraction: MEDIUM -- regex parsing of Python source is fragile, works for current codebase

**Research date:** 2026-03-18
**Valid until:** 2026-04-18 (stable domain, registry API unlikely to change)
