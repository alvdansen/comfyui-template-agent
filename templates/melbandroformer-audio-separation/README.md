# MelBandRoFormer Audio Separation

> Status: Submitted -- awaiting publish

Audio stem separation using MelBandRoFormer. Separates any audio track into vocals and instruments using kijai's ComfyUI-MelBandRoFormer pack with the MelBandRoformer fp16 model. The first audio-category template in the library.

## Agent Workflow

This template was built using the ComfyUI Template Agent skill pipeline:

1. **Discover** (`/comfy-discover`) -- Found ComfyUI-MelBandRoFormer trending (240K+ downloads, kijai)
2. **Audit** (`/comfy-template-audit`) -- No existing template for audio stem separation; gap confirmed
3. **Compose** (`/comfy-compose`) -- Built 5-node linear pipeline: LoadAudio -> ModelLoader -> Sampler -> SaveAudioMP3 (x2 for vocals/instruments)
4. **Validate** (`/comfy-validate`) -- All submission guidelines passed
5. **Document** (`/comfy-document`) -- Generated index.json (media type: audio, 1 custom node, 1 model) and Notion submission markdown

## What Was Built

- **Workflow:** `workflow.json` -- 5-node audio separation pipeline
- **Node pack:** [comfyui-melbandroformer](https://registry.comfy.org/nodes/comfyui-melbandroformer) (240K+ downloads)
- **Model:** MelBandRoformer_fp16.safetensors (456 MB)

## Outputs

| File | Purpose |
|------|---------|
| `workflow.json` | 5-node audio separation pipeline |
| `index.json` | Template registry metadata |
| `submission.md` | Submission documentation |
| `build.py` | Reproducible workflow builder |

## Notes

First audio-category template in the ComfyUI template library.
Model auto-downloads from HuggingFace on first run (~456 MB).
safetensors format is cloud-safe and will display download links in the template UI.
Cloud test pending.
