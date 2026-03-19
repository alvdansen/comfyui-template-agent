---
name: comfy-document
description: "Generate submission-ready documentation for ComfyUI workflow templates: index.json metadata, Notion markdown, IO extraction, and thumbnail reminders"
---

# Skill: comfy-document

Generate submission-ready documentation for ComfyUI workflow templates. Auto-extracts metadata from workflow JSON and produces index.json entries, Notion submission markdown, and thumbnail requirement reminders.

## When to Use

- User wants to generate submission docs for a workflow template
- User needs to create an index.json entry from a workflow file
- User wants to prepare a Notion submission form
- User wants to check IO specs (inputs/outputs) of a workflow
- User asks about thumbnail requirements

## Quick Start

```
"Generate docs for my workflow"
"Create index.json entry from workflow.json"
"What are the thumbnail requirements?"
"Prepare Notion submission for my-template"
"What models does this workflow use?"
```

## Workflow

1. **Load workflow JSON** from file or from a composition session.
2. **Auto-extract** from workflow: node types, models, custom nodes, IO spec, media type.
3. **Ask user for**: title, description, tags (these need human judgment).
4. **Generate index.json entry** with `generate_index_entry` -- auto-fills everything possible.
5. **Generate Notion markdown** with `generate_notion_markdown` -- copy-pasteable submission text.
6. **Show thumbnail_reminder** at the end -- always remind about format specs.
7. **Offer to save** index entry to file if needed.

## CLI Shortcut

```bash
# Generate both index.json and Notion markdown
python -m src.document.generate --file workflow.json --name my-template

# Index entry only as raw JSON
python -m src.document.generate --file workflow.json --name my-template --output index --json

# Notion markdown only with workflow link
python -m src.document.generate --file workflow.json --name my-template --output notion --workflow-link "https://..."

# Full options
python -m src.document.generate --file workflow.json --name my-template --title "My Template" --description "Does cool stuff" --tags "flux,image,fast" --username "author" --vram 8 --size 12
```

## Flags

| Flag | Required | Description |
|------|----------|-------------|
| `--file` | Yes | Path to workflow JSON file |
| `--name` | Yes | Template name (e.g. `my-new-template`) |
| `--title` | No | Title override (auto-generated from name if omitted) |
| `--description` | No | Template description |
| `--tags` | No | Comma-separated tags |
| `--username` | No | Author name |
| `--vram` | No | VRAM estimate in GB (default: 0) |
| `--size` | No | Size estimate in GB (default: 0) |
| `--output` | No | Output mode: `index`, `notion`, or `both` (default: `both`) |
| `--workflow-link` | No | Workflow link for Notion output |
| `--json` | No | Raw JSON output (index entry only) |

## Programmatic API

```python
from src.document import (
    generate_index_entry, extract_io_spec, format_index_entry,
    generate_notion_markdown, thumbnail_reminder,
    IndexEntry, IOSpec, IOItem,
)

# Generate index entry from workflow dict
entry = generate_index_entry(
    workflow,
    name="my-template",
    title="My Template",
    tags=["flux", "image"],
    username="author",
)

# Format as JSON
print(format_index_entry(entry))

# Generate Notion markdown
print(generate_notion_markdown(entry, workflow_link="https://..."))

# Just extract IO spec
io = extract_io_spec(workflow)
print(f"Inputs: {[i.nodeType for i in io.inputs]}")
print(f"Outputs: {[o.nodeType for o in io.outputs]}")

# Show thumbnail requirements
print(thumbnail_reminder())
```

## Key Behaviors

- **Auto-detect everything possible**: models, custom nodes, IO spec, media type are all extracted from the workflow JSON automatically.
- **Ask for creative fields only**: title, description, and tags require human judgment -- prompt the user for these.
- **Thumbnail reminder always shown**: Every documentation generation ends with the thumbnail requirements reminder.
- **Format gating**: Rejects API-format JSON (must be workflow format with `nodes` array).
- **Subgraph awareness**: IO extraction looks inside subgraph definitions too, not just top-level nodes.

## Key Files

- `src/document/models.py` -- IndexEntry, IOSpec, IOItem, NotionSubmission Pydantic models
- `src/document/metadata.py` -- generate_index_entry, extract_io_spec, format_index_entry
- `src/document/notion.py` -- generate_notion_markdown, thumbnail_reminder
- `src/document/generate.py` -- CLI entry point
- `tests/test_document.py` -- Tests for all documentation functions
