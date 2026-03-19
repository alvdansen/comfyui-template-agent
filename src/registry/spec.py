"""Inspect ComfyUI node packs to see individual nodes with I/O specs."""

import argparse
import json

from src.registry.models import ComfyNode, ComfyNodeResult
from src.shared.cache import DiskCache
from src.shared.config import CACHE_TTLS
from src.shared.http import fetch_json, get_client

_cache = DiskCache()


def get_pack_nodes(node_pack_id: str, limit: int = 100) -> list[ComfyNode]:
    """Fetch all individual nodes for a node pack, with caching and pagination."""
    cache_key = f"spec_{node_pack_id}"
    cached = _cache.get(cache_key, CACHE_TTLS["spec"])
    if cached is not None:
        return [ComfyNode(**n) for n in cached]

    all_nodes: list[ComfyNode] = []
    page = 1

    client = get_client()
    try:
        while True:
            data = fetch_json(
                client, "/comfy-nodes",
                params={"node_id": node_pack_id, "limit": limit, "page": page},
            )
            result = ComfyNodeResult(**data)
            all_nodes.extend(result.comfy_nodes)

            if len(all_nodes) >= result.total:
                break
            page += 1
    finally:
        client.close()

    _cache.set(cache_key, [n.model_dump() for n in all_nodes])
    return all_nodes


def format_pack_detail(
    pack_id: str,
    nodes: list[ComfyNode],
    summary: bool = True,
) -> str:
    """Format node pack inspection results.

    Summary mode: node count and names grouped by category.
    Detail mode: full I/O specifications for each node.
    """
    if not nodes:
        return f"No nodes found for pack '{pack_id}'."

    lines = [f"## {pack_id} ({len(nodes)} nodes)\n"]

    if summary:
        # Group by category
        by_category: dict[str, list[ComfyNode]] = {}
        for n in nodes:
            cat = n.category or "uncategorized"
            by_category.setdefault(cat, []).append(n)

        for cat in sorted(by_category.keys()):
            cat_nodes = by_category[cat]
            lines.append(f"### {cat} ({len(cat_nodes)})")
            for n in sorted(cat_nodes, key=lambda x: x.comfy_node_name):
                status = ""
                if n.deprecated:
                    status = " [DEPRECATED]"
                elif n.experimental:
                    status = " [EXPERIMENTAL]"
                lines.append(f"  - {n.comfy_node_name}{status}")
            lines.append("")
    else:
        # Full detail mode
        for n in sorted(nodes, key=lambda x: x.comfy_node_name):
            status = ""
            if n.deprecated:
                status = " [DEPRECATED]"
            elif n.experimental:
                status = " [EXPERIMENTAL]"

            lines.append(f"### {n.comfy_node_name}{status}")
            lines.append(f"Category: {n.category}")

            inputs = n.parsed_input_types()
            if inputs:
                lines.append("Inputs:")
                for section_name, section in inputs.items():
                    if isinstance(section, dict):
                        lines.append(f"  {section_name}:")
                        for param, type_info in section.items():
                            if isinstance(type_info, list) and type_info:
                                lines.append(f"    - {param}: {type_info[0]}")
                            else:
                                lines.append(f"    - {param}: {type_info}")

            returns = n.parsed_return_types()
            if returns:
                names = n.return_names
                lines.append(f"Returns: {returns}")
                if names:
                    lines.append(f"Return names: {names}")

            lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect a ComfyUI node pack")
    parser.add_argument("node_pack_id", help="Node pack ID (e.g. comfyui-impact-pack)")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--detail", action="store_true",
                        help="Show full I/O specifications")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output raw JSON")
    args = parser.parse_args()

    nodes = get_pack_nodes(args.node_pack_id, limit=args.limit)

    if args.output_json:
        print(json.dumps([n.model_dump() for n in nodes], indent=2))
    else:
        print(format_pack_detail(args.node_pack_id, nodes, summary=not args.detail))
