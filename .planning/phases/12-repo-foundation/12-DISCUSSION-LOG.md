# Phase 12: Repo Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-09
**Phase:** 12-repo-foundation
**Areas discussed:** Author & attribution, Changelog depth, .gitignore scope

---

## Author & attribution

| Option | Description | Selected |
|--------|-------------|----------|
| Alvdansen Labs | Organization as sole author/copyright holder | ✓ |
| Timothy + Alvdansen | Individual credit under org umbrella | |
| Timothy solo | Personal ownership | |

**User's choice:** Alvdansen Labs
**Notes:** None

| Option | Description | Selected |
|--------|-------------|----------|
| timothy@promptcrafted.com | Existing email from global config | |
| No email | Omit from pyproject.toml | |

**User's choice:** timothy@comfy.org (custom input)
**Notes:** User provided a different email than the options presented

---

## Changelog depth

| Option | Description | Selected |
|--------|-------------|----------|
| Milestone summaries | 3-5 bullet points per milestone, ~20 lines | |
| Phase-level breakdown | Each phase listed, ~50 lines | |
| Keep a Changelog format | keepachangelog.com standard with Added/Changed/Fixed | ✓ |

**User's choice:** Keep a Changelog format
**Notes:** None

| Option | Description | Selected |
|--------|-------------|----------|
| Placeholder | Just "Unreleased" header, fill in later | |
| Pre-populated | List planned items now | ✓ |

**User's choice:** Pre-populated
**Notes:** User emphasized: "so long as 'may need updates' can be changed to 'I will be absolutely sure to continuously update as needed'"

---

## .gitignore scope

| Option | Description | Selected |
|--------|-------------|----------|
| Add .venv/ and .planning/ | Required by success criteria | ✓ |
| Add templates/*/build.py | Exclude if dev-only artifacts | |
| Add COMPAT-FIX.md | Exclude if scratch file | ✓ |
| Keep build.py files tracked | If they're part of deliverables | |

**User's choice:** Add .venv/ and .planning/, exclude COMPAT-FIX.md. User deferred build.py and COMPAT-FIX.md decisions to Claude's analysis.
**Notes:** User said "its your job to be perfectly thorough and safe and correct about this and know the difference"

**Claude's analysis result:**

| Option | Description | Selected |
|--------|-------------|----------|
| Track build.py, exclude COMPAT-FIX.md | Build scripts are core deliverables; COMPAT-FIX.md is internal | ✓ |
| Exclude both | Keep both out of public repo | |
| Track both | Include COMPAT-FIX.md as reference | |

**User's choice:** Agree — track build.py, exclude COMPAT-FIX.md

---

## Claude's Discretion

- pyproject.toml classifiers and keywords
- Exact CHANGELOG.md historical entry wording
- Additional .gitignore patterns for common artifacts

## Deferred Ideas

None — discussion stayed within phase scope
