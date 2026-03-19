#!/usr/bin/env python3
"""Extract core ComfyUI node names from GitHub source.

Fetches nodes.py and comfy_extras/nodes_*.py from the ComfyUI repository,
extracts NODE_CLASS_MAPPINGS entries, and writes to data/core_nodes.json.

Usage:
    python scripts/extract_core_nodes.py

Set GITHUB_TOKEN env var to avoid rate limits (60 req/hr unauthenticated).
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "core_nodes.json"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
MAIN_NODES_URL = "https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/nodes.py"
EXTRAS_API_URL = "https://api.github.com/repos/comfyanonymous/ComfyUI/contents/comfy_extras"


def _github_headers() -> dict[str, str]:
    headers = {"User-Agent": "ComfyTemplateAgent/1.0"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def _extract_node_names(source: str) -> list[str]:
    """Extract node names from NODE_CLASS_MAPPINGS in Python source."""
    nodes = []
    # Match NODE_CLASS_MAPPINGS = { ... } blocks
    # Handle both single-line and multi-line dicts, and .update() calls
    patterns = [
        r'NODE_CLASS_MAPPINGS\s*=\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}',
        r'NODE_CLASS_MAPPINGS\.update\(\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}\s*\)',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, source, re.DOTALL):
            block = match.group(1)
            # Extract quoted string keys
            nodes.extend(re.findall(r'["\']([^"\']+)["\']', block))
    return nodes


def extract_core_nodes() -> list[str]:
    """Extract core node names from ComfyUI GitHub source."""
    headers = _github_headers()
    client = httpx.Client(timeout=30.0, headers=headers, follow_redirects=True)
    all_nodes: list[str] = []

    # Main nodes.py
    print("Fetching nodes.py...", file=sys.stderr)
    resp = client.get(MAIN_NODES_URL)
    resp.raise_for_status()
    names = _extract_node_names(resp.text)
    print(f"  Found {len(names)} nodes in nodes.py", file=sys.stderr)
    all_nodes.extend(names)

    # comfy_extras/nodes_*.py files
    print("Fetching comfy_extras/ file list...", file=sys.stderr)
    resp = client.get(EXTRAS_API_URL)
    resp.raise_for_status()
    files = resp.json()

    node_files = [f for f in files if f["name"].startswith("nodes_") and f["name"].endswith(".py")]
    print(f"  Found {len(node_files)} node files in comfy_extras/", file=sys.stderr)

    for i, f in enumerate(node_files, 1):
        fname = f["name"]
        print(f"  [{i}/{len(node_files)}] Fetching {fname}...", file=sys.stderr)
        try:
            file_resp = client.get(f["download_url"])
            file_resp.raise_for_status()
            names = _extract_node_names(file_resp.text)
            if names:
                print(f"    Found {len(names)} nodes", file=sys.stderr)
            all_nodes.extend(names)
        except httpx.HTTPStatusError as e:
            print(f"    WARNING: Failed to fetch {fname}: {e}", file=sys.stderr)
            if e.response.status_code == 403:
                print("    Rate limited! Set GITHUB_TOKEN env var.", file=sys.stderr)
                break

    client.close()
    return sorted(set(all_nodes))


def main() -> None:
    nodes = extract_core_nodes()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "nodes": nodes,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "source": "github.com/comfyanonymous/ComfyUI",
        "count": len(nodes),
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nWrote {len(nodes)} core nodes to {OUTPUT_FILE}", file=sys.stderr)


if __name__ == "__main__":
    main()
