I'll build this as a drop-in bundle: the mega-prompt, an implementation plan, and the `.claude/` files, then run the scripts against fixtures to check they work.

The directory-creation call didn't run, so I'm repeating it once.

Mega-prompt and the URL parser and compliance validator are written. Now the manifest verifier, preflight, hook and self-test, then fixtures.

All 22 self-tests pass. I'll check the CLI entry points and the hook directly, since the tests only call the functions.

Now the rules, standards, patterns and templates.

The bundle is ready: `00-MEGA-PROMPT.md` is the prompt to paste into Claude Code, and `figma-to-lumen-bundle.zip` has everything else. The bundled scripts pass all 22 self-tests on fixtures, but nothing has run against your real repo, Lumen package, MCP servers or Figma file.

**How to use it**
1. Unzip and copy the `.claude/` contents next to your existing `.claude/`. The prompt tells Claude Code to merge and not overwrite, so your `.clauderc` and `figma-to-lumen.md` are merged rather than replaced.
2. Open Claude Code at the root of your Next.js repo, paste the mega-prompt, and give it the Figma URL.

**What the prompt makes Claude Code do**
- **Align first.** Phase 0 inventories your existing `.claude/`, MCP tools and repo, and writes an alignment report. Nothing is added to `.claude/` until that exists.
- **Run a four-agent pipeline.** An ingestor reads Figma, a resolver queries Lumen via MCP, a builder writes the components and stories, and a reviewer re-checks a sample against Lumen without editing source.
- **Leave evidence.** Each run produces a snapshot, a Lumen resolution file, a manifest and a report under `design-sync/<fileKey>/`.
- **Fail loudly.** Anything Lumen can't express becomes a recorded gap instead of a guess, and the manifest check fails if any screen or component is unaccounted for.
- **Prove itself.** Claude Code has to show self-test output, a live run and an idempotency run before it reports done.

The bundle also holds the skill, workflow, rules, standards, patterns, templates, optional write-time hook and implementation plan.

**What I couldn't know, and the prompt tells Claude Code to verify**
- **MCP tool names:** the names in your example, like `figma/get_node`, are treated as illustrative. Phase 0 discovers the real ones.
- **Package name:** `@cba/lumen-ui` comes from your example and is marked unverified in the compliance config.
- **`.clauderc`:** I'm not certain Claude Code reads it. The prompt asks Claude Code to check, and enforcement doesn't depend on it (it also sits in the rules, validator and reviewer).
- **Hook schema:** the optional write hook assumes the Claude Code hook format as I understand it. It's optional and Phase 4 enforces the same checks without it.

**Limits**
- The compliance validator is a lexical checker, not a TypeScript parser. It won't see spread props or dynamic prop objects, so `tsc`, lint and the reviewer still matter.
- Visual comparison with Figma only runs if a browser test tool is already installed. Otherwise the report says "not run" and lists a manual checklist.
- The fixtures use a fictional Lumen API and exist only to test the scripts.

Files are in the zip (also sent separately):
- 00-MEGA-PROMPT.md
- IMPLEMENTATION-PLAN.md
- README.md
- figma-to-lumen-bundle.zip