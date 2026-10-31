# Claude Code implementation prompt — AI Animation Generator

Use this prompt together with `create-animation-implementation-blueprint.md`.

---

You are the principal software architect and implementation engineer for my existing AI publishing framework. Implement the reusable AI Animation Generator described in `create-animation-implementation-blueprint.md`.

## Hard constraints

1. **Do not use WebSearch, web browsing, external research, or network calls.** The blueprint contains the platform snapshot, technical requirements and reference URLs needed for this implementation. Use the local specifications in the blueprint and local repository files only.
2. First inspect the existing repository, `.claude/` framework, publishing pipeline, package/runtime conventions, product manifests, and existing Draw Things scripts. Preserve the existing architecture and naming conventions where they make sense. Do not create a parallel framework unnecessarily.
3. Do not overwrite, rename, delete or reformat unrelated files. Do not replace existing working publishing workflows.
4. Do not assume `draw-things-cli` supports video generation. Inspect the installed command help and version locally. Implement only capabilities that are explicitly exposed and tested. The standard Pillow/FFmpeg pipeline must work even if AI video generation is unavailable.
5. Keep all original book covers, artwork, source pages, PDFs, logos, fonts and audio immutable. Write generated assets only into dedicated job output directories.
6. Do not fabricate product metadata, claims, page counts, supported model options, brand details, music licences or customer testimonials.
7. Prefer deterministic, typed, testable Python code. Do not embed renderer logic in SKILL.md instructions.
8. Use Claude Code `AskUserQuestion` when a user-facing workflow has missing material inputs, and include a **Recommended** option wherever a recommendation is appropriate. Never ask users to repeat information already present in prompt arguments, product manifests or brand profiles.

## How to work

### Step 1 — Repository discovery (do not edit yet)

Inspect the repository and produce a concise discovery report covering:

- Existing `.claude/skills`, `.claude/agents`, `.claude/rules`, `CLAUDE.md` and settings/hooks.
- Existing book/product manifest schema and publishing pipeline lifecycle hooks.
- Existing Python packaging/runtime and dependency management.
- Existing Draw Things invocation patterns, installed model paths and any current video workflow.
- Existing FFmpeg/FFprobe availability and encoder/filter support, if locally executable.
- Output directory, logging, test and CLI conventions.
- Architectural conflicts or reusable components discovered.

If a blocking ambiguity cannot be resolved from the repository, ask one focused `AskUserQuestion` with a Recommended option. Otherwise proceed with sensible defaults.

### Step 2 — Produce an implementation plan

Map the blueprint onto the actual repository. Show the proposed files to add/change, dependencies, public Python APIs, schema decisions, integration hook, tests and phase boundaries. Keep the existing framework intact. Do not implement all functionality in one large change.

### Step 3 — Implement the foundation first

Implement only the minimum production foundation:

- Normalized `AnimationJob`, asset manifest, platform profile and storyboard schemas.
- Config loading and validation.
- Job directory/state store with resumable stage records and input hashes.
- Asset discovery/validation from explicit product manifests.
- Pillow scene composition helpers (canvas, image fit/contain, text layout, safe-zone overlay, shadows and masks).
- FFmpeg command builder using safe subprocess argument arrays (never shell-string interpolation of user text).
- FFprobe metadata reader and platform output validator.
- CLI `doctor`, `create`, `preview`, `render` and `validate-output` commands or the equivalent existing-project convention.
- One complete `etsy_page_gallery` standard-rendering template.
- Unit and integration tests for the above.

Use H.264/libx264, `yuv420p`, square pixels, fixed frame rate and `+faststart` as the default MP4 path. Etsy output must be silent and comply with the embedded Etsy profile. GIF must remain a secondary output, not part of the first milestone.

### Step 4 — Add the Claude Code interface

Add `/create-animation` under the correctly discovered project-level skill path. Keep its SKILL.md concise: prompt parsing, intake, agent delegation, profile/template selection, approval gate, calls to the Python CLI and delivery summary. Put longer references under the skill's `references/` directory.

Add only the useful subagents and scoped rules from the blueprint. Do not create an excessive number of tiny skills/agents. Keep `CLAUDE.md` short and add only a cross-reference to `/create-animation` and the relevant rules.

The skill must support these three entry paths:

1. Post-book-creation publishing hook with an existing product manifest.
2. Independent `/create-animation` with natural language or flags.
3. Generic branded campaign / public-service ad.

Parse provided arguments first, then ask only for missing information. A campaign involving health/safety/legal/financial claims must require approved copy/source and human review.

### Step 5 — Add templates and platform exports incrementally

Use the blueprint's embedded profiles and candidate template catalog. Start with Etsy, then add Instagram Reels/Feed and Facebook Feed/Reels. Maintain separate platform compositions; do not simply crop one Reel to every destination. Create six candidate templates per channel group and use the screening process to select four provisional production templates per group.

### Step 6 — Add AI video only after standard rendering is stable

Add a provider interface and optional Draw Things video adapter only after verifying a supported local invocation/API. If not supported by the installed CLI, make the adapter return `unsupported` and document the manual/app-based option; do not invent commands or block the rest of the pipeline.

### Step 7 — Verification and report

Run the full relevant test suite and produce:

- Architecture summary.
- Actual changed/added file tree.
- Dependency changes.
- CLI usage examples.
- Test results.
- One demonstration output from fixture assets, if the repository has suitable assets; otherwise create small synthetic test fixtures and clearly label them as test-only.
- FFprobe report for the demo MP4.
- Known limitations and deferred phases.

Do not mark a phase complete unless its acceptance criteria pass. Stop after a coherent milestone and summarize exactly what is implemented versus planned.

## Required design rules

- Templates are declarative configuration and compile into a standardized storyboard.
- Platform profiles govern output constraints; do not scatter platform checks through templates.
- Pillow creates still compositions, cards, text, masks and custom frame assets. Use FFmpeg filters for temporal motion wherever practical. Avoid dumping hundreds of PNG frames unless a custom per-frame effect requires it.
- Render all derivatives from immutable high-quality source assets; do not repeatedly resize or re-encode an already degraded intermediate.
- All human-editable choices (page IDs/order/count, scene timing, crop anchor, title text, background theme, transition and CTA) must be data/config driven.
- Every job must produce a job manifest, storyboard, contact sheet, preview, QA report and final output manifest.
- Use a preview + human approval gate for new templates, new campaign types, AI-generated footage and any factual campaign copy. Trusted repeatable batches may use a configurable approval policy.
- Every output must be validated with FFprobe and the relevant platform profile before being reported as complete.

Now begin with Step 1. Do not modify files until the repository discovery report and implementation plan have been presented.
