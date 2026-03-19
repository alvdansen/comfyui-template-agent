# Phase 4: Composition - Research

**Researched:** 2026-03-19
**Domain:** ComfyUI workflow graph construction, type-safe composition, MCP-backed node specs
**Confidence:** HIGH

## Summary

Phase 4 builds a type-safe workflow graph builder that constructs valid ComfyUI workflow JSON (the `nodes[]` + `links[]` format, never API format). The two entry paths are: (1) scaffold from an existing template via deep copy + modification, and (2) compose from scratch by adding nodes and connections programmatically. Both paths must validate connection types, populate widgets_values correctly, and output structurally valid workflow JSON.

The critical technical insight is that the MCP server's `get_node_info(node_name)` tool returns full INPUT_TYPES specs from ComfyUI's `/object_info` endpoint -- including field names, types, defaults, COMBO option lists, and min/max ranges. This eliminates the need for custom `/object_info` caching or static snapshots. The builder queries MCP for node specs at composition time and uses them to: validate connection types, populate widgets_values in correct positional order, and offer COMBO options to the user.

The workflow JSON format uses `version: 0.4` (observed in real templates, not 1.0 as the spec page claims), array-format links `[link_id, origin_node_id, origin_slot, target_node_id, target_slot, type_string]`, and positional `widgets_values[]` arrays where positions map to the node's INPUT_TYPES definition order. Subgraphs live in `definitions.subgraphs[]` with their own nodes/links/inputs/outputs. Auto-layout uses a simple left-to-right DAG layer assignment algorithm -- "good enough" spacing that users polish in ComfyUI Desktop.

**Primary recommendation:** Build a `WorkflowGraph` class that wraps the JSON structure with methods for add_node, connect, set_widget, remove_node, and serialize. Node specs come from MCP `get_node_info()` at runtime. Type checking happens on every `connect()` call. Scaffold is implemented as `WorkflowGraph.from_json(deep_copy)` + modification methods.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Full graph complexity -- support any valid ComfyUI graph including branching, multi-path, and basic subgraphs
- Ask for key params -- auto-default most parameters (using MCP search_nodes defaults), but prompt for important ones (model, resolution, steps)
- Both starting paths: goal-based for common patterns ("I want a Flux img2img workflow"), node-first for custom builds
- Best available nodes -- suggest whatever works best regardless of core/custom, flag custom nodes for awareness
- Auto-layout with human polish -- builder auto-places nodes in logical flow, user does a polish pass in ComfyUI UI
- Auto-generate titles/descriptions -- Claude generates based on nodes used
- Basic subgraph support -- wrapping a set of nodes into a named subgraph
- Output path: default to current directory, `--output` flag for custom path
- MCP server required for composition -- error if comfyui-mcp not available
- Cloud submission via MCP -- offer to submit composed workflow to Comfy Cloud for testing via submit_workflow
- Cloud-first option -- user can also START by using Comfy Cloud to test/iterate
- All scaffold operations: swap nodes, change parameters, add/remove nodes, rewire connections
- Both scaffold sources: 400+ template library (Phase 2 search) OR load local workflow JSON file
- Scaffold is a deep copy + modification, not in-place editing
- Always workflow format (nodes[] + links[]), never API format (COMP-04)
- Use Phase 3 validator engine for guideline compliance check on final output

### Claude's Discretion
- Interaction model specifics (conversational vs programmatic vs hybrid)
- Validation granularity during incremental composition
- MCP integration approach (direct calls vs cached wrapper)
- Auto-layout algorithm
- Type checking implementation for node connections
- How to handle connection type mismatches during composition

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| COMP-01 | User can scaffold a new workflow from an existing template and modify/extend it | WorkflowGraph.from_json() + deep copy pattern, scaffold operations (swap_node, set_widget, add_node, remove_node, connect, disconnect) |
| COMP-02 | User can compose valid workflow JSON from scratch via type-safe graph builder | WorkflowGraph class with MCP-backed node specs, type-checked connections, auto-populated widgets_values |
| COMP-03 | User can compose workflows incrementally with per-step validation | Light validation on each connect() call (type check), full validation via run_validation() on save |
| COMP-04 | Composed workflows use correct workflow format (not API format) | WorkflowGraph.serialize() always outputs workflow format with nodes[], links[], version 0.4 |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | 2.12+ | Graph node/link/workflow models | Already used project-wide for data models |
| copy (stdlib) | - | Deep copy for scaffold operations | Standard approach for immutable-source cloning |
| uuid (stdlib) | - | Generate subgraph IDs | Subgraph IDs are UUID-format strings |
| json (stdlib) | - | Workflow JSON serialization | Direct JSON output |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| comfyui-mcp (MCP tool) | latest | Node specs via get_node_info(), submit_workflow() | Every composition operation that needs node input/output specs |
| src/validator/engine.py | existing | run_validation() on composed output | Final validation before save |
| src/templates/fetch.py | existing | fetch_workflow_json() for scaffold base | When scaffolding from template library |
| src/shared/format_detector.py | existing | detect_format() gate | Ensure output is workflow format |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Runtime MCP calls for node specs | Static data/core_nodes_specs.json | MCP gives live specs for ALL nodes (core + custom); static file goes stale and only covers core |
| Custom graph class | networkx | Overkill -- we need ~5 methods, not a full graph library |
| Array-format links | Object-format links | Real templates use array format; spec says objects are also valid but templates don't use them |

**Installation:**
```bash
# No new packages needed -- uses existing project dependencies + MCP tools
pip install -e .  # existing project setup
```

## Architecture Patterns

### Recommended Project Structure
```
src/
  composer/
    __init__.py
    graph.py          # WorkflowGraph class (core builder)
    models.py         # Pydantic models for composition (GraphNode, GraphLink, NodeSpec)
    scaffold.py       # Scaffold operations (from_template, from_local_file)
    layout.py         # Auto-layout algorithm
    node_specs.py     # MCP wrapper for node spec fetching + in-memory cache
    serialize.py      # Export to workflow JSON format
    compose.py        # CLI entry point + format functions
```

### Pattern 1: WorkflowGraph Builder
**What:** A mutable graph object that wraps the workflow JSON structure with typed methods.
**When to use:** Every composition operation (scratch or scaffold).
**Example:**
```python
# Source: Pattern derived from real template analysis + ComfyUI workflow spec
class WorkflowGraph:
    """Type-safe ComfyUI workflow graph builder."""

    def __init__(self):
        self._nodes: dict[int, GraphNode] = {}
        self._links: list[GraphLink] = []
        self._next_node_id: int = 1
        self._next_link_id: int = 1
        self._groups: list[dict] = []
        self._definitions: dict = {"subgraphs": []}
        self._extra: dict = {}

    @classmethod
    def from_json(cls, workflow_data: dict) -> "WorkflowGraph":
        """Create graph from existing workflow JSON (scaffold entry point).
        Uses deep copy -- original data is never modified."""
        import copy
        data = copy.deepcopy(workflow_data)
        graph = cls()
        # Parse nodes, links, groups, definitions from data
        # Rebuild internal state from parsed data
        return graph

    def add_node(self, node_type: str, title: str = "",
                 position: tuple[float, float] | None = None,
                 widgets_values: list | None = None) -> int:
        """Add a node. Returns node ID."""
        # Fetch spec from MCP if not cached
        # Auto-populate widgets_values from defaults if not provided
        # Auto-assign position if not provided (layout algo)
        pass

    def connect(self, source_node_id: int, source_output: int | str,
                target_node_id: int, target_input: int | str) -> int:
        """Connect two nodes. Returns link ID.
        Validates type compatibility. Raises TypeError on mismatch."""
        # Resolve output type from source node spec
        # Resolve input type from target node spec
        # Check type compatibility
        # Create link entry
        pass

    def set_widget(self, node_id: int, widget_name: str, value) -> None:
        """Set a widget value by name (not position).
        Validates value against spec (COMBO options, min/max)."""
        pass

    def swap_node(self, node_id: int, new_type: str) -> None:
        """Replace a node's type, preserving compatible connections."""
        pass

    def remove_node(self, node_id: int) -> None:
        """Remove node and all its connections."""
        pass

    def serialize(self) -> dict:
        """Export as workflow format JSON dict."""
        pass
```

### Pattern 2: MCP-Backed Node Spec Cache
**What:** A thin wrapper around MCP `get_node_info()` that caches specs in memory for the session.
**When to use:** Every time the builder needs to know a node's inputs/outputs/defaults.
**Example:**
```python
class NodeSpecCache:
    """Cache node specs from MCP get_node_info() for the session."""

    def __init__(self):
        self._cache: dict[str, NodeSpec] = {}

    def get(self, node_type: str) -> NodeSpec:
        """Get node spec, fetching from MCP if not cached."""
        if node_type not in self._cache:
            # Call MCP get_node_info(node_type)
            # Parse into NodeSpec model
            # Cache for session
            pass
        return self._cache[node_type]

class NodeSpec(BaseModel):
    """Parsed node specification from MCP/object_info."""
    name: str
    display_name: str = ""
    category: str = ""
    inputs_required: dict[str, InputSpec] = {}
    inputs_optional: dict[str, InputSpec] = {}
    outputs: list[OutputSpec] = []
    is_output_node: bool = False

class InputSpec(BaseModel):
    """Single input specification."""
    name: str
    type: str  # "IMAGE", "LATENT", "INT", "FLOAT", "STRING", "COMBO", etc.
    default: Any = None
    min: float | None = None
    max: float | None = None
    step: float | None = None
    combo_options: list[str] | None = None  # For COMBO type
    is_widget: bool = True  # False for connection-only inputs like IMAGE, LATENT

class OutputSpec(BaseModel):
    """Single output specification."""
    name: str
    type: str  # "IMAGE", "LATENT", "MODEL", etc.
```

### Pattern 3: Scaffold Deep Copy + Modify
**What:** Load existing template, deep copy, then apply modifications using graph methods.
**When to use:** COMP-01 scaffold path.
**Example:**
```python
def scaffold_from_template(template_name: str) -> WorkflowGraph:
    """Load template and create a modifiable graph."""
    from src.templates.fetch import fetch_workflow_json
    workflow_data = fetch_workflow_json(template_name)
    if not workflow_data:
        raise ValueError(f"Template '{template_name}' not found")
    return WorkflowGraph.from_json(workflow_data)

def scaffold_from_file(file_path: str) -> WorkflowGraph:
    """Load local workflow JSON and create a modifiable graph."""
    import json
    from src.shared.format_detector import detect_format
    with open(file_path) as f:
        data = json.load(f)
    if detect_format(data) != "workflow":
        raise ValueError("File is not workflow format (nodes[] + links[])")
    return WorkflowGraph.from_json(data)
```

### Pattern 4: Auto-Layout (DAG Layer Assignment)
**What:** Assign node positions using topological sort + layer assignment. Left-to-right flow.
**When to use:** After all nodes and connections are established, before serialize.
**Example:**
```python
def auto_layout(graph: WorkflowGraph,
                x_spacing: float = 400,
                y_spacing: float = 150,
                start_x: float = 100,
                start_y: float = 200) -> None:
    """Assign positions to nodes using DAG layer assignment.

    Algorithm:
    1. Topological sort nodes
    2. Assign each node to a layer (column) based on longest path from source
    3. Within each layer, space nodes vertically
    4. Set pos = [start_x + layer * x_spacing, start_y + row * y_spacing]
    """
    pass
```

### Anti-Patterns to Avoid
- **Raw JSON string construction:** Never use string formatting or f-strings to build workflow JSON. Always use the WorkflowGraph builder which validates structure.
- **Positional widgets_values without spec:** Never guess widget positions. Always look up the node spec to map widget names to positions.
- **Assuming node type names:** Never hardcode node types. Validate against MCP registry or core_nodes.json.
- **In-place template modification:** Always deep copy first. The scaffold source must remain unchanged.
- **Generating API format accidentally:** The builder must always output workflow format. Use format_detector as a final gate.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Node input/output specs | Static JSON files of all node definitions | MCP `get_node_info()` with in-memory cache | Specs change across ComfyUI versions; MCP gives live data for all installed nodes including custom |
| Widget name-to-position mapping | Custom parser for INPUT_TYPES ordering | Derive from MCP spec's `input.required` + `input.optional` dict ordering | Dict ordering in Python 3.7+ preserves insertion order; ComfyUI returns inputs in widget position order |
| Type compatibility checking | Custom type hierarchy | Simple equality check on type strings | ComfyUI uses string-based type matching; "IMAGE" must match "IMAGE". Wildcards (`*`) accept anything. |
| Workflow format validation | Custom schema validator | `src/shared/format_detector.py` + `src/validator/engine.py` | Already built in Phase 3; reuse directly |
| Guideline compliance | New validation logic | `run_validation()` from Phase 3 | Already covers all template guidelines |
| Template fetching | Custom GitHub fetcher | `fetch_workflow_json()` from Phase 2 | Already handles caching, .app suffix, CDN routing |
| Graph layout | Complex force-directed layout | Simple topological layer assignment | Templates need "good enough" layout; users polish in ComfyUI UI |

**Key insight:** The MCP server is the single source of truth for node specifications. Building custom caching of /object_info or static node definition files is unnecessary and will go stale. The tradeoff is that composition requires a running ComfyUI instance connected via MCP -- but CONTEXT.md explicitly locks this: "MCP server required for composition."

## Common Pitfalls

### Pitfall 1: widgets_values Positional Ordering
**What goes wrong:** widgets_values is a positional array where each index maps to a specific input parameter. If the order is wrong, parameters get assigned to the wrong widgets -- seed goes where sampler_name should be, etc.
**Why it happens:** The mapping from position to parameter name is implicit. It follows the order of INPUT_TYPES from /object_info, but excludes inputs that are connection-only (like IMAGE, LATENT, MODEL) and excludes inputs with `defaultInput: true` or `forceInput: true`.
**How to avoid:** Build widgets_values by iterating the node spec's required+optional inputs in order, skipping non-widget types (IMAGE, LATENT, MODEL, CLIP, VAE, CONDITIONING, MASK, AUDIO, NOISE, SAMPLER, SIGMAS, GUIDER, and any custom tensor types). Only primitive types (INT, FLOAT, STRING, BOOLEAN) and COMBO become widgets.
**Warning signs:** widgets_values array length doesn't match expected widget count; values appear in wrong UI fields when loaded.

### Pitfall 2: Link Array Format vs Object Format
**What goes wrong:** The official spec says links can be objects with `id`, `origin_id`, `origin_slot`, `target_id`, `target_slot`, `type` fields. But real templates use the array format: `[link_id, origin_node_id, origin_slot, target_node_id, target_slot, type_string]`.
**Why it happens:** The spec documents both formats. The ComfyUI frontend writes array format. Using object format may not load correctly in some versions.
**How to avoid:** Always output array-format links. Parse both formats when reading (for from_json compatibility).
**Warning signs:** Workflow loads but connections don't appear; links show as objects in output JSON.

### Pitfall 3: Stale Node ID / Link ID Counters
**What goes wrong:** `last_node_id` and `last_link_id` at the top level must equal the actual maximum ID in the workflow. If they're wrong, ComfyUI may create duplicate IDs when the user adds nodes in the UI, causing silent corruption.
**Why it happens:** After adding/removing nodes during scaffold modification, the counters aren't updated.
**How to avoid:** Compute `last_node_id` and `last_link_id` from actual max IDs during serialize(), never maintain them manually.
**Warning signs:** Duplicate node IDs after user edits in ComfyUI; "node already exists" errors.

### Pitfall 4: Missing Required Node Fields
**What goes wrong:** Generated nodes lack required fields like `flags: {}`, `order: N`, `mode: 0`, `properties: {}`, causing load failures.
**Why it happens:** The builder focuses on functional fields (type, inputs, outputs, widgets_values) and forgets structural fields.
**How to avoid:** Ensure every node has: id, type, pos, size, flags, order, mode, properties, inputs, outputs, widgets_values. Set defaults: `flags: {}`, `mode: 0`, `properties: {"Node name for S&R": node_type}`.
**Warning signs:** Workflow JSON loads but nodes appear broken or invisible.

### Pitfall 5: Subgraph ID Format
**What goes wrong:** Subgraph IDs must be UUID-format strings (e.g., `"ef10a538-17cf-46fb-930c-5460c4cf7f0e"`). Nodes referencing subgraphs use this UUID as their `type` field. Using non-UUID strings breaks subgraph resolution.
**Why it happens:** Builder generates simple string IDs instead of UUIDs.
**How to avoid:** Use `uuid.uuid4()` for subgraph IDs. The `extract_node_types()` function in cross_ref.py already filters UUID-pattern types.
**Warning signs:** Subgraph nodes show as "unknown type" in ComfyUI.

### Pitfall 6: MCP Server Not Running
**What goes wrong:** Composition silently fails or crashes when the comfyui-mcp server is not connected.
**Why it happens:** MCP tools are external dependencies. The server may not be running or ComfyUI may not be started.
**How to avoid:** Check MCP availability at composition start. Provide a clear error message: "Composition requires a running ComfyUI instance with the comfyui-mcp server connected. Start ComfyUI and ensure the MCP server is active."
**Warning signs:** "Tool not found" errors; empty node specs.

## Code Examples

### Workflow JSON Structure (from real template analysis)
```python
# Source: Analysis of templates_rob_wan_ati_motion_control and other real templates
WORKFLOW_STRUCTURE = {
    "id": "uuid-string",           # Optional, workflow UUID
    "revision": 0,                  # Optional
    "last_node_id": 136,            # REQUIRED: max node ID in workflow
    "last_link_id": 178,            # REQUIRED: max link ID in workflow
    "nodes": [                      # REQUIRED: array of node objects
        {
            "id": 77,              # Unique integer ID
            "type": "LoadImage",   # Node class name (or UUID for subgraph ref)
            "pos": [15.0, 331.7],  # [x, y] position
            "size": [410, 470],    # [width, height]
            "flags": {},           # Usually empty
            "order": 0,            # Execution order
            "mode": 0,             # 0=always, 2=never, 4=bypass
            "inputs": [            # Connection inputs
                {
                    "name": "images",
                    "type": "IMAGE",
                    "link": 878,       # Link ID or null
                    # Optional: "shape": 7 (for optional inputs)
                }
            ],
            "outputs": [           # Connection outputs
                {
                    "name": "IMAGE",
                    "type": "IMAGE",
                    "links": [864],    # Array of link IDs or null
                }
            ],
            "properties": {        # Node properties
                "Node name for S&R": "LoadImage",
                "cnr_id": "comfy-core",  # Optional: pack ID
                "ver": "0.3.65",         # Optional: version
            },
            "widgets_values": [    # Positional widget values
                "white_tiger.png",
                "image"
            ],
            "title": "Custom Title",  # Optional: display title
            "color": "#232",          # Optional: node color
            "bgcolor": "#353",        # Optional: node background
        }
    ],
    "links": [                      # REQUIRED: array of link arrays
        # [link_id, origin_node_id, origin_slot, target_node_id, target_slot, type]
        [863, 472, 0, 476, 0, "INT"],
        [864, 460, 0, 476, 1, "IMAGE"],
    ],
    "groups": [],                   # Optional: visual groupings
    "definitions": {                # Optional: subgraph definitions
        "subgraphs": [
            {
                "id": "uuid-string",
                "version": "...",
                "state": {},
                "name": "Subgraph Name",
                "inputNode": "...",
                "outputNode": "...",
                "inputs": [
                    {
                        "id": "uuid",
                        "name": "amount",
                        "type": "INT",
                        "linkIds": [852],
                        "pos": [-2280, 709],
                    }
                ],
                "outputs": [
                    {
                        "id": "uuid",
                        "name": "width",
                        "type": "INT",
                        "linkIds": [829, 834],
                        "pos": [-1240, 689],
                    }
                ],
                "widgets": [],
                "nodes": [],       # Same format as top-level nodes
                "groups": [],
                "links": [],       # Same format as top-level links
                "extra": {},
            }
        ]
    },
    "config": {},                   # Optional
    "extra": {},                    # Optional
    "version": 0.4,                 # REQUIRED: format version
}
```

### MCP get_node_info Response Structure
```python
# Source: IO-AtelierTech/comfyui-mcp models.py + ComfyUI /object_info docs
# MCP get_node_info("KSampler") returns:
NODE_INFO_EXAMPLE = {
    "name": "KSampler",
    "display_name": "KSampler",
    "description": "...",
    "category": "sampling",
    "input": {
        "required": {
            "model": ["MODEL"],           # Connection type -- NOT a widget
            "seed": ["INT", {             # Widget: INT with constraints
                "default": 0,
                "min": 0,
                "max": 0xffffffffffffffff,
                "control_after_generate": True,
            }],
            "steps": ["INT", {
                "default": 20,
                "min": 1,
                "max": 10000,
            }],
            "cfg": ["FLOAT", {
                "default": 8.0,
                "min": 0.0,
                "max": 100.0,
                "step": 0.1,
                "round": 0.01,
            }],
            "sampler_name": [             # COMBO: list of options
                ["euler", "euler_a", "heun", "dpm_2", "..."],
            ],
            "scheduler": [
                ["normal", "karras", "exponential", "sgm_uniform", "..."],
            ],
            "positive": ["CONDITIONING"],  # Connection type
            "negative": ["CONDITIONING"],  # Connection type
            "latent_image": ["LATENT"],    # Connection type
        },
        "optional": {
            "denoise": ["FLOAT", {
                "default": 1.0,
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
            }],
        }
    },
    "output": ["LATENT"],
    "output_name": ["LATENT"],
    "output_node": False,
}
```

### Widget vs Connection Type Classification
```python
# Source: ComfyUI docs + analysis of INPUT_TYPES patterns
# Types that are CONNECTION-ONLY (never widgets):
CONNECTION_TYPES = {
    "MODEL", "CLIP", "VAE", "CONDITIONING", "LATENT", "IMAGE", "MASK",
    "AUDIO", "NOISE", "SAMPLER", "SIGMAS", "GUIDER", "CONTROL_NET",
    "STYLE_MODEL", "GLIGEN", "UPSCALE_MODEL", "TAESD",
}

# Types that become WIDGETS (appear in widgets_values):
WIDGET_TYPES = {"INT", "FLOAT", "STRING", "BOOLEAN"}  # + COMBO (list type)

def is_widget_input(input_spec) -> bool:
    """Determine if an input creates a widget or is connection-only."""
    if isinstance(input_spec, list) and len(input_spec) > 0:
        type_info = input_spec[0]
        # COMBO: first element is a list of options
        if isinstance(type_info, list):
            return True
        # Primitive widget types
        if type_info in WIDGET_TYPES:
            return True
        # Connection types
        if type_info in CONNECTION_TYPES:
            return False
        # Unknown custom types -- treat as connection
        return False
    return False
```

### Type Checking on Connect
```python
# Source: ComfyUI type system analysis
def check_type_compatibility(output_type: str, input_type: str) -> bool:
    """Check if output type can connect to input type.

    Rules:
    - Exact match: "IMAGE" -> "IMAGE" = OK
    - Wildcard: "*" accepts/provides anything
    - List types: input can accept union ["IMAGE", "MASK"]
    - Otherwise: no implicit coercion
    """
    if output_type == "*" or input_type == "*":
        return True
    if isinstance(input_type, list):
        return output_type in input_type
    return output_type == input_type
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Workflow version 1.0 (spec) | Version 0.4 (real templates) | Current | Use 0.4 in output; spec page may be aspirational |
| Static /object_info snapshot | MCP get_node_info() live queries | MCP server matured 2025-2026 | No stale node specs; works for core + custom nodes |
| widgets_values only (positional) | widget_names proposed but NOT merged | PR #3625 closed Sep 2024 | Still positional-only; must derive mapping from spec |
| defaultInput included in widgets_values | defaultInput/forceInput excluded | ComfyUI issue #7777, 2025 | Widget count reduced; must check for these flags |
| Manual node layout | DAG layer assignment algorithms | comfyui-auto-nodes-layout extension | Dagre-style layout is the community standard |
| V2 node schema (define_schema + io.*) | Coexists with legacy INPUT_TYPES | ComfyUI 2025-2026 | /object_info still returns legacy format; V3 schema not yet universal |

**Deprecated/outdated:**
- PR #3625 (widget_names in JSON) -- closed, never merged. Do not rely on widget_names field existing.
- Version 1.0 in the spec docs -- real templates use version 0.4. The spec page may describe a future version.

## Open Questions

1. **MCP tool availability check**
   - What we know: The comfyui-mcp server is configured via `uvx comfyui-mcp` and connects to a local ComfyUI instance.
   - What's unclear: How to programmatically check if MCP tools are available from within Python code (not from Claude's tool context). The skill layer can check, but the Python module needs a strategy.
   - Recommendation: The skill (SKILL.md) instructs Claude to call get_node_info as a test probe. If it fails, error out with instructions. The Python builder accepts node specs as constructor args rather than calling MCP directly -- Claude fetches specs via MCP and passes them in.

2. **widgets_values for defaultInput/forceInput nodes**
   - What we know: Inputs marked defaultInput or forceInput are excluded from widgets_values as of ~2025 (issue #7777).
   - What's unclear: Whether the MCP/object_info response flags these inputs.
   - Recommendation: Check the MCP spec for `defaultInput`/`forceInput` metadata. If absent, assume all non-connection inputs are widgets (safer default, may produce extra values but won't miss any).

3. **Version field: 0.4 or 1.0?**
   - What we know: Real templates use `"version": 0.4`. The official spec page says `version: 1`.
   - What's unclear: Whether ComfyUI accepts both.
   - Recommendation: Output `0.4` to match existing templates. This is the proven-working value.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x |
| Config file | pyproject.toml (existing) |
| Quick run command | `python -m pytest tests/test_composer.py -x` |
| Full suite command | `python -m pytest tests/ -x` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| COMP-01 | Scaffold from template with modifications | unit | `python -m pytest tests/test_composer.py::test_scaffold_from_template -x` | No, Wave 0 |
| COMP-01 | Scaffold swap_node preserves connections | unit | `python -m pytest tests/test_composer.py::test_scaffold_swap_node -x` | No, Wave 0 |
| COMP-02 | Compose from scratch with type-checked connections | unit | `python -m pytest tests/test_composer.py::test_compose_from_scratch -x` | No, Wave 0 |
| COMP-02 | Type mismatch raises error | unit | `python -m pytest tests/test_composer.py::test_type_mismatch_error -x` | No, Wave 0 |
| COMP-03 | Incremental add_node + connect with validation | unit | `python -m pytest tests/test_composer.py::test_incremental_composition -x` | No, Wave 0 |
| COMP-04 | Serialized output is workflow format | unit | `python -m pytest tests/test_composer.py::test_output_workflow_format -x` | No, Wave 0 |
| COMP-04 | Output has correct structural fields | unit | `python -m pytest tests/test_composer.py::test_output_structural_fields -x` | No, Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_composer.py -x`
- **Per wave merge:** `python -m pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_composer.py` -- covers COMP-01 through COMP-04
- [ ] `tests/conftest.py` -- needs new fixtures: `sample_node_spec`, `sample_ksampler_spec`, `sample_workflow_for_scaffold`
- [ ] No new framework install needed -- pytest already configured

## Sources

### Primary (HIGH confidence)
- Real template analysis: `templates_rob_wan_ati_motion_control`, `templates_rob_realistic_2k_images_quick_variations.app` -- actual workflow JSON structure, link format, node format, subgraph structure
- [ComfyUI Workflow JSON Spec](https://docs.comfy.org/specs/workflow_json) -- official v1.0 spec (top-level fields, node/link structure)
- [ComfyUI Data Types docs](https://docs.comfy.org/custom-nodes/backend/datatypes) -- INPUT_TYPES structure, supported types, defaults/min/max/step
- [IO-AtelierTech/comfyui-mcp models.py](https://github.com/IO-AtelierTech/comfyui-mcp) -- NodeInfo model structure for /object_info responses
- Existing codebase: `src/shared/format_detector.py`, `src/templates/fetch.py`, `src/validator/engine.py`

### Secondary (MEDIUM confidence)
- [ComfyUI Issue #7777](https://github.com/comfyanonymous/ComfyUI/issues/7777) -- widgets_values exclusion of defaultInput/forceInput
- [ComfyUI PR #3625](https://github.com/comfyanonymous/ComfyUI/pull/3625) -- widget_names proposal (closed, not merged)
- [ComfyUI Discussion #4787](https://github.com/comfyanonymous/ComfyUI/discussions/4787) -- widgets_values pain points
- [comfyui-auto-nodes-layout](https://github.com/phineas-pta/comfyui-auto-nodes-layout) -- DAG layout algorithm reference (Dagre/ELK)
- [ComfyUI example_node.py](https://github.com/comfyanonymous/ComfyUI/blob/master/custom_nodes/example_node.py.example) -- V3 node schema (io.Schema)

### Tertiary (LOW confidence)
- [ComfyGPT paper](https://arxiv.org/html/2503.17671v1) -- 12-15% LLM baseline accuracy (confirmed by project research)
- Version 0.4 vs 1.0 discrepancy -- observed in templates but not explained in docs; treating 0.4 as correct

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- uses existing project dependencies, MCP is locked in CONTEXT.md
- Architecture: HIGH -- pattern derived from real template analysis and existing codebase patterns
- Pitfalls: HIGH -- verified against real templates, ComfyUI issues, and project pitfalls research
- MCP integration: MEDIUM -- MCP server structure verified but exact tool response format needs runtime validation

**Research date:** 2026-03-19
**Valid until:** 2026-04-19 (30 days -- ComfyUI ecosystem moves fast but core workflow format is stable)
