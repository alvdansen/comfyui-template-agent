# comfy-validate Gotchas

## UUID-Style Node Types Skipped
Node types longer than 30 characters containing hyphens are treated as subgraph references and skipped in custom node detection. This avoids false positives but means actual custom nodes with long hyphenated names could be missed.

## API Node Detection Is Separate
`detect_api_nodes()` runs independently from `RULE_REGISTRY` to keep auth concerns distinct. Its findings feed into `check_api_node_color_yellow` but are not part of the standard rule loop.

## Note Color Darkness Heuristic
Note color check uses `#0` prefix to detect dark colors. This catches `#000000` through `#0FFFFF` but would miss dark colors like `#1A1A1A`. Edge case, but worth knowing.

## Lenient Mode Skips Info Rules
Lenient mode filters out `Severity.info` findings. Since `cloud_compatible`, `thumbnail_specs`, `simplicity_readability`, and `naming_conventions` are all info-level, they only appear in strict mode. Use strict for submissions.

## Core Node List May Be Stale
`data/core_nodes.json` is a static list (~179 nodes). ComfyUI adds new core nodes regularly. If a known core node gets flagged as custom, run `python scripts/update_core_nodes.py` to refresh from GitHub, or manually add it. API nodes (Gemini, BFL, etc.) are excluded from the custom node check automatically.

## Format Gating
Validation expects workflow format JSON (with `nodes` array). API format (string keys like `"3"`, `"4"`) is rejected before any rules run. Use `detect_format()` to check beforehand.
