---
name: comfy-templates
description: "When the user wants to browse existing templates, check if a node has template coverage, or find gaps worth filling"
---

# Template Intelligence

Full access to the ComfyUI template library: search, detail view, cross-reference, gap analysis, and coverage reports.

## Commands

```bash
# Search templates
python -m src.templates.search --query "upscale" --type video
python -m src.templates.search --query "flux" --model "flux"

# Template detail (shows node types extracted from workflow JSON)
python -m src.templates.fetch --detail "flux_schnell_simple_generation"
python -m src.templates.fetch --list

# Cross-reference: which templates use a node/pack?
python -m src.templates.cross_ref --query "ComfyUI-KJNodes" --level pack
python -m src.templates.cross_ref --query "KSampler" --level node

# Gap analysis: popular packs without templates
python -m src.templates.coverage gap --limit 20
python -m src.templates.coverage gap --by-category --limit 10

# Coverage report
python -m src.templates.coverage coverage
```

Use `--refresh` on any command to bypass cache.

## Live Example

!python -m src.templates.coverage gap --limit 3

## Key Constraints

- Cross-reference returns exact and fuzzy matches -- fuzzy may surface unexpected results when exact match returns nothing.
- Coverage % is pack-level, not node-level.
- Gap scoring: `log10(downloads) * (1 + log2(stars) * 0.5)` -- balances volume with community signal.
- `fetch_all_nodes` uses `pages` param -- don't assume single-page responses.
