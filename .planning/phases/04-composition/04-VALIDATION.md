---
phase: 4
slug: composition
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (from Phase 1) |
| **Config file** | pyproject.toml (exists) |
| **Quick run command** | `python -m pytest tests/test_composer.py -x -q` |
| **Full suite command** | `python -m pytest tests/ -v --tb=short` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick command (phase-specific tests)
- **After every plan wave:** Run full suite (includes Phase 1-3 regression)
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 4-01-01 | 01 | 1 | COMP-02,04 | unit | `pytest tests/test_composer.py -k graph` | ⬜ pending |
| 4-01-02 | 01 | 1 | COMP-01 | unit | `pytest tests/test_composer.py -k scaffold` | ⬜ pending |
| 4-02-01 | 02 | 2 | COMP-03 | integration | `pytest tests/test_composer.py -k incremental` | ⬜ pending |

---

## Wave 0 Requirements

- [ ] `tests/test_composer.py` — stubs for COMP-01 through COMP-04

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Auto-layout visual quality | COMP-02 | Layout aesthetics subjective | Open composed workflow in ComfyUI, verify nodes don't overlap |
| Cloud submission flow | COMP-03 | Requires MCP + cloud auth | Run compose -> submit_workflow -> check cloud queue |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
