# Rule: Figma → Lumen generation

These rules apply to the `figma-to-react-lumen` skill, its agents, and any manual work touching files that carry the `@generated-by figma-to-react-lumen` header.

## MUST

1. Treat `figma-dev-access` and `lumen-knowledgebase` MCP servers as the only sources of truth for Figma and Lumen facts. Web search is disabled and must not be attempted or suggested.
2. Back every Lumen component, prop, token and import path in generated code with an entry in `design-sync/<fileKey>/lumen-resolution.json` that records the MCP tool and query that produced it.
3. Record anything Lumen cannot express as a **gap** with a reason. Never approximate, hand-roll a look-alike, or hardcode a value to "get it done".
4. Cover everything the designer produced: each screen, layout and component is generated, reused, or an explicit gap. Ignored items need a reason.
5. Use Lumen components, props and tokens for all styling and layout.
6. Add the provenance header (`@generated-by figma-to-react-lumen`, Figma file key and node id) to every generated file.
7. Run `validate-lumen-compliance.mjs` and `verify-manifest.mjs` before declaring completion, and report checks that were not run as "not run".
8. Keep changes inside the generation paths, `.storybook/` (minimal), and `design-sync/`.

## MUST NOT

1. No inline `style`, no hex/rgb/hsl values, no raw px, no `any`, no raw `button`/`input`/`select`/`textarea`.
2. No non-Lumen UI libraries, and no new dependencies without explicit mention in the report.
3. No overwriting files that lack the generated header.
4. No credentials, tokens or MCP secrets in files, logs or reports.
5. No pushing, PRs, CI changes, or edits outside the repo.
6. No claims of verification that were not performed.

## Waivers

A single-line waiver is allowed only in this form and is listed in the final report:

```
// lumen-compliance-ignore-next-line <rule-id> -- <reason with ticket/reference>
```

## Where enforcement lives

- Config: `.claude/rules/lumen-compliance.config.json`
- Validator: `.claude/scripts/figma-to-lumen/validate-lumen-compliance.mjs`
- Optional write-time hook: `.claude/scripts/figma-to-lumen/hook-validate-on-write.mjs`
- Reviewer agent: `.claude/agents/lumen-reviewer.md`
