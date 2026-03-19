# Phase 3: Validation Engine - Research

**Researched:** 2026-03-19
**Domain:** Workflow validation against ComfyUI template creation guidelines
**Confidence:** HIGH

## Summary

Phase 3 builds a validation engine that checks ComfyUI workflow JSON files against template creation guidelines. The domain is well-bounded: 12 structured rules already exist in `data/guidelines.json`, core node whitelist is in `data/core_nodes.json` (114 entries), format detection works in `src/shared/format_detector.py`, and node extraction (including subgraph recursion) works in `src/templates/cross_ref.py`. The research shows all four VALD requirements can be implemented with pure Python logic operating on workflow JSON -- no external API calls needed for the core validation path.

The API node auth detection (VALD-02) is the only area requiring a curated data file: a mapping of known API node class_types to their auth requirements. This comes from the MCP server report which documents the pattern: API nodes have hidden inputs `auth_token_comfy_org` and `api_key_comfy_org`. The known API node providers (Gemini, BFL, Bria, ByteDance, ElevenLabs, Recraft, Luma) are documented and can be pattern-matched.

**Primary recommendation:** Build a validator registry pattern where each guideline rule maps to a pure function `(workflow_dict) -> list[Finding]`. Compose validators into profiles (strict/lenient). Output a structured report with overall pass/fail, per-rule results, and fix suggestions.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Binary classification: core or custom** -- if it's not in `data/core_nodes.json`, it's custom. No "approved custom" tier.
- **Two modes: strict + lenient** -- strict for final submission (all rules enforced), lenient for drafts (only blockers/errors)
- **Rule suppression via flag** -- `--ignore core_node_preference` style flags to suppress specific rules when running validation
- Rules map to severity levels; lenient mode only reports errors, strict reports everything

### Claude's Discretion
- Validation report format and severity levels
- Core node alternative suggestion approach
- Cloud compatibility check depth
- API node detection method
- Rule engine architecture (registry pattern, chain of validators, etc.)
- How to load and apply `data/guidelines.json` rules programmatically
- Integration with existing `format_detector.py` as first validation step

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| VALD-01 | Check workflow for custom node usage and suggest core alternatives | Core nodes whitelist in `data/core_nodes.json`; `extract_node_types()` handles subgraph recursion; binary core/custom classification per locked decision |
| VALD-02 | Detect API nodes and show auth requirement warnings | Known API node patterns from MCP report; hidden input detection pattern (`auth_token_comfy_org`); curated provider list |
| VALD-03 | Full guideline compliance check (subgraph rules, color/note conventions, set/get ban, naming) | All 12 rules in `data/guidelines.json` with IDs, severity, descriptions; workflow JSON exposes node types, colors, titles for programmatic checking |
| VALD-04 | Cloud compatibility validation with pass/fail report | Combines VALD-01 (custom node flagging) + VALD-02 (API auth) + cloud_compatible rule; structured report output |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | >=2.0 | Validation models, report schema | Already in project; type-safe structured output |
| json (stdlib) | 3.12 | Load workflow/guidelines/core_nodes JSON | No external dependency needed |
| pathlib (stdlib) | 3.12 | File path handling | Cross-platform, already used in project |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| argparse (stdlib) | 3.12 | CLI entry point | Following established module pattern |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom validator functions | JSON Schema validation (jsonschema lib) | JSON Schema validates structure but can't check semantic rules like "no Set/Get nodes" or color conventions. Custom functions needed. |
| Flat function list | Plugin-based validator loading | Over-engineering for 12 rules. Registry dict is sufficient. |

**Installation:**
```bash
# No new dependencies needed -- uses existing pydantic + stdlib
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── validator/
│   ├── __init__.py
│   ├── models.py         # Pydantic models: Finding, RuleResult, ValidationReport
│   ├── rules.py          # Individual rule check functions
│   ├── engine.py         # Validator registry, compose + run, strict/lenient profiles
│   ├── api_nodes.py      # API node detection + auth requirement mapping
│   └── validate.py       # CLI entry point + format functions (argparse)
data/
├── api_nodes.json        # NEW: API node class_types -> provider + auth info
├── core_nodes.json       # EXISTS: 114 core node class_types
└── guidelines.json       # EXISTS: 12 rules with IDs and severity
```

### Pattern 1: Validator Registry
**What:** Each guideline rule from `data/guidelines.json` maps to a pure function with signature `(workflow: dict, config: dict) -> list[Finding]`. A registry dict maps rule IDs to functions. The engine iterates the registry, collects findings, and assembles the report.
**When to use:** Always -- this is the core architecture.
**Example:**
```python
from dataclasses import dataclass
from enum import Enum

class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class Finding:
    rule_id: str
    severity: Severity
    message: str
    node_id: int | None = None
    node_type: str = ""
    suggestion: str = ""

# Rule function signature
def check_no_set_get_nodes(workflow: dict, config: dict) -> list[Finding]:
    findings = []
    for node in workflow.get("nodes", []):
        node_type = node.get("type", "")
        if node_type in ("SetNode", "GetNode", "Set", "Get"):
            findings.append(Finding(
                rule_id="no_set_get_nodes",
                severity=Severity.ERROR,
                message=f"Set/Get node '{node_type}' found (node {node.get('id')})",
                node_id=node.get("id"),
                node_type=node_type,
                suggestion="Remove Set/Get nodes; use direct connections for clarity",
            ))
    return findings

# Registry
RULE_REGISTRY: dict[str, callable] = {
    "no_set_get_nodes": check_no_set_get_nodes,
    "core_node_preference": check_core_node_preference,
    # ... one entry per guideline rule
}
```

### Pattern 2: Strict/Lenient Profile
**What:** Map guideline severity to Finding severity. In lenient mode, filter to ERROR only. In strict mode, show everything.
**When to use:** CLI `--mode strict|lenient` flag.
**Example:**
```python
# guidelines.json severity -> Finding severity mapping
SEVERITY_MAP = {
    "required": Severity.ERROR,
    "recommended": Severity.WARNING,
}

def filter_findings(findings: list[Finding], mode: str) -> list[Finding]:
    if mode == "lenient":
        return [f for f in findings if f.severity == Severity.ERROR]
    return findings  # strict: all findings
```

### Pattern 3: Rule Suppression
**What:** `--ignore rule_id [rule_id ...]` skips specific rules from execution.
**When to use:** When a user intentionally violates a rule (e.g., using custom nodes for a specific reason).
**Example:**
```python
def run_validation(workflow: dict, mode: str = "strict", ignore: list[str] = None) -> ValidationReport:
    ignore = set(ignore or [])
    findings = []
    for rule_id, check_fn in RULE_REGISTRY.items():
        if rule_id in ignore:
            continue
        findings.extend(check_fn(workflow, config))
    return build_report(findings, mode)
```

### Pattern 4: Format Gate
**What:** `detect_format()` runs first. If format is "api" or "unknown", return immediately with a clear error. Validation only proceeds on "workflow" format.
**When to use:** Always -- first step in validation pipeline.

### Anti-Patterns to Avoid
- **LLM-based rule interpretation:** Do not pass guidelines.json descriptions to an LLM to "decide" if a workflow passes. Every rule must be a deterministic function.
- **Monolithic validate function:** Do not put all checks in one giant function. Each rule is its own function for testability.
- **Mutating the workflow:** Validators read-only. Never modify the input workflow dict.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Node type extraction from workflow JSON | Custom JSON walker | `extract_node_types()` from `src/templates/cross_ref.py` | Already handles subgraph recursion, UUID filtering |
| Format detection | Format-sniffing logic | `detect_format()` from `src/shared/format_detector.py` | Already tested, handles edge cases |
| Core node lookup | Inline set literal | Load `data/core_nodes.json` once as `frozenset` | Maintainable, already curated, 114 entries |
| Workflow loading | Custom file loader | `fetch_workflow_json()` from `src/templates/fetch.py` for remote, `json.load()` for local files | Handles .app suffix, caching |

**Key insight:** Most of the data plumbing already exists. The validation engine is primarily about writing rule check functions and composing them with a report formatter.

## Common Pitfalls

### Pitfall 1: Set/Get Node Name Variants
**What goes wrong:** Set/Get nodes may appear as different class_type strings across ComfyUI versions and custom node packs.
**Why it happens:** The core Set/Get nodes use `SetNode` and `GetNode` as class_types, but some custom node packs provide their own Set/Get implementations with different names.
**How to avoid:** Match on substring patterns: any node type containing "SetNode" or "GetNode", plus known variants like "Set" and "Get" from popular packs. Keep the match list in a constant, not inline.
**Warning signs:** Tests pass on fixture data but miss Set/Get nodes in real workflows.

### Pitfall 2: Subgraph Node Visibility
**What goes wrong:** Validators only check top-level `nodes[]` and miss custom nodes inside subgraphs (`definitions.subgraphs[].nodes[]`).
**Why it happens:** Easy to iterate only `workflow["nodes"]` and forget about subgraph internals.
**How to avoid:** Use `extract_node_types()` which already handles subgraph recursion. For rules that need per-node info (not just type), write a shared `iter_all_nodes(workflow)` generator that yields nodes from both levels.
**Warning signs:** Workflow with subgraphs passes validation but contains banned nodes inside subgraphs.

### Pitfall 3: Note Node Color Detection
**What goes wrong:** Checking note node colors requires reading `color` or `bgcolor` properties from the node dict. The exact field name and format (hex string vs named color) may vary.
**Why it happens:** ComfyUI workflow JSON stores visual properties differently depending on version and whether custom colors were set.
**How to avoid:** Check both `color` and `bgcolor` fields. Normalize to lowercase hex. Black is `#000000` or similar dark variants. The rule should check that note-type nodes do NOT have yellow/default coloring, rather than asserting exact black.
**Warning signs:** Color check passes when color field is absent (should default to a warning).

### Pitfall 4: API Node Detection False Positives
**What goes wrong:** Pattern-matching node names for "API" could flag nodes that aren't actually API nodes (e.g., a custom node with "API" in its name that doesn't require auth).
**Why it happens:** Using substring matching instead of a curated list.
**How to avoid:** Use a curated list of known API node class_types from the MCP report. The known providers are: Gemini (`GeminiImage2Node`, `GeminiFlashEdit`), BFL (FLUX Pro/Fill/Redux/Depth/Canny), Bria, ByteDance, ElevenLabs, Recraft, Luma. Store in `data/api_nodes.json` with provider name and auth type.
**Warning signs:** Non-API custom nodes flagged as requiring auth.

### Pitfall 5: Guideline Rules That Can't Be Checked Programmatically
**What goes wrong:** Some rules in `guidelines.json` are subjective or require visual inspection (e.g., `simplicity_readability`, `thumbnail_specs`, `api_badge_position`).
**Why it happens:** Not all guidelines are machine-checkable. They require human judgment.
**How to avoid:** Classify each rule as `automatable` or `manual_review`. For manual rules, the validator outputs an INFO-level reminder rather than a pass/fail check. Document which rules are automatable in the code.
**Warning signs:** Trying to write a deterministic check for "simplicity" -- this is a human judgment call.

## Code Examples

### Rule Automatability Classification

Based on `data/guidelines.json`, here is the breakdown:

| Rule ID | Automatable | Check Logic |
|---------|------------|-------------|
| `core_node_preference` | YES | Compare `extract_node_types()` against `core_nodes.json` set |
| `no_set_get_nodes` | YES | Scan node types for Set/Get variants |
| `cloud_compatible` | PARTIAL | Check for custom nodes (VALD-01) + API auth (VALD-02); actual cloud test is manual |
| `thumbnail_specs` | NO | Visual asset check -- reminder only |
| `api_badge_position` | NO | Visual layout check -- reminder only |
| `unique_subgraph_names` | YES | Collect subgraph names from `definitions.subgraphs`, check for duplicates with different internals |
| `subgraph_rules` | PARTIAL | Can detect Preview/Save nodes inside subgraphs; can't judge "practical significance" |
| `note_color_black` | YES | Check `color`/`bgcolor` on Note-type nodes |
| `api_node_color_yellow` | PARTIAL | Can check if API nodes have color set; can't verify exact yellow shade without knowing ComfyUI's palette |
| `group_color_default` | PARTIAL | Can check if groups have custom colors set; "default" means no color override |
| `simplicity_readability` | NO | Subjective -- reminder only |
| `naming_conventions` | PARTIAL | Can check template name format (no spaces, lowercase, etc.); can't verify "follows existing patterns" without template index |

### Known API Nodes Data Structure

```json
{
  "api_nodes": [
    {
      "class_type_pattern": "Gemini",
      "provider": "Google Gemini",
      "auth_type": "comfy_org_jwt",
      "known_nodes": ["GeminiImage2Node", "GeminiFlashEdit"]
    },
    {
      "class_type_pattern": "BFL",
      "provider": "Black Forest Labs",
      "auth_type": "comfy_org_jwt",
      "known_nodes": ["BFLFluxProGenerate", "BFLFluxFillGenerate", "BFLFluxReduxGenerate", "BFLFluxDepthGenerate", "BFLFluxCannyGenerate"]
    },
    {
      "class_type_pattern": "Bria",
      "provider": "Bria AI",
      "auth_type": "comfy_org_jwt",
      "known_nodes": []
    },
    {
      "class_type_pattern": "ByteDance",
      "provider": "ByteDance",
      "auth_type": "comfy_org_jwt",
      "known_nodes": []
    },
    {
      "class_type_pattern": "ElevenLabs",
      "provider": "ElevenLabs",
      "auth_type": "comfy_org_jwt",
      "known_nodes": []
    },
    {
      "class_type_pattern": "Recraft",
      "provider": "Recraft",
      "auth_type": "comfy_org_jwt",
      "known_nodes": []
    },
    {
      "class_type_pattern": "Luma",
      "provider": "Luma AI",
      "auth_type": "comfy_org_jwt",
      "known_nodes": []
    }
  ],
  "auth_hidden_inputs": ["auth_token_comfy_org", "api_key_comfy_org"],
  "source": "REPORT-COMFYUI-MCP.md + HANDOFF-MCP-IMPROVEMENTS.md"
}
```

### Validation Report Model

```python
from pydantic import BaseModel

class Finding(BaseModel):
    rule_id: str
    severity: str  # "error", "warning", "info"
    message: str
    node_id: int | None = None
    node_type: str = ""
    suggestion: str = ""

class RuleResult(BaseModel):
    rule_id: str
    rule_title: str
    passed: bool
    findings: list[Finding]

class ValidationReport(BaseModel):
    workflow_format: str  # "workflow", "api", "unknown"
    mode: str  # "strict", "lenient"
    passed: bool  # overall pass/fail
    score: str  # e.g., "8/10 rules passed"
    rules_checked: int
    rules_passed: int
    rules_failed: int
    rules_skipped: int  # suppressed via --ignore
    results: list[RuleResult]
    summary: list[Finding]  # top issues, fix-first ordering
```

### Report Format Function

```python
def format_report(report: ValidationReport) -> str:
    lines = []
    status = "PASS" if report.passed else "FAIL"
    lines.append(f"Validation Report [{status}] ({report.mode} mode)")
    lines.append(f"Score: {report.score}")
    lines.append("")

    # Fix-first: errors first, then warnings, then info
    for result in sorted(report.results, key=lambda r: (r.passed, r.rule_id)):
        icon = "PASS" if result.passed else "FAIL"
        lines.append(f"  [{icon}] {result.rule_title} ({result.rule_id})")
        for f in result.findings:
            lines.append(f"    [{f.severity.upper()}] {f.message}")
            if f.suggestion:
                lines.append(f"      Fix: {f.suggestion}")

    return "\n".join(lines)
```

### Iteration Helper for All Nodes

```python
def iter_all_nodes(workflow: dict):
    """Yield every node dict from top-level and all subgraphs."""
    for node in workflow.get("nodes", []):
        yield node
    for subgraph in workflow.get("definitions", {}).get("subgraphs", []):
        for node in subgraph.get("nodes", []):
            yield node
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Guidelines in Notion only | `data/guidelines.json` with 12 structured rules | Phase 1 (this project) | Machine-readable validation possible |
| Manual core node checking | `data/core_nodes.json` whitelist (114 entries) | Phase 1 (this project) | O(1) lookup for core/custom classification |
| No format detection | `detect_format()` in shared module | Phase 1 (this project) | Gate validation on correct format |

**No deprecated approaches to worry about** -- this is new functionality building on Phase 1/2 infrastructure.

## Open Questions

1. **Exact Set/Get node class_types**
   - What we know: Guidelines say "never use Set and Get nodes." The class_types in ComfyUI core are likely `SetNode` and `GetNode`.
   - What's unclear: Whether custom node packs provide variants with different class_types.
   - Recommendation: Start with `{"SetNode", "GetNode", "Set", "Get"}` and expand if real workflows reveal other variants. LOW risk -- easy to extend the set.

2. **Note node type string**
   - What we know: Note nodes need black background per guidelines.
   - What's unclear: Exact `type` string for Note nodes in workflow JSON (likely `"Note"` but could be `"Reroute"` or similar).
   - Recommendation: Check for `type == "Note"` and `type == "NoteNode"`. Verify against a real workflow with notes.

3. **API node detection completeness**
   - What we know: 7 providers documented in MCP report.
   - What's unclear: Whether new API node providers have been added since the report.
   - Recommendation: Use the known list plus pattern matching on hidden input names (`auth_token_comfy_org`). The curated list handles known cases; pattern matching catches new ones in workflows that include full node definitions.

4. **Core node alternative suggestions for VALD-01**
   - What we know: User wants suggestions when custom nodes are used.
   - What's unclear: Whether to maintain a curated mapping (custom_node -> core_alternative) or just flag without suggesting.
   - Recommendation: Flag custom nodes with a generic message ("Consider if a core node can achieve this"). A curated mapping would be high-maintenance and low-value for v1. The agent (Claude) can suggest alternatives conversationally.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >=9.0 |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `python -m pytest tests/test_validator.py -x` |
| Full suite command | `python -m pytest tests/ -x` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VALD-01 | Custom node detection + core alternative flagging | unit | `python -m pytest tests/test_validator.py::test_custom_node_detection -x` | Wave 0 |
| VALD-01 | Subgraph nodes included in custom check | unit | `python -m pytest tests/test_validator.py::test_custom_nodes_in_subgraphs -x` | Wave 0 |
| VALD-02 | API node detection with auth warnings | unit | `python -m pytest tests/test_validator.py::test_api_node_detection -x` | Wave 0 |
| VALD-02 | Unknown API node pattern matching | unit | `python -m pytest tests/test_validator.py::test_api_node_pattern_match -x` | Wave 0 |
| VALD-03 | Set/Get node ban check | unit | `python -m pytest tests/test_validator.py::test_no_set_get_nodes -x` | Wave 0 |
| VALD-03 | Note color convention check | unit | `python -m pytest tests/test_validator.py::test_note_color_black -x` | Wave 0 |
| VALD-03 | Subgraph name uniqueness check | unit | `python -m pytest tests/test_validator.py::test_unique_subgraph_names -x` | Wave 0 |
| VALD-03 | Subgraph content rules (preview/save outside) | unit | `python -m pytest tests/test_validator.py::test_subgraph_content_rules -x` | Wave 0 |
| VALD-04 | Cloud compatibility composite check | unit | `python -m pytest tests/test_validator.py::test_cloud_compatibility -x` | Wave 0 |
| VALD-04 | Strict vs lenient mode filtering | unit | `python -m pytest tests/test_validator.py::test_strict_lenient_modes -x` | Wave 0 |
| ALL | Format gate rejects API format | unit | `python -m pytest tests/test_validator.py::test_format_gate -x` | Wave 0 |
| ALL | Rule suppression via --ignore | unit | `python -m pytest tests/test_validator.py::test_rule_suppression -x` | Wave 0 |
| ALL | CLI entry point | integration | `python -m pytest tests/test_validator.py::test_cli -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_validator.py -x`
- **Per wave merge:** `python -m pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_validator.py` -- covers VALD-01 through VALD-04
- [ ] `data/api_nodes.json` -- curated API node provider list (test fixtures can inline this, but production needs the file)
- [ ] Conftest fixtures: `sample_workflow_with_custom_nodes`, `sample_workflow_with_api_nodes`, `sample_workflow_with_set_get`, `sample_workflow_with_notes`

## Sources

### Primary (HIGH confidence)
- `data/guidelines.json` -- 12 structured rules, read directly from project
- `data/core_nodes.json` -- 114 core node types, read directly from project
- `src/shared/format_detector.py` -- existing format detection, read directly
- `src/templates/cross_ref.py` -- `extract_node_types()` with subgraph handling, read directly
- `C:/Users/minta/Projects/comfyui/REPORT-COMFYUI-MCP.md` -- API node auth detection patterns, known providers
- `C:/Users/minta/Projects/comfyui/HANDOFF-MCP-IMPROVEMENTS.md` -- Firebase JWT auth flow details

### Secondary (MEDIUM confidence)
- `.planning/research/PITFALLS.md` -- domain pitfalls research from Phase 0
- `.planning/phases/03-validation-engine/03-CONTEXT.md` -- user decisions and canonical refs

### Tertiary (LOW confidence)
- Set/Get node exact class_type names -- inferred, needs validation against real workflows
- Note node type string -- inferred as "Note", needs verification
- API node provider completeness -- based on MCP report which may be outdated

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new dependencies, uses existing project infrastructure
- Architecture: HIGH -- validator registry is a well-understood pattern, all data sources exist
- Pitfalls: HIGH -- domain-specific, verified against actual code and data files
- Rule automatability: MEDIUM -- some rules need real workflow testing to confirm field names/formats

**Research date:** 2026-03-19
**Valid until:** 2026-04-19 (stable domain, no external API changes expected)
