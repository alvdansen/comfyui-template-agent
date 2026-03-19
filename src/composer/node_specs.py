"""Node spec cache for composition engine.

The cache does NOT call MCP directly -- Claude fetches specs via MCP tools
and passes them in. This avoids the MCP-from-Python problem.
"""

from __future__ import annotations

from src.composer.models import NodeSpec, parse_node_spec


class NodeSpecCache:
    """In-memory cache for node specifications within a session."""

    def __init__(self) -> None:
        self._cache: dict[str, NodeSpec] = {}

    def get(self, node_type: str) -> NodeSpec | None:
        """Return cached spec or None if not cached."""
        return self._cache.get(node_type)

    def put(self, node_type: str, spec: NodeSpec) -> None:
        """Store a spec in the cache."""
        self._cache[node_type] = spec

    def has(self, node_type: str) -> bool:
        """Check if a spec is cached."""
        return node_type in self._cache

    def from_mcp_response(self, name: str, raw: dict) -> NodeSpec:
        """Parse an MCP get_node_info response and cache the result.

        Args:
            name: Node type name (e.g. "KSampler").
            raw: Raw dict from MCP get_node_info response.

        Returns:
            Parsed and cached NodeSpec.
        """
        spec = parse_node_spec(name, raw)
        self._cache[name] = spec
        return spec
