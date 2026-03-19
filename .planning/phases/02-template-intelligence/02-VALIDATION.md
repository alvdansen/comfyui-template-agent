---
phase: 2
slug: template-intelligence
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (from Phase 1) |
| **Config file** | pyproject.toml (exists) |
| **Quick run command** | `python -m pytest tests/test_templates.py tests/test_coverage.py -x -q` |
| **Full suite command** | `python -m pytest tests/ -v --tb=short` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick command (phase-specific tests)
- **After every plan wave:** Run full suite (includes Phase 1 regression)
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 2-01-01 | 01 | 1 | TMPL-01 | integration | `pytest tests/test_templates.py -k search` | ⬜ pending |
| 2-01-02 | 01 | 1 | TMPL-02 | integration | `pytest tests/test_templates.py -k detail` | ⬜ pending |
| 2-01-03 | 01 | 1 | TMPL-03 | integration | `pytest tests/test_cross_ref.py -k cross_ref` | ⬜ pending |
| 2-02-01 | 02 | 2 | TMPL-04 | integration | `pytest tests/test_coverage.py -k gap` | ⬜ pending |
| 2-02-02 | 02 | 2 | TMPL-05 | integration | `pytest tests/test_coverage.py -k coverage` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_templates.py` — stubs for TMPL-01, TMPL-02, TMPL-03
- [ ] `tests/test_coverage.py` — stubs for TMPL-04, TMPL-05

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Template suggestion quality | TMPL-04 | LLM-generated suggestions are subjective | Review gap analysis output for suggestion relevance |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
