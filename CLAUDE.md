# ComfyUI Template Agent

Claude Code agent toolkit for ComfyUI template creation. Six skills guide template creators from node discovery through submission documentation.

## Skills

| Skill | Trigger |
|-------|---------|
| comfy-discover | Exploring nodes -- trending, new, popular, or searching by capability |
| comfy-template-audit | Browsing templates, checking coverage, finding gaps worth filling |
| comfy-validate | Checking workflow JSON against guidelines, cloud compatibility, submission readiness |
| comfy-compose | Building workflows -- from scratch, from scaffold, or modifying existing |
| comfy-document | Generating submission docs -- index.json, Notion markdown, thumbnail specs |
| comfy-flow | Guided end-to-end template creation ("let's make a template") |

## Development

```bash
pytest                                     # Run tests (~0.5s)
python -m src.registry.highlights trending  # Test discovery
python -m src.validator.validate --file workflow.json  # Test validation
python -m src.templates.coverage gap --limit 10  # Test gap analysis
```

## Architecture

- `src/shared/` -- HTTP client (httpx), caching (DiskCache), format detection
- `src/registry/` -- Node discovery (highlights, search, spec)
- `src/templates/` -- Template library (fetch, search, cross_ref, coverage)
- `src/validator/` -- Validation engine (rules, engine, validate CLI)
- `src/composer/` -- Workflow composition (graph, scaffold, layout, compose CLI)
- `src/document/` -- Documentation generation (metadata, notion, generate CLI, orchestrator)
- `data/` -- Static data (core_nodes.json, guidelines.json, api_nodes.json)

## Conventions

- Pydantic models for all data structures
- Module-level DiskCache singletons for HTTP caching
- httpx with `follow_redirects=True` for all HTTP requests
- Tests in `tests/` mirroring `src/` structure
- CLI entry points via `python -m src.module.script`
- Workflow format JSON (nodes[] + links[]), never API format (string keys)

<important if="modifying skills">
Skills live in `.claude/skills/comfy-*/`. Each skill folder has:
- `SKILL.md` -- trigger description and essential behavior
- `gotchas.md` -- known failure points and non-obvious behavior

Do NOT create `scripts/` or `references/` subdirs unless the skill genuinely needs them.
</important>

<important if="adding dependencies">
All dependencies declared in `pyproject.toml`. Currently: httpx, pydantic.
Dev: pytest, ruff. Python 3.12+ required.
</important>

<important if="composing workflows">
ComfyUI MCP server must be connected (comfyui-cloud or comfyui-mcp).
NodeSpecCache is pass-through -- fetch specs via MCP `search_nodes`, then feed raw dicts in.
</important>

<!-- GSD:project-start source:PROJECT.md -->
## Project

**ComfyUI Template Agent**

An internal Claude Code agent toolkit for the ComfyUI templates team that streamlines the entire template creation workflow — from discovering trending nodes and ideating new templates, through composing valid workflow JSON, to generating Notion-ready submission docs. It packages a guided, phase-based workflow (inspired by GSD's structure) that's purpose-built for ComfyUI template creation, with built-in awareness of custom node constraints, API node auth requirements, cloud compatibility, and the team's Notion submission process.

**Core Value:** Template creators can go from "what should we build next?" to "here's a cloud-tested workflow with submission docs" in a single guided session, with the agent handling node discovery, compatibility checks, workflow composition, and documentation formatting.

### Constraints

- **Tech stack**: Python + Claude Code skills/agents — matches existing comfy-tip and MCP tooling
- **Distribution**: Lives in this repo (comfyui-template-agent), installable as Claude Code skills
- **API access**: Registry API (api.comfy.org, public), GitHub API (workflow_templates repo, public), ComfyUI Cloud MCP (existing)
- **No Notion API in v1**: Output is markdown, not direct Notion writes
- **Template format**: Must match workflow_templates repo conventions (index.json schema, file naming, bundle structure)
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

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
| Model | HuggingFace ID | Size | VRAM | Precision |
|-------|---------------|------|------|-----------|
| Florence-2-large-ft | `microsoft/Florence-2-large-ft` | ~1.5 GB | ~2-3 GB (fp16) | fp16 recommended |
- `microsoft/Florence-2-base` / `Florence-2-base-ft` -- smaller, worse quality
- `HuggingFaceM4/Florence-2-DocVQA` -- specialized for documents only
- `thwri/CogFlorence-2.1-Large` / `CogFlorence-2.2-Large` -- community fine-tunes
- `gokaygokay/Florence-2-SD3-Captioner` / `Florence-2-Flux-Large` -- prompt generation specialists
- `MiaoshouAI/Florence-2-large-PromptGen-v2.0` -- caption-focused
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
### Cloud Compatibility
- **Pack in registry:** YES (`comfyui-florence2` on registry.comfy.org)
- **Model auto-download:** YES (HuggingFace Hub, triggered at runtime)
- **Model format:** safetensors (safe format, will display download links)
- **Risk:** Model downloads ~1.5 GB on first run. Cloud environments should handle this, but first-run latency is notable.
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
| Model | HuggingFace | Filename | Size | Path |
|-------|------------|----------|------|------|
| FLUX.1-schnell Q4_K_S | `city96/FLUX.1-schnell-gguf` | `flux1-schnell-Q4_K_S.gguf` | 6.78 GB | `models/unet_gguf/` |
| FLUX.1-schnell Q8_0 (alt) | `city96/FLUX.1-schnell-gguf` | `flux1-schnell-Q8_0.gguf` | 12.7 GB | `models/unet_gguf/` |
| Model | HuggingFace | Filename | Size | Path |
|-------|------------|----------|------|------|
| CLIP-L | `comfyanonymous/flux_text_encoders` | `clip_l.safetensors` | ~246 MB | `models/clip/` |
| T5-XXL (GGUF Q8) | `city96/t5-v1_1-xxl-encoder-gguf` | `t5-v1_1-xxl-encoder-Q8_0.gguf` | 5.06 GB | `models/clip_gguf/` |
| Model | HuggingFace | Filename | Size | Path |
|-------|------------|----------|------|------|
| FLUX VAE | `black-forest-labs/FLUX.1-schnell` | `ae.safetensors` | ~168 MB | `models/vae/` |
### Core Nodes Also Required (built into ComfyUI)
| Core Node | Purpose |
|-----------|---------|
| `KSampler` or `KSamplerAdvanced` | Sampling/denoising |
| `EmptyLatentImage` | Latent space initialization |
| `CLIPTextEncode` | Prompt encoding (uses CLIP output from GGUF loader) |
| `VAEDecode` | Latent-to-image decoding |
| `SaveImage` or `PreviewImage` | Output |
### Template Recommendation
### Cloud Compatibility -- CRITICAL WARNING
| Concern | Status | Impact |
|---------|--------|--------|
| GGUF format in templates | NOT in official templates yet | Open issue #11819 requesting GGUF templates |
| `.gguf` model safety display | Models shown as "unsafe" in template UI | Won't auto-show download links for GGUF files |
| Pack in registry | YES (`ComfyUI-GGUF` on registry.comfy.org) | Pack installs fine |
| Cloud model availability | UNKNOWN | GGUF models may not be pre-cached on Comfy Cloud |
## Template 3: ComfyUI Impact Pack -- Face Detection + Auto-Detailing
### Custom Node Packs (TWO packs required)
| Field | Value |
|-------|-------|
| Registry ID | `comfyui-impact-pack` |
| GitHub | `ltdrdata/ComfyUI-Impact-Pack` |
| Publisher | ltdrdata |
| Downloads | ~2.37M |
| Stars | ~3K |
| Python deps | `segment-anything`, `scikit-image`, `piexif`, `transformers`, `opencv-python-headless`, `GitPython`, `scipy>=1.11.4`, `numpy`, `dill`, `matplotlib`, `sam2` (from GitHub) |
| Field | Value |
|-------|-------|
| Registry ID | `comfyui-impact-subpack` |
| GitHub | `ltdrdata/ComfyUI-Impact-Subpack` |
| Publisher | ltdrdata |
| Python deps | `ultralytics` (YOLO framework) |
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
| Model | Source | Filename | Size | Path |
|-------|--------|----------|------|------|
| Face YOLOv8m | HuggingFace (Bingsu/adetailer) | `face_yolov8m.pt` | ~50 MB | `models/ultralytics/bbox/` |
| Model | Source | Filename | Size | Path |
|-------|--------|----------|------|------|
| SAM ViT-B | Facebook Research | `sam_vit_b_01ec64.pth` | ~375 MB | `models/sams/` |
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
### Cloud Compatibility
| Concern | Status | Impact |
|---------|--------|--------|
| Impact Pack in registry | YES | Installs via registry |
| Impact Subpack in registry | YES | Installs via registry |
| Two-pack dependency | Must declare BOTH in `requiresCustomNodes` | Easy to miss the Subpack |
| SAM model auto-download | YES (install.py auto-downloads to `models/sams/`) | Works on cloud |
| YOLO model | NOT auto-downloaded | Must be manually placed or downloaded via ComfyUI-Manager |
| `.pt` model format | PyTorch format, may trigger safety warnings in newer PyTorch | Impact Subpack has `model-whitelist.txt` for this |
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
### Cloud Compatibility
| Concern | Status | Impact |
|---------|--------|--------|
| Pack in registry | YES (publisher: kijai) | Installs via registry |
| Model format | `.safetensors` | Safe format, will display download links |
| Model size | 456 MB (fp16) | Reasonable download |
| Audio I/O | Requires ComfyUI audio node support | ComfyUI has native `LoadAudio`/`SaveAudio` nodes (added ~2024) |
| Risk | Audio templates are less common in the library | May need extra testing to verify audio pipeline works end-to-end on cloud |
## Cross-Template Dependencies
### Shared Dependencies
| Dependency | Used By | Notes |
|------------|---------|-------|
| `transformers` | Florence2, Impact Pack | Both need HuggingFace transformers; version ranges should be compatible |
| `torch` / `torchvision` | All 4 | Provided by ComfyUI runtime, not declared by packs |
| `numpy` | Impact Pack, MelBandRoFormer (via einops) | Universal, no conflicts |
### No Inter-Template Dependencies
### Pack Install Summary
| Template | Custom Packs Required | Total Model Download |
|----------|----------------------|---------------------|
| Florence2 | 1 (`comfyui-florence2`) | ~1.5 GB |
| GGUF FLUX | 1 (`ComfyUI-GGUF`) | ~12 GB (Q4_K_S UNET + Q8 T5 + CLIP-L + VAE) |
| Impact Pack | 2 (`comfyui-impact-pack` + `comfyui-impact-subpack`) | ~4.6 GB (checkpoint + SAM + YOLO) |
| MelBandRoFormer | 1 (`comfyui-melbandroformer`) | ~456 MB |
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
## Template index.json Model Metadata Format
| Template | directory values |
|----------|-----------------|
| Florence2 | `LLM` |
| GGUF FLUX | `unet_gguf`, `clip_gguf`, `clip`, `vae` |
| Impact Pack | `checkpoints`, `sams`, `ultralytics/bbox` |
| MelBandRoFormer | `diffusion_models` |
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
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
