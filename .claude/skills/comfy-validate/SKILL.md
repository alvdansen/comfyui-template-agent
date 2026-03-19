---
name: comfy-validate
description: "Validate ComfyUI workflow JSON files against template creation guidelines. Check cloud compatibility, custom node usage, and submission readiness."
---

# Skill: comfy-validate

Validate ComfyUI workflow JSON files against template creation guidelines.

## When to Use

- User wants to check if a workflow follows template creation guidelines
- User wants to verify cloud compatibility before submitting a template
- User wants to find custom nodes that could be replaced with core nodes
- User wants to detect API nodes and understand auth requirements

## How to Use

### Full validation (strict mode -- for submission)
```bash
python -m src.validator.validate --file path/to/workflow.json --mode strict
```

### Draft check (lenient mode -- errors only)
```bash
python -m src.validator.validate --file path/to/workflow.json --mode lenient
```

### Skip specific rules
```bash
python -m src.validator.validate --file path/to/workflow.json --ignore core_node_preference thumbnail_specs
```

## Available Rules

| Rule ID | What it checks | Severity |
|---------|---------------|----------|
| core_node_preference | Custom nodes that could be core | required |
| no_set_get_nodes | Set/Get node usage (banned) | required |
| cloud_compatible | Cloud deployment readiness | required |
| note_color_black | Note nodes have black background | required |
| api_node_color_yellow | API nodes have yellow color | required |
| unique_subgraph_names | No duplicate subgraph names | required |
| subgraph_rules | No Preview/Save inside subgraphs | required |
| naming_conventions | Template naming patterns | required |
| thumbnail_specs | Thumbnail format requirements | required |
| api_badge_position | Top-left corner clear | recommended |
| group_color_default | Default group colors | recommended |
| simplicity_readability | Workflow clarity | recommended |
| api_node_auth | API node auth requirements | warning |

## Output

Returns a validation report with:
- Overall PASS/FAIL status
- Score (rules passed / rules checked)
- Per-rule results with findings
- Fix suggestions for each issue
- Strict mode: all issues shown
- Lenient mode: only blocking errors shown

## Key Files

- `src/validator/validate.py` -- CLI entry point
- `src/validator/engine.py` -- Validation engine
- `src/validator/rules.py` -- Rule check functions
- `data/guidelines.json` -- Rule definitions
- `data/core_nodes.json` -- Core node whitelist
- `data/api_nodes.json` -- API node provider list
