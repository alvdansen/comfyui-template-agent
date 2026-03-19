# Phase 2: Template Intelligence - Research

**Researched:** 2026-03-19
**Domain:** Template data fetching, indexing, search, cross-referencing, gap analysis
**Confidence:** HIGH

## Summary

Phase 2 builds a template intelligence layer on top of Phase 1's registry infrastructure. The primary data source is the workflow_templates GitHub repo's `index.json` (a nested array of category objects containing ~60+ template entries) plus individual workflow JSON files (~70+ .json files in the `templates/` folder). The index.json provides metadata (name, title, description, mediaType, tags, models, requiresCustomNodes, io), while the workflow JSON files contain the actual node graph (nodes[] with `type` field = class_type, plus links[]).

A critical discovery: many recent templates use **subgraph UUIDs** as node types at the top level (e.g., `ef10a538-17cf-46fb-930c-5460c4cf7f0e`), with actual class_types buried inside `definitions.subgraphs[].nodes[]`. Cross-referencing must recursively extract class_types from subgraphs to be accurate. Non-subgraph templates (especially API templates) use standard class_type strings directly. The `requiresCustomNodes` field in index.json provides a shortcut for pack-level cross-referencing without parsing workflow JSON.

Gap analysis connects Phase 1 registry data (8,400+ nodes via `fetch_all_nodes()`) to template coverage. The approach is set-difference: nodes in registry minus nodes referenced in templates = uncovered nodes. Scoring by popularity (downloads, stars) surfaces the most impactful gaps. The `classify_node()` function from Phase 1 enables per-category gap breakdown.

**Primary recommendation:** Fetch index.json from GitHub raw CDN with 24hr cache, build an in-memory reverse index (node class_type -> list of templates), and use `requiresCustomNodes` for pack-level queries while lazily loading workflow JSONs for node-level queries.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **No local clone** -- fetch from GitHub API + cache, no git clone of workflow_templates
- **Daily cache with manual override** -- 24hr TTL default, user can force refresh
- **Use existing Phase 1 infrastructure** -- `src/shared/http.py`, `src/shared/cache.py`
- **Exact class_type matching by default** for cross-reference
- **Optional fuzzy matching** for "related" node discovery (e.g., all KSampler variants)
- **Count + examples** for cross-reference results: "Used in 7 templates" + top 3 examples
- **Four coverage metrics**: templates per category, node coverage %, thin spots, growth trends
- **Both gap presentation views**: default ranked list + `--by-category` flag
- **Node info + suggestion** for gap entries: include details AND suggest template idea

### Claude's Discretion
- GitHub API strategy (raw CDN for index.json vs API for individual files)
- GITHUB_TOKEN support for authenticated rate limits
- Popularity threshold for gap analysis (tiered approach recommended)
- Pack-level vs node-level gap granularity
- Coverage report format (summary vs drill-down)
- Reverse index data structure (node -> templates mapping)
- Template search algorithm (substring, regex, or weighted)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| TMPL-01 | Search existing 400+ templates by name, category, or model | index.json has `title`, `description`, `tags`, `mediaType`, `models` fields for search; substring matching on these fields covers all search dimensions |
| TMPL-02 | View template details (nodes used, models, custom node dependencies) | index.json provides `models`, `requiresCustomNodes`, `io`; workflow JSON provides full node graph with class_types; subgraph extraction needed for complete node lists |
| TMPL-03 | Check if a specific node or pack is used in existing templates | `requiresCustomNodes` field enables pack-level lookup directly from index.json; node-level requires reverse index built from workflow JSONs + subgraph extraction |
| TMPL-04 | Generate gap analysis showing popular nodes not covered by any template | Set-difference of registry nodes vs template-referenced nodes; popularity scoring from Phase 1's `fetch_all_nodes()`; `classify_node()` for category breakdown |
| TMPL-05 | View template coverage report by category | index.json `mediaType` field (image/video/audio/3d) + `tags` for subcategories; cross-reference with registry category distribution |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| httpx | 0.28+ | Fetch index.json and workflow JSONs from GitHub | Already in use (Phase 1), async-capable, proper timeout handling |
| pydantic | 2.0+ | Template and TemplateIndex models | Already in use (Phase 1), type-safe JSON parsing |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| (stdlib) json | 3.12 | Parse workflow JSON files | Always -- workflow JSONs are plain JSON |
| (stdlib) re | 3.12 | Fuzzy search with regex patterns | When user searches with partial names |
| (stdlib) collections.Counter | 3.12 | Category counting for coverage reports | Coverage report generation |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| In-memory reverse index | SQLite FTS | Overkill for ~70 templates; in-memory dict is instant and simpler |
| Substring search | Whoosh/lunr.py | Full-text search libraries add deps for negligible benefit at this scale |

**Installation:** No new dependencies needed -- reuses Phase 1's httpx + pydantic.

## Architecture Patterns

### Recommended Project Structure
```
src/
  templates/
    __init__.py
    models.py          # Template, TemplateCategory, TemplateIndex Pydantic models
    fetch.py           # Fetch index.json + individual workflow JSONs from GitHub
    search.py          # Search templates by name, category, model, tag
    cross_ref.py       # Node-to-template reverse index, cross-reference lookups
    coverage.py        # Gap analysis engine + coverage reports
```

### Pattern 1: Lazy-Load with Cached Index
**What:** Fetch and cache index.json (lightweight, ~200KB) eagerly on first use. Fetch individual workflow JSONs lazily on demand (only when user asks for node-level detail or cross-reference needs it). Cache workflow JSONs individually with 24hr TTL.
**When to use:** Always. The index has all metadata needed for search, category browsing, and pack-level cross-reference. Workflow JSONs are only needed for node-level analysis.
**Example:**
```python
# Source: project convention from Phase 1
GITHUB_RAW = "https://raw.githubusercontent.com/Comfy-Org/workflow_templates/refs/heads/main/templates"

def fetch_template_index(force_refresh: bool = False) -> list[TemplateCategory]:
    """Fetch and cache the template index.json from GitHub raw CDN."""
    cache_key = "template_index"
    if not force_refresh:
        cached = _cache.get(cache_key, CACHE_TTLS["templates"])
        if cached is not None:
            return [TemplateCategory(**c) for c in cached]

    client = get_client()  # reuse Phase 1 client but with GitHub base URL
    url = f"{GITHUB_RAW}/index.json"
    data = client.get(url).json()
    _cache.set(cache_key, data)
    return [TemplateCategory(**c) for c in data]
```

### Pattern 2: Reverse Index for Cross-Reference
**What:** Build a dict mapping `node_class_type -> list[TemplateSummary]` and `node_pack_id -> list[TemplateSummary]` from the template data. Pack-level index uses `requiresCustomNodes` from index.json (no workflow fetch needed). Node-level index requires fetching and parsing workflow JSONs.
**When to use:** For TMPL-03 (cross-reference) and TMPL-04 (gap analysis).
**Example:**
```python
def build_pack_index(categories: list[TemplateCategory]) -> dict[str, list[TemplateSummary]]:
    """Build pack_id -> templates mapping from index.json requiresCustomNodes."""
    index: dict[str, list[TemplateSummary]] = {}
    for cat in categories:
        for tmpl in cat.templates:
            for pack_id in (tmpl.requiresCustomNodes or []):
                index.setdefault(pack_id, []).append(
                    TemplateSummary(name=tmpl.name, title=tmpl.title,
                                   mediaType=tmpl.mediaType, tags=tmpl.tags)
                )
    return index
```

### Pattern 3: Subgraph-Aware Node Extraction
**What:** When extracting node class_types from a workflow JSON, recursively walk `definitions.subgraphs[].nodes[]` in addition to the top-level `nodes[]`. Filter out UUID-style type values (subgraph references) and collect actual class_type strings.
**When to use:** For node-level cross-reference and gap analysis.
**Example:**
```python
import re

_UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

def extract_node_types(workflow: dict) -> set[str]:
    """Extract all node class_types from a workflow, including subgraph internals."""
    types: set[str] = set()
    # Top-level nodes
    for node in workflow.get("nodes", []):
        node_type = node.get("type", "")
        if node_type and not _UUID_PATTERN.match(node_type):
            types.add(node_type)
    # Subgraph nodes
    for subgraph in workflow.get("definitions", {}).get("subgraphs", []):
        for node in subgraph.get("nodes", []):
            node_type = node.get("type", "")
            if node_type and not _UUID_PATTERN.match(node_type):
                types.add(node_type)
    return types
```

### Pattern 4: Two-Phase Gap Analysis
**What:** Phase A uses pack-level data (fast, from index.json only). Phase B uses node-level data (slower, requires fetching workflow JSONs). Default to Phase A for quick results; upgrade to Phase B when user needs node-specific gaps.
**When to use:** TMPL-04 gap analysis.

### Anti-Patterns to Avoid
- **Fetching all 70+ workflow JSONs eagerly:** Each is 20-50KB. Total ~2-3MB but 70+ HTTP requests. Lazy-load and cache individually.
- **Ignoring subgraph definitions:** Many recent templates wrap all logic in subgraphs. Top-level nodes[] may only show `SaveImage` + a UUID, missing all the real class_types.
- **Using GitHub API for file content:** The API has 60 req/hr unauthenticated limit. Use raw.githubusercontent.com CDN instead (no rate limit for public repos).
- **Building full reverse index on every query:** Build once, cache the index alongside template data with same TTL.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTP + caching | Custom HTTP layer | Phase 1's `http.py` + `cache.py` | Already tested, handles timeouts and errors |
| Category classification | New category mapper | Phase 1's `classify_node()` | Consistent categories across registry and templates |
| Node popularity scoring | New scoring heuristic | Phase 1's `_score_trending()` / `fetch_all_nodes()` | Already has download/star/age weighting |
| UUID detection | String parsing | `re.compile(UUID_PATTERN)` | Standard regex, no reinvention |

**Key insight:** Phase 2 is primarily a data integration layer. The building blocks (HTTP, cache, node data, categories) all exist from Phase 1. The new work is: Pydantic models for template data, search logic, reverse index construction, and gap analysis scoring.

## Common Pitfalls

### Pitfall 1: index.json Structure Assumption
**What goes wrong:** Assuming index.json is a flat array of template objects. It's actually an array of category objects, each containing a `templates[]` array.
**Why it happens:** The schema isn't documented in the README; you must inspect the actual data.
**How to avoid:** Model as `list[TemplateCategory]` where `TemplateCategory` has `moduleName`, `category`, `title`, `type`, `templates: list[Template]`.
**Warning signs:** Template count seems low (getting category count instead of template count).

### Pitfall 2: Template Name != Filename
**What goes wrong:** Assuming the `name` field in index.json directly maps to `{name}.json` filename.
**Why it happens:** Some names have `.app` suffix, some use `templates_` or `templates-` prefixes.
**How to avoid:** When fetching individual workflow JSONs, try the name as-is, then strip `.app`, then try common prefix variations. Or fetch the directory listing once and build a name-to-filename mapping.
**Warning signs:** 404 errors when fetching individual templates.

### Pitfall 3: Subgraph Node Extraction
**What goes wrong:** Cross-reference misses most nodes because recent templates wrap everything in subgraphs. Top-level `nodes[]` shows only `SaveImage` + a UUID subgraph reference.
**Why it happens:** ComfyUI introduced subgraphs in 2025-2026; the workflow_templates repo adopted them for cleaner UX.
**How to avoid:** Always extract from `definitions.subgraphs[].nodes[]` as well as top-level. Filter UUID type values.
**Warning signs:** Cross-reference shows most nodes unused in templates when they clearly are.

### Pitfall 4: GitHub Rate Limits
**What goes wrong:** Hitting 60 req/hr limit when fetching individual workflow JSONs for node extraction.
**Why it happens:** Gap analysis needs to scan all ~70 templates for node types.
**How to avoid:** Use raw.githubusercontent.com (CDN, no rate limit) instead of api.github.com. Cache aggressively (24hr TTL). Build the full reverse index in one batch fetch, not per-query.
**Warning signs:** HTTP 429 responses, "API rate limit exceeded" errors.

### Pitfall 5: Missing requiresCustomNodes Field
**What goes wrong:** Assuming all templates have the `requiresCustomNodes` field populated.
**Why it happens:** Some older templates or templates using only core nodes omit this field.
**How to avoid:** Default to empty list. For accurate cross-reference, parse the actual workflow JSON rather than relying solely on index.json metadata.
**Warning signs:** Pack cross-reference shows 0 results for a pack you know is used.

## Code Examples

### Template Index Pydantic Models
```python
# Source: index.json schema analysis
from pydantic import BaseModel, Field

class TemplateIO(BaseModel):
    nodeId: int
    nodeType: str
    file: str = ""
    mediaType: str = ""

class TemplateIOSpec(BaseModel):
    inputs: list[TemplateIO] = []
    outputs: list[TemplateIO] = []

class Template(BaseModel):
    name: str
    title: str
    description: str = ""
    mediaType: str = ""
    mediaSubtype: str = ""
    tags: list[str] = []
    models: list[str] = []
    requiresCustomNodes: list[str] = []
    date: str = ""
    openSource: bool = True
    size: int = 0
    vram: int = 0
    usage: int = 0
    searchRank: int = 0
    username: str = ""
    io: TemplateIOSpec = Field(default_factory=TemplateIOSpec)
    thumbnail: list[str] = []

class TemplateCategory(BaseModel):
    moduleName: str = ""
    category: str = ""
    icon: str = ""
    title: str = ""
    type: str = ""
    isEssential: bool = False
    templates: list[Template] = []
```

### GitHub Raw CDN Fetch (No Rate Limits)
```python
# Source: project convention
import httpx

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Comfy-Org/workflow_templates/refs/heads/main/templates"

def fetch_from_github_raw(filename: str) -> dict:
    """Fetch a file from the workflow_templates repo via raw CDN (no rate limit)."""
    url = f"{GITHUB_RAW_BASE}/{filename}"
    # Create a standalone client (not the registry API client which has base_url set)
    with httpx.Client(timeout=httpx.Timeout(15.0, connect=5.0),
                      headers={"User-Agent": "ComfyTemplateAgent/1.0"}) as client:
        resp = client.get(url, follow_redirects=True)
        resp.raise_for_status()
        return resp.json()
```

### Gap Analysis Opportunity Scoring
```python
# Source: project convention, building on Phase 1 heuristics
def score_gap_opportunity(node_pack: NodePack, template_count: int) -> float:
    """Score how valuable a template for this node would be.

    Higher score = more valuable gap to fill.
    Factors: popularity (downloads), community interest (stars), zero template coverage.
    """
    if template_count > 0:
        return 0.0  # Not a gap

    dl_score = math.log(node_pack.downloads + 1, 10)  # log10 scale
    star_score = math.log(node_pack.github_stars + 1, 2)  # log2 scale

    return dl_score * (1 + star_score * 0.5)
```

### Search with Weighted Matching
```python
# Source: standard pattern
def search_templates(
    categories: list[TemplateCategory],
    query: str,
    media_type: str | None = None,
    model: str | None = None,
) -> list[Template]:
    """Search templates by name/description, optionally filtered by type or model."""
    query_lower = query.lower()
    results: list[tuple[float, Template]] = []

    for cat in categories:
        for tmpl in cat.templates:
            if media_type and tmpl.mediaType != media_type:
                continue
            if model and not any(model.lower() in m.lower() for m in tmpl.models):
                continue

            score = 0.0
            if query_lower in tmpl.title.lower():
                score += 3.0  # Title match is strongest
            if query_lower in tmpl.description.lower():
                score += 1.0
            if any(query_lower in tag.lower() for tag in tmpl.tags):
                score += 2.0

            if score > 0:
                results.append((score, tmpl))

    results.sort(key=lambda x: (-x[0], x[1].title))
    return [tmpl for _, tmpl in results]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| All templates use direct class_types | Many use subgraph UUIDs wrapping class_types | 2025-2026 | Must extract from definitions.subgraphs |
| index.json flat template list | Nested category objects with templates arrays | Recent | Model must reflect nested structure |
| Templates reference core nodes only | Templates now include requiresCustomNodes field | Recent | Enables pack-level cross-reference without parsing workflow JSON |

**Deprecated/outdated:**
- None specific to this phase -- the data format is current and actively maintained.

## Open Questions

1. **Template name to filename mapping**
   - What we know: Names in index.json don't always match filenames 1:1. Some have `.app` suffix, different prefix conventions.
   - What's unclear: The exact mapping rule. May need to fetch the directory listing once or use a known mapping pattern.
   - Recommendation: Fetch the GitHub directory listing once (cached), build a name-to-filename lookup. Fall back to trying `{name}.json` directly.

2. **Growth trends data source**
   - What we know: Coverage report should show "growth trends" per CONTEXT.md decisions.
   - What's unclear: index.json has a `date` field per template. No historical snapshots exist.
   - Recommendation: Use template `date` fields to show "templates added per month" as the growth trend. This is the only data available without tracking changes over time.

3. **Node coverage % denominator**
   - What we know: "Node coverage %" requires knowing total unique nodes. Registry has ~8,400 node packs, each containing multiple class_types.
   - What's unclear: Whether to measure coverage at pack level (simpler, ~300 from fetch_all_nodes) or individual class_type level (more accurate, much larger number).
   - Recommendation: Pack-level for the default metric (using `requiresCustomNodes`), with node-level as an optional deep-dive.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0+ |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `python -m pytest tests/test_templates.py -x` |
| Full suite command | `python -m pytest tests/ -x` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TMPL-01 | Search templates by name/category/model | unit | `python -m pytest tests/test_template_search.py -x` | No -- Wave 0 |
| TMPL-02 | View template details with nodes/models/deps | unit | `python -m pytest tests/test_template_fetch.py -x` | No -- Wave 0 |
| TMPL-03 | Cross-reference node/pack against templates | unit | `python -m pytest tests/test_cross_ref.py -x` | No -- Wave 0 |
| TMPL-04 | Gap analysis with popularity scoring | unit | `python -m pytest tests/test_coverage.py::test_gap_analysis -x` | No -- Wave 0 |
| TMPL-05 | Coverage report by category | unit | `python -m pytest tests/test_coverage.py::test_coverage_report -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_template_search.py tests/test_template_fetch.py tests/test_cross_ref.py tests/test_coverage.py -x`
- **Per wave merge:** `python -m pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_template_search.py` -- covers TMPL-01
- [ ] `tests/test_template_fetch.py` -- covers TMPL-02
- [ ] `tests/test_cross_ref.py` -- covers TMPL-03
- [ ] `tests/test_coverage.py` -- covers TMPL-04, TMPL-05
- [ ] Test fixtures: sample index.json data, sample workflow JSON with subgraphs, sample workflow JSON without subgraphs

## Sources

### Primary (HIGH confidence)
- GitHub `Comfy-Org/workflow_templates/templates/index.json` -- live data fetched and analyzed, ~60+ templates in nested category structure
- GitHub `Comfy-Org/workflow_templates/templates/*.json` -- individual workflow files inspected, confirmed workflow format with subgraph support
- GitHub `Comfy-Org/workflow_templates/README.md` -- file naming, bundle structure, directory organization
- Phase 1 source code (`src/shared/`, `src/registry/`) -- established patterns for HTTP, caching, models, scoring

### Secondary (MEDIUM confidence)
- `.planning/research/SUMMARY.md` -- gap analysis as killer differentiator, architecture patterns
- `.planning/research/ARCHITECTURE.md` -- template browser component design, data flow

### Tertiary (LOW confidence)
- Template name-to-filename mapping -- inferred from inspection, not documented. Needs validation during implementation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new dependencies, reuses Phase 1 infrastructure
- Architecture: HIGH -- data source fully inspected, models can be directly derived from live data
- Pitfalls: HIGH -- subgraph extraction verified against actual template files, rate limit issue well-documented
- Gap analysis: MEDIUM -- scoring heuristic is reasonable but may need tuning based on actual data distribution

**Research date:** 2026-03-19
**Valid until:** 2026-04-19 (30 days -- template repo structure is stable)
