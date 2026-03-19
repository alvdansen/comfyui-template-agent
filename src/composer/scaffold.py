"""Scaffold workflows from templates or local files."""

from __future__ import annotations

import json

from src.composer.graph import WorkflowGraph
from src.composer.node_specs import NodeSpecCache
from src.shared.format_detector import detect_format
from src.templates.fetch import fetch_workflow_json


def scaffold_from_template(
    template_name: str, specs: NodeSpecCache | None = None
) -> WorkflowGraph:
    """Load a template workflow and return a modifiable WorkflowGraph.

    Fetches the workflow JSON via the template fetch system, then creates
    a deep-copy WorkflowGraph that can be freely modified without affecting
    the cached template data.

    Args:
        template_name: Template name as used in the template index.
        specs: Optional NodeSpecCache for type-aware operations.

    Returns:
        A new WorkflowGraph instance loaded from the template.

    Raises:
        ValueError: If the template is not found or could not be fetched.
    """
    workflow_data = fetch_workflow_json(template_name)
    if workflow_data is None:
        raise ValueError(
            f"Template '{template_name}' not found or could not be fetched"
        )
    return WorkflowGraph.from_json(workflow_data, specs=specs)


def scaffold_from_file(
    file_path: str, specs: NodeSpecCache | None = None
) -> WorkflowGraph:
    """Load a local workflow JSON file and return a modifiable WorkflowGraph.

    Validates that the file contains workflow format (nodes[] + links[]),
    not API format.

    Args:
        file_path: Path to a workflow JSON file.
        specs: Optional NodeSpecCache for type-aware operations.

    Returns:
        A new WorkflowGraph instance loaded from the file.

    Raises:
        ValueError: If the file is not workflow format.
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fmt = detect_format(data)
    if fmt != "workflow":
        raise ValueError(
            f"File is not workflow format (needs nodes[] + links[]). Got: {fmt}"
        )

    return WorkflowGraph.from_json(data, specs=specs)
