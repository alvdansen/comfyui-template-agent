"""Pydantic models for the validation engine."""

from enum import Enum

from pydantic import BaseModel


class Severity(str, Enum):
    """Severity level for validation findings."""

    error = "error"
    warning = "warning"
    info = "info"


class Finding(BaseModel):
    """A single validation finding."""

    rule_id: str
    severity: Severity
    message: str
    node_id: int | None = None
    node_type: str = ""
    suggestion: str = ""


class RuleResult(BaseModel):
    """Result of running a single rule check."""

    rule_id: str
    rule_title: str
    passed: bool
    findings: list[Finding]


class ValidationReport(BaseModel):
    """Complete validation report."""

    workflow_format: str
    mode: str
    passed: bool
    score: str
    rules_checked: int
    rules_passed: int
    rules_failed: int
    rules_skipped: int
    results: list[RuleResult]
    summary: list[Finding]
