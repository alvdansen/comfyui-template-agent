"""Gap analysis and coverage reporting for the ComfyUI template library."""

import argparse
import math
from collections import Counter

from src.registry.highlights import fetch_all_nodes
from src.registry.models import NodePack
from src.shared.categories import classify_node
from src.templates.cross_ref import build_pack_index
from src.templates.fetch import fetch_template_index, flatten_templates


def score_gap_opportunity(node_pack: NodePack, template_count: int) -> float:
    """Score a node pack's gap opportunity based on popularity.

    Packs already covered by templates score 0. Uncovered packs are scored
    using log-scaled downloads and stars.
    """
    if template_count > 0:
        return 0.0
    dl_score = math.log(node_pack.downloads + 1, 10)
    star_score = math.log(node_pack.github_stars + 1, 2)
    return dl_score * (1 + star_score * 0.5)


def suggest_template_idea(node_pack: NodePack) -> str:
    """Suggest a template idea based on the node pack's classification."""
    categories = classify_node(node_pack.name, node_pack.description)
    desc_snippet = (node_pack.description or "")[:100]

    suggestions = {
        "video": "Could pair with img2vid or video effects workflow",
        "image": "Could pair with txt2img or image processing workflow",
        "audio": "Could pair with text-to-speech or audio processing workflow",
        "3d": "Could pair with 3D generation or depth-based workflow",
    }

    for cat in categories:
        if cat in suggestions:
            return f"{suggestions[cat]}. Context: {desc_snippet}"

    return f"Could serve as utility node in multi-step pipeline. Context: {desc_snippet}"


def gap_analysis(
    by_category: bool = False,
    limit: int = 20,
    force_refresh: bool = False,
) -> dict:
    """Identify popular node packs that lack template coverage.

    Returns scored gaps sorted by opportunity, optionally grouped by category.
    """
    all_packs = fetch_all_nodes()
    categories = fetch_template_index(force_refresh)
    pack_index = build_pack_index(categories)

    gaps: list[dict] = []
    for pack in all_packs:
        template_count = len(pack_index.get(pack.id, []))
        score = score_gap_opportunity(pack, template_count)
        if score > 0:
            pack_categories = classify_node(pack.name, pack.description)
            gaps.append({
                "name": pack.name,
                "id": pack.id,
                "downloads": pack.downloads,
                "stars": pack.github_stars,
                "score": score,
                "suggestion": suggest_template_idea(pack),
                "categories": pack_categories,
            })

    gaps.sort(key=lambda g: g["score"], reverse=True)

    result: dict = {
        "total_gaps": len(gaps),
        "total_packs_checked": len(all_packs),
        "gaps": gaps[:limit],
    }

    if by_category:
        grouped: dict[str, list[dict]] = {}
        for gap in gaps[:limit]:
            for cat in gap["categories"]:
                grouped.setdefault(cat, []).append(gap)
        result["by_category"] = grouped

    return result


def format_gap_analysis(result: dict) -> str:
    """Format gap analysis results as human-readable text."""
    lines: list[str] = []
    total = result["total_gaps"]
    checked = result["total_packs_checked"]
    lines.append(
        f"Gap Analysis: {total} packs with no template coverage "
        f"(checked {checked})"
    )
    lines.append("")

    if "by_category" in result:
        for cat, cat_gaps in result["by_category"].items():
            lines.append(f"### {cat.capitalize()} ({len(cat_gaps)} gaps)")
            for i, gap in enumerate(cat_gaps, 1):
                lines.append(
                    f"  #{i} {gap['name']} "
                    f"(downloads: {gap['downloads']:,}, stars: {gap['stars']}) "
                    f"-- Score: {gap['score']:.1f}"
                )
                lines.append(f"    Suggestion: {gap['suggestion']}")
            lines.append("")
    else:
        for i, gap in enumerate(result["gaps"], 1):
            lines.append(
                f"#{i} {gap['name']} "
                f"(downloads: {gap['downloads']:,}, stars: {gap['stars']}) "
                f"-- Score: {gap['score']:.1f}"
            )
            lines.append(f"  Suggestion: {gap['suggestion']}")

    return "\n".join(lines)


def coverage_report(force_refresh: bool = False) -> dict:
    """Generate a coverage report for the template library.

    Returns metrics on category distribution, pack coverage, thin spots,
    and growth trends.
    """
    categories = fetch_template_index(force_refresh)
    all_templates = flatten_templates(categories)
    all_packs = fetch_all_nodes()

    # Metric 1: Templates per category (by mediaType)
    templates_by_category = dict(Counter(t.mediaType for t in all_templates))

    # Metric 2: Node coverage % (unique packs referenced in templates)
    covered_packs: set[str] = set()
    for t in all_templates:
        for pack_id in t.requiresCustomNodes:
            covered_packs.add(pack_id)
    total_registry_packs = len(all_packs) if all_packs else 1
    coverage_pct = (len(covered_packs) / total_registry_packs) * 100

    # Metric 3: Thin spots (categories below average template count)
    if templates_by_category:
        avg_per_category = sum(templates_by_category.values()) / len(
            templates_by_category
        )
    else:
        avg_per_category = 0
    thin_spots = [
        {"category": cat, "count": count, "average": round(avg_per_category, 1)}
        for cat, count in templates_by_category.items()
        if count < avg_per_category
    ]

    # Metric 4: Growth trends (templates added per month, last 6 months)
    month_counter: Counter = Counter()
    for t in all_templates:
        if t.date and len(t.date) >= 7:
            month_key = t.date[:7]  # YYYY-MM
            month_counter[month_key] += 1
    # Sort by month descending, take last 6
    sorted_months = sorted(month_counter.items(), reverse=True)[:6]
    growth_by_month = {month: count for month, count in sorted_months}

    return {
        "total_templates": len(all_templates),
        "templates_by_category": templates_by_category,
        "coverage_pct": coverage_pct,
        "thin_spots": thin_spots,
        "growth_by_month": growth_by_month,
    }


def format_coverage_report(result: dict) -> str:
    """Format coverage report as human-readable text."""
    lines: list[str] = []

    total = result["total_templates"]
    pct = result["coverage_pct"]
    lines.append(
        f"Template Library: {total} templates, {pct:.1f}% pack coverage"
    )
    lines.append("")

    # Category table
    lines.append("Templates by Category:")
    max_count = max(result["templates_by_category"].values(), default=1)
    for cat, count in sorted(
        result["templates_by_category"].items(), key=lambda x: x[1], reverse=True
    ):
        bar_len = int((count / max_count) * 20)
        bar = "#" * bar_len
        lines.append(f"  {cat:<12} {count:>4}  {bar}")
    lines.append("")

    # Thin spots
    if result["thin_spots"]:
        lines.append("Thin Spots (below average):")
        for spot in result["thin_spots"]:
            lines.append(
                f"  {spot['category']}: {spot['count']} templates "
                f"(avg: {spot['average']})"
            )
        lines.append("")

    # Growth trends
    if result["growth_by_month"]:
        lines.append("Growth Trends (recent months):")
        for month, count in result["growth_by_month"].items():
            lines.append(f"  {month}: {count} templates added")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Template coverage CLI")
    subparsers = parser.add_subparsers(dest="command")

    gap_parser = subparsers.add_parser("gap", help="Run gap analysis")
    gap_parser.add_argument(
        "--by-category", action="store_true", help="Group gaps by category"
    )
    gap_parser.add_argument(
        "--limit", type=int, default=20, help="Max gaps to show"
    )

    cov_parser = subparsers.add_parser("coverage", help="Coverage report")
    cov_parser.add_argument(
        "--refresh", action="store_true", help="Force refresh cached data"
    )

    args = parser.parse_args()

    if args.command == "gap":
        result = gap_analysis(
            by_category=args.by_category, limit=args.limit
        )
        print(format_gap_analysis(result))
    elif args.command == "coverage":
        result = coverage_report(force_refresh=args.refresh)
        print(format_coverage_report(result))
    else:
        parser.print_help()
