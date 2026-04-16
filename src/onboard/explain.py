"""Creator-friendly node and workflow explanations for /comfy-explain.

Ground truth lives in three places:
  1. data/core_nodes.json       — stable core ComfyUI nodes and their roles
  2. data/guidelines.json       — submission rules / gotchas
  3. the live registry          — fetched via src/registry for non-core packs

This module assembles a short creator-readable paragraph that answers
"what does X do and when would I use it?" without dumping a reference page.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CORE_NODES_PATH = DATA_DIR / "core_nodes.json"
GUIDELINES_PATH = DATA_DIR / "guidelines.json"


@dataclass(frozen=True)
class Explanation:
    target: str
    plain_language: str
    analogy: str
    typical_use: str
    common_mistakes: tuple[str, ...]
    source: str

    def render(self) -> str:
        mistakes = "\n  - ".join(self.common_mistakes) if self.common_mistakes else "—"
        return (
            f"# {self.target}\n\n"
            f"**What it is:** {self.plain_language}\n\n"
            f"**Analogy:** {self.analogy}\n\n"
            f"**Typical use:** {self.typical_use}\n\n"
            f"**Common mistakes:**\n  - {mistakes}\n\n"
            f"_source: {self.source}_\n"
        )


@lru_cache(maxsize=1)
def _load_core() -> dict[str, dict]:
    if not CORE_NODES_PATH.exists():
        return {}
    return json.loads(CORE_NODES_PATH.read_text())


@lru_cache(maxsize=1)
def _load_guidelines() -> dict:
    if not GUIDELINES_PATH.exists():
        return {}
    return json.loads(GUIDELINES_PATH.read_text())


# Curated analogies for the nodes beginners actually ask about.
# Keep short — the agent's own reasoning fills in context.
ANALOGIES: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "KSampler": (
        "The oven. It takes a latent 'dough' and a recipe (prompt + model) and bakes the final image.",
        "Almost every image workflow has one. It's where generation actually happens.",
        (
            "Using too few steps (under ~12) gives smudgy results for most models.",
            "Picking the wrong sampler/scheduler combo for the model — FLUX prefers simple+euler, SDXL prefers dpmpp_2m+karras.",
            "Setting denoise < 1.0 when you meant to generate from scratch (that's for img2img).",
        ),
    ),
    "CLIPTextEncode": (
        "The translator. Converts your written prompt into a numeric format the sampler can actually use.",
        "Any workflow that takes text input has one or two of these (positive + negative prompt).",
        (
            "Forgetting to connect both positive AND negative — negative can be empty but the wire must exist.",
            "Using SDXL-style prompts (comma-separated booru tags) on a FLUX model — FLUX prefers natural sentences.",
        ),
    ),
    "VAEDecode": (
        "The developer tray. Takes the latent image (compressed) and turns it into actual pixels you can see.",
        "Runs once near the end of every image workflow.",
        (
            "Using the wrong VAE for the model (e.g. an SD1.5 VAE with an SDXL model) produces washed-out or color-shifted output.",
        ),
    ),
    "VAEEncode": (
        "The reverse developer tray. Takes a real pixel image and compresses it back into the latent space the sampler works in.",
        "Any img2img, inpainting, or control workflow that feeds an existing image into generation.",
        (
            "Same VAE/model mismatch issue as VAEDecode — use the matching VAE.",
        ),
    ),
    "LoadImage": (
        "The file picker. Reads a PNG/JPG/WebP from disk and makes it available to the rest of the graph.",
        "Any workflow that starts with an existing image: img2img, face fix, upscale, inpaint.",
        (
            "On Comfy Cloud the path must be an uploaded image, not a local filename.",
            "PNG transparency is preserved but most downstream nodes ignore alpha — expect flattened output.",
        ),
    ),
    "EmptyLatentImage": (
        "The blank canvas. Tells the sampler 'start from noise at this size' for text-to-image.",
        "Text-to-image workflows only. Replaced by VAEEncode for img2img.",
        (
            "Picking a non-multiple-of-8 resolution — most models need width and height divisible by 8 (or 16 for some).",
            "Batch size > 1 multiplies VRAM use roughly linearly.",
        ),
    ),
    "SaveImage": (
        "The output folder. Writes the final pixel image to disk with a filename prefix you choose.",
        "Every workflow that produces a visible image ends here.",
        (
            "PreviewImage is similar but doesn't persist — use SaveImage if you actually want the file.",
        ),
    ),
    "CheckpointLoaderSimple": (
        "The model loader. Loads a .safetensors/.ckpt file and gives you three wires: MODEL, CLIP, VAE.",
        "SD1.5, SD2, SDXL, SD3, Pony workflows. Not used for FLUX GGUF (that uses UnetLoaderGGUF + separate CLIP + VAE).",
        (
            "Model filename must match the exact file in models/checkpoints — case sensitive on Linux/Cloud.",
        ),
    ),
    "UnetLoaderGGUF": (
        "The quantized model loader. Loads a GGUF-compressed UNet — enables running FLUX or SD3 on consumer VRAM.",
        "FLUX.1-schnell and FLUX.1-dev at Q4/Q8 for 6-12 GB cards. Requires separate CLIP and VAE loaders.",
        (
            "Must pair with CLIPLoader and VAELoader — it does NOT bundle them like CheckpointLoaderSimple.",
            "Different GGUF quants have very different quality — Q4_K_S is the smallest, Q8 is near-lossless.",
        ),
    ),
}


def explain_node(target: str) -> Explanation:
    core = _load_core()
    core_entry = core.get(target) or core.get(target.lower())

    analogy_entry = ANALOGIES.get(target)
    if analogy_entry:
        plain_lang, typical, mistakes = analogy_entry
        return Explanation(
            target=target,
            plain_language=plain_lang.split(". ")[0] + ".",
            analogy=plain_lang,
            typical_use=typical,
            common_mistakes=mistakes,
            source="curated core-node analogy",
        )

    if core_entry:
        desc = core_entry.get("description") or core_entry.get("summary") or "Core ComfyUI node."
        category = core_entry.get("category", "unknown")
        return Explanation(
            target=target,
            plain_language=desc,
            analogy=f"(no plain-language analogy yet — category: {category})",
            typical_use="See `python -m src.registry.search --query " + target + "` for templates using this node.",
            common_mistakes=tuple(core_entry.get("gotchas", []) or []),
            source="data/core_nodes.json",
        )

    return Explanation(
        target=target,
        plain_language=(
            f"'{target}' is not in the curated core-node catalog. "
            "Fetch its registry spec via `python -m src.registry.spec <pack-id>` or MCP `search_nodes` "
            "to see the actual inputs and outputs."
        ),
        analogy="(custom-pack node — no stock analogy)",
        typical_use=(
            "Search the template library with "
            f"`python -m src.templates.search --query {target}` to see if any existing template uses it."
        ),
        common_mistakes=(
            "Custom pack may be missing on cloud — check the registry for the pack-id before using.",
        ),
        source="generated fallback (no catalog entry)",
    )


def explain_guideline(topic: str) -> Explanation:
    gl = _load_guidelines()
    if not gl:
        return Explanation(
            target=topic,
            plain_language="Guidelines file not loaded.",
            analogy="—",
            typical_use="Run from a project that has data/guidelines.json.",
            common_mistakes=(),
            source="missing",
        )
    hits = [
        (k, v) for k, v in gl.items() if topic.lower() in k.lower() or topic.lower() in str(v).lower()
    ]
    if not hits:
        return Explanation(
            target=topic,
            plain_language=f"No guideline rule matches '{topic}'.",
            analogy="—",
            typical_use="Try `python -m src.validator.validate --list-rules` for the full list.",
            common_mistakes=(),
            source="data/guidelines.json",
        )
    first_key, first_val = hits[0]
    return Explanation(
        target=first_key,
        plain_language=str(first_val)[:400],
        analogy="Guideline rules act like a linter for workflow JSON.",
        typical_use=f"Surfaces in `python -m src.validator.validate` output when the rule fires.",
        common_mistakes=(),
        source="data/guidelines.json",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Explain a ComfyUI node or guideline in plain language")
    parser.add_argument("--node", help="Node class name to explain")
    parser.add_argument("--guideline", help="Guideline keyword to explain")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args(argv)

    if not args.node and not args.guideline:
        parser.error("Pass --node or --guideline")

    if args.node:
        ex = explain_node(args.node)
    else:
        ex = explain_guideline(args.guideline)

    if args.json:
        print(
            json.dumps(
                {
                    "target": ex.target,
                    "plain_language": ex.plain_language,
                    "analogy": ex.analogy,
                    "typical_use": ex.typical_use,
                    "common_mistakes": list(ex.common_mistakes),
                    "source": ex.source,
                },
                indent=2,
            )
        )
    else:
        print(ex.render())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
