"""CLI entry point and report formatter for the validation engine."""

import argparse
import json
import sys

from src.validator.engine import run_validation
from src.validator.models import ValidationReport


def format_report(report: ValidationReport) -> str:
    """Format a ValidationReport as human-readable text.

    Lines:
    - Header: Validation Report [PASS|FAIL] (mode)
    - Score line
    - Per-rule results sorted by (passed ascending, rule_id)
    - Per-finding with severity and optional fix suggestion
    - Skipped rule count if any
    """
    status = "PASS" if report.passed else "FAIL"
    lines: list[str] = [
        f"Validation Report [{status}] ({report.mode} mode)",
        f"Score: {report.score}",
        "",
    ]

    # Sort results: failures first, then by rule_id
    sorted_results = sorted(report.results, key=lambda r: (r.passed, r.rule_id))

    for result in sorted_results:
        icon = "PASS" if result.passed else "FAIL"
        lines.append(f"  [{icon}] {result.rule_title} ({result.rule_id})")
        for finding in result.findings:
            lines.append(f"    [{finding.severity.value.upper()}] {finding.message}")
            if finding.suggestion:
                lines.append(f"      Fix: {finding.suggestion}")

    if report.rules_skipped > 0:
        lines.append(f"\n{report.rules_skipped} rule(s) skipped via --ignore")

    return "\n".join(lines)


def load_workflow(path: str) -> dict:
    """Load a workflow JSON file from disk.

    Args:
        path: Path to a .json workflow file.

    Returns:
        Parsed dict.

    Raises:
        FileNotFoundError: If file does not exist.
        json.JSONDecodeError: If file is not valid JSON.
    """
    with open(path) as f:
        return json.load(f)


def main() -> None:
    """CLI entry point for workflow validation."""
    parser = argparse.ArgumentParser(
        description="Validate ComfyUI workflow JSON files against template guidelines"
    )
    parser.add_argument(
        "--file", required=True, help="Path to workflow JSON file"
    )
    parser.add_argument(
        "--mode",
        default="strict",
        choices=["strict", "lenient"],
        help="Validation mode (default: strict)",
    )
    parser.add_argument(
        "--ignore",
        nargs="*",
        default=[],
        help="Rule IDs to skip",
    )

    args = parser.parse_args()

    workflow = load_workflow(args.file)
    report = run_validation(workflow, mode=args.mode, ignore=args.ignore)
    print(format_report(report))
    sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
