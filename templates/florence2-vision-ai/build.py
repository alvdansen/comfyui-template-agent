"""Build script for the Florence2 Vision AI workflow template.

Creates workflow.json, index.json, and submission.md for the
ComfyUI-Florence2 (kijai) image captioning template.

Run from the project root:
    python templates/florence2-vision-ai/build.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure project root is on the path when run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.composer.graph import WorkflowGraph
from src.composer.layout import auto_layout
from src.composer.models import parse_node_spec
from src.composer.node_specs import NodeSpecCache
from src.document.metadata import format_index_entry, generate_index_entry
from src.document.notion import generate_notion_markdown
from src.validator.engine import run_validation
from src.validator.validate import format_report

OUTPUT_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Node spec definitions (mirrors what MCP get_node_info returns)
# ---------------------------------------------------------------------------

# Core nodes — minimal specs sufficient for graph construction
CORE_NODE_SPECS: dict[str, dict] = {
    "LoadImage": {
        "display_name": "Load Image",
        "category": "image",
        "input": {
            "required": {
                "image": [["example.png"], {}],
                "upload": [["image"], {}],
            },
            "optional": {},
        },
        "output": ["IMAGE", "MASK"],
        "output_name": ["IMAGE", "MASK"],
        "output_node": False,
    },
    "PreviewImage": {
        "display_name": "Preview Image",
        "category": "image",
        "input": {
            "required": {
                "images": ["IMAGE", {}],
            },
            "optional": {},
        },
        "output": [],
        "output_name": [],
        "output_node": True,
    },
    "PreviewAny": {
        "display_name": "Preview Any",
        "category": "utils",
        "input": {
            "required": {
                "input": ["*", {}],
            },
            "optional": {},
        },
        "output": [],
        "output_name": [],
        "output_node": True,
    },
}

# Florence2 custom node specs (ComfyUI-Florence2 by kijai)
FLORENCE2_NODE_SPECS: dict[str, dict] = {
    "DownloadAndLoadFlorence2Model": {
        "display_name": "DownloadAndLoadFlorence2Model",
        "category": "Florence2",
        "input": {
            "required": {
                "model": [
                    [
                        "microsoft/Florence-2-base",
                        "microsoft/Florence-2-base-ft",
                        "microsoft/Florence-2-large",
                        "microsoft/Florence-2-large-ft",
                        "HuggingFaceM4/Florence-2-DocVQA",
                        "thwri/CogFlorence-2.2-Large",
                        "gokaygokay/Florence-2-SD3-Captioner",
                        "MiaoshouAI/Florence-2-base-PromptGen-v1.5",
                        "MiaoshouAI/Florence-2-large-PromptGen-v1.5",
                    ],
                    {},
                ],
                "precision": [["fp16", "bf16", "fp32"], {}],
                "attention": [["sdpa", "flash_attention_2", "eager"], {}],
            },
            "optional": {},
        },
        "output": ["FL2MODEL"],
        "output_name": ["FL2MODEL"],
        "output_node": False,
    },
    "Florence2Run": {
        "display_name": "Florence2Run",
        "category": "Florence2",
        "input": {
            "required": {
                "image": ["IMAGE", {}],
                "florence2_model": ["FL2MODEL", {}],
                "task": [
                    [
                        "caption",
                        "detailed_caption",
                        "more_detailed_caption",
                        "caption_to_phrase_grounding",
                        "referring_expression_segmentation",
                        "region_to_segmentation",
                        "open_vocabulary_detection",
                        "dense_region_caption",
                        "region_proposal",
                        "region_to_category",
                        "region_to_description",
                        "ocr",
                        "ocr_with_region",
                        "object_detection",
                    ],
                    {},
                ],
                "text_input": ["STRING", {"default": "", "multiline": False}],
                "fill_mask": ["BOOLEAN", {"default": True}],
                "max_new_tokens": ["INT", {"default": 1024, "min": 1, "max": 4096}],
                "num_beams": ["INT", {"default": 3, "min": 1, "max": 64}],
            },
            "optional": {},
        },
        "output": ["IMAGE", "MASK", "STRING", "JSON"],
        "output_name": ["IMAGE", "MASK", "STRING", "JSON"],
        "output_node": False,
    },
}


def build_spec_cache() -> NodeSpecCache:
    """Populate a NodeSpecCache with all specs needed for this workflow."""
    cache = NodeSpecCache()
    all_specs = {**CORE_NODE_SPECS, **FLORENCE2_NODE_SPECS}
    for node_type, raw in all_specs.items():
        spec = parse_node_spec(node_type, raw)
        cache.put(node_type, spec)
    return cache


def build_workflow(cache: NodeSpecCache) -> WorkflowGraph:
    """Construct the Florence2 Vision AI workflow graph."""
    graph = WorkflowGraph(specs=cache)

    # Node 1: LoadImage — loads the input image
    load_image_id = graph.add_node("LoadImage", title="Load Image")
    # Default widget: image filename
    graph.set_widget(load_image_id, "image", "example.png")

    # Node 2: DownloadAndLoadFlorence2Model — downloads and loads the model
    model_loader_id = graph.add_node(
        "DownloadAndLoadFlorence2Model",
        title="Load Florence2 Model",
    )
    graph.set_widget(model_loader_id, "model", "microsoft/Florence-2-large-ft")
    graph.set_widget(model_loader_id, "precision", "fp16")
    graph.set_widget(model_loader_id, "attention", "sdpa")

    # Node 3: Florence2Run — runs vision task
    florence2_run_id = graph.add_node("Florence2Run", title="Florence2 Run")
    graph.set_widget(florence2_run_id, "task", "more_detailed_caption")
    graph.set_widget(florence2_run_id, "text_input", "")
    graph.set_widget(florence2_run_id, "fill_mask", True)
    graph.set_widget(florence2_run_id, "max_new_tokens", 1024)
    graph.set_widget(florence2_run_id, "num_beams", 3)

    # Node 4: PreviewImage — shows the annotated output image
    preview_image_id = graph.add_node("PreviewImage", title="Preview Image")

    # Node 5: PreviewAny — shows the text/caption output
    preview_any_id = graph.add_node("PreviewAny", title="Preview Caption")

    # Connections:
    # LoadImage IMAGE (slot 0) -> Florence2Run image (slot 0)
    graph.connect(load_image_id, 0, florence2_run_id, "image")

    # DownloadAndLoadFlorence2Model FL2MODEL (slot 0) -> Florence2Run florence2_model (slot 1)
    graph.connect(model_loader_id, 0, florence2_run_id, "florence2_model")

    # Florence2Run IMAGE (slot 0) -> PreviewImage images (slot 0)
    graph.connect(florence2_run_id, 0, preview_image_id, "images")

    # Florence2Run STRING (slot 2) -> PreviewAny input (slot 0)
    graph.connect(florence2_run_id, 2, preview_any_id, "input")

    return graph


def main() -> None:
    """Build and save the Florence2 Vision AI template files."""
    print("Building Florence2 Vision AI workflow template...")
    print()

    # --- Step 1: Build workflow ---
    cache = build_spec_cache()
    graph = build_workflow(cache)
    auto_layout(graph)
    workflow = graph.serialize()

    # Save workflow.json
    workflow_path = OUTPUT_DIR / "workflow.json"
    with open(workflow_path, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2)
    print(f"Workflow saved: {workflow_path}")
    print(f"  Nodes: {len(workflow['nodes'])}, Links: {len(workflow['links'])}")
    print()

    # --- Step 2: Validate (strict mode, zero errors expected) ---
    report = run_validation(workflow, mode="strict")
    print(format_report(report))
    print()

    # Only hard errors (severity="error") should block — warnings and info are expected
    # for custom-node templates (core_node_preference, LoadImage local file, etc.)
    hard_errors = [
        f
        for r in report.results
        for f in r.findings
        if f.severity.value == "error"
    ]
    if hard_errors:
        print("ERROR: Strict validation found blocking errors:")
        for e in hard_errors:
            print(f"  [ERROR] {e.message}")
        sys.exit(1)

    # --- Step 3: Generate index.json ---
    entry = generate_index_entry(
        workflow=workflow,
        name="florence2-vision-ai",
        title="Florence2 Vision AI",
        description=(
            "Demonstrates Florence2 multi-task vision AI using the ComfyUI-Florence2 node pack "
            "by kijai. Supports detailed image captioning, OCR, object detection, and grounding. "
            "This template uses the more_detailed_caption task to generate rich image descriptions."
        ),
        tags=["vision", "captioning", "florence2", "image-to-text", "AI", "multi-task"],
        username="kijai",
        vram=8,
    )

    # Override requiresCustomNodes with the correct registry ID
    entry.requiresCustomNodes = ["comfyui-florence2"]

    index_path = OUTPUT_DIR / "index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(format_index_entry(entry))
        f.write("\n")
    print(f"Index entry saved: {index_path}")

    # --- Step 4: Generate submission.md ---
    submission_md = generate_notion_markdown(
        entry=entry,
        extra_notes=(
            "Florence2 is Microsoft's multi-task vision model. "
            "The DownloadAndLoadFlorence2Model node downloads the model from Hugging Face on first run. "
            "Supported tasks include: caption, detailed_caption, more_detailed_caption, OCR, "
            "object detection, dense region caption, and grounding. "
            "Switch the task widget in Florence2Run to explore different capabilities."
        ),
    )

    submission_path = OUTPUT_DIR / "submission.md"
    with open(submission_path, "w", encoding="utf-8") as f:
        f.write(submission_md)
        f.write("\n")
    print(f"Submission doc saved: {submission_path}")
    print()
    print("All files generated successfully.")


if __name__ == "__main__":
    main()
