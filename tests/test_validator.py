"""Tests for the validation engine (VALD-01 through VALD-04)."""

import json
import tempfile
from unittest import mock

import pytest

from src.validator.engine import run_validation
from src.validator.models import Finding, Severity, ValidationReport
from src.validator.validate import format_report, load_workflow, main

# -- Inline fixtures --

WORKFLOW_WITH_CUSTOM = {
    "nodes": [
        {"id": 1, "type": "KSampler"},
        {"id": 2, "type": "VAEDecode"},
        {"id": 3, "type": "SomeCustomNode"},
    ],
    "links": [],
}

WORKFLOW_WITH_API = {
    "nodes": [{"id": 1, "type": "GeminiImage2Node"}],
    "links": [],
}

WORKFLOW_WITH_SET_GET = {
    "nodes": [
        {"id": 1, "type": "SetNode"},
        {"id": 2, "type": "GetNode"},
    ],
    "links": [],
}

WORKFLOW_WITH_NOTES = {
    "nodes": [
        {"id": 1, "type": "Note", "color": "#ffff00", "bgcolor": "#ffff00"},
    ],
    "links": [],
}

WORKFLOW_ALL_CORE = {
    "nodes": [
        {"id": 1, "type": "KSampler"},
        {"id": 2, "type": "VAEDecode"},
        {"id": 3, "type": "SaveImage"},
    ],
    "links": [],
}

API_FORMAT = {"1": {"class_type": "KSampler", "inputs": {}}}

WORKFLOW_WITH_SUBGRAPH_CUSTOM = {
    "nodes": [{"id": 1, "type": "KSampler"}],
    "links": [],
    "definitions": {
        "subgraphs": [
            {
                "id": "sub-1",
                "name": "Upscale",
                "nodes": [
                    {"id": 10, "type": "SomeCustomNode"},
                ],
            }
        ]
    },
}

WORKFLOW_WITH_DUP_SUBGRAPHS = {
    "nodes": [{"id": 1, "type": "KSampler"}],
    "links": [],
    "definitions": {
        "subgraphs": [
            {"id": "sub-1", "name": "Upscale", "nodes": []},
            {"id": "sub-2", "name": "Upscale", "nodes": []},
        ]
    },
}

WORKFLOW_WITH_PREVIEW_IN_SUBGRAPH = {
    "nodes": [{"id": 1, "type": "KSampler"}],
    "links": [],
    "definitions": {
        "subgraphs": [
            {
                "id": "sub-1",
                "name": "Process",
                "nodes": [
                    {"id": 10, "type": "PreviewImage"},
                ],
            }
        ]
    },
}

WORKFLOW_WITH_BFL = {
    "nodes": [{"id": 1, "type": "BFLSomeNewNode"}],
    "links": [],
}


def test_format_gate_rejects_api():
    """API-format dict should be rejected before any rule checks run."""
    report = run_validation(API_FORMAT)
    assert isinstance(report, ValidationReport)
    assert report.passed is False
    assert report.workflow_format != "workflow"
    error_findings = [f for f in report.summary if f.severity == Severity.error]
    assert len(error_findings) >= 1
    assert "format" in error_findings[0].message.lower() or "api" in error_findings[0].message.lower()


def test_custom_node_detection():
    """Workflow with custom node should produce warning findings."""
    report = run_validation(WORKFLOW_WITH_CUSTOM)
    custom_findings = [
        f for f in _all_findings(report)
        if f.rule_id == "core_node_preference"
    ]
    assert len(custom_findings) == 1
    assert custom_findings[0].severity == Severity.warning
    assert "SomeCustomNode" in custom_findings[0].message


def test_custom_nodes_in_subgraphs():
    """Custom node inside a subgraph should be detected."""
    report = run_validation(WORKFLOW_WITH_SUBGRAPH_CUSTOM)
    custom_findings = [
        f for f in _all_findings(report)
        if f.rule_id == "core_node_preference" and "SomeCustomNode" in f.message
    ]
    assert len(custom_findings) >= 1


def test_api_node_detection():
    """Workflow with GeminiImage2Node should flag Google Gemini provider."""
    report = run_validation(WORKFLOW_WITH_API)
    api_findings = [
        f for f in _all_findings(report)
        if f.rule_id == "api_node_auth"
    ]
    assert len(api_findings) >= 1
    assert "Google Gemini" in api_findings[0].message


def test_api_node_pattern_match():
    """Node with BFL prefix should match via pattern."""
    report = run_validation(WORKFLOW_WITH_BFL)
    api_findings = [
        f for f in _all_findings(report)
        if f.rule_id == "api_node_auth"
    ]
    assert len(api_findings) >= 1
    assert "Black Forest Labs" in api_findings[0].message


def test_no_set_get_nodes():
    """SetNode and GetNode should produce error findings."""
    report = run_validation(WORKFLOW_WITH_SET_GET)
    sg_findings = [
        f for f in _all_findings(report)
        if f.rule_id == "no_set_get_nodes"
    ]
    assert len(sg_findings) == 2
    assert all(f.severity == Severity.error for f in sg_findings)


def test_note_color_black():
    """Note node with non-black background should produce error finding."""
    report = run_validation(WORKFLOW_WITH_NOTES)
    note_findings = [
        f for f in _all_findings(report)
        if f.rule_id == "note_color_black"
    ]
    assert len(note_findings) >= 1
    assert note_findings[0].severity == Severity.error


def test_unique_subgraph_names():
    """Two subgraphs named 'Upscale' should produce error finding."""
    report = run_validation(WORKFLOW_WITH_DUP_SUBGRAPHS)
    dup_findings = [
        f for f in _all_findings(report)
        if f.rule_id == "unique_subgraph_names"
    ]
    assert len(dup_findings) >= 1
    assert dup_findings[0].severity == Severity.error


def test_subgraph_content_rules():
    """PreviewImage inside subgraph should produce error finding."""
    report = run_validation(WORKFLOW_WITH_PREVIEW_IN_SUBGRAPH)
    sub_findings = [
        f for f in _all_findings(report)
        if f.rule_id == "subgraph_rules"
    ]
    assert len(sub_findings) >= 1
    assert sub_findings[0].severity == Severity.error


def test_cloud_compatibility():
    """Cloud compatibility check should produce combined results."""
    report = run_validation(WORKFLOW_ALL_CORE)
    # Should have a cloud_compatible rule result
    cloud_results = [r for r in report.results if r.rule_id == "cloud_compatible"]
    assert len(cloud_results) == 1


def test_strict_lenient_modes():
    """Strict returns all findings; lenient returns only errors."""
    strict_report = run_validation(WORKFLOW_WITH_CUSTOM, mode="strict")
    lenient_report = run_validation(WORKFLOW_WITH_CUSTOM, mode="lenient")
    strict_findings = _all_findings(strict_report)
    lenient_findings = _all_findings(lenient_report)
    # Lenient should have fewer or equal findings
    assert len(lenient_findings) <= len(strict_findings)
    # All lenient findings should be errors
    for f in lenient_findings:
        assert f.severity == Severity.error


def test_rule_suppression():
    """Passing ignore list should skip specified rules."""
    report = run_validation(WORKFLOW_WITH_CUSTOM, ignore=["core_node_preference"])
    custom_findings = [
        f for f in _all_findings(report)
        if f.rule_id == "core_node_preference"
    ]
    assert len(custom_findings) == 0
    assert report.rules_skipped >= 1


def test_all_core_nodes_pass():
    """Workflow with only core nodes should pass custom node check."""
    report = run_validation(WORKFLOW_ALL_CORE)
    custom_findings = [
        f for f in _all_findings(report)
        if f.rule_id == "core_node_preference"
    ]
    assert len(custom_findings) == 0


# -- CLI and report formatter tests --


def test_format_report_pass():
    """Passing report in lenient mode should show [PASS] header and per-rule pass icons."""
    # Use lenient mode so info-level findings (naming, thumbnail, etc.) are filtered out
    report = run_validation(WORKFLOW_ALL_CORE, mode="lenient")
    output = format_report(report)
    assert "Validation Report [PASS]" in output
    assert "[PASS]" in output


def test_format_report_fail():
    """Failing report should show [FAIL] header and fix suggestions."""
    report = run_validation(WORKFLOW_WITH_SET_GET)
    output = format_report(report)
    assert "Validation Report [FAIL]" in output
    assert "[FAIL]" in output
    assert "[ERROR]" in output
    # Set/Get nodes have suggestions
    assert "Fix:" in output


def test_format_report_skipped():
    """Skipped rules should show skip count."""
    report = run_validation(WORKFLOW_ALL_CORE, ignore=["core_node_preference", "no_set_get_nodes"])
    output = format_report(report)
    assert "skipped via --ignore" in output


def test_load_workflow():
    """load_workflow should parse a JSON file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(WORKFLOW_ALL_CORE, f)
        f.flush()
        loaded = load_workflow(f.name)
    assert loaded == WORKFLOW_ALL_CORE


def test_load_workflow_file_not_found():
    """load_workflow should raise FileNotFoundError for missing files."""
    with pytest.raises(FileNotFoundError):
        load_workflow("/nonexistent/path/workflow.json")


def test_cli_with_file():
    """CLI main() should run without exception on valid workflow."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(WORKFLOW_ALL_CORE, f)
        f.flush()
        tmpfile = f.name

    with mock.patch("sys.argv", ["prog", "--file", tmpfile, "--mode", "lenient"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Should exit 0 (pass) for all-core workflow in lenient mode
        assert exc_info.value.code == 0


def test_cli_ignore_flag():
    """CLI --ignore should suppress specified rules in output."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(WORKFLOW_WITH_CUSTOM, f)
        f.flush()
        tmpfile = f.name

    with mock.patch("sys.argv", ["prog", "--file", tmpfile, "--ignore", "core_node_preference", "no_set_get_nodes"]):
        with mock.patch("builtins.print") as mock_print:
            with pytest.raises(SystemExit):
                main()
            printed = mock_print.call_args[0][0]
            assert "core_node_preference" not in printed or "skipped" in printed
            assert "skipped via --ignore" in printed


# -- Helpers --

def _all_findings(report: ValidationReport) -> list[Finding]:
    """Flatten all findings from all rule results."""
    findings = []
    for result in report.results:
        findings.extend(result.findings)
    return findings
