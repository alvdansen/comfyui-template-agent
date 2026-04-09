# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v2.0 — Template Batch: Trending Node Coverage

**Shipped:** 2026-04-09
**Phases:** 5 | **Plans:** 5 | **Commits:** 11

### What Was Built
- 4 production-ready ComfyUI templates covering high-demand node packs with zero prior template coverage
- MelBandRoFormer audio stem separation (linear pipeline, 5 nodes)
- Florence2 vision AI captioning (multi-output, 6 nodes, auto-download model)
- GGUF quantized FLUX.1-schnell txt2img (9 nodes, consumer 8 GB VRAM target)
- Impact Pack face detailer (fan-out topology, 11 nodes, dual-pack dependency)
- Tooling fixes: audio core nodes in core_nodes.json, .gguf model detection in metadata.py
- Description Note nodes added to all 4 templates for in-editor documentation

### What Worked
- Existing v1.0 infrastructure (validator, composer, doc generator) handled all 4 templates without new Python code
- Tooling fixes as Phase 7 prerequisite prevented cascading validation issues in subsequent templates
- Independent template phases (8-11) allowed flexible execution order
- Build scripts per template enable reproducible workflow generation

### What Was Inefficient
- v2.0 phases executed outside normal GSD plan/execute cycle — no SUMMARY.md files or phase directories created, making automated progress tracking impossible
- MILESTONES.md accomplishments had to be reconstructed from git log rather than extracted from summaries
- No UAT/verification step for templates — relied on manual testing

### Patterns Established
- Template directory structure: `templates/{name}/` with workflow.json, index.json, notion.md, build.py
- Description Note nodes as standard practice for in-editor documentation
- Build scripts (build.py) for reproducible template generation from code

### Key Lessons
1. When work is done outside GSD execution, milestone archival loses automated stats — consider lightweight tracking even for rapid execution
2. Tooling fixes before content creation (Phase 7 → Phases 8-11) is the right dependency pattern — always fix infrastructure first
3. Four templates in a single milestone is a comfortable batch size — each template is independent enough to avoid blocking

### Cost Observations
- Commits: 11 (v2.0 range)
- Files changed: 24 (+4509/-1186 lines)
- Timeline: 2026-03-25 (single session for execution, planning started earlier)
- Notable: All template execution completed in one session — infrastructure investment in v1.0 paid off

---

## Milestone: v1.0 — MVP

**Shipped:** 2026-03-20
**Phases:** 6 | **Plans:** 14 | **Sessions:** ~1 hour total

### What Was Built
- 6 Claude Code skills covering full template creation workflow
- Python modules: shared infrastructure, registry discovery, template intelligence, validation engine, workflow composition, documentation generation
- Install script, README, E2E tests

### What Worked
- Phase-based GSD workflow kept scope focused
- Average 4.4 min/plan execution time
- Pydantic models + httpx + DiskCache as infrastructure choices

### What Was Inefficient
- Phase 4 (Composition) took longest at 22min / 3 plans — graph builder complexity
- Some early phases could have been combined (1+2 share data layer)

### Key Lessons
1. Small focused plans (avg 4.4 min) execute faster and more reliably than large monolithic ones
2. Shared infrastructure in Phase 1 pays dividends across all later phases

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Commits | Phases | Key Change |
|-----------|---------|--------|------------|
| v1.0 | ~30 | 6 | Full GSD plan/execute cycle, 14 granular plans |
| v2.0 | 11 | 5 | Rapid execution, existing infra reused, no new Python code |

### Top Lessons (Verified Across Milestones)

1. Infrastructure-first phases (Phase 1 in v1.0, Phase 7 in v2.0) prevent downstream issues — validated twice
2. Independent phases enable flexible execution — both milestones benefited from parallelizable work
