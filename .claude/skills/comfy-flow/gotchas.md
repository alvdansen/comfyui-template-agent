# comfy-flow Gotchas

## Phase Transitions Are Pure Functions
`advance_phase()` returns the next phase without mutating the session. You must assign it: `session.phase = advance_phase(session)`. Calling it alone does nothing.

## Validation Gate
Cannot advance from validate to document phase unless `session.validation_passed` is `True`. User can override by manually setting `session.phase = FlowPhase.document` ("skip validation").

## Session State Is In-Memory Only
`FlowSession` is a Pydantic model held in memory. It is NOT persisted to disk. If the Claude Code conversation ends, the session is lost. Design for single-conversation flows.

## CLI Prints Guidance, Not Error
When `compose` CLI is called without `--scaffold` or `--file`, it prints a guidance message directing to the Claude Code skill rather than raising an error. This is intentional.

## Flexible Entry Points
Users can start at any phase by constructing a session with pre-set fields:
```python
session = FlowSession(phase=FlowPhase.validate, workflow_path="my-workflow.json")
```
The flow does not enforce sequential progression -- it's a guide, not a constraint.

## suggest_next_actions Context Sensitivity
Suggestions adapt based on accumulated state (discovered_nodes, template_gaps, workflow_path, validation_passed). Empty state produces generic "get started" suggestions; populated state produces specific next steps with CLI commands.
