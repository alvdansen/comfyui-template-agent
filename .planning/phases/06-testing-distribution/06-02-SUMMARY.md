---
phase: 06-testing-distribution
plan: 02
status: complete
started: 2026-03-19
completed: 2026-03-19
---

## One-liner

Guided interactive testing of all 6 skills with user, fixing issues inline as discovered.

## What was done

- Tested all 6 skills: comfy-discover, comfy-template-audit, comfy-validate, comfy-compose, comfy-document, comfy-flow
- Fixed python3 → python for Windows compatibility
- Fixed package importability (setuptools config)
- Renamed comfy-templates → comfy-template-audit for clarity
- Built workflow_to_api converter (src/shared/convert.py)
- Resolved API node auth: automatic in MCP v0.2.0+
- Added LoadImage local file detection to validator
- Expanded core_nodes.json (118 → 179 nodes)
- Rewrote notion.py with 6 new documentation sections
- Added API model detection in metadata.py
- Updated cloud polling guidance
- Added Notion MCP integration to comfy-document

## Issues found and fixed

- Skills not importable from outside project dir (missing setuptools config)
- comfy-tip/comfy-discover naming conflict (removed global comfy-tip)
- API node auth was upstream gap (resolved in MCP v0.2.0)
- Core nodes list missing ~60 nodes (false positive custom node warnings)
- notion.py missing How It Works, Node Dependencies, Cost Estimate sections
- Workflow-to-API format conversion missing entirely
- UI-only widget values (control_after_generate) leaking into API payloads

## Key files modified

- src/shared/convert.py (new)
- src/validator/api_nodes.py
- src/validator/rules.py
- src/document/metadata.py
- src/document/notion.py
- data/core_nodes.json
- All 6 skill SKILL.md and gotchas.md files
- pyproject.toml
- scripts/update_core_nodes.py (new)
