"""Pydantic models for the composition engine."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


# ── Type Classification ─────────────────────────────────────────────────────

CONNECTION_TYPES = {
    "MODEL",
    "CLIP",
    "VAE",
    "CONDITIONING",
    "LATENT",
    "IMAGE",
    "MASK",
    "AUDIO",
    "NOISE",
    "SAMPLER",
    "SIGMAS",
    "GUIDER",
    "CONTROL_NET",
    "STYLE_MODEL",
    "GLIGEN",
    "UPSCALE_MODEL",
    "TAESD",
}

WIDGET_TYPES = {"INT", "FLOAT", "STRING", "BOOLEAN"}


def is_widget_input(input_spec_raw: list) -> bool:
    """Determine if a raw MCP input spec creates a widget or is connection-only.

    Args:
        input_spec_raw: Raw input spec from MCP, e.g. ["INT", {"default": 0}]
                        or [["euler", "euler_a"]] for COMBO.

    Returns:
        True if the input is a widget (appears in widgets_values),
        False if it's a connection-only input.
    """
    if not isinstance(input_spec_raw, list) or len(input_spec_raw) == 0:
        return False
    type_info = input_spec_raw[0]
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


# ── Input / Output Specs ────────────────────────────────────────────────────


class InputSpec(BaseModel):
    """Single input specification parsed from MCP node info."""

    name: str
    type: str
    default: Any = None
    min: float | None = None
    max: float | None = None
    step: float | None = None
    combo_options: list[str] | None = None
    is_widget: bool = True


class OutputSpec(BaseModel):
    """Single output specification."""

    name: str
    type: str


# ── Node Spec ───────────────────────────────────────────────────────────────


class NodeSpec(BaseModel):
    """Parsed node specification from MCP get_node_info."""

    name: str
    display_name: str = ""
    category: str = ""
    inputs_required: dict[str, InputSpec] = {}
    inputs_optional: dict[str, InputSpec] = {}
    outputs: list[OutputSpec] = []
    is_output_node: bool = False


# ── Graph Node / Link ───────────────────────────────────────────────────────


class GraphNode(BaseModel):
    """A node in the workflow graph with all required structural fields."""

    id: int
    type: str
    pos: list[float]
    size: list[float] = [315, 170]
    flags: dict = {}
    order: int = 0
    mode: int = 0
    inputs: list[dict] = []
    outputs: list[dict] = []
    properties: dict = {}
    widgets_values: list = []
    title: str = ""
    color: str = ""
    bgcolor: str = ""


class GraphLink(BaseModel):
    """A connection between two nodes in the workflow graph."""

    link_id: int
    origin_node_id: int
    origin_slot: int
    target_node_id: int
    target_slot: int
    type: str

    def to_array(self) -> list:
        """Convert to the array format used in workflow JSON."""
        return [
            self.link_id,
            self.origin_node_id,
            self.origin_slot,
            self.target_node_id,
            self.target_slot,
            self.type,
        ]


# ── Parsing Helpers ─────────────────────────────────────────────────────────


def _parse_input(name: str, raw: list) -> InputSpec:
    """Parse a single raw input spec into an InputSpec model."""
    if not isinstance(raw, list) or len(raw) == 0:
        return InputSpec(name=name, type="UNKNOWN", is_widget=False)

    type_info = raw[0]
    constraints = raw[1] if len(raw) > 1 and isinstance(raw[1], dict) else {}

    # COMBO type: first element is a list of options
    if isinstance(type_info, list):
        return InputSpec(
            name=name,
            type="COMBO",
            combo_options=type_info,
            default=type_info[0] if type_info else None,
            is_widget=True,
        )

    # Standard type
    is_widget = type_info in WIDGET_TYPES
    is_connection = type_info in CONNECTION_TYPES

    return InputSpec(
        name=name,
        type=type_info,
        default=constraints.get("default"),
        min=constraints.get("min"),
        max=constraints.get("max"),
        step=constraints.get("step"),
        combo_options=None,
        is_widget=is_widget and not is_connection,
    )


def parse_node_spec(name: str, raw_info: dict) -> NodeSpec:
    """Convert MCP get_node_info response dict into a NodeSpec model.

    Args:
        name: Node type name (e.g. "KSampler").
        raw_info: Raw dict from MCP get_node_info response.

    Returns:
        Parsed NodeSpec with classified inputs and outputs.
    """
    input_data = raw_info.get("input", {})
    required_raw = input_data.get("required", {})
    optional_raw = input_data.get("optional", {})

    inputs_required = {k: _parse_input(k, v) for k, v in required_raw.items()}
    inputs_optional = {k: _parse_input(k, v) for k, v in optional_raw.items()}

    output_types = raw_info.get("output", [])
    output_names = raw_info.get("output_name", [])
    outputs = []
    for i, otype in enumerate(output_types):
        oname = output_names[i] if i < len(output_names) else otype
        outputs.append(OutputSpec(name=oname, type=otype))

    return NodeSpec(
        name=name,
        display_name=raw_info.get("display_name", ""),
        category=raw_info.get("category", ""),
        inputs_required=inputs_required,
        inputs_optional=inputs_optional,
        outputs=outputs,
        is_output_node=raw_info.get("output_node", False),
    )
