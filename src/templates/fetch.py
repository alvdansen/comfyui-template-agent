"""Fetch and cache template index and workflow JSONs from GitHub raw CDN."""

import argparse
import json
import re

import httpx

from src.shared.cache import DiskCache
from src.shared.config import CACHE_TTLS, GITHUB_RAW_BASE
from src.shared.http import get_github_client
from src.templates.models import Template, TemplateCategory

_cache = DiskCache()

_UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)


def fetch_template_index(force_refresh: bool = False) -> list[TemplateCategory]:
    """Fetch and cache the template index.json from GitHub raw CDN.

    Returns a list of TemplateCategory objects parsed from the nested index structure.
    """
    cache_key = "template_index"
    if not force_refresh:
        cached = _cache.get(cache_key, CACHE_TTLS["templates"])
        if cached is not None:
            return [TemplateCategory(**c) for c in cached]

    client = get_github_client()
    try:
        url = f"{GITHUB_RAW_BASE}/index.json"
        resp = client.get(url)
        resp.raise_for_status()
        data = resp.json()
    finally:
        client.close()

    _cache.set(cache_key, data)
    return [TemplateCategory(**c) for c in data]


def fetch_workflow_json(
    template_name: str, force_refresh: bool = False
) -> dict | None:
    """Fetch a single workflow JSON by template name.

    Tries the name as-is, then with/without .app suffix to handle naming quirks.
    Returns the parsed JSON dict or None on failure.
    """
    cache_key = f"template_workflow_{template_name}"
    if not force_refresh:
        cached = _cache.get(cache_key, CACHE_TTLS["templates"])
        if cached is not None:
            return cached

    client = get_github_client()
    try:
        # Try name as-is first
        candidates = [template_name]
        # If name ends with .app, also try without
        if template_name.endswith(".app"):
            candidates.append(template_name[:-4])
        else:
            # Try with .app suffix
            candidates.append(f"{template_name}.app")

        for name in candidates:
            url = f"{GITHUB_RAW_BASE}/{name}.json"
            try:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    _cache.set(cache_key, data)
                    return data
            except (httpx.HTTPError, json.JSONDecodeError):
                continue
    finally:
        client.close()

    return None


def extract_node_types(workflow: dict) -> set[str]:
    """Extract all node class_types from a workflow, including subgraph internals.

    Filters out UUID-pattern values which are subgraph references, not real node types.
    """
    types: set[str] = set()

    # Top-level nodes
    for node in workflow.get("nodes", []):
        node_type = node.get("type", "")
        if node_type and not _UUID_PATTERN.match(node_type):
            types.add(node_type)

    # Subgraph nodes
    for subgraph in workflow.get("definitions", {}).get("subgraphs", []):
        for node in subgraph.get("nodes", []):
            node_type = node.get("type", "")
            if node_type and not _UUID_PATTERN.match(node_type):
                types.add(node_type)

    return types


def flatten_templates(categories: list[TemplateCategory]) -> list[Template]:
    """Flatten nested categories into a flat list of all templates."""
    templates: list[Template] = []
    for cat in categories:
        templates.extend(cat.templates)
    return templates


def get_template_detail(
    template_name: str, force_refresh: bool = False
) -> dict | None:
    """Get combined metadata and node types for a template.

    Returns a dict with template metadata fields plus extracted node_types,
    or None if the template is not found in the index.
    """
    categories = fetch_template_index(force_refresh)

    # Find template and its parent category
    template: Template | None = None
    parent_category = ""
    for cat in categories:
        for tmpl in cat.templates:
            if tmpl.name == template_name:
                template = tmpl
                parent_category = cat.category
                break
        if template is not None:
            break

    if template is None:
        return None

    # Fetch workflow and extract node types
    node_types: list[str] = []
    workflow = fetch_workflow_json(template_name, force_refresh)
    if workflow:
        node_types = sorted(extract_node_types(workflow))

    return {
        "name": template.name,
        "title": template.title,
        "description": template.description,
        "mediaType": template.mediaType,
        "tags": template.tags,
        "models": template.models,
        "requiresCustomNodes": template.requiresCustomNodes,
        "category": parent_category,
        "node_types": node_types,
        "node_count": len(node_types),
        "vram": template.vram,
        "size": template.size,
        "usage": template.usage,
        "date": template.date,
        "username": template.username,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Template fetch CLI")
    parser.add_argument("--list", action="store_true", help="List all template names")
    parser.add_argument("--detail", type=str, help="Show full detail for a template")
    parser.add_argument(
        "--refresh", action="store_true", help="Force refresh cached data"
    )
    args = parser.parse_args()

    if args.list:
        categories = fetch_template_index(force_refresh=args.refresh)
        for cat in categories:
            print(f"\n[{cat.category}]")
            for tmpl in cat.templates:
                print(f"  {tmpl.name}: {tmpl.title}")
    elif args.detail:
        detail = get_template_detail(args.detail, force_refresh=args.refresh)
        if detail:
            print(json.dumps(detail, indent=2))
        else:
            print(f"Template '{args.detail}' not found.")
    else:
        parser.print_help()
