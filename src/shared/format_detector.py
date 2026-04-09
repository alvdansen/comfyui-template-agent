"""Detect whether JSON data is ComfyUI workflow format or API format."""


def detect_format(data: dict) -> str:
    """Detect whether JSON is workflow format or API format.

    Returns: 'workflow', 'api', or 'unknown'
    """
    # Workflow format: has 'nodes' array and usually 'links'
    if isinstance(data.get("nodes"), list):
        return "workflow"
    # API format: flat dict where values have 'class_type'
    if any(
        isinstance(v, dict) and "class_type" in v
        for v in data.values()
        if isinstance(v, dict)
    ):
        return "api"
    return "unknown"
