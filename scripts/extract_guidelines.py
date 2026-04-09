#!/usr/bin/env python3
"""Extract template creation guidelines from Notion export to structured JSON.

Reads the Notion markdown export and produces data/guidelines.json with
structured rules, submission process, thumbnail requirements, and color conventions.

Also copies key reference images to data/guidelines/.

Usage:
    python scripts/extract_guidelines.py
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

# On Windows, /tmp in git-bash maps to the user's temp dir
_tmp = Path(tempfile.gettempdir())
NOTION_DIR = _tmp / "notion-export"
DATA_DIR = Path(__file__).parent.parent / "data"
GUIDELINES_DIR = DATA_DIR / "guidelines"
OUTPUT_FILE = DATA_DIR / "guidelines.json"

# Key images to preserve (Notion export name -> our name)
IMAGE_MAP = {
    "image.png": "image.png",
    "image 2.png": "image_2.png",
    "image 3.png": "image_3.png",
    "image 4.png": "image_4.png",
    "image 7.png": "image_7.png",
    "image 8.png": "image_8.png",
    "image 10.png": "image_10.png",
}


def extract_guidelines() -> dict:
    """Parse Notion markdown into structured guidelines JSON."""
    rules = [
        {
            "id": "core_node_preference",
            "title": "Use core nodes when possible",
            "description": (
                "Use ComfyUI core nodes if possible; custom nodes only when no core node "
                "exists. Custom nodes rely on third-party updates, risking template breakage. "
                "Core nodes are maintainable by Comfy Org and offer better compatibility for "
                "local users and stable long-term maintenance."
            ),
            "severity": "required",
            "images": ["image.png"],
        },
        {
            "id": "no_set_get_nodes",
            "title": "Never use Set/Get nodes",
            "description": (
                "Do not use Set and Get nodes in templates. While they can simplify the "
                "workflow, they make it hard for users to follow the logic."
            ),
            "severity": "required",
            "images": [],
        },
        {
            "id": "cloud_compatible",
            "title": "Build and test on Comfy Cloud",
            "description": (
                "Build the workflow on Cloud, then share the workflow link. "
                "The workflow will be tested on cloud to verify it works."
            ),
            "severity": "required",
            "images": [],
        },
        {
            "id": "thumbnail_specs",
            "title": "Thumbnail requirements",
            "description": (
                "Use workflow effect previews, not screenshots. Keep style consistent "
                "with existing templates. Ratio: 1:1. If it's a video, keep to 3-5s. "
                "You can use the input/output. Supported types at: "
                "https://github.com/Comfy-Org/workflow_templates?tab=readme-ov-file#4--choose-thumbnail-type"
            ),
            "severity": "required",
            "images": ["image_2.png"],
        },
        {
            "id": "api_badge_position",
            "title": "Avoid key info in top-left corner",
            "description": (
                "Please avoid key information in the top-left corner of thumbnails. "
                "Provider info will be added there if the template contains an API node."
            ),
            "severity": "recommended",
            "images": ["image_3.png"],
        },
        {
            "id": "unique_subgraph_names",
            "title": "No identically-named subgraphs with different internals",
            "description": (
                "Don't copy subgraphs with the same name and modify parameters internally, "
                "as this leads to logical confusion. Move different settings outside the "
                "subgraph, making it easier to read and understand."
            ),
            "severity": "required",
            "images": ["image_4.png"],
        },
        {
            "id": "subgraph_rules",
            "title": "Subgraph content specifications",
            "description": (
                "Preview nodes and Save nodes should be placed outside subgraphs. "
                "Avoid storing additional content inside subgraphs or including preview "
                "nodes with no practical significance. If sections use the same logic, "
                "convert to a subgraph. Refer to Core Subgraph Blueprints guideline."
            ),
            "severity": "required",
            "images": ["image_7.png", "image_8.png"],
        },
        {
            "id": "note_color_black",
            "title": "Note nodes must use black background",
            "description": (
                "Note nodes should use black to distinguish from the yellow color of "
                "API nodes, avoiding user confusion."
            ),
            "severity": "required",
            "images": ["image_10.png"],
        },
        {
            "id": "api_node_color_yellow",
            "title": "API nodes colored yellow",
            "description": (
                "API nodes are colored yellow. Note nodes must be black to avoid "
                "confusion with API node coloring."
            ),
            "severity": "required",
            "images": ["image_10.png"],
        },
        {
            "id": "group_color_default",
            "title": "Use default ComfyUI group color",
            "description": (
                "Use the default ComfyUI group color to ensure good readability "
                "in both light and dark modes."
            ),
            "severity": "recommended",
            "images": [],
        },
        {
            "id": "simplicity_readability",
            "title": "Simplicity and readability",
            "description": (
                "Workflow logic should be clear and easy to understand, not limited "
                "to a single template scenario, and should have certain universality "
                "to facilitate user understanding and reuse."
            ),
            "severity": "recommended",
            "images": [],
        },
        {
            "id": "naming_conventions",
            "title": "Template naming rules",
            "description": (
                "Make sure all required fields are filled out when submitting. "
                "Follow the existing naming patterns in the template library."
            ),
            "severity": "required",
            "images": [],
        },
    ]

    submission_process = [
        "Build the workflow on Comfy Cloud",
        "Test the workflow on cloud to verify it works",
        "Submit via the Notion submission form with all required fields",
        "Include workflow link from Cloud",
        "Provide thumbnail (1:1 ratio, effect preview not screenshot)",
        "QA review by Comfy team",
    ]

    thumbnail_requirements = {
        "dimensions": "1:1 ratio",
        "format": "image or video (3-5s for video)",
        "content_types": ["workflow effect preview", "input/output examples"],
        "avoid": "screenshots, key info in top-left corner",
        "reference": "https://github.com/Comfy-Org/workflow_templates?tab=readme-ov-file#4--choose-thumbnail-type",
    }

    color_conventions = {
        "notes": "black",
        "api_nodes": "yellow",
        "groups": "default ComfyUI color",
    }

    return {
        "source": "ComfyUI Template Creation Guidelines (Notion export)",
        "rules": rules,
        "submission_process": submission_process,
        "thumbnail_requirements": thumbnail_requirements,
        "color_conventions": color_conventions,
    }


def copy_images() -> list[str]:
    """Copy key images from Notion export to data/guidelines/."""
    GUIDELINES_DIR.mkdir(parents=True, exist_ok=True)
    copied = []
    for src_name, dst_name in IMAGE_MAP.items():
        src = NOTION_DIR / src_name
        dst = GUIDELINES_DIR / dst_name
        if src.exists():
            shutil.copy2(src, dst)
            copied.append(dst_name)
            print(f"  Copied {src_name} -> {dst_name}", file=sys.stderr)
        else:
            print(f"  WARNING: {src_name} not found in Notion export", file=sys.stderr)
    return copied


def main() -> None:
    if not NOTION_DIR.exists():
        print(
            "Notion export not found at /tmp/notion-export/. "
            "Re-export from Notion and extract to /tmp/notion-export/ before running.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Extracting guidelines...", file=sys.stderr)
    guidelines = extract_guidelines()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(guidelines, f, indent=2)
    print(f"Wrote guidelines to {OUTPUT_FILE}", file=sys.stderr)
    print(f"  {len(guidelines['rules'])} rules", file=sys.stderr)

    print("\nCopying key images...", file=sys.stderr)
    copied = copy_images()
    print(f"  Copied {len(copied)} images", file=sys.stderr)


if __name__ == "__main__":
    main()
