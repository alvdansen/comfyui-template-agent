# Requirements: ComfyUI Template Agent

**Defined:** 2026-03-18
**Core Value:** Template creators can go from "what should we build next?" to "here's a cloud-tested workflow with submission docs" in a single guided session

## v1 Requirements

### Discovery

- [ ] **DISC-01**: User can browse trending/new/rising/popular/random nodes from the ComfyUI registry
- [ ] **DISC-02**: User can search nodes by name, category, or input/output type
- [ ] **DISC-03**: User can filter discovery by media category (video, image, audio, 3D, etc.)
- [ ] **DISC-04**: User can view what nodes a custom node pack includes
- [ ] **DISC-05**: User can get random node suggestions for idea sparking

### Template Intelligence

- [ ] **TMPL-01**: User can search existing 400+ templates by name, category, or model
- [ ] **TMPL-02**: User can view template details (nodes used, models, custom node dependencies)
- [ ] **TMPL-03**: User can check if a specific node or pack is already used in an existing template
- [ ] **TMPL-04**: User can generate gap analysis showing popular nodes not covered by any template
- [ ] **TMPL-05**: User can view template coverage report by category

### Composition

- [ ] **COMP-01**: User can scaffold a new workflow from an existing template and modify/extend it
- [ ] **COMP-02**: User can compose valid workflow JSON from scratch via type-safe graph builder
- [ ] **COMP-03**: User can compose workflows incrementally with per-step validation
- [ ] **COMP-04**: Composed workflows use correct workflow format (not API format)

### Validation

- [ ] **VALD-01**: User can check workflow for custom node usage and get core node alternatives suggested
- [ ] **VALD-02**: User can detect API nodes in workflow and see auth requirement warnings
- [ ] **VALD-03**: User can run full guideline compliance check (subgraph rules, color/note conventions, set/get node ban)
- [ ] **VALD-04**: User can validate workflow for Comfy Cloud compatibility

### Documentation

- [ ] **DOCS-01**: User can auto-generate index.json metadata entry from a workflow file
- [ ] **DOCS-02**: User can generate Notion-friendly markdown for the submission process
- [ ] **DOCS-03**: User can auto-extract IO spec (inputs/outputs) from workflow JSON
- [ ] **DOCS-04**: User gets reminded about thumbnail/screenshot requirements with format specs

### Orchestration

- [ ] **ORCH-01**: User can run guided phase flow: discover > ideate > compose > validate > document
- [ ] **ORCH-02**: Each phase provides context-aware suggestions based on previous phase output

## v2 Requirements

### Discovery

- **DISC-06**: User can compare nodes side-by-side (downloads, stars, features)
- **DISC-07**: User receives weekly digest of new nodes in subscribed categories

### Template Intelligence

- **TMPL-06**: User can generate template ideas based on community workflow trends
- **TMPL-07**: User can view template usage analytics from Comfy Cloud

### Composition

- **COMP-05**: User can create and manage reusable subgraph blueprints
- **COMP-06**: User can auto-generate App Mode metadata for templates

### Documentation

- **DOCS-05**: Direct Notion API integration for auto-creating submission pages
- **DOCS-06**: Auto-generate template description copy for marketing/social

## Out of Scope

| Feature | Reason |
|---------|--------|
| Running/testing workflows on Comfy Cloud | Users test manually via cloud UI -- automation requires auth complexity |
| Thumbnail generation or image processing | Outputs are workflow artifacts; visual assets handled by creators |
| OAuth/auth management for Comfy.org | Existing MCP server handles auth; this tool outputs workflows |
| Template review/approval workflow | Organizational process, not tooling scope |
| Mobile or web UI | Claude Code skills are the interface |
| Real-time collaboration | Single-user tool; team coordination via Notion |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DISC-01 | Phase 1 | Pending |
| DISC-02 | Phase 1 | Pending |
| DISC-03 | Phase 1 | Pending |
| DISC-04 | Phase 1 | Pending |
| DISC-05 | Phase 1 | Pending |
| TMPL-01 | Phase 2 | Pending |
| TMPL-02 | Phase 2 | Pending |
| TMPL-03 | Phase 2 | Pending |
| TMPL-04 | Phase 2 | Pending |
| TMPL-05 | Phase 2 | Pending |
| COMP-01 | Phase 4 | Pending |
| COMP-02 | Phase 4 | Pending |
| COMP-03 | Phase 4 | Pending |
| COMP-04 | Phase 4 | Pending |
| VALD-01 | Phase 3 | Pending |
| VALD-02 | Phase 3 | Pending |
| VALD-03 | Phase 3 | Pending |
| VALD-04 | Phase 3 | Pending |
| DOCS-01 | Phase 5 | Pending |
| DOCS-02 | Phase 5 | Pending |
| DOCS-03 | Phase 5 | Pending |
| DOCS-04 | Phase 5 | Pending |
| ORCH-01 | Phase 5 | Pending |
| ORCH-02 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 24 total
- Mapped to phases: 24
- Unmapped: 0

---
*Requirements defined: 2026-03-18*
*Last updated: 2026-03-18 after roadmap creation*
