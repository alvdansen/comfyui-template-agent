"""Build script for GGUF Quantized FLUX.1-schnell txt2img template.

Builds workflow.json, index.json, and submission.md for the gguf-quantized-txt2img
template using ComfyUI-GGUF custom nodes (city96) with FLUX.1-schnell model.

Run from repo root:
    python templates/gguf-quantized-txt2img/build.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add repo root to path so src imports work regardless of cwd
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.composer.graph import WorkflowGraph
from src.composer.layout import auto_layout
from src.composer.models import InputSpec, NodeSpec, OutputSpec, parse_node_spec
from src.composer.node_specs import NodeSpecCache
from src.document.metadata import format_index_entry, generate_index_entry
from src.document.notion import generate_notion_markdown
from src.validator.engine import run_validation
from src.validator.validate import format_report

TEMPLATE_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Node specs — both core ComfyUI nodes and ComfyUI-GGUF custom nodes.
# The NodeSpecCache is spec-provider-agnostic (MCP / manual / embedded).
# We define specs here so the graph builder can correctly resolve named slots
# and auto-populate widgets_values ordering.
# ---------------------------------------------------------------------------


def _make_specs() -> NodeSpecCache:
    """Build a NodeSpecCache with all specs needed for this workflow."""
    cache = NodeSpecCache()

    # --- ComfyUI-GGUF custom nodes (city96) ---

    cache.from_mcp_response("UnetLoaderGGUF", {
        "input": {
            "required": {
                # COMBO: list of filenames (placeholder value for build; real loader
                # populates from disk). We define the spec shape correctly.
                "unet_name": [["flux1-schnell-Q4_K_S.gguf"], {}],
            },
            "optional": {},
        },
        "output": ["MODEL"],
        "output_name": ["MODEL"],
        "display_name": "Unet Loader (GGUF)",
        "category": "bootleg",
        "output_node": False,
    })

    cache.from_mcp_response("DualCLIPLoaderGGUF", {
        "input": {
            "required": {
                "clip_name1": [["clip_l.safetensors"], {}],
                "clip_name2": [["t5-v1_1-xxl-encoder-Q8_0.gguf"], {}],
                "type": [["flux", "stable_diffusion", "sd3", "hunyuan_video"], {}],
            },
            "optional": {},
        },
        "output": ["CLIP"],
        "output_name": ["CLIP"],
        "display_name": "DualCLIP Loader (GGUF)",
        "category": "bootleg",
        "output_node": False,
    })

    # --- Core ComfyUI nodes ---

    cache.from_mcp_response("VAELoader", {
        "input": {
            "required": {
                "vae_name": [["ae.safetensors"], {}],
            },
            "optional": {},
        },
        "output": ["VAE"],
        "output_name": ["VAE"],
        "display_name": "Load VAE",
        "category": "loaders",
        "output_node": False,
    })

    cache.from_mcp_response("CLIPTextEncode", {
        "input": {
            "required": {
                "clip": ["CLIP", {}],
                "text": ["STRING", {"multiline": True, "default": ""}],
            },
            "optional": {},
        },
        "output": ["CONDITIONING"],
        "output_name": ["CONDITIONING"],
        "display_name": "CLIP Text Encode (Prompt)",
        "category": "conditioning",
        "output_node": False,
    })

    cache.from_mcp_response("EmptyLatentImage", {
        "input": {
            "required": {
                "width": ["INT", {"default": 512, "min": 16, "max": 16384, "step": 8}],
                "height": ["INT", {"default": 512, "min": 16, "max": 16384, "step": 8}],
                "batch_size": ["INT", {"default": 1, "min": 1, "max": 4096}],
            },
            "optional": {},
        },
        "output": ["LATENT"],
        "output_name": ["LATENT"],
        "display_name": "Empty Latent Image",
        "category": "latent",
        "output_node": False,
    })

    cache.from_mcp_response("KSampler", {
        "input": {
            "required": {
                "model": ["MODEL", {}],
                "positive": ["CONDITIONING", {}],
                "negative": ["CONDITIONING", {}],
                "latent_image": ["LATENT", {}],
                "seed": ["INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}],
                "control_after_generate": [["fixed", "increment", "decrement", "randomize"], {}],
                "steps": ["INT", {"default": 20, "min": 1, "max": 10000}],
                "cfg": ["FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.1}],
                "sampler_name": [["euler", "euler_cfg_pp", "euler_ancestral", "euler_ancestral_cfg_pp", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral", "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm", "lcm", "ipndm", "ipndm_v", "deis", "ddim", "uni_pc", "uni_pc_bh2"], {}],
                "scheduler": [["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform", "beta"], {}],
                "denoise": ["FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}],
            },
            "optional": {},
        },
        "output": ["LATENT"],
        "output_name": ["LATENT"],
        "display_name": "KSampler",
        "category": "sampling",
        "output_node": False,
    })

    cache.from_mcp_response("VAEDecode", {
        "input": {
            "required": {
                "samples": ["LATENT", {}],
                "vae": ["VAE", {}],
            },
            "optional": {},
        },
        "output": ["IMAGE"],
        "output_name": ["IMAGE"],
        "display_name": "VAE Decode",
        "category": "latent",
        "output_node": False,
    })

    cache.from_mcp_response("SaveImage", {
        "input": {
            "required": {
                "images": ["IMAGE", {}],
                "filename_prefix": ["STRING", {"default": "ComfyUI"}],
            },
            "optional": {},
        },
        "output": [],
        "output_name": [],
        "display_name": "Save Image",
        "category": "image",
        "output_node": True,
    })

    return cache


def build_workflow() -> dict:
    """Construct the GGUF FLUX.1-schnell txt2img workflow and return serialized JSON."""
    specs = _make_specs()
    g = WorkflowGraph(specs=specs)

    # ------------------------------------------------------------------
    # Add all 9 nodes
    # ------------------------------------------------------------------

    # Node 1: UnetLoaderGGUF — loads quantized FLUX UNET
    unet_id = g.add_node("UnetLoaderGGUF", title="GGUF UNET Loader")
    g.get_node(unet_id).widgets_values = ["flux1-schnell-Q4_K_S.gguf"]

    # Node 2: DualCLIPLoaderGGUF — loads CLIP-L + T5-XXL encoders
    clip_loader_id = g.add_node("DualCLIPLoaderGGUF", title="GGUF CLIP Loader")
    g.get_node(clip_loader_id).widgets_values = [
        "clip_l.safetensors",
        "t5-v1_1-xxl-encoder-Q8_0.gguf",
        "flux",
    ]

    # Node 3: VAELoader — loads FLUX VAE
    vae_loader_id = g.add_node("VAELoader")
    g.get_node(vae_loader_id).widgets_values = ["ae.safetensors"]

    # Node 4: CLIPTextEncode (positive)
    pos_encode_id = g.add_node("CLIPTextEncode", title="Positive Prompt")
    g.get_node(pos_encode_id).widgets_values = [
        "a beautiful sunset over mountains, highly detailed, 8k"
    ]

    # Node 5: CLIPTextEncode (negative) — empty for FLUX
    neg_encode_id = g.add_node("CLIPTextEncode", title="Negative Prompt")
    g.get_node(neg_encode_id).widgets_values = [""]

    # Node 6: EmptyLatentImage — 1024x1024
    latent_id = g.add_node("EmptyLatentImage")
    g.get_node(latent_id).widgets_values = [1024, 1024, 1]

    # Node 7: KSampler — FLUX settings (4 steps, cfg=1.0, euler+simple)
    ksampler_id = g.add_node("KSampler")
    g.get_node(ksampler_id).widgets_values = [42, "fixed", 4, 1.0, "euler", "simple", 1.0]

    # Node 8: VAEDecode — decodes latent to image
    vae_decode_id = g.add_node("VAEDecode")

    # Node 9: SaveImage — saves output
    save_id = g.add_node("SaveImage")
    g.get_node(save_id).widgets_values = ["gguf_flux"]

    # ------------------------------------------------------------------
    # Wire connections (using named slots resolved from specs)
    # ------------------------------------------------------------------

    # UnetLoaderGGUF MODEL → KSampler model
    g.connect(unet_id, "MODEL", ksampler_id, "model")

    # DualCLIPLoaderGGUF CLIP → CLIPTextEncode (positive) clip
    g.connect(clip_loader_id, "CLIP", pos_encode_id, "clip")

    # DualCLIPLoaderGGUF CLIP → CLIPTextEncode (negative) clip
    g.connect(clip_loader_id, "CLIP", neg_encode_id, "clip")

    # CLIPTextEncode (positive) CONDITIONING → KSampler positive
    g.connect(pos_encode_id, "CONDITIONING", ksampler_id, "positive")

    # CLIPTextEncode (negative) CONDITIONING → KSampler negative
    g.connect(neg_encode_id, "CONDITIONING", ksampler_id, "negative")

    # EmptyLatentImage LATENT → KSampler latent_image
    g.connect(latent_id, "LATENT", ksampler_id, "latent_image")

    # KSampler LATENT → VAEDecode samples
    g.connect(ksampler_id, "LATENT", vae_decode_id, "samples")

    # VAELoader VAE → VAEDecode vae
    g.connect(vae_loader_id, "VAE", vae_decode_id, "vae")

    # VAEDecode IMAGE → SaveImage images
    g.connect(vae_decode_id, "IMAGE", save_id, "images")

    # ------------------------------------------------------------------
    # Auto-layout (left-to-right DAG layering)
    # ------------------------------------------------------------------
    auto_layout(g, x_spacing=380, y_spacing=200, start_x=80, start_y=100)

    return g.serialize()


def validate_workflow(workflow: dict) -> None:
    """Run strict validation and print the report. Raises SystemExit on hard errors."""
    report = run_validation(workflow, mode="strict")
    print(format_report(report))

    # Count only error-severity findings (warnings and info are expected
    # for custom nodes and cloud-test reminders)
    error_count = sum(
        1
        for result in report.results
        for finding in result.findings
        if finding.severity.value == "error"
    )

    if error_count > 0:
        print(f"\nBUILD FAILED: {error_count} error(s) found in strict validation.")
        sys.exit(1)
    else:
        print(
            "\nValidation passed: 0 errors "
            "(warnings/info are expected for custom nodes and submission reminders)."
        )


def build_index(workflow: dict) -> str:
    """Generate index.json content string."""
    entry = generate_index_entry(
        workflow=workflow,
        name="gguf-quantized-txt2img",
        title="GGUF Quantized FLUX.1-schnell Text to Image",
        description=(
            "Text-to-image workflow using GGUF-quantized FLUX.1-schnell with "
            "ComfyUI-GGUF (city96). Runs Q4_K_S quantized UNET and Q8_0 T5-XXL encoder, "
            "significantly reducing VRAM requirements compared to full-precision models. "
            "NOTE: .gguf model files cannot be included in the template bundle and must be "
            "downloaded manually — see submission.md for download URLs and placement paths."
        ),
        tags=["flux", "gguf", "quantized", "txt2img", "low-vram", "text-to-image"],
        username="city96",
        vram=8,
        size=1024,
    )

    # Override requiresCustomNodes with the canonical registry ID for ComfyUI-GGUF
    entry.requiresCustomNodes = ["ComfyUI-GGUF"]

    return format_index_entry(entry)


# ---------------------------------------------------------------------------
# GGUF setup instructions injected into submission.md as extra_notes.
# Required because .gguf files are blocked by ComfyUI template safety policy
# and cannot be bundled — users must download models manually.
# ---------------------------------------------------------------------------

GGUF_SETUP_NOTES = """\
## GGUF Model Setup (Required — Manual Download)

> **Important:** `.gguf` files are blocked by the ComfyUI template safety policy and
> cannot be bundled in the template. You must download these model files manually before
> running this workflow.

### Models Required

| File | Size | Purpose | Download |
|------|------|---------|----------|
| `flux1-schnell-Q4_K_S.gguf` | ~6.4 GB | FLUX.1-schnell UNET (4-bit quantized) | [Hugging Face — city96/FLUX.1-schnell-gguf](https://huggingface.co/city96/FLUX.1-schnell-gguf) |
| `t5-v1_1-xxl-encoder-Q8_0.gguf` | ~8.6 GB | T5-XXL text encoder (8-bit quantized) | [Hugging Face — city96/t5-v1_1-xxl-encoder-gguf](https://huggingface.co/city96/t5-v1_1-xxl-encoder-gguf) |
| `clip_l.safetensors` | ~246 MB | CLIP-L text encoder | [Hugging Face — comfyanonymous/flux_text_encoders](https://huggingface.co/comfyanonymous/flux_text_encoders) |
| `ae.safetensors` | ~335 MB | FLUX VAE | [Hugging Face — black-forest-labs/FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell) |

### File Placement

After downloading, place files in your ComfyUI installation:

```
ComfyUI/
  models/
    unet/
      flux1-schnell-Q4_K_S.gguf          <- UNET goes here
    clip/
      clip_l.safetensors                  <- CLIP-L goes here
      t5-v1_1-xxl-encoder-Q8_0.gguf      <- T5-XXL goes here
    vae/
      ae.safetensors                      <- VAE goes here
```

### Custom Node Installation

Install **ComfyUI-GGUF** (city96) via ComfyUI Manager or manually:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/city96/ComfyUI-GGUF
cd ComfyUI-GGUF
pip install -r requirements.txt
```

Registry ID: `ComfyUI-GGUF`
GitHub: https://github.com/city96/ComfyUI-GGUF
"""


def build_notion(workflow: dict) -> str:
    """Generate submission.md content string."""
    entry = generate_index_entry(
        workflow=workflow,
        name="gguf-quantized-txt2img",
        title="GGUF Quantized FLUX.1-schnell Text to Image",
        description=(
            "Text-to-image workflow using GGUF-quantized FLUX.1-schnell with "
            "ComfyUI-GGUF (city96). Runs Q4_K_S quantized UNET and Q8_0 T5-XXL encoder, "
            "significantly reducing VRAM requirements compared to full-precision models."
        ),
        tags=["flux", "gguf", "quantized", "txt2img", "low-vram", "text-to-image"],
        username="city96",
        vram=8,
        size=1024,
    )
    entry.requiresCustomNodes = ["ComfyUI-GGUF"]

    return generate_notion_markdown(
        entry=entry,
        extra_notes=GGUF_SETUP_NOTES,
    )


def main() -> None:
    """Build all template artifacts and write to the template directory."""
    print("Building GGUF Quantized FLUX.1-schnell txt2img template...")
    print()

    # 1. Build workflow graph
    print("Step 1: Building workflow graph...")
    workflow = build_workflow()
    print(f"  Nodes: {len(workflow['nodes'])}, Links: {len(workflow['links'])}")

    # 2. Validate (strict mode, zero errors expected)
    print("\nStep 2: Validating workflow (strict mode)...")
    validate_workflow(workflow)

    # 3. Write workflow.json
    workflow_path = TEMPLATE_DIR / "workflow.json"
    workflow_path.write_text(json.dumps(workflow, indent=2))
    print(f"\nStep 3: Wrote {workflow_path}")

    # 4. Build and write index.json
    print("\nStep 4: Generating index.json...")
    index_content = build_index(workflow)
    index_path = TEMPLATE_DIR / "index.json"
    index_path.write_text(index_content)
    print(f"  Wrote {index_path}")

    # 5. Build and write submission.md
    print("\nStep 5: Generating submission.md...")
    notion_content = build_notion(workflow)
    notion_path = TEMPLATE_DIR / "submission.md"
    notion_path.write_text(notion_content)
    print(f"  Wrote {notion_path}")

    print("\nDone. Template artifacts:")
    for f in [workflow_path, index_path, notion_path]:
        size = f.stat().st_size
        print(f"  {f.relative_to(REPO_ROOT)}  ({size:,} bytes)")


if __name__ == "__main__":
    main()
