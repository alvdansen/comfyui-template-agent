# Contributing

Thanks for your interest in contributing to ComfyUI Template Agent. This guide covers setup, conventions, and how to author new skills.

## Development Setup

**Prerequisites:**

- Python 3.12+
- Claude Code with skills support
- ComfyUI MCP server (`comfyui-cloud` or `comfyui-mcp`) -- only needed for compose/flow skills

**Install:**

```bash
git clone https://github.com/alvdansen/comfyui-template-agent.git
cd comfyui-template-agent
./setup.sh        # Creates venv, installs deps, links skills, runs tests
```

`setup.sh` runs `pip install -e ".[dev]"` (editable mode), symlinks skills into `~/.claude/skills/`, and verifies the test suite passes.

**Verify:** `pytest` should complete in ~0.5s with all tests passing.

## Code Style

- **Data models:** Pydantic models for all data structures
- **HTTP:** httpx with `follow_redirects=True` for all requests
- **Caching:** Module-level `DiskCache()` singletons -- one per module, not per function
- **Testing:** Tests in `tests/` mirroring `src/` structure. Add tests for new features.
- **Linting:** ruff with `line-length = 100`, target Python 3.12. Config in `pyproject.toml`.
- **CLI:** Entry points via `python -m src.module.script` with argparse
- **Workflow format:** Always workflow format JSON (`nodes[]` + `links[]`), never API format (string keys)

**Pre-commit check:**

```bash
pytest && ruff check src/
```

Both must pass before submitting a PR.

## Pull Request Process

1. Create a feature branch from `master`
2. Make changes following the code style above
3. Run `pytest && ruff check src/` -- both must pass
4. Write a clear PR description: what changed and why
5. One logical change per PR preferred

No CI pipeline yet -- the local test suite is the quality gate.

## Skill Authoring

Skills live in `.claude/skills/comfy-{name}/`. Each skill folder contains two files:

```
.claude/skills/comfy-{name}/
  SKILL.md       # Trigger, capabilities, commands, example session
  gotchas.md     # Known failure points and non-obvious behavior
```

**Do NOT** create `scripts/` or `references/` subdirectories unless the skill genuinely needs them.

### SKILL.md format

```markdown
---
name: comfy-{name}
description: "When the user wants to..."
---

# {Title}

{One-line purpose}

## Capabilities

- {What the skill can do, bulleted}

## Commands

```bash
{CLI commands with flags and descriptions}
```

## Example Session

**User:** {natural language request}
**Agent:** {action + result in 1-2 sentences}
**User:** {follow-up}
**Agent:** {result}
**User:** {next step}
**Agent:** {final output}

## Key Constraints

- {Constraint 1}
- {Constraint 2}
```

### Rules

- Trigger description in frontmatter starts with "When the user wants to..."
- `gotchas.md` stays as a separate file -- never fold into `SKILL.md`
- Every CLI command in the Example Session must exist in the Commands section
- Example sessions are 3-4 turns showing the workflow, not full tutorials
