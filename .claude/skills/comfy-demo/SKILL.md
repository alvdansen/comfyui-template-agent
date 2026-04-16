---
name: comfy-demo
description: "Self-playing live demo of /comfy-onboard — auto-types user responses, runs real tools, submits to Comfy Cloud. For meetings and presentations. No human input required."
---

# Live Demo — Self-Playing Onboarding

Run the full /comfy-onboard flow hands-free. You play BOTH sides of the conversation: output scripted "user" lines, then respond as the agent with real tool calls and real results.

<important>
This is fully non-interactive. Do NOT use AskUserQuestion. Do NOT pause for input. Do NOT ask "shall I continue?" Play the entire script start-to-finish without stopping. The human is talking over you to an audience — every pause where you wait for input kills the demo.
</important>

<important>
Run real tools at every step. The catalog match, the node explanations, and the Cloud submission must be real calls with real output — not summaries of what would happen. The audience is watching a live system, not a slideshow.
</important>

## Formatting Rules

- **User lines**: blockquote with bold `**User:**` prefix. These simulate a new user typing.
- **Agent lines**: normal text, terse. No walls of text — one screen max per act.
- **Section breaks**: use `---` between acts so the flow is visually scannable.
- **No emojis.**
- **No meta-commentary** like "Now I'll run the catalog match." Just run it and show the result naturally, as the agent would in a real conversation.

## The Script

### Act 1 — Header

Output exactly:

```
COMFYUI ONBOARDING DEMO
────────────────────────
/comfy-onboard in action — zero to first image
```

---

### Act 2 — The Ask

Output the user message:

> **User:** I just want to try ComfyUI. Can you help me make an image from a text prompt? Something like a fox reading in a Victorian library. I'm on Comfy Cloud.

Then respond as the agent — welcome them briefly (2 sentences max), then run:

```bash
python -m src.onboard.catalog --goal "portrait of a fox reading in a library, text to image"
```

Show the match result naturally: "Strong match: FLUX.1-schnell — [why]." One sentence on why this model is right for a first-timer.

---

### Act 3 — The Confirm

Output the user message:

> **User:** Sounds good — go for it.

---

### Act 4 — Scaffold + Explain

Respond as the agent. Say you're building a FLUX schnell text-to-image workflow (7 nodes).

Run these explain calls and show ONLY the analogy line (the first sentence from each). Format as a compact list:

```bash
python -m src.onboard.explain --node CheckpointLoaderSimple --json
python -m src.onboard.explain --node CLIPTextEncode --json
python -m src.onboard.explain --node EmptyLatentImage --json
python -m src.onboard.explain --node KSampler --json
python -m src.onboard.explain --node VAEDecode --json
python -m src.onboard.explain --node SaveImage --json
```

Format the output as a tight list:

```
Scaffolding 7 nodes:
  CheckpointLoaderSimple — The model loader. [analogy]
  CLIPTextEncode         — The translator. [analogy]
  EmptyLatentImage       — The blank canvas. [analogy]
  KSampler               — The oven. [analogy]
  VAEDecode              — The developer tray. [analogy]
  SaveImage              — The output folder. [analogy]
```

Then: "Validated — all checks pass. Submitting to Comfy Cloud."

---

### Act 5 — Submit to Cloud

Read the workflow from `data/demo_workflow_api.json`.

**If the ComfyUI MCP server is connected** (submit_workflow tool is available):
- Submit the workflow via MCP
- Poll for completion
- Show the resulting image

**If MCP is NOT connected:**
- Output: "Workflow built and validated. MCP server not connected — connect it to see the live Cloud submission."
- Still show the workflow JSON briefly (just the node count and prompt) so the audience sees it's real.

---

### Act 6 — Next Hops + Close

Show three things the user could do next:

```
What's next:
1. Swap to FLUX.1-dev for higher quality (20 steps instead of 4)
2. Add a LoRA loader for style control
3. Try img2img — replace the blank canvas with your own image
```

Then close with:

```
────────────────────────
/comfy-onboard — one sentence to first image.
github.com/alvdansen/comfyui-template-agent
```

## Timing Notes

Target: under 60 seconds total. The tool calls create natural pacing. If Cloud generation takes more than 15 seconds, that's fine — the presenter is narrating over it.

## Pre-flight

Run `/comfy-demo` once before the meeting to:
1. Verify the MCP connection works
2. Warm the Cloud instance (first generation is always slower)
3. Confirm the model files resolve on Cloud

If model names need adjusting for your Cloud setup, edit `data/demo_workflow_api.json`.
