# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.0] - 2026-04-17

### Added
- MIT LICENSE and complete pyproject.toml metadata for public release
- CHANGELOG.md documenting project history
- README rewritten for external engineering audience
- CONTRIBUTING.md with dev setup, code style, and skill authoring guide
- AGENTS.md following 2026 Linux Foundation standard
- Architecture diagram (Excalidraw SVG/PNG)
- Slide deck for Comfy-Org Research Phase presentation
- GitHub Actions CI with parallel lint and test jobs
- GitHub issue templates (bug report, feature request)
- Demo GIF showing end-to-end skill invocation
- HANDOFF.md evaluation guide for Comfy-Org developers

### Changed
- CLAUDE.md trimmed for external contributors (removed internal GSD enforcement)
- All 6 SKILL.md files standardized with trigger, capabilities, example sessions, and gotchas
- Template READMEs added to all 4 template directories
- Repository published under Alvdansen Labs organization

## [2.0.0] - 2026-04-09

### Added
- MelBandRoFormer audio stem separation template (5 nodes, linear pipeline)
- Florence2 vision AI captioning/detection template (6 nodes, multi-output)
- GGUF quantized FLUX.1-schnell txt2img template (9 nodes, consumer VRAM target)
- Impact Pack face detection and auto-detailing template (11 nodes, fan-out topology)
- Description Note nodes in all 4 templates for in-editor documentation
- Build scripts (build.py) per template for reproducible workflow generation

### Fixed
- Audio core nodes missing from core_nodes.json
- GGUF model detection in metadata.py

## [1.0.0] - 2026-03-20

### Added
- 6 Claude Code skills: discover, template-audit, validate, compose, document, flow
- Shared infrastructure: HTTP client (httpx), disk caching, format detection
- Registry module: trending/new/rising node discovery, search, node pack specs
- Template intelligence: library browsing, cross-referencing, coverage gap analysis
- Validation engine: 12 rule checks, strict/lenient modes, API node detection
- Composition module: type-safe workflow graph builder, scaffolding, layout
- Documentation generator: index.json, Notion markdown, metadata extraction
- Guided orchestrator (/comfy-flow): end-to-end template creation workflow
- Install script (setup.sh) for team onboarding
- 212 tests passing in 0.5 seconds
