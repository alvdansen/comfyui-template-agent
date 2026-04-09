"""Build script for the Impact Pack Face Detailer template.

Creates workflow.json, index.json, and submission.md.
Run from project root:
    python templates/impact-pack-face-detailer/build.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure project root is on sys.path when run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.composer.graph import WorkflowGraph
from src.document.metadata import format_index_entry, generate_index_entry
from src.document.notion import generate_notion_markdown
from src.validator.engine import run_validation
from src.validator.validate import format_report

OUTPUT_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Step 1: Build the raw workflow JSON
#
# WorkflowGraph.add_node() builds inputs/outputs only when a NodeSpec is
# available.  Because the custom Impact Pack node specs require a live MCP
# connection, we construct the full workflow dict directly — exactly as the
# LiteGraph runtime expects it — then round-trip it through from_json() /
# serialize() to get the validated, canonical form.
# ---------------------------------------------------------------------------

def build_workflow_dict() -> dict:
    """Return the complete workflow JSON dict for the Face Detailer template."""

    # Node IDs (1-based, sequential)
    # 1  CheckpointLoaderSimple
    # 2  CLIPTextEncode (positive)
    # 3  CLIPTextEncode (negative)
    # 4  EmptyLatentImage
    # 5  KSampler
    # 6  VAEDecode
    # 7  UltralyticsDetectorProvider
    # 8  SAMLoader
    # 9  FaceDetailer
    # 10 PreviewImage
    # 11 SaveImage

    nodes = [
        # ── 1. CheckpointLoaderSimple ──────────────────────────────────────
        {
            "id": 1,
            "type": "CheckpointLoaderSimple",
            "pos": [30, 300],
            "size": [315, 98],
            "flags": {},
            "order": 0,
            "mode": 0,
            "inputs": [],
            "outputs": [
                {"name": "MODEL",  "type": "MODEL",  "links": [1, 12]},
                {"name": "CLIP",   "type": "CLIP",   "links": [2, 3]},
                {"name": "VAE",    "type": "VAE",    "links": [4, 17]},
            ],
            "properties": {"Node name for S&R": "CheckpointLoaderSimple"},
            "widgets_values": ["v1-5-pruned-emaonly.safetensors"],
        },

        # ── 2. CLIPTextEncode (positive) ───────────────────────────────────
        {
            "id": 2,
            "type": "CLIPTextEncode",
            "title": "Positive Prompt",
            "pos": [400, 190],
            "size": [425, 180],
            "flags": {},
            "order": 1,
            "mode": 0,
            "inputs": [
                {"name": "clip", "type": "CLIP", "link": 2},
            ],
            "outputs": [
                {"name": "CONDITIONING", "type": "CONDITIONING", "links": [5, 13]},
            ],
            "properties": {"Node name for S&R": "CLIPTextEncode"},
            "widgets_values": [
                "a portrait photo of a woman, highly detailed face, sharp focus, studio lighting"
            ],
        },

        # ── 3. CLIPTextEncode (negative) ───────────────────────────────────
        {
            "id": 3,
            "type": "CLIPTextEncode",
            "title": "Negative Prompt",
            "pos": [400, 400],
            "size": [425, 180],
            "flags": {},
            "order": 2,
            "mode": 0,
            "inputs": [
                {"name": "clip", "type": "CLIP", "link": 3},
            ],
            "outputs": [
                {"name": "CONDITIONING", "type": "CONDITIONING", "links": [6, 14]},
            ],
            "properties": {"Node name for S&R": "CLIPTextEncode"},
            "widgets_values": ["blurry, low quality, deformed"],
        },

        # ── 4. EmptyLatentImage ────────────────────────────────────────────
        {
            "id": 4,
            "type": "EmptyLatentImage",
            "pos": [400, 610],
            "size": [315, 106],
            "flags": {},
            "order": 3,
            "mode": 0,
            "inputs": [],
            "outputs": [
                {"name": "LATENT", "type": "LATENT", "links": [7]},
            ],
            "properties": {"Node name for S&R": "EmptyLatentImage"},
            "widgets_values": [512, 768, 1],
        },

        # ── 5. KSampler ────────────────────────────────────────────────────
        {
            "id": 5,
            "type": "KSampler",
            "pos": [870, 300],
            "size": [315, 262],
            "flags": {},
            "order": 4,
            "mode": 0,
            "inputs": [
                {"name": "model",        "type": "MODEL",        "link": 1},
                {"name": "positive",     "type": "CONDITIONING", "link": 5},
                {"name": "negative",     "type": "CONDITIONING", "link": 6},
                {"name": "latent_image", "type": "LATENT",       "link": 7},
            ],
            "outputs": [
                {"name": "LATENT", "type": "LATENT", "links": [8]},
            ],
            "properties": {"Node name for S&R": "KSampler"},
            "widgets_values": [42, "fixed", 20, 7.0, "euler", "normal", 1.0],
        },

        # ── 6. VAEDecode ───────────────────────────────────────────────────
        {
            "id": 6,
            "type": "VAEDecode",
            "pos": [1240, 300],
            "size": [210, 46],
            "flags": {},
            "order": 5,
            "mode": 0,
            "inputs": [
                {"name": "samples", "type": "LATENT", "link": 8},
                {"name": "vae",     "type": "VAE",    "link": 4},
            ],
            "outputs": [
                {"name": "IMAGE", "type": "IMAGE", "links": [9, 10]},
            ],
            "properties": {"Node name for S&R": "VAEDecode"},
            "widgets_values": [],
        },

        # ── 7. UltralyticsDetectorProvider ────────────────────────────────
        {
            "id": 7,
            "type": "UltralyticsDetectorProvider",
            "pos": [870, 620],
            "size": [315, 80],
            "flags": {},
            "order": 6,
            "mode": 0,
            "inputs": [],
            "outputs": [
                {"name": "BBOX_DETECTOR",  "type": "BBOX_DETECTOR",  "links": [15]},
                {"name": "SEGM_DETECTOR",  "type": "SEGM_DETECTOR",  "links": []},
            ],
            "properties": {"Node name for S&R": "UltralyticsDetectorProvider"},
            "widgets_values": ["face_yolov8m.pt"],
        },

        # ── 8. SAMLoader ──────────────────────────────────────────────────
        {
            "id": 8,
            "type": "SAMLoader",
            "pos": [870, 740],
            "size": [315, 80],
            "flags": {},
            "order": 7,
            "mode": 0,
            "inputs": [],
            "outputs": [
                {"name": "SAM_MODEL", "type": "SAM_MODEL", "links": [16]},
            ],
            "properties": {"Node name for S&R": "SAMLoader"},
            "widgets_values": ["sam_vit_b_01ec64.pth", "AUTO"],
        },

        # ── 9. FaceDetailer ───────────────────────────────────────────────
        {
            "id": 9,
            "type": "FaceDetailer",
            "pos": [1240, 500],
            "size": [380, 420],
            "flags": {},
            "order": 8,
            "mode": 0,
            "inputs": [
                {"name": "image",         "type": "IMAGE",         "link": 9},
                {"name": "model",         "type": "MODEL",         "link": 12},
                {"name": "clip",          "type": "CLIP",          "link": None},
                {"name": "vae",           "type": "VAE",           "link": 17},
                {"name": "positive",      "type": "CONDITIONING",  "link": 13},
                {"name": "negative",      "type": "CONDITIONING",  "link": 14},
                {"name": "bbox_detector", "type": "BBOX_DETECTOR", "link": 15},
                {"name": "sam_model_opt", "type": "SAM_MODEL",     "link": 16},
            ],
            "outputs": [
                {"name": "IMAGE",          "type": "IMAGE",  "links": [18]},
                {"name": "CROPPED_REFINED","type": "IMAGE",  "links": []},
                {"name": "CROPPED_ENHANCED_ALPHA","type": "IMAGE","links": []},
                {"name": "MASK",           "type": "MASK",   "links": []},
                {"name": "DETAILER_PIPE",  "type": "DETAILER_PIPE","links": []},
                {"name": "CNET_IMAGES",    "type": "IMAGE",  "links": []},
            ],
            "properties": {"Node name for S&R": "FaceDetailer"},
            "widgets_values": [
                384,    # guide_size
                True,   # guide_size_for
                1024,   # max_size
                42,     # seed
                "fixed",# control_after_generate
                20,     # steps
                7.0,    # cfg
                "euler",# sampler_name
                "normal",# scheduler
                0.4,    # denoise
                5,      # feather
                True,   # noise_mask
                True,   # force_inpaint
                0.5,    # bbox_threshold
                10,     # bbox_dilation
                2.0,    # bbox_crop_factor
                "False",# sam_detection_hint
                0,      # sam_dilation
                0.93,   # sam_threshold
                512,    # sam_bbox_expansion
                0.1,    # sam_mask_hint_threshold
                "False",# sam_mask_hint_use_negative
                "center-1",# drop_size
                None,   # wildcard (optional, not connected)
                1,      # cycle
                False,  # inpaint_model
                0,      # noise_mask_feather
            ],
        },

        # ── 10. PreviewImage (Before) ─────────────────────────────────────
        {
            "id": 10,
            "type": "PreviewImage",
            "title": "Before",
            "pos": [1500, 190],
            "size": [210, 246],
            "flags": {},
            "order": 9,
            "mode": 0,
            "inputs": [
                {"name": "images", "type": "IMAGE", "link": 10},
            ],
            "outputs": [],
            "properties": {"Node name for S&R": "PreviewImage"},
            "widgets_values": [],
        },

        # ── 11. SaveImage (After) ─────────────────────────────────────────
        {
            "id": 11,
            "type": "SaveImage",
            "title": "After",
            "pos": [1680, 500],
            "size": [315, 270],
            "flags": {},
            "order": 10,
            "mode": 0,
            "inputs": [
                {"name": "images", "type": "IMAGE", "link": 18},
            ],
            "outputs": [],
            "properties": {"Node name for S&R": "SaveImage"},
            "widgets_values": ["face_detailed"],
        },
    ]

    # Links: [link_id, src_node_id, src_slot, tgt_node_id, tgt_slot, type]
    links = [
        [1,  1, 0, 5,  0, "MODEL"],         # Checkpoint MODEL → KSampler model
        [2,  1, 1, 2,  0, "CLIP"],           # Checkpoint CLIP  → Positive CLIP
        [3,  1, 1, 3,  0, "CLIP"],           # Checkpoint CLIP  → Negative CLIP
        [4,  1, 2, 6,  1, "VAE"],            # Checkpoint VAE   → VAEDecode vae
        [5,  2, 0, 5,  1, "CONDITIONING"],   # Positive → KSampler positive
        [6,  3, 0, 5,  2, "CONDITIONING"],   # Negative → KSampler negative
        [7,  4, 0, 5,  3, "LATENT"],         # EmptyLatent → KSampler latent_image
        [8,  5, 0, 6,  0, "LATENT"],         # KSampler LATENT → VAEDecode samples
        [9,  6, 0, 9,  0, "IMAGE"],          # VAEDecode IMAGE → FaceDetailer image
        [10, 6, 0, 10, 0, "IMAGE"],          # VAEDecode IMAGE → PreviewImage
        [12, 1, 0, 9,  1, "MODEL"],          # Checkpoint MODEL → FaceDetailer model
        [13, 2, 0, 9,  4, "CONDITIONING"],   # Positive → FaceDetailer positive
        [14, 3, 0, 9,  5, "CONDITIONING"],   # Negative → FaceDetailer negative
        [15, 7, 0, 9,  6, "BBOX_DETECTOR"],  # UltralyticsDet → FaceDetailer bbox_detector
        [16, 8, 0, 9,  7, "SAM_MODEL"],      # SAMLoader → FaceDetailer sam_model_opt
        [17, 1, 2, 9,  3, "VAE"],            # Checkpoint VAE → FaceDetailer vae
        [18, 9, 0, 11, 0, "IMAGE"],          # FaceDetailer IMAGE → SaveImage
    ]

    return {
        "last_node_id": 11,
        "last_link_id": 18,
        "nodes": nodes,
        "links": links,
        "groups": [],
        "config": {},
        "extra": {},
        "version": 0.4,
    }


def main() -> None:
    print("=== Impact Pack Face Detailer — Build Script ===\n")

    # ------------------------------------------------------------------
    # Step 1: Build workflow
    # ------------------------------------------------------------------
    print("Step 1: Building workflow graph...")
    raw_dict = build_workflow_dict()

    # Round-trip through WorkflowGraph to validate structure and get
    # canonical serialization (format detection assert runs on serialize())
    graph = WorkflowGraph.from_json(raw_dict)
    workflow = graph.serialize()
    print(f"  {len(workflow['nodes'])} nodes, {len(workflow['links'])} links")

    # ------------------------------------------------------------------
    # Step 2: Save workflow.json
    # ------------------------------------------------------------------
    workflow_path = OUTPUT_DIR / "workflow.json"
    workflow_path.write_text(json.dumps(workflow, indent=2))
    print(f"  Saved: {workflow_path}")

    # ------------------------------------------------------------------
    # Step 3: Validate (strict mode)
    # ------------------------------------------------------------------
    print("\nStep 2: Validating (strict mode)...")
    report = run_validation(workflow, mode="strict")
    print(format_report(report))

    # Count errors — info/warning findings are expected and acceptable
    error_findings = [
        f for r in report.results for f in r.findings
        if f.severity.value == "error"
    ]
    if error_findings:
        print(f"\nFAILED: {len(error_findings)} error(s) found.")
        sys.exit(1)
    else:
        print("  Zero errors — validation clean.")

    # ------------------------------------------------------------------
    # Step 4: Generate index.json
    #
    # generate_index_entry() auto-detects requiresCustomNodes as node type
    # names (FaceDetailer, SAMLoader, UltralyticsDetectorProvider).
    # The template spec requires package-level declarations:
    #   comfyui-impact-pack    (FaceDetailer, SAMLoader)
    #   comfyui-impact-subpack (UltralyticsDetectorProvider)
    # We override requiresCustomNodes after auto-detection.
    # ------------------------------------------------------------------
    print("\nStep 3: Generating index.json...")
    entry = generate_index_entry(
        workflow=workflow,
        name="impact-pack-face-detailer",
        title="Impact Pack Face Detailer",
        description=(
            "Automatically detects and re-generates faces at higher quality using "
            "ComfyUI Impact Pack. Runs a base SD 1.5 generation, then applies "
            "FaceDetailer with YOLO face detection and SAM segmentation to refine "
            "facial details with a lower denoise pass — before/after previews included."
        ),
        tags=["face", "inpaint", "enhancement", "impact-pack", "SD1.5", "detailing"],
        username="comfy-template-agent",
        vram=8,
    )

    # Override with package-level custom node declarations
    entry.requiresCustomNodes = [
        "comfyui-impact-pack",
        "comfyui-impact-subpack",
    ]

    index_json = format_index_entry(entry)
    index_path = OUTPUT_DIR / "index.json"
    index_path.write_text(index_json)
    print(f"  Saved: {index_path}")
    print(f"  requiresCustomNodes: {entry.requiresCustomNodes}")
    print(f"  models: {entry.models}")

    # ------------------------------------------------------------------
    # Step 5: Generate submission.md
    # ------------------------------------------------------------------
    print("\nStep 4: Generating submission.md...")
    markdown = generate_notion_markdown(
        entry=entry,
        extra_notes=(
            "FaceDetailer requires TWO custom node packs:\n"
            "- comfyui-impact-pack (FaceDetailer, SAMLoader)\n"
            "- comfyui-impact-subpack (UltralyticsDetectorProvider / YOLO)\n\n"
            "Models required:\n"
            "- Base checkpoint: v1-5-pruned-emaonly.safetensors\n"
            "- YOLO detector: face_yolov8m.pt (place in models/ultralytics/bbox/)\n"
            "- SAM: sam_vit_b_01ec64.pth (place in models/sams/)"
        ),
    )
    submission_path = OUTPUT_DIR / "submission.md"
    submission_path.write_text(markdown)
    print(f"  Saved: {submission_path}")

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    print("\n=== Build complete ===")
    print(f"  workflow.json  → {workflow_path}")
    print(f"  index.json     → {index_path}")
    print(f"  submission.md  → {submission_path}")


if __name__ == "__main__":
    main()
