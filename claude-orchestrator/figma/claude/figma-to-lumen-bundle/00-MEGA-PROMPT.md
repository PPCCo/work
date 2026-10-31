# MEGA-PROMPT — Build the `figma-to-react-lumen` Autonomous Pipeline

> **How to use:** Open Claude Code in the root of the Next.js repository. Make sure the `.claude/` folder is present (your existing framework), copy the contents of this bundle's `.claude/` folder next to it (do NOT overwrite — see Phase 0), then paste everything below the line as your prompt. Provide the Figma hi-fi URL when asked (or append it to the prompt).

---

## 1. ROLE

You are a senior staff engineer and framework architect working inside CommBank (CBA). You are extending an **existing** `.claude/` framework (skills, agents, workflows, standards, scripts, rules) so that a single invocation can turn UI Designer hi-fi Figma screens into production-quality **React components, layouts and screens built on Lumen (CommBank's design system)**, plus a **Storybook** that documents every component, layout and screen the designer produced.

You operate autonomously, but you are **evidence-driven**: you never guess what the Lumen API looks like.

## 2. SITUATION AND INPUTS

You will receive, together with this prompt:

1. **A Figma file URL** containing hi-fi screens from our UI Designer (Dev Mode access is licensed). A `node-id` may or may not be present.
2. **The repository** of an existing **Next.js** app. Generated components and Storybook are to be added to **this** repo.
3. **A bundle of draft framework files** (skills, agents, workflow, rules, standards, patterns, templates, scripts, fixtures) that are **proposals**. They are strong starting points, not gospel.
4. **The existing `.claude/` framework**, which is the authority on conventions.

### Tooling reality (critical)

- **`WebSearch` is disabled.** Do not try to search the web, fetch docs, or install knowledge from the internet. Never write a plan step that depends on it.
- You do have **two MCP servers**, and they are your only sources of truth:
  - `figma-dev-access`: live Figma file/node access (structure, styles, variables, screenshots, possibly Code Connect data).
  - `lumen-knowledgebase`: live Lumen design-system knowledge (components, props, tokens, patterns, import paths, usage guidance).
- **Exact MCP tool names are NOT known to the author of this prompt.** Examples such as `figma/get_node` or `lumen/get_component_specs` are illustrative only. In Phase 0 you must **discover the real tool names and schemas** from the connected servers, then record them in `.claude/rules/figma-to-lumen.mcp-tools.md` and use only those.
- Package names such as `@cba/lumen-ui` come from an example. **Verify the real package name and import paths via the Lumen MCP**, then write them into the compliance config. If the MCP cannot confirm something, record it as an open question; do not invent it.
- `.clauderc` appeared in an example. **Check how (or whether) your framework actually consumes it.** If nothing reads it, treat it as documentation and enforce through hooks, scripts and agent instructions instead. Say which you found.

## 3. NON-NEGOTIABLE PRINCIPLES

1. **MCP is the source of truth.** Every Lumen component, prop, token and import path that appears in generated code must be backed by evidence returned by `lumen-knowledgebase` during this run, and recorded in a resolution file.
2. **Unknown means "gap", not "guess".** If Figma shows something Lumen cannot express, record it in a `gaps` list with a reason and a suggested handling. Never silently approximate and never hand-roll a look-alike.
3. **No hardcoded design values.** No hex/rgb/hsl, no raw px, no inline `style`, no non-Lumen UI libraries. Use Lumen components, props and tokens.
4. **Full coverage.** Every top-level screen/frame and every component the designer produced must end up as generated code **or** an explicit, reasoned gap. Silent omission is a failure. The manifest verifier enforces this.
5. **Align before you add.** Existing framework conventions win over the bundle's drafts. Merge, adapt and rename to fit. Never overwrite existing files without a diff-based reason.
6. **Test what you add.** Nothing is "done" until the pipeline's own scripts, a fixture dry-run and a real run have produced evidence (Section 8).
7. **Minimal footprint.** Add only what the pipeline needs. Reuse existing agents, standards and scripts wherever they already do the job.
8. **Honest reporting.** Report what was verified, what was not, and what could not be verified (for example, visual diff not run). Do not claim a check passed unless you ran it.
9. **No new runtime dependencies** in the Next.js app without listing them in the report. Storybook devDependencies are allowed only if Storybook is missing, and the version must match `storybook = "v8"` unless the repo already pins another major (then flag it).

## 4. PHASE 0 — DISCOVER AND ALIGN (do this before writing anything)

Produce `design-sync/ALIGNMENT-REPORT.md` (and keep it in the repo) containing:

1. **Framework inventory.** Read every file in `.claude/` (skills, agents, workflows, standards, rules, scripts, any `settings*.json`, any `CLAUDE.md`). Summarise: naming conventions, frontmatter conventions, how skills are invoked/chained, how agents are declared (tools, model), how rules are enforced, test/verification conventions, commit/branch conventions, anything about "autonomy levels" or approval gates.
2. **Overlap and conflict table** between the bundle's draft files and what exists. For each draft file: `NEW` / `MERGE INTO <existing>` / `REPLACE (justify)` / `SKIP (already covered by <existing>)`. Existing `.clauderc` and `figma-to-lumen.md` workflow are **merged**, not replaced.
3. **MCP discovery.** List tools and resources of `figma-dev-access` and `lumen-knowledgebase`. For each: name, purpose, inputs, outputs. Note anything the pipeline needs that is missing (for example, no way to fetch variables, no component props endpoint). Make a few small, harmless probe calls to confirm output shapes; save trimmed samples under `design-sync/_probes/`.
4. **Repository inventory.** Next.js version, App Router vs Pages Router, TypeScript config and path aliases, package manager, existing component folder convention, existing Lumen usage and provider/theme wiring (find where Lumen's provider/theme is mounted), existing `.storybook/` config and Storybook version, test runner, lint/format setup, scripts in `package.json`.
5. **Decisions** for: output folders (default `src/components`, `src/layouts`, `src/screens`, adjusted to repo convention), story title taxonomy, whether components need `'use client'`, how Lumen provider is applied in Storybook decorators, and whether a Playwright/visual check is available.
6. **Open questions and assumptions**, each with how the pipeline behaves until answered.

**Gate 0:** if MCP servers are unreachable, or Lumen's package is not installed in the repo, **stop** and report exactly what is missing. Do not proceed with guesses.

## 5. WHAT TO BUILD (inside the existing `.claude/`)

The bundle contains drafts of each item. Adapt them to Phase 0 findings.

| Area | Item | Purpose |
|---|---|---|
| Skill | `skills/figma-to-react-lumen/SKILL.md` (+ `templates/`) | Entry point. Input: Figma URL. Orchestrates the workflow and gates. |
| Workflow | `workflows/figma-to-lumen.md` | Detailed phase spec (merge with the existing draft). |
| Agents | `figma-ingestor`, `lumen-resolver`, `lumen-builder`, `lumen-reviewer` | Separation of concerns; the reviewer is independent of the builder. |
| Rules | `rules/figma-to-lumen.md`, `.clauderc` additions, `rules/lumen-compliance.config.json`, `rules/figma-to-lumen.mcp-tools.md` (generated in Phase 0) | Hard constraints and config. |
| Standards | `standards/lumen-compliance.md`, `standards/storybook-figma-stories.md` | Quality bar for code and stories. |
| Patterns | `patterns/figma-to-lumen-mapping.md`, `patterns/figma-to-lumen-artifacts.md` | Figma→Lumen mapping heuristics and artifact contracts. |
| Scripts | `scripts/figma-to-lumen/*.mjs` | Deterministic checks: URL parser, preflight, compliance validator, manifest verifier, write-hook, self-test. |
| Hook (optional) | Settings snippet | Run the validator after every generated-file write. Merge into existing settings. |

Only keep what Phase 0 shows to be needed. If your framework already has an equivalent (for example a generic reviewer agent), reference or extend it instead of duplicating.

## 6. PIPELINE SPECIFICATION

Single entry point: the skill `figma-to-react-lumen <figma-url> [--nodes <ids>] [--dry-run]`.

All pipeline artifacts live in `design-sync/<fileKey>/` (committed, so reviewers can audit the evidence):

- `source-snapshot.json` — what Figma contains (inventory + styles + variables + screenshots index).
- `lumen-resolution.json` — Lumen evidence: components, props, import paths, tokens, with the MCP tool and query that produced each entry.
- `manifest.json` — every Figma item mapped to generated files, reused components, or gaps.
- `review.md` — independent reviewer output.
- `REPORT.md` — final human-readable summary.

**Phase 1 — Ingest (figma-ingestor).** Run `parse-figma-url.mjs` on the URL. Resolve scope: if a `node-id` is given use it; else enumerate pages and top-level frames. Pull structure, auto-layout, component/instance/variant info, styles, **variables and their modes**, text styles, and a screenshot per top-level frame. Classify each item as `screen`, `layout`, `component`, or `ignored` (with reason) using `patterns/figma-to-lumen-mapping.md`. If the design uses Code Connect data, harvest it: mapped components are **reused**, not regenerated. Write `source-snapshot.json`. **Gate 1:** inventory is non-empty and every item has a classification.

**Phase 2 — Resolve (lumen-resolver).** For each distinct Figma pattern, query Lumen via MCP: component, variants, props, composition rules, tokens, import path, layout primitives and accessibility guidance. Map Figma variables and styles to Lumen tokens. Record evidence in `lumen-resolution.json`, including the tool name and query. Anything unresolved goes to `gaps`. **Gate 2:** no pattern is both unresolved and unlisted as a gap.

**Phase 3 — Build (lumen-builder).** Before writing, check the repo for existing components that already fulfil the item and reuse them. Then generate, per item: a typed functional React component (explicit props interface, data/actions as props, no hardcoded copy that should be props unless it is clearly static), a Storybook CSF3 story (default export `Meta`, `satisfies Meta<typeof X>`, `tags: ['autodocs']`, `args`/`argTypes` for dynamic props, one named story per Figma variant/state), and for each screen a **screen story** at the designer's viewport using realistic fixtures. Wire Lumen's provider/theme into Storybook per the Phase 0 decision. Follow the templates. Run the compliance validator on each file as it is written.

**Phase 4 — Verify (scripts, then lumen-reviewer).**
1. `validate-lumen-compliance.mjs` on all generated files: zero violations.
2. `verify-manifest.mjs`: full coverage, files exist, every component and screen has stories, variant counts match.
3. Repo checks: `tsc --noEmit`, lint, and `storybook build` (or the repo's equivalent scripts). If a check cannot run (for example, no network for installs), say so.
4. Visual check **only if** Playwright or an equivalent is already available: render each screen story and compare with the Figma screenshot, recording differences. Otherwise list "visual diff not run" in the report along with a manual checklist.
5. The independent **lumen-reviewer** re-queries Lumen MCP for a sample (at least 20% of components, and every gap) and cross-checks against the code. It writes `review.md` with findings; it must not edit source files.
**Gate 4:** if anything fails, loop back (max 3 build-verify iterations), then stop with a precise failure report instead of papering over it.

**Phase 5 — Report.** `REPORT.md`: what was generated (counts and file list), reused components, gaps with reasons and suggested follow-ups for the designer or Lumen team, checks run vs not run, assumptions made, and commands to run Storybook locally.

## 7. AUTONOMY, SAFETY AND STOP CONDITIONS

- Work inside the repo. Do not push, do not open PRs, do not modify CI, do not modify or delete anything outside the generation paths and `design-sync/`. If the repo convention calls for a branch, create `feat/figma-to-lumen-<fileKey>` locally only.
- Never write secrets, tokens or the Figma access token into files or logs.
- Stop and ask only when: MCP is unreachable; Lumen is not installed; a Figma node cannot be classified after two attempts; a gap affects more than 25% of screens; or an action would overwrite hand-written code that is not generated by this pipeline. Otherwise proceed and record assumptions.
- Generated files carry a header comment with `@generated-by figma-to-react-lumen`, the Figma file key and node id. Regeneration may overwrite files with that header; files without it are never overwritten (write a sibling `.generated.tsx` and report it instead).
- Be idempotent: running the skill twice on the same URL yields the same result and a minimal diff.
- Keep your narration short. The artifacts and the report are the communication.

## 8. TESTING AND ACCEPTANCE (you must run these and show the output)

1. **Unit/self tests:** `node .claude/scripts/figma-to-lumen/selftest.mjs` passes (URL parsing, validator rules against good and bad fixtures, manifest verifier against good and mutated manifests). If you changed any script during alignment, extend the self-test to cover the change.
2. **Framework alignment test:** show that the new skill, agents and workflow are discoverable and load in the existing framework (for example, listing skills/agents the way your framework does), that frontmatter matches the existing conventions, and that no existing file was unintentionally altered (`git diff --stat` for `.claude/` should show only additions and intentional merges).
3. **Fixture dry-run:** run the pipeline stages against the fixtures in `scripts/figma-to-lumen/__fixtures__/` without MCP, to prove the deterministic parts work.
4. **Live run:** run the real skill on the provided Figma URL. Acceptance criteria:
   - 100% of screens/components accounted for (generated, reused, or a justified gap);
   - zero compliance violations;
   - `tsc --noEmit` and lint clean for generated files;
   - Storybook builds, and every screen has a story at the designer's viewport;
   - the report states exactly what was and was not verified.
5. **Idempotency check:** run the skill a second time; the diff must be empty or explainable.

## 9. FINAL RESPONSE FORMAT

When finished, reply with:

1. **Verdict** in one or two sentences (pass, partial, blocked).
2. **What was added/changed** in `.claude/` (a table: file → NEW/MERGED/UNCHANGED).
3. **Test evidence** (commands and outcomes from Section 8).
4. **Pipeline output summary** (counts, gaps, reused components).
5. **Open questions / risks** that need a human (designer, Lumen team, platform team).
6. **How to run it next time:** the exact invocation.

Begin with Phase 0. Do not write files into `.claude/` until `ALIGNMENT-REPORT.md` exists.
