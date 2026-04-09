"""ComfyUI workflow composition engine.

Public API for building, scaffolding, and saving ComfyUI workflows.
"""

from src.composer.compose import save_workflow
from src.composer.graph import WorkflowGraph, check_type_compatibility
from src.composer.layout import auto_layout
from src.composer.models import (
    GraphLink,
    GraphNode,
    InputSpec,
    NodeSpec,
    OutputSpec,
    parse_node_spec,
)
from src.composer.node_specs import NodeSpecCache
from src.composer.scaffold import scaffold_from_file, scaffold_from_template

__all__ = [
    "WorkflowGraph",
    "check_type_compatibility",
    "NodeSpec",
    "InputSpec",
    "OutputSpec",
    "GraphNode",
    "GraphLink",
    "parse_node_spec",
    "NodeSpecCache",
    "scaffold_from_template",
    "scaffold_from_file",
    "auto_layout",
    "save_workflow",
]
