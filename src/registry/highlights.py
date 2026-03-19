"""Discover trending, new, rising, popular, and random ComfyUI nodes."""

import argparse
import json
import math
import random
from datetime import datetime, timezone

from src.registry.models import NodePack
from src.shared.cache import DiskCache
from src.shared.categories import classify_node
from src.shared.config import CACHE_TTLS
from src.shared.http import fetch_json, get_client

_cache = DiskCache()


def _days_since(date_str: str) -> int:
    """Days between a date string and now, minimum 1."""
    try:
        created = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return max((datetime.now(timezone.utc) - created).days, 1)
    except (ValueError, TypeError):
        return 365


def _score_trending(node: NodePack) -> float:
    """Trending = high download velocity + star signal, with recency boost."""
    days = _days_since(node.created_at)
    dl_per_day = node.downloads / days
    star_bonus = math.log(node.github_stars + 1, 2)
    recency = max(1, 10 - (days / 30))
    return dl_per_day * (1 + star_bonus) * recency


def _score_rising(node: NodePack) -> float:
    """Rising = new nodes with surprisingly high adoption (< 90 days)."""
    days = _days_since(node.created_at)
    if days > 90:
        return 0
    dl_per_day = node.downloads / days
    return dl_per_day * (90 - days)


def fetch_all_nodes(pages: int = 6) -> list[NodePack]:
    """Bulk fetch node packs from the registry, with disk caching."""
    cached = _cache.get("highlights", CACHE_TTLS["highlights"])
    if cached is not None:
        return [NodePack(**n) for n in cached]

    all_nodes: list[NodePack] = []
    client = get_client()
    try:
        for page in range(1, pages + 1):
            try:
                data = fetch_json(client, "/nodes", params={"page": page, "limit": 50})
                for n in data.get("nodes", []):
                    if n.get("status") != "NodeStatusActive":
                        continue
                    # Extract author from publisher if missing
                    if not n.get("author"):
                        publisher = n.get("publisher") or {}
                        n["author"] = publisher.get("name", "")
                    all_nodes.append(NodePack(**n))
            except Exception:
                continue
    finally:
        client.close()

    _cache.set("highlights", [n.model_dump() for n in all_nodes])
    return all_nodes


def get_highlights(
    mode: str = "trending",
    limit: int = 10,
    category: str | None = None,
    truly_random: bool = False,
) -> list[NodePack]:
    """Get discovery results by mode, with optional category filtering.

    Modes: trending, new, rising, popular, random.
    Categories: video, image, audio, 3d.
    """
    nodes = fetch_all_nodes()
    if not nodes:
        return []

    # Apply category filter
    if category:
        nodes = [
            n for n in nodes
            if category in classify_node(n.name, n.description)
        ]
        if not nodes:
            return []

    if mode == "trending":
        scored = sorted(nodes, key=_score_trending, reverse=True)
        return scored[:limit]

    elif mode == "new":
        # Last 14 days with downloads > 0
        fresh = [
            n for n in nodes
            if _days_since(n.created_at) <= 14 and n.downloads > 0
        ]
        if not fresh:
            # Fallback to most recent
            fresh = sorted(nodes, key=lambda n: n.created_at, reverse=True)
        else:
            fresh = sorted(fresh, key=lambda n: n.created_at, reverse=True)
        return fresh[:limit]

    elif mode == "popular":
        by_downloads = sorted(nodes, key=lambda n: n.downloads, reverse=True)
        return by_downloads[:limit]

    elif mode == "rising":
        scored = sorted(nodes, key=_score_rising, reverse=True)
        rising = [n for n in scored if _score_rising(n) > 0]
        return rising[:limit]

    elif mode == "random":
        if truly_random:
            return random.sample(nodes, min(limit, len(nodes)))
        else:
            # Weighted random biased toward quality
            weights = [n.downloads + n.github_stars + 1 for n in nodes]
            picks: list[NodePack] = []
            seen: set[str] = set()
            attempts = 0
            while len(picks) < min(limit, len(nodes)) and attempts < limit * 10:
                chosen = random.choices(nodes, weights=weights, k=1)[0]
                if chosen.id not in seen:
                    picks.append(chosen)
                    seen.add(chosen.id)
                attempts += 1
            return picks

    else:
        raise ValueError(f"Unknown mode: {mode!r}. Use: trending, new, rising, popular, random.")


def format_results(nodes: list[NodePack], mode: str) -> str:
    """Format discovery results as a human-readable table."""
    if not nodes:
        return f"No {mode} nodes found."

    lines = [f"## {mode.capitalize()} Nodes ({len(nodes)} results)\n"]
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
    parser = argparse.ArgumentParser(description="Discover ComfyUI nodes")
    parser.add_argument("--mode", default="trending",
                        choices=["trending", "new", "rising", "popular", "random"])
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--category", choices=["video", "image", "audio", "3d"])
    parser.add_argument("--truly-random", action="store_true",
                        help="Truly random instead of weighted (for random mode)")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output raw JSON")
    args = parser.parse_args()

    results = get_highlights(
        mode=args.mode,
        limit=args.limit,
        category=args.category,
        truly_random=args.truly_random,
    )

    if args.output_json:
        print(json.dumps([n.model_dump() for n in results], indent=2))
    else:
        print(format_results(results, args.mode))
