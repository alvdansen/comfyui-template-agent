# Domain Pitfalls

**Domain:** Publishing internal Claude Code agent toolkit + async presentation materials
**Researched:** 2026-04-08
**Milestone:** v3.0 — Publish & Present

---

## Critical Pitfalls

Mistakes that cause embarrassment, security incidents, or major rework.

### Pitfall 1: Git History Leaks Personal and Internal Data

**What goes wrong:** The repo goes public with 111 commits containing personal identifiers, internal paths, and planning artifacts baked into the permanent history. Even if files are removed from HEAD, they remain in git objects forever. Anyone can `git log --all -p` and find:
- Personal email addresses: `macapple@Mac.attlocal.net`, `macapple@Timotheoss-MacBook-Pro.local`, `peppamintdynamo@gmail.com`
- Local machine hostnames embedded in git author metadata
- Internal planning artifacts with developer names and workflow decisions
- Windows paths from comfy-tip heritage: `C:/Users/minta/Projects/comfy-tip/` (in 13+ planning files)
- The original remote `aramintak/comfyui-template-agent` which differs from the target `Alvdansen Labs` org

**Why it happens:** The repo was developed as a personal internal tool over two milestones with no expectation of public visibility. Git author metadata auto-populates from local machine config. Planning files reference source material by absolute path.

**Consequences:** Personal information exposed publicly. The comfy-tip path references reveal the original developer's Windows username (`minta`). Professional credibility impact if the published repo looks like it wasn't cleaned for public consumption.

**Prevention:**
1. Run `gitleaks detect --source . --verbose` on the full repo to find any secrets or sensitive patterns
2. Decide: fresh commit history (squash all to single commit or cherry-pick key commits) vs. rewrite with `git filter-repo` to clean author metadata
3. Fresh history is STRONGLY recommended for this repo — 111 commits of internal development process do not add value for external consumers, and rewriting is error-prone
4. If preserving history: use `git filter-repo --mailmap` to normalize all author/committer emails to the public-facing identity
5. Verify with `git log --format='%an <%ae>' | sort -u` after cleanup

**Detection:** Run `git shortlog -sne --all` — if you see multiple identities or local hostnames, cleanup is needed.

### Pitfall 2: Publishing .planning/ Directory as-is

**What goes wrong:** The `.planning/` directory (784 KB across phases, milestones, research, roadmaps, retrospectives) ships with the public repo. This contains:
- GSD workflow internals (state machine, velocity metrics, session timing)
- Phase execution plans with implementation details, line-by-line code plans
- Developer-facing retrospectives ("what was inefficient")
- Internal requirement tracking and validation checklists
- Research files referencing comfy-tip source code paths

**Why it happens:** The `.planning/` directory is integral to the GSD workflow and is checked into git. There is no `.gitignore` entry for it. The natural assumption is "it's just planning docs" but it exposes process internals that are confusing or unprofessional for external consumers.

**Consequences:** External users see internal process artifacts alongside the actual product. It clutters the repo with files irrelevant to using or contributing to the tool. The retrospective contains velocity metrics that are meaningless without context.

**Prevention:**
- Option A (recommended): Add `.planning/` to `.gitignore` before publishing, remove from tracking with `git rm -r --cached .planning/`
- Option B: Move select useful docs (architecture decisions, design rationale) to a `docs/` directory in cleaned form, exclude the rest
- Option C: If using fresh history (see Pitfall 1), simply don't include `.planning/` in the initial commit

**Detection:** Check if `.planning/` exists in the published tree. Ask: "Would an external user benefit from any of these files?"

### Pitfall 3: No LICENSE File

**What goes wrong:** The repo ships publicly without a LICENSE file. Currently there is NO license file in the repository. Without an explicit license, the code is technically "all rights reserved" by default under copyright law — meaning nobody can legally use, modify, or distribute it, even though it is publicly visible.

**Why it happens:** Internal tools don't need licenses. The decision gets deferred during development.

**Consequences:** Contributors and users have no legal basis to use the code. Comfy-Org cannot absorb the code into their org without a clear license. Other developers rightfully won't touch it. GitHub's licensing detection will show "No license" which signals an amateur or abandoned project.

**Prevention:**
1. Choose a license BEFORE the first public commit
2. Recommendation: **Apache 2.0** — provides patent protection, is standard for Python tools in this ecosystem, and aligns with ComfyUI's GPL-3.0 (Apache 2.0 is compatible as a permissive license being consumed by a copyleft project)
3. Alternative: MIT if simplicity is preferred, but Apache 2.0's patent clause is safer when the code may be absorbed into a larger org
4. Add LICENSE file to repo root and `license` field to `pyproject.toml`

**Detection:** `ls LICENSE*` returns nothing. `pyproject.toml` has no license field.

### Pitfall 4: Skill Symlink Installation Breaks on Fresh Machines

**What goes wrong:** The `setup.sh` creates symlinks from `~/.claude/skills/comfy-*` pointing to the repo's `.claude/skills/` directory. This coupling means:
- Skills break if the repo directory is moved, renamed, or deleted
- Symlinks are absolute paths tied to the machine's filesystem layout
- Windows symlinks require Developer Mode or Admin privileges (noted in setup.ps1 but easy to miss)
- Claude Code's skill resolution may not follow symlinks in all environments
- If a user already has skills with conflicting names (especially `comfy-discover` from the global `comfy-tip`), the setup script logs a warning but doesn't resolve the conflict

**Why it happens:** Symlinks were the quickest distribution method for an internal tool used by one developer.

**Consequences:** Setup fails silently or creates broken skill references on other machines. Windows users hit permission errors. The README mentions the comfy-tip conflict but the setup script only SKIPs — it doesn't offer to replace.

**Prevention:**
1. Document the symlink approach honestly in README, including the "repo must stay in place" constraint
2. Add an `--uninstall` flag to setup scripts that cleanly removes symlinks
3. Consider alternative: copy skills instead of symlinking (loses live-editing but gains portability)
4. For public release, the recommended pattern per Claude Code docs is to commit skills to the project `.claude/skills/` and let users clone the repo — Claude Code auto-discovers project skills without symlinking
5. Test setup.sh on a fresh macOS and Linux machine (not just the development machine)

**Detection:** Run `ls -la ~/.claude/skills/comfy-*` on a fresh machine after setup — dangling symlinks indicate the problem.

---

## Moderate Pitfalls

### Pitfall 5: comfy-tip Heritage Creates Naming Confusion

**What goes wrong:** The codebase was built on top of `comfy-tip` (a separate repo/tool). References to comfy-tip appear in:
- CLAUDE.md project constraints ("matches existing comfy-tip and MCP tooling")
- README.md tip about naming conflicts
- 24 files in `.planning/` referencing comfy-tip architecture, scoring heuristics, Windows paths
- Key Decisions table mentioning "Build on comfy-tip + MCP rather than from scratch"
- Phase 1 research docs containing comfy-tip source code snippets and file paths

External users who encounter "comfy-tip" references will be confused — they cannot access that repo and the references add no value.

**Prevention:**
1. Audit all files in the publishable tree for `comfy-tip` references
2. Remove or replace with context-free descriptions ("adapted from existing registry client code")
3. If `.planning/` is excluded (see Pitfall 2), this eliminates most references automatically
4. CLAUDE.md and README.md need manual cleanup — 5 references total in the shipping files

**Detection:** `grep -r "comfy-tip" . --include="*.md" --include="*.py"` in the published tree.

### Pitfall 6: pyproject.toml Missing Public Release Metadata

**What goes wrong:** The `pyproject.toml` is minimal — suitable for internal use but missing fields expected for a public project:
- No `license` field
- No `authors` field (or it will auto-populate from git which has the personal emails)
- No `readme` field
- No `urls` (homepage, repository, issues)
- No `classifiers` for PyPI discoverability
- No Python version `requires-python` upper bound (currently `>=3.12` which is fine)
- Version is `0.1.0` — appropriate for pre-release but should be intentional

**Prevention:**
1. Add `license = {text = "Apache-2.0"}` (or chosen license)
2. Add `authors = [{name = "Alvdansen Labs"}]` (org, not personal)
3. Add `readme = "README.md"`
4. Add `[project.urls]` section with repository link
5. Consider whether to bump version to `1.0.0` or keep `0.x` to signal pre-release

**Detection:** Read `pyproject.toml` and check for missing standard fields per Python Packaging User Guide.

### Pitfall 7: Manim Animations Fail in Headless/Remote Rendering

**What goes wrong:** Manim Community Edition has specific rendering pitfalls when running on remote servers (Hermes) or in CI:
- **No display server:** Manim's preview mode (`-p` flag) tries to open a window, which fails headlessly. Must use `--disable_caching -qh` without `-p`
- **LaTeX dependency:** Many Manim text features require a LaTeX installation (texlive). Remote servers may not have it installed. Missing LaTeX causes cryptic `subprocess.CalledProcessError` failures
- **ffmpeg version mismatch:** Manim v0.19+ replaced external ffmpeg with `pyav`, but older Manim or mixed environments still need ffmpeg. Version mismatches cause encoding failures
- **Font rendering differences:** Fonts available on macOS (SF Pro, Helvetica Neue) may not exist on Linux servers, causing text layout differences between local preview and remote render
- **Caching stale scenes:** Manim aggressively caches rendered scenes. When iterating, old cached output plays instead of re-rendered content. Use `--disable_caching` or `manim render --flush_cache`
- **OpenGL renderer issues:** Some Manim objects lack `should_render` attribute, causing `AttributeError` with the OpenGL renderer

**Prevention:**
1. Always render with `--disable_caching -qh --format mp4` for final output
2. Use `-pql` (low quality preview) for iteration, high quality only for final render
3. Pin Manim version in requirements: `manim==0.20.1` (current stable as of early 2026)
4. Include a `render.sh` script that sets all flags correctly for headless rendering
5. Test the exact render pipeline on the target server (Hermes) before creating all animations
6. Stick to built-in fonts (e.g., Manim's default or explicitly bundled fonts) to avoid cross-platform differences
7. Keep each scene under 60 seconds — longer scenes increase render time exponentially and make iteration painful

**Detection:** First render on Hermes fails. Check for LaTeX errors, missing font warnings, or stale cache output.

### Pitfall 8: Presentation Materials Bloat the Code Repository

**What goes wrong:** Manim source files (.py), rendered videos (.mp4), PowerPoint files (.pptx), Excalidraw files (.excalidraw), and thumbnail images are committed alongside the code. This:
- Bloats the repo size (a single 1080p 2-minute animation is 50-200 MB)
- Makes `git clone` slow for users who just want the code
- Binary files in git don't diff well — every edit creates a full copy in history
- Comfy-Org may want the code but not the presentation materials

**Prevention:**
1. Store presentation materials in a SEPARATE repo or directory that is git-ignored
2. Option A (recommended): Create `alvdansen-labs/comfyui-template-agent-presentation` as a separate repo
3. Option B: Use Git LFS for binary assets (videos, images, pptx) if they must live in the same repo
4. Option C: Host rendered videos on YouTube/Vimeo and link from README — no binary in git
5. Keep Manim SOURCE files (.py) in the code repo (they're small text files) but .gitignore the `media/` output directory
6. Excalidraw `.excalidraw` files are JSON and small — these can live in the repo
7. Add to `.gitignore`: `media/`, `*.mp4`, `*.mov`, `*.pptx`, `*.key`

**Detection:** `git ls-files | grep -E '\.(mp4|mov|pptx|png|jpg)$'` — any matches indicate binary bloat risk.

### Pitfall 9: README Not Rewritten for External Audience

**What goes wrong:** The current README is written for internal use and assumes context:
- `git clone <repo-url>` has a placeholder URL
- References comfy-tip naming conflict (external users don't have comfy-tip)
- "Cloud vs Local" section assumes knowledge of Comfy Cloud MCP
- No badges (license, Python version, tests passing)
- No screenshots or GIF demos showing what the tool actually does
- No "Why this exists" section for newcomers
- Architecture section is a bare bullet list
- "Contributing" section is a single paragraph

**Prevention:**
1. Rewrite README for someone who has never heard of this project
2. Add: project logo/banner, badges, "What is this?", "Why?", screenshots/GIF demo, clear prerequisites
3. Remove: comfy-tip references, internal team assumptions
4. Add example output (what does a completed template look like?)
5. Consider a "Quick Start" that gets someone from clone to first template in under 5 minutes

**Detection:** Have someone unfamiliar with the project read the README and note every point of confusion.

### Pitfall 10: Git Remote Points to Wrong Org

**What goes wrong:** The current remote is `https://github.com/aramintak/comfyui-template-agent.git`. Publishing requires moving to the Alvdansen Labs org. If the transfer or fork isn't handled correctly:
- Old links break (GitHub redirects help but aren't permanent)
- CI/CD pipelines reference the old URL
- Contributors push to the wrong remote
- The `aramintak` personal account namespace leaks the individual developer identity when the goal is an org-level publication

**Prevention:**
1. Create fresh repo under `alvdansen-labs` org (preferred over transfer if using fresh history)
2. If transferring: GitHub handles redirects from old URL, but update all references in README, CLAUDE.md, pyproject.toml
3. Update the origin remote: `git remote set-url origin https://github.com/alvdansen-labs/comfyui-template-agent.git`
4. Verify no hardcoded references to `aramintak` or `timm156` in any published files

**Detection:** `git remote -v` should show the Alvdansen Labs org URL after publishing.

---

## Minor Pitfalls

### Pitfall 11: .venv Directory Not in .gitignore Properly

**What goes wrong:** The `.venv/` directory appears as untracked in git status. While `.gitignore` does not list `.venv/`, the directory hasn't been committed. However, the risk is that someone accidentally commits it, adding hundreds of MB of Python packages to the repo.

**Prevention:** Add `.venv/` to `.gitignore` immediately. Also add `*.egg-info/` (already present) and `comfyui_template_agent.egg-info/` (currently a top-level directory that appears untracked).

**Detection:** `git status` shows `.venv/` as untracked.

### Pitfall 12: COMPAT-FIX.md and Build Scripts Are Internal Artifacts

**What goes wrong:** `COMPAT-FIX.md` is an untracked file that appears to be a debugging/fix note. The `templates/*/build.py` files are template generation scripts that may reference internal paths or assumptions. These internal artifacts ship without context.

**Prevention:**
1. Review `COMPAT-FIX.md` — if it's a debugging note, delete it before publishing
2. Review each `build.py` — ensure they work standalone without internal dependencies
3. Consider whether templates should ship with the agent toolkit or be a separate deliverable

**Detection:** `git status` shows these as untracked new files.

### Pitfall 13: Manim Animation Pacing Mismatched to Audience

**What goes wrong:** Technical demo animations built by developers tend to move too fast. The developer knows the content and paces it for themselves, not for a first-time viewer. Common mistakes:
- Transitions happen in 0.3s when viewers need 1-2s to process
- Text appears and disappears before it can be read
- No pauses between conceptual sections
- Code examples scroll past without highlighting the important parts
- No visual hierarchy — everything animates with equal emphasis

**Prevention:**
1. Follow the 3-second rule: every new piece of information stays visible for at least 3 seconds
2. Use `self.wait(2)` between major sections in Manim
3. Use progressive reveal (FadeIn/Write one element at a time, not all at once)
4. Get someone unfamiliar with the project to watch at 1x speed and note confusion points
5. Target 3-5 minutes per video segment — shorter is better for async viewing
6. Build a scene outline BEFORE coding — one claim per scene, 3-6 scenes max per video

**Detection:** Watch the rendered animation at 1x speed without skipping. If you're impatient, the pacing is correct for external viewers.

### Pitfall 14: Comfy-Org Absorption Expectations Misaligned

**What goes wrong:** The deliverable is prepared for Comfy-Org to "stress-test and absorb" but the handoff expectations are undefined:
- Does "absorb" mean they fork it, or adopt it into their org?
- Do they want the Python source, just the skills, or the full toolkit?
- Will they run it against their own workflow_templates CI?
- Is there an expected interface contract (API stability, CLI signatures)?
- Are there code style or testing requirements from Comfy-Org?

**Prevention:**
1. Clarify with Comfy-Org contacts BEFORE polishing: what exactly do they want to receive?
2. Prepare the repo to be self-contained — it should work without any of your local setup
3. Include a `CONTRIBUTING.md` that documents how to extend the toolkit
4. Add a `ARCHITECTURE.md` or `docs/design.md` explaining the module structure and extension points
5. Make the test suite comprehensive enough that Comfy-Org can run `pytest` and verify nothing is broken
6. Tag a release (e.g., `v3.0.0`) so there's a clear "this is what we delivered" checkpoint

**Detection:** Ask: "If I handed this repo URL to a Comfy-Org engineer with zero context, could they clone it, run setup, and use all 6 skills within 30 minutes?"

### Pitfall 15: CLAUDE.md Contains Internal GSD Workflow Instructions

**What goes wrong:** The project's `CLAUDE.md` contains GSD Workflow Enforcement rules ("Before using Edit, Write, or other file-changing tools, start work through a GSD command..."). This is an internal development workflow that:
- Confuses external contributors who don't have GSD installed
- References `/gsd:quick`, `/gsd:debug`, `/gsd:execute-phase` which are not part of this toolkit
- The "Developer Profile" section says "not yet configured"
- Template-specific node documentation (Florence2, GGUF, Impact Pack, MelBandRoFormer) is embedded in CLAUDE.md — useful during development but overwhelming for external users

**Prevention:**
1. Strip GSD workflow enforcement section from public CLAUDE.md
2. Strip or relocate the "Developer Profile" placeholder
3. Move template-specific node documentation to `docs/templates/` or the template directories themselves
4. Keep CLAUDE.md focused on: what the project is, conventions for contributing, how skills work
5. Consider a separate `CLAUDE.md.internal` for GSD workflow rules (added to `.gitignore`)

**Detection:** Read CLAUDE.md as an external contributor — any mention of GSD, `/gsd:*`, or developer profiles is internal-only.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Git history cleanup | Rewriting history breaks existing forks/clones | Use fresh repo approach — no external consumers yet, so no breakage |
| Secret scanning | False sense of security from scanning HEAD only | Scan full history with `gitleaks detect --source . --verbose` |
| License selection | Choosing incompatible license for Comfy-Org absorption | Verify Comfy-Org's preferred license; Apache 2.0 is safe default |
| .planning cleanup | Accidentally deleting files still needed for v3.0 execution | Complete v3.0 BEFORE cleaning; archive .planning/ locally |
| Skill installation docs | Assuming Claude Code skill format is stable | Pin to current skill spec; note that `commands/` and `skills/` merged |
| Manim rendering | Local renders look good but remote (Hermes) renders fail | Run ONE test render on Hermes before building all animations |
| Manim asset sizing | Rendered videos exceed GitHub's 100 MB file limit | Use separate repo or Git LFS for video assets |
| PowerPoint creation | Slides contain too much text, not enough visuals | Follow 6-word-per-slide rule; let Manim videos carry the detail |
| Excalidraw diagrams | Architecture diagrams don't match actual code structure | Generate diagrams FROM the code (module imports, skill graph) not from memory |
| README rewrite | Over-engineering the README with badges and shields | Focus on "clone, setup, use" flow; badges are polish, not substance |
| Org transfer | GitHub repo transfer vs. fresh push confusion | Fresh push to new org is cleaner if history is being reset anyway |
| Comfy-Org handoff | Delivering without a clear "what to evaluate" guide | Include a HANDOFF.md or EVALUATION.md with specific test scenarios |

---

## Pitfall Dependency Chain

Some pitfalls must be resolved in order:

```
Pitfall 3 (License) --> Must be decided BEFORE any public commit
Pitfall 1 (Git History) --> Must be resolved BEFORE Pitfall 10 (Remote/Org)
Pitfall 2 (.planning/) --> Should be resolved DURING Pitfall 1 (part of history cleanup)
Pitfall 5 (comfy-tip refs) --> Should be resolved DURING Pitfall 9 (README rewrite)
Pitfall 15 (CLAUDE.md) --> Should be resolved DURING Pitfall 9 (README rewrite)
Pitfall 7 (Manim remote) --> Must be tested BEFORE building all animations (Pitfall 8)
Pitfall 8 (Presentation repo) --> Repo structure decided BEFORE creating any videos
```

Suggested resolution order:
1. License decision (Pitfall 3)
2. Manim test render on Hermes (Pitfall 7)
3. Presentation repo structure decision (Pitfall 8)
4. Content cleanup: CLAUDE.md, README, comfy-tip refs (Pitfalls 5, 9, 15)
5. .planning/ and internal artifact cleanup (Pitfalls 2, 6, 11, 12)
6. Git history decision and execution (Pitfall 1)
7. Org creation and push (Pitfall 10)
8. Comfy-Org handoff preparation (Pitfall 14)

---

## Sources

### Git History & Secrets
- [GitHub Secret Scanning Basics](https://github.com/orgs/community/discussions/149172) — GitHub's built-in scanning capabilities (HIGH confidence)
- [Remove Secrets from Git History (Microsoft)](https://techcommunity.microsoft.com/blog/azureinfrastructureblog/how-to-safely-remove-secrets-from-your-git-history-the-right-way/4464722) — git filter-repo methodology (HIGH confidence)
- [Gitleaks GitHub](https://github.com/gitleaks/gitleaks) — Pre-commit secret scanning tool (HIGH confidence)
- [git-filter-repo](https://github.com/newren/git-filter-repo) — Official replacement for git-filter-branch (HIGH confidence)

### Licensing
- [Apache vs MIT License (SOOS)](https://soos.io/apache-vs-mit-license) — Comparison and patent implications (MEDIUM confidence)
- [Choose a License](https://choosealicense.com/licenses/) — License selection guide (HIGH confidence)
- [Python Packaging Licensing Examples](https://packaging.python.org/en/latest/guides/licensing-examples-and-user-scenarios/) — pyproject.toml license field (HIGH confidence)

### Claude Code Skills
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills) — Official skill format, installation, distribution (HIGH confidence)
- [Agent Skills Standard](https://agentskills.io) — Cross-platform skill specification (HIGH confidence)
- [Claude Skills Guide 2026](https://anandbg.com/blog/claude-skills-comprehensive-guide-2026) — Practical distribution patterns (MEDIUM confidence)

### Manim
- [Manim Community Docs](https://docs.manim.community/en/stable/) — Official documentation (HIGH confidence)
- [Manim Skill for Hermes Agent](https://github.com/NousResearch/hermes-agent/tree/main/skills/creative/manim-video) — Hermes rendering pipeline (MEDIUM confidence)
- [Manim Rendering Issues #4365](https://github.com/ManimCommunity/manim/issues/4365) — Known rendering failures (HIGH confidence)
- [Manim Best Practices (adithya-s-k)](https://github.com/adithya-s-k/manim_skill/blob/main/skills/manimce-best-practices/rules/timing.md) — Animation timing rules (MEDIUM confidence)

### GitHub Repository Transfer
- [GitHub: Transferring a Repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository) — Official transfer docs (HIGH confidence)

### Python Packaging
- [Editable Installs (setuptools)](https://setuptools.pypa.io/en/latest/userguide/development_mode.html) — Current editable install behavior (HIGH confidence)
- [pip install documentation](https://pip.pypa.io/en/stable/cli/pip_install/) — Cross-platform installation (HIGH confidence)
