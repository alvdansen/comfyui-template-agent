# Roadmap: ComfyUI Template Agent

## Milestones

- v1.0 MVP - Phases 1-6 (shipped 2026-03-20)
- v2.0 Template Batch - Phases 7-11 (in progress)

## Phases

<details>
<summary>v1.0 MVP (Phases 1-6) - SHIPPED 2026-03-20</summary>

- [x] **Phase 1: Foundation + Discovery** - Shared infrastructure and registry node discovery skill
- [x] **Phase 2: Template Intelligence** - Template library browsing, cross-referencing, and gap analysis
- [x] **Phase 3: Validation Engine** - Guideline compliance checks and compatibility validation
- [x] **Phase 4: Composition** - Type-safe workflow building and template scaffolding
- [x] **Phase 5: Documentation + Orchestration** - Submission doc generation and guided end-to-end flow
- [x] **Phase 6: Testing & Distribution** - E2E testing, install script, README, repo cleanup

</details>

### v2.0 Template Batch -- Trending Node Coverage

- [x] **Phase 7: Tooling Fixes** - Fix core_nodes.json audio gaps and metadata.py GGUF detection
- [x] **Phase 8: MelBandRoFormer Template** - Audio stem separation workflow (5 nodes, linear pipeline)
- [x] **Phase 9: Florence2 Template** - Vision AI captioning/detection workflow (6 nodes, multi-output)
- [x] **Phase 10: GGUF Template** - Quantized FLUX.1-schnell txt2img workflow (9 nodes, GGUF loaders)
- [x] **Phase 11: Impact Pack Template** - Face detection + auto-detailing workflow (11 nodes, fan-out)

## Phase Details

### Phase 7: Tooling Fixes
**Goal**: Validation and metadata generation work correctly for audio workflows and GGUF model files
**Depends on**: Phase 6 (v1.0 complete)
**Requirements**: TOOL-01, TOOL-02
**Success Criteria** (what must be TRUE):
  1. A workflow containing LoadAudio, SaveAudio, or EmptyLatentAudio passes validation without being flagged as custom node dependencies
  2. A workflow containing .gguf model file references produces correct model entries in generated index.json metadata
**Plans**: TBD

### Phase 8: MelBandRoFormer Template
**Goal**: A production-ready audio stem separation template exists in the template library, ready for submission
**Depends on**: Phase 7
**Requirements**: MELB-01, MELB-02, MELB-03, MELB-04
**Success Criteria** (what must be TRUE):
  1. User can load the workflow in ComfyUI and separate an audio file into vocal and instrumental stems via dual SaveAudio outputs
  2. Running strict validation on the workflow produces zero errors (core_node_preference warnings are expected and acceptable)
  3. index.json contains correct requiresCustomNodes (kijai/ComfyUI-MelBandRoFormer), model path (diffusion_models/), and IO spec (audio input, dual audio output)
  4. Notion submission markdown is complete and ready to paste into the submission page
**Plans**: TBD
**UI hint**: no

### Phase 9: Florence2 Template
**Goal**: A production-ready vision AI template exists demonstrating Florence2 captioning, ready for submission
**Depends on**: Phase 7
**Requirements**: FLOR-01, FLOR-02, FLOR-03, FLOR-04
**Success Criteria** (what must be TRUE):
  1. User can load the workflow in ComfyUI and run Florence2 captioning on an input image, receiving text output and optionally annotated image output
  2. Running strict validation on the workflow produces zero errors
  3. index.json contains correct model reference (microsoft/Florence-2-large-ft via auto-download) and IO spec (image input, text + image output)
  4. Notion submission markdown is complete and ready to paste into the submission page
**Plans**: TBD
**UI hint**: no

### Phase 10: GGUF Template
**Goal**: A production-ready quantized txt2img template exists using GGUF loaders with FLUX.1-schnell, ready for submission with manual model setup documentation
**Depends on**: Phase 7
**Requirements**: GGUF-01, GGUF-02, GGUF-03, GGUF-04
**Success Criteria** (what must be TRUE):
  1. User can load the workflow in ComfyUI and generate images from text prompts using GGUF-quantized FLUX.1-schnell on consumer hardware (8 GB VRAM)
  2. Running strict validation on the workflow produces zero errors
  3. index.json contains manual model installation notes explaining that .gguf files require manual download (blocked by template safety policy)
  4. Notion submission markdown includes prominent GGUF setup instructions with model download URLs, file placement paths, and VRAM requirements
**Plans**: TBD
**UI hint**: no

### Phase 11: Impact Pack Template
**Goal**: A production-ready face detection and auto-detailing template exists using FaceDetailer, ready for submission
**Depends on**: Phase 7
**Requirements**: IMPC-01, IMPC-02, IMPC-03, IMPC-04
**Success Criteria** (what must be TRUE):
  1. User can load the workflow in ComfyUI and automatically detect and enhance faces in generated images via FaceDetailer with YOLO detection and SAM masking
  2. Running strict validation on the workflow produces zero errors
  3. index.json declares both comfyui-impact-pack AND comfyui-impact-subpack in requiresCustomNodes (missing Subpack causes runtime failure)
  4. Notion submission markdown is complete and ready to paste into the submission page
**Plans**: TBD
**UI hint**: no

## Progress

**Execution Order:**
Phase 7 first (prerequisite), then Phases 8-11 can execute in parallel.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation + Discovery | v1.0 | 2/2 | Complete | 2026-03-19 |
| 2. Template Intelligence | v1.0 | 2/2 | Complete | 2026-03-19 |
| 3. Validation Engine | v1.0 | 2/2 | Complete | 2026-03-19 |
| 4. Composition | v1.0 | 3/3 | Complete | 2026-03-19 |
| 5. Documentation + Orchestration | v1.0 | 2/2 | Complete | 2026-03-20 |
| 6. Testing & Distribution | v1.0 | 3/3 | Complete | 2026-03-20 |
| 7. Tooling Fixes | v2.0 | 1/1 | Complete | 2026-03-25 |
| 8. MelBandRoFormer Template | v2.0 | 1/1 | Complete | 2026-03-25 |
| 9. Florence2 Template | v2.0 | 1/1 | Complete | 2026-03-25 |
| 10. GGUF Template | v2.0 | 1/1 | Complete | 2026-03-25 |
| 11. Impact Pack Template | v2.0 | 1/1 | Complete | 2026-03-25 |
