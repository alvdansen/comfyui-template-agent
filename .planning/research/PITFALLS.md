# Pitfalls Research

**Domain:** AI-assisted ComfyUI template creation tooling
**Researched:** 2026-03-18
**Confidence:** MEDIUM-HIGH (domain-specific research verified against official docs, ComfyGPT paper, and workflow_templates repo)

## Critical Pitfalls

### Pitfall 1: Two JSON Formats — Workflow vs API Format Confusion

**What goes wrong:**
ComfyUI has two distinct JSON representations: the **workflow format** (used by the UI, contains visual layout, `nodes[]`, `links[]`, `widgets_values`) and the **API format** (used for execution, contains `class_type`, `inputs` with connection arrays `["nodeId", outputIndex]`). The template repo uses **workflow format**. The MCP/execution layer uses **API format**. Mixing them up produces JSON that looks valid but fails silently — it loads in the UI but won't execute, or vice versa.

**Why it happens:**
Both are valid JSON with overlapping field names. LLMs trained on ComfyUI data see both formats interleaved. The API format omits titles, positions, and visual metadata, so generated API-format JSON dragged into ComfyUI produces "a skeleton of a real workflow" with missing data. Most tutorials and code examples use API format because that's what programmatic execution needs, but templates must be workflow format.

**How to avoid:**
- Hardcode the target format as **workflow format** (matching workflow_templates repo) in all generation prompts and validation
- Build a format detector that checks for `nodes[]` + `links[]` (workflow) vs flat node-ID keys with `class_type` (API) as the first validation step
- Never generate API format for templates — if execution testing is needed, convert workflow->API using `/workflow/convert` endpoint or the sync scripts in the repo

**Warning signs:**
- Generated JSON has `class_type` at the top level without `nodes[]` array
- Generated JSON lacks `pos`, `size`, `order`, `mode` fields on nodes
- Template loads in ComfyUI but shows no visual connections
- Template executes via API but can't be imported back into the editor

**Phase to address:**
Phase 1 (core workflow composition) — format must be locked down before any generation logic is built.

---

### Pitfall 2: Widget Values vs Input Connections — The Dual-Value Problem

**What goes wrong:**
ComfyUI nodes have two ways to receive data: **widget values** (static parameters like text, numbers, dropdown selections stored in `widgets_values[]`) and **input connections** (links from other nodes stored in `inputs[]`). The workflow JSON stores values in both places, and they can diverge. When a value is provided via a connection, the widget value is still present but ignored. AI-generated workflows frequently set widget values but forget to create the corresponding link, or create links that override important widget defaults.

**Why it happens:**
The `widgets_values` array is positional — mapping values to widget names requires loading node type definitions from `/object_info`. Without that mapping, it's impossible to know that `widgets_values[3]` is the "sampler_name" parameter. LLMs generate plausible-looking arrays without understanding which position maps to which parameter. The official spec even acknowledges this is "really hard and engineering intensive" to work with programmatically.

**How to avoid:**
- Fetch and cache `/object_info` node definitions to get the canonical widget-to-position mapping for every node type
- Build a node schema registry that maps each node's `INPUT_TYPES` to widget positions
- Validate that connected inputs don't have conflicting widget values
- When generating workflows, populate `widgets_values` from the node schema, not from LLM guessing

**Warning signs:**
- `widgets_values` array length doesn't match expected widget count for the node type
- Values appear in wrong positions (e.g., a sampler name where seed should be)
- Node works in isolation but produces wrong results when connected

**Phase to address:**
Phase 1-2 (node schema registry must exist before workflow composition begins).

---

### Pitfall 3: LLM Node Hallucination — Fabricating Non-Existent Nodes

**What goes wrong:**
LLMs generate workflows referencing node types that don't exist in ComfyUI. The ComfyGPT paper documents this as a primary failure mode — few-shot LLM approaches achieve only **12-15% pass accuracy** for workflow generation because models fabricate fictitious node names. With 3,500+ real node types and daily ecosystem changes, even well-trained models hallucinate plausible-sounding but non-existent nodes.

**Why it happens:**
Training data contains outdated node names, renamed nodes, and deprecated nodes. Node naming conventions are inconsistent across the ecosystem (e.g., `KSampler` vs `SamplerCustom` vs `KSamplerAdvanced`). LLMs pattern-match on naming conventions and generate nodes like `ImageUpscaleAdvanced` that sound right but don't exist.

**How to avoid:**
- Maintain a live registry of valid node types from `/object_info` or api.comfy.org
- Validate every `type` field in generated workflows against the registry BEFORE presenting to the user
- For template creation (core nodes only): maintain a whitelist of ~100 core node types, reject everything else
- When the agent suggests a node, include a confidence indicator: "core node (verified)" vs "custom node (registry match)" vs "UNKNOWN (not found)"

**Warning signs:**
- Node type names that are very long or use unusual casing
- Node types that combine concepts (e.g., `LoadCheckpointAndSample`) — ComfyUI uses single-responsibility nodes
- Any node type not found in the cached registry

**Phase to address:**
Phase 1 (node registry/validation must be the foundation everything builds on).

---

### Pitfall 4: Custom Node Dependency Creep in Templates

**What goes wrong:**
Templates that depend on custom (third-party) nodes break when those nodes aren't installed, are updated with breaking changes, or are abandoned by maintainers. The official template guidelines explicitly state: "do not use any third-party nodes" for core templates. Yet template creators naturally reach for custom nodes that solve problems more elegantly than composing core nodes.

**Why it happens:**
Custom nodes often provide convenience wrappers that combine multiple core node operations. An AI agent optimizing for "simplest workflow" will naturally prefer a single custom node over a 5-node core composition. The agent may not distinguish between core and custom nodes without explicit metadata.

**How to avoid:**
- Tag every node in the registry as `core` vs `custom` (source: api.comfy.org publisher field)
- Default to core-only mode for template generation; require explicit override for custom nodes
- When custom nodes are used, auto-populate `requiresCustomNodes` in the template metadata
- Show the user a dependency risk score: node age, update frequency, download count, GitHub stars
- For each custom node used, generate a "core-only alternative" suggestion if possible

**Warning signs:**
- Template uses more than 2-3 custom node packs
- Custom node has < 1000 downloads or hasn't been updated in 6+ months
- Node pack has open issues about ComfyUI version compatibility

**Phase to address:**
Phase 2 (validation layer) — after core composition works, add dependency analysis.

---

### Pitfall 5: Link Type Mismatches — Silent Connection Failures

**What goes wrong:**
ComfyUI connections are typed (IMAGE, LATENT, MODEL, CLIP, VAE, CONDITIONING, etc.). Connecting an output of type LATENT to an input expecting IMAGE compiles but fails at execution with "Return type mismatch between linked nodes." AI-generated workflows frequently create type-mismatched connections because the LLM doesn't track output types through the graph.

**Why it happens:**
The link format `[link_id, source_node_id, source_output_index, dest_node_id, dest_input_index, data_type]` requires knowing the exact output type at each slot index for every node. This is implicit knowledge derived from node definitions, not visible in the workflow JSON itself. LLMs guess connection types based on semantic similarity rather than the actual type system.

**How to avoid:**
- Build a type checker that resolves output types from node definitions and validates every link's `data_type` against source output type AND destination input type
- Generate connections by walking the type graph: "KSampler output[0] is LATENT" -> "VAEDecode input[0] expects LATENT" -> valid connection
- Reject any workflow where link types don't match both ends
- Provide type-aware autocomplete: when the agent needs to connect node A's output, filter valid destination nodes by type compatibility

**Warning signs:**
- Links with generic or missing type fields
- Connections between nodes that operate on different modalities (text nodes connected to image nodes without proper encoding)
- Workflow loads in UI but fails on queue with type mismatch errors

**Phase to address:**
Phase 1-2 (type validation is fundamental to workflow composition).

---

### Pitfall 6: Registry and Repo Data Drift

**What goes wrong:**
The api.comfy.org registry (8,400+ nodes, live metadata) and the workflow_templates GitHub repo (400+ templates, index.json) are separate data sources maintained by different processes. Node metadata in the registry may not match what's actually used in templates. A node could be listed in the registry but not yet supported in cloud environments. A template could reference a node version that's been superseded.

**Why it happens:**
The registry is updated by node publishers (continuous). The template repo is updated by PR review (batched). There's no automated sync between "nodes available in registry" and "nodes safe for templates." The agent needs both sources but may cache stale data from either.

**How to avoid:**
- Treat the registry as the source of truth for "what nodes exist" and the template repo as the source of truth for "what templates exist"
- Cache with explicit TTLs: registry data refreshed daily, template index refreshed on each session
- When cross-referencing, always check the template repo's `index.json` version against the latest commit
- Flag discrepancies: "Node X is in your workflow but not found in registry" or "Template Y references node version Z but registry shows version W"

**Warning signs:**
- Agent suggests nodes that exist in registry but fail in ComfyUI cloud
- Templates reference node packs not found in the registry
- `index.json` locally differs from GitHub HEAD

**Phase to address:**
Phase 2-3 (cross-referencing layer, after individual data sources are reliable).

---

### Pitfall 7: Template Validation Rules Trapped in Notion

**What goes wrong:**
The team's template creation guidelines live in a Notion doc — not machine-readable, not version-controlled, not testable. Rules like "prefer core nodes," "no set/get nodes," "subgraph conventions," "color/note standards" are prose descriptions that the agent must interpret. When guidelines update in Notion, the agent's validation logic silently becomes stale.

**Why it happens:**
Notion is the team's natural workspace for documentation. Converting prose rules to machine-readable validation logic requires upfront engineering. It's easy to assume "the agent will just read the guidelines" — but LLM interpretation of prose rules is unreliable and non-deterministic.

**How to avoid:**
- Extract Notion guidelines into a structured validation schema (JSON or YAML) that lives in the repo alongside the agent
- Each rule becomes a named validator with: rule ID, description, check logic, severity (error/warning/info)
- Version the validation schema so it can be updated independently
- Keep the Notion doc as the human-readable source, but generate/sync the machine-readable schema from it
- If full extraction is too costly for v1, at minimum hardcode the critical rules (no set/get, core nodes preferred) and flag everything else as "manual review needed"

**Warning signs:**
- Agent approves workflows that violate guidelines a human reviewer catches
- Different agent sessions apply rules inconsistently
- Guidelines in Notion update but agent behavior doesn't change

**Phase to address:**
Phase 2 (validation layer) — but the rule extraction should start in Phase 1 as a data task.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcode core node list instead of fetching from registry | Fast to implement, no API dependency | List goes stale as ComfyUI adds core nodes (happens every few releases) | MVP only — replace with registry-backed list by v1.1 |
| Generate workflow JSON via string templates instead of graph construction | Easier to prototype | Impossible to validate connections, can't compose programmatically, fragile to format changes | Never for production — always build a graph model |
| Skip `/object_info` integration and hardcode widget schemas | No need to run ComfyUI server | Widget positions change across versions, new nodes can't be used | MVP for the ~20 most common nodes only |
| Store template guidelines as LLM prompt context instead of structured rules | No engineering effort | Non-deterministic validation, can't unit-test rules, guidelines drift | Phase 1 only — must extract to structured schema by Phase 2 |
| Cache registry data indefinitely | Faster, no rate limiting concerns | Stale node data, missing new nodes, wrong version info | Acceptable with daily TTL and manual refresh option |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| api.comfy.org registry | Assuming all listed nodes work in ComfyUI Cloud | Check `cloud_compatible` or equivalent field; many nodes are local-only |
| workflow_templates repo | Treating `index.json` as the complete template list | Some templates exist as files but aren't in `index.json` yet (pending PR); always cross-check file system |
| ComfyUI `/object_info` endpoint | Calling it without a running ComfyUI instance | Cache the response; for the agent, bundle a snapshot of core node definitions as fallback |
| Notion template guidelines | Scraping Notion pages programmatically | Notion API requires auth and page IDs change; extract rules once, maintain in repo |
| comfy-tip node discovery | Assuming trending nodes are template-ready | Trending custom nodes are often too new/unstable for templates; filter by age + stability metrics |
| Template thumbnails | Generating or referencing thumbnails programmatically | Templates need human-captured screenshots; agent should remind user, not try to automate |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Fetching full registry on every node lookup | 5-10s delay per query, API rate limits | Cache registry locally, refresh daily, search cached data | At >50 lookups/session |
| Loading all 400+ template JSONs to check for duplicates | Memory spike, slow cross-reference | Build a lightweight template index (name, nodes used, tags) at startup | At >500 templates |
| Validating workflow by executing it on ComfyUI | Requires running server, model downloads, GPU time | Structural validation first (schema, types, connections); execution validation is a separate manual step | Always — execution validation is out of scope for agent |
| LLM generating entire workflow JSON in one shot | Token limits, error accumulation, low accuracy | Compose incrementally: skeleton -> nodes -> connections -> widgets -> metadata | At >15 nodes in a workflow |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Embedding API keys in generated workflow JSON | Keys leak when workflows are shared or committed | Never include auth tokens in workflow JSON; API nodes use ComfyUI's account-level auth, not per-workflow keys |
| Trusting registry node metadata without validation | Malicious node pack could have misleading metadata | Cross-reference registry metadata with actual node behavior; flag nodes with suspiciously broad permissions |
| Storing ComfyUI Cloud credentials in agent config | Credential exposure in repo or agent memory | Use environment variables or ComfyUI's built-in auth flow; agent should never handle credentials directly |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Generating complete workflow JSON and dumping it on the user | Overwhelming, impossible to review, user can't learn | Build incrementally: show the workflow graph step by step, explain why each node was chosen |
| Silently preferring core nodes without explaining why | User doesn't understand constraints, fights the tool | Explain: "Using KSampler (core) instead of CustomSampler because templates should minimize dependencies" |
| Auto-fixing validation errors without surfacing them | User doesn't learn guidelines, same errors repeat | Show the error, explain the rule, then offer the fix |
| Requiring ComfyUI knowledge to use the agent | Excludes new template creators | Provide contextual explanations: "This node encodes your text prompt into a format the model understands" |
| Generating metadata (index.json entry) before workflow is validated | Metadata references a broken workflow | Always: compose -> validate -> THEN generate metadata |

## "Looks Done But Isn't" Checklist

- [ ] **Workflow JSON:** Has `version: 1` field — verify it's present (required by schema, easy to forget)
- [ ] **Node positions:** All nodes have `pos` and `size` — verify they don't overlap (AI generates [0,0] for everything)
- [ ] **Link IDs:** All link IDs are unique and sequential — verify no duplicates (LLMs reuse IDs)
- [ ] **State tracking:** `lastNodeId`, `lastLinkId` match actual max IDs — verify consistency
- [ ] **Model metadata:** `properties.models` URLs are valid HuggingFace/CivitAI links — verify they resolve
- [ ] **Model filenames:** Filenames in model metadata match `widgets_values` exactly — verify string equality
- [ ] **Template metadata:** `index.json` entry has all required fields (name, description, mediaType, thumbnailVariant) — verify against schema
- [ ] **File naming:** Workflow filename has no spaces, dots, or special characters — verify regex `^[a-z0-9_-]+\.json$`
- [ ] **Thumbnail reference:** Thumbnail files exist with correct naming convention (`name-1.webp`) — verify files exist (agent can't generate these, but should check)
- [ ] **Bundle sync:** After adding template, `sync_bundles.py` has been run — remind user

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wrong JSON format (API vs workflow) | MEDIUM | Convert using `/workflow/convert` endpoint or manual restructuring; if too broken, regenerate from scratch |
| Widget values in wrong positions | HIGH | Must re-derive all widget mappings from `/object_info`; essentially regenerate the node's widget section |
| Hallucinated nodes | LOW | Replace with real nodes from registry; agent should suggest alternatives automatically |
| Type-mismatched connections | MEDIUM | Identify broken links via type checker, remove them, suggest valid reconnections |
| Custom node dependency | LOW-MEDIUM | Replace custom nodes with core equivalents; may require restructuring workflow if no core equivalent exists |
| Stale registry data | LOW | Force refresh cache; re-validate workflow against fresh data |
| Validation rules drift | MEDIUM | Re-extract rules from Notion; re-validate all recently created templates |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Format confusion (workflow vs API) | Phase 1: Core Foundation | Format detector passes on 10+ real templates from repo |
| Widget value mapping | Phase 1-2: Node Schema + Composition | Widget arrays match `/object_info` definitions for all core nodes |
| Node hallucination | Phase 1: Node Registry | 100% of generated node types found in registry/whitelist |
| Custom node creep | Phase 2: Validation | Templates flagged with custom node count; core-only mode enforced by default |
| Link type mismatches | Phase 1-2: Type System | All links in generated workflows pass bidirectional type check |
| Registry/repo drift | Phase 2-3: Cross-referencing | Cache timestamps visible; stale data warnings surfaced |
| Notion rules extraction | Phase 1 (data task) + Phase 2 (validation) | Structured rule set covers all Notion guidelines; validation results match human review |

## Sources

- [ComfyUI Workflow JSON Spec](https://docs.comfy.org/specs/workflow_json) — Official schema documentation (HIGH confidence)
- [Workflow format vs API format confusion - Issue #1335](https://github.com/comfyanonymous/ComfyUI/issues/1335) — Community discussion on format differences (HIGH confidence)
- [ComfyGPT: Self-Optimizing Multi-Agent System for ComfyUI Workflow Generation](https://arxiv.org/html/2503.17671v1) — Academic paper on LLM workflow generation failures, 12-15% baseline accuracy (HIGH confidence)
- [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates) — Official template repo structure and contribution guidelines (HIGH confidence)
- [JSON format developer complaints - Discussion #4787](https://github.com/comfyanonymous/ComfyUI/discussions/4787) — Widget values pain points (MEDIUM confidence)
- [ComfyUI Templates Documentation](https://docs.comfy.org/interface/features/template) — Official template guidelines (HIGH confidence)
- [Custom Node Troubleshooting](https://docs.comfy.org/troubleshooting/custom-node-issues) — Breaking changes, version mismatches (HIGH confidence)
- [ComfyUI Registry Overview](https://docs.comfy.org/registry/overview) — Registry API documentation (HIGH confidence)
- [API Key Integration](https://docs.comfy.org/development/comfyui-server/api-key-integration) — Auth requirements for API nodes (HIGH confidence)
- [Custom nodes breaking after updates](https://www.apatero.com/blog/custom-nodes-breaking-comfyui-updates-fix-guide-2025) — Compatibility issues (MEDIUM confidence)

---
*Pitfalls research for: AI-assisted ComfyUI template creation tooling*
*Researched: 2026-03-18*
