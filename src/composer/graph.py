"""Type-safe ComfyUI workflow graph builder."""

from __future__ import annotations

from src.composer.models import GraphLink, GraphNode, NodeSpec
from src.composer.node_specs import NodeSpecCache
from src.shared.format_detector import detect_format


def check_type_compatibility(output_type: str, input_type: str) -> bool:
    """Check if an output type can connect to an input type.

    Rules:
    - Exact match: "IMAGE" -> "IMAGE" = OK
    - Wildcard: "*" accepts/provides anything
    - Otherwise: no implicit coercion
    """
    if output_type == "*" or input_type == "*":
        return True
    return output_type == input_type


class WorkflowGraph:
    """Type-safe ComfyUI workflow graph builder.

    Constructs valid workflow JSON (nodes[] + links[] format, version 0.4)
    with type-checked connections, auto-populated widgets_values, and
    all required structural fields.
    """

    def __init__(self, specs: NodeSpecCache | None = None) -> None:
        self._nodes: dict[int, GraphNode] = {}
        self._links: list[GraphLink] = []
        self._specs: NodeSpecCache = specs or NodeSpecCache()
        self._next_node_id: int = 1
        self._next_link_id: int = 1
        self._groups: list[dict] = []
        self._definitions: dict = {"subgraphs": []}
        self._extra: dict = {}

    def add_node(
        self,
        node_type: str,
        title: str = "",
        pos: list[float] | None = None,
        widgets_values: list | None = None,
    ) -> int:
        """Add a node to the graph. Returns the new node ID.

        If a spec is available and widgets_values is None, auto-populates
        widgets_values from spec defaults in correct positional order.
        """
        node_id = self._next_node_id
        self._next_node_id += 1

        spec = self._specs.get(node_type)

        # Build inputs, outputs, and widgets_values from spec
        node_inputs: list[dict] = []
        node_outputs: list[dict] = []
        auto_widgets: list = []

        if spec is not None:
            # Process required inputs in order
            for input_name, input_spec in spec.inputs_required.items():
                if input_spec.is_widget:
                    auto_widgets.append(
                        _default_for_input(input_spec)
                    )
                else:
                    node_inputs.append(
                        {"name": input_name, "type": input_spec.type, "link": None}
                    )

            # Process optional inputs in order
            for input_name, input_spec in spec.inputs_optional.items():
                if input_spec.is_widget:
                    auto_widgets.append(
                        _default_for_input(input_spec)
                    )
                else:
                    node_inputs.append(
                        {"name": input_name, "type": input_spec.type, "link": None}
                    )

            # Build outputs
            for output_spec in spec.outputs:
                node_outputs.append(
                    {"name": output_spec.name, "type": output_spec.type, "links": []}
                )

        final_widgets = widgets_values if widgets_values is not None else auto_widgets

        node = GraphNode(
            id=node_id,
            type=node_type,
            pos=pos or [0, 0],
            size=[315, 170],
            flags={},
            order=0,
            mode=0,
            inputs=node_inputs,
            outputs=node_outputs,
            properties={"Node name for S&R": node_type},
            widgets_values=final_widgets,
            title=title,
        )

        self._nodes[node_id] = node
        return node_id

    def connect(
        self,
        src_node_id: int,
        src_output: int | str,
        tgt_node_id: int,
        tgt_input: int | str,
    ) -> int:
        """Connect two nodes. Returns the link ID.

        Validates type compatibility. Raises TypeError on mismatch.
        Raises KeyError if node not found. Raises IndexError if slot not found.
        """
        src_node = self._nodes[src_node_id]
        tgt_node = self._nodes[tgt_node_id]

        # Resolve source output slot
        src_slot = _resolve_output_slot(src_node, src_output)
        # Resolve target input slot
        tgt_slot = _resolve_input_slot(tgt_node, tgt_input)

        output_type = src_node.outputs[src_slot]["type"]
        input_type = tgt_node.inputs[tgt_slot]["type"]

        if not check_type_compatibility(output_type, input_type):
            raise TypeError(
                f"Cannot connect {output_type} to {input_type}"
            )

        link_id = self._next_link_id
        self._next_link_id += 1

        link = GraphLink(
            link_id=link_id,
            origin_node_id=src_node_id,
            origin_slot=src_slot,
            target_node_id=tgt_node_id,
            target_slot=tgt_slot,
            type=output_type,
        )
        self._links.append(link)

        # Update node references
        src_node.outputs[src_slot]["links"].append(link_id)
        tgt_node.inputs[tgt_slot]["link"] = link_id

        return link_id

    def set_widget(self, node_id: int, widget_name: str, value: object) -> None:
        """Set a widget value by name.

        Validates COMBO values against allowed options.
        Raises ValueError if value is invalid.
        Raises KeyError if node not found or widget name not found.
        """
        node = self._nodes[node_id]
        spec = self._specs.get(node.type)

        if spec is None:
            raise KeyError(
                f"No spec available for node type '{node.type}' -- cannot resolve widget by name"
            )

        # Find widget index by iterating inputs in order, counting only widgets
        widget_idx = 0
        target_spec = None
        found = False

        for input_name, input_spec in spec.inputs_required.items():
            if input_spec.is_widget:
                if input_name == widget_name:
                    target_spec = input_spec
                    found = True
                    break
                widget_idx += 1

        if not found:
            for input_name, input_spec in spec.inputs_optional.items():
                if input_spec.is_widget:
                    if input_name == widget_name:
                        target_spec = input_spec
                        found = True
                        break
                    widget_idx += 1

        if not found:
            raise KeyError(f"Widget '{widget_name}' not found in node type '{node.type}'")

        # Validate COMBO options
        if target_spec.combo_options is not None and value not in target_spec.combo_options:
            raise ValueError(
                f"'{value}' is not a valid option for '{widget_name}'. "
                f"Valid options: {target_spec.combo_options}"
            )

        # Validate numeric range
        if target_spec.min is not None and isinstance(value, (int, float)):
            if value < target_spec.min:
                raise ValueError(
                    f"Value {value} is below minimum {target_spec.min} for '{widget_name}'"
                )
        if target_spec.max is not None and isinstance(value, (int, float)):
            if value > target_spec.max:
                raise ValueError(
                    f"Value {value} is above maximum {target_spec.max} for '{widget_name}'"
                )

        node.widgets_values[widget_idx] = value

    def remove_node(self, node_id: int) -> None:
        """Remove a node and all links connected to it.

        Cleans up link references in remaining nodes.
        """
        # Find and remove all links involving this node
        links_to_remove = [
            link for link in self._links
            if link.origin_node_id == node_id or link.target_node_id == node_id
        ]

        for link in links_to_remove:
            # Clean up references in other nodes
            if link.origin_node_id != node_id and link.origin_node_id in self._nodes:
                src_node = self._nodes[link.origin_node_id]
                out = src_node.outputs[link.origin_slot]
                if link.link_id in out["links"]:
                    out["links"].remove(link.link_id)

            if link.target_node_id != node_id and link.target_node_id in self._nodes:
                tgt_node = self._nodes[link.target_node_id]
                inp = tgt_node.inputs[link.target_slot]
                if inp["link"] == link.link_id:
                    inp["link"] = None

            self._links.remove(link)

        del self._nodes[node_id]

    def serialize(self) -> dict:
        """Export as workflow format JSON dict.

        Always outputs workflow format with nodes[], links[], version 0.4.
        Asserts format detection passes as a safety gate.
        """
        node_ids = list(self._nodes.keys())
        link_ids = [link.link_id for link in self._links]

        nodes_list = []
        for node in self._nodes.values():
            node_dict = node.model_dump(exclude_none=True)
            # Remove empty optional fields for cleaner output
            if not node_dict.get("title"):
                node_dict.pop("title", None)
            if not node_dict.get("color"):
                node_dict.pop("color", None)
            if not node_dict.get("bgcolor"):
                node_dict.pop("bgcolor", None)
            nodes_list.append(node_dict)

        links_list = [link.to_array() for link in self._links]

        result = {
            "last_node_id": max(node_ids) if node_ids else 0,
            "last_link_id": max(link_ids) if link_ids else 0,
            "nodes": nodes_list,
            "links": links_list,
            "groups": self._groups,
            "config": {},
            "extra": self._extra,
            "version": 0.4,
        }

        if self._definitions["subgraphs"]:
            result["definitions"] = self._definitions

        assert detect_format(result) == "workflow", (
            "Serialized output failed format detection -- expected 'workflow'"
        )

        return result


# ── Helpers ─────────────────────────────────────────────────────────────────


def _default_for_input(input_spec) -> object:
    """Return the default value for a widget input spec."""
    if input_spec.default is not None:
        return input_spec.default
    if input_spec.combo_options:
        return input_spec.combo_options[0] if input_spec.combo_options else ""
    type_defaults = {
        "INT": 0,
        "FLOAT": 0.0,
        "STRING": "",
        "BOOLEAN": False,
    }
    return type_defaults.get(input_spec.type, "")


def _resolve_output_slot(node: GraphNode, slot: int | str) -> int:
    """Resolve an output slot reference to an integer index."""
    if isinstance(slot, int):
        return slot
    for i, out in enumerate(node.outputs):
        if out["name"] == slot:
            return i
    raise IndexError(f"Output slot '{slot}' not found on node {node.id} ({node.type})")


def _resolve_input_slot(node: GraphNode, slot: int | str) -> int:
    """Resolve an input slot reference to an integer index."""
    if isinstance(slot, int):
        return slot
    for i, inp in enumerate(node.inputs):
        if inp["name"] == slot:
            return i
    raise IndexError(f"Input slot '{slot}' not found on node {node.id} ({node.type})")
