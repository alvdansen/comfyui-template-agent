"""Core metadata extraction from ComfyUI workflow JSON."""

import datetime
import json
import re
from pathlib import Path

from src.document.models import IndexEntry, IOItem, IOSpec
from src.shared.format_detector import detect_format
from src.templates.fetch import extract_node_types

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

_core_nodes: frozenset[str] | None = None

_UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)

# Node types that represent inputs
_INPUT_TYPES = {
    "LoadImage": "image",
    "LoadImageMask": "image",
    "LoadVideo": "video",
    "VHS_LoadVideo": "video",
    "LoadAudio": "audio",
}

# Node types that represent outputs
_OUTPUT_TYPES = {
    "SaveImage": "image",
    "PreviewImage": "image",
    "SaveAnimatedWEBP": "video",
    "VHS_VideoCombine": "video",
    "SaveAudio": "audio",
}

# Node types that use API models (model name in widgets_values)
_API_MODEL_NODES = {
    "GeminiImage2Node",
    "GeminiTextNode",
    "NanoBananaNode",
    "KlingVideoNode",
    "RunwayGen3Node",
    "LumaVideoNode",
    "IdeogramNode",
    "FluxProNode",
    "RecraftNode",
}


def _load_core_nodes() -> frozenset[str]:
    """Load core_nodes.json once, return frozenset of node names."""
    global _core_nodes
    if _core_nodes is None:
        with open(DATA_DIR / "core_nodes.json") as f:
            data = json.load(f)
        _core_nodes = frozenset(data["nodes"])
    return _core_nodes


def _extract_field_name(node: dict) -> str:
    """Extract a human-readable field name from a node's widgets_values.

    For LoadImage: first widget is the filename.
    For SaveImage/VHS_VideoCombine: first widget is the output prefix.
    """
    widgets = node.get("widgets_values")
    if not isinstance(widgets, list) or not widgets:
        return ""
    first = widgets[0]
    if isinstance(first, str) and first:
        # Strip file extension for input images
        name = first
        for ext in (".png", ".jpg", ".jpeg", ".webp", ".mp4", ".wav"):
            if name.endswith(ext):
                name = name[: -len(ext)]
                break
        return name
    return ""


def _extract_io_from_nodes(nodes: list[dict], inputs: list[IOItem], outputs: list[IOItem]) -> None:
    """Extract IO items from a list of node dicts, appending to inputs/outputs."""
    for node in nodes:
        node_type = node.get("type", "")
        node_id = node.get("id")
        if node_type in _INPUT_TYPES:
            inputs.append(
                IOItem(
                    nodeId=node_id,
                    nodeType=node_type,
                    fieldName=_extract_field_name(node),
                    mediaType=_INPUT_TYPES[node_type],
                )
            )
        elif node_type in _OUTPUT_TYPES:
            outputs.append(
                IOItem(
                    nodeId=node_id,
                    nodeType=node_type,
                    fieldName=_extract_field_name(node),
                    mediaType=_OUTPUT_TYPES[node_type],
                )
            )


def extract_io_spec(workflow: dict) -> IOSpec:
    """Extract input/output specification from workflow JSON.

    Finds LoadImage/LoadVideo/SaveImage/VHS_VideoCombine etc. nodes
    in both top-level nodes and subgraph internals.
    """
    inputs: list[IOItem] = []
    outputs: list[IOItem] = []

    # Top-level nodes
    _extract_io_from_nodes(workflow.get("nodes", []), inputs, outputs)

    # Subgraph nodes
    for subgraph in workflow.get("definitions", {}).get("subgraphs", []):
        _extract_io_from_nodes(subgraph.get("nodes", []), inputs, outputs)

    return IOSpec(inputs=inputs, outputs=outputs)


def _detect_models(workflow: dict) -> list[str]:
    """Find model file paths and API model names from the workflow.

    Checks two sources:
    1. Loader nodes (type contains 'Load') with file-path-like widget values
    2. API model nodes with model name strings in widget values
    """
    model_extensions = (".safetensors", ".ckpt", ".pt", ".pth", ".bin")
    models: set[str] = set()

    def _check_nodes(nodes: list[dict]) -> None:
        for node in nodes:
            node_type = node.get("type", "")
            widgets = node.get("widgets_values")
            if not isinstance(widgets, list):
                continue

            # File-based models from loader nodes
            if "Load" in node_type:
                for val in widgets:
                    if not isinstance(val, str):
                        continue
                    if "/" in val or val.endswith(model_extensions):
                        models.add(val)

            # API models from known API node types
            if node_type in _API_MODEL_NODES:
                for val in widgets:
                    if not isinstance(val, str):
                        continue
                    # API model names: short, hyphenated, no spaces, no file ext
                    # e.g. "gemini-3-pro-image-preview", "kling-video-v2"
                    # Reject: prompts (have spaces), file paths, URLs, colors
                    if (
                        "-" in val
                        and " " not in val
                        and not val.endswith(model_extensions)
                        and "/" not in val
                        and len(val) > 5
                        and len(val) < 80
                        and not val.startswith(("#", "http"))
                    ):
                        models.add(f"{val} (API)")
                        break  # First matching string is the model name

    _check_nodes(workflow.get("nodes", []))
    for subgraph in workflow.get("definitions", {}).get("subgraphs", []):
        _check_nodes(subgraph.get("nodes", []))

    return sorted(models)


def _detect_media_type(workflow: dict) -> str:
    """Detect primary media type from output nodes.

    Checks for video output nodes first (higher priority), then image, then audio.
    """
    all_types: set[str] = set()

    for node in workflow.get("nodes", []):
        all_types.add(node.get("type", ""))
    for subgraph in workflow.get("definitions", {}).get("subgraphs", []):
        for node in subgraph.get("nodes", []):
            all_types.add(node.get("type", ""))

    # Video takes priority
    if all_types & {"VHS_VideoCombine", "SaveAnimatedWEBP"}:
        return "video"
    if all_types & {"SaveAudio"}:
        return "audio"
    if all_types & {"SaveImage", "PreviewImage"}:
        return "image"
    return "image"


def _detect_custom_nodes(workflow: dict) -> list[str]:
    """Detect non-core custom nodes used in the workflow.

    Uses extract_node_types for full enumeration, then filters against
    the core nodes list. UUID-pattern types (subgraph refs) are excluded.
    """
    all_types = extract_node_types(workflow)
    core = _load_core_nodes()
    custom = []
    for t in sorted(all_types):
        if t not in core and not _UUID_PATTERN.match(t):
            custom.append(t)
    return custom


def generate_index_entry(
    workflow: dict,
    name: str,
    title: str = "",
    description: str = "",
    tags: list[str] | None = None,
    username: str = "",
    vram: int = 0,
    size: int = 0,
) -> IndexEntry:
    """Generate a complete index.json entry from a workflow JSON.

    Auto-detects models, custom nodes, IO spec, and media type.
    Raises ValueError if the workflow is not in workflow format.
    """
    fmt = detect_format(workflow)
    if fmt != "workflow":
        raise ValueError(
            f"Expected workflow format, got '{fmt}'. "
            "Only ComfyUI workflow JSON (with 'nodes' array) is supported."
        )

    io = extract_io_spec(workflow)
    models = _detect_models(workflow)
    media_type = _detect_media_type(workflow)
    custom_nodes = _detect_custom_nodes(workflow)

    if not title:
        title = name.replace("-", " ").title()

    return IndexEntry(
        name=name,
        title=title,
        description=description,
        mediaType=media_type,
        tags=tags or [],
        models=models,
        requiresCustomNodes=custom_nodes,
        date=datetime.date.today().isoformat(),
        username=username,
        vram=vram,
        size=size,
        io=io,
    )


def format_index_entry(entry: IndexEntry) -> str:
    """Format an IndexEntry as pretty-printed JSON string."""
    return json.dumps(entry.model_dump(), indent=2)
