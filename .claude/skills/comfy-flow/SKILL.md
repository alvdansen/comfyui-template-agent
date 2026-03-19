---
name: comfy-flow
description: "When the user wants guided end-to-end template creation, or says anything like 'let's make a template' or 'start a new template'"
---

# Guided Template Creation

Orchestrates the full template creation pipeline: discover, ideate, compose, validate, document.

## The Five Phases

| Phase | Skill | Goal |
|-------|-------|------|
| 1. Discover | comfy-discover | Find interesting nodes |
| 2. Ideate | comfy-template-audit | Identify gaps worth filling |
| 3. Compose | comfy-compose | Build the workflow JSON |
| 4. Validate | comfy-validate | Pass guideline compliance |
| 5. Document | comfy-document | Generate submission docs |

<important>
At the start of any flow session, check `.env` for `COMFY_ORG_API_KEY`.

- **Cloud or local?** — ask the user. API node auth (Gemini, BFL, etc.) is handled automatically by the MCP server (v0.2.0+).
  For local execution, user must open ComfyUI in **browser** at `http://127.0.0.1:8188`.
</important>

## Key Constraints

- Validation gate blocks advancement to document phase -- user can override with "skip validation".
- Phase transitions are pure functions (`advance_phase` returns next phase, doesn't mutate session).
- Session state is in-memory only -- not persisted across conversations.
- Users can enter at any phase: "I have a workflow, validate it" starts at Phase 4.
- Context carries forward between phases: discovered nodes, gaps, workflow path, validation status.

## Quick Reference

| Phase | Key Command |
|-------|-------------|
| Discover | `python -m src.registry.highlights --mode trending --limit 10` |
| Ideate | `python -m src.templates.coverage gap --limit 20` |
| Compose | `python -m src.composer.compose --scaffold <template> --output workflow.json` |
| Validate | `python -m src.validator.validate --file workflow.json` |
| Document | `python -m src.document.generate --file workflow.json --name my-template` |

Use `format_session_status(session)` to show current phase, progress, and suggested next actions.
