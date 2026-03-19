---
name: comfy-discover
description: "When the user wants to explore ComfyUI nodes -- trending, new, popular, or searching for specific capabilities"
---

# Node Discovery

Surface interesting nodes from the ComfyUI registry for template creation inspiration.

## Commands

```bash
# Browse modes
python3 -m src.registry.highlights --mode trending --limit 10
python3 -m src.registry.highlights --mode new --limit 10
python3 -m src.registry.highlights --mode rising --limit 10
python3 -m src.registry.highlights --mode popular --limit 10
python3 -m src.registry.highlights --mode random --truly-random --limit 5

# Filter by media category (video, image, audio, 3d)
python3 -m src.registry.highlights --mode trending --category video

# Search nodes
python3 -m src.registry.search --query "upscale" --limit 10
python3 -m src.registry.search --type-input IMAGE --type-output MASK

# Inspect a node pack
python3 -m src.registry.spec <node-pack-id> --detail
```

Add `--json` to any command for raw JSON output.

## Key Constraints

- Category filter uses keyword matching, not registry tags (tags field is empty for most packs).
- Cache TTLs: 1hr browsing, 15min search, 24hr specs. Use `--refresh` to bypass.
- Node IDs from results cross-reference with all other comfy-* skills.
- `search_by_type` uses two-step: search packs, then verify I/O via comfy-nodes API.

## Live Example

!python3 -m src.registry.highlights --mode trending --limit 3
