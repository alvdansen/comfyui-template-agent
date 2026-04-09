"""Fetch the current core node list from ComfyUI's GitHub repo.

Usage: python scripts/update_core_nodes.py

Pulls node class names from ComfyUI/nodes.py and comfy_extras/ on GitHub,
then updates data/core_nodes.json.
"""

import json
import re
from pathlib import Path

import httpx

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "core_nodes.json"

# ComfyUI source files that register core nodes
SOURCES = [
    "https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/nodes.py",
    "https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/comfy_extras/nodes_images.py",
    "https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/comfy_extras/nodes_video.py",
    "https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/comfy_extras/nodes_post_processing.py",
    "https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/comfy_extras/nodes_model_merging.py",
    "https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/comfy_extras/nodes_upscale_model.py",
]

# Pattern: NODE_CLASS_MAPPINGS entries like "NodeName": NodeClass or "NodeName": NodeName
CLASS_MAPPING_RE = re.compile(r'"([A-Za-z][A-Za-z0-9_]+)"')


def fetch_node_names_from_source(url: str) -> set[str]:
    """Extract node names from NODE_CLASS_MAPPINGS in a source file."""
    resp = httpx.get(url, follow_redirects=True, timeout=15)
    if resp.status_code != 200:
        print(f"  WARN: {url} returned {resp.status_code}")
        return set()

    text = resp.text
    names = set()

    # Find NODE_CLASS_MAPPINGS dict
    in_mappings = False
    for line in text.split("\n"):
        if "NODE_CLASS_MAPPINGS" in line and "=" in line:
            in_mappings = True
            continue
        if in_mappings:
            if line.strip() == "}" or line.strip() == "}":
                in_mappings = False
                continue
            match = CLASS_MAPPING_RE.search(line)
            if match:
                names.add(match.group(1))

    return names


def fetch_extras_index() -> list[str]:
    """Get all comfy_extras Python files from GitHub directory listing."""
    url = "https://api.github.com/repos/comfyanonymous/ComfyUI/contents/comfy_extras"
    resp = httpx.get(url, follow_redirects=True, timeout=15)
    if resp.status_code != 200:
        return []
    files = resp.json()
    return [
        f["download_url"]
        for f in files
        if f["name"].startswith("nodes_") and f["name"].endswith(".py")
    ]


def main():
    # Load existing
    existing = set()
    if DATA_PATH.exists():
        with open(DATA_PATH) as f:
            existing = set(json.load(f).get("nodes", []))
    print(f"Existing: {len(existing)} nodes")

    # Fetch all extras files
    print("Fetching comfy_extras file list...")
    extras_urls = fetch_extras_index()
    print(f"  Found {len(extras_urls)} extras files")

    # Always include main nodes.py
    all_urls = ["https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/nodes.py"]
    all_urls.extend(extras_urls)

    all_nodes = set()
    for url in all_urls:
        short = url.split("/")[-1]
        names = fetch_node_names_from_source(url)
        if names:
            print(f"  {short}: {len(names)} nodes")
            all_nodes.update(names)

    # Merge with existing (don't remove manually added nodes)
    merged = existing | all_nodes
    added = merged - existing
    if added:
        print(f"\nNew nodes: {sorted(added)}")

    # Save
    with open(DATA_PATH, "w") as f:
        json.dump({"nodes": sorted(merged)}, f, indent=2)
        f.write("\n")
    print(f"\nTotal: {len(merged)} nodes (was {len(existing)}, added {len(added)})")


if __name__ == "__main__":
    main()
