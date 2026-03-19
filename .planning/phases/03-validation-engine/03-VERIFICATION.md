---
phase: 03-validation-engine
verified: 2026-03-18T00:00:00Z
status: passed
score: 12/12 must-haves verified
re_verification: false
gaps: []
human_verification: []
---

# Phase 3: Validation Engine Verification Report

**Phase Goal:** Users can validate any workflow against template creation guidelines and get actionable fix suggestions
**Verified:** 2026-03-18
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Workflow with custom nodes returns findings listing each custom node and flagging it as non-core | VERIFIED | `check_core_node_preference` in rules.py flags non-core nodes as `Severity.warning`. `test_custom_node_detection` passes. |
| 2 | Workflow with API nodes returns findings identifying provider and auth requirements | VERIFIED | `detect_api_nodes` in api_nodes.py emits provider name + auth_type in suggestion. `test_api_node_detection` and `test_api_node_pattern_match` both pass. |
| 3 | Workflow with Set/Get nodes returns error-severity findings | VERIFIED | `check_no_set_get_nodes` matches {"SetNode","GetNode","Set","Get"} at `Severity.error`. `test_no_set_get_nodes` passes with 2 findings. |
| 4 | Workflow with non-black Note nodes returns error-severity findings | VERIFIED | `check_note_color_black` flags bgcolor/color not starting with `#0` at `Severity.error`. `test_note_color_black` passes. |
| 5 | Workflow with duplicate subgraph names returns error-severity findings | VERIFIED | `check_unique_subgraph_names` uses Counter to find duplicates at `Severity.error`. `test_unique_subgraph_names` passes. |
| 6 | Strict mode returns all findings; lenient mode returns only errors | VERIFIED | engine.py filters findings to `Severity.error` only when `mode == "lenient"`. `test_strict_lenient_modes` confirms lenient <= strict and all lenient findings are errors. |
| 7 | Rule suppression via ignore list skips specified rules | VERIFIED | engine.py builds `ignore_set` and skips matching rule IDs; increments `rules_skipped`. `test_rule_suppression` confirms zero `core_node_preference` findings and `rules_skipped >= 1`. |
| 8 | API-format JSON is rejected before any rule checks run | VERIFIED | `detect_format` called first in `run_validation`; returns early with `passed=False` and format error finding if not "workflow". `test_format_gate_rejects_api` passes. |
| 9 | User can run validation from CLI with --mode and --ignore flags | VERIFIED | validate.py implements argparse with `--file` (required), `--mode` (choices strict/lenient), `--ignore` (nargs=*). `--help` output confirmed. `test_cli_with_file` and `test_cli_ignore_flag` pass. |
| 10 | Validation report is human-readable with pass/fail icons and fix suggestions | VERIFIED | `format_report` emits `[PASS]/[FAIL]` per rule and `Fix:` per finding with suggestion. `test_format_report_fail` confirms `[ERROR]` + `Fix:` in output. |
| 11 | User can invoke validation via Claude Code skill /comfy-validate | VERIFIED | `.claude/skills/comfy-validate/SKILL.md` exists with correct frontmatter, usage examples for all three modes, rule table listing all 13 rules, and key file references. |
| 12 | Validation works on both local file paths and workflow JSON dicts | VERIFIED | `run_validation(workflow: dict)` accepts dict directly; `load_workflow(path)` handles file loading. CLI composes both. `test_load_workflow` + `test_cli_with_file` pass. |

**Score:** 12/12 truths verified

---

### Required Artifacts

| Artifact | Provides | Status | Details |
|----------|----------|--------|---------|
| `src/validator/__init__.py` | Package init | VERIFIED | File exists |
| `src/validator/models.py` | Pydantic models: Finding, RuleResult, ValidationReport, Severity | VERIFIED | All four classes present with correct fields |
| `src/validator/rules.py` | 12 rule check functions + RULE_REGISTRY + iter_all_nodes | VERIFIED | 12 functions registered in RULE_REGISTRY dict; `iter_all_nodes` generator yields top-level and subgraph nodes |
| `src/validator/api_nodes.py` | API node detection with provider + auth mapping | VERIFIED | `detect_api_nodes` + `load_api_node_data` present; exact + pattern matching implemented |
| `src/validator/engine.py` | Validation engine: compose rules, run validation, filter by mode | VERIFIED | `run_validation` with format gate, rule registry loop, lenient filter, api_node_auth result, and summary assembly |
| `data/api_nodes.json` | Curated API node provider list with auth types | VERIFIED | 7 providers (Gemini, BFL, Bria, ByteDance, ElevenLabs, Recraft, Luma); `auth_hidden_inputs` key present |
| `src/validator/validate.py` | CLI entry point, format_report, load_workflow | VERIFIED | All three functions present; argparse with `--file`, `--mode`, `--ignore`; exits 0/1 based on `report.passed` |
| `.claude/skills/comfy-validate/SKILL.md` | Claude Code skill definition for /comfy-validate | VERIFIED | Frontmatter with name/description; usage examples; 13-rule table; key files section |
| `tests/test_validator.py` | Tests for VALD-01 through VALD-04 | VERIFIED | 20 tests, 20 passing (0.17s) |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/validator/engine.py` | `src/validator/rules.py` | `from src.validator.rules import RULE_REGISTRY` | WIRED | Import present at line 6; RULE_REGISTRY iterated in rule loop |
| `src/validator/rules.py` | `data/core_nodes.json` | `json.load` in `_load_core_nodes()` | WIRED | `DATA_DIR / "core_nodes.json"` path resolved from `__file__`; used in `check_core_node_preference` |
| `src/validator/rules.py` | `src/shared/format_detector.py` | detect_format import | NOT WIRED (by design) | format_detector is imported in engine.py, not rules.py — this is architecturally correct. The key link in the PLAN was imprecise; the actual wiring is engine.py -> format_detector.py which is verified below. |
| `src/validator/engine.py` | `src/shared/format_detector.py` | `from src.shared.format_detector import detect_format` | WIRED | Import at line 3; called at line 27 as the format gate |
| `src/validator/engine.py` | `src/validator/api_nodes.py` | `from src.validator.api_nodes import detect_api_nodes` | WIRED | Import at line 4; called at line 77 to produce api_node_auth RuleResult |
| `src/validator/validate.py` | `src/validator/engine.py` | `from src.validator.engine import run_validation` | WIRED | Import at line 7; called in `main()` at line 86 |
| `.claude/skills/comfy-validate/SKILL.md` | `src/validator/validate.py` | `python -m src.validator.validate` CLI reference | WIRED | Pattern appears in three usage examples in SKILL.md |

Note: The PLAN key_link `from rules.py to format_detector.py` is not wired as written — format_detector is imported by engine.py instead. This is the correct design (format gate belongs in the engine layer, not in individual rule functions). No gap.

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| VALD-01 | 03-01, 03-02 | User can check workflow for custom node usage and get core node alternatives suggested | SATISFIED | `check_core_node_preference` flags non-core nodes with suggestion "Consider if a core ComfyUI node can achieve the same result". Verified by `test_custom_node_detection` and `test_custom_nodes_in_subgraphs`. |
| VALD-02 | 03-01, 03-02 | User can detect API nodes in workflow and see auth requirement warnings | SATISFIED | `detect_api_nodes` identifies 7 providers via known list + pattern match; suggestion includes auth_type. Verified by `test_api_node_detection` and `test_api_node_pattern_match`. |
| VALD-03 | 03-01, 03-02 | User can run full guideline compliance check (subgraph rules, color/note conventions, set/get node ban) | SATISFIED | `check_no_set_get_nodes`, `check_note_color_black`, `check_unique_subgraph_names`, `check_subgraph_rules` all implemented and tested. |
| VALD-04 | 03-01, 03-02 | User can validate workflow for Comfy Cloud compatibility | SATISFIED | `check_cloud_compatible` produces INFO reminder; format gate rejects API format; CLI exits 0/1 for automation. |

No orphaned requirements — REQUIREMENTS.md maps exactly VALD-01 through VALD-04 to Phase 3, all accounted for.

---

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| `src/validator/rules.py` | `check_cloud_compatible`, `check_thumbnail_specs`, `check_api_badge_position`, `check_simplicity_readability`, `check_naming_conventions` return static INFO findings regardless of workflow content | Info | Intentional design — these are reminder rules, not structural checks. Not a blocker. The PLAN explicitly described them as "INFO reminders". |

No placeholders, TODOs, or stub implementations found. No `return null`, `return {}`, or empty handlers. All rule functions produce substantive output.

---

### Human Verification Required

None. All phase behaviors are verifiable via automated tests and code inspection. The CLI, rule logic, and skill definition are fully machine-verifiable.

---

## Gaps Summary

No gaps. All 12 must-haves verified. All 4 requirements satisfied. All 20 tests passing in 0.17s. The validation engine is fully implemented, wired, and tested.

---

_Verified: 2026-03-18_
_Verifier: Claude (gsd-verifier)_
