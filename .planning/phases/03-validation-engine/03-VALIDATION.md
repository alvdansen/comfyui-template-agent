---
phase: 3
slug: validation-engine
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (from Phase 1) |
| **Config file** | pyproject.toml (exists) |
| **Quick run command** | `python -m pytest tests/test_validator.py -x -q` |
| **Full suite command** | `python -m pytest tests/ -v --tb=short` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick command (phase-specific tests)
- **After every plan wave:** Run full suite (includes Phase 1+2 regression)
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 3-01-01 | 01 | 1 | VALD-01 | unit | `pytest tests/test_validator.py -k custom_node` | ⬜ pending |
| 3-01-02 | 01 | 1 | VALD-02 | unit | `pytest tests/test_validator.py -k api_node` | ⬜ pending |
| 3-01-03 | 01 | 1 | VALD-03 | unit | `pytest tests/test_validator.py -k guideline` | ⬜ pending |
| 3-01-04 | 01 | 1 | VALD-04 | unit | `pytest tests/test_validator.py -k cloud` | ⬜ pending |

---

## Wave 0 Requirements

- [ ] `tests/test_validator.py` — stubs for VALD-01 through VALD-04

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Fix suggestion relevance | VALD-01 | Suggestions are contextual | Review validation output for helpful vs generic suggestions |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
