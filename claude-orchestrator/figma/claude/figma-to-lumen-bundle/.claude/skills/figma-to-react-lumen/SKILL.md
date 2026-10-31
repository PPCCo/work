---
name: figma-to-react-lumen
description: Convert a Figma hi-fi design URL into React components, layouts and screens built on the Lumen design system, with a Storybook story for every component, layout and screen. Use when the user provides a figma.com URL and wants it implemented in the Next.js repo using Lumen. Relies on the figma-dev-access and lumen-knowledgebase MCP servers; does not use web search.
---

# figma-to-react-lumen

Turns UI Designer hi-fi Figma screens into Lumen-based React code and a complete Storybook, autonomously, with evidence and gates at every step.

## Invocation

```
figma-to-react-lumen <figma-url> [--nodes <id,id,...>] [--dry-run]
```

- `<figma-url>`: a `figma.com/design/...` URL (with or without `node-id`). Without a node id, the whole file is in scope.
- `--nodes`: restrict scope to specific node ids (API form `12:34`).
- `--dry-run`: run Phases 1 and 2 only and stop after writing the snapshot, resolution and a planned manifest. No source files are written.

## Operating rules (read first)

1. Read `.claude/rules/figma-to-lumen.md` and `.claude/standards/lumen-compliance.md`. They override anything below if they conflict.
2. **MCP is the only source of truth** for Figma and Lumen facts. No web search. Never guess a Lumen component, prop, token or import path.
3. Tool names for the MCP servers are recorded in `.claude/rules/figma-to-lumen.mcp-tools.md`. If that file is missing, run the discovery step in `workflows/figma-to-lumen.md` Phase 0 first.
4. Full coverage or an explicit gap. Never silently skip a screen or component.

## Steps

1. **Preflight**
   - `node .claude/scripts/figma-to-lumen/parse-figma-url.mjs "<url>"`; stop on `ok:false` and tell the user why.
   - `node .claude/scripts/figma-to-lumen/preflight.mjs --repo . --config .claude/rules/lumen-compliance.config.json`; stop on blockers.
   - Confirm both MCP servers respond (one cheap call each). Stop and report if either does not.
2. **Ingest** → delegate to agent `figma-ingestor` → `design-sync/<fileKey>/source-snapshot.json`. Gate 1.
3. **Resolve** → delegate to agent `lumen-resolver` → `design-sync/<fileKey>/lumen-resolution.json`. Gate 2.
4. **Build** → delegate to agent `lumen-builder` (batch by feature/screen; it may run in parallel batches of at most 4 items). Writes components, layouts, screens, stories and `manifest.json`.
5. **Verify**
   - `node .claude/scripts/figma-to-lumen/validate-lumen-compliance.mjs --config .claude/rules/lumen-compliance.config.json --evidence design-sync/<fileKey>/lumen-resolution.json <generated files>`
   - `node .claude/scripts/figma-to-lumen/verify-manifest.mjs --dir design-sync/<fileKey> --repo .`
   - Repo checks using the project's own scripts: typecheck, lint, Storybook build.
   - Delegate to agent `lumen-reviewer` → `design-sync/<fileKey>/review.md`.
   - On failure, send findings back to `lumen-builder`. Maximum 3 iterations, then stop with a precise failure report.
6. **Report** → write `design-sync/<fileKey>/REPORT.md` from `templates/REPORT.md.tpl`, then reply with a short summary (counts, gaps, checks run versus not run, how to launch Storybook).

## Outputs

| Path | Content |
|---|---|
| `design-sync/<fileKey>/source-snapshot.json` | Figma inventory, styles, variables, screenshots index |
| `design-sync/<fileKey>/lumen-resolution.json` | MCP-verified Lumen components, props, imports, tokens, gaps |
| `design-sync/<fileKey>/manifest.json` | Figma item → generated files / reused / gap |
| `design-sync/<fileKey>/review.md` | Independent reviewer findings |
| `design-sync/<fileKey>/REPORT.md` | Final report |
| `src/components|layouts|screens/**` | Generated code and `*.stories.tsx` (paths per `ALIGNMENT-REPORT.md`) |

Artifact contracts: `.claude/patterns/figma-to-lumen-artifacts.md`. Mapping heuristics: `.claude/patterns/figma-to-lumen-mapping.md`. Story standard: `.claude/standards/storybook-figma-stories.md`.

## Stop and ask the user only when

- an MCP server is unreachable or Lumen is not installed in the repo;
- a Figma node cannot be classified after two attempts;
- gaps affect more than 25% of screens;
- a write would overwrite a file that lacks the `@generated-by figma-to-react-lumen` header.

Otherwise continue, and record assumptions in the report.

## Idempotency

Re-running on the same URL must produce the same output and a minimal diff. Files carrying the `@generated-by` header may be regenerated; files without it are never overwritten (write a sibling `*.generated.tsx` and report it).
