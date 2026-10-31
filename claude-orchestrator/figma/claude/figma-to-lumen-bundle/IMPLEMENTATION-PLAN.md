# Implementation Plan: `figma-to-react-lumen` pipeline

Companion to `00-MEGA-PROMPT.md`. Claude Code should follow this plan, adapting it to the Phase 0 findings. Nothing here requires web search.

## 1. Goal

One invocation, `figma-to-react-lumen <figma-url>`, converts the UI Designer's hi-fi Figma screens into Lumen-based React components, layouts and screens inside the existing Next.js app, plus a Storybook covering every component, layout and screen, with evidence that each Lumen usage was verified through MCP.

## 2. What is in this bundle

```
00-MEGA-PROMPT.md                         the prompt to give Claude Code
IMPLEMENTATION-PLAN.md                    this file
.claude/
  skills/figma-to-react-lumen/
    SKILL.md                              entry point / orchestrator
    templates/                            component, story, screen story, report templates
  agents/
    figma-ingestor.md                     Phase 1
    lumen-resolver.md                     Phase 2
    lumen-builder.md                      Phase 3 (and fix loops)
    lumen-reviewer.md                     Phase 4, independent
  workflows/figma-to-lumen.md             detailed phases (merge with existing file)
  rules/
    figma-to-lumen.md                     hard rules
    clauderc.additions.md                 keys to MERGE into the existing .clauderc
    lumen-compliance.config.json          validator config (DRAFT: package names unverified)
  standards/
    lumen-compliance.md
    storybook-figma-stories.md
  patterns/
    figma-to-lumen-mapping.md
    figma-to-lumen-artifacts.md           JSON contracts for the artifacts
  scripts/figma-to-lumen/
    parse-figma-url.mjs                   URL → fileKey / nodeId
    preflight.mjs                         repo readiness checks
    validate-lumen-compliance.mjs         compliance gate (lexical)
    verify-manifest.mjs                   coverage gate
    hook-validate-on-write.mjs            optional write-time hook
    settings.hook.snippet.json            hook config to merge
    selftest.mjs                          runs everything against fixtures
    __fixtures__/                         FICTIONAL Lumen API, test data only
```

The scripts use Node built-ins only (Node 18+). They were run against the fixtures before packaging (22 tests passing), but they have **not** been run against your real repo, real Lumen package or real Figma file; that is what the live run in Section 6 is for.

## 3. Facts that must be established in Phase 0 (not assumed)

| Unknown | How to resolve | Where it lands |
|---|---|---|
| Exact MCP tool names and schemas for both servers | List tools/resources, probe harmlessly | `.claude/rules/figma-to-lumen.mcp-tools.md` |
| Real Lumen package name and import paths (`@cba/lumen-ui` is from an example) | Lumen MCP + `node_modules` | `lumen-compliance.config.json` |
| Whether `.clauderc` is consumed by anything | Inspect framework scripts/settings | `ALIGNMENT-REPORT.md` |
| Claude Code hook schema in the installed version | Inspect existing `settings.json` hooks, or `/hooks` in the CLI | hook snippet, selftest |
| Agent frontmatter conventions (tools, model) in the existing framework | Read existing agents | Adjust the four agent files |
| How Lumen provider/theme is mounted in the app | Search `layout.tsx`, `_app.tsx`, providers | `.storybook/preview.tsx` decision |
| Router (App or Pages), aliases, folder conventions, Storybook version | Repo inventory + `preflight.mjs` | Output paths, story framework package |
| Whether Figma MCP exposes variables, Code Connect, screenshots | MCP discovery | `limitations` in the snapshot, adjustments to Phase 1 |

## 4. Work breakdown

1. **Phase 0 (no writes to `.claude/`):** run the discovery in the mega-prompt and write `design-sync/ALIGNMENT-REPORT.md`.
2. **Install the bundle with merge semantics:**
   - NEW files: copy in.
   - `.clauderc`: merge keys from `clauderc.additions.md`.
   - Existing `workflows/figma-to-lumen.md`: merge; keep existing content that is not contradicted.
   - `settings.json`: merge the hook snippet only if the hook contract is confirmed. Otherwise skip the hook; Phase 4 validation still enforces everything.
   - Rename or adapt files to match existing naming and frontmatter conventions.
   - Drop anything the framework already covers.
3. **Generate `figma-to-lumen.mcp-tools.md`** from discovery. Update the agent files if tools must be allow-listed explicitly in this framework's frontmatter.
4. **Finalise `lumen-compliance.config.json`** (Lumen prefixes, aliases) from verified facts.
5. **Run `selftest.mjs`.** Fix and extend tests for any script you modify (for example if the Lumen import style is per-component paths, add a fixture covering it).
6. **Fixture dry-run** of the deterministic stages.
7. **Live run** on the real Figma URL; iterate through Gate 4.
8. **Idempotency run** and final report.

## 5. Design decisions (and why)

| Decision | Reason |
|---|---|
| Evidence file (`lumen-resolution.json`) between resolver and builder | Makes "always verify Lumen props" mechanically checkable, rather than a prompt-only instruction |
| Independent reviewer agent with no write access to source | Code authors tend to approve their own output; the reviewer re-queries Lumen MCP |
| Deterministic scripts for URL parsing, compliance and coverage | LLM judgement is wrong sometimes; these checks are cheap and repeatable |
| Manifest with `expected` inventory and explicit gaps | Prevents silent omission of designer screens |
| Generated-file header + never overwrite headerless files | Protects hand-written code and enables safe regeneration |
| Gaps over approximation | A visible gap gets fixed upstream (designer or Lumen team); a quiet look-alike rots |
| Validator is lexical, not a TS parser | No dependencies to install or approve; `tsc` and lint cover the typed side |
| Reuse repo components and Code Connect mappings first | Avoids duplicating components that already exist |

## 6. Test plan and acceptance

| # | Test | Pass criteria |
|---|---|---|
| T1 | `node .claude/scripts/figma-to-lumen/selftest.mjs` | All tests pass |
| T2 | Framework alignment | Skill, agents and workflow load in the existing framework; `git diff --stat .claude/` shows only additions and intended merges |
| T3 | Preflight | `preflight.mjs --repo . --config .claude/rules/lumen-compliance.config.json` has no blockers |
| T4 | Fixture dry-run | Validator and manifest verifier give expected pass/fail on fixtures |
| T5 | Live run | 100% inventory accounted for; zero compliance violations; typecheck and lint clean for generated files; Storybook builds; each screen has a story at the designer's frame size |
| T6 | Independent review | `review.md` verdict pass or pass-with-notes; sampled Lumen props re-verified via MCP |
| T7 | Idempotency | Second run gives an empty or explainable diff |
| T8 | Negative test | Temporarily introduce an unverified prop into a generated file and confirm the validator (and the hook, if installed) blocks it, then revert |

## 7. Risks and mitigations

| Risk | Mitigation |
|---|---|
| MCP tool names/shapes differ from what the drafts assume | Phase 0 discovery; agents reference the generated tools file, not hardcoded names |
| Lumen package is on a private registry and not installed | Preflight blocks; report exactly what is needed |
| Large Figma files exhaust context | Ingest per page/frame, write snapshot incrementally, build in batches of at most 4 items per builder call |
| Lexical validator misses typed or dynamic props | Reviewer samples, `tsc`, lint; warnings for spreads |
| Designs use patterns Lumen lacks | Gap list with suggestions; threshold stop at more than 25% of screens |
| Visual fidelity cannot be measured automatically | Report "not run" honestly; manual checklist; optional Playwright if already installed |
| Regeneration clobbers manual edits | Header-based ownership; headerless files get a sibling `.generated.tsx` |
| Hook contract differs by Claude Code version | Hook is optional and Phase 4 enforcement does not depend on it |

## 8. Out of scope

Pushing, PRs, CI changes, publishing Storybook, wiring generated screens into Next.js routes (screens are generated as components and stories; routing is a separate decision), data fetching/business logic, and backend work.
