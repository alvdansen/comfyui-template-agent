# Template Submission: GGUF Quantized FLUX.1-schnell Text to Image

## Workflow Details
- **Name:** gguf-quantized-txt2img
- **Media Type:** image
- **Date:** 2026-03-25
- **Author:** city96

## Description
Text-to-image workflow using GGUF-quantized FLUX.1-schnell with ComfyUI-GGUF (city96). Runs Q4_K_S quantized UNET and Q8_0 T5-XXL encoder, significantly reducing VRAM requirements compared to full-precision models.

## How It Works

1. [Describe the processing pipeline]
2. Output: **gguf_flux** (image)

## Node Dependencies

- **ComfyUI-GGUF** (custom node)

## Models Required

- `ae.safetensors`
- `clip_l.safetensors`
- `flux1-schnell-Q4_K_S.gguf`
- `t5-v1_1-xxl-encoder-Q8_0.gguf`

## Inputs
None

## Outputs
| Node | Prefix | Media | Description |
|------|--------|-------|-------------|
| SaveImage (node 9) | gguf_flux | image | [Add description] |

## Tags
flux, gguf, quantized, txt2img, low-vram, text-to-image

## Cloud Test

- **Job ID:** [Run workflow on Comfy Cloud and paste job ID]
- **Status:** [Pending]
- **Date:** [Date]

## Validation

- [Run `/comfy-validate` and paste results]

## Notes
## GGUF Model Setup (Required — Manual Download)

> **Important:** `.gguf` files are blocked by the ComfyUI template safety policy and
> cannot be bundled in the template. You must download these model files manually before
> running this workflow.

### Models Required

| File | Size | Purpose | Download |
|------|------|---------|----------|
| `flux1-schnell-Q4_K_S.gguf` | ~6.4 GB | FLUX.1-schnell UNET (4-bit quantized) | [Hugging Face — city96/FLUX.1-schnell-gguf](https://huggingface.co/city96/FLUX.1-schnell-gguf) |
| `t5-v1_1-xxl-encoder-Q8_0.gguf` | ~8.6 GB | T5-XXL text encoder (8-bit quantized) | [Hugging Face — city96/t5-v1_1-xxl-encoder-gguf](https://huggingface.co/city96/t5-v1_1-xxl-encoder-gguf) |
| `clip_l.safetensors` | ~246 MB | CLIP-L text encoder | [Hugging Face — comfyanonymous/flux_text_encoders](https://huggingface.co/comfyanonymous/flux_text_encoders) |
| `ae.safetensors` | ~335 MB | FLUX VAE | [Hugging Face — black-forest-labs/FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell) |

### File Placement

After downloading, place files in your ComfyUI installation:

```
ComfyUI/
  models/
    unet/
      flux1-schnell-Q4_K_S.gguf          <- UNET goes here
    clip/
      clip_l.safetensors                  <- CLIP-L goes here
      t5-v1_1-xxl-encoder-Q8_0.gguf      <- T5-XXL goes here
    vae/
      ae.safetensors                      <- VAE goes here
```

### Custom Node Installation

Install **ComfyUI-GGUF** (city96) via ComfyUI Manager or manually:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/city96/ComfyUI-GGUF
cd ComfyUI-GGUF
pip install -r requirements.txt
```

Registry ID: `ComfyUI-GGUF`
GitHub: https://github.com/city96/ComfyUI-GGUF


---
## Thumbnail Requirements

- Ratio: 1:1
- Video thumbnails: 3-5 seconds
- Use workflow output (effect preview), NOT screenshots
- Keep style consistent with existing templates
- Avoid key info in top-left corner (API badge goes there)
- Supported types: https://github.com/Comfy-Org/workflow_templates?tab=readme-ov-file#4--choose-thumbnail-type