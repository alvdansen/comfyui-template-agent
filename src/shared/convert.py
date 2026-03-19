"""Convert between ComfyUI workflow format and API format.

Workflow format: nodes[] + links[] (used by UI, templates)
API format: flat dict with string node IDs, class_type + inputs (used for execution)
"""

from __future__ import annotations

from typing import Any

from src.composer.models import CONNECTION_TYPES


# UI-only node types that don't execute — safe to skip
UI_ONLY_TYPES = {"Note", "MarkdownNote", "PrimitiveNode", "Reroute"}

# UI-only widget names that appear in widgets_values but are NOT real node inputs.
# These are frontend controls that should be stripped during conversion.
UI_ONLY_WIDGETS = {"control_after_generate", "upload"}


def workflow_to_api(workflow: dict, node_specs: dict[str, dict] | None = None) -> dict:
    """Convert workflow-format JSON to API-format JSON.

    IMPORTANT: For accurate conversion, pass node_specs from MCP search_nodes.
    Without specs, widget values (seed, steps, cfg, model name, etc.) cannot be
    mapped to their correct input names — the workflow will run with defaults.

    Args:
        workflow: Workflow-format dict with nodes[] and links[].
        node_specs: Dict of node_type -> spec info (from MCP search_nodes).
            Required inputs first, then optional, positionally mapped to
            widgets_values. UI-only controls (control_after_generate, upload)
            are automatically stripped.

    Returns:
        API-format dict ready for submit_workflow.
    """
    nodes = workflow.get("nodes", [])
    links = workflow.get("links", [])

    # Build link lookup: link_id -> (origin_node_id, origin_slot)
    link_map: dict[int, tuple[int, int]] = {}
    for link in links:
        if isinstance(link, list) and len(link) >= 5:
            link_id, origin_id, origin_slot = link[0], link[1], link[2]
            link_map[link_id] = (origin_id, origin_slot)
        elif isinstance(link, dict):
            link_map[link["id"]] = (link["origin_id"], link["origin_slot"])

    api = {}

    for node in nodes:
        node_type = node.get("type", "")

        # Skip UI-only nodes
        if node_type in UI_ONLY_TYPES:
            continue
        # Skip subgraph reference nodes (UUID types)
        if len(node_type) > 30 and "-" in node_type:
            continue

        node_id = str(node.get("id"))
        node_inputs = node.get("inputs", [])
        widgets = node.get("widgets_values", [])

        api_inputs: dict[str, Any] = {}

        # 1. Map connection inputs (linked slots)
        for inp in node_inputs:
            link_id = inp.get("link")
            if link_id is not None and link_id in link_map:
                origin_id, origin_slot = link_map[link_id]
                api_inputs[inp["name"]] = [str(origin_id), origin_slot]

        # 2. Map widget values using spec if available
        if node_specs and node_type in node_specs:
            _map_widgets_from_spec(api_inputs, widgets, node_specs[node_type])
        else:
            # Fallback: use node's input list to identify connection vs widget slots
            _map_widgets_from_inputs(api_inputs, widgets, node_inputs)

        api[node_id] = {
            "class_type": node_type,
            "inputs": api_inputs,
        }

    return api


def _map_widgets_from_spec(
    api_inputs: dict, widgets: list, spec: dict
) -> None:
    """Map widgets_values to named inputs using the node spec.

    Processes required inputs first, then optional, matching the order
    that ComfyUI uses to populate widgets_values. Skips connection-type
    inputs and UI-only controls (control_after_generate, upload).
    """
    input_data = spec.get("input", {})
    required = input_data.get("required", {})
    optional = input_data.get("optional", {})

    widget_idx = 0
    # Process required then optional, in order
    for section in [required, optional]:
        for name, raw_spec in section.items():
            if name in api_inputs:
                # Already set by a connection
                continue
            if _is_widget_spec(raw_spec):
                if widget_idx < len(widgets):
                    # Skip UI-only controls — they consume a widget slot
                    # but shouldn't be in the API payload
                    if name in UI_ONLY_WIDGETS:
                        widget_idx += 1
                        continue
                    api_inputs[name] = widgets[widget_idx]
                    widget_idx += 1
            # Connection types don't consume widget values


def _map_widgets_from_inputs(
    api_inputs: dict, widgets: list, node_inputs: list[dict]
) -> None:
    """Fallback: map widgets using the node's input slot types as hints.

    Connection-type inputs (MODEL, CLIP, etc.) don't appear in widgets_values.
    Everything else is a widget, consumed in order. UI-only controls are stripped.

    WARNING: Without specs, widget-to-name mapping may be wrong for nodes with
    many widget inputs. Always prefer _map_widgets_from_spec when specs are available.
    """
    # Collect names of connection-type inputs (already mapped or typed as connections)
    connection_names = set()
    for inp in node_inputs:
        inp_type = inp.get("type", "")
        if inp_type in CONNECTION_TYPES:
            connection_names.add(inp["name"])

    # Widget names are inputs NOT in connection_names and NOT already in api_inputs
    widget_names = []
    for inp in node_inputs:
        name = inp.get("name", "")
        if name not in connection_names and name not in api_inputs:
            if name not in UI_ONLY_WIDGETS:
                widget_names.append(name)

    for i, name in enumerate(widget_names):
        if i < len(widgets):
            api_inputs[name] = widgets[i]


def _is_widget_spec(raw_spec: list | Any) -> bool:
    """Check if a raw MCP spec entry is a widget type."""
    if not isinstance(raw_spec, list) or len(raw_spec) == 0:
        return False
    type_info = raw_spec[0]
    if isinstance(type_info, list):  # COMBO
        return True
    if type_info in {"INT", "FLOAT", "STRING", "BOOLEAN"}:
        return True
    if type_info in CONNECTION_TYPES:
        return False
    return False
