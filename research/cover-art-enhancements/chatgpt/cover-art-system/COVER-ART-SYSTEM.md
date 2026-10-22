# Cover Art System — Installation and Operating Guide

## What this adds

This is an additive Claude Code subsystem for the existing publishing framework. Both public frameworks already contain `.claude/agents/visual/art-director.md`; the book framework also has `book-generate-assets`, and the puzzle framework has `product-build-cover`. Reuse the existing art director and the appropriate existing generation skill. This package adds the cover-specific standard, a reusable cover-art skill, an independent critic, policy thresholds, and mechanical preflight—it deliberately does not add a competing art-director agent. It does not replace project state, book metadata, the design-policy engine, draw-things-cli settings, artifact registration, or the existing cover-approval gate.

Integrate `cover-art-system` into the design/prompt stage of `book-generate-assets` (publish-book) or `product-build-cover` (publish-puzzle), before the existing draw-things-cli/provider call. Keep each existing skill's provenance, artifact registration, and state transitions. The system adds one repeatable creative process:

1. Read the real book brief/content and exact text metadata.
2. Define a book-specific cover promise and visual thesis.
3. Invent multiple distinct visual directions or map one direction to each user-supplied reference image.
4. Write coherent prompts for the configured Qwen Image / draw-things-cli workflow.
5. Run an independent critique against an explicit scorecard.
6. Validate the resulting JSON package mechanically.
7. Generate and inspect the image candidates, including exact lettering and thumbnail use.
8. Hand candidates back to the existing framework's normal approval and production process.

## Files

```text
.claude/agents/visual/cover-art-critic.md
.claude/config/cover-art-policy.json
.claude/scripts/cover_art_preflight.py
.claude/skills/cover-art-system/SKILL.md
.claude/skills/cover-art-system/references/cover-design-standard.md
.claude/skills/cover-art-system/references/reference-image-analysis.md
docs/COVER-ART-SYSTEM.md
```

## Installation

Copy these files into the matching locations in the target repository. They are new files; merge rather than overwrite any existing files with the same names. The public repositories' architecture describes reusable skills beneath `.claude/skills/`, agents beneath `.claude/agents/<department>/`, and project-specific cover assets beneath `projects/<project-id>/visuals/cover/`. Preserve these conventions and the framework's state/approval process.

From the repository root, test that the policy is valid JSON and that the checker starts:

```bash
python3 -m json.tool .claude/config/cover-art-policy.json >/dev/null
python3 .claude/scripts/cover_art_preflight.py --help
```

The skill is made discoverable by its frontmatter name `cover-art-system`. In Claude Code, use the installed skill through its normal skill discovery mechanism, or invoke the workflow in plain language, for example:

> Use the cover-art-system skill for this book. Read the actual project brief and content before writing prompts. Create three materially different cover directions with exact title, series and publisher text, independently critique them, and save the validated prompt package under the project's visuals/cover directory. Use the configured draw-things-cli/Qwen Image settings; do not invent CLI flags or change the publishing lifecycle.

## Reference-image mode

Attach the images to the Claude session or make them accessible in the book project. Then ask:

> Use these three images as design references for the current book. Analyse each separately, transfer only abstract design principles, and create one distinct prompt direction per image. Keep the book brief and required visible text constant. Do not copy a reference's specific composition, subject, lettering, branding, character or unique motif. Save all three directions and the reference analysis in the cover prompt package.

With three usable reference images, the expected package has three reference records and three directions, each containing a matching `reference_id`. Every direction must still pass review. The system should not use one overall winner to conceal a failing variant.

## Output files created per book

The skill's default artifact names are:

- `visuals/cover/cover_prompt_package.json` — validated source-of-truth package for prompts and review.
- `visuals/cover/cover_art_direction.md` — concise art direction readable by a human.
- image candidates saved according to the repository's project naming and artifact-registration conventions.

Use the actual project path in place of `<project>`. Avoid overwriting approved artifacts; make candidates versioned and register them through the framework's existing artifact workflow.

## Package preflight

Run:

```bash
python3 .claude/scripts/cover_art_preflight.py projects/<project-id>/visuals/cover/cover_prompt_package.json
```

Exit codes:

- `0` — package passed mechanical preflight;
- `1` — package content or declared review gates failed;
- `2` — input/policy could not be read or parsed.

The checker verifies JSON structure, required source metadata, prompt inclusion of exact visible strings, the number/mapping of reference directions, unique directions/prompts, critic scorecard completeness, scores/weights, blockers, and generation plan. It cannot reliably judge visual beauty, image-model compliance, or whether a design feels generic; those remain Claude's design and visual-review responsibilities.

## How the critic gate works

The director creates concepts and prompts; the critic scores them independently. The current policy weights total 100 points:

| Dimension | Weight |
|---|---:|
| Book specificity | 20 |
| Visual hook | 15 |
| Composition | 15 |
| Palette and rendering | 10 |
| Typography | 15 |
| Audience fit | 10 |
| Thumbnail readability | 10 |
| Originality | 5 |

A ready-to-generate package requires no blockers, every critical dimension at least 4/5, and an overall weighted score of at least 84/100 for every direction. There are at most two revision cycles. These thresholds are intentionally strict: a generic but technically complete prompt is not a pass.

## Exact text and Qwen Image limitations

The prompt should direct Qwen Image to render the exact title, and series/publisher lines when present. This does not guarantee perfect glyphs or spelling from the image model. Inspect each generated image. If the text is wrong after targeted retries, keep the art only when it has a clear title-safe zone and use the framework's normal typesetting/layout process to add the exact strings. Do not claim the integrated cover is final until text is correct and legible.

## Integration cautions

- Reuse `.claude/agents/visual/art-director.md` as the creative lead; do not install a second art-director agent. The new critic is intentionally independent.
- Do not duplicate or replace the existing book/puzzle recommendation engine. Route the design/prompt stage in `book-generate-assets` or `product-build-cover` through this skill, then pass approved prompt outputs into the existing image-generation adapter.
- Do not change the sampler, CFG, steps, resolution, or other draw-things-cli options in this subsystem. They are intentionally left to the current model/parameter recommendation system.
- Do not let the skill bypass existing stage transitions, hash registration, human approvals, or release authorisation.
- Keep images and project-specific reference analysis in the relevant project. Do not add unpublished user-supplied reference art to a global style library without permission.
- When a model returns incorrect lettering, do not silently compensate by weakening the quality gate.

## Acceptance tests

Before considering integration complete, verify these cases manually:

1. **No references:** a book brief produces at least three substantially different concepts whose titles, hooks and compositions fit that book.
2. **Three references:** three images produce three reference records and exactly three directions, each linked to one image and transformed into the book's own visual language.
3. **Different categories:** a children's picture book, an adult mandala book, and an educational nonfiction title yield appropriate but non-template-driven art direction.
4. **Metadata exactness:** title, subtitle, series and publisher strings are preserved exactly; empty subtitle/series is accepted only if that field is genuinely absent.
5. **Critique gate:** a direction with an incorrect title or a low critical score fails preflight and is not handed off as production-ready.
6. **Originality:** reference-mode prompts do not request exact composition, character, logo, lettering, or a close recreation of a supplied cover.
7. **Thumbnail check:** the focal concept and title hierarchy remain clear at a small retail size.
8. **Framework integrity:** the new files do not alter project state, approvals, artifact hashes, publication status, or existing draw-things-cli argument policy.
