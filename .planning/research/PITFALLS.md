# Domain Pitfalls: v2.0 Template Batch

**Domain:** ComfyUI workflow template creation for 4 specific node packs
**Researched:** 2026-03-25
**Overall confidence:** MEDIUM-HIGH
**Scope:** Pitfalls specific to creating production-ready templates for ComfyUI-Florence2, ComfyUI-GGUF, ComfyUI Impact Pack, and ComfyUI-MelBandRoFormer

---

## Critical Pitfalls

Mistakes that cause template rejection, rewrite, or cloud failure.

### Pitfall 1: GGUF Format Blocked by Template Model Embedding System

**What goes wrong:** The ComfyUI template system's model embedding feature (which allows users to auto-download models when loading a template) explicitly treats `.gguf` files as "unsafe." When a GGUF model URL is embedded in a node's `properties.models`, it "will be flagged as unsafe and the link will not be shown" to the user. This means the GGUF template cannot use the standard model auto-download mechanism that every other template relies on.

**Why it happens:** The template system only accepts "safe" formats (`.safetensors`, `.sft`). The `.gguf` format, while perfectly functional, is classified as unsafe by the template embedding policy. This is a policy decision in the ComfyUI template system, not a technical limitation.

**Consequences:** Users who load the GGUF template will NOT get an automatic model download prompt. They must manually find, download, and place GGUF model files into `ComfyUI/models/unet` before the workflow can run. This is a significantly worse UX than other templates and may cause the template to fail review.

**Affects:** ComfyUI-GGUF template exclusively.

**Prevention:**
- Document the manual model download step prominently in the template description and Notion submission
- Consider whether a `.safetensors` fallback workflow makes more sense for the template (defeats the purpose of GGUF though)
- Investigate if the template can reference the T5/CLIP text encoder models in `.safetensors` (which CAN be auto-downloaded) while only requiring manual placement of the GGUF UNET
- In the index.json metadata, explicitly note that this template requires manual model setup
- Add a Note node in the workflow explaining where to get the GGUF model file

**Warning signs:**
- Template passes validation but fails user testing because models are not auto-downloaded
- Review feedback: "models not found on load"

**Detection:** Validator should flag any template using `UnetLoaderGGUF` and warn about the model embedding limitation.

**Confidence:** HIGH -- verified directly from [ComfyUI template docs](https://docs.comfy.org/interface/features/template) which state ".gguf are considered unsafe."

---

### Pitfall 2: Impact Pack Requires TWO Node Packs (Subpack Dependency)

**What goes wrong:** The FaceDetailer workflow requires `UltralyticsDetectorProvider` to load the face detection model (e.g., `face_yolov8m.pt`). This node does NOT exist in ComfyUI-Impact-Pack itself -- it lives in the separate [ComfyUI-Impact-Subpack](https://github.com/ltdrdata/ComfyUI-Impact-Subpack). Creating a FaceDetailer template that references `UltralyticsDetectorProvider` without declaring the Subpack dependency means the template breaks for any user who only installs Impact Pack.

**Why it happens:** The Impact Pack split its YOLO/Ultralytics detection into a separate "Subpack" because it has a heavy `ultralytics` pip dependency. The main Impact Pack provides the `FaceDetailer` node, but the detection model loading is delegated to the Subpack. This is a non-obvious split -- most tutorials and references describe "Impact Pack" as a single entity.

**Consequences:** Users install Impact Pack, load the template, and get "Node type not found: UltralyticsDetectorProvider" error. The template appears broken even though the user followed the stated dependencies.

**Affects:** ComfyUI Impact Pack template.

**Prevention:**
- List BOTH `ComfyUI-Impact-Pack` AND `ComfyUI-Impact-Subpack` in `requiresCustomNodes` metadata
- In the template description, explicitly state both packs are needed
- Add a Note node in the workflow explaining: "Requires Impact Pack + Impact Subpack"
- The YOLO model file must go in `ComfyUI/models/ultralytics/bbox/face_yolov8m.pt` -- embed this path clearly
- Consider using `ONNXDetectorProvider` from the main Impact Pack as an alternative (but YOLO is more accurate)

**Warning signs:**
- Template validates (node types check out against specs) but fails at runtime because Subpack is missing
- Custom node list in metadata only mentions Impact Pack

**Detection:** The validator's `check_core_node_preference` rule will flag custom nodes, but it won't distinguish between "installed via Impact Pack" and "requires separate Subpack install." Add a special case for `UltralyticsDetectorProvider` -> warn about Subpack requirement.

**Confidence:** HIGH -- verified from [Impact-Subpack repo](https://github.com/ltdrdata/ComfyUI-Impact-Subpack) which confirms UltralyticsDetectorProvider is exclusively in the Subpack.

---

### Pitfall 3: Florence2 Model Auto-Download During Template Load

**What goes wrong:** The `DownloadAndLoadFlorence2Model` node downloads models from Hugging Face at runtime (2-7 GB per model variant). On first use, this triggers a multi-GB download that can take several minutes. On Comfy Cloud, this download happens on every cold start unless the model is pre-cached. The template appears to "hang" or "fail" when it's actually just downloading.

**Why it happens:** Florence2 uses a custom download-and-load pattern rather than ComfyUI's standard model loader path. Models go to `ComfyUI/models/LLM`, not the standard `checkpoints` or `diffusion_models` directories. The `DownloadAndLoadFlorence2Model` node handles its own HuggingFace download logic, bypassing the template model embedding system entirely.

**Consequences:**
- First-time users wait 2-10 minutes with no progress feedback
- On cloud: cold starts incur download time every time (unless cached)
- Cloud GPU billing accumulates during download (not during inference)
- Model size varies by variant: `florence-2-base` ~0.5GB, `florence-2-large` ~1.5GB, `florence-2-large-ft` ~1.5GB
- Using `florence-2-large` with `fp32` requires 16GB+ VRAM

**Affects:** ComfyUI-Florence2 template.

**Prevention:**
- Default the template to `florence-2-base-ft` (best quality-to-size ratio for general use)
- Set precision to `fp16` (not `fp32`) to halve VRAM usage
- Set attention to `sdpa` (widest compatibility, no special hardware needed)
- Add a Note node: "First run downloads ~1GB model. Subsequent runs use cache."
- In Notion submission, document the download behavior and expected wait time
- Set `keep_model_loaded: True` if the template runs Florence2 multiple times
- Consider using `Florence2ModelLoader` (loads from local path) instead of `DownloadAndLoadFlorence2Model` -- this allows embedding the model in template properties for auto-download, IF the model is in `.safetensors` format

**Warning signs:**
- Template times out on cloud testing
- User reports "workflow stuck" -- actually downloading
- VRAM OOM errors when using `large` variant with `fp32`

**Detection:** Check the Florence2 loader node's widget values for precision and model variant. Flag `fp32` + `large` combo as high-VRAM risk.

**Confidence:** HIGH -- verified from [Florence2 memory management docs](https://deepwiki.com/kijai/ComfyUI-Florence2/7.1-memory-management) and [node documentation](https://deepwiki.com/kijai/ComfyUI-Florence2).

---

### Pitfall 4: Audio Nodes Missing from core_nodes.json (Stale Core List)

**What goes wrong:** The project's `data/core_nodes.json` does NOT include `LoadAudio` or `SaveAudio`, even though these are built-in ComfyUI core nodes (in `comfy_extras/nodes_audio.py`). The MelBandRoFormer template needs `LoadAudio` for input and `SaveAudio` for output. When the template is validated, these core audio nodes will be incorrectly flagged as "custom nodes" by `check_core_node_preference`, producing spurious warnings.

**Why it happens:** The `core_nodes.json` was generated at a point when audio nodes were not yet added to ComfyUI core, or the generation script missed `comfy_extras/` nodes. The validate gotchas doc already notes: "ComfyUI adds new core nodes regularly. If a known core node gets flagged as custom, run `python scripts/update_core_nodes.py` to refresh."

**Consequences:**
- MelBandRoFormer template validation produces false-positive warnings about `LoadAudio`/`SaveAudio`
- The `requiresCustomNodes` metadata in index.json incorrectly lists `LoadAudio`/`SaveAudio` as dependencies
- The metadata generation (`_detect_custom_nodes`) will include audio nodes in the custom node list
- The `_detect_media_type` function in `metadata.py` checks for `SaveAudio` to detect audio media type -- this works correctly, but the custom node detection runs separately and contradicts it

**Affects:** ComfyUI-MelBandRoFormer template directly. Also affects any future audio template.

**Prevention:**
- Update `core_nodes.json` BEFORE building any templates -- add at minimum: `LoadAudio`, `SaveAudio`, `EmptyLatentAudio`, `StableAudioSampler`, `StableAudioConditioning`
- Run `python scripts/update_core_nodes.py` or manually add the audio nodes
- After updating, verify that validation no longer flags `LoadAudio`/`SaveAudio`

**Warning signs:**
- Validation output includes "Custom node 'LoadAudio' -- not a core node"
- Generated index.json lists LoadAudio/SaveAudio in requiresCustomNodes

**Detection:** Run validation on any workflow containing `LoadAudio` -- if it flags as custom, the core list is stale.

**Confidence:** HIGH -- verified by searching `core_nodes.json` (no audio nodes present) and confirming [LoadAudio is in core ComfyUI](https://github.com/comfyanonymous/ComfyUI/blob/master/comfy_extras/nodes_audio.py).

---

### Pitfall 5: MelBandRoFormer Models Live in diffusion_models, Not a Custom Path

**What goes wrong:** The MelBandRoFormer model loader uses `folder_paths.get_filename_list("diffusion_models")` -- meaning models must be in `ComfyUI/models/diffusion_models/`. This is the SAME directory used by Flux, SD3, and other diffusion UNET models. If the template embeds a model download pointing to this directory, the model file (`MelBandRoformer_fp16.safetensors`, ~456MB) gets mixed in with all the user's diffusion models. More critically, users may not realize to place the audio model here because "diffusion_models" sounds like it's only for image generation models.

**Why it happens:** MelBandRoFormer reuses an existing ComfyUI folder path rather than registering a custom model directory. This is a pragmatic choice by the node author but creates confusion.

**Consequences:**
- Users download the model but put it in `models/audio/` or another intuitive location -- workflow fails with "model not found"
- The shared `diffusion_models` directory becomes cluttered with unrelated model types
- Template model embedding uses `"directory": "diffusion_models"` which is technically correct but semantically confusing

**Affects:** ComfyUI-MelBandRoFormer template.

**Prevention:**
- In the template, add a Note node specifying: "Model goes in ComfyUI/models/diffusion_models/"
- Use the exact model filename in the template's widgets_values: `MelBandRoformer_fp16.safetensors`
- Embed the model in node properties with: `"directory": "diffusion_models"`, `"url": "https://huggingface.co/Kijai/MelBandRoFormer_comfy/resolve/main/MelBandRoformer_fp16.safetensors"` -- the model IS `.safetensors` so it CAN be auto-downloaded via the template system
- In Notion docs, explain the directory choice

**Warning signs:**
- User reports "model not found" despite having downloaded it
- Model dropdown in the node doesn't show the MelBandRoFormer model

**Confidence:** HIGH -- verified from [nodes.py source](https://github.com/kijai/ComfyUI-MelBandRoFormer/blob/main/nodes.py) which uses `folder_paths.get_filename_list("diffusion_models")`.

---

## Moderate Pitfalls

### Pitfall 6: Florence2 Task-Specific Text Input Constraint

**What goes wrong:** The `Florence2Run` node's `text_input` field is only used by 3 of the 14 tasks: `referring_expression_segmentation`, `caption_to_phrase_grounding`, and `docvqa`. For all other tasks (captioning, OCR, region proposals), the text_input is silently ignored. Template creators who set a descriptive text_input for a captioning task create a misleading template -- users think they're providing a prompt, but it has no effect.

**Why it happens:** Florence2 is a multi-task model where most tasks are unconditional (no text prompt needed). The node accepts text_input as a universal parameter but only forwards it to tasks that support prompts. There's no validation or warning when text_input is provided to a non-prompt task.

**Affects:** ComfyUI-Florence2 template.

**Prevention:**
- Match the task type to the text_input presence:
  - Tasks that USE text_input: `referring_expression_segmentation`, `caption_to_phrase_grounding`, `docvqa`
  - Tasks that IGNORE text_input: `caption`, `detailed_caption`, `more_detailed_caption`, `region_caption`, `dense_region_caption`, `region_proposal`, `ocr`, `ocr_with_region`, `prompt_gen_*`
- For the template, choose a task that demonstrates value clearly: `more_detailed_caption` (unconditional) or `caption_to_phrase_grounding` (uses text input)
- Add a Note node explaining which tasks accept text input

**Warning signs:**
- Template has text_input connected/set but task is `caption` -- the input does nothing
- User changes the text and sees no change in output

**Confidence:** HIGH -- documented in [Florence2 node analysis](https://deepwiki.com/kijai/ComfyUI-Florence2/4.2-florence2run-node).

---

### Pitfall 7: Impact Pack Version Instability and Parameter Drift

**What goes wrong:** ComfyUI Impact Pack has a history of breaking changes where "when a new parameter is created in an update, the values of nodes created in the previous version can be shifted to different fields." Between versions 2.22 and 2.21, there was partial compatibility loss. Version 8.19 removed legacy mmdet nodes entirely. Version 4.20.1 changed RegionalSampler parameter ordering. The template we build today may break on Impact Pack's next update.

**Why it happens:** Impact Pack is one of the most actively developed custom node packs (3K+ stars, frequent updates). New features (wildcard support, DETAILER_PIPE changes) alter the node interface. The maintainer ships breaking changes with version bumps but users auto-update.

**Consequences:**
- Template FaceDetailer widget values shift positions after user updates Impact Pack
- New required parameters appear that the template doesn't include
- Template loads but produces wrong results because parameter positions shifted

**Affects:** ComfyUI Impact Pack template.

**Prevention:**
- Pin the Impact Pack version in template documentation ("Tested with Impact Pack v8.24+")
- Use FaceDetailer rather than FaceDetailerPipe (the basic version changes less often)
- Set ALL widget values explicitly -- don't rely on defaults that may change
- Keep the FaceDetailer configuration simple: avoid advanced features like wildcard processing or detailer hooks that are more likely to change
- After composing, test with the latest Impact Pack version to confirm compatibility

**Warning signs:**
- FaceDetailer has more input slots than expected
- Widget values array length doesn't match current node spec
- "MASKS" vs "MASK" naming conflicts (changed in v4.12)

**Detection:** Compare widget_values array length against the MCP-fetched node spec. Mismatch = version drift.

**Confidence:** MEDIUM -- based on [Impact Pack changelog](https://github.com/ltdrdata/ComfyUI-Impact-Pack) and [community reports](https://github.com/ltdrdata/ComfyUI-Impact-Pack/issues/1080). Future breaking changes are unpredictable.

---

### Pitfall 8: GGUF Node Category Is "bootleg" -- Confuses Template Organization

**What goes wrong:** All ComfyUI-GGUF nodes register under the `"bootleg"` category in ComfyUI's node menu. This non-standard category name makes it harder for users to find the nodes and creates confusion about whether they're "official." In a template context, this also means the nodes won't appear under standard categories like "loaders" that users typically browse.

**Why it happens:** The GGUF pack author chose "bootleg" as a self-deprecating category name during the WIP phase. The name has persisted through production use.

**Affects:** ComfyUI-GGUF template.

**Prevention:**
- In template notes, explain that GGUF nodes are under the "bootleg" category
- Use exact node type names in documentation: `UnetLoaderGGUF`, `DualCLIPLoaderGGUF`
- This is cosmetic -- doesn't affect functionality, but documentation should address it

**Confidence:** HIGH -- verified from [GGUF documentation](https://deepwiki.com/city96/ComfyUI-GGUF).

---

### Pitfall 9: FaceDetailer Thread Limiting After Execution

**What goes wrong:** A documented issue reports that after running FaceDetailer, subsequent generation processes use fewer CPU cores (8 instead of all available) and take 2-3x longer. This persists until ComfyUI is restarted. On cloud, this means the template execution could degrade performance for subsequent workflows in the same session.

**Why it happens:** FaceDetailer's internal detection process (YOLO inference) may set thread limits via PyTorch or OpenMP that persist in the process environment after the node completes.

**Affects:** ComfyUI Impact Pack template, especially on cloud where sessions are shared.

**Prevention:**
- Document this as a known behavior in the template notes
- On cloud: this is less of an issue since cloud sessions are typically isolated
- Keep the FaceDetailer workflow simple to minimize the impact window
- This is an upstream bug -- cannot be fixed in the template itself

**Warning signs:**
- Subsequent workflow runs are noticeably slower after running the FaceDetailer template
- CPU utilization drops after FaceDetailer execution

**Confidence:** MEDIUM -- based on [community report](https://github.com/ltdrdata/ComfyUI-Impact-Pack/issues/1097). May be fixed in newer versions.

---

### Pitfall 10: GGUF Architecture Mismatch for SD1/SDXL Models

**What goes wrong:** GGUF quantization works well with transformer/DiT architectures (Flux, SD3) but is problematic for conv2d architectures (SD1, SDXL). Conv2d models require `shape_fix=True` and higher quantization levels (Q8_0+). If the template defaults to a low quantization like Q4_K_S on an SDXL model, the output quality degrades significantly.

**Why it happens:** "While quantization wasn't feasible for regular UNET models (conv2d), transformer/DiT models such as flux seem less affected by quantization." The GGUF pack supports both but the quality tradeoffs differ dramatically.

**Affects:** ComfyUI-GGUF template.

**Prevention:**
- Target the template at Flux (transformer/DiT) architecture, not SDXL or SD1
- Recommend Q4_K_S or Q5_K_S quantization for the Flux GGUF model
- Document recommended quantization levels in the template notes
- Use `UnetLoaderGGUF` for simple loading; only use `UnetLoaderGGUFAdvanced` if architecture override is needed

**Warning signs:**
- Template uses SDXL GGUF model at Q4 quantization -- output will be noticeably degraded
- User reports "blurry" or "artifacted" results

**Confidence:** HIGH -- verified from [GGUF documentation](https://deepwiki.com/city96/ComfyUI-GGUF).

---

### Pitfall 11: MelBandRoFormer Stereo/Mono Audio Mismatch

**What goes wrong:** The MelBandRoFormer sampler expects stereo audio input. If the user provides mono audio, the node may fail or produce poor separation results. The node can resample to the correct sample rate, but mono-to-stereo conversion is not automatic.

**Why it happens:** The underlying model was trained on stereo audio and expects 2-channel input. ComfyUI's `LoadAudio` node loads whatever format the file is in -- it doesn't convert mono to stereo.

**Affects:** ComfyUI-MelBandRoFormer template.

**Prevention:**
- Add a Note node: "Input audio must be stereo. Mono audio may produce errors or poor results."
- In the template description, specify "stereo audio input required"
- Consider whether a mono-to-stereo conversion node should be part of the template pipeline (if one exists as a core node)

**Warning signs:**
- Template works with test audio but fails with user-provided mono files
- Separation quality is unexpectedly poor

**Confidence:** MEDIUM -- based on [MelBandRoFormer documentation](https://www.runcomfy.com/comfyui-nodes/ComfyUI-MelBandRoFormer/mel-band-ro-former-sampler). Exact mono handling behavior needs cloud testing.

---

## Minor Pitfalls

### Pitfall 12: Florence2 Transformers Version Pinning

**What goes wrong:** ComfyUI-Florence2 requires `transformers >= 4.39.0` but explicitly excludes version `4.50.*` due to compatibility issues. If the cloud environment has an incompatible transformers version, the Florence2 node fails to load.

**Affects:** ComfyUI-Florence2 template (cloud only).

**Prevention:** This is a cloud infrastructure concern, not a template authoring issue. Document the version requirement. If cloud testing fails, check transformers version first.

**Confidence:** HIGH -- verified from [pyproject.toml](https://github.com/kijai/ComfyUI-Florence2/blob/main/pyproject.toml).

---

### Pitfall 13: GGUF Loader Not Discoverable via Standard Search

**What goes wrong:** When using the MCP `search_nodes` to find GGUF loaders, the "bootleg" category and non-standard naming may cause the nodes to not surface in standard searches. The node type name `UnetLoaderGGUF` is close to the core `UNETLoader` but they are fundamentally different.

**Affects:** ComfyUI-GGUF template (composition phase).

**Prevention:**
- Use exact node type names when searching: `UnetLoaderGGUF`, `DualCLIPLoaderGGUF`, `TripleCLIPLoaderGGUF`, `CLIPLoaderGGUF`, `UnetLoaderGGUFAdvanced`
- Do not confuse core `UNETLoader` with `UnetLoaderGGUF` -- they have different model directory expectations
- Note the casing difference: core is `UNETLoader` (all caps UNET), GGUF is `UnetLoaderGGUF` (mixed case)

**Confidence:** MEDIUM -- based on naming analysis; actual MCP search behavior needs testing.

---

### Pitfall 14: Florence2Run Has 4 Outputs But Templates Usually Need 1-2

**What goes wrong:** `Florence2Run` returns a 4-tuple: `(IMAGE, MASK, STRING, JSON)`. The specific outputs populated depend on the task:
- Captioning tasks: only STRING output is useful
- Segmentation tasks: IMAGE and MASK outputs are useful
- OCR: STRING output
- Grounding: IMAGE output with bounding boxes drawn

Template creators who connect all 4 outputs create confusing workflows with dangling connections for outputs that are empty for the selected task.

**Affects:** ComfyUI-Florence2 template.

**Prevention:**
- Only connect the outputs relevant to the chosen task
- Add a Note node explaining which outputs are active for the task
- For a captioning template: connect STRING output to a display/note
- For a segmentation template: connect IMAGE and MASK outputs

**Confidence:** HIGH -- verified from [Florence2 node specs](https://deepwiki.com/kijai/ComfyUI-Florence2/4.2-florence2run-node).

---

### Pitfall 15: Impact Pack FaceDetailer SAM Model Is Optional But Improves Quality

**What goes wrong:** FaceDetailer has an optional `sam_model_opt` input. Without SAM, FaceDetailer uses only the BBOX detector's rectangular region -- the enhanced face area has hard rectangular boundaries that can show visible seams. With SAM, the face is precisely segmented before enhancement, producing much cleaner results. Templates that skip the SAM model produce noticeably worse output.

**Affects:** ComfyUI Impact Pack template.

**Prevention:**
- Include SAM model loading (`SAMLoader`) in the template for best results
- Use `sam_vit_b_01ec64.pth` (smallest SAM variant, ~375MB) for the template default
- SAM model path: `ComfyUI/models/sams/sam_vit_b_01ec64.pth`
- Embed the SAM model in template properties for auto-download (it's `.pth` format -- check if this is considered "safe" by template system; `.pth` may also be flagged as unsafe like `.gguf`)

**Warning signs:**
- Face enhancement has visible rectangular seam borders
- Quality significantly worse than tutorials that include SAM

**Confidence:** MEDIUM-HIGH -- based on [FaceDetailer documentation](https://www.runcomfy.com/comfyui-nodes/ComfyUI-Impact-Pack/FaceDetailer) and [community guides](https://mybyways.com/blog/improving-faces-with-impact-pack-detailers).

---

## Validation Rule Conflicts

| Template | Validation Rule | Expected Behavior | Actual Behavior | Fix |
|----------|----------------|-------------------|-----------------|-----|
| ALL 4 | `core_node_preference` | Flags custom nodes as warning | Correctly flags all pack-specific nodes | Suppress warning severity for templates intentionally showcasing custom node packs |
| MelBandRoFormer | `core_node_preference` | Should NOT flag `LoadAudio`/`SaveAudio` | WILL flag them as custom (stale core list) | Update `core_nodes.json` with audio nodes |
| ALL 4 | `cloud_compatible` | Info reminder | Correct, but all 4 need actual cloud testing | No code fix -- operational requirement |
| Impact Pack | `check_core_node_preference` | Flags FaceDetailer, UltralyticsDetectorProvider | Correct behavior | Expected -- these are intentionally custom |
| GGUF | metadata `_detect_models` | Should detect GGUF model file | May NOT detect `.gguf` extension | `_detect_models` checks for `.safetensors`, `.ckpt`, `.pt`, `.pth`, `.bin` but NOT `.gguf` -- needs extension |

---

## Model Size and Download Concerns

| Template | Model(s) | Size | Format | Auto-Download? | Directory |
|----------|----------|------|--------|----------------|-----------|
| Florence2 | florence-2-base-ft | ~1GB | HF auto-download | Node handles it (bypasses template system) | `models/LLM` |
| Florence2 | florence-2-large-ft | ~1.5GB | HF auto-download | Node handles it (bypasses template system) | `models/LLM` |
| GGUF | flux1-dev-Q4_K_S.gguf | ~6GB | `.gguf` | NO -- unsafe format, blocked | `models/unet` |
| GGUF | T5 text encoder (GGUF) | ~5GB | `.gguf` | NO -- unsafe format, blocked | `models/clip` |
| GGUF | CLIP-L (safetensors) | ~250MB | `.safetensors` | YES | `models/clip` |
| Impact Pack | face_yolov8m.pt | ~6MB | `.pt` | Possibly -- `.pt` may be flagged unsafe | `models/ultralytics/bbox` |
| Impact Pack | sam_vit_b_01ec64.pth | ~375MB | `.pth` | Possibly -- `.pth` may be flagged unsafe | `models/sams` |
| Impact Pack | SD/SDXL checkpoint | ~2-7GB | `.safetensors` | YES | `models/checkpoints` |
| MelBandRoFormer | MelBandRoformer_fp16.safetensors | ~456MB | `.safetensors` | YES | `models/diffusion_models` |

**Key insight:** Only MelBandRoFormer and Impact Pack's checkpoint have fully auto-downloadable models via the template system. Florence2 handles its own downloads. GGUF is entirely blocked. Impact Pack's detection models (`.pt`, `.pth`) need testing to confirm template embedding support.

---

## Cloud Compatibility Matrix

| Template | Cloud Risk | Primary Concern | Mitigation |
|----------|-----------|-----------------|------------|
| Florence2 | MEDIUM | First-run model download (1-1.5GB) adds to cold start time | Use `base-ft` variant, `fp16` precision, document wait time |
| GGUF | HIGH | `.gguf` models can't be auto-provisioned; manual upload required | Document manual model placement, or investigate if cloud pre-caches popular GGUF models |
| Impact Pack | MEDIUM | Subpack must be installed; YOLO model must be in correct subdirectory | Ensure both packs in registry; embed model if `.pt` embedding works |
| MelBandRoFormer | LOW | Model is `.safetensors`, auto-downloadable; audio processing is lightweight | Straightforward cloud deployment; document stereo input requirement |

---

## Phase-Specific Warnings

| Phase/Task | Likely Pitfall | Mitigation | Affected Template |
|------------|---------------|------------|-------------------|
| Pre-composition setup | Stale core_nodes.json missing audio nodes | Update core list before any template work | MelBandRoFormer |
| Pre-composition setup | `_detect_models` missing `.gguf` extension | Add `.gguf` to model extension list in `metadata.py` | GGUF |
| Composition | GGUF text encoder selection (T5 vs CLIP vs Dual) | Use `DualCLIPLoaderGGUF` for Flux (needs T5 + CLIP-L) | GGUF |
| Composition | Florence2 task selection affects which outputs to wire | Match outputs to task type; don't wire unused outputs | Florence2 |
| Composition | FaceDetailer has 15+ inputs -- easy to miss required ones | Use MCP node spec to enumerate all required inputs | Impact Pack |
| Validation | All templates trigger `core_node_preference` warnings | Expected -- suppress or lower severity for intentional custom node templates | ALL |
| Validation | Impact Pack template only lists 1 of 2 required packs | Explicitly check for Subpack requirement | Impact Pack |
| Model embedding | GGUF format blocked by template system | Document manual setup; explore partial safetensors embedding | GGUF |
| Model embedding | Impact Pack `.pt`/`.pth` models may be blocked | Test template embedding with `.pt` format; fallback to manual docs | Impact Pack |
| Documentation | GGUF needs extra setup instructions vs other templates | More detailed Notion submission with model installation guide | GGUF |
| Cloud testing | Florence2 cold start downloads are slow | Budget extra time; use smallest viable model variant | Florence2 |
| Cloud testing | GGUF models must be manually provisioned | Test with pre-placed models; document for reviewers | GGUF |

---

## Code Changes Required Before Template Composition

These are NOT template issues -- they're tooling gaps in the existing codebase that will cause problems for this milestone.

1. **Update `data/core_nodes.json`:** Add `LoadAudio`, `SaveAudio`, `EmptyLatentAudio`, `StableAudioSampler`, `StableAudioConditioning`, and any other audio-related core nodes. Without this, MelBandRoFormer template validation will produce false positives.

2. **Extend `_detect_models` in `src/document/metadata.py`:** Add `.gguf` to the `model_extensions` tuple. Currently: `(".safetensors", ".ckpt", ".pt", ".pth", ".bin")`. Without this, GGUF template metadata won't list the GGUF model files.

3. **Add audio output node to `_OUTPUT_TYPES` in `metadata.py`:** `SaveAudio` is already handled by `_detect_media_type`, but `_OUTPUT_TYPES` dict (used for IO spec extraction) doesn't include it. Add `"SaveAudio": "audio"` and `"LoadAudio": "audio"` to `_INPUT_TYPES`.

4. **Consider adding `_INPUT_TYPES` entry for Florence2 loader:** `DownloadAndLoadFlorence2Model` and `Florence2ModelLoader` are model loaders but don't match the `"Load" in node_type` heuristic in `_detect_models` because they use HuggingFace repo names, not file paths.

---

## Sources

- [ComfyUI Template System Docs](https://docs.comfy.org/interface/features/template) -- Model embedding rules, unsafe format policy (HIGH confidence)
- [ComfyUI-GGUF GitHub](https://github.com/city96/ComfyUI-GGUF) -- Node types, architecture support, known issues (HIGH confidence)
- [ComfyUI-GGUF DeepWiki](https://deepwiki.com/city96/ComfyUI-GGUF) -- Quantization levels, VRAM savings (HIGH confidence)
- [ComfyUI-Florence2 GitHub](https://github.com/kijai/ComfyUI-Florence2) -- Node types, model requirements (HIGH confidence)
- [Florence2 Memory Management](https://deepwiki.com/kijai/ComfyUI-Florence2/7.1-memory-management) -- VRAM by model size (HIGH confidence)
- [Florence2 Node Analysis](https://deepwiki.com/kijai/ComfyUI-Florence2/4-florence2-nodes) -- Task types, input constraints (HIGH confidence)
- [ComfyUI-Impact-Pack GitHub](https://github.com/ltdrdata/ComfyUI-Impact-Pack) -- FaceDetailer, breaking changes (HIGH confidence)
- [ComfyUI-Impact-Subpack GitHub](https://github.com/ltdrdata/ComfyUI-Impact-Subpack) -- UltralyticsDetectorProvider location (HIGH confidence)
- [FaceDetailer Documentation](https://www.runcomfy.com/comfyui-nodes/ComfyUI-Impact-Pack/FaceDetailer) -- Required inputs, SAM model (MEDIUM-HIGH confidence)
- [ComfyUI-MelBandRoFormer GitHub](https://github.com/kijai/ComfyUI-MelBandRoFormer) -- Node types, model path (HIGH confidence)
- [MelBandRoFormer HuggingFace](https://huggingface.co/Kijai/MelBandRoFormer_comfy) -- Model files, sizes (HIGH confidence)
- [ComfyUI Core Audio Nodes](https://github.com/comfyanonymous/ComfyUI/blob/master/comfy_extras/nodes_audio.py) -- LoadAudio/SaveAudio are core (HIGH confidence)
- [Impact Pack Thread Issue](https://github.com/ltdrdata/ComfyUI-Impact-Pack/issues/1097) -- FaceDetailer thread limiting (MEDIUM confidence)
- [ComfyUI Workflow Templates README](https://github.com/Comfy-Org/workflow_templates/blob/main/README.md) -- Submission requirements, index.json schema (HIGH confidence)

---
*Pitfalls research for: v2.0 Template Batch -- 4 node pack templates*
*Researched: 2026-03-25*
