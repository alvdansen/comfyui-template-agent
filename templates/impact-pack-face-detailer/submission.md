# Template Submission: Impact Pack Face Detailer

## Workflow Details
- **Name:** impact-pack-face-detailer
- **Media Type:** image
- **Date:** 2026-03-25
- **Author:** comfy-template-agent

## Description
Automatically detects and re-generates faces at higher quality using ComfyUI Impact Pack. Runs a base SD 1.5 generation, then applies FaceDetailer with YOLO face detection and SAM segmentation to refine facial details with a lower denoise pass — before/after previews included.

## How It Works

1. [Describe the processing pipeline]
2. Output: 2 image files
   - `image_output`
   - `face_detailed`

## Node Dependencies

- **comfyui-impact-pack** (custom node)
- **comfyui-impact-subpack** (custom node)

## Models Required

- `sam_vit_b_01ec64.pth`
- `v1-5-pruned-emaonly.safetensors`

## Inputs
None

## Outputs
| Node | Prefix | Media | Description |
|------|--------|-------|-------------|
| PreviewImage (node 10) | image_output | image | [Add description] |
| SaveImage (node 11) | face_detailed | image | [Add description] |

## Tags
face, inpaint, enhancement, impact-pack, SD1.5, detailing

## Cloud Test

- **Job ID:** [Run workflow on Comfy Cloud and paste job ID]
- **Status:** [Pending]
- **Date:** [Date]

## Validation

- [Run `/comfy-validate` and paste results]

## Notes
FaceDetailer requires TWO custom node packs:
- comfyui-impact-pack (FaceDetailer, SAMLoader)
- comfyui-impact-subpack (UltralyticsDetectorProvider / YOLO)

Models required:
- Base checkpoint: v1-5-pruned-emaonly.safetensors
- YOLO detector: face_yolov8m.pt (place in models/ultralytics/bbox/)
- SAM: sam_vit_b_01ec64.pth (place in models/sams/)

---
## Thumbnail Requirements

- Ratio: 1:1
- Video thumbnails: 3-5 seconds
- Use workflow output (effect preview), NOT screenshots
- Keep style consistent with existing templates
- Avoid key info in top-left corner (API badge goes there)
- Supported types: https://github.com/Comfy-Org/workflow_templates?tab=readme-ov-file#4--choose-thumbnail-type