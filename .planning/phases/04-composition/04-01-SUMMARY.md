---
phase: 04-composition
plan: 01
subsystem: composer
tags: [pydantic, graph-builder, type-checking, workflow-json, comfyui]

requires:
  - phase: 03-validation
    provides: format_detector for serialize output gate
provides:
  - WorkflowGraph class with add_node, connect, set_widget, remove_node, serialize
  - NodeSpec/InputSpec/OutputSpec/GraphNode/GraphLink Pydantic models
  - NodeSpecCache for in-memory session caching of MCP node specs
  - is_widget_input() and parse_node_spec() helpers for MCP response parsing
affects: [04-composition plans 02-03, scaffold, layout, compose CLI]

tech-stack:
  added: []
  patterns: [TDD red-green for composition, MCP-passthrough spec cache, type-checked graph connections]

key-files:
  created:
    - src/composer/__init__.py
    - src/composer/models.py
    - src/composer/node_specs.py
    - src/composer/graph.py
  modified:
    - tests/conftest.py
    - tests/test_composer.py

key-decisions:
  - "NodeSpecCache is pass-through only -- Claude fetches specs via MCP and passes them in, avoiding MCP-from-Python problem"
  - "GraphLink uses Pydantic model with to_array() method for clean serialization to workflow link format"
  - "widgets_values auto-populated by iterating spec required+optional inputs in order, skipping connection types"

patterns-established:
  - "MCP pass-through pattern: Python code never calls MCP directly; Claude fetches data and passes it in via constructors"
  - "Spec-driven node construction: add_node auto-populates inputs, outputs, and widgets_values from NodeSpec"
  - "Type-safe connections: connect() validates output/input type compatibility before creating links"

requirements-completed: [COMP-02, COMP-04]

duration: 4min
completed: 2026-03-19
---

# Phase 4 Plan 1: Core Graph Builder Summary

**Type-safe WorkflowGraph builder with Pydantic models, MCP-backed spec cache, auto-populated widgets_values, and workflow format serialization (version 0.4)**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-19T03:52:44Z
- **Completed:** 2026-03-19T03:57:06Z
- **Tasks:** 2 (both TDD)
- **Files modified:** 6

## Accomplishments
- Pydantic models for full composition domain: NodeSpec, InputSpec, OutputSpec, GraphNode, GraphLink
- is_widget_input() classifies 17 connection types vs 4 widget types + COMBO detection
- WorkflowGraph with add_node (auto-populates widgets_values from spec defaults), connect (type-checked), set_widget (COMBO/range validation), remove_node (link cleanup), serialize (workflow format with version 0.4)
- 47 composition tests pass, 166 total tests pass with no regressions

## Task Commits

Each task was committed atomically (TDD: test then implementation):

1. **Task 1: Composition models and node spec cache**
   - `5a70f4f` (test) - Failing tests for models and cache
   - `4aba3bf` (feat) - Implementation of models and cache
2. **Task 2: WorkflowGraph builder core**
   - `047aa7f` (test) - Failing tests for graph builder
   - `d12fe0b` (feat) - Implementation of graph builder

## Files Created/Modified
- `src/composer/__init__.py` - Package init
- `src/composer/models.py` - NodeSpec, InputSpec, OutputSpec, GraphNode, GraphLink models + is_widget_input, parse_node_spec helpers
- `src/composer/node_specs.py` - NodeSpecCache with get/put/has/from_mcp_response
- `src/composer/graph.py` - WorkflowGraph class with type-safe composition methods
- `tests/conftest.py` - Added sample_ksampler_spec, sample_loadimage_spec, sample_vaedecode_spec fixtures
- `tests/test_composer.py` - 47 tests covering models, cache, graph builder, type checking, serialization

## Decisions Made
- NodeSpecCache is pass-through: Claude fetches specs via MCP tools and passes raw dicts in, avoiding the MCP-from-Python problem identified in research
- GraphLink uses Pydantic BaseModel (not NamedTuple) with to_array() for clean serialization
- widgets_values auto-populated by iterating required+optional inputs in order, skipping connection-type inputs (matching ComfyUI's INPUT_TYPES ordering)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- WorkflowGraph ready for scaffold operations (Plan 02: from_json + swap_node + disconnect)
- NodeSpecCache ready for MCP integration in compose CLI (Plan 03)
- All 166 tests pass, clean baseline for next plans

---
*Phase: 04-composition*
*Completed: 2026-03-19*
