# comfy-document Gotchas

## Model Detection Heuristic
Model detection looks for nodes with `Load` in the type name, then checks `widgets_values` for strings containing `/` or ending with model extensions (`.safetensors`, `.ckpt`, `.pt`, `.pth`, `.bin`). Non-standard loaders without `Load` in the name will be missed.

## extract_node_types Reuse
Custom node detection uses `extract_node_types` from `src.templates.fetch` for consistency with template cross-referencing. This is the same function used in Phase 2 -- ensures custom node lists match across skills.

## Format Gating
`generate_index_entry` rejects API-format JSON (must have `nodes` array, not string keys). Check with `detect_format()` first. API-format workflows must be converted before documentation can be generated.

## Subgraph IO Extraction
IO extraction (`extract_io_spec`) looks inside `definitions.subgraphs[].nodes` but does NOT recurse into nested subgraphs (subgraphs within subgraphs). Single-level depth only.

## UUID Node Type Filtering
Custom node detection excludes UUID-pattern types (matching `^[0-9a-f]{8}-...`) since these are subgraph references, not actual custom nodes.

## Media Type Priority
`_detect_media_type` checks in order: video > audio > image. If a workflow has both `SaveImage` and `VHS_VideoCombine`, it's classified as video.
