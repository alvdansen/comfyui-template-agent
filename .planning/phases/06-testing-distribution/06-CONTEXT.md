# Phase 6: Testing & Distribution - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

E2E testing with real ComfyUI workflows, install script for team onboarding, README, repo cleanup, AND a quality audit of all skills/CLAUDE.md against Claude Code best practices. This phase ensures the toolkit is not just functional but follows the patterns that make Claude Code agents effective. Delivers TEST-01 through TEST-04.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion (full discretion given)

User provided extensive Claude Code best practices reference as the quality bar. Phase 6 must audit and fix the toolkit against these patterns in addition to standard testing/distribution tasks.

**E2E Testing (TEST-01):**
- Test each skill with real ComfyUI workflow JSON files (not just mocked data)
- Include at least: a standard SD workflow, a Flux workflow, a video workflow (Wan), an API node workflow
- Test the full /comfy-flow pipeline end-to-end
- Tests should use fixture workflow files in `tests/fixtures/`

**Install Script (TEST-02):**
- Single setup script that handles: pip install, skill symlinking to `~/.claude/skills/`, prerequisite checks (Python 3.12+, comfyui-mcp server)
- Should work on macOS and Windows (the team uses both)
- "Clone + run setup" experience

**README (TEST-03):**
- Internal team doc (not public-facing yet)
- Under 200 lines (CLAUDE.md best practice)
- Sections: What this is, Setup, Available Skills (with examples), Prerequisites, Contributing
- Include real usage examples for each skill showing natural language prompts

**Repo Cleanup (TEST-04):**
- .gitignore: __pycache__, .cache/, *.pyc, .env, data/highlights_cache.json
- No secrets, no temp files, no Notion export artifacts
- Clean pyproject.toml with all dependencies declared

**Quality Audit (critical — from best practices reference):**

The following Claude Code best practices MUST be audited and fixed across all 6 skills:

### Skill Architecture Audit
- [ ] **Skills are folders, not files** — use `references/`, `scripts/`, `examples/` subdirectories for progressive disclosure
- [ ] **Description is a trigger, not summary** — "when should I fire?" not "what I do"
- [ ] **Don't state the obvious** — focus on what pushes Claude out of default behavior
- [ ] **Don't railroad** — give goals and constraints, not prescriptive step-by-step
- [ ] **Include scripts** — Claude composes rather than reconstructs boilerplate
- [ ] **Gotchas section** — highest-signal content, add failure points
- [ ] **Embed `!command`** for dynamic shell output where useful (e.g., `!python -m src.registry.highlights trending` to show live examples)

### CLAUDE.md Audit
- [ ] Under 200 lines total
- [ ] Domain-specific rules in `<important if="...">` tags if file grows
- [ ] Use `.claude/rules/` for split instructions if needed
- [ ] No stale patterns or half-finished migrations

### Workflow Quality Audit
- [ ] Each skill can be invoked with natural language OR explicit flags
- [ ] Skills share session context (results carry forward)
- [ ] Progressive disclosure: summary by default, detail on request
- [ ] /comfy-flow guides users through the full feedback loop: discover → ideate → compose → validate → document
- [ ] Context-aware suggestions at each step
- [ ] User can enter at any step, exit and resume

### Testing Quality Audit
- [ ] Phase-wise gated tests (unit per module, integration across modules)
- [ ] Tests verify observable behavior, not implementation details
- [ ] Full test suite runs in <15 seconds

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### All Existing Skills (audit targets)
- `.claude/skills/comfy-discover/SKILL.md` — node discovery
- `.claude/skills/comfy-templates/SKILL.md` — template intelligence
- `.claude/skills/comfy-validate/SKILL.md` — validation engine
- `.claude/skills/comfy-compose/SKILL.md` — workflow composition
- `.claude/skills/comfy-document/SKILL.md` — documentation generation
- `.claude/skills/comfy-flow/SKILL.md` — orchestrator

### Project Files
- `pyproject.toml` — project config and dependencies
- `data/` — core_nodes.json, guidelines.json, api_nodes.json
- All `src/` modules: shared/, registry/, templates/, validator/, composer/, document/

### Claude Code Best Practices (from user reference)
- Skills: folders with subdirs, trigger descriptions, gotchas sections, progressive disclosure, embedded scripts
- CLAUDE.md: <200 lines, domain tags, rules splitting
- Workflows: natural language + flags, context sharing, progressive detail

</canonical_refs>

<code_context>
## Existing Code Insights

### Current State
- 6 skills in `.claude/skills/` — each is a single SKILL.md file (audit: should be folders with subdirs)
- 212 tests across 8 test files — all passing in 0.5s
- No CLAUDE.md for this project yet (need to create one)
- No .gitignore yet
- No install script
- No README

### What Needs Doing
1. Create test fixtures (real workflow JSONs)
2. Write E2E integration tests
3. Audit + restructure all 6 skills (add references/, examples/, gotchas)
4. Create project CLAUDE.md (<200 lines)
5. Write setup.sh/setup.py install script
6. Write README.md
7. Clean up .gitignore
8. Verify pyproject.toml is complete

</code_context>

<specifics>
## Specific Ideas

- The quality audit is the most important part of this phase — functional code without good skill architecture produces a mediocre agent experience
- "Skills are folders, not files" is the single highest-impact improvement
- Each skill should have a `gotchas/` or gotchas section documenting known failure points discovered during Phases 1-5
- The /comfy-flow skill should feel like GSD's question → research → requirements → roadmap feedback loop, adapted for template creation

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-testing-distribution*
*Context gathered: 2026-03-19*
