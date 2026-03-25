# Template Submission: MelBandRoFormer Audio Separation

## Workflow Details
- **Name:** melbandroformer-audio-separation
- **Media Type:** audio
- **Date:** 2026-03-25
- **Author:** kijai

## Description
Separate any audio track into vocals and instruments using MelBandRoFormer — a state-of-the-art music source separation model by kijai. Load an audio file, run separation, and save both stems as MP3.

## How It Works

1. Load **audio_1.mp3**
2. [Describe the processing pipeline]

## Node Dependencies

- **ComfyUI-MelBandRoFormer** (custom node)

## Models Required

- `MelBandRoformer_fp16.safetensors`

## Inputs
| Node | Type | Field | Description |
|------|------|-------|-------------|
| LoadAudio (node 1) | AUDIO | audio_1.mp3 | [Add description] |

## Outputs
None

## Tags
audio, stem separation, music, vocals, instruments, MelBandRoFormer

## Cloud Test

- **Job ID:** [Run workflow on Comfy Cloud and paste job ID]
- **Status:** [Pending]
- **Date:** [Date]

## Validation

- [Run `/comfy-validate` and paste results]

## Notes
Custom node: ComfyUI-MelBandRoFormer (https://github.com/kijai/ComfyUI-MelBandRoFormer). Install via ComfyUI Manager. Model file MelBandRoformer_fp16.safetensors should be placed in ComfyUI/models/audio_separation/ (or wherever the node expects it).

---
## Thumbnail Requirements

- Ratio: 1:1
- Video thumbnails: 3-5 seconds
- Use workflow output (effect preview), NOT screenshots
- Keep style consistent with existing templates
- Avoid key info in top-left corner (API badge goes there)
- Supported types: https://github.com/Comfy-Org/workflow_templates?tab=readme-ov-file#4--choose-thumbnail-type