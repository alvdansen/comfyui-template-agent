"""Cross-reference nodes and packs against the template library."""

import argparse
import json

from src.shared.cache import DiskCache
from src.shared.config import CACHE_TTLS
from src.templates.fetch import (
    extract_node_types,
    fetch_template_index,
    fetch_workflow_json,
)
from src.templates.models import TemplateCategory, TemplateSummary

_cache = DiskCache()


def build_pack_index(
    categories: list[TemplateCategory],
) -> dict[str, list[TemplateSummary]]:
    """Build pack_id -> template summaries mapping from requiresCustomNodes.

    This uses index.json metadata only -- no workflow fetch needed.
    """
    index: dict[str, list[TemplateSummary]] = {}
    for cat in categories:
        for tmpl in cat.templates:
            for pack_id in tmpl.requiresCustomNodes:
                index.setdefault(pack_id, []).append(
                    TemplateSummary(
                        name=tmpl.name,
                        title=tmpl.title,
                        mediaType=tmpl.mediaType,
                        tags=tmpl.tags,
                        category=cat.category,
                    )
                )
    return index


def build_node_index(
    categories: list[TemplateCategory],
) -> dict[str, list[TemplateSummary]]:
    """Build class_type -> template summaries mapping from workflow JSONs.

    Fetches each workflow JSON and extracts node types including subgraph internals.
    Results are cached with the templates TTL.
    """
    cached = _cache.get("template_node_index", CACHE_TTLS["templates"])
    if cached is not None:
        # Reconstruct TemplateSummary objects from cached dicts
        return {
            key: [TemplateSummary(**s) for s in summaries]
            for key, summaries in cached.items()
        }

    index: dict[str, list[TemplateSummary]] = {}
    for cat in categories:
        for tmpl in cat.templates:
            workflow = fetch_workflow_json(tmpl.name)
            if not workflow:
                continue
            node_types = extract_node_types(workflow)
            summary = TemplateSummary(
                name=tmpl.name,
                title=tmpl.title,
                mediaType=tmpl.mediaType,
                tags=tmpl.tags,
                category=cat.category,
            )
            for node_type in node_types:
                index.setdefault(node_type, []).append(summary)

    # Cache as serializable dicts
    cache_data = {
        key: [s.model_dump() for s in summaries] for key, summaries in index.items()
    }
    _cache.set("template_node_index", cache_data)
    return index


def cross_reference(
    query: str, level: str = "pack", force_refresh: bool = False
) -> dict:
    """Look up which templates use a given node class_type or pack ID.

    Args:
        query: The node class_type or pack ID to search for.
        level: "pack" for pack-level lookup, "node" for node-level lookup.
        force_refresh: Force re-fetching template data.

    Returns a dict with query, level, exact_matches, fuzzy_matches, total_count,
    and top_examples.
    """
    categories = fetch_template_index(force_refresh)

    if level == "pack":
        index = build_pack_index(categories)
    else:
        index = build_node_index(categories)

    # Exact match
    exact_matches = index.get(query, [])

    # Fuzzy match: substring match on keys if no exact match
    fuzzy_matches: list[TemplateSummary] = []
    if not exact_matches:
        query_lower = query.lower()
        seen_names: set[str] = set()
        for key, summaries in index.items():
            if query_lower in key.lower() and key != query:
                for s in summaries:
                    if s.name not in seen_names:
                        fuzzy_matches.append(s)
                        seen_names.add(s.name)

    matches = exact_matches or fuzzy_matches
    top_examples = [
        {"name": s.name, "title": s.title, "category": s.category}
        for s in matches[:3]
    ]

    return {
        "query": query,
        "level": level,
        "exact_matches": [s.model_dump() for s in exact_matches],
        "fuzzy_matches": [s.model_dump() for s in fuzzy_matches],
        "total_count": len(matches),
        "top_examples": top_examples,
    }


def format_cross_reference(result: dict) -> str:
    """Format cross-reference results as human-readable text."""
    lines: list[str] = []
    total = result["total_count"]
    query = result["query"]
    level = result["level"]

    if total == 0:
        lines.append(f"'{query}' ({level}) not found in any templates.")
        return "\n".join(lines)

    match_type = "exact" if result["exact_matches"] else "fuzzy"
    lines.append(f"'{query}' ({level}) used in {total} template(s) ({match_type}):")

    if result["fuzzy_matches"] and not result["exact_matches"]:
        lines.append("  (Related matches - fuzzy)")

    for ex in result["top_examples"]:
        lines.append(f"  - {ex['title']} [{ex['category']}] ({ex['name']})")

    if total > 3:
        lines.append(f"  ... and {total - 3} more")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Template cross-reference CLI")
    parser.add_argument("--query", type=str, required=True, help="Node or pack to look up")
    parser.add_argument(
        "--level",
        type=str,
        choices=["pack", "node"],
        default="pack",
        help="Lookup level",
    )
    parser.add_argument(
        "--refresh", action="store_true", help="Force refresh cached data"
    )
    args = parser.parse_args()

    result = cross_reference(
        query=args.query, level=args.level, force_refresh=args.refresh
    )
    print(format_cross_reference(result))
