# comfy-compose Gotchas

## NodeSpecCache Is Pass-Through
NodeSpecCache does NOT auto-fetch specs. You must call MCP `search_nodes`, get the raw dict, and feed it via `cache.from_mcp_response(name, raw)`. Without specs, `add_node` creates nodes with empty inputs/outputs/widgets.

## Link Format Compatibility
`from_json` supports both array format `[id, src, src_slot, tgt, tgt_slot, type]` and object format `{link_id, origin_node_id, ...}`. Different ComfyUI versions emit different formats. The graph handles both transparently.

## swap_node Graceful Degradation
When `swap_node` is called without a spec, it only updates the node type and `properties["Node name for S&R"]`. It does NOT rebuild inputs/outputs or remove incompatible connections. With a spec, it fully rebuilds and prunes broken links.

## auto_layout Algorithm
Uses DFS longest-path layer assignment. Works well for pipeline-style workflows but may produce suboptimal layouts for highly connected graphs (many cross-layer connections). Manual position adjustments may be needed.

## Lenient Validation on Save
`save_workflow` runs lenient validation by default because composed workflows are drafts. This means info-level issues (thumbnail specs, cloud compatibility reminders) are suppressed. Run strict validation separately before submission.

## Output Format Lock
`serialize()` always outputs workflow format (nodes[] + links[], version 0.4) and runs `detect_format()` as a safety assertion. It will never produce API format.

## Local Execution Requires Browser Mode
ComfyUI Desktop app does NOT expose an API endpoint. Claude Code cannot queue workflows to the Desktop app. The user must open ComfyUI in a browser at `http://127.0.0.1:8188` and log into Comfy.org there. Desktop app auth is separate from browser auth — being logged in on Desktop does NOT mean the browser session is authenticated.

## API Node Auth Is Automatic (v0.2.0+)
API node auth (Gemini, BFL, Bria, Luma, etc.) is handled automatically by the MCP server since v0.2.0. If jobs silently vanish (accepted but never execute), the MCP server likely needs updating. Previously this was an upstream gap — now resolved.

## Widget Value Resolution
`set_widget` resolves by name, not index. It counts only widget-type inputs (those with `is_widget=True`) in spec order. If a spec is not loaded for that node type, `set_widget` raises `KeyError`.
