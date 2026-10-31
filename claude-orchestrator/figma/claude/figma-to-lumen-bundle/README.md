# figma-to-react-lumen bundle

1. Put the `.claude/` folder contents from this bundle next to your existing `.claude/` **without overwriting**: Claude Code will merge in Phase 0. If you copy manually, do not clobber your existing `.clauderc` or `workflows/figma-to-lumen.md`.
2. Open Claude Code at the root of your Next.js repo.
3. Paste `00-MEGA-PROMPT.md` (everything below its first horizontal rule), then give it the Figma URL.
4. Optionally attach `IMPLEMENTATION-PLAN.md` for the work breakdown, test plan and risks.

Quick check of the bundled scripts at any time:

```
node .claude/scripts/figma-to-lumen/selftest.mjs
```

Things in this bundle that are **assumptions to verify**, not facts: the package name `@cba/lumen-ui`, all MCP tool names, how `.clauderc` is consumed, and the Claude Code hook schema. The fixtures use a fictional Lumen API for testing the validator only.
