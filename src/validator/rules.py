"""Individual rule check functions for all 12 guidelines."""

import json
from collections import Counter
from pathlib import Path
from typing import Generator

from src.validator.api_nodes import detect_api_nodes
from src.validator.models import Finding, Severity

_core_nodes: frozenset | None = None
_guidelines: dict | None = None

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _load_core_nodes() -> frozenset[str]:
    """Load core_nodes.json once, return frozenset of node names."""
    global _core_nodes
    if _core_nodes is None:
        with open(DATA_DIR / "core_nodes.json") as f:
            data = json.load(f)
        _core_nodes = frozenset(data["nodes"])
    return _core_nodes


def _load_guidelines() -> dict[str, dict]:
    """Load guidelines.json, return dict keyed by rule ID."""
    global _guidelines
    if _guidelines is None:
        with open(DATA_DIR / "guidelines.json") as f:
            data = json.load(f)
        _guidelines = {r["id"]: r for r in data["rules"]}
    return _guidelines


def iter_all_nodes(workflow: dict) -> Generator[dict, None, None]:
    """Yield every node dict from top-level and subgraphs."""
    for node in workflow.get("nodes", []):
        yield node
    for subgraph in workflow.get("definitions", {}).get("subgraphs", []):
        for node in subgraph.get("nodes", []):
            yield node


# -- Severity mapping from guidelines severity to Finding severity --
SEVERITY_MAP = {
    "required": Severity.error,
    "recommended": Severity.warning,
}


# -- Rule check functions --
# All have signature: (workflow: dict) -> list[Finding]


def check_core_node_preference(workflow: dict) -> list[Finding]:
    """Flag custom (non-core) nodes with warning severity."""
    from src.validator.api_nodes import load_api_node_data

    core = _load_core_nodes()
    # Build set of known API node types (handled separately by detect_api_nodes)
    api_data = load_api_node_data()
    api_patterns = [e.get("class_type_pattern", "") for e in api_data.get("api_nodes", [])]
    api_known = set()
    for entry in api_data.get("api_nodes", []):
        api_known.update(entry.get("known_nodes", []))

    findings = []
    for node in iter_all_nodes(workflow):
        node_type = node.get("type", "")
        node_id = node.get("id")
        # Skip UUID-style subgraph references
        if len(node_type) > 30 and "-" in node_type:
            continue
        # Skip known API nodes (handled by detect_api_nodes)
        if node_type in api_known or any(p and p in node_type for p in api_patterns):
            continue
        if node_type and node_type not in core:
            findings.append(
                Finding(
                    rule_id="core_node_preference",
                    severity=Severity.warning,
                    message=f"Custom node '{node_type}' (node {node_id}) - not a core node",
                    node_id=node_id,
                    node_type=node_type,
                    suggestion="Consider if a core ComfyUI node can achieve the same result",
                )
            )
    return findings


def check_no_set_get_nodes(workflow: dict) -> list[Finding]:
    """Flag SetNode/GetNode/Set/Get with error severity."""
    banned = {"SetNode", "GetNode", "Set", "Get"}
    findings = []
    for node in iter_all_nodes(workflow):
        node_type = node.get("type", "")
        node_id = node.get("id")
        if node_type in banned:
            findings.append(
                Finding(
                    rule_id="no_set_get_nodes",
                    severity=Severity.error,
                    message=f"Set/Get node '{node_type}' (node {node_id}) is not allowed in templates",
                    node_id=node_id,
                    node_type=node_type,
                    suggestion="Remove Set/Get nodes and use direct connections instead",
                )
            )
    return findings


def check_note_color_black(workflow: dict) -> list[Finding]:
    """Flag Note nodes with non-dark background as error."""
    note_types = {"Note", "NoteNode"}
    findings = []
    for node in iter_all_nodes(workflow):
        node_type = node.get("type", "")
        node_id = node.get("id")
        if node_type not in note_types:
            continue
        bgcolor = node.get("bgcolor", "")
        color = node.get("color", "")
        # Check if color values are present
        if not bgcolor and not color:
            findings.append(
                Finding(
                    rule_id="note_color_black",
                    severity=Severity.info,
                    message=f"Note node (node {node_id}) has no color set",
                    node_id=node_id,
                    node_type=node_type,
                    suggestion="Set Note node background to black (#000000)",
                )
            )
            continue
        # Check if dark (starts with #0 or is #000000)
        check_color = bgcolor or color
        is_dark = check_color.lower().startswith("#0") or check_color.lower() == "#000000"
        if not is_dark:
            findings.append(
                Finding(
                    rule_id="note_color_black",
                    severity=Severity.error,
                    message=f"Note node (node {node_id}) has non-black background '{check_color}'",
                    node_id=node_id,
                    node_type=node_type,
                    suggestion="Set Note node background to black to distinguish from yellow API nodes",
                )
            )
    return findings


def check_unique_subgraph_names(workflow: dict) -> list[Finding]:
    """Flag duplicate subgraph names as error."""
    subgraphs = workflow.get("definitions", {}).get("subgraphs", [])
    names = [sg.get("name", "") for sg in subgraphs if sg.get("name")]
    counts = Counter(names)
    findings = []
    for name, count in counts.items():
        if count > 1:
            findings.append(
                Finding(
                    rule_id="unique_subgraph_names",
                    severity=Severity.error,
                    message=f"Subgraph name '{name}' is used {count} times - names must be unique",
                    suggestion="Rename subgraphs to reflect their distinct purpose",
                )
            )
    return findings


def check_subgraph_rules(workflow: dict) -> list[Finding]:
    """Flag Preview*/Save* nodes inside subgraphs as error."""
    subgraphs = workflow.get("definitions", {}).get("subgraphs", [])
    findings = []
    for sg in subgraphs:
        sg_name = sg.get("name", sg.get("id", "unknown"))
        for node in sg.get("nodes", []):
            node_type = node.get("type", "")
            node_id = node.get("id")
            if node_type.startswith("Preview") or node_type.startswith("Save"):
                findings.append(
                    Finding(
                        rule_id="subgraph_rules",
                        severity=Severity.error,
                        message=f"'{node_type}' (node {node_id}) should not be inside subgraph '{sg_name}'",
                        node_id=node_id,
                        node_type=node_type,
                        suggestion="Move Preview/Save nodes outside of subgraphs",
                    )
                )
    return findings


def check_api_node_color_yellow(workflow: dict) -> list[Finding]:
    """For nodes matched by detect_api_nodes, check if color is set."""
    api_findings = detect_api_nodes(workflow)
    api_node_ids = {f.node_id for f in api_findings}
    findings = []
    for node in iter_all_nodes(workflow):
        if node.get("id") in api_node_ids:
            if not node.get("color"):
                findings.append(
                    Finding(
                        rule_id="api_node_color_yellow",
                        severity=Severity.info,
                        message=f"API node '{node.get('type', '')}' (node {node.get('id')}) has no color set",
                        node_id=node.get("id"),
                        node_type=node.get("type", ""),
                        suggestion="Set API node color to yellow for visual distinction",
                    )
                )
    return findings


def check_group_color_default(workflow: dict) -> list[Finding]:
    """Check groups for non-default colors."""
    groups = workflow.get("groups", [])
    findings = []
    for group in groups:
        color = group.get("color")
        if color is not None:
            findings.append(
                Finding(
                    rule_id="group_color_default",
                    severity=Severity.warning,
                    message=f"Group '{group.get('title', 'untitled')}' has custom color '{color}'",
                    suggestion="Use the default ComfyUI group color for light/dark mode readability",
                )
            )
    return findings


def check_cloud_compatible(workflow: dict) -> list[Finding]:
    """INFO reminder about cloud testing."""
    return [
        Finding(
            rule_id="cloud_compatible",
            severity=Severity.info,
            message="Workflow must be built and tested on Comfy Cloud before submission",
            suggestion="Build and test on cloud.comfy.org to verify compatibility",
        )
    ]


def check_thumbnail_specs(workflow: dict) -> list[Finding]:
    """INFO reminder about thumbnail requirements."""
    return [
        Finding(
            rule_id="thumbnail_specs",
            severity=Severity.info,
            message="Thumbnail must be 1:1 ratio, showing effect preview (not a screenshot)",
            suggestion="Use workflow output as thumbnail; video thumbnails should be 3-5s",
        )
    ]


def check_api_badge_position(workflow: dict) -> list[Finding]:
    """INFO reminder about top-left corner."""
    return [
        Finding(
            rule_id="api_badge_position",
            severity=Severity.info,
            message="Avoid placing key information in the top-left corner of thumbnails",
            suggestion="Provider badge will be overlaid in top-left for API node templates",
        )
    ]


def check_simplicity_readability(workflow: dict) -> list[Finding]:
    """INFO reminder about clarity and universality."""
    return [
        Finding(
            rule_id="simplicity_readability",
            severity=Severity.info,
            message="Workflow logic should be clear, easy to understand, and have universality",
            suggestion="Ensure the template is not limited to a single scenario",
        )
    ]


def check_naming_conventions(workflow: dict) -> list[Finding]:
    """INFO reminder about naming patterns."""
    return [
        Finding(
            rule_id="naming_conventions",
            severity=Severity.info,
            message="Follow existing naming patterns in the template library",
            suggestion="Ensure all required fields are filled when submitting",
        )
    ]


# -- Rule registry: maps rule ID to check function --
RULE_REGISTRY: dict[str, callable] = {
    "core_node_preference": check_core_node_preference,
    "no_set_get_nodes": check_no_set_get_nodes,
    "cloud_compatible": check_cloud_compatible,
    "thumbnail_specs": check_thumbnail_specs,
    "api_badge_position": check_api_badge_position,
    "unique_subgraph_names": check_unique_subgraph_names,
    "subgraph_rules": check_subgraph_rules,
    "note_color_black": check_note_color_black,
    "api_node_color_yellow": check_api_node_color_yellow,
    "group_color_default": check_group_color_default,
    "simplicity_readability": check_simplicity_readability,
    "naming_conventions": check_naming_conventions,
}
