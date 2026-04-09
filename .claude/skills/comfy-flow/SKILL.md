---
name: comfy-flow
description: "When the user wants guided end-to-end template creation, or says anything like 'let's make a template' or 'start a new template'"
---

# Guided Template Creation

Orchestrates the full template creation pipeline: discover, ideate, compose, validate, document.

<important>
At the start of any flow session, check `.env` for `COMFY_ORG_API_KEY`.

- **Cloud or local?** — ask the user. API node auth (Gemini, BFL, etc.) is handled automatically by the MCP server (v0.2.0+).
  For local execution, user must open ComfyUI in **browser** at `http://127.0.0.1:8188`.
</important>

## Capabilities

- Guide users through the complete 5-phase template creation pipeline
- Discover trending nodes and identify template gaps
- Compose workflows with validation gates between phases
- Generate submission documentation at the end
- Allow entry at any phase (skip discovery if user already has a workflow)
- Carry context forward between phases (discovered nodes, gaps, workflow path)

## Commands

```bash
# Phase 1: Discover
python -m src.registry.highlights --mode trending --limit 10
# Phase 2: Ideate
python -m src.templates.coverage gap --limit 20
# Phase 3: Compose
python -m src.composer.compose --scaffold <template> --output workflow.json
# Phase 4: Validate
python -m src.validator.validate --file workflow.json
# Phase 5: Document
python -m src.document.generate --file workflow.json --name my-template
```

## Example Session

**User:** Let's make a new template
**Agent:** Starting guided template creation. Phase 1: Discover. Running `python -m src.registry.highlights --mode trending --limit 10`. Here are the top trending node packs -- any catch your eye?
**User:** The MelBandRoFormer audio separation looks interesting
**Agent:** Phase 2: Ideate. Running gap analysis -- no existing template for ComfyUI-MelBandRoFormer (240K downloads). Strong candidate. Moving to Phase 3: Compose. Fetching node specs and building workflow...
**User:** Looks good, validate and generate docs
**Agent:** Phase 4: Validate -- all rules pass. Phase 5: Document -- generated index.json and submission markdown. Created Notion page. Thumbnail reminder: 1:1 ratio, audio waveform visualization. Template ready for submission.

## Key Constraints

- Validation gate blocks advancement to document phase -- user can override with "skip validation".
- Phase transitions are pure functions (`advance_phase` returns next phase, doesn't mutate session).
- Session state is in-memory only -- not persisted across conversations.
- Users can enter at any phase: "I have a workflow, validate it" starts at Phase 4.
- Context carries forward between phases: discovered nodes, gaps, workflow path, validation status.
