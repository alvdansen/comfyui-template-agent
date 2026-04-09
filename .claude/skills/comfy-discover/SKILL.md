---
name: comfy-discover
description: "When the user wants to explore ComfyUI nodes -- trending, new, popular, or searching for specific capabilities"
---

# Node Discovery

Surface interesting nodes from the ComfyUI registry for template creation inspiration.

## Capabilities

- Browse trending, new, rising, popular, and random nodes
- Filter by media category (video, image, audio, 3d)
- Search nodes by name or capability keyword
- Search by input/output type (e.g., IMAGE -> MASK)
- Inspect node pack details and I/O specifications

## Commands

```bash
# Browse modes
python -m src.registry.highlights --mode trending --limit 10
python -m src.registry.highlights --mode new --limit 10
python -m src.registry.highlights --mode rising --limit 10
python -m src.registry.highlights --mode popular --limit 10
python -m src.registry.highlights --mode random --truly-random --limit 5

# Filter by media category (video, image, audio, 3d)
python -m src.registry.highlights --mode trending --category video

# Search nodes
python -m src.registry.search --query "upscale" --limit 10
python -m src.registry.search --type-input IMAGE --type-output MASK

# Inspect a node pack
python -m src.registry.spec <node-pack-id> --detail
```

Add `--json` to any command for raw JSON output.

## Example Session

**User:** Show me trending audio nodes
**Agent:** Runs `python -m src.registry.highlights --mode trending --category audio --limit 10`. Found 8 audio packs -- top 3: ComfyUI-MelBandRoFormer (240K downloads), ComfyUI-AudioReactive (95K), ComfyUI-Whisper (78K).
**User:** Tell me more about MelBandRoFormer
**Agent:** Runs `python -m src.registry.spec comfyui-melbandroformer --detail`. Pack by kijai -- 2 nodes: MelBandRoFormerModelLoader and MelBandRoFormerSampler. Separates audio into vocals and instruments using MelBandRoFormer model.
**User:** Any templates using it yet?
**Agent:** Cross-references with template library. No existing template -- this is a gap worth filling.

## Key Constraints

- Category filter uses keyword matching, not registry tags (tags field is empty for most packs).
- Cache TTLs: 1hr browsing, 15min search, 24hr specs. Use `--refresh` to bypass.
- Node IDs from results cross-reference with all other comfy-* skills.
- `search_by_type` uses two-step: search packs, then verify I/O via comfy-nodes API.
