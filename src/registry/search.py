"""Search ComfyUI nodes by name, category, and I/O type."""

import argparse
import json

from src.registry.models import ComfyNode, ComfyNodeResult, NodePack, SearchResult
from src.shared.cache import DiskCache
from src.shared.categories import classify_node
from src.shared.config import CACHE_TTLS
from src.shared.http import fetch_json, get_client

_cache = DiskCache()


def search_nodes(
    query: str,
    category: str | None = None,
    limit: int = 20,
) -> list[NodePack]:
    """Search node packs by name/description, with optional category filter.

    Uses the /nodes?search=X endpoint.
    """
    cache_key = f"search_{query}_{category}"
    cached = _cache.get(cache_key, CACHE_TTLS["search"])
    if cached is not None:
        return [NodePack(**n) for n in cached]

    client = get_client()
    try:
        data = fetch_json(client, "/nodes", params={"search": query, "limit": limit})
        result = SearchResult(**data)
        nodes = result.nodes
    finally:
        client.close()

    if category:
        nodes = [
            n for n in nodes
            if category in classify_node(n.name, n.description)
        ]

    _cache.set(cache_key, [n.model_dump() for n in nodes])
    return nodes


def search_by_type(
    input_type: str | None = None,
    output_type: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """Search for nodes by their input or output ComfyUI types.

    Searches packs by type name, then fetches comfy_nodes to verify I/O match.
    Returns list of {pack: NodePack, matching_nodes: list[ComfyNode]}.
    """
    query = input_type or output_type or ""
    if not query:
        return []

    packs = search_nodes(query, limit=limit)
    results: list[dict] = []

    client = get_client()
    try:
        for pack in packs:
            try:
                data = fetch_json(
                    client, "/comfy-nodes",
                    params={"node_id": pack.id, "limit": 100},
                )
                comfy_result = ComfyNodeResult(**data)
                matching: list[ComfyNode] = []

                for cn in comfy_result.comfy_nodes:
                    match = True
                    if input_type:
                        inputs = cn.parsed_input_types()
                        all_input_types = []
                        for section in inputs.values():
                            if isinstance(section, dict):
                                for v in section.values():
                                    if isinstance(v, list) and v:
                                        all_input_types.append(str(v[0]))
                        if input_type.upper() not in [t.upper() for t in all_input_types]:
                            match = False

                    if output_type:
                        returns = cn.parsed_return_types()
                        if output_type.upper() not in [str(r).upper() for r in returns]:
                            match = False

                    if match:
                        matching.append(cn)

                if matching:
                    results.append({
                        "pack": pack,
                        "matching_nodes": matching,
                    })
            except Exception:
                continue
    finally:
        client.close()

    return results


def format_search_results(nodes: list[NodePack], query: str) -> str:
    """Format search results as a human-readable table."""
    if not nodes:
        return f'No results for "{query}".'

    lines = [f'## Search Results for "{query}" ({len(nodes)} results)\n']
    lines.append(f"{'Name':<30} {'Author':<20} {'Downloads':>10} {'Stars':>6}  Description")
    lines.append("-" * 100)

    for n in nodes:
        desc = (n.description or "")[:100]
        lines.append(
            f"{n.name:<30} {n.author:<20} {n.downloads:>10,} {n.github_stars:>6}  {desc}"
        )
        if n.repository:
            lines.append(f"  -> {n.repository}")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search ComfyUI nodes")
    parser.add_argument("--query", required=False, help="Search text")
    parser.add_argument("--category", choices=["video", "image", "audio", "3d"])
    parser.add_argument("--type-input", help="Filter by input type (e.g. IMAGE)")
    parser.add_argument("--type-output", help="Filter by output type (e.g. MASK)")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output raw JSON")
    args = parser.parse_args()

    if args.type_input or args.type_output:
        results = search_by_type(
            input_type=args.type_input,
            output_type=args.type_output,
            limit=args.limit,
        )
        if args.output_json:
            out = [
                {
                    "pack": r["pack"].model_dump(),
                    "matching_nodes": [cn.model_dump() for cn in r["matching_nodes"]],
                }
                for r in results
            ]
            print(json.dumps(out, indent=2))
        else:
            if not results:
                print("No matching nodes found.")
            else:
                for r in results:
                    pack = r["pack"]
                    print(f"\n{pack.name} by {pack.author} ({pack.downloads:,} downloads)")
                    for cn in r["matching_nodes"]:
                        print(f"  - {cn.comfy_node_name} [{cn.category}]")
                        if cn.parsed_input_types():
                            print(f"    Inputs: {list(cn.parsed_input_types().get('required', {}).keys())}")
                        if cn.parsed_return_types():
                            print(f"    Returns: {cn.parsed_return_types()}")
    elif args.query:
        nodes = search_nodes(args.query, category=args.category, limit=args.limit)
        if args.output_json:
            print(json.dumps([n.model_dump() for n in nodes], indent=2))
        else:
            print(format_search_results(nodes, args.query))
    else:
        parser.error("Either --query or --type-input/--type-output is required")
