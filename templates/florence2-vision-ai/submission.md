# Template Submission: Florence2 Vision AI

## Workflow Details
- **Name:** florence2-vision-ai
- **Media Type:** image
- **Date:** 2026-03-25
- **Author:** kijai

## Description
Demonstrates Florence2 multi-task vision AI using the ComfyUI-Florence2 node pack by kijai. Supports detailed image captioning, OCR, object detection, and grounding. This template uses the more_detailed_caption task to generate rich image descriptions.

## How It Works

1. Load **example**
2. [Describe the processing pipeline]
3. Output: **image** (image)

## Node Dependencies

- **comfyui-florence2** (custom node)

## Models Required

- `microsoft/Florence-2-large-ft`

## Inputs
| Node | Type | Field | Description |
|------|------|-------|-------------|
| LoadImage (node 1) | IMAGE | example | [Add description] |

## Outputs
| Node | Prefix | Media | Description |
|------|--------|-------|-------------|
| PreviewImage (node 4) | image_output | image | [Add description] |

## Tags
vision, captioning, florence2, image-to-text, AI, multi-task

## Cloud Test

- **Job ID:** [Run workflow on Comfy Cloud and paste job ID]
- **Status:** [Pending]
- **Date:** [Date]

## Validation

- [Run `/comfy-validate` and paste results]

## Notes
Florence2 is Microsoft's multi-task vision model. The DownloadAndLoadFlorence2Model node downloads the model from Hugging Face on first run. Supported tasks include: caption, detailed_caption, more_detailed_caption, OCR, object detection, dense region caption, and grounding. Switch the task widget in Florence2Run to explore different capabilities.

---
## Thumbnail Requirements

- Ratio: 1:1
- Video thumbnails: 3-5 seconds
- Use workflow output (effect preview), NOT screenshots
- Keep style consistent with existing templates
- Avoid key info in top-left corner (API badge goes there)
- Supported types: https://github.com/Comfy-Org/workflow_templates?tab=readme-ov-file#4--choose-thumbnail-type
