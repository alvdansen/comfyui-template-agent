"""Build script for the MelBandRoFormer audio stem separation template.

Creates:
  - workflow.json   (ComfyUI workflow format)
  - index.json      (template metadata)
  - submission.md   (Notion submission markdown)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure project root is on sys.path regardless of where the script is run from
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.composer.graph import WorkflowGraph
from src.composer.layout import auto_layout
from src.composer.models import NodeSpec, InputSpec, OutputSpec, parse_node_spec
from src.composer.node_specs import NodeSpecCache
from src.document.metadata import generate_index_entry, format_index_entry
from src.document.notion import generate_notion_markdown
from src.validator.engine import run_validation

OUTPUT_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Node specs (MCP-equivalent raw dicts)
# These describe the node interfaces so WorkflowGraph can build correct
# inputs/outputs arrays and validate widget/connection operations.
# ---------------------------------------------------------------------------

_SPECS_RAW: dict[str, dict] = {
    "LoadAudio": {
        "display_name": "Load Audio",
        "category": "audio",
        "input": {
            "required": {
                "audio": [["audio_1.mp3", "audio_2.wav"], {}],
            },
            "optional": {
                "start_time": ["FLOAT", {"default": 0.0, "min": 0.0}],
                "duration": ["FLOAT", {"default": 0.0, "min": 0.0}],
            },
        },
        "output": ["AUDIO"],
        "output_name": ["AUDIO"],
        "output_node": False,
    },
    "MelBandRoFormerModelLoader": {
        "display_name": "MelBandRoFormer Model Loader",
        "category": "audio/separation",
        "input": {
            "required": {
                "model": [["MelBandRoformer_fp16.safetensors", "MelBandRoformer.safetensors"], {}],
            },
            "optional": {},
        },
        "output": ["MELROFORMERMODEL"],
        "output_name": ["MELROFORMERMODEL"],
        "output_node": False,
    },
    "MelBandRoFormerSampler": {
        "display_name": "MelBandRoFormer Sampler",
        "category": "audio/separation",
        "input": {
            "required": {
                "model": ["MELROFORMERMODEL", {}],
                "audio": ["AUDIO", {}],
                "num_overlap": ["INT", {"default": 4, "min": 1, "max": 32}],
                "chunk_size": ["INT", {"default": 352800, "min": 1}],
            },
            "optional": {},
        },
        "output": ["AUDIO", "AUDIO"],
        "output_name": ["vocals", "instruments"],
        "output_node": False,
    },
    "SaveAudioMP3": {
        "display_name": "Save Audio (MP3)",
        "category": "audio",
        "input": {
            "required": {
                "audio": ["AUDIO", {}],
                "filename_prefix": ["STRING", {"default": "audio"}],
                "quality": [["128k", "192k", "256k", "320k"], {}],
            },
            "optional": {},
        },
        "output": [],
        "output_name": [],
        "output_node": True,
    },
}

# The MELROFORMERMODEL type is a custom connection type — treat it as a
# connection (not a widget) by adding it to the CONNECTION_TYPES workaround.
# We do this by patching the models module so is_widget_input returns False.
import src.composer.models as _composer_models
_composer_models.CONNECTION_TYPES.add("MELROFORMERMODEL")


def build_spec_cache() -> NodeSpecCache:
    """Parse raw spec dicts into NodeSpec objects and load into cache."""
    cache = NodeSpecCache()
    for node_type, raw in _SPECS_RAW.items():
        spec = parse_node_spec(node_type, raw)
        cache.put(node_type, spec)
    return cache


def build_workflow() -> dict:
    """Construct the MelBandRoFormer separation workflow graph."""
    specs = build_spec_cache()
    wf = WorkflowGraph(specs=specs)

    # Add nodes
    load_audio = wf.add_node("LoadAudio", title="Load Audio")
    model_loader = wf.add_node("MelBandRoFormerModelLoader", title="MelBand Model Loader")
    sampler = wf.add_node("MelBandRoFormerSampler", title="MelBand Separator")
    save_vocals = wf.add_node("SaveAudioMP3", title="Save Vocals")
    save_instruments = wf.add_node("SaveAudioMP3", title="Save Instruments")

    # Set widget values
    wf.set_widget(model_loader, "model", "MelBandRoformer_fp16.safetensors")
    wf.set_widget(sampler, "num_overlap", 4)
    wf.set_widget(sampler, "chunk_size", 352800)
    wf.set_widget(save_vocals, "filename_prefix", "vocals")
    wf.set_widget(save_instruments, "filename_prefix", "instruments")

    # Connect nodes
    # LoadAudio.AUDIO -> MelBandRoFormerSampler.audio
    wf.connect(load_audio, 0, sampler, "audio")
    # MelBandRoFormerModelLoader.MELROFORMERMODEL -> MelBandRoFormerSampler.model
    wf.connect(model_loader, 0, sampler, "model")
    # MelBandRoFormerSampler.vocals (slot 0) -> SaveAudioMP3 #1.audio
    wf.connect(sampler, 0, save_vocals, "audio")
    # MelBandRoFormerSampler.instruments (slot 1) -> SaveAudioMP3 #2.audio
    wf.connect(sampler, 1, save_instruments, "audio")

    # Apply layout
    auto_layout(wf)

    return wf.serialize()


def validate_workflow(workflow: dict) -> None:
    """Run strict validation and print results. Exits on errors."""
    report = run_validation(workflow, mode="strict")
    print(f"Validation: {report.score}")
    for result in report.results:
        if not result.passed:
            for finding in result.findings:
                print(f"  [{finding.severity.value.upper()}] [{result.rule_id}] {finding.message}")
    if not report.passed:
        # Check if only warnings (no errors)
        errors = [
            f
            for r in report.results
            for f in r.findings
            if f.severity.value == "error"
        ]
        if errors:
            print("FATAL: workflow has validation errors.", file=sys.stderr)
            sys.exit(1)
        else:
            print("Validation passed (warnings only — expected for custom nodes).")
    else:
        print("Validation passed.")


def build_index_entry(workflow: dict) -> str:
    """Generate index.json content from the workflow."""
    entry = generate_index_entry(
        workflow,
        name="melbandroformer-audio-separation",
        title="MelBandRoFormer Audio Separation",
        description=(
            "Separate any audio track into vocals and instruments using "
            "MelBandRoFormer — a state-of-the-art music source separation model "
            "by kijai. Load an audio file, run separation, and save both stems as MP3."
        ),
        tags=["audio", "stem separation", "music", "vocals", "instruments", "MelBandRoFormer"],
        username="kijai",
        vram=4,
        size=1,
    )

    # Ensure the custom node registry ID is correct.
    # generate_index_entry auto-detects custom node *type names* from the workflow.
    # The registry package ID (comfyui-melbandroformer) differs from type names,
    # so we override requiresCustomNodes with the canonical registry ID.
    entry.requiresCustomNodes = ["ComfyUI-MelBandRoFormer"]

    # SaveAudioMP3 is not in _OUTPUT_TYPES in metadata.py, so media type
    # detection falls back to "image". Override to "audio" explicitly.
    entry.mediaType = "audio"

    return format_index_entry(entry), entry


def build_notion_markdown(entry) -> str:
    """Generate Notion submission markdown from the index entry."""
    return generate_notion_markdown(
        entry,
        workflow_link="",
        extra_notes=(
            "Custom node: ComfyUI-MelBandRoFormer (https://github.com/kijai/ComfyUI-MelBandRoFormer). "
            "Install via ComfyUI Manager. Model file MelBandRoformer_fp16.safetensors should be placed "
            "in ComfyUI/models/audio_separation/ (or wherever the node expects it)."
        ),
    )


def main() -> None:
    print("Building MelBandRoFormer audio separation template...")
    print()

    # 1. Build workflow
    print("Step 1: Building workflow graph...")
    workflow = build_workflow()
    print(f"  Nodes: {len(workflow['nodes'])}, Links: {len(workflow['links'])}")

    # 2. Validate
    print()
    print("Step 2: Validating workflow (strict mode)...")
    validate_workflow(workflow)

    # 3. Write workflow.json
    workflow_path = OUTPUT_DIR / "workflow.json"
    with open(workflow_path, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2)
    print()
    print(f"Step 3: Wrote {workflow_path}")

    # 4. Generate index.json
    print()
    print("Step 4: Generating index.json...")
    index_json_str, entry = build_index_entry(workflow)
    index_path = OUTPUT_DIR / "index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_json_str)
    print(f"  Wrote {index_path}")
    print(f"  requiresCustomNodes: {entry.requiresCustomNodes}")
    print(f"  models: {entry.models}")
    print(f"  mediaType: {entry.mediaType}")

    # 5. Generate submission.md
    print()
    print("Step 5: Generating submission.md...")
    notion_md = build_notion_markdown(entry)
    submission_path = OUTPUT_DIR / "submission.md"
    with open(submission_path, "w", encoding="utf-8") as f:
        f.write(notion_md)
    print(f"  Wrote {submission_path}")

    print()
    print("Done. All 3 files written to:")
    print(f"  {OUTPUT_DIR}/")
    for fname in ("workflow.json", "index.json", "submission.md"):
        p = OUTPUT_DIR / fname
        print(f"  - {fname} ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
