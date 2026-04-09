# GGUF Quantized FLUX.1-schnell Text to Image

> Status: Demo

Low-VRAM text-to-image using quantized FLUX.1-schnell. Uses city96's ComfyUI-GGUF pack to run Q4_K_S quantized UNET and Q8_0 T5-XXL encoder, cutting VRAM requirements significantly compared to full-precision FLUX models.

## Agent Workflow

This template was built using the ComfyUI Template Agent skill pipeline:

1. **Discover** (`/comfy-discover`) -- Found ComfyUI-GGUF trending (1.69M+ downloads, city96)
2. **Audit** (`/comfy-template-audit`) -- No existing GGUF template in the library; open issue #11819 requesting GGUF templates
3. **Compose** (`/comfy-compose`) -- Built 9-node pipeline: DualCLIPLoaderGGUF + UnetLoaderGGUF -> CLIPTextEncode -> KSampler -> VAEDecode -> SaveImage
4. **Validate** (`/comfy-validate`) -- Passed with note: .gguf models shown as "unsafe" in template UI (known limitation)
5. **Document** (`/comfy-document`) -- Generated index.json (media type: image, 1 custom node, 4 models) and submission markdown

## What Was Built

- **Workflow:** `workflow.json` -- 9-node quantized FLUX txt2img pipeline
- **Node pack:** [ComfyUI-GGUF](https://registry.comfy.org/nodes/ComfyUI-GGUF) (1.69M+ downloads)
- **Models:** flux1-schnell-Q4_K_S.gguf (6.78 GB), t5-v1_1-xxl-encoder-Q8_0.gguf (5.06 GB), clip_l.safetensors (246 MB), ae.safetensors (168 MB)

## Outputs

| File | Purpose |
|------|---------|
| `workflow.json` | 9-node quantized FLUX txt2img pipeline |
| `index.json` | Template registry metadata |
| `submission.md` | Submission documentation with manual model download URLs |
| `build.py` | Reproducible workflow builder |

## Notes

GGUF models display as "unsafe" in the template UI and won't auto-show download links.
Models must be downloaded manually -- see submission.md for download URLs and file placement paths.
Total model download is ~12 GB.
Addresses open issue [#11819](https://github.com/Comfy-Org/ComfyUI/issues/11819) requesting GGUF templates.
