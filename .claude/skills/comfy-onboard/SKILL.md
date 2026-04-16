---
name: comfy-onboard
description: "When a new user wants to get their first ComfyUI generation running — they don't have a workflow yet, don't know what template fits their goal, or say something like 'I just want to try ComfyUI' or 'help me get started'"
---

# First-Run Onboarding

Close the cold-start cliff. Take a user from "what do I even do here" to a validated, running workflow in one conversation. Lean on the existing compose/validate skills for the heavy lifting — this skill's job is intent matching and hand-holding.

<important>
This skill is for users who may have zero ComfyUI experience. Do NOT assume they know what a node is, what a KSampler is, what a latent is, or the difference between workflow format and API format. Explain in plain language first, jargon second.

Always confirm before writing any file. Never auto-scaffold without the user saying yes.
</important>

<important if="user is completely new">
Start by asking two things:

1. **What do you want to make?** (one sentence is fine)
2. **Do you have ComfyUI running yet?** (local app, cloud, or neither)

If neither, offer the cloud path first — zero install, Comfy Org API handles auth, first image in under 2 minutes. Point them at the Comfy Org signup if they don't have an account.
</important>

## Capabilities

- Match a user's natural-language goal to a starter template from the onboarding catalog
- Show the user what the starter will produce BEFORE building anything
- Scaffold the chosen starter via `comfy-compose`
- Explain every node in the scaffolded graph in plain language (delegates to `comfy-explain`)
- Validate the result via `comfy-validate` and translate errors into fixes
- Offer concrete next hops ("here are 3 ways to take this further")

## Commands

```bash
# Match a goal to starter templates (text output)
python -m src.onboard.catalog --goal "I want to make an image from text"

# JSON mode for structured downstream use
python -m src.onboard.catalog --goal "fix the face in my image" --json

# Limit to top N candidates
python -m src.onboard.catalog --goal "caption my photos" --top 2

# Scaffold the chosen starter (reuses comfy-compose)
python -m src.composer.compose --scaffold gguf-quantized-txt2img --output my-first-workflow.json

# Validate the scaffolded workflow
python -m src.validator.validate --file my-first-workflow.json
```

## Flow

1. **Ask** — "What do you want to make?" + "Local or cloud?"
2. **Match** — run `src.onboard.catalog` with the user's words. Show top 1-3 candidates with the `why` field.
3. **Confirm** — let the user pick or veto. If no strong match, show the fallback list and ask them to describe their goal differently.
4. **Scaffold** — run `src.composer.compose --scaffold <template>`. Save to a filename the user picked (default `my-first-workflow.json`).
5. **Explain** — walk through the scaffolded graph. For each node call `src.onboard.explain --node <ClassName>` and read the creator-friendly analogy aloud. Keep this terse — 1 sentence per node unless the user asks for more.
6. **Validate** — run `src.validator.validate --file <path>`. If errors, translate them. If clean, say so and move on.
7. **Run** — if they're on cloud, submit via MCP `submit_workflow`. If local, tell them to open ComfyUI at http://127.0.0.1:8188 and drop the file into the canvas.
8. **Next hops** — read out the `next_hops` list from the matched starter. Ask which one they want to try, or suggest stopping here and going to `/comfy-flow` to author a full template.

## Example Session

**User:** I just want to try ComfyUI — I want to make an image from text.
**Agent:** Welcome. Two questions: do you have ComfyUI running locally already, or would you like to use Comfy Cloud? And do you have a rough idea of what you want the image to be (a portrait, a landscape, an abstract thing)?
**User:** Cloud. And I want a portrait of a fox in a library.
**Agent:** Good — cloud means no install, no model downloads, and the API auth is handled for you. Running `python -m src.onboard.catalog --goal "portrait of a fox in a library, text to image"`. One strong match: **text-to-image-fast** → the FLUX.1-schnell GGUF starter. FLUX is currently the best open text-to-image model and schnell is the fast variant — one image in about 8 seconds. OK if I scaffold that for you?
**User:** Yes.
**Agent:** Running `python -m src.composer.compose --scaffold gguf-quantized-txt2img --output my-first-workflow.json`. Scaffolded 8 nodes. Let me explain each one briefly: **UnetLoaderGGUF** loads the compressed FLUX model. **CLIPLoader** and **VAELoader** load the two helper models FLUX needs. **EmptyLatentImage** is the blank canvas — I've set it to 1024x1024. **CLIPTextEncode** takes your prompt and converts it to numbers the model can use. **KSampler** is the oven that actually bakes the image. **VAEDecode** turns the latent back into pixels. **SaveImage** writes the PNG to disk. Now validating... [runs validator] All 12 checks pass. Ready to submit. Shall I send it to Comfy Cloud with the prompt "a detailed portrait of a fox sitting in a victorian library, warm lighting"?
**User:** Yes.
**Agent:** [submits via MCP, polls, returns image URL] Done — here's your first FLUX image. Three next hops: swap to FLUX.1-dev for higher quality (slower), add a LoRA for style control, or try img2img with LoadImage + VAEEncode. Which one interests you? Or we can stop here.

## Key Constraints

- Never scaffold without explicit user confirmation.
- Never pretend a starter will do something it won't — if the user's goal is outside the catalog, show the fallback message honestly.
- The catalog has only 4 starters in v2.0.0 (text2img-fast, face-fix, caption, audio-sep). Do not invent a fifth one.
- If `comfy-compose` fails (MCP server not connected, node spec missing), drop into `comfy-explain` mode and walk the user through the error — don't retry blindly.
- Keep node explanations short. A new user does not need the full input/output schema — they need the analogy.
- This skill does NOT try to teach ComfyUI. It tries to get the user one working result, fast, so they feel capable enough to ask the next question.
