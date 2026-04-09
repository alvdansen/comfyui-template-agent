# Impact Pack Face Detailer

> Status: Demo

Automatic face detection and re-generation at higher quality. Uses ltdrdata's ComfyUI Impact Pack with YOLO face detection and SAM segmentation to refine facial details after a base SD 1.5 generation. Includes before/after preview outputs.

## Agent Workflow

This template was built using the ComfyUI Template Agent skill pipeline:

1. **Discover** (`/comfy-discover`) -- Found ComfyUI-Impact-Pack trending (2.37M+ downloads, ltdrdata)
2. **Audit** (`/comfy-template-audit`) -- No focused FaceDetailer template; Impact Pack has 200+ nodes but no template showcasing the face detailing pipeline
3. **Compose** (`/comfy-compose`) -- Built 11-node fan-out pipeline: CheckpointLoader -> KSampler -> FaceDetailer (with UltralyticsDetectorProvider + SAMLoader) -> SaveImage
4. **Validate** (`/comfy-validate`) -- Passed with note: requires both Impact Pack and Impact Subpack
5. **Document** (`/comfy-document`) -- Generated index.json (media type: image, 2 custom nodes, 2 models) and submission markdown

## What Was Built

- **Workflow:** `workflow.json` -- 11-node face detection and detailing pipeline
- **Node packs:** [comfyui-impact-pack](https://registry.comfy.org/nodes/comfyui-impact-pack) (2.37M+ downloads) + [comfyui-impact-subpack](https://registry.comfy.org/nodes/comfyui-impact-subpack)
- **Models:** sam_vit_b_01ec64.pth (~375 MB), face_yolov8m.pt (~50 MB), plus a base SD 1.5 checkpoint

## Outputs

| File | Purpose |
|------|---------|
| `workflow.json` | 11-node face detection and detailing pipeline |
| `index.json` | Template registry metadata |
| `submission.md` | Submission documentation |
| `build.py` | Reproducible workflow builder |

## Notes

Requires TWO custom node packs (Impact Pack + Impact Subpack).
YOLO face detection model (face_yolov8m.pt) is not auto-downloaded -- must be placed manually in `models/ultralytics/bbox/` or installed via ComfyUI-Manager.
The .pt model format may trigger safety warnings in newer PyTorch versions.
