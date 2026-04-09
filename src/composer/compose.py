"""CLI entry point and composition save/report functions."""

import argparse
import json
import sys

from src.composer.graph import WorkflowGraph
from src.composer.layout import auto_layout
from src.composer.scaffold import scaffold_from_file, scaffold_from_template
from src.shared.format_detector import detect_format
from src.validator.engine import run_validation


def save_workflow(
    graph: WorkflowGraph,
    output_path: str,
    validate: bool = True,
    layout: bool = True,
) -> dict:
    """Save a composed workflow graph to a JSON file.

    Args:
        graph: The WorkflowGraph to save.
        output_path: File path to write the workflow JSON.
        validate: If True, run lenient validation on the output.
        layout: If True, run auto_layout before serializing.

    Returns:
        Dict with path, node_count, link_count, and validation summary.

    Raises:
        RuntimeError: If serialized output is not workflow format.
    """
    if layout:
        auto_layout(graph)

    result = graph.serialize()

    # Safety gate: output must be workflow format (COMP-04)
    fmt = detect_format(result)
    if fmt != "workflow":
        raise RuntimeError(
            f"Composed output is not workflow format (got '{fmt}'). "
            "This should never happen -- please report a bug."
        )

    # Run validation if requested
    validation_summary = None
    if validate:
        report = run_validation(result, mode="lenient")
        validation_summary = {
            "passed": report.passed,
            "score": report.score,
            "top_findings": [
                {"severity": f.severity.value, "message": f.message}
                for f in report.summary[:5]
            ],
        }

    # Write to disk
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return {
        "path": output_path,
        "node_count": len(result.get("nodes", [])),
        "link_count": len(result.get("links", [])),
        "validation": validation_summary,
    }


def format_composition_report(result: dict) -> str:
    """Format a save_workflow result as human-readable text.

    Args:
        result: Dict returned by save_workflow.

    Returns:
        Multi-line string with save path, counts, and validation summary.
    """
    lines = [
        f"Workflow saved to {result['path']}",
        f"Nodes: {result['node_count']}, Links: {result['link_count']}",
    ]

    validation = result.get("validation")
    if validation is not None:
        status = "PASS" if validation["passed"] else "FAIL"
        lines.append(f"Validation: [{status}] {validation['score']}")
        for finding in validation.get("top_findings", []):
            lines.append(f"  [{finding['severity'].upper()}] {finding['message']}")

    return "\n".join(lines)


def main() -> None:
    """CLI entry point for workflow composition."""
    parser = argparse.ArgumentParser(
        description="Compose ComfyUI workflow JSON from templates or local files"
    )
    parser.add_argument(
        "--scaffold",
        type=str,
        default=None,
        help="Template name to scaffold from",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Local workflow JSON file to scaffold from",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="workflow.json",
        help="Output file path (default: workflow.json)",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip validation on save",
    )
    parser.add_argument(
        "--no-layout",
        action="store_true",
        help="Skip auto-layout",
    )

    args = parser.parse_args()

    if args.scaffold:
        graph = scaffold_from_template(args.scaffold)
    elif args.file:
        graph = scaffold_from_file(args.file)
    else:
        print(
            "Use --scaffold or --file to start. "
            "For scratch composition, use the Claude Code skill."
        )
        sys.exit(0)

    result = save_workflow(
        graph,
        args.output,
        validate=not args.no_validate,
        layout=not args.no_layout,
    )
    print(format_composition_report(result))


if __name__ == "__main__":
    main()
