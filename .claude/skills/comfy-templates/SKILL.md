---
name: comfy-templates
description: "Browse, search, and analyze the ComfyUI template library. View template details with node types. Cross-reference nodes against templates. Generate gap analysis and coverage reports."
---

# ComfyUI Template Intelligence

## What This Does
Provides full access to the ComfyUI template library: search templates, view detailed metadata and node types, cross-reference which templates use specific nodes or packs, identify gaps where popular nodes lack templates, and generate coverage reports.

## Quick Start
Just describe what you're looking for in natural language:
- "What templates exist for video generation?"
- "Show me the details of the flux_schnell template"
- "What nodes does the wan_image_to_video template use?"
- "Is ComfyUI-KJNodes used in any template?"
- "What popular nodes don't have templates yet?"
- "Show me the template coverage report"
- "Search for templates using flux"
- "What gaps exist in image templates?"
- "How many templates are there per category?"
- "List all available templates"

## How It Works

### Search Templates
```bash
python -m src.templates.search --query "upscale" --type video
python -m src.templates.search --query "flux" --model "flux"
python -m src.templates.search --query "audio" --type audio
```

### Template Detail
View full metadata and extracted node types for a single template:
```bash
python -m src.templates.fetch --detail "flux_schnell_simple_generation"
python -m src.templates.fetch --detail "wan_image_to_video" --refresh
python -m src.templates.fetch --list
```

### Cross-Reference
Find which templates use a specific node pack or node type:
```bash
python -m src.templates.cross_ref --query "ComfyUI-KJNodes" --level pack
python -m src.templates.cross_ref --query "KSampler" --level node
python -m src.templates.cross_ref --query "VAEDecode" --level node --refresh
```

### Gap Analysis
Identify popular node packs that have no template coverage:
```bash
python -m src.templates.coverage gap --limit 20
python -m src.templates.coverage gap --by-category --limit 10
```

### Coverage Report
Get a bird's-eye view of template library health:
```bash
python -m src.templates.coverage coverage
python -m src.templates.coverage coverage --refresh
```

## Output Format
- **Search**: Ranked list of matching templates with title, category, tags, and relevance score
- **Detail**: Full metadata including node types extracted from the workflow JSON
- **Cross-reference**: Templates using the queried node/pack, with exact and fuzzy matches
- **Gap analysis**: Ranked list of uncovered packs scored by popularity, with template suggestions
- **Coverage report**: Category distribution table, pack coverage %, thin spots, monthly growth trends

## Integration
Results from template intelligence can be combined with discovery results from the `comfy-discover` skill. Example workflow: discover trending nodes -> check if they have templates -> identify gaps -> suggest new template ideas.

## Tips
- Template and registry data are cached (configurable TTL)
- Use `--refresh` to force re-fetch from upstream
- Gap analysis connects Phase 1 registry data with Phase 2 template data
- Coverage report thin spots highlight categories that need more templates
- Node IDs from cross-reference results can be used with `comfy-discover` for deeper inspection
