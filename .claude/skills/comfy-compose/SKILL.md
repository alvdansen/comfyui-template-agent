---
name: comfy-compose
description: "When the user wants to build a new ComfyUI workflow -- from scratch, from a template scaffold, or by modifying an existing workflow file"
---

# Workflow Composition

Compose valid ComfyUI workflow JSON through guided building or template scaffolding.

<important>
Before starting, check prerequisites:

1. **ComfyUI MCP server connected** — test by calling `search_nodes`. If it fails, instruct user to start ComfyUI + MCP server.
2. **Cloud or local?** — ask the user. This determines auth and image handling.
</important>

<important if="submitting to cloud">
API node auth (Gemini, BFL, Bria, Luma) is handled automatically by the MCP server (v0.2.0+). No token passing needed.
If a LoadImage node references a local file, it won't exist on cloud — ask the user if they have the image locally and suggest alternatives.

**v0.2.1 improvements:**
- Failed jobs now return clear error messages (node type, exception). No more silent failures.
- Invalid node types and bad model names are caught before submission (pre-validation).
- `use_previous_output` tool lets you chain workflows — reuse an output image as input in the next workflow without manual download/upload.

**Polling**: Cloud jobs can take 30s to several minutes depending on complexity.
- Poll `get_job_status` every 10-15 seconds.
- Do NOT give up unless `get_job_status` returns an explicit error/failure status.
- If the job is still "running" or "queued" after 2+ minutes, ask the user: "Still running — keep waiting or cancel?" Do NOT silently stop polling.
- API node workflows (Gemini, BFL) are especially slow — budget 3-5 minutes.
</important>

<important if="submitting workflow to cloud or local execution">
Composed workflows are **workflow format** (nodes[] + links[]). The `submit_workflow` MCP tool needs **API format** (flat dict with string node IDs).

To convert, use `workflow_to_api()` from `src.shared.convert`:

```python
from src.shared.convert import workflow_to_api

api_workflow = workflow_to_api(workflow_data, node_specs=specs)
```

**You MUST look up node specs before converting.** Without specs, widget values get wrong names and the workflow silently fails or runs with defaults.

1. Collect unique `class_type` values from the workflow
2. For each, call MCP `search_nodes(q="NodeType")` to get the input schema
3. Pass specs as `{node_type: spec_dict}` to the converter
4. The converter automatically strips UI-only controls (`control_after_generate`, `upload`) that appear in widget values but aren't real node inputs

Known pitfalls without specs:
- Widget names guessed wrong (e.g. `system_instruction` vs `system_prompt`)
- UI-only values like `control_after_generate` included in API payload (causes rejection)
- Positional mismatch when required/optional input order differs from widget order
</important>

## Capabilities

- Build workflows from scratch with type-safe node connections
- Scaffold from existing templates with deep copy isolation
- Load and modify existing workflow JSON files
- Auto-layout nodes using DAG layer assignment
- Swap node types with connection compatibility checking
- Convert workflow format to API format for cloud submission

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

## Example Session

**User:** I want to build a FLUX img2img workflow
**Agent:** Searches templates with `python -m src.composer.compose --scaffold flux_schnell_simple_generation --output workflow.json`. Scaffolded from FLUX schnell template. Now modifying: replacing EmptyLatentImage with LoadImage + VAEEncode for img2img.
**User:** Add a ControlNet node too
**Agent:** Fetches ControlNet node spec via MCP `search_nodes`. Adding ControlNetApply node, connecting: ControlNet model -> ControlNetApply, image -> ControlNetApply, ControlNetApply -> KSampler conditioning. Running auto-layout.
**User:** Save and validate
**Agent:** Saves to workflow.json (8 nodes, 11 links). Runs `python -m src.validator.validate --file workflow.json --mode lenient`. 3 info-level notes, 0 errors. Draft is valid.

## Key Constraints

- NodeSpecCache is pass-through: fetch MCP specs via `search_nodes`, then feed raw dicts via `cache.from_mcp_response(name, raw)`.
- `from_json` supports both array and object link formats (ComfyUI versions differ).
- `swap_node` only removes connections when spec is provided (graceful degradation without spec).
- `auto_layout` uses DFS longest-path layer assignment -- may produce suboptimal layouts for highly connected graphs.
- Output is always workflow format JSON (nodes[] + links[]), never API format.
