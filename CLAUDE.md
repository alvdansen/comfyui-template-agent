# ComfyUI Template Agent

Claude Code agent toolkit for ComfyUI template creation. Six skills guide template creators from node discovery through submission documentation.

## Skills

| Skill | Trigger |
|-------|---------|
| comfy-discover | Exploring nodes -- trending, new, popular, or searching by capability |
| comfy-template-audit | Browsing templates, checking coverage, finding gaps worth filling |
| comfy-validate | Checking workflow JSON against guidelines, cloud compatibility, submission readiness |
| comfy-compose | Building workflows -- from scratch, from scaffold, or modifying existing |
| comfy-document | Generating submission docs -- index.json, Notion markdown, thumbnail specs |
| comfy-flow | Guided end-to-end template creation ("let's make a template") |

## Development

```bash
pytest                                     # Run tests (~0.5s)
python -m src.registry.highlights trending  # Test discovery
python -m src.validator.validate --file workflow.json  # Test validation
python -m src.templates.coverage gap --limit 10  # Test gap analysis
```

## Architecture

- `src/shared/` -- HTTP client (httpx), caching (DiskCache), format detection
- `src/registry/` -- Node discovery (highlights, search, spec)
- `src/templates/` -- Template library (fetch, search, cross_ref, coverage)
- `src/validator/` -- Validation engine (rules, engine, validate CLI)
- `src/composer/` -- Workflow composition (graph, scaffold, layout, compose CLI)
- `src/document/` -- Documentation generation (metadata, notion, generate CLI, orchestrator)
- `data/` -- Static data (core_nodes.json, guidelines.json, api_nodes.json)

## Conventions

- Pydantic models for all data structures
- Module-level DiskCache singletons for HTTP caching
- httpx with `follow_redirects=True` for all HTTP requests
- Tests in `tests/` mirroring `src/` structure
- CLI entry points via `python -m src.module.script`
- Workflow format JSON (nodes[] + links[]), never API format (string keys)

<important if="modifying skills">
Skills live in `.claude/skills/comfy-*/`. Each skill folder has:
- `SKILL.md` -- trigger description and essential behavior
- `gotchas.md` -- known failure points and non-obvious behavior

Do NOT create `scripts/` or `references/` subdirs unless the skill genuinely needs them.
</important>

<important if="adding dependencies">
All dependencies declared in `pyproject.toml`. Currently: httpx, pydantic.
Dev: pytest, ruff. Python 3.12+ required.
</important>

<important if="composing workflows">
ComfyUI MCP server must be connected (comfyui-cloud or comfyui-mcp).
NodeSpecCache is pass-through -- fetch specs via MCP `search_nodes`, then feed raw dicts in.
</important>
