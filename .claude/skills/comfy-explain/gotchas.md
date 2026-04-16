# comfy-explain gotchas

## The curated analogy set is intentionally small
The `ANALOGIES` dict in `src/onboard/explain.py` only covers the ~9 core nodes users ask about on day one. Do NOT expand it to cover every core node — the curation effort is in keeping the analogies short and memorable, and a dict with 200 entries becomes a reference manual, which is exactly what the skill is trying to avoid. If a user asks about a custom-pack node, fall back to the registry spec.

## Analogies MUST stay accurate as ComfyUI evolves
The "oven" metaphor for KSampler stops being accurate if someone replaces it with a one-step flow-matching solver. Re-audit the analogy set every time ComfyUI ships a major model (e.g. FLUX.2, SD4, Sora-style video). The analogies are marketing copy, but they have to also be TRUE.

## Error translation is lossy
ComfyUI error messages include Python tracebacks. Do NOT paste the traceback back at the user. Extract the node class name + the failure category (model-not-found, shape-mismatch, missing-pack, API-auth) and explain THAT.

## Don't guess when you don't know
If a custom-pack node has no registry entry and no curated analogy, tell the user so:
> "I don't have this node in my curated catalog and I can't fetch a live spec. Can you paste the node's GitHub README or the error it's throwing?"

Do NOT hallucinate what the node does just because its name sounds descriptive.

## Validator rule translations
Guideline rules in `data/guidelines.json` often reference internal rule IDs (e.g. `cloud_compat_sam_allowlist_v3`). Never expose the rule ID to a user — translate it to the underlying constraint in creator words.

## Template cross-reference is the secret weapon
The strongest answer to "how do I use X?" is almost always "here is a working template that uses X — copy it and change the prompt." `src.templates.search --query X` is cheap. Use it liberally.

## When the user is really asking "should I use X?"
"What is ControlNet?" sometimes means "should I use ControlNet for MY goal?" If you detect that intent, route to `/comfy-onboard` to learn the user's goal, THEN come back and explain ControlNet in context of that goal. Explanation without context is trivia.
