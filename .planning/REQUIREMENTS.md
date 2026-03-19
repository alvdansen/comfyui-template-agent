# Requirements: ComfyUI Template Agent

**Defined:** 2026-03-18
**Core Value:** Template creators can go from "what should we build next?" to "here's a cloud-tested workflow with submission docs" in a single guided session

## v1 Requirements

### Discovery

- [x] **DISC-01**: User can browse trending/new/rising/popular/random nodes from the ComfyUI registry
- [x] **DISC-02**: User can search nodes by name, category, or input/output type
- [x] **DISC-03**: User can filter discovery by media category (video, image, audio, 3D, etc.)
- [x] **DISC-04**: User can view what nodes a custom node pack includes
- [x] **DISC-05**: User can get random node suggestions for idea sparking

### Template Intelligence

- [x] **TMPL-01**: User can search existing 400+ templates by name, category, or model
- [x] **TMPL-02**: User can view template details (nodes used, models, custom node dependencies)
- [x] **TMPL-03**: User can check if a specific node or pack is already used in an existing template
- [x] **TMPL-04**: User can generate gap analysis showing popular nodes not covered by any template
- [x] **TMPL-05**: User can view template coverage report by category

### Composition

- [x] **COMP-01**: User can scaffold a new workflow from an existing template and modify/extend it
- [x] **COMP-02**: User can compose valid workflow JSON from scratch via type-safe graph builder
- [x] **COMP-03**: User can compose workflows incrementally with per-step validation
- [x] **COMP-04**: Composed workflows use correct workflow format (not API format)

### Validation

- [x] **VALD-01**: User can check workflow for custom node usage and get core node alternatives suggested
- [x] **VALD-02**: User can detect API nodes in workflow and see auth requirement warnings
- [x] **VALD-03**: User can run full guideline compliance check (subgraph rules, color/note conventions, set/get node ban)
- [x] **VALD-04**: User can validate workflow for Comfy Cloud compatibility

### Documentation

- [x] **DOCS-01**: User can auto-generate index.json metadata entry from a workflow file
- [x] **DOCS-02**: User can generate Notion-friendly markdown for the submission process
- [x] **DOCS-03**: User can auto-extract IO spec (inputs/outputs) from workflow JSON
- [x] **DOCS-04**: User gets reminded about thumbnail/screenshot requirements with format specs

### Orchestration

- [x] **ORCH-01**: User can run guided phase flow: discover > ideate > compose > validate > document
- [x] **ORCH-02**: Each phase provides context-aware suggestions based on previous phase output

### Testing & Distribution

- [ ] **TEST-01**: All skills tested end-to-end with real ComfyUI workflows
- [ ] **TEST-02**: Install script sets up skills, symlinks, and dependencies for a new team member
- [ ] **TEST-03**: README documents all skills, setup instructions, and usage examples
- [ ] **TEST-04**: Repo is clean and ready for sharing (gitignore, no secrets, no temp files)

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
| DISC-01 | Phase 1 | Complete |
| DISC-02 | Phase 1 | Complete |
| DISC-03 | Phase 1 | Complete |
| DISC-04 | Phase 1 | Complete |
| DISC-05 | Phase 1 | Complete |
| TMPL-01 | Phase 2 | Complete |
| TMPL-02 | Phase 2 | Complete |
| TMPL-03 | Phase 2 | Complete |
| TMPL-04 | Phase 2 | Complete |
| TMPL-05 | Phase 2 | Complete |
| COMP-01 | Phase 4 | Complete |
| COMP-02 | Phase 4 | Complete |
| COMP-03 | Phase 4 | Complete |
| COMP-04 | Phase 4 | Complete |
| VALD-01 | Phase 3 | Complete |
| VALD-02 | Phase 3 | Complete |
| VALD-03 | Phase 3 | Complete |
| VALD-04 | Phase 3 | Complete |
| DOCS-01 | Phase 5 | Complete |
| DOCS-02 | Phase 5 | Complete |
| DOCS-03 | Phase 5 | Complete |
| DOCS-04 | Phase 5 | Complete |
| ORCH-01 | Phase 5 | Complete |
| ORCH-02 | Phase 5 | Complete |

**Coverage:**
- v1 requirements: 24 total
- Mapped to phases: 24
- Unmapped: 0

---
*Requirements defined: 2026-03-18*
*Last updated: 2026-03-18 after roadmap creation*
