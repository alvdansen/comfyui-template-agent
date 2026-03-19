---
phase: 1
slug: foundation-discovery
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-18
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | pyproject.toml (Wave 0 creates) |
| **Quick run command** | `python -m pytest tests/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -v --tb=short` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -v --tb=short`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | DISC-01 | integration | `pytest tests/test_registry.py -k trending` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 1 | DISC-02 | integration | `pytest tests/test_registry.py -k search` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 1 | DISC-03 | unit | `pytest tests/test_registry.py -k category` | ❌ W0 | ⬜ pending |
| 1-01-04 | 01 | 1 | DISC-04 | integration | `pytest tests/test_registry.py -k pack` | ❌ W0 | ⬜ pending |
| 1-01-05 | 01 | 1 | DISC-05 | unit | `pytest tests/test_registry.py -k random` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_registry.py` — stubs for DISC-01 through DISC-05
- [ ] `tests/conftest.py` — shared fixtures (mock API responses, cache dir)
- [ ] `pyproject.toml` — pytest configuration + project metadata
- [ ] `pytest` + `httpx` + `pydantic` — dev dependencies

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Progressive detail display | DISC-01 | Output formatting is subjective | Run discovery, verify summary vs detailed output |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
