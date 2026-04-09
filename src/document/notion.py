"""Notion-friendly markdown generation for template submissions."""

import json
from pathlib import Path

from src.document.models import IndexEntry, IOItem

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


def _io_table(items: list[IOItem], kind: str) -> list[str]:
    """Generate a markdown table for IO items."""
    lines = []
    if kind == "input":
        lines.append("| Node | Type | Field | Description |")
        lines.append("|------|------|-------|-------------|")
        for item in items:
            field = item.fieldName or f"{item.mediaType}_input"
            lines.append(
                f"| {item.nodeType} (node {item.nodeId}) | {item.mediaType.upper()} "
                f"| {field} | [Add description] |"
            )
    else:
        lines.append("| Node | Prefix | Media | Description |")
        lines.append("|------|--------|-------|-------------|")
        for item in items:
            prefix = item.fieldName or f"{item.mediaType}_output"
            lines.append(
                f"| {item.nodeType} (node {item.nodeId}) | {prefix} "
                f"| {item.mediaType} | [Add description] |"
            )
    return lines


def _node_dependencies_section(entry: IndexEntry) -> list[str]:
    """Generate node dependencies section with custom vs core breakdown."""
    lines = ["## Node Dependencies", ""]
    if entry.requiresCustomNodes:
        for node in entry.requiresCustomNodes:
            lines.append(f"- **{node}** (custom node)")
    else:
        lines.append("All core nodes — no custom dependencies.")
    lines.append("")
    return lines


def _models_section(entry: IndexEntry) -> list[str]:
    """Generate models section distinguishing file-based vs API models."""
    lines = ["## Models Required", ""]
    if not entry.models:
        lines.append("None — no local models required.")
    else:
        api_models = [m for m in entry.models if m.endswith("(API)")]
        file_models = [m for m in entry.models if not m.endswith("(API)")]
        if file_models:
            for m in file_models:
                lines.append(f"- `{m}`")
        if api_models:
            for m in api_models:
                lines.append(f"- {m}")
    lines.append("")
    return lines


def _how_it_works_section(entry: IndexEntry) -> list[str]:
    """Generate a How It Works section from IO spec.

    Provides a numbered list showing the data flow from inputs to outputs.
    The caller can edit descriptions after generation.
    """
    lines = ["## How It Works", ""]
    step = 1

    # Inputs
    if entry.io.inputs:
        input_names = []
        for item in entry.io.inputs:
            name = item.fieldName or f"{item.mediaType} input"
            input_names.append(f"**{name}**")
        lines.append(f"{step}. Load {', '.join(input_names)}")
        step += 1

    # Processing (inferred from node counts)
    lines.append(f"{step}. [Describe the processing pipeline]")
    step += 1

    # Outputs
    if entry.io.outputs:
        output_count = len(entry.io.outputs)
        first_output = entry.io.outputs[0]
        media = first_output.mediaType
        if output_count == 1:
            name = first_output.fieldName or media
            lines.append(f"{step}. Output: **{name}** ({media})")
        else:
            lines.append(f"{step}. Output: {output_count} {media} files")
            for item in entry.io.outputs:
                name = item.fieldName or f"{media}_output"
                lines.append(f"   - `{name}`")

    lines.append("")
    return lines


def _cost_estimate_section(entry: IndexEntry) -> list[str]:
    """Generate cost estimate section for API-based workflows."""
    api_models = [m for m in entry.models if m.endswith("(API)")]
    if not api_models:
        return []
    lines = [
        "## Cost Estimate",
        "",
        "| Component | Est. Cost |",
        "|-----------|-----------|",
        "| [Fill in per-component costs] | $0.00 |",
        "| **Total per run** | **$0.00** |",
        "",
    ]
    return lines


def _cloud_test_section() -> list[str]:
    """Generate placeholder cloud test section."""
    return [
        "## Cloud Test",
        "",
        "- **Job ID:** [Run workflow on Comfy Cloud and paste job ID]",
        "- **Status:** [Pending]",
        "- **Date:** [Date]",
        "",
    ]


def _validation_section() -> list[str]:
    """Generate placeholder validation section."""
    return [
        "## Validation",
        "",
        "- [Run `/comfy-validate` and paste results]",
        "",
    ]


def generate_notion_markdown(
    entry: IndexEntry,
    workflow_link: str = "",
    extra_notes: str = "",
) -> str:
    """Generate copy-pasteable Notion submission markdown from an IndexEntry."""
    sections: list[str] = []

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

    # Description
    sections.append("## Description")
    sections.append(entry.description or "[Add description here]")
    sections.append("")

    # How It Works
    sections.extend(_how_it_works_section(entry))

    # Node Dependencies
    sections.extend(_node_dependencies_section(entry))

    # Models
    sections.extend(_models_section(entry))

    # Inputs
    sections.append("## Inputs")
    if entry.io.inputs:
        sections.extend(_io_table(entry.io.inputs, "input"))
    else:
        sections.append("None")
    sections.append("")

    # Outputs
    sections.append("## Outputs")
    if entry.io.outputs:
        sections.extend(_io_table(entry.io.outputs, "output"))
    else:
        sections.append("None")
    sections.append("")

    # Cost estimate (only for API workflows)
    sections.extend(_cost_estimate_section(entry))

    # Tags
    sections.append("## Tags")
    sections.append(", ".join(entry.tags) if entry.tags else "None specified")
    sections.append("")

    # Cloud test placeholder
    sections.extend(_cloud_test_section())

    # Validation placeholder
    sections.extend(_validation_section())

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
