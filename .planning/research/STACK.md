# Technology Stack

**Project:** ComfyUI Template Agent v2.0 -- Template Batch (4 Trending Node Packs)
**Researched:** 2026-03-25
**Overall confidence:** HIGH (node class names, model paths verified against GitHub source + HuggingFace)

> This STACK.md covers what each of the 4 new templates requires: custom node packs, node class names, model files, model paths, Python dependencies, and cloud compatibility. The agent toolkit's own stack (Python, httpx, Pydantic, etc.) is unchanged from v1.0.

---

## Template 1: ComfyUI-Florence2 -- Vision AI

### Custom Node Pack

| Field | Value |
|-------|-------|
| Registry ID | `comfyui-florence2` |
| GitHub | `kijai/ComfyUI-Florence2` |
| Publisher | kijai |
| Downloads | ~1.25M |
| Python deps | `transformers>=4.39.0,!=4.50.*` (only declared dependency) |
| Implicit deps | `torch`, `torchvision`, `PIL` (provided by ComfyUI runtime) |

### Node Class Names (NODE_CLASS_MAPPINGS)

| class_type | Display Name | Purpose |
|------------|-------------|---------|
| `DownloadAndLoadFlorence2Model` | DownloadAndLoadFlorence2Model | Downloads model from HuggingFace Hub, loads into memory |
| `DownloadAndLoadFlorence2Lora` | DownloadAndLoadFlorence2Lora | Loads LoRA adapters for fine-tuned variants |
| `Florence2ModelLoader` | Florence2ModelLoader | Loads model from local `models/LLM/` directory |
| `Florence2Run` | Florence2Run | Executes vision tasks on input image |

### Models Required

**Primary model (use this for template):**

| Model | HuggingFace ID | Size | VRAM | Precision |
|-------|---------------|------|------|-----------|
| Florence-2-large-ft | `microsoft/Florence-2-large-ft` | ~1.5 GB | ~2-3 GB (fp16) | fp16 recommended |

**Why `large-ft`:** Fine-tuned variant has best task performance across all benchmarks. The `base` variant is smaller (~0.45B params) but noticeably worse at detection/segmentation. The `large` (non-ft) variant is pre-trained only. Use `large-ft` (0.77B params) as the default -- it is the community standard.

**Alternative models available in the dropdown (do NOT include in template):**
- `microsoft/Florence-2-base` / `Florence-2-base-ft` -- smaller, worse quality
- `HuggingFaceM4/Florence-2-DocVQA` -- specialized for documents only
- `thwri/CogFlorence-2.1-Large` / `CogFlorence-2.2-Large` -- community fine-tunes
- `gokaygokay/Florence-2-SD3-Captioner` / `Florence-2-Flux-Large` -- prompt generation specialists
- `MiaoshouAI/Florence-2-large-PromptGen-v2.0` -- caption-focused

**Model storage path:** `ComfyUI/models/LLM/` (auto-downloaded by `DownloadAndLoadFlorence2Model`)

### Supported Tasks (Florence2Run task dropdown)

| Task | Input | Output | Template Use Case |
|------|-------|--------|-------------------|
| `caption` | image | text | Basic captioning |
| `detailed_caption` | image | text | Detailed description |
| `more_detailed_caption` | image | text | Verbose description |
| `dense_region_caption` | image | bboxes + labels | Region-level captioning |
| `region_proposal` | image | bboxes | Object proposals |
| `referring_expression_segmentation` | image + text | segmentation mask | Text-guided segmentation |
| `caption_to_phrase_grounding` | image + text | bboxes + labels | Phrase grounding |
| `ocr` | image | text | Text recognition |
| `ocr_with_region` | image | quad_boxes + labels | Localized OCR |
| `docvqa` | image + text | text | Document Q&A |
| `prompt_gen_tags` | image | text | Tag generation |
| `prompt_gen_mixed_caption` | image | text | SD-style prompt |
| `prompt_gen_analyze` | image | text | Analysis |
| `prompt_gen_mixed_caption_plus` | image | text | Enhanced prompts |

### Template Recommendation

Build a **multi-task showcase** workflow: one `DownloadAndLoadFlorence2Model` node feeding multiple `Florence2Run` nodes with different tasks (`caption`, `dense_region_caption`, `ocr`, `referring_expression_segmentation`). This demonstrates Florence2's versatility in a single template. Confidence: HIGH.

### Cloud Compatibility

- **Pack in registry:** YES (`comfyui-florence2` on registry.comfy.org)
- **Model auto-download:** YES (HuggingFace Hub, triggered at runtime)
- **Model format:** safetensors (safe format, will display download links)
- **Risk:** Model downloads ~1.5 GB on first run. Cloud environments should handle this, but first-run latency is notable.

---

## Template 2: ComfyUI-GGUF -- Quantized FLUX txt2img

### Custom Node Pack

| Field | Value |
|-------|-------|
| Registry ID | `ComfyUI-GGUF` |
| GitHub | `city96/ComfyUI-GGUF` |
| Publisher | city96 |
| Downloads | ~1.69M |
| Stars | ~3.4K |
| Python deps | `gguf` (pip package) |

### Node Class Names (NODE_CLASS_MAPPINGS)

| class_type | TITLE | Purpose |
|------------|-------|---------|
| `UnetLoaderGGUF` | Unet Loader (GGUF) | Loads quantized UNET/diffusion model from GGUF file |
| `CLIPLoaderGGUF` | CLIPLoader (GGUF) | Loads single CLIP text encoder in GGUF format |
| `DualCLIPLoaderGGUF` | DualCLIPLoader (GGUF) | Loads two CLIP encoders (CLIP-L + T5-XXL for FLUX) |
| `TripleCLIPLoaderGGUF` | TripleCLIPLoader (GGUF) | Three CLIP encoders (SD3 use case) |
| `QuadrupleCLIPLoaderGGUF` | QuadrupleCLIPLoader (GGUF) | Four CLIP encoders |
| `UnetLoaderGGUFAdvanced` | Unet Loader (GGUF/Advanced) | Advanced loader with dtype override options |

### Model Folder Paths

| Node | Primary Folder | Fallback Folders |
|------|---------------|-----------------|
| `UnetLoaderGGUF` / `UnetLoaderGGUFAdvanced` | `models/unet_gguf` | `models/diffusion_models`, `models/unet` |
| `CLIPLoaderGGUF` / `DualCLIPLoaderGGUF` / etc. | `models/clip_gguf` | `models/clip`, `models/text_encoders` |

### Models Required for FLUX.1-schnell Template

**Use FLUX.1-schnell (not dev) because:** Apache 2.0 license, free for commercial use, 4-step generation (faster), identical architecture. FLUX.1-dev has a non-commercial license which complicates template distribution.

**UNET (quantized):**

| Model | HuggingFace | Filename | Size | Path |
|-------|------------|----------|------|------|
| FLUX.1-schnell Q4_K_S | `city96/FLUX.1-schnell-gguf` | `flux1-schnell-Q4_K_S.gguf` | 6.78 GB | `models/unet_gguf/` |
| FLUX.1-schnell Q8_0 (alt) | `city96/FLUX.1-schnell-gguf` | `flux1-schnell-Q8_0.gguf` | 12.7 GB | `models/unet_gguf/` |

**Why Q4_K_S as default:** Best balance of quality and VRAM. Runs on 8 GB GPUs. Q8_0 is higher quality but needs 16+ GB. Template should default to Q4_K_S with a note about Q8_0 for better hardware.

**Text Encoders (CLIP-L + T5-XXL):**

| Model | HuggingFace | Filename | Size | Path |
|-------|------------|----------|------|------|
| CLIP-L | `comfyanonymous/flux_text_encoders` | `clip_l.safetensors` | ~246 MB | `models/clip/` |
| T5-XXL (GGUF Q8) | `city96/t5-v1_1-xxl-encoder-gguf` | `t5-v1_1-xxl-encoder-Q8_0.gguf` | 5.06 GB | `models/clip_gguf/` |

**Why T5 Q8_0:** The T5-XXL encoder is 9.5 GB at fp16. Q8_0 (5 GB) preserves quality while halving VRAM. Q5_K_M (3.4 GB) is acceptable; below Q5 quality degrades noticeably. T5 does not support imatrix quants, so use Q5_K_M or larger.

**VAE:**

| Model | HuggingFace | Filename | Size | Path |
|-------|------------|----------|------|------|
| FLUX VAE | `black-forest-labs/FLUX.1-schnell` | `ae.safetensors` | ~168 MB | `models/vae/` |

### Core Nodes Also Required (built into ComfyUI)

The GGUF nodes replace only the model loaders. The rest of the txt2img pipeline uses core nodes:

| Core Node | Purpose |
|-----------|---------|
| `KSampler` or `KSamplerAdvanced` | Sampling/denoising |
| `EmptyLatentImage` | Latent space initialization |
| `CLIPTextEncode` | Prompt encoding (uses CLIP output from GGUF loader) |
| `VAEDecode` | Latent-to-image decoding |
| `SaveImage` or `PreviewImage` | Output |

### Template Recommendation

Build a **FLUX.1-schnell txt2img** workflow: `UnetLoaderGGUF` + `DualCLIPLoaderGGUF` (CLIP-L safetensors + T5-XXL GGUF) + standard `KSampler` + `VAEDecode` pipeline. This showcases the GGUF value proposition: run FLUX on 8 GB VRAM. Confidence: HIGH.

### Cloud Compatibility -- CRITICAL WARNING

| Concern | Status | Impact |
|---------|--------|--------|
| GGUF format in templates | NOT in official templates yet | Open issue #11819 requesting GGUF templates |
| `.gguf` model safety display | Models shown as "unsafe" in template UI | Won't auto-show download links for GGUF files |
| Pack in registry | YES (`ComfyUI-GGUF` on registry.comfy.org) | Pack installs fine |
| Cloud model availability | UNKNOWN | GGUF models may not be pre-cached on Comfy Cloud |

**Mitigation:** The template workflow JSON is valid regardless. The model download URLs can still be specified in the `models` metadata field. Users downloading the template will need to manually place GGUF files. This is a known ecosystem gap, not a blocker for template creation, but worth documenting clearly in the submission.

---

## Template 3: ComfyUI Impact Pack -- Face Detection + Auto-Detailing

### Custom Node Packs (TWO packs required)

**Pack 1: Impact Pack**

| Field | Value |
|-------|-------|
| Registry ID | `comfyui-impact-pack` |
| GitHub | `ltdrdata/ComfyUI-Impact-Pack` |
| Publisher | ltdrdata |
| Downloads | ~2.37M |
| Stars | ~3K |
| Python deps | `segment-anything`, `scikit-image`, `piexif`, `transformers`, `opencv-python-headless`, `GitPython`, `scipy>=1.11.4`, `numpy`, `dill`, `matplotlib`, `sam2` (from GitHub) |

**Pack 2: Impact Subpack (REQUIRED for face detection)**

| Field | Value |
|-------|-------|
| Registry ID | `comfyui-impact-subpack` |
| GitHub | `ltdrdata/ComfyUI-Impact-Subpack` |
| Publisher | ltdrdata |
| Python deps | `ultralytics` (YOLO framework) |

**Why Subpack is required:** As of Impact Pack v8.0, `UltralyticsDetectorProvider` was moved out of the main pack into the Subpack. FaceDetailer requires a BBOX_DETECTOR, which comes from UltralyticsDetectorProvider. Without the Subpack, FaceDetailer has no face detection input. This is a mandatory dependency.

### Node Class Names for FaceDetailer Workflow

| class_type | Source Pack | Purpose |
|------------|------------|---------|
| `FaceDetailer` | Impact Pack | All-in-one face detect + inpaint + enhance |
| `FaceDetailerPipe` | Impact Pack | Piped variant (alternative) |
| `SAMLoader` | Impact Pack | Loads SAM model for segmentation refinement |
| `UltralyticsDetectorProvider` | **Impact Subpack** | Loads YOLO face detection model, provides BBOX_DETECTOR |
| `BboxDetectorSEGS` | Impact Pack | BBOX to segments conversion |
| `DetailerForEach` | Impact Pack | Per-segment detailing (alternative to FaceDetailer) |
| `SAMDetectorCombined` | Impact Pack | SAM-based detection |
| `ImpactSimpleDetectorSEGS` | Impact Pack | Simplified detection |

### Models Required

**Face Detection Model (YOLO):**

| Model | Source | Filename | Size | Path |
|-------|--------|----------|------|------|
| Face YOLOv8m | HuggingFace (Bingsu/adetailer) | `face_yolov8m.pt` | ~50 MB | `models/ultralytics/bbox/` |

**Segment Anything Model:**

| Model | Source | Filename | Size | Path |
|-------|--------|----------|------|------|
| SAM ViT-B | Facebook Research | `sam_vit_b_01ec64.pth` | ~375 MB | `models/sams/` |

Download URL: `https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth`

**Why ViT-B (not ViT-H or ViT-L):** ViT-B is the smallest SAM variant (375 MB vs 2.4 GB for ViT-H). For face refinement, ViT-B provides adequate mask quality. Templates should minimize model download burden. ViT-B is the Impact Pack default (auto-downloaded by install.py).

**Base Model (for inpainting/detailing KSampler):**

The FaceDetailer node includes an internal KSampler that re-generates detected face regions. This requires a standard checkpoint model. Use whatever base model the user already has. For the template, use a standard SD1.5 or SDXL checkpoint reference.

| Model | Filename | Size | Path | Note |
|-------|----------|------|------|------|
| SD 1.5 (example) | `v1-5-pruned-emaonly.safetensors` | ~4.2 GB | `models/checkpoints/` | Or any compatible checkpoint |

### Core Nodes Also Required

| Core Node | Purpose |
|-----------|---------|
| `CheckpointLoaderSimple` | Load base model for detailing |
| `CLIPTextEncode` | Positive/negative prompts for face re-generation |
| `LoadImage` | Input image |
| `SaveImage` / `PreviewImage` | Output |
| `VAEDecode` | If using non-FaceDetailer pipeline |

### Template Recommendation

Build a **FaceDetailer pipeline**: `LoadImage` -> image input to `FaceDetailer` node. The FaceDetailer takes: model (from `CheckpointLoaderSimple`), clip, vae, image, bbox_detector (from `UltralyticsDetectorProvider` with `face_yolov8m.pt`), sam_model_opt (from `SAMLoader` with `sam_vit_b_01ec64.pth`), and positive/negative conditioning. This is the canonical Impact Pack use case and the most-requested workflow. Confidence: HIGH.

### Cloud Compatibility

| Concern | Status | Impact |
|---------|--------|--------|
| Impact Pack in registry | YES | Installs via registry |
| Impact Subpack in registry | YES | Installs via registry |
| Two-pack dependency | Must declare BOTH in `requiresCustomNodes` | Easy to miss the Subpack |
| SAM model auto-download | YES (install.py auto-downloads to `models/sams/`) | Works on cloud |
| YOLO model | NOT auto-downloaded | Must be manually placed or downloaded via ComfyUI-Manager |
| `.pt` model format | PyTorch format, may trigger safety warnings in newer PyTorch | Impact Subpack has `model-whitelist.txt` for this |

---

## Template 4: ComfyUI-MelBandRoFormer -- Audio Stem Separation

### Custom Node Pack

| Field | Value |
|-------|-------|
| Registry ID | `comfyui-melbandroformer` |
| GitHub | `kijai/ComfyUI-MelBandRoFormer` |
| Publisher | kijai |
| Downloads | ~240K |
| Python deps | `rotary_embedding_torch`, `einops` |

### Node Class Names (NODE_CLASS_MAPPINGS)

| class_type | Display Name | Purpose |
|------------|-------------|---------|
| `MelBandRoFormerModelLoader` | Mel-Band RoFormer Model Loader | Loads separation model from `diffusion_models/` |
| `MelBandRoFormerSampler` | Mel-Band RoFormer Sampler | Runs separation, outputs vocals + instruments |

### Custom Types

| Type Name | Description |
|-----------|-------------|
| `MELROFORMERMODEL` | Model object passed from Loader to Sampler |
| `AUDIO` | Audio data (input and output) |

### Models Required

| Model | HuggingFace | Filename | Size | Path |
|-------|------------|----------|------|------|
| MelBandRoformer fp16 | `Kijai/MelBandRoFormer_comfy` | `MelBandRoformer_fp16.safetensors` | 456 MB | `models/diffusion_models/` |
| MelBandRoformer fp32 (alt) | `Kijai/MelBandRoFormer_comfy` | `MelBandRoformer_fp32.safetensors` | 913 MB | `models/diffusion_models/` |

**Why fp16:** Half the size, negligible quality difference for audio separation. Use fp16 as default.

HuggingFace URL: `https://huggingface.co/Kijai/MelBandRoFormer_comfy/tree/main`

### Core Nodes Also Required

| Core Node | Purpose |
|-----------|---------|
| `LoadAudio` | Load input audio file (core ComfyUI audio node) |
| `SaveAudioMP3` or `SaveAudio` | Save separated stems |
| `PreviewAudio` | Preview output in UI |

### Sampler Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `num_overlap` | 4 | Higher = better quality, slower. 4 is good default. |
| `chunk_size` | 352800 | Audio chunk length. Default handles ~8s at 44.1kHz. |

### Template Recommendation

Build a **vocal/instrumental separation** workflow: `LoadAudio` -> `MelBandRoFormerModelLoader` + `MelBandRoFormerSampler` -> two output branches: `SaveAudio` (vocals) + `SaveAudio` (instruments). Simple, clean, demonstrates the pack's core value. Confidence: HIGH.

### Cloud Compatibility

| Concern | Status | Impact |
|---------|--------|--------|
| Pack in registry | YES (publisher: kijai) | Installs via registry |
| Model format | `.safetensors` | Safe format, will display download links |
| Model size | 456 MB (fp16) | Reasonable download |
| Audio I/O | Requires ComfyUI audio node support | ComfyUI has native `LoadAudio`/`SaveAudio` nodes (added ~2024) |
| Risk | Audio templates are less common in the library | May need extra testing to verify audio pipeline works end-to-end on cloud |

---

## Cross-Template Dependencies

### Shared Dependencies

| Dependency | Used By | Notes |
|------------|---------|-------|
| `transformers` | Florence2, Impact Pack | Both need HuggingFace transformers; version ranges should be compatible |
| `torch` / `torchvision` | All 4 | Provided by ComfyUI runtime, not declared by packs |
| `numpy` | Impact Pack, MelBandRoFormer (via einops) | Universal, no conflicts |

### No Inter-Template Dependencies

The 4 templates are fully independent. No template requires nodes from another template's pack. Each can be built, tested, and submitted independently in any order.

### Pack Install Summary

| Template | Custom Packs Required | Total Model Download |
|----------|----------------------|---------------------|
| Florence2 | 1 (`comfyui-florence2`) | ~1.5 GB |
| GGUF FLUX | 1 (`ComfyUI-GGUF`) | ~12 GB (Q4_K_S UNET + Q8 T5 + CLIP-L + VAE) |
| Impact Pack | 2 (`comfyui-impact-pack` + `comfyui-impact-subpack`) | ~4.6 GB (checkpoint + SAM + YOLO) |
| MelBandRoFormer | 1 (`comfyui-melbandroformer`) | ~456 MB |

---

## What NOT to Include

| Exclusion | Why |
|-----------|-----|
| FLUX.1-dev models | Non-commercial license. Use FLUX.1-schnell (Apache 2.0) for templates. |
| Florence-2-base variants | Noticeably worse performance. Always use `large-ft`. |
| SAM ViT-H / ViT-L | 2.4 GB / 1.2 GB respectively. ViT-B is sufficient for face detailing. |
| T5-XXL below Q5 quantization | Quality degrades noticeably. Q5_K_M is the minimum recommended. |
| Impact Pack's 200+ non-FaceDetailer nodes | Template should be focused. Only use the face detection + detailing subset. |
| ComfyUI-Florence2SAM2 | Different pack by different author (rdancer). Not the trending one (kijai). |
| MelBandRoFormer fp32 model | Twice the size for negligible quality gain. Default to fp16. |
| `TripleCLIPLoaderGGUF` / `QuadrupleCLIPLoaderGGUF` | For SD3/other architectures, not FLUX. |
| `UnetLoaderGGUFAdvanced` | Standard `UnetLoaderGGUF` is sufficient for the template. |

---

## Template index.json Model Metadata Format

Each template's models should be declared in the workflow JSON's node `properties.models` field:

```json
{
  "name": "model_filename.safetensors",
  "url": "https://huggingface.co/.../resolve/main/model_filename.safetensors?download=true",
  "hash": "SHA256_value",
  "hash_type": "SHA256",
  "directory": "model_subfolder"
}
```

**GGUF caveat:** The template system displays `.gguf` files as "unsafe" and won't auto-show download links. The metadata can still be included, but users may need manual download instructions. This is an ecosystem limitation, not a template authoring problem.

**Model `directory` values by template:**

| Template | directory values |
|----------|-----------------|
| Florence2 | `LLM` |
| GGUF FLUX | `unet_gguf`, `clip_gguf`, `clip`, `vae` |
| Impact Pack | `checkpoints`, `sams`, `ultralytics/bbox` |
| MelBandRoFormer | `diffusion_models` |

---

## Sources

### Florence2
- [kijai/ComfyUI-Florence2 GitHub](https://github.com/kijai/ComfyUI-Florence2) -- node source code, NODE_CLASS_MAPPINGS (HIGH confidence)
- [ComfyUI-Florence2 nodes.py](https://github.com/kijai/ComfyUI-Florence2/blob/main/nodes.py) -- task types, model list (HIGH confidence)
- [ComfyUI-Florence2 pyproject.toml](https://github.com/kijai/ComfyUI-Florence2/blob/main/pyproject.toml) -- dependencies (HIGH confidence)
- [microsoft/Florence-2-large on HuggingFace](https://huggingface.co/microsoft/Florence-2-large) -- model specs, 0.77B params (HIGH confidence)
- [Florence2 Nodes DeepWiki](https://deepwiki.com/kijai/ComfyUI-Florence2/4-florence2-nodes) -- task enumeration (MEDIUM confidence)

### GGUF
- [city96/ComfyUI-GGUF GitHub](https://github.com/city96/ComfyUI-GGUF) -- node source, architecture (HIGH confidence)
- [city96/ComfyUI-GGUF nodes.py](https://github.com/city96/ComfyUI-GGUF/blob/main/nodes.py) -- NODE_CLASS_MAPPINGS, folder paths (HIGH confidence)
- [city96/FLUX.1-schnell-gguf on HuggingFace](https://huggingface.co/city96/FLUX.1-schnell-gguf) -- model files, sizes (HIGH confidence)
- [city96/FLUX.1-dev-gguf on HuggingFace](https://huggingface.co/city96/FLUX.1-dev-gguf) -- model files (HIGH confidence)
- [city96/t5-v1_1-xxl-encoder-gguf on HuggingFace](https://huggingface.co/city96/t5-v1_1-xxl-encoder-gguf) -- T5 encoder GGUF files (HIGH confidence)
- [comfyanonymous/flux_text_encoders on HuggingFace](https://huggingface.co/comfyanonymous/flux_text_encoders/blob/main/clip_l.safetensors) -- CLIP-L model (HIGH confidence)
- [GGUF Template Request Issue #11819](https://github.com/Comfy-Org/ComfyUI/issues/11819) -- GGUF not yet in official templates (HIGH confidence)

### Impact Pack
- [ltdrdata/ComfyUI-Impact-Pack GitHub](https://github.com/ltdrdata/ComfyUI-Impact-Pack) -- overview, node list (HIGH confidence)
- [ComfyUI-Impact-Pack __init__.py](https://github.com/ltdrdata/ComfyUI-Impact-Pack/blob/Main/__init__.py) -- NODE_CLASS_MAPPINGS (HIGH confidence)
- [ltdrdata/ComfyUI-Impact-Subpack GitHub](https://github.com/ltdrdata/ComfyUI-Impact-Subpack) -- UltralyticsDetectorProvider, model paths (HIGH confidence)
- [ComfyUI-Impact-Pack requirements.txt](https://github.com/ltdrdata/ComfyUI-Impact-Pack/blob/Main/requirements.txt) -- Python dependencies (HIGH confidence)
- [Impact Pack Installation DeepWiki](https://deepwiki.com/ltdrdata/ComfyUI-Impact-Pack/2-installation-and-configuration) -- model download paths (MEDIUM confidence)
- [FaceDetailer tutorial - ThinkDiffusion](https://learn.thinkdiffusion.com/comfyui-face-detailer/) -- workflow pattern (MEDIUM confidence)

### MelBandRoFormer
- [kijai/ComfyUI-MelBandRoFormer GitHub](https://github.com/kijai/ComfyUI-MelBandRoFormer) -- overview (HIGH confidence)
- [ComfyUI-MelBandRoFormer nodes.py](https://github.com/kijai/ComfyUI-MelBandRoFormer/blob/main/nodes.py) -- NODE_CLASS_MAPPINGS, types (HIGH confidence)
- [Kijai/MelBandRoFormer_comfy on HuggingFace](https://huggingface.co/Kijai/MelBandRoFormer_comfy/tree/main) -- model files, exact sizes (HIGH confidence)
- [ComfyUI-MelBandRoFormer pyproject.toml](https://github.com/kijai/ComfyUI-MelBandRoFormer/blob/main/pyproject.toml) -- dependencies (HIGH confidence)

### General
- [Comfy-Org/workflow_templates GitHub](https://github.com/Comfy-Org/workflow_templates) -- template format, model metadata schema (HIGH confidence)
- [ComfyUI Workflow JSON Spec](https://docs.comfy.org/specs/workflow_json) -- workflow format (HIGH confidence)
- [ComfyUI FLUX tutorial](https://docs.comfy.org/tutorials/flux/flux-1-text-to-image) -- FLUX workflow structure (HIGH confidence)
