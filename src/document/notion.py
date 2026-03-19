"""Notion-friendly markdown generation for template submissions."""

import json
from pathlib import Path

from src.document.models import IndexEntry

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _load_thumbnail_specs() -> dict:
    """Load the thumbnail_specs rule from guidelines.json."""
    with open(DATA_DIR / "guidelines.json") as f:
        data = json.load(f)
    for rule in data["rules"]:
        if rule["id"] == "thumbnail_specs":
            return rule
    return {}


def thumbnail_reminder() -> str:
    """Return formatted thumbnail requirements text."""
    _load_thumbnail_specs()  # Validate data exists
    lines = [
        "## Thumbnail Requirements",
        "",
        "- Ratio: 1:1",
        "- Video thumbnails: 3-5 seconds",
        "- Use workflow output (effect preview), NOT screenshots",
        "- Keep style consistent with existing templates",
        "- Avoid key info in top-left corner (API badge goes there)",
        "- Supported types: https://github.com/Comfy-Org/workflow_templates?tab=readme-ov-file#4--choose-thumbnail-type",
    ]
    return "\n".join(lines)


def generate_notion_markdown(
    entry: IndexEntry,
    workflow_link: str = "",
    extra_notes: str = "",
) -> str:
    """Generate copy-pasteable Notion submission markdown from an IndexEntry."""
    sections = []

    # Header
    sections.append(f"# Template Submission: {entry.title}")
    sections.append("")

    # Workflow details
    sections.append("## Workflow Details")
    sections.append(f"- **Name:** {entry.name}")
    sections.append(f"- **Media Type:** {entry.mediaType}")
    sections.append(f"- **Date:** {entry.date}")
    sections.append(f"- **Author:** {entry.username}")
    if workflow_link:
        sections.append(f"- **Workflow Link:** {workflow_link}")
    sections.append("")

    # Models
    sections.append("## Models Required")
    if entry.models:
        for model in entry.models:
            sections.append(f"- {model}")
    else:
        sections.append("None (core nodes only)")
    sections.append("")

    # Custom nodes
    sections.append("## Custom Node Dependencies")
    if entry.requiresCustomNodes:
        for node in entry.requiresCustomNodes:
            sections.append(f"- {node}")
    else:
        sections.append("None")
    sections.append("")

    # IO
    sections.append("## Inputs & Outputs")
    input_types = ", ".join(item.nodeType for item in entry.io.inputs) or "None"
    output_types = ", ".join(item.nodeType for item in entry.io.outputs) or "None"
    sections.append(f"**Inputs:** {input_types}")
    sections.append(f"**Outputs:** {output_types}")
    sections.append("")

    # Tags
    sections.append("## Tags")
    sections.append(", ".join(entry.tags) if entry.tags else "None specified")
    sections.append("")

    # Description
    sections.append("## Description")
    sections.append(entry.description or "[Add description here]")
    sections.append("")

    # Extra notes
    if extra_notes:
        sections.append("## Notes")
        sections.append(extra_notes)
        sections.append("")

    # Thumbnail reminder
    sections.append("---")
    sections.append(thumbnail_reminder())

    return "\n".join(sections)


def format_notion_markdown(markdown: str) -> str:
    """Identity function for pattern consistency with other modules."""
    return markdown
