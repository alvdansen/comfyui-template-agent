"""Validation engine: compose rules, run validation, filter by mode."""

from src.shared.format_detector import detect_format
from src.validator.api_nodes import detect_api_nodes
from src.validator.models import Finding, RuleResult, Severity, ValidationReport
from src.validator.rules import RULE_REGISTRY, _load_guidelines


def run_validation(
    workflow: dict,
    mode: str = "strict",
    ignore: list[str] | None = None,
) -> ValidationReport:
    """Run all validation rules on a workflow.

    Args:
        workflow: ComfyUI workflow dict (must be workflow format, not API format).
        mode: 'strict' (all findings) or 'lenient' (only errors).
        ignore: List of rule IDs to skip.

    Returns:
        ValidationReport with all results.
    """
    ignore_set = set(ignore) if ignore else set()

    # Format gate
    fmt = detect_format(workflow)
    if fmt != "workflow":
        error_finding = Finding(
            rule_id="format_gate",
            severity=Severity.error,
            message=f"Expected workflow format, got '{fmt}'. Convert API format to workflow format before validating.",
        )
        return ValidationReport(
            workflow_format=fmt,
            mode=mode,
            passed=False,
            score="0/0 rules passed",
            rules_checked=0,
            rules_passed=0,
            rules_failed=0,
            rules_skipped=0,
            results=[],
            summary=[error_finding],
        )

    # Load guidelines for titles
    guidelines = _load_guidelines()

    results: list[RuleResult] = []
    skipped = 0

    for rule_id, rule_fn in RULE_REGISTRY.items():
        if rule_id in ignore_set:
            skipped += 1
            continue

        findings = rule_fn(workflow)

        # In lenient mode, keep only error-severity findings
        if mode == "lenient":
            findings = [f for f in findings if f.severity == Severity.error]

        guideline = guidelines.get(rule_id, {})
        title = guideline.get("title", rule_id)

        result = RuleResult(
            rule_id=rule_id,
            rule_title=title,
            passed=len(findings) == 0,
            findings=findings,
        )
        results.append(result)

    # API node detection as a separate rule result
    if "api_node_auth" not in ignore_set:
        api_findings = detect_api_nodes(workflow)
        if mode == "lenient":
            api_findings = [f for f in api_findings if f.severity == Severity.error]
        results.append(
            RuleResult(
                rule_id="api_node_auth",
                rule_title="API node authentication",
                passed=len(api_findings) == 0,
                findings=api_findings,
            )
        )
    else:
        skipped += 1

    # Compute totals
    checked = len(results)
    passed_count = sum(1 for r in results if r.passed)
    failed_count = checked - passed_count
    overall_passed = all(r.passed for r in results)

    # Build summary: flatten findings, sort by severity, take top 10
    severity_order = {Severity.error: 0, Severity.warning: 1, Severity.info: 2}
    all_findings = []
    for r in results:
        all_findings.extend(r.findings)
    all_findings.sort(key=lambda f: severity_order.get(f.severity, 3))
    summary = all_findings[:10]

    return ValidationReport(
        workflow_format=fmt,
        mode=mode,
        passed=overall_passed,
        score=f"{passed_count}/{checked} rules passed",
        rules_checked=checked,
        rules_passed=passed_count,
        rules_failed=failed_count,
        rules_skipped=skipped,
        results=results,
        summary=summary,
    )
