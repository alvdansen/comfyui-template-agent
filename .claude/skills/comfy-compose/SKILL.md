---
name: comfy-compose
description: "Compose valid ComfyUI workflow JSON through guided building or template scaffolding. Uses MCP node specs for type-safe connections and auto-populated widget defaults."
---

# Skill: comfy-compose

Compose valid ComfyUI workflow JSON through guided building or template scaffolding. Uses MCP node specs for type-safe connections and auto-populated widget defaults.

## Prerequisites

ComfyUI MCP server must be connected (comfyui-cloud or comfyui-mcp). Test by calling `search_nodes` -- if it fails, instruct user to start ComfyUI + MCP server.

## When to Use

- User wants to create a new ComfyUI workflow from scratch or from a template
- User wants to scaffold from an existing template and modify it
- User wants to compose a workflow with specific nodes and connections
- User wants to load a local workflow file and add/modify nodes

## Two Starting Paths

### 1. Goal-based (common patterns)
User describes what they want ("I want a Flux img2img workflow"). Claude searches templates, scaffolds the closest match, then modifies.

### 2. Node-first (custom builds)
User names specific nodes. Claude composes from scratch using WorkflowGraph.

## Composition Workflow

1. **Determine starting path** -- goal-based or node-first based on user request.
2. **If goal-based**: Search templates with `search_templates` MCP tool or `python -m src.templates.search`. Scaffold closest match with `scaffold_from_template`.
3. **If node-first**: Create empty `WorkflowGraph`, add nodes one by one.
4. **For each node**: Call MCP `search_nodes` to get full spec. Use `parse_node_spec` to convert. Feed to graph's `NodeSpecCache` via `cache.from_mcp_response(name, raw)`.
5. **Ask user about key parameters**: model, resolution, steps, CFG. Auto-default everything else from spec defaults.
6. **Connect nodes** with type checking via `graph.connect()`. Flag any custom node usage ("Note: X is a custom node -- template guidelines prefer core nodes, but it's the best option for this task").
7. **Run auto_layout** to position nodes in logical left-to-right flow.
8. **Save** with `save_workflow` which runs lenient validation automatically.
9. **Show validation report**. Fix any issues found.
10. **Offer to submit** to Comfy Cloud via `submit_workflow` MCP tool for testing.
11. **Auto-generate title and description** based on nodes used and workflow purpose.

## CLI Shortcut

```bash
python -m src.composer.compose --scaffold <template_name> --output workflow.json
python -m src.composer.compose --file <path/to/workflow.json> --output modified.json
```

### Flags

| Flag | Description |
|------|-------------|
| `--scaffold <name>` | Start from existing template |
| `--file <path>` | Start from local workflow JSON file |
| `--output <path>` | Output path (default: workflow.json) |
| `--no-validate` | Skip validation (not recommended) |
| `--no-layout` | Skip auto-layout positioning |

## Programmatic API

```python
from src.composer import WorkflowGraph, NodeSpecCache, save_workflow
from src.composer import scaffold_from_template, scaffold_from_file
from src.composer.models import parse_node_spec

# Scaffold from template
graph = scaffold_from_template("flux-schnell-basic", specs=cache)

# Or build from scratch
cache = NodeSpecCache()
spec = cache.from_mcp_response("KSampler", mcp_raw_dict)
graph = WorkflowGraph(specs=cache)
node_id = graph.add_node("KSampler")
graph.set_widget(node_id, "steps", 30)
graph.connect(src_id, 0, tgt_id, "samples")

# Save with validation
result = save_workflow(graph, "workflow.json")
```

## Usage Examples

```
"compose a Flux img2img workflow"
"scaffold from wan-t2v-basic and swap the model loader"
"compose a workflow using KSampler, VAEDecode, and SaveImage from scratch"
"load workflow.json and add an upscale step"
```

## Key Behaviors

- **Best available nodes**: Suggest whatever works best regardless of core/custom. Flag custom nodes for awareness but do not force core-only replacements.
- **Smart defaults**: Auto-populate most parameters from MCP node specs. Only ask about model, resolution, steps, and CFG.
- **Auto-generate metadata**: Create titles and descriptions from workflow content and node composition.
- **Cloud-first option**: User can submit to Comfy Cloud at any point via `submit_workflow` MCP tool, not just at the end.
- **All scaffold operations**: Swap nodes (`graph.swap_node`), change params (`graph.set_widget`), add/remove nodes, rewire connections.
- **Basic subgraph support**: Wrapping nodes into named subgraph groups.
- **Always workflow format**: Output is always workflow format JSON (nodes[] + links[]), never API format.

## Key Files

- `src/composer/compose.py` -- CLI entry point, save_workflow, format_composition_report
- `src/composer/graph.py` -- WorkflowGraph builder with type-safe connections
- `src/composer/scaffold.py` -- scaffold_from_template, scaffold_from_file
- `src/composer/layout.py` -- auto_layout algorithm
- `src/composer/models.py` -- NodeSpec, InputSpec, OutputSpec, GraphNode, GraphLink
- `src/composer/node_specs.py` -- NodeSpecCache for MCP spec caching
