"""Tests for the orchestrator session state and phase transitions."""

from src.document.orchestrator import (
    FlowPhase,
    FlowSession,
    advance_phase,
    format_session_status,
    suggest_next_actions,
)


def test_flow_phase_order():
    """FlowPhase enum has 6 values in expected order."""
    phases = list(FlowPhase)
    assert len(phases) == 6
    assert phases == [
        FlowPhase.discover,
        FlowPhase.ideate,
        FlowPhase.compose,
        FlowPhase.validate,
        FlowPhase.document,
        FlowPhase.complete,
    ]


def test_advance_discover_to_ideate():
    """advance_phase from discover returns ideate."""
    session = FlowSession(phase=FlowPhase.discover)
    assert advance_phase(session) == FlowPhase.ideate


def test_advance_validate_blocks_on_failure():
    """advance_phase stays at validate when validation_passed is False."""
    session = FlowSession(phase=FlowPhase.validate, validation_passed=False)
    assert advance_phase(session) == FlowPhase.validate


def test_advance_validate_proceeds_on_pass():
    """advance_phase from validate goes to document when validation passed."""
    session = FlowSession(phase=FlowPhase.validate, validation_passed=True)
    assert advance_phase(session) == FlowPhase.document


def test_advance_complete():
    """advance_phase from complete stays at complete (terminal)."""
    session = FlowSession(phase=FlowPhase.complete)
    assert advance_phase(session) == FlowPhase.complete


def test_suggest_discover_empty():
    """Fresh session suggestions mention trending."""
    session = FlowSession()
    suggestions = suggest_next_actions(session)
    assert any("trending" in s for s in suggestions)


def test_suggest_discover_with_nodes():
    """Session with discovered nodes mentions cross_ref and the node."""
    session = FlowSession(discovered_nodes=["impact-pack"])
    suggestions = suggest_next_actions(session)
    assert any("cross_ref" in s for s in suggestions)
    assert any("impact-pack" in s for s in suggestions)


def test_suggest_validate_failed():
    """Failed validation suggestions mention Fix and the issue."""
    session = FlowSession(
        phase=FlowPhase.validate,
        validation_passed=False,
        validation_issues=["Custom node usage"],
        workflow_path="out.json",
    )
    suggestions = suggest_next_actions(session)
    assert any("Fix" in s for s in suggestions)
    assert any("Custom node usage" in s for s in suggestions)


def test_suggest_validate_passed():
    """Passed validation suggestions mention Generate and docs."""
    session = FlowSession(
        phase=FlowPhase.validate,
        validation_passed=True,
        workflow_path="out.json",
    )
    suggestions = suggest_next_actions(session)
    assert any("Generate" in s or "docs" in s for s in suggestions)


def test_format_session_status():
    """format_session_status includes phase name, node, and progress indicator."""
    session = FlowSession(
        phase=FlowPhase.compose,
        discovered_nodes=["test-node"],
    )
    status = format_session_status(session)
    assert "Compose" in status
    assert "test-node" in status
    assert "3/5" in status


def test_session_serialization():
    """FlowSession round-trips through model_dump and reconstruction."""
    session = FlowSession(
        phase=FlowPhase.ideate,
        discovered_nodes=["node-a", "node-b"],
        template_gaps=["video upscaling"],
        notes=["interesting concept"],
    )
    data = session.model_dump()
    restored = FlowSession(**data)
    assert restored.phase == FlowPhase.ideate
    assert restored.discovered_nodes == ["node-a", "node-b"]
    assert restored.template_gaps == ["video upscaling"]
    assert restored.notes == ["interesting concept"]
