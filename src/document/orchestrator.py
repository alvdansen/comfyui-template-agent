"""Orchestrator for guided template creation flow.

Manages session state across five phases: discover, ideate, compose,
validate, and document. Carries context between phases and provides
context-aware suggestions.
"""

from enum import Enum

from pydantic import BaseModel, Field


class FlowPhase(str, Enum):
    """Phases of the template creation flow."""

    discover = "discover"
    ideate = "ideate"
    compose = "compose"
    validate = "validate"
    document = "document"
    complete = "complete"


class FlowSession(BaseModel):
    """Tracks accumulated context through the guided template creation flow."""

    phase: FlowPhase = FlowPhase.discover
    discovered_nodes: list[str] = Field(default_factory=list)
    template_gaps: list[str] = Field(default_factory=list)
    scaffold_template: str = ""
    workflow_path: str = ""
    workflow_data: dict = Field(default_factory=dict)
    validation_passed: bool = False
    validation_issues: list[str] = Field(default_factory=list)
    index_entry: dict = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


_PHASE_ORDER = [
    FlowPhase.discover,
    FlowPhase.ideate,
    FlowPhase.compose,
    FlowPhase.validate,
    FlowPhase.document,
    FlowPhase.complete,
]


def advance_phase(session: FlowSession) -> FlowPhase:
    """Return the next logical phase without mutating the session.

    Validation must pass before advancing to document phase.
    Complete is a terminal state.
    """
    if session.phase == FlowPhase.complete:
        return FlowPhase.complete

    if session.phase == FlowPhase.validate and not session.validation_passed:
        return FlowPhase.validate

    idx = _PHASE_ORDER.index(session.phase)
    if idx + 1 < len(_PHASE_ORDER):
        return _PHASE_ORDER[idx + 1]
    return session.phase


def suggest_next_actions(session: FlowSession) -> list[str]:
    """Return context-aware suggestion strings based on current phase and state."""
    phase = session.phase

    if phase == FlowPhase.discover:
        if not session.discovered_nodes:
            return [
                "Run `python3 -m src.registry.highlights --mode trending` to see what's hot",
                "Try `python3 -m src.registry.highlights --mode random` for inspiration",
            ]
        first = session.discovered_nodes[0]
        return [
            f"Check template coverage: `python3 -m src.templates.cross_ref --query {first} --level pack`",
            "Move to ideation to find gaps",
        ]

    if phase == FlowPhase.ideate:
        if not session.template_gaps:
            suggestions = [
                "Run gap analysis: `python3 -m src.templates.coverage --mode gaps`",
            ]
            if session.discovered_nodes:
                suggestions.append(
                    f"Search templates: `python3 -m src.templates.search --query {session.discovered_nodes[0]}`"
                )
            return suggestions
        return [
            "Ready to compose! Pick a gap area and scaffold or build from scratch",
            "Scaffold from closest template: `python -m src.composer.compose --scaffold <name>`",
        ]

    if phase == FlowPhase.compose:
        if not session.workflow_path:
            return [
                "Compose a workflow using comfy-compose skill",
                "Or scaffold: `python -m src.composer.compose --scaffold <template> --output workflow.json`",
            ]
        return [
            f"Workflow saved to {session.workflow_path}. Run validation next.",
            "Move to validation to check guideline compliance",
        ]

    if phase == FlowPhase.validate:
        if not session.validation_passed:
            suggestions = [
                f"Fix issues and re-validate: `python -m src.validator.validate --file {session.workflow_path}`",
            ]
            for issue in session.validation_issues[:3]:
                suggestions.append(f"Issue: {issue}")
            return suggestions
        return [
            "Validation passed! Generate submission docs next.",
            f"Run: `python -m src.document.generate --file {session.workflow_path} --name <template-name>`",
        ]

    if phase == FlowPhase.document:
        return [
            "Generate index.json and Notion markdown",
            "Review thumbnail requirements",
            "Submit workflow to Comfy Cloud for testing",
        ]

    if phase == FlowPhase.complete:
        return ["Session complete! Your template is ready for submission."]

    return ["Continue with the current phase."]


def format_session_status(session: FlowSession) -> str:
    """Return a multi-line status string showing progress and suggestions."""
    phase_labels = {
        FlowPhase.discover: "(1/5)",
        FlowPhase.ideate: "(2/5)",
        FlowPhase.compose: "(3/5)",
        FlowPhase.validate: "(4/5)",
        FlowPhase.document: "(5/5)",
        FlowPhase.complete: "(done)",
    }

    label = phase_labels.get(session.phase, "")
    lines = [
        "## Template Creation Flow",
        "",
        f"**Current Phase:** {session.phase.value.title()} {label}",
        "",
        "### Progress",
    ]

    # Build checklist
    phase_past = _PHASE_ORDER.index(session.phase)
    checklist_phases = [
        (FlowPhase.discover, "Discover", f"({len(session.discovered_nodes)} nodes noted)" if session.discovered_nodes else ""),
        (FlowPhase.ideate, "Ideate", f"({len(session.template_gaps)} gaps found)" if session.template_gaps else ""),
        (FlowPhase.compose, "Compose", f"({session.workflow_path})" if session.workflow_path else ""),
        (FlowPhase.validate, "Validate", "(PASSED)" if session.validation_passed else ""),
        (FlowPhase.document, "Document", ""),
    ]

    for p, name, detail in checklist_phases:
        p_idx = _PHASE_ORDER.index(p)
        if p_idx < phase_past:
            mark = "x"
        elif p_idx == phase_past:
            mark = "~"
        else:
            mark = " "
        suffix = f" {detail}" if detail else ""
        lines.append(f"- [{mark}] {name}{suffix}")

    # Context section
    lines.append("")
    lines.append("### Context")
    if session.discovered_nodes:
        lines.append(f"**Nodes of interest:** {', '.join(session.discovered_nodes)}")
    if session.scaffold_template:
        lines.append(f"**Scaffolded from:** {session.scaffold_template}")
    if session.workflow_path:
        lines.append(f"**Workflow:** {session.workflow_path}")
    if session.validation_passed:
        lines.append("**Validation:** PASSED")
    elif session.validation_issues:
        lines.append("**Validation:** FAILED")

    # Suggestions
    suggestions = suggest_next_actions(session)
    lines.append("")
    lines.append("### Suggested Next Steps")
    for i, s in enumerate(suggestions, 1):
        lines.append(f"{i}. {s}")

    return "\n".join(lines)
