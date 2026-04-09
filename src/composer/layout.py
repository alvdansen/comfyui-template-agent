"""Auto-layout algorithm for ComfyUI workflow graphs.

Assigns non-overlapping node positions using DAG layer assignment
with left-to-right flow. Source nodes appear to the left of their targets.
"""

from __future__ import annotations

from collections import defaultdict

from src.composer.graph import WorkflowGraph


def auto_layout(
    graph: WorkflowGraph,
    x_spacing: float = 400,
    y_spacing: float = 150,
    start_x: float = 100,
    start_y: float = 200,
) -> None:
    """Assign non-overlapping positions to all nodes using DAG layer assignment.

    Algorithm (left-to-right flow):
    1. Build adjacency from links (source -> targets).
    2. Find root nodes (no incoming connections).
    3. Assign layers via longest-path from roots. Roots get layer 0.
       Handles cycles by skipping back-edges.
    4. Group nodes by layer.
    5. Within each layer, sort by original vertical position.
    6. Assign positions: x = start_x + layer * x_spacing,
       y = start_y + row * y_spacing.

    Mutates node positions in place.

    Args:
        graph: The WorkflowGraph to layout.
        x_spacing: Horizontal distance between layers.
        y_spacing: Vertical distance between nodes in the same layer.
        start_x: X offset for the leftmost layer.
        start_y: Y offset for the topmost row.
    """
    nodes = graph.get_nodes()
    if not nodes:
        return

    node_ids = {n.id for n in nodes}
    links = graph._links

    # Build adjacency: source_id -> [target_ids]
    successors: dict[int, list[int]] = defaultdict(list)
    predecessors: dict[int, set[int]] = defaultdict(set)

    for link in links:
        if link.origin_node_id in node_ids and link.target_node_id in node_ids:
            successors[link.origin_node_id].append(link.target_node_id)
            predecessors[link.target_node_id].add(link.origin_node_id)

    # Find root nodes (no predecessors)
    roots = [nid for nid in node_ids if nid not in predecessors]

    # If no roots (cycle-only graph), pick all nodes as roots
    if not roots:
        roots = sorted(node_ids)

    # Assign layers using longest path (handles DAGs and breaks cycles)
    layers: dict[int, int] = {}
    visited: set[int] = set()

    def assign_layer(nid: int, current_layer: int, in_stack: set[int]) -> None:
        """DFS-based longest path assignment with cycle detection."""
        if nid in in_stack:
            # Back-edge detected (cycle) -- skip
            return
        if nid in layers and layers[nid] >= current_layer:
            # Already assigned a deeper layer -- skip
            return

        layers[nid] = current_layer
        visited.add(nid)
        in_stack.add(nid)

        for succ in successors.get(nid, []):
            assign_layer(succ, current_layer + 1, in_stack)

        in_stack.discard(nid)

    for root in sorted(roots):
        assign_layer(root, 0, set())

    # Assign any unvisited nodes (disconnected) to layer 0
    for nid in node_ids:
        if nid not in layers:
            layers[nid] = 0

    # Group nodes by layer
    layer_groups: dict[int, list[int]] = defaultdict(list)
    for nid, layer in layers.items():
        layer_groups[layer].append(nid)

    # Build a lookup for original vertical positions
    node_map = {n.id: n for n in nodes}

    # Sort within each layer by original vertical position
    for layer_idx in layer_groups:
        layer_groups[layer_idx].sort(
            key=lambda nid: node_map[nid].pos[1] if len(node_map[nid].pos) > 1 else 0
        )

    # Assign positions
    for layer_idx, node_ids_in_layer in layer_groups.items():
        for row, nid in enumerate(node_ids_in_layer):
            node_map[nid].pos = [
                start_x + layer_idx * x_spacing,
                start_y + row * y_spacing,
            ]
