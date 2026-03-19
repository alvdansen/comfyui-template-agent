# TODOs

## Resolved

- [x] **API node cloud support via MCP** — Fixed in MCP server v0.2.0 (commit f8b789b). Auth for partner/API nodes (Gemini, BFL, etc.) is now automatic. Updated: `src/validator/api_nodes.py`, `comfy-compose/SKILL.md`, `comfy-flow/SKILL.md`, `comfy-compose/gotchas.md`. Resolved 2026-03-19.

## Open

- [ ] **Refine `scripts/update_core_nodes.py`** — The regex for parsing NODE_CLASS_MAPPINGS from GitHub source misses most comfy_extras nodes. Currently works for `nodes.py` but not the 96 extras files. Low priority since manual additions work fine.
