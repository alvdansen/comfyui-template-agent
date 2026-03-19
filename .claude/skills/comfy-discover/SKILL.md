---
name: comfy-discover
description: "Discover trending, new, and interesting ComfyUI nodes from the registry for template inspiration"
---

# Node Discovery

## What This Does
Surfaces interesting nodes from the ComfyUI registry for template creation inspiration. Browse trending, new, rising, and popular nodes, search by name or type, filter by media category, and inspect node packs.

## Quick Start
Just describe what you're looking for in natural language:
- "What's trending in ComfyUI?"
- "Show me new video processing nodes"
- "Find nodes for audio generation"
- "Surprise me with something random"
- "What nodes does ComfyUI-Impact-Pack include?"
- "Find nodes that output MASK type"

## How It Works

### Browse Discovery Modes
```bash
python3 -m src.registry.highlights --mode trending --limit 10
python3 -m src.registry.highlights --mode new --limit 10
python3 -m src.registry.highlights --mode rising --limit 10
python3 -m src.registry.highlights --mode popular --limit 10
python3 -m src.registry.highlights --mode random --limit 5
python3 -m src.registry.highlights --mode random --truly-random --limit 5
```

### Filter by Media Category
Add --category to any browse command:
```bash
python3 -m src.registry.highlights --mode trending --category video
python3 -m src.registry.highlights --mode popular --category audio
```
Categories: video, image, audio, 3d

### Search Nodes
```bash
python3 -m src.registry.search --query "upscale" --limit 10
python3 -m src.registry.search --query "controlnet" --category image
python3 -m src.registry.search --type-input IMAGE --type-output MASK
```

### Inspect Node Pack
```bash
python3 -m src.registry.spec <node-pack-id>
python3 -m src.registry.spec comfyui-impact-pack --detail
```

### JSON Output
Add --json to any command for raw JSON output (useful for piping to other tools).

## Output Format
Results show as summary cards by default:
- Name, Author, Downloads, Stars, Description, Repository link
- Node ID is always included for cross-referencing with other skills

When user asks for details on a specific node or pack, show full I/O specifications.

## Tips
- Discovery results are cached (1hr for browsing, 15min for search, 24hr for specs)
- Use "random" mode for creative inspiration; "trending" for popular choices
- Node IDs from results can be used with other comfy-* skills
- The category filter uses keyword matching, not registry tags (which are empty)
