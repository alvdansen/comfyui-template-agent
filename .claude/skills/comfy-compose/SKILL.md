---
name: comfy-compose
description: "When the user wants to build a new ComfyUI workflow -- from scratch, from a template scaffold, or by modifying an existing workflow file"
---

# Workflow Composition

Compose valid ComfyUI workflow JSON through guided building or template scaffolding.

<important>
ComfyUI MCP server must be connected (comfyui-cloud or comfyui-mcp). Test by calling `search_nodes` -- if it fails, instruct user to start ComfyUI + MCP server.
</important>

## Two Starting Paths

**Goal-based**: User describes what they want ("Flux img2img workflow"). Search templates, scaffold closest match, modify.

**Node-first**: User names specific nodes. Build from scratch using WorkflowGraph.

## Commands

```bash
# Scaffold from template
python -m src.composer.compose --scaffold <template_name> --output workflow.json

# Load and modify existing workflow
python -m src.composer.compose --file workflow.json --output modified.json
```

| Flag | Description |
|------|-------------|
| `--scaffold <name>` | Start from existing template |
| `--file <path>` | Start from local workflow JSON |
| `--output <path>` | Output path (default: workflow.json) |
| `--no-validate` | Skip validation (not recommended) |
| `--no-layout` | Skip auto-layout positioning |

## Key Constraints

- NodeSpecCache is pass-through: fetch MCP specs via `search_nodes`, then feed raw dicts via `cache.from_mcp_response(name, raw)`.
- `from_json` supports both array and object link formats (ComfyUI versions differ).
- `swap_node` only removes connections when spec is provided (graceful degradation without spec).
- `auto_layout` uses DFS longest-path layer assignment -- may produce suboptimal layouts for highly connected graphs.
- `save_workflow` uses lenient validation by default since composed workflows are drafts.
- Output is always workflow format JSON (nodes[] + links[]), never API format.
- Flag custom node usage for awareness but do not force core-only replacements.
