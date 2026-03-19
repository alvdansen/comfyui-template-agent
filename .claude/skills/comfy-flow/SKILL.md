---
name: comfy-flow
description: "Guided end-to-end template creation flow: discover trending nodes, ideate from gaps, compose workflows, validate against guidelines, and generate submission docs"
---

# Skill: comfy-flow

Guided template creation from idea to submission docs.

## When to Use

- User wants to create a new template from scratch with guidance
- User says "let's make a template" or "start a new template"
- User wants the full workflow: discover, ideate, compose, validate, document

## The Five Phases

| Phase | Skill | What Happens | Key Output |
|-------|-------|-------------|------------|
| 1. Discover | comfy-discover | Browse trending/new nodes, find interesting capabilities | List of promising nodes |
| 2. Ideate | comfy-templates | Check template coverage, find gaps worth filling | Template gap or concept |
| 3. Compose | comfy-compose | Build workflow JSON from scratch or scaffold from template | Valid workflow.json |
| 4. Validate | comfy-validate | Check guideline compliance, flag issues | Validation report (must pass) |
| 5. Document | comfy-document | Generate index.json entry, Notion markdown, thumbnail reminders | Submission-ready docs |

## How It Works

The flow maintains a session with context carried between phases. Claude tracks:
- Discovered nodes of interest
- Template gaps identified
- Composed workflow path and data
- Validation status
- Generated documentation

### Starting the Flow

```python
from src.document import FlowSession, FlowPhase, suggest_next_actions, format_session_status

session = FlowSession()
print(format_session_status(session))
```

This prints the current phase, progress, and suggested next actions.

### Phase 1: Discover

- Use comfy-discover skill commands to browse nodes
- When user finds interesting nodes, note them in session.discovered_nodes
- Suggest: `python3 -m src.registry.highlights --mode trending --limit 10`

### Phase 2: Ideate

- Use comfy-templates skill to check coverage and find gaps
- Cross-reference discovered nodes against existing templates
- When user identifies a gap or concept, note in session.template_gaps
- Suggest: `python3 -m src.templates.coverage --mode gaps`

### Phase 3: Compose

- Use comfy-compose skill to build the workflow
- If scaffolding from existing template, note session.scaffold_template
- Save to session.workflow_path when done
- Suggest: `python -m src.composer.compose --scaffold <template> --output workflow.json`

### Phase 4: Validate

- Run validation on composed workflow
- Must pass before proceeding to docs
- If issues found, fix and re-validate
- Suggest: `python -m src.validator.validate --file workflow.json`

### Phase 5: Document

- Generate index.json entry and Notion submission markdown
- Show thumbnail requirements
- Suggest: `python -m src.document.generate --file workflow.json --name my-template`

## Flexible Entry Points

Users can enter at any phase:
- "I already have a workflow, validate it" -- start at Phase 4
- "I have a validated workflow, generate docs" -- start at Phase 5
- "Show me what's trending" -- start at Phase 1

To start at a specific phase:
```python
session = FlowSession(phase=FlowPhase.validate, workflow_path="my-workflow.json")
```

## Context-Aware Suggestions

After each action, call `suggest_next_actions(session)` to get relevant next steps. The suggestions adapt based on:
- What the user has done so far (discovered nodes, gaps found, etc.)
- Current phase
- Validation status (blocks advancement if failed)

## Session Status

At any point, `format_session_status(session)` shows:
- Current phase (1-5)
- Checklist of completed phases
- Accumulated context (nodes, gaps, workflow path)
- Suggested next actions with concrete CLI commands

## Usage Examples

```
"Let's create a new template"
"Start the template creation flow"
"I want to make a video template using Wan 2.1"
"I have workflow.json ready, help me validate and document it"
"What's the next step?" (shows session status)
"Generate submission docs for my workflow"
```

## Key Behaviors

- Each phase builds on the previous one's output
- Validation must pass before documentation (but user can override with "skip validation")
- Thumbnail reminder is always shown during documentation phase
- Session state is in-memory (not persisted to disk) -- one continuous Claude Code conversation
- User can jump between phases freely; the flow is a guide, not a constraint

## Key Files

- `src/document/orchestrator.py` -- FlowSession, FlowPhase, advance_phase, suggest_next_actions, format_session_status
- `.claude/skills/comfy-discover/SKILL.md` -- Phase 1 skill
- `.claude/skills/comfy-templates/SKILL.md` -- Phase 2 skill
- `.claude/skills/comfy-compose/SKILL.md` -- Phase 3 skill
- `.claude/skills/comfy-validate/SKILL.md` -- Phase 4 skill (CLI: `python -m src.validator.validate`)
- `.claude/skills/comfy-document/SKILL.md` -- Phase 5 skill
