# Feature Landscape: v2.0 Template Batch

**Domain:** ComfyUI workflow templates for 4 trending node packs
**Researched:** 2026-03-25
**Overall confidence:** MEDIUM-HIGH

## Template Overview

Each template targets a high-download, zero-coverage node pack from the Comfy registry. Templates must pass the existing validation engine, ship with index.json metadata and Notion submission docs, and run on Comfy Cloud.

| Template | Node Pack | Downloads | Domain | Complexity |
|----------|-----------|-----------|--------|------------|
| Florence2 Vision AI | ComfyUI-Florence2 (kijai) | 1.25M | Vision/NLP | Medium |
| GGUF Quantized txt2img | ComfyUI-GGUF (city96) | 1.69M | Image Gen | Low-Medium |
| Impact Pack Face Detailer | ComfyUI Impact Pack (ltdrdata) | 2.37M | Post-processing | Medium-High |
| MelBandRoFormer Stem Split | ComfyUI-MelBandRoFormer (kijai) | 240K | Audio | Low |

---

## Template 1: ComfyUI-Florence2 -- Vision AI Multi-Task

### What It Does

Showcases Florence-2 as a vision foundation model that handles captioning, object detection, segmentation, and OCR from a single model load. The template demonstrates the multi-task nature: one model, many outputs.

### Ideal Workflow Graph

```
LoadImage ──────────────────────────┐
                                    v
DownloadAndLoadFlorence2Model ──> Florence2Run ──> IMAGE (annotated)
           (florence-2-large-ft)     ^    │──────> MASK (segmentation)
                                    │    │──────> STRING (caption/OCR text)
                                    │    └──────> JSON (structured data)
                                    │
                              text_input + task selector
                                    │
                              PreviewImage <── IMAGE output
                              PreviewAny  <── STRING output
```

**Recommended task for primary demo:** `more_detailed_caption` -- universally useful, zero text input required, produces impressive results on any image.

**Secondary tasks to expose:** `referring_expression_segmentation` (text-guided segmentation) and `caption_to_phrase_grounding` (object detection with bounding boxes) -- these showcase the interactive nature where user text input drives what gets detected.

### Node Inventory

| Node | Class Type | Pack | Role | Required |
|------|-----------|------|------|----------|
| Load Image | `LoadImage` | Core | Input image | Yes |
| Download & Load Florence2 Model | `DownloadAndLoadFlorence2Model` | ComfyUI-Florence2 | Model loader | Yes |
| Florence2 Run | `Florence2Run` | ComfyUI-Florence2 | Inference | Yes |
| Preview Image | `PreviewImage` | Core | Show annotated result | Yes |
| Preview Any | `PreviewAny` | Core | Show text output | Yes |

### Key Connections

| Source Node | Output Slot | Target Node | Input Slot | Type |
|-------------|-------------|-------------|------------|------|
| LoadImage | IMAGE (0) | Florence2Run | image | IMAGE |
| DownloadAndLoadFlorence2Model | florence2_model (0) | Florence2Run | florence2_model | FL2MODEL |
| Florence2Run | image (0) | PreviewImage | images | IMAGE |

### Widget Configuration

| Node | Widget | Recommended Value | Rationale |
|------|--------|-------------------|-----------|
| DownloadAndLoadFlorence2Model | model | `microsoft/Florence-2-large-ft` | Best quality for template; fine-tuned variant handles all tasks well |
| DownloadAndLoadFlorence2Model | precision | `fp16` | Balances quality and VRAM; works on consumer GPUs |
| DownloadAndLoadFlorence2Model | attention | `sdpa` | Most compatible attention mechanism; flash_attention_2 may not be available everywhere |
| Florence2Run | task | `more_detailed_caption` | Best default demo; no text input needed |
| Florence2Run | fill_mask | `True` | Required for segmentation tasks to produce filled masks |
| Florence2Run | max_new_tokens | `1024` | Sufficient for detailed captions |
| Florence2Run | num_beams | `3` | Good quality/speed tradeoff |

### Table Stakes

| Feature | Why Expected | Notes |
|---------|-------------|-------|
| Multi-task demonstration | Florence2's selling point is one model, many tasks -- template must show at least captioning + detection | Users download Florence2 specifically for its versatility |
| Image annotation output | Bounding boxes and region labels rendered on the image | Florence2Run outputs annotated IMAGE directly for detection tasks |
| Text caption output | Readable text describing the image | Core output for captioning tasks; use PreviewAny to display |
| Model auto-download | DownloadAndLoadFlorence2Model handles download | No manual model management needed |

### Differentiators

| Feature | Value Proposition | Notes |
|---------|-------------------|-------|
| Task switcher via widget | Users change the `task` dropdown to switch between captioning, detection, segmentation, OCR without rewiring | Single workflow, 15 different tasks |
| Segmentation mask output | Usable as input for inpainting or compositing downstream | Mask output from Florence2Run enables pipeline integration |
| Prompt-driven detection | `referring_expression_segmentation` lets users type what to find | Interactive: "find the red car" produces a mask of just the red car |
| Structured JSON output | `data` output carries bounding box coordinates, labels, regions | Enables downstream programmatic use, not just visual |

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Chaining Florence2 with a diffusion model | Overly complex for a template showcasing Florence2 itself; muddies the value prop | Keep template focused on vision understanding, not generation |
| Multiple Florence2Run nodes for different tasks | Increases VRAM usage and complexity; users can switch the task widget | Single Florence2Run node with task dropdown |
| LoRA fine-tuning demo | DownloadAndLoadFlorence2Lora exists but adds complexity and requires niche LoRA models | Stick to base/ft models; LoRA is advanced usage |
| DocVQA as primary task | Requires a document-style image to be meaningful; too niche for a general template | Show it as a note/comment, not the default task |
| keep_model_loaded=True | Wastes VRAM between runs; cloud billing concern | Default False; user can enable if doing batch work |

### Model Requirements

| Model | Size | VRAM (fp16) | Source |
|-------|------|-------------|--------|
| Florence-2-large-ft | ~1.5GB | ~3-4GB | HuggingFace microsoft/Florence-2-large-ft (auto-downloaded) |

**Cloud compatibility:** HIGH -- model is small, auto-downloads, no manual placement needed. No API auth required.

---

## Template 2: ComfyUI-GGUF -- Quantized Flux txt2img

### What It Does

Demonstrates running Flux (or similar transformer/DiT model) using GGUF quantization for dramatically reduced VRAM requirements. The template is a drop-in alternative to the standard Flux txt2img workflow, but accessible on consumer GPUs with 8-12GB VRAM.

### Ideal Workflow Graph

```
UnetLoaderGGUF ──────────────────────> MODEL ─┐
  (flux1-dev-Q8_0.gguf)                       │
                                               v
DualCLIPLoaderGGUF ─────────────────> CLIP ──> CLIPTextEncode (positive) ──> CONDITIONING ─┐
  (clip_l.safetensors +                  │                                                  │
   t5xxl_fp16.safetensors)               └──> CLIPTextEncode (negative) ──> CONDITIONING ─┐ │
                                                                                           │ │
VAELoader ──────────────────────────> VAE ──────────────────────────────┐                  │ │
  (ae.safetensors)                                                      │                  │ │
                                                                        v                  v v
EmptyLatentImage ──> LATENT ──> KSampler <─────────────────────────────────────────────────┘
  (1024x1024)                      │
                                   v
                              VAEDecode ──> IMAGE ──> PreviewImage
```

### Node Inventory

| Node | Class Type | Pack | Role | Required |
|------|-----------|------|------|----------|
| Unet Loader (GGUF) | `UnetLoaderGGUF` | ComfyUI-GGUF | Load quantized diffusion model | Yes |
| Dual CLIP Loader (GGUF) | `DualCLIPLoaderGGUF` | ComfyUI-GGUF | Load CLIP text encoders | Yes |
| CLIP Text Encode (positive) | `CLIPTextEncode` | Core | Positive prompt | Yes |
| CLIP Text Encode (negative) | `CLIPTextEncode` | Core | Negative prompt | Yes |
| VAE Loader | `VAELoader` | Core | Load VAE | Yes |
| Empty Latent Image | `EmptyLatentImage` | Core | Create latent canvas | Yes |
| KSampler | `KSampler` | Core | Sampling/denoising | Yes |
| VAE Decode | `VAEDecode` | Core | Latent to image | Yes |
| Preview Image | `PreviewImage` | Core | Display result | Yes |

### Key Connections

| Source Node | Output | Target Node | Input | Type |
|-------------|--------|-------------|-------|------|
| UnetLoaderGGUF | MODEL (0) | KSampler | model | MODEL |
| DualCLIPLoaderGGUF | CLIP (0) | CLIPTextEncode (pos) | clip | CLIP |
| DualCLIPLoaderGGUF | CLIP (0) | CLIPTextEncode (neg) | clip | CLIP |
| CLIPTextEncode (pos) | CONDITIONING (0) | KSampler | positive | CONDITIONING |
| CLIPTextEncode (neg) | CONDITIONING (0) | KSampler | negative | CONDITIONING |
| VAELoader | VAE (0) | VAEDecode | vae | VAE |
| EmptyLatentImage | LATENT (0) | KSampler | latent_image | LATENT |
| KSampler | LATENT (0) | VAEDecode | samples | LATENT |
| VAEDecode | IMAGE (0) | PreviewImage | images | IMAGE |

### Widget Configuration

| Node | Widget | Recommended Value | Rationale |
|------|--------|-------------------|-----------|
| UnetLoaderGGUF | unet_name | `flux1-dev-Q8_0.gguf` | Best quality GGUF quant; Q8 is near-lossless for Flux |
| DualCLIPLoaderGGUF | clip_name1 | `clip_l.safetensors` | Standard CLIP-L for Flux |
| DualCLIPLoaderGGUF | clip_name2 | `t5xxl_fp16.safetensors` | T5-XXL text encoder (can also be GGUF quantized) |
| DualCLIPLoaderGGUF | type | `flux` | Flux-specific CLIP configuration |
| EmptyLatentImage | width | `1024` | Flux native resolution |
| EmptyLatentImage | height | `1024` | Flux native resolution |
| KSampler | sampler_name | `euler` | Standard for Flux |
| KSampler | scheduler | `simple` | Works well with Flux |
| KSampler | steps | `20` | Good quality for Flux dev |
| KSampler | cfg | `1.0` | Flux uses guidance-free or low CFG |

### Table Stakes

| Feature | Why Expected | Notes |
|---------|-------------|-------|
| Drop-in GGUF model loading | Users expect the GGUF nodes to work exactly like standard loaders, just with .gguf files | UnetLoaderGGUF outputs MODEL, same type as UNETLoader |
| Standard txt2img pipeline | The rest of the workflow must be familiar: prompt, sample, decode, preview | Only the loaders change; everything else is core nodes |
| Working Flux generation | Template must actually produce good images; GGUF is about efficiency, not different output | Q8 quality is virtually identical to fp16 |
| Proper model file paths | Models in correct directories (unet/ for GGUF, clip/ for CLIP, vae/ for VAE) | Cloud must find the models |

### Differentiators

| Feature | Value Proposition | Notes |
|---------|-------------------|-------|
| VRAM accessibility | Run Flux on 8-12GB GPUs instead of requiring 24GB+ | This is the entire point of GGUF; template makes it easy |
| DualCLIPLoaderGGUF with mixed formats | Can load one CLIP in GGUF and another in safetensors | Flexibility for partial quantization |
| Near-identical output quality | Q8 GGUF produces images visually identical to full precision | Users get Flux quality without Flux VRAM requirements |
| Educational value | Shows the GGUF ecosystem: where to get models, which quant levels to choose | Notes in template explain Q4 vs Q8 tradeoffs |

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| UnetLoaderGGUFAdvanced as default | Adds dequant_dtype/patch_dtype complexity; confusing for beginners | Use simple UnetLoaderGGUF; advanced node is for power users |
| Q4 quantization as default | Visible quality loss; bad first impression for a template | Default to Q8; mention Q4 in notes for extreme low-VRAM |
| LoRA in the GGUF workflow | LoRA support with GGUF is limited/experimental; may not work on all quants | Keep it pure txt2img; LoRA can be a separate template |
| TripleCLIPLoaderGGUF or QuadrupleCLIPLoaderGGUF | Only needed for SD3.5 or exotic architectures; overcomplicates Flux demo | DualCLIPLoaderGGUF is correct for Flux |
| Multiple quantization levels side-by-side | Confusing; users can swap the model file themselves | One model, one quality level; document alternatives in notes |
| Flux guidance node (FluxGuidance) | Standard KSampler with cfg=1.0 works for Flux dev; adding FluxGuidance complicates the graph for marginal benefit | Keep it simple with KSampler |

### Model Requirements

| Model | Size | VRAM | Source | Directory |
|-------|------|------|--------|-----------|
| flux1-dev-Q8_0.gguf | ~11.9GB | ~12GB | city96/FLUX.1-dev-gguf on HuggingFace | models/unet/ |
| clip_l.safetensors | ~235MB | shared | comfyanonymous/flux_text_encoders on HuggingFace | models/clip/ |
| t5xxl_fp16.safetensors | ~9.8GB | shared | comfyanonymous/flux_text_encoders on HuggingFace | models/clip/ |
| ae.safetensors | ~168MB | ~0.5GB | black-forest-labs/FLUX.1-dev on HuggingFace | models/vae/ |

**Total VRAM estimate:** ~12-14GB for Q8 (vs ~24GB for fp16 Flux)

**Cloud compatibility:** MEDIUM -- models are large and must be pre-placed. Cloud providers typically have Flux models cached. The GGUF quant files may need manual upload if not pre-cached. Check Comfy Cloud model availability.

**Alternative for lower VRAM:** Swap to `flux1-dev-Q4_K_S.gguf` (~6.8GB) for 8GB GPU cards, and use `t5xxl-Q8_0.gguf` instead of the fp16 T5 encoder.

---

## Template 3: ComfyUI Impact Pack -- Face Detection + Auto-Detailing

### What It Does

Demonstrates the detect-detail pipeline: automatically find faces in a generated or loaded image, then re-render each face at higher detail using inpainting. This is the most common post-processing step in SD/Flux workflows -- fixing mangled or low-detail faces.

### Ideal Workflow Graph

```
CheckpointLoaderSimple ──> MODEL ──────────────────────────┐
         │                                                  │
         ├──> CLIP ──> CLIPTextEncode (pos) ──> COND ──┐   │
         │         └──> CLIPTextEncode (neg) ──> COND ─┐│   │
         └──> VAE ─────────────────────────────────┐   ││   │
                                                    │   ││   │
LoadImage ──> IMAGE ────────────────────────────────┼───┼┼───┼──┐
                                                    │   ││   │  │
UltralyticsDetectorProvider ──> BBOX_DETECTOR ──┐   │   ││   │  │
  (face_yolov8m.pt)                             │   │   ││   │  │
                                                v   v   vv   v  v
SAMLoader ──> SAM_MODEL ──────────────────> FaceDetailer
  (sam_vit_b_01ec64.pth)                        │
                                                ├──> IMAGE (enhanced) ──> PreviewImage
                                                ├──> IMAGE (cropped_refined)
                                                ├──> IMAGE (cropped_enhanced_alpha)
                                                ├──> MASK (detection mask)
                                                └──> DETAILER_PIPE
```

### Node Inventory

| Node | Class Type | Pack | Role | Required |
|------|-----------|------|------|----------|
| Checkpoint Loader | `CheckpointLoaderSimple` | Core | Load base model for re-rendering | Yes |
| CLIP Text Encode (pos) | `CLIPTextEncode` | Core | Positive prompt for face detail | Yes |
| CLIP Text Encode (neg) | `CLIPTextEncode` | Core | Negative prompt | Yes |
| Load Image | `LoadImage` | Core | Input image with faces | Yes |
| Ultralytics Detector Provider | `UltralyticsDetectorProvider` | Impact Pack | Load face detection model | Yes |
| SAM Loader | `SAMLoader` | Impact Pack | Load Segment Anything model | Yes |
| Face Detailer | `FaceDetailer` | Impact Pack | Detect and enhance faces | Yes |
| Preview Image | `PreviewImage` | Core | Show enhanced result | Yes |

### Key Connections

| Source Node | Output | Target Node | Input | Type |
|-------------|--------|-------------|-------|------|
| CheckpointLoaderSimple | MODEL (0) | FaceDetailer | model | MODEL |
| CheckpointLoaderSimple | CLIP (1) | CLIPTextEncode (pos) | clip | CLIP |
| CheckpointLoaderSimple | CLIP (1) | CLIPTextEncode (neg) | clip | CLIP |
| CheckpointLoaderSimple | VAE (2) | FaceDetailer | vae | VAE |
| CLIPTextEncode (pos) | CONDITIONING (0) | FaceDetailer | positive | CONDITIONING |
| CLIPTextEncode (neg) | CONDITIONING (0) | FaceDetailer | negative | CONDITIONING |
| LoadImage | IMAGE (0) | FaceDetailer | image | IMAGE |
| UltralyticsDetectorProvider | BBOX_DETECTOR (0) | FaceDetailer | bbox_detector | BBOX_DETECTOR |
| SAMLoader | SAM_MODEL (0) | FaceDetailer | sam_model_opt | SAM_MODEL |
| FaceDetailer | IMAGE (0) | PreviewImage | images | IMAGE |

### Widget Configuration

| Node | Widget | Recommended Value | Rationale |
|------|--------|-------------------|-----------|
| CheckpointLoaderSimple | ckpt_name | (user's choice / SD1.5 or SDXL) | Model should match the source image's generation model |
| UltralyticsDetectorProvider | model_name | `face_yolov8m.pt` | Standard face detection model; best balance of speed and accuracy |
| SAMLoader | model_name | `sam_vit_b_01ec64.pth` | SAM base model; sufficient for face masking |
| SAMLoader | device_mode | `AUTO` | Let ComfyUI choose CPU/GPU |
| FaceDetailer | guide_size | `512` | Good detail resolution for faces |
| FaceDetailer | guide_size_for | `True` | Apply guide size to detected bbox |
| FaceDetailer | max_size | `1024` | Cap to prevent excessive processing |
| FaceDetailer | steps | `20` | Sufficient for face re-rendering |
| FaceDetailer | cfg | `7.0` | Standard CFG for inpainting |
| FaceDetailer | denoise | `0.5` | Moderate denoise preserves face structure while adding detail |
| FaceDetailer | seed | `0` | Reproducible results |
| CLIPTextEncode (pos) | text | `"detailed face, sharp features, high quality"` | Guides the face re-rendering |
| CLIPTextEncode (neg) | text | `"blurry, distorted, deformed"` | Prevents common face artifacts |

### Table Stakes

| Feature | Why Expected | Notes |
|---------|-------------|-------|
| Automatic face detection | Users download Impact Pack specifically for auto face fixing | UltralyticsDetectorProvider + face_yolov8m.pt is the standard approach |
| SAM-based face masking | Pixel-accurate face masks prevent background bleed | SAMLoader + sam_vit_b is the expected combo with bbox detection |
| Single-node face enhancement | FaceDetailer wraps detect+mask+inpaint into one node | This is the flagship node; users expect it front and center |
| Works with any checkpoint | Template must be checkpoint-agnostic via CheckpointLoaderSimple | Users bring their own SD1.5/SDXL/etc model |

### Differentiators

| Feature | Value Proposition | Notes |
|---------|-------------------|-------|
| Face-focused prompting | Positive/negative prompts specifically tuned for face quality | Most users don't realize FaceDetailer uses conditioning |
| Mask output visualization | Showing the detection mask helps users understand what was processed | Connect FaceDetailer MASK output to a separate PreviewImage |
| SAM precision masking | Using SAM on top of bbox detection gives pixel-perfect face boundaries | Without SAM, the bbox rectangle bleeds into background |
| Before/after comparison | LoadImage output + FaceDetailer output shown side by side | Compelling visual proof of the enhancement |

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Full generation + FaceDetailer pipeline | Adding txt2img before FaceDetailer doubles the template complexity | Use LoadImage as input; user can chain with their own generation workflow |
| FaceDetailer (pipe) variant | Pipe version bundles parameters, hiding them from the user; less educational | Use standard FaceDetailer with explicit connections |
| Multiple detector types (CLIPSeg, ONNX) | Adds confusion; face_yolov8m is the proven standard | Stick with UltralyticsDetectorProvider |
| DetailerForEach / SEGSDetailer | More flexible but much more complex; not needed for the common face-fix use case | FaceDetailer is the right abstraction level |
| Multi-pass detailing (chained FaceDetailers) | Advanced technique; makes the template too complex | Single pass is sufficient for 90% of use cases |
| ControlNet/IPAdapter integration with detailer | Expert-level feature; distracts from core value | Keep template focused on the detect-detail pattern |

### Model Requirements

| Model | Size | VRAM | Source | Directory |
|-------|------|------|--------|-----------|
| Any SD1.5/SDXL checkpoint | 2-7GB | 4-8GB | User's choice | models/checkpoints/ |
| face_yolov8m.pt | ~6MB | Minimal | Ultralytics / ComfyUI-Manager auto-download | models/ultralytics/bbox/ |
| sam_vit_b_01ec64.pth | ~375MB | ~1GB | Meta / ComfyUI-Manager auto-download | models/sams/ |

**Total VRAM estimate:** ~5-10GB (dominated by the checkpoint, not the detection models)

**Cloud compatibility:** HIGH -- Impact Pack is widely used, detection models are small and often pre-cached. Checkpoint is user-provided. The face_yolov8m and SAM models may need to be declared in the models array.

---

## Template 4: ComfyUI-MelBandRoFormer -- Audio Stem Separation

### What It Does

Splits an audio file into vocals and instrumentals using the Mel-Band RoFormer model. This is the simplest template of the four: load audio, load model, process, get two separate audio outputs.

### Ideal Workflow Graph

```
LoadAudio ──────────────────> AUDIO ──┐
  (input.wav/mp3/flac)                │
                                      v
MelBandRoFormerModelLoader ──> MODEL ──> MelBandRoFormerSampler
  (MelBandRoFormer model)                    │
                                             ├──> AUDIO (vocals) ──> SaveAudio ("vocals")
                                             └──> AUDIO (instruments) ──> SaveAudio ("instruments")
```

### Node Inventory

| Node | Class Type | Pack | Role | Required |
|------|-----------|------|------|----------|
| Load Audio | `LoadAudio` | Core | Input audio file | Yes |
| Mel-Band RoFormer Model Loader | `MelBandRoFormerModelLoader` | ComfyUI-MelBandRoFormer | Load separation model | Yes |
| Mel-Band RoFormer Sampler | `MelBandRoFormerSampler` | ComfyUI-MelBandRoFormer | Perform stem separation | Yes |
| Save Audio (vocals) | `SaveAudio` | Core | Save vocal track | Yes |
| Save Audio (instruments) | `SaveAudio` | Core | Save instrumental track | Yes |

### Key Connections

| Source Node | Output | Target Node | Input | Type |
|-------------|--------|-------------|-------|------|
| LoadAudio | AUDIO (0) | MelBandRoFormerSampler | audio | AUDIO |
| MelBandRoFormerModelLoader | MELROFORMERMODEL (0) | MelBandRoFormerSampler | model | MELROFORMERMODEL |
| MelBandRoFormerSampler | vocals (0) | SaveAudio (vocals) | audio | AUDIO |
| MelBandRoFormerSampler | instruments (1) | SaveAudio (instruments) | audio | AUDIO |

### Widget Configuration

| Node | Widget | Recommended Value | Rationale |
|------|--------|-------------------|-----------|
| MelBandRoFormerModelLoader | model_name | (best available .ckpt in diffusion_models/) | Use the latest MelBandRoFormer model from Kijai/MelBandRoFormer_comfy on HuggingFace |
| SaveAudio (vocals) | filename_prefix | `vocals` | Clear naming for output files |
| SaveAudio (instruments) | filename_prefix | `instruments` | Clear naming for output files |

### Table Stakes

| Feature | Why Expected | Notes |
|---------|-------------|-------|
| Vocal/instrumental separation | The fundamental use case; users download this pack for exactly this | MelBandRoFormerSampler outputs both vocals and instruments |
| Standard audio input | LoadAudio supports wav, mp3, ogg, flac, aiff | Users bring their own audio files |
| Saved output files | Both separated stems saved as audio files | SaveAudio with clear filename prefixes |
| Simple 3-node core | Load model, process audio, save outputs | MelBandRoFormer has only 2 custom nodes -- template should reflect this simplicity |

### Differentiators

| Feature | Value Proposition | Notes |
|---------|-------------------|-------|
| Dual output demonstration | Both stems saved simultaneously with clear naming | Shows the two-output nature of the sampler node |
| Audio-domain template | Fills a gap in template coverage; most templates are image/video focused | Audio templates are underrepresented in the library |
| Minimal node count | 5 nodes total; easiest template to understand and modify | Simplicity is a feature for audio users who may be new to ComfyUI |
| Pipeline-ready outputs | AUDIO type outputs can chain into other audio processing nodes | Enables vocal-only TTS, instrumental remixing, etc. |

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Chaining with video/image generation | Audio separation is its own domain; mixing with image gen is confusing | Keep it audio-only; users can integrate into larger workflows |
| Multiple separation passes | Over-engineering; one pass produces clean separation | Single pass with good model is sufficient |
| Custom audio visualization | No core ComfyUI nodes for waveform display; would need another custom pack | Save files; users listen externally |
| Batch processing multiple files | LoadAudio handles one file; batching adds loop complexity | One file at a time; users re-run for multiple files |
| Alternative audio separation packs (audio-separation-nodes-comfyui) | Different node pack; this template is specifically for MelBandRoFormer | Stick to kijai's nodes; they're the ones with 240K downloads |

### Model Requirements

| Model | Size | VRAM | Source | Directory |
|-------|------|------|--------|-----------|
| MelBandRoFormer checkpoint | ~100-200MB | ~2-4GB | Kijai/MelBandRoFormer_comfy on HuggingFace | models/diffusion_models/ |

**Total VRAM estimate:** ~2-4GB (lightweight model)

**Cloud compatibility:** MEDIUM -- LoadAudio/SaveAudio are core nodes but relatively new additions (2025). MelBandRoFormer model needs to be available on cloud. The AUDIO type is well-supported in current ComfyUI. Model must be declared in template metadata.

**Important note:** The core_nodes.json in the project does not list LoadAudio/SaveAudio. These are confirmed core nodes in ComfyUI (by comfyanonymous) but were added after the original core_nodes.json was compiled. The validator may flag these as custom nodes unless core_nodes.json is updated.

---

## Feature Dependencies Across Templates

```
All templates share:
  - Template metadata generation (index.json) ← existing DOCS-01
  - Notion submission doc generation ← existing DOCS-02
  - Validation against guidelines ← existing VALD-01..04

Template-specific:
  Florence2: DownloadAndLoadFlorence2Model → Florence2Run (simple chain)
  GGUF: UnetLoaderGGUF + DualCLIPLoaderGGUF → standard pipeline (drop-in replacement)
  Impact Pack: UltralyticsDetectorProvider + SAMLoader → FaceDetailer (detector-detailer pattern)
  MelBandRoFormer: MelBandRoFormerModelLoader → MelBandRoFormerSampler (simple chain)
```

## Cross-Template Feature Matrix

| Feature | Florence2 | GGUF | Impact Pack | MelBand |
|---------|-----------|------|-------------|---------|
| Custom node count | 2 | 2 | 3 | 2 |
| Core node count | 2-3 | 7 | 5 | 3 |
| Total node count | 4-5 | 9 | 8 | 5 |
| Connection complexity | Low | Medium | Medium-High | Low |
| Model count | 1 | 3-4 | 2-3 (+ checkpoint) | 1 |
| VRAM requirement | Low (~4GB) | Medium-High (~12GB) | Medium (~5-10GB) | Low (~2-4GB) |
| Media type | image | image | image | audio |
| Primary output | TEXT + IMAGE + MASK | IMAGE | IMAGE | AUDIO |
| User text input required | Optional (task-dependent) | Yes (prompt) | Yes (face prompt) | No |

## MVP Recommendation

Build in this order:

1. **MelBandRoFormer** (simplest: 5 nodes, 2 custom, linear graph, low VRAM) -- fast win, fills audio gap
2. **Florence2** (simple: 4-5 nodes, 2 custom, linear graph, low VRAM) -- fills vision AI gap, multi-task demo
3. **GGUF txt2img** (medium: 9 nodes, 2 custom, standard pipeline, needs large models) -- high demand, model management complexity
4. **Impact Pack FaceDetailer** (most complex: 8 nodes, 3 custom, multiple detector inputs, needs checkpoint) -- most connections, most models, highest user expectations

**Rationale:** Start with the simplest graphs to validate the template creation pipeline, then tackle increasingly complex workflows. MelBandRoFormer and Florence2 are both linear chains that exercise the composer's add_node/connect flow without complex fan-in patterns. GGUF adds the standard multi-loader pipeline. Impact Pack is the stress test with detector providers, SAM, and the many-input FaceDetailer node.

## Validation Concerns

| Concern | Templates Affected | Resolution |
|---------|-------------------|------------|
| LoadAudio/SaveAudio not in core_nodes.json | MelBandRoFormer | Update core_nodes.json to include audio nodes |
| Custom connection types (FL2MODEL, MELROFORMERMODEL, BBOX_DETECTOR, SAM_MODEL) | All except GGUF | Composer's CONNECTION_TYPES set needs extension, or these types must be handled as custom/wildcard |
| Large model files for GGUF | GGUF | Models array in index.json must include download URLs and SHA256 hashes |
| Detection model auto-download | Impact Pack | face_yolov8m.pt and SAM models may auto-download but must be declared in template metadata |
| Newer GGUF node names | GGUF | UnetLoaderGGUF, DualCLIPLoaderGGUF are the correct current class names |

## Sources

### Florence2
- [kijai/ComfyUI-Florence2 GitHub](https://github.com/kijai/ComfyUI-Florence2) -- node source code, supported models (HIGH confidence)
- [Florence-2 ComfyUI Guide](https://comfyui.nomadoor.net/en/basic-workflows/florence2/) -- workflow patterns (MEDIUM confidence)
- [Florence2 Supported Tasks - DeepWiki](https://deepwiki.com/kijai/ComfyUI-Florence2/5-supported-tasks) -- complete task list (HIGH confidence)
- [RunComfy Florence2 Guide](https://www.runcomfy.com/comfyui-nodes/ComfyUI-Florence2) -- node catalog (MEDIUM confidence)

### GGUF
- [city96/ComfyUI-GGUF GitHub](https://github.com/city96/ComfyUI-GGUF) -- node source code, all loader nodes (HIGH confidence)
- [city96/FLUX.1-dev-gguf HuggingFace](https://huggingface.co/city96/FLUX.1-dev-gguf) -- quantized model files (HIGH confidence)
- [Flux GGUF Low VRAM Guide](https://www.nextdiffusion.ai/tutorials/how-to-run-flux-dev-gguf-in-comfyui-low-vram-guide) -- VRAM requirements by quant level (MEDIUM confidence)
- [ComfyUI GGUF 2026 Guide](https://cosmo-edge.com/comfyui-gguf-image-generation/) -- current best practices (MEDIUM confidence)

### Impact Pack
- [ltdrdata/ComfyUI-Impact-Pack GitHub](https://github.com/ltdrdata/ComfyUI-Impact-Pack) -- official repo (HIGH confidence)
- [FaceDetailer Node Docs - ComfyAI](https://comfyai.run/documentation/FaceDetailer) -- complete node spec (MEDIUM confidence)
- [FaceDetailer RunComfy Guide](https://www.runcomfy.com/comfyui-nodes/ComfyUI-Impact-Pack/FaceDetailer) -- workflow tutorial (MEDIUM confidence)
- [ThinkDiffusion FaceDetailer Guide](https://learn.thinkdiffusion.com/comfyui-face-detailer/) -- best practices (MEDIUM confidence)
- [myByways Impact Pack Detailers](https://mybyways.com/blog/improving-faces-with-impact-pack-detailers) -- multi-pass patterns (MEDIUM confidence)

### MelBandRoFormer
- [kijai/ComfyUI-MelBandRoFormer GitHub](https://github.com/kijai/ComfyUI-MelBandRoFormer) -- node source code, complete API (HIGH confidence)
- [MelBandRoFormer RunComfy Guide](https://www.runcomfy.com/comfyui-nodes/ComfyUI-MelBandRoFormer) -- workflow guide (MEDIUM confidence)
- [Mel-Band RoFormer Paper](https://arxiv.org/abs/2310.01809) -- underlying model architecture (HIGH confidence)

### General
- [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates) -- template repo structure, index.json schema (HIGH confidence)
- [ComfyUI Audio Processing](https://comfyanonymous.github.io/ComfyUI_examples/audio/) -- core audio node examples (HIGH confidence)
