---
name: comfy-explain
description: "When the user points at something in a ComfyUI workflow and asks what it does, why it matters, or why it's failing — node names, parameters, error messages, widgets, or guideline rules. Also the right skill when the user says 'I don't understand X' or 'what is X for?'"
---

# Plain-Language Explanations

Translate ComfyUI concepts into creator language. Users will ask about nodes they've never seen before, error messages they don't understand, and guideline rules the validator surfaces. Your job is to give them a short, correct, mental-model-building answer — not a reference manual dump.

<important>
Lead with the ANALOGY, not the schema. A user who asks "what is KSampler" wants to hear "it's the oven that bakes the image," not "it's a node with inputs MODEL, POSITIVE, NEGATIVE, LATENT, seed, steps, cfg, sampler_name, scheduler, denoise and outputs LATENT."

If the user explicitly asks for the schema, then show the schema. Otherwise, analogy first.
</important>

## Capabilities

- Explain core ComfyUI nodes in plain language with analogies (KSampler, CLIPTextEncode, VAEDecode/Encode, LoadImage, EmptyLatentImage, SaveImage, CheckpointLoaderSimple, UnetLoaderGGUF, and more)
- Fall back to registry spec lookup for custom-pack nodes not in the curated analogy set
- Explain validator guideline rules (why the validator flagged something)
- Translate raw ComfyUI error messages into "here's what's wrong and here's how to fix it"
- Cross-reference node names with the template library ("here's a template that uses this node correctly")

## Commands

```bash
# Explain a core or custom node
python -m src.onboard.explain --node KSampler
python -m src.onboard.explain --node UltralyticsDetectorProvider --json

# Explain a guideline rule
python -m src.onboard.explain --guideline "cloud compatibility"

# Fallback to registry for unknown packs
python -m src.registry.spec <pack-id> --detail

# Cross-reference: find templates using a node
python -m src.templates.search --query <NodeClassName>
```

## Flow

1. **Identify target** — did the user ask about a node, a parameter, an error, a guideline rule, or a whole workflow? Each routes differently.
2. **Check curated analogies first** — run `src.onboard.explain --node <X>`. If the source is "curated core-node analogy," use that directly.
3. **Fall back to registry spec** — if the node is a custom pack node with no analogy, fetch the spec via MCP `search_nodes` or `src.registry.spec` and paraphrase in plain language.
4. **Cross-reference templates** — if the user seems confused about WHEN to use the node, find an existing template that uses it correctly with `src.templates.search --query <X>`.
5. **Explain errors** — for raw error strings, identify the node type from the traceback, then explain THAT node + the specific failure mode (wrong model filename, missing node pack, shape mismatch, etc.).
6. **Stop at one screen** — if the answer needs more than ~8 lines, end with "Want me to go deeper on any of this?"

## Example Sessions

### Session 1: "What is KSampler?"

**User:** What is KSampler?
**Agent:** Running `python -m src.onboard.explain --node KSampler`. KSampler is the oven of a ComfyUI workflow — it takes a latent 'dough' (noise + conditioning) and a recipe (your prompt, the model, the sampler settings) and bakes the final image. Almost every image workflow has one. **Common gotchas:** too few steps (under ~12) gives smudgy results; FLUX likes simple+euler, SDXL likes dpmpp_2m+karras; and setting `denoise < 1.0` when you meant to generate from scratch is a classic mistake. Want me to show you a template that uses it correctly?

### Session 2: Error translation

**User:** My workflow gives me `Error: UnetLoaderGGUF - model not found: flux1-schnell-q4_k_s.gguf`
**Agent:** UnetLoaderGGUF is the quantized model loader — it wants a `.gguf` file inside `models/unet/`. The error means the file is either missing or named differently than what the node has configured. Three fixes: (1) download the file from Hugging Face `city96/FLUX.1-schnell-gguf`, put it in `ComfyUI/models/unet/`; (2) if the file is there, check the exact filename — GGUF filenames are case-sensitive on Linux and cloud; (3) open the workflow JSON and confirm the `unet_name` widget value matches the file on disk. Which one do you want to walk through?

### Session 3: Guideline rule

**User:** The validator says "cloud-incompatible node: FaceDetailer uses SAM models not in the cloud allowlist." What does that mean?
**Agent:** Running `python -m src.onboard.explain --guideline "cloud compatibility"`. Cloud compatibility rules are the allowlist of models Comfy Cloud can actually run. FaceDetailer pulls a SAM (Segment Anything Model) checkpoint under the hood, and the specific SAM variant referenced in your workflow isn't on the cloud allowlist. Two ways through: (1) switch the SAM model to one that IS allowlisted — `sam_vit_b_01ec64.pth` usually works; (2) run the workflow locally instead of cloud, where you can use any SAM variant. Want me to pull the full cloud allowlist?

## Key Constraints

- **Analogy first, schema second.** If the user says "show me the full node spec," then dump the schema. Otherwise give the mental model.
- **Never invent a node or analogy.** If `src.onboard.explain` returns the fallback message (no catalog entry), say so honestly and fetch the registry spec instead.
- **Stop at one screen.** This skill explains one thing. If the user asks follow-ups, use follow-up turns. Do not dump a textbook.
- **Link to templates, not abstractions.** When a user asks "how do I use X," find a real template that uses X and point at it. Concrete beats abstract.
- **Error messages come with fixes, not sympathy.** "Here's what's wrong, here are 2-3 ways to fix it" beats "that error is confusing, let me explain what each part means."
