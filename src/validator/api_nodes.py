"""API node detection with provider and auth mapping."""

import json
from pathlib import Path
from typing import Any

from src.validator.models import Finding, Severity

_api_node_data: dict | None = None

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "api_nodes.json"


def load_api_node_data() -> dict:
    """Load api_nodes.json, caching at module level."""
    global _api_node_data
    if _api_node_data is None:
        with open(DATA_PATH) as f:
            _api_node_data = json.load(f)
    return _api_node_data


def detect_api_nodes(workflow: dict) -> list[Finding]:
    """Detect API nodes in a workflow by known list + pattern match.

    Returns list of Finding objects for each matched API node.
    """
    from src.validator.rules import iter_all_nodes

    data = load_api_node_data()
    api_entries = data.get("api_nodes", [])
    findings: list[Finding] = []

    # Build lookup: known_node -> entry
    known_lookup: dict[str, dict] = {}
    for entry in api_entries:
        for known in entry.get("known_nodes", []):
            known_lookup[known] = entry

    for node in iter_all_nodes(workflow):
        node_type = node.get("type", "")
        node_id = node.get("id")
        matched_entry = None

        # 1. Exact match against known_nodes
        if node_type in known_lookup:
            matched_entry = known_lookup[node_type]
        else:
            # 2. Substring match on class_type_pattern
            for entry in api_entries:
                pattern = entry.get("class_type_pattern", "")
                if pattern and pattern in node_type:
                    matched_entry = entry
                    break

        if matched_entry:
            provider = matched_entry["provider"]
            auth_type = matched_entry["auth_type"]
            findings.append(
                Finding(
                    rule_id="api_node_auth",
                    severity=Severity.warning,
                    message=f"API node '{node_type}' (node {node_id}) uses {provider}",
                    node_id=node_id,
                    node_type=node_type,
                    suggestion=(
                        f"API node using {provider} — auth is handled automatically "
                        f"by the MCP server (v0.2.0+). If jobs silently vanish, "
                        f"update your MCP server: npm install in comfyui-mcp-server dir."
                    ),
                )
            )

    # Detect LoadImage nodes that reference local files (cloud won't have them)
    for node in iter_all_nodes(workflow):
        node_type = node.get("type", "")
        if node_type == "LoadImage":
            image_name = None
            widgets = node.get("widgets_values", [])
            if widgets:
                image_name = widgets[0] if isinstance(widgets[0], str) else None
            findings.append(
                Finding(
                    rule_id="api_node_auth",
                    severity=Severity.warning,
                    message=f"LoadImage node {node.get('id')} references local file"
                    + (f" '{image_name}'" if image_name else ""),
                    node_id=node.get("id"),
                    node_type=node_type,
                    suggestion=(
                        f"Do you have '{image_name}' on your local machine? "
                        f"Check your ComfyUI input/ directory. "
                        f"For cloud: upload images first or use LoadImageFromUrl with a public URL."
                    ) if image_name else (
                        "Check your ComfyUI input/ directory for the referenced image. "
                        "For cloud: upload images first or use LoadImageFromUrl with a public URL."
                    ),
                )
            )

    return findings
