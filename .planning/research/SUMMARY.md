# Project Research Summary

**Project:** ComfyUI Template Agent v2.0 -- Template Batch (4 Trending Node Packs)
**Domain:** ComfyUI workflow template creation for high-download custom node packs
**Researched:** 2026-03-25
**Confidence:** HIGH

## Executive Summary

This v2.0 milestone produces four production-ready ComfyUI workflow templates targeting node packs with zero current coverage in the template library: ComfyUI-Florence2 (1.25M downloads, vision AI), ComfyUI-GGUF (1.69M downloads, quantized diffusion), ComfyUI Impact Pack (2.37M downloads, face detailing), and ComfyUI-MelBandRoFormer (240K downloads, audio separation). All node class names, model paths, and API surfaces were verified against GitHub source code and HuggingFace model repos -- the technical specification is solid. Critically, no new Python code is required: the existing v1.0 toolkit (WorkflowGraph, validator, document generators) handles all four templates without modification. The work is composition and documentation, not engineering.

The recommended approach is sequential template composition in ascending complexity order: MelBandRoFormer (5 nodes, linear) -> Florence2 (6 nodes, multi-output) -> GGUF (9 nodes, standard pipeline) -> Impact Pack FaceDetailer (11 nodes, fan-out from checkpoint). This order validates the compose-validate-document pipeline against progressively harder graphs and surfaces any tooling gaps before tackling the most complex workflow. Each template is fully independent -- no inter-template dependencies exist -- so the order is a pragmatic complexity ladder, not a functional requirement.

The primary risks are two required tooling fixes that must precede any template composition, and the GGUF cloud deployment problem (`.gguf` files are blocked by the ComfyUI template model embedding safety policy). The GGUF template can still be submitted with manual model installation documentation, but it will not benefit from auto-download like the other three. Impact Pack also requires declaring two separate node packs in metadata (`comfyui-impact-pack` + `comfyui-impact-subpack`) -- missing the Subpack causes a runtime "Node type not found" error for `UltralyticsDetectorProvider`.

## Key Findings

### Recommended Stack

The agent toolkit stack (Python 3.12+, httpx, Pydantic) is unchanged from v1.0. The v2.0 work adds zero new dependencies. Each template is a workflow JSON file composed via the existing `WorkflowGraph` API, validated with the existing 12-rule engine, and documented with the existing metadata/Notion generators. All four node packs are registered on registry.comfy.org and install via the standard registry path.

The four node packs add these external Python dependencies to the ComfyUI environment at runtime: `transformers>=4.39.0,!=4.50.*` (Florence2), `gguf` (GGUF), `ultralytics` + `segment-anything` + `scipy>=1.11.4` (Impact Pack), and `rotary_embedding_torch` + `einops` (MelBandRoFormer). These are ComfyUI runtime concerns, not agent toolkit concerns.

**Core technologies:**
- `WorkflowGraph` (src/composer/graph.py): the only composition API needed for all 4 templates -- no changes required
- `run_validation(mode="strict")`: 12-rule validation before submission; all 4 templates will produce expected `core_node_preference` warnings (intentional, not errors)
- `generate_index_entry()` + `generate_notion_markdown()`: metadata and submission doc generation; requires two pre-flight code fixes for GGUF and audio support
- ComfyUI MCP server (`comfyui-cloud` or `comfyui-mcp`): required for `search_nodes` to fetch node specs before composition

**Required pre-composition code fixes (blocking):**
- `data/core_nodes.json`: add `LoadAudio`, `SaveAudio`, `EmptyLatentAudio` -- missing audio nodes cause false-positive validation errors on the MelBandRoFormer template
- `src/document/metadata.py` `_detect_models`: add `.gguf` to model extension list; add `SaveAudio`/`LoadAudio` to IO type maps

### Expected Features

**Must have (table stakes) -- per template:**
- Florence2: multi-task demo (captioning + detection in single workflow), model auto-download via `DownloadAndLoadFlorence2Model`, image annotation output showing bounding boxes
- GGUF: drop-in GGUF model loading that outputs standard MODEL type, standard txt2img pipeline (only the loaders change), working FLUX.1-schnell generation on 8 GB VRAM
- Impact Pack: automatic face detection via YOLO, SAM-based pixel-accurate face masking, single-node face enhancement (FaceDetailer wraps detect + inpaint)
- MelBandRoFormer: vocals/instruments separation with dual SaveAudio outputs, simple linear graph reflecting the pack's 2-node API

**Should have (differentiators):**
- Florence2: task-switcher via widget (one workflow, 15 tasks), segmentation mask output usable downstream, Note node explaining which tasks use text_input
- GGUF: inline documentation explaining Q4/Q8 VRAM tradeoffs, mixed-format DualCLIPLoaderGGUF (one safetensors + one GGUF encoder)
- Impact Pack: before/after comparison showing VAEDecode output alongside FaceDetailer output, face-specific positive/negative prompts, mask output visualization
- MelBandRoFormer: clear filename prefixes for stem outputs, Note node documenting stereo input requirement and model path

**Defer (v2+):**
- Florence2 LoRA fine-tuning demo (requires niche LoRA models, adds complexity)
- GGUF LoRA integration (experimental with quantized models, limited support)
- Impact Pack multi-pass detailing (advanced pattern, not the 90% use case)
- MelBandRoFormer batch processing (LoadAudio is single-file only, batching requires loop complexity)

### Architecture Approach

All four templates follow an identical composition pattern through the existing codebase: fetch node specs via MCP `search_nodes`, build a `WorkflowGraph`, call `add_node()` + `connect()` + `set_widget()`, run `auto_layout()`, serialize with `save_workflow()`, validate strict, then generate metadata and docs. No template requires subgraphs, Set/Get nodes, or API-authenticated nodes. Custom connection types (FL2MODEL, MELROFORMERMODEL, BBOX_DETECTOR, SAM_MODEL) flow through the existing wildcard path in `is_widget_input()` -- no code changes needed for these.

**Major components and their role in v2.0:**
1. `WorkflowGraph` (src/composer/): build all 4 workflow graphs; handles all node types, connections, and widget configuration by name
2. Validator (12 rules): all 4 templates produce `core_node_preference` warnings (expected); `cloud_compatible` produces INFO reminders; target zero errors across all 4
3. Document generators (src/document/): `generate_index_entry()` auto-extracts IO, models, and custom nodes; `generate_notion_markdown()` produces submission docs -- two metadata.py fixes needed before these work correctly for GGUF and audio

**Output structure (new `templates/` directory):**
```
templates/
  florence2-vision-ai/         workflow.json, index.json, submission.md
  gguf-quantized-txt2img/      workflow.json, index.json, submission.md
  impact-pack-face-detailer/   workflow.json, index.json, submission.md
  melbandroformer-audio-separation/  workflow.json, index.json, submission.md
```

### Critical Pitfalls

1. **GGUF models blocked by template safety policy** -- `.gguf` files are classified "unsafe" by the ComfyUI template model embedding system; auto-download prompts will not appear. Mitigation: add a prominent Note node with manual download instructions; embed only the safetensors components (CLIP-L, VAE) for auto-download; document manual UNET placement in the Notion submission.

2. **Impact Pack requires two separate registry packs** -- `UltralyticsDetectorProvider` lives in `comfyui-impact-subpack`, not `comfyui-impact-pack`. Forgetting the Subpack in `requiresCustomNodes` causes "Node type not found" at runtime. Mitigation: list both packs in metadata; add a Note node in the workflow stating both are required.

3. **core_nodes.json missing audio nodes causes false validation positives** -- `LoadAudio`/`SaveAudio` are ComfyUI core nodes (in `comfy_extras/nodes_audio.py`) but absent from `data/core_nodes.json`. Without fixing this first, MelBandRoFormer template validation incorrectly lists them as custom node dependencies. Mitigation: update core_nodes.json before any template composition.

4. **Florence2 first-run download delays** -- `DownloadAndLoadFlorence2Model` triggers a 1-1.5 GB HuggingFace download on first run, bypassing the template system. On cloud, cold starts incur this delay. Mitigation: default to `microsoft/Florence-2-large-ft` with `fp16` precision and `sdpa` attention; add a Note node explaining the download behavior and wait time.

5. **Impact Pack version drift breaks widget values** -- Impact Pack ships breaking changes that shift widget parameter positions between versions. Mitigation: use `FaceDetailer` (basic variant, not FaceDetailerPipe) which changes less frequently; set ALL widget values explicitly via `set_widget()` by name (not index position); document tested version ("Tested with Impact Pack v8.24+").

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Pre-flight Tooling Fixes
**Rationale:** Two code changes in the existing toolkit are required before any template can be correctly validated or documented. These are not optional -- without them, the MelBandRoFormer template produces false-positive validation errors and the GGUF template metadata omits model files. Must happen before any template composition begins.
**Delivers:** Correct validation and metadata generation for audio and GGUF workflows; updated `data/core_nodes.json`; patched `src/document/metadata.py`
**Addresses:** Pitfalls 3 (stale core_nodes.json) and the `.gguf` metadata detection gap
**Avoids:** Misleading validation output that causes template rework later

### Phase 2: MelBandRoFormer Audio Separation Template
**Rationale:** Simplest graph (5 nodes, 3 links, linear pipeline, 2 custom nodes). Validates the end-to-end compose-validate-document flow with minimal risk. Exercises audio IO detection fixed in Phase 1. Fast win -- fills the audio gap in the template library with a fully safetensors model (auto-downloadable).
**Delivers:** `templates/melbandroformer-audio-separation/` (workflow.json + index.json + submission.md)
**Uses:** `MelBandRoFormerModelLoader` + `MelBandRoFormerSampler` (kijai/ComfyUI-MelBandRoFormer); model `MelBandRoformer_fp16.safetensors` (~456 MB) at `models/diffusion_models/`
**Avoids:** Pitfall 5 (model path confusion -- document `diffusion_models/` in Note node); Pitfall 11 (stereo input -- document in Note)

### Phase 3: Florence2 Vision AI Template
**Rationale:** Still simple (6 nodes, 4 links) but introduces a new pattern: model loader feeding a multi-output processor node (IMAGE, MASK, STRING, JSON). Tests the FL2MODEL custom connection type flowing through the wildcard path. Moderate VRAM (~3-4 GB), model auto-downloads, high cloud compatibility.
**Delivers:** `templates/florence2-vision-ai/` (workflow.json + index.json + submission.md)
**Uses:** `DownloadAndLoadFlorence2Model` + `Florence2Run` (kijai/ComfyUI-Florence2); model auto-downloaded to `models/LLM/` (~1.5 GB for florence-2-large-ft)
**Implements:** Multi-output node pattern; task-switcher via dropdown widget; Note node documenting task options
**Avoids:** Pitfall 3 (download delay -- default `large-ft` fp16 sdpa, Note node with wait time warning); Pitfall 6 (task/text_input mismatch -- default to `more_detailed_caption`); Pitfall 14 (unused outputs -- only wire IMAGE and STRING relevant to the default task)

### Phase 4: GGUF Quantized FLUX.1-schnell txt2img Template
**Rationale:** Standard txt2img pipeline pattern (mirrors existing Flux fixtures in the codebase) with GGUF loader substitutions. 9 nodes, 8 links. Tests `UnetLoaderGGUF` + `DualCLIPLoaderGGUF` fan-out pattern. Highest user demand (1.69M downloads). GGUF cloud limitation requires extra documentation effort -- tackle after simpler templates establish the documentation workflow.
**Delivers:** `templates/gguf-quantized-txt2img/` (workflow.json + index.json + submission.md)
**Uses:** `UnetLoaderGGUF` + `DualCLIPLoaderGGUF` (city96/ComfyUI-GGUF); models: `flux1-schnell-Q4_K_S.gguf` (~6.78 GB, manual download), `clip_l.safetensors` (~246 MB, auto), `t5-v1_1-xxl-encoder-Q8_0.gguf` (~5 GB, manual), `ae.safetensors` (~168 MB, auto)
**Avoids:** Pitfall 1 (GGUF safety block -- explicit Note node + expanded Notion docs for manual setup); Pitfall 8 (bootleg category -- document exact node type names); Pitfall 10 (architecture mismatch -- target Flux/transformer only, not SD1/SDXL); use FLUX.1-schnell (Apache 2.0) not FLUX.1-dev (non-commercial license)

### Phase 5: Impact Pack Face Detailer Template
**Rationale:** Most complex graph (11 nodes, 13+ links, fan-out from CheckpointLoaderSimple to both KSampler and FaceDetailer). Multiple custom connection types (BBOX_DETECTOR, SAM_MODEL). Highest user expectations (2.37M downloads, most-requested post-processing workflow). Do last when the compose/validate/document flow is well-practiced and composition patterns are internalized.
**Delivers:** `templates/impact-pack-face-detailer/` (workflow.json + index.json + submission.md)
**Uses:** `FaceDetailer` + `SAMLoader` (comfyui-impact-pack) + `UltralyticsDetectorProvider` (comfyui-impact-subpack); models: `face_yolov8m.pt` (~6 MB, `models/ultralytics/bbox/`), `sam_vit_b_01ec64.pth` (~375 MB, `models/sams/`), any SD1.5 checkpoint
**Avoids:** Pitfall 2 (Subpack dependency -- list both packs in requiresCustomNodes, Note node in workflow); Pitfall 7 (version drift -- use FaceDetailer basic, set all widgets by name); Pitfall 9 (thread limiting -- document as known behavior in Note); Pitfall 15 (SAM quality -- include SAMLoader, don't make it optional)

### Phase Ordering Rationale

- Phase 1 (tooling) is a hard prerequisite: without it, Phase 2 produces misleading validation output and Phase 4 produces incomplete metadata
- Phases 2-5 are in strict complexity order (5 -> 6 -> 9 -> 11 nodes) to build composition confidence before tackling the most complex graph
- GGUF (Phase 4) comes after Florence2 (Phase 3) because GGUF requires significantly more documentation effort for the cloud limitation; establishing the documentation workflow on simpler templates first reduces rework risk
- Impact Pack (Phase 5) is last because FaceDetailer has the most inputs (15+), the highest version instability risk, and the two-pack dependency gotcha -- experience from the first three templates reduces the chance of errors on the highest-stakes template

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 4 (GGUF):** GGUF model cloud pre-caching status on Comfy Cloud is unknown -- verify whether `flux1-schnell-Q4_K_S.gguf` is pre-cached before submission, or accept manual setup as the documented path; also confirm whether FLUX.1-schnell is preferred over FLUX.1-dev for licensing reasons in the template registry
- **Phase 5 (Impact Pack):** `.pth` format (SAM model `sam_vit_b_01ec64.pth`) may be blocked by template embedding like `.gguf` is -- test empirically at composition time; if blocked, SAM requires manual placement documentation
- **Phase 5 (Impact Pack):** Re-verify FaceDetailer widget count and ordering via MCP at composition time (not from research); Impact Pack version drift makes research-time widget specs unreliable

Phases with standard patterns (skip additional research):
- **Phase 1 (Tooling):** Direct code edits to known files with known changes; no research needed
- **Phase 2 (MelBandRoFormer):** Node spec minimal (2 custom nodes), model is safetensors, graph is linear -- fully specified in research
- **Phase 3 (Florence2):** Node spec verified against GitHub source; all parameters documented; well-understood composition pattern

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Node class names verified against NODE_CLASS_MAPPINGS in GitHub source; model filenames and paths verified against HuggingFace repos; all packs confirmed on registry.comfy.org |
| Features | MEDIUM-HIGH | Table stakes and differentiators derived from download counts, community guides, and node documentation; some widget defaults sourced from tutorials (MEDIUM) rather than official docs |
| Architecture | HIGH | Existing codebase fully analyzed; composition pattern well-understood; custom connection type handling confirmed via code inspection; no new code needed for composition |
| Pitfalls | HIGH | Critical pitfalls verified from primary sources (official template docs for GGUF safety policy, GitHub source for Subpack split, nodes.py for MelBandRoFormer model path); moderate pitfalls from community reports (MEDIUM) |

**Overall confidence:** HIGH

### Gaps to Address

- **GGUF cloud model availability:** Whether `flux1-schnell-Q4_K_S.gguf` is pre-cached on Comfy Cloud infrastructure is unknown. At Phase 4 start, check the Comfy Cloud model catalog or test empirically. If not pre-cached, the submission must include prominent manual setup documentation and reviewer notes explaining the limitation.

- **`.pth` model embedding support:** The SAM model (`sam_vit_b_01ec64.pth`) is in `.pth` format. The template system only explicitly approves `.safetensors`/`.sft` for auto-download. Test whether `.pth` triggers the same "unsafe" block as `.gguf` before finalizing the Impact Pack template model metadata. If blocked, add manual placement instructions to the Note node.

- **Florence2 `_detect_models` heuristic coverage:** The metadata generator's `_detect_models` uses a `"Load" in node_type` heuristic that may miss `DownloadAndLoadFlorence2Model` because it identifies models by HuggingFace repo name, not a local file path. The Phase 1 metadata.py fix should address this; verify it correctly catches the Florence2 model at Phase 3 composition time.

- **MelBandRoFormer mono audio behavior:** Exact behavior when mono audio is provided (hard error vs. silent quality degradation) needs cloud testing during Phase 2 validation. Document whichever behavior is confirmed in the template's Note node.

## Sources

### Primary (HIGH confidence)
- [kijai/ComfyUI-Florence2 GitHub](https://github.com/kijai/ComfyUI-Florence2) -- NODE_CLASS_MAPPINGS, task types, model list, dependencies, pyproject.toml
- [city96/ComfyUI-GGUF GitHub](https://github.com/city96/ComfyUI-GGUF) -- node source, folder paths, architecture notes, nodes.py
- [city96/FLUX.1-schnell-gguf HuggingFace](https://huggingface.co/city96/FLUX.1-schnell-gguf) -- model files, quantization levels, exact sizes
- [ltdrdata/ComfyUI-Impact-Pack GitHub](https://github.com/ltdrdata/ComfyUI-Impact-Pack) -- NODE_CLASS_MAPPINGS, requirements.txt
- [ltdrdata/ComfyUI-Impact-Subpack GitHub](https://github.com/ltdrdata/ComfyUI-Impact-Subpack) -- confirms UltralyticsDetectorProvider is exclusively in the Subpack
- [kijai/ComfyUI-MelBandRoFormer nodes.py](https://github.com/kijai/ComfyUI-MelBandRoFormer/blob/main/nodes.py) -- NODE_CLASS_MAPPINGS, folder path (`diffusion_models`), custom types
- [Kijai/MelBandRoFormer_comfy HuggingFace](https://huggingface.co/Kijai/MelBandRoFormer_comfy/tree/main) -- model filenames and exact sizes
- [ComfyUI Template System Docs](https://docs.comfy.org/interface/features/template) -- model embedding policy, unsafe format definition
- [ComfyUI Core Audio Nodes](https://github.com/comfyanonymous/ComfyUI/blob/master/comfy_extras/nodes_audio.py) -- confirms LoadAudio/SaveAudio are core nodes
- [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates) -- template format, index.json schema, naming conventions, submission process

### Secondary (MEDIUM confidence)
- [Florence2 DeepWiki](https://deepwiki.com/kijai/ComfyUI-Florence2) -- task types, text_input constraint per task, memory management
- [ComfyUI-GGUF DeepWiki](https://deepwiki.com/city96/ComfyUI-GGUF) -- quantization levels, VRAM savings, bootleg category, architecture support matrix
- [FaceDetailer node documentation](https://www.runcomfy.com/comfyui-nodes/ComfyUI-Impact-Pack/FaceDetailer) -- required/optional inputs, SAM model integration
- [Impact Pack Thread Issue #1097](https://github.com/ltdrdata/ComfyUI-Impact-Pack/issues/1097) -- FaceDetailer thread limiting behavior

### Tertiary (LOW confidence, needs validation)
- [Flux GGUF Low VRAM Guide](https://www.nextdiffusion.ai/tutorials/how-to-run-flux-dev-gguf-in-comfyui-low-vram-guide) -- VRAM estimates by quantization level (community-written, needs cloud testing to confirm)
- [MelBandRoFormer RunComfy Guide](https://www.runcomfy.com/comfyui-nodes/ComfyUI-MelBandRoFormer) -- stereo input requirement (community-written, exact failure mode needs cloud testing)

---
*Research completed: 2026-03-25*
*Ready for roadmap: yes*
