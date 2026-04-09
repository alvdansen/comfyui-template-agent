---
name: comfy-document
description: "When the user has a finished workflow and needs submission documentation -- index.json metadata, Notion markdown, or thumbnail specs"
---

# Submission Documentation

Generate submission-ready documentation for ComfyUI workflow templates. Auto-extracts metadata from workflow JSON.

<important>
After generating documentation, **create a private Notion page** with the content using the Notion MCP tool.
Do NOT create public pages. Use `notion-create-pages` with no parent (creates a private workspace-level page).

```
notion-create-pages({
  pages: [{
    properties: { title: "Template: <template-name>" },
    icon: "🎨",
    content: "<generated notion markdown>"
  }]
})
```

Always ask the user before creating the Notion page. Never create public or shared pages without explicit permission.
</important>

## Capabilities

- Generate index.json template registry metadata from workflow JSON
- Generate Notion-ready submission markdown
- Auto-extract models, custom nodes, I/O spec, and media type
- Create private Notion pages via MCP (with user permission)
- Provide thumbnail format requirements reminder

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

## Example Session

**User:** Generate submission docs for my audio template
**Agent:** Runs `python -m src.document.generate --file workflow.json --name melbandroformer-audio-separation --title "MelBandRoFormer Audio Separation" --tags "audio,stem separation,vocals"`. Generated index.json entry (1 custom node, 1 model, media type: audio) and Notion markdown.
**User:** Create the Notion page
**Agent:** Creates private Notion page via MCP with the generated submission markdown. Page title: "Template: MelBandRoFormer Audio Separation". Link: [notion page URL].
**User:** What about the thumbnail?
**Agent:** Thumbnail reminder: 1:1 ratio, use workflow output (audio waveform visualization), avoid key info in top-left corner (API badge placement). Supported formats at the workflow_templates repo README.

## Key Constraints

- Auto-extracts: models, custom nodes, IO spec, media type. Only ask user for title, description, tags.
- Format gating: rejects API-format JSON (must have `nodes` array, not string keys).
- Model detection uses `Load` substring in node type plus file extension heuristic -- may miss non-standard loaders.
- Subgraph IO extraction looks inside definitions but does not recurse nested subgraphs.
- Thumbnail reminder is always shown at the end.
