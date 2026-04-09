"""CLI entry point for documentation generation."""

import argparse
import json
import sys

from src.document.metadata import generate_index_entry, format_index_entry
from src.document.notion import generate_notion_markdown


def main() -> None:
    """CLI entry point for generating template submission documentation."""
    parser = argparse.ArgumentParser(
        description="Generate submission-ready documentation for ComfyUI workflow templates"
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to workflow JSON file",
    )
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Template name (e.g. 'my-new-template')",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="",
        help="Title override (auto-generated from name if omitted)",
    )
    parser.add_argument(
        "--description",
        type=str,
        default="",
        help="Template description",
    )
    parser.add_argument(
        "--tags",
        type=str,
        default="",
        help="Comma-separated tags",
    )
    parser.add_argument(
        "--username",
        type=str,
        default="",
        help="Author name",
    )
    parser.add_argument(
        "--vram",
        type=int,
        default=0,
        help="VRAM estimate in GB",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=0,
        help="Size estimate in GB",
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["index", "notion", "both"],
        default="both",
        help="Output mode (default: both)",
    )
    parser.add_argument(
        "--workflow-link",
        type=str,
        default="",
        help="Workflow link for Notion output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Raw JSON output (index entry only)",
    )

    args = parser.parse_args()

    # Load workflow JSON
    try:
        with open(args.file, encoding="utf-8") as f:
            workflow = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse tags
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None

    # Generate index entry
    try:
        entry = generate_index_entry(
            workflow,
            name=args.name,
            title=args.title,
            description=args.description,
            tags=tags,
            username=args.username,
            vram=args.vram,
            size=args.size,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Output based on mode
    if args.json_output:
        print(entry.model_dump_json(indent=2))
    else:
        if args.output in ("index", "both"):
            print(format_index_entry(entry))
        if args.output == "both":
            print("\n" + "=" * 60 + "\n")
        if args.output in ("notion", "both"):
            print(generate_notion_markdown(entry, workflow_link=args.workflow_link))


if __name__ == "__main__":
    main()
