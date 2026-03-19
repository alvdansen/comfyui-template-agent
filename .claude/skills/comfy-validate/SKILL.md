---
name: comfy-validate
description: "When the user has a workflow JSON and wants to check guideline compliance, cloud compatibility, or submission readiness"
---

# Workflow Validation

Validate ComfyUI workflow JSON against template creation guidelines.

## Commands

```bash
# Strict mode (for submission)
python -m src.validator.validate --file workflow.json --mode strict

# Lenient mode (drafts -- errors only, skips info-level rules)
python -m src.validator.validate --file workflow.json --mode lenient

# Skip specific rules
python -m src.validator.validate --file workflow.json --ignore core_node_preference thumbnail_specs
```

## Rules

| Rule ID | What it checks | Severity |
|---------|---------------|----------|
| core_node_preference | Custom nodes replaceable by core | required |
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

## Key Constraints

- Use strict mode for submissions, lenient for draft checks.
- API node detection runs separately from RULE_REGISTRY to keep auth concerns distinct.
- UUID-style node types (>30 chars with hyphens) are skipped in custom node detection -- these are subgraph references.
- Note color darkness check uses `#0` prefix heuristic.
