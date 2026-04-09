---
phase: 13-content-cleanup
plan: 03
subsystem: docs
tags: [skill-md, standardization, example-sessions, capabilities]

# Dependency graph
requires:
  - phase: 13-content-cleanup
    plan: 01
    provides: Trimmed CLAUDE.md with skills table for name consistency
provides:
  - All 6 SKILL.md files standardized with Capabilities, Commands, Example Session, Key Constraints
affects: [13-04, 14-visual-assets]

# Tech tracking
tech-stack:
  added: []
  patterns: [standardized SKILL.md format, User/Agent example session convention]

key-files:
  modified:
    - .claude/skills/comfy-discover/SKILL.md
    - .claude/skills/comfy-template-audit/SKILL.md
    - .claude/skills/comfy-validate/SKILL.md
    - .claude/skills/comfy-compose/SKILL.md
    - .claude/skills/comfy-document/SKILL.md
    - .claude/skills/comfy-flow/SKILL.md

key-decisions:
  - "comfy-validate keeps ## Rules table between Commands and Example Session as reference exception"
  - "comfy-compose at 99 lines (above 80 target) due to 3 substantial <important> blocks -- acceptable"
  - "comfy-flow Commands section uses phase-labeled bash block instead of table format"
  - "Removed Two Starting Paths section from comfy-compose -- covered by Capabilities"

patterns-established:
  - "SKILL.md section order: frontmatter, title, [important blocks], Capabilities, Commands, Example Session, Key Constraints"
  - "Example sessions use **User:**/**Agent:** format with 3-4 turns"
  - "Every CLI command in Example Session must appear in Commands section"

requirements-completed: [CONTENT-08]

# Metrics
duration: 5min
completed: 2026-04-09
---

# Phase 13 Plan 03: SKILL.md Standardization Summary

**All 6 SKILL.md files standardized with consistent format: Capabilities bulleted list, Commands bash block, Example Session with User/Agent dialogue, and Key Constraints -- preserving all existing important blocks**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-09T10:11:40Z
- **Completed:** 2026-04-09T10:16:40Z
- **Tasks:** 1
- **Files modified:** 6

## Accomplishments

- Added ## Capabilities section to all 6 SKILL.md files (none had it before)
- Added ## Example Session with 3-4 turn User/Agent dialogues to all 6 files (none had it before)
- Standardized section ordering across all 6 files: frontmatter, title, important blocks, Capabilities, Commands, Example Session, Key Constraints
- Preserved all 3 `<important>` blocks in comfy-compose (prerequisites, cloud submission, workflow format conversion)
- Preserved `<important>` blocks in comfy-document (Notion page creation) and comfy-flow (cloud/local check)
- Removed ## Live Example from comfy-template-audit (inappropriate `!python` line)
- Converted comfy-flow Quick Reference table to bash code block with phase labels
- Removed `format_session_status` reference from comfy-flow (implementation detail)
- Removed "Two Starting Paths" section from comfy-compose (content folded into Capabilities)
- Verified all Example Session commands exist in Commands section of same file
- All 6 frontmatter `name:` fields match CLAUDE.md skills table entries
- No gotchas.md files modified (per D-12)
- 212 tests pass (regression verified)

## Task Commits

Each task was committed atomically:

1. **Task 1: Standardize all 6 SKILL.md files with capabilities and example sessions** - `b0ede9e` (feat)

## Files Created/Modified

- `.claude/skills/comfy-discover/SKILL.md` -- 55 lines (was 40). Added Capabilities, Example Session.
- `.claude/skills/comfy-template-audit/SKILL.md` -- 57 lines (was 44). Added Capabilities, Example Session. Removed Live Example.
- `.claude/skills/comfy-validate/SKILL.md` -- 63 lines (was 46). Added Capabilities, Example Session. Kept Rules table.
- `.claude/skills/comfy-compose/SKILL.md` -- 99 lines (was 89). Added Capabilities, Example Session. Preserved 3 important blocks. Removed Two Starting Paths.
- `.claude/skills/comfy-document/SKILL.md` -- 81 lines (was 64). Added Capabilities, Example Session. Preserved important block.
- `.claude/skills/comfy-flow/SKILL.md` -- 56 lines (was 45). Added Capabilities, Example Session. Converted table to bash block. Removed format_session_status.

## Decisions Made

- comfy-validate keeps the ## Rules table between Commands and Example Session -- the plan explicitly allowed this as an exception since the rules table is valuable reference
- comfy-compose lands at 99 lines (above the 50-80 target) because the 3 `<important>` blocks take ~50 lines alone -- preserving them was a hard requirement
- comfy-flow Commands section uses phase-labeled bash comments (`# Phase 1: Discover`) for clarity instead of the old table format
- Removed comfy-compose "Two Starting Paths" subsection -- the goal-based vs node-first distinction is now implicit in the Capabilities list

## Deviations from Plan

None -- plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None -- documentation-only changes.

## Next Phase Readiness

- All 6 SKILL.md files standardized for external audience
- Template READMEs remain (Plan 13-04)
- Cross-file consistency verified: skill names match CLAUDE.md table

## Self-Check: PASSED

- .claude/skills/comfy-discover/SKILL.md: FOUND
- .claude/skills/comfy-template-audit/SKILL.md: FOUND
- .claude/skills/comfy-validate/SKILL.md: FOUND
- .claude/skills/comfy-compose/SKILL.md: FOUND
- .claude/skills/comfy-document/SKILL.md: FOUND
- .claude/skills/comfy-flow/SKILL.md: FOUND
- Commit b0ede9e: FOUND

---
*Phase: 13-content-cleanup*
*Completed: 2026-04-09*
