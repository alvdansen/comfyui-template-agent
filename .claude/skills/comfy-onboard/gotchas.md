# comfy-onboard gotchas

Non-obvious failure modes and edge cases. Read this before editing the skill.

## Intent matching is a tie-breaker, not an oracle
The `src.onboard.catalog` scorer is a simple phrase + token overlap. It will happily return an exact-phrase hit for "I want to make an image from text" but gets mushy on ambiguous goals like "I want to make art with AI." When the top two matches are within 2 points of each other, show BOTH to the user and ask — do not pick silently.

## Users who say "I want to try ComfyUI" have no goal yet
The goal phrase catalog only works if the user has a concrete intent. When they say "I just want to try it," the correct move is NOT to match — it's to ask a clarifying question ("do you want to make an image, fix an image, caption an image, or work with audio?") and THEN match against their answer.

## "Cloud vs local" is not optional in v2
The scaffolded starters all assume `comfy-compose` can reach something runnable. If the user says "neither" to local/cloud, stop the flow and point them at cloud signup. Do not scaffold a workflow they cannot run — that's worse than no scaffold.

## The face-fix starter needs an input image
`impact-pack-face-detailer` fails on cloud if `LoadImage` references a local file path that isn't uploaded. Before scaffolding this one, ask the user to upload their image first (or tell them how to upload via the MCP server's `upload_file` tool).

## The audio-separation starter is VRAM-hungry
MelBandRoFormer needs ~6-8 GB VRAM for a 3-minute track. On cloud this is fine. On local with a 4 GB card, it will OOM. If the user says "local" and "audio separation," warn them about VRAM requirements before scaffolding.

## Next-hop suggestions must match the actual starter
Each starter's `next_hops` list is hand-curated for that specific template. Do not mix-and-match across starters — "swap to FLUX.1-dev" makes sense for `gguf-quantized-txt2img` and nobody else.

## The skill is NOT a ComfyUI tutorial
This skill's contract is: one working output, fast. It is explicitly NOT trying to teach the user what a checkpoint is, why negative prompts help, or the history of diffusion models. If the user asks those questions, point them at `/comfy-explain` or offer `/comfy-flow` for deeper template authoring. Keep onboarding conversations under ~15 messages.

## Cloud submission polling
`comfy-compose` already handles this, but worth repeating here: after submitting the scaffolded workflow, poll `get_job_status` every 10-15 seconds. Do NOT give up before 3 minutes on a first-run user — a slow first image is vastly better than a silent failure.

## What we'd add in v3
- Bring-your-own-goal intent learner (log unmatched goals, curate weekly)
- Image preview in-chat (depends on harness capability)
- Telemetry opt-in to measure onboarding completion rate
- A starter for ControlNet pose-to-image (requested repeatedly in the #proj-comfy-agent channel)
