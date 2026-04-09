# Milestones

## v2.0 Template Batch -- Trending Node Coverage (Shipped: 2026-04-09)

**Phases completed:** 5 phases (7-11), 5 plans

**Key accomplishments:**

- Fixed core_nodes.json audio gaps (LoadAudio, SaveAudio, EmptyLatentAudio) and .gguf model detection in metadata.py
- Delivered MelBandRoFormer audio stem separation template (5 nodes, linear pipeline, 456 MB model)
- Delivered Florence2 vision AI captioning template (6 nodes, multi-output, auto-download model)
- Delivered GGUF quantized FLUX.1-schnell txt2img template (9 nodes, consumer 8 GB VRAM target)
- Delivered Impact Pack face detailer template (11 nodes, dual-pack dependency, fan-out topology)
- Added description Note nodes to all 4 templates for in-editor documentation

**Archive:** [v2.0-ROADMAP.md](milestones/v2.0-ROADMAP.md) | [v2.0-REQUIREMENTS.md](milestones/v2.0-REQUIREMENTS.md)

---

## v1.0 MVP (Shipped: 2026-03-20)

**Phases completed:** 6 phases (1-6), 14 plans

**Key accomplishments:**

- Built shared infrastructure: HTTP client, disk caching, format detection
- Node discovery skill with 5 browse modes (trending/new/rising/popular/random) + search
- Template intelligence: library search, cross-referencing, gap analysis across 400+ templates
- Validation engine: 12 guideline rules, strict/lenient modes, cloud compatibility checks
- Workflow composition: type-safe graph builder, template scaffolding, incremental validation
- Documentation generation: index.json metadata, Notion markdown, guided end-to-end flow
- E2E testing, install script, README, repo cleanup

**Archive:** [v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md) | [v1.0-REQUIREMENTS.md](milestones/v1.0-REQUIREMENTS.md)

---
