# Phase 12: Repo Foundation - Context

**Gathered:** 2026-04-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Repo has all legal and structural prerequisites for public release: MIT LICENSE, complete pyproject.toml metadata, comprehensive .gitignore, and retroactive CHANGELOG.md. Delivers REPO-01, REPO-02, REPO-03, REPO-04.

</domain>

<decisions>
## Implementation Decisions

### Author & attribution
- **D-01:** Alvdansen Labs is the sole author and copyright holder in both pyproject.toml and MIT LICENSE
- **D-02:** Author contact email is timothy@comfy.org
- **D-03:** Repository URL will be github.com/alvdansen/comfyui-template-agent (per v3.0 milestone decision)

### Changelog format
- **D-04:** Use Keep a Changelog format (keepachangelog.com) with Added/Changed/Fixed sections per version
- **D-05:** v3.0 entry is pre-populated with planned items and will be continuously updated as phases complete

### .gitignore scope
- **D-06:** Add .venv/ and .planning/ to .gitignore (required by success criteria)
- **D-07:** Add COMPAT-FIX.md to .gitignore — internal bash compatibility guide, not a deliverable
- **D-08:** templates/*/build.py files are tracked — they are core deliverables demonstrating toolkit usage
- **D-09:** Existing patterns carry forward: __pycache__/, *.pyc, .pytest_cache/, data/cache/, .claude/settings.local.json, .env, *.egg-info/, dist/, build/, .ruff_cache/

### Claude's Discretion
- pyproject.toml classifiers and keywords selection (standard Python packaging choices)
- Exact CHANGELOG.md wording for v1.0 and v2.0 historical entries (factual summary of shipped work)
- Any additional .gitignore patterns for common Python/IDE artifacts (*.swp, .DS_Store, .idea/, .vscode/, etc.)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project metadata
- `pyproject.toml` — Current project config (version 0.1.0, needs update to 3.0.0 with full metadata)
- `.gitignore` — Current exclusion patterns (needs .venv/, .planning/, COMPAT-FIX.md additions)

### Milestone context
- `.planning/ROADMAP.md` — Phase 12 success criteria (4 specific requirements)
- `.planning/REQUIREMENTS.md` — REPO-01 through REPO-04 requirement definitions
- `.planning/STATE.md` — v3.0 decisions (fresh repo under alvdansen org, .planning/ excluded)

### Prior phase decisions
- `.planning/phases/06-testing-distribution/06-CONTEXT.md` — Phase 6 .gitignore patterns and pyproject.toml completeness decisions

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `pyproject.toml` — Exists with basic structure, needs metadata additions (not a rewrite)
- `.gitignore` — Exists with 10 patterns, needs 3 additions

### Established Patterns
- Python 3.12+ minimum, httpx + pydantic stack
- Dev deps: pytest, ruff
- setuptools packaging with src/ layout

### Integration Points
- pyproject.toml `license` field must reference the new LICENSE file
- CHANGELOG.md documents milestones: v1.0 (6 skills, 14 plans), v2.0 (4 templates), v3.0 (publish)
- Repository URL in pyproject.toml must match the alvdansen org target

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches for LICENSE text, changelog entries, and .gitignore patterns. User gave full discretion on implementation details beyond the decisions above.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 12-repo-foundation*
*Context gathered: 2026-04-09*
