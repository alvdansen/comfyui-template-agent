# Florence2 Vision AI

> Status: Demo

Multi-task vision AI using Florence2. Generates detailed image captions using kijai's ComfyUI-Florence2 pack with Microsoft's Florence-2-large-ft model. Demonstrates the `more_detailed_caption` task for rich image descriptions.

## Agent Workflow

This template was built using the ComfyUI Template Agent skill pipeline:

1. **Discover** (`/comfy-discover`) -- Found ComfyUI-Florence2 trending (1.25M+ downloads, kijai)
2. **Audit** (`/comfy-template-audit`) -- No existing template for Florence2 vision tasks; gap confirmed
3. **Compose** (`/comfy-compose`) -- Built 6-node pipeline: LoadImage -> ModelLoader -> Florence2Run -> PreviewImage
4. **Validate** (`/comfy-validate`) -- All submission guidelines passed (draft mode)
5. **Document** (`/comfy-document`) -- Generated index.json (media type: image, 1 custom node, 1 model) and submission markdown

## What Was Built

- **Workflow:** `workflow.json` -- 6-node vision AI captioning pipeline
- **Node pack:** [comfyui-florence2](https://registry.comfy.org/nodes/comfyui-florence2) (1.25M+ downloads)
- **Model:** microsoft/Florence-2-large-ft (~1.5 GB)

## Outputs

| File | Purpose |
|------|---------|
| `workflow.json` | 6-node vision AI captioning pipeline |
| `index.json` | Template registry metadata |
| `submission.md` | Submission documentation |
| `build.py` | Reproducible workflow builder |

## Notes

Model downloads ~1.5 GB on first run from HuggingFace Hub.
Supports 14+ vision tasks via the `task` parameter on Florence2Run, including captioning, OCR, object detection, and phrase grounding.
Switch the task widget in the Florence2Run node to explore different capabilities.
