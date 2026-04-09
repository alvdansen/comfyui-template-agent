---
name: comfy-template-audit
description: "When the user wants to audit existing templates, check if a node has template coverage, or find gaps worth filling"
---

# Template Intelligence

Full access to the ComfyUI template library: search, detail view, cross-reference, gap analysis, and coverage reports.

## Capabilities

- Search the template library by keyword, type, or model
- View template details including extracted node types
- Cross-reference nodes or packs against existing templates
- Run gap analysis to find popular packs without templates
- Generate coverage reports across the template library

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

## Example Session

**User:** What popular node packs don't have templates yet?
**Agent:** Runs `python -m src.templates.coverage gap --limit 5`. Top gaps: ComfyUI-KJNodes (2.1M downloads, no template), ComfyUI-VideoHelperSuite (1.2M, no template), ComfyUI-WanVideoWrapper (890K, no template).
**User:** Which templates use KSampler?
**Agent:** Runs `python -m src.templates.cross_ref --query "KSampler" --level node`. Found 23 templates using KSampler -- most common in txt2img and img2img workflows.
**User:** Show me the FLUX schnell template details
**Agent:** Runs `python -m src.templates.fetch --detail "flux_schnell_simple_generation"`. Uses 5 nodes: KSampler, CLIPTextEncode, EmptyLatentImage, VAEDecode, SaveImage. Model: FLUX.1-schnell.

## Key Constraints

- Cross-reference returns exact and fuzzy matches -- fuzzy may surface unexpected results when exact match returns nothing.
- Coverage % is pack-level, not node-level.
- Gap scoring: `log10(downloads) * (1 + log2(stars) * 0.5)` -- balances volume with community signal.
- `fetch_all_nodes` uses `pages` param -- don't assume single-page responses.
