---
name: comfy-document
description: "When the user has a finished workflow and needs submission documentation -- index.json metadata, Notion markdown, or thumbnail specs"
---

# Submission Documentation

Generate submission-ready documentation for ComfyUI workflow templates. Auto-extracts metadata from workflow JSON.

## Commands

```bash
# Generate both index.json and Notion markdown
python -m src.document.generate --file workflow.json --name my-template

# Index entry only (raw JSON)
python -m src.document.generate --file workflow.json --name my-template --output index --json

# Notion markdown with workflow link
python -m src.document.generate --file workflow.json --name my-template --output notion --workflow-link "https://..."

# Full options
python -m src.document.generate --file workflow.json --name my-template \
  --title "My Template" --description "Does cool stuff" \
  --tags "flux,image,fast" --username "author" --vram 8 --size 12
```

| Flag | Required | Description |
|------|----------|-------------|
| `--file` | Yes | Path to workflow JSON |
| `--name` | Yes | Template name (e.g. `my-new-template`) |
| `--title` | No | Title override (auto-generated from name) |
| `--description` | No | Template description |
| `--tags` | No | Comma-separated tags |
| `--username` | No | Author name |
| `--vram` | No | VRAM estimate in GB |
| `--size` | No | Size estimate in GB |
| `--output` | No | `index`, `notion`, or `both` (default) |
| `--json` | No | Raw JSON output |

## Key Constraints

- Auto-extracts: models, custom nodes, IO spec, media type. Only ask user for title, description, tags.
- Format gating: rejects API-format JSON (must have `nodes` array, not string keys).
- Model detection uses `Load` substring in node type plus file extension heuristic -- may miss non-standard loaders.
- Subgraph IO extraction looks inside definitions but does not recurse nested subgraphs.
- Thumbnail reminder is always shown at the end.
