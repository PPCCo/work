# Skill for Qwen-Image-2512

I have decided to use Qwen-Image-2512 since it is better than Flux.2-Klein. In the above file you generated, can you replace the strategy and instructions to use Qwen-Image-2512 (`Q8_0`) instead of Flux.2-Klein. Only give me files that you change or add.

## Response

Good — I have what I need. This is a substantial rewrite since Qwen-Image-2512 differs from Klein in ways that matter: it's a 20B model (vs 4B), it has a **real negative-prompt channel** via CFG (Klein has none), different native resolutions, and a different loader stack for the Q8_0 GGUF you picked. Let me rebuild the affected files.

Now the core rewrite — the prompt standards. This is where the model's actual behavior differs most.Now the runtime reference — model files, GGUF loaders, resolution, VRAM.Now update the audit script — the biggest logic change: negation handling flips, plus a real negative-prompt field.Now `build_prompt.py` — RUNTIME tiers, negative prompt plumbing, magic-suffix flag.Now `batch_generate.py` — needs to actually wire the negative node instead of treating it as decorative.Now update the two remaining references and the SKILL.md itself.Now the assets — style_packs.json needs `negative` fields, renamed `variant` values, and a `magic_suffix` constant. Also brief.example.json.Now the SKILL.md itself — the entry point.Now let's test everything end to end before touching the cover pack.All three behave correctly. Now the full build → batch pipeline test.Now `batch_generate.py` with a synthetic workflow that includes a negative node, to verify the patch actually writes to it.

Let me check exactly what's left before I answer that.Not yet — the cover pack still has nine files referencing Klein. Let me finish those now, then package everything.Simple docstring fix there. Now the substantial one — `cover_prompt.py`.Now the cover style packs — add `negative`, rename variants, bump version.Now the remaining smaller files: the agent, the skill doc, the standard, the README, the template, and INTEGRATION.md.That remaining mention is intentional context. Now the `book-cover-art` skill doc.Now the design standard's model row, the scripts README, the brief template, and INTEGRATION.md.Now the docstring line in `cover_compose.py`, the brief template's provenance field, and INTEGRATION.md.Now INTEGRATION.md — the install instructions and the hardware-reality callout.Now let's do a full verification sweep across both packages, then assemble the unified `.claude/` zip.One real bug: a stale filename reference. Let me fix and do a final cross-reference check.Now let's re-run the full end-to-end tests on both packages to confirm nothing broke, then assemble the unified `.claude/` package.The auditor is correctly cross-discovered (`auditor: qwen-kids-art`) and negative prompts flow through end to end. Now let's assemble the unified `.claude/` package.It's empty, harmless leftover — cleaning it out.Clean. Now verify the auto-discovery actually works from inside this exact nested layout (this is the real integration test — no env var at all).Auto-discovery works with zero configuration in the packaged layout. Now let's validate the full tree, add a top-level README pointing at INTEGRATION.md, and zip it.No — not yet, but they are now. Two things were still on Klein when you asked:

I've done the `interior-art` skill itself — prompt standards, audit script, build script, batch script, style packs.

There are nine files in the cover pack that still said Klein — `cover_prompt.py` (the big one: GEN_SIZES moved to Qwen's actual native ratios, negative-prompt plumbing added, `find_klein_auditor`→`find_qwen_auditor`), `cover_style_packs.json` (added a `negative` list to all six cover packs, renamed `base/distilled`→`full/lightning`), the `cover-art-director` agent, the `book-cover-art` skill, the design standard's tool table, the scripts README, the brief template's provenance field, `cover_compose.py`'s docstring, and `INTEGRATION.md`.

Unzip this into your `publish-book` repo root and it lays out as:

```
.claude/
├── agents/            cover-art-director, cover-typographer, cover-copywriter, cover-critic
├── skills/
│   ├── qwen-kids-art/       ← the interior-art skill, nested here on purpose
│   ├── book-cover-brief/
│   ├── book-cover-art/
│   ├── book-cover-compose/
│   └── book-cover-review/
├── standards/          five cover-*.md files
├── schemas/, templates/, assets/, scripts/cover/
```

The nesting matters: `cover_prompt.py` auto-discovers `qwen-kids-art` at exactly `.claude/skills/qwen-kids-art` — I tested this from the actual unzipped layout with `QWEN_SKILL_PATH` unset, and it found it with zero configuration (`"auditor": "qwen-kids-art"` in the output).

Everything's tested end to end from inside this package, not just in isolation: `cover_spec.py` → `cover_prompt.py` (auto-discovering the skill, real negative prompt attached, audit passing) → the same auditor logic the interior skill uses. I also ran a syntax and JSON-validity sweep over all 35 files after assembly.

One thing worth reading before your first render: `INTEGRATION.md` now opens with a hardware callout I added — Qwen-Image-2512 is a 20B model versus Klein's 4B, the Q8_0 GGUF is ~20GB on disk, and you want 24GB+ VRAM to run it comfortably. If your ComfyUI box was sized for the old setup, that's worth confirming before you build a pipeline around it.
