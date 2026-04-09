"""Search templates by name, category, model, or tag with weighted scoring."""

import argparse

from src.templates.fetch import fetch_template_index, flatten_templates
from src.templates.models import Template


def search_templates(
    query: str,
    media_type: str | None = None,
    model: str | None = None,
    force_refresh: bool = False,
) -> list[Template]:
    """Search templates with weighted scoring across title, tags, description, and models.

    Scoring weights:
        - Title match: +3.0
        - Tag match: +2.0
        - Model match: +2.0
        - Description match: +1.0

    Results are sorted by score descending, then title ascending.
    """
    categories = fetch_template_index(force_refresh)
    all_templates = flatten_templates(categories)
    query_lower = query.lower()

    scored: list[tuple[float, Template]] = []

    for tmpl in all_templates:
        # Apply filters first
        if media_type and tmpl.mediaType != media_type:
            continue
        if model and not any(model.lower() in m.lower() for m in tmpl.models):
            continue

        score = 0.0
        if query_lower in tmpl.title.lower():
            score += 3.0
        if any(query_lower in tag.lower() for tag in tmpl.tags):
            score += 2.0
        if query_lower in tmpl.description.lower():
            score += 1.0
        if any(query_lower in m.lower() for m in tmpl.models):
            score += 2.0

        if score > 0:
            scored.append((score, tmpl))

    scored.sort(key=lambda x: (-x[0], x[1].title))
    return [tmpl for _, tmpl in scored]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Template search CLI")
    parser.add_argument("--query", type=str, required=True, help="Search query")
    parser.add_argument("--type", type=str, help="Filter by media type")
    parser.add_argument("--model", type=str, help="Filter by model name")
    parser.add_argument(
        "--refresh", action="store_true", help="Force refresh cached data"
    )
    args = parser.parse_args()

    results = search_templates(
        query=args.query,
        media_type=args.type,
        model=args.model,
        force_refresh=args.refresh,
    )
    if results:
        print(f"Found {len(results)} template(s):")
        for tmpl in results:
            print(f"  [{tmpl.mediaType}] {tmpl.title} ({tmpl.name})")
    else:
        print("No templates found.")
