# Cover pack — integration into publish-book

A drop-in extension for the Claude Publishing House repo. Everything here lives
under `.claude/`, follows the repo's existing conventions (agents, skills,
standards, schemas, templates, deterministic scripts), and adds no network
access, no external writes and no new publishing capability.

---

## 1. Install

```bash
cp -r publish-book-cover-pack/.claude/. /path/to/publish-book/.claude/
cd /path/to/publish-book
python .claude/scripts/ph_cli.py framework validate
```

Nothing is overwritten: every file is new and namespaced `cover-*` or
`book-cover-*`. Then make the Klein prompt skill findable, so cover prompts are
audited by the same rules as interior art:

```bash
# in .claude/settings.local.json or the shell that runs Claude Code
export KLEIN_SKILL_PATH=/path/to/klein-kids-art
```

Python needs Pillow (`pip install Pillow`); `pypdf` is optional and only used to
measure PDF wraps. Fonts must be installed locally — the composer refuses to
invent type.

## 2. What lands where

```
.claude/
├── agents/
│   ├── cover-art-director.md      decides the look, writes audited Klein prompts
│   ├── cover-typographer.md       sets all type, assembles the deliverables
│   ├── cover-copywriter.md        back cover + the listing fields it feeds
│   └── cover-critic.md            adversarial review before the gate
├── skills/
│   ├── book-cover-brief/          /book-cover-brief   geometry + direction
│   ├── book-cover-art/            /book-cover-art     Klein artwork
│   ├── book-cover-compose/        /book-cover-compose type + wrap + ebook
│   └── book-cover-review/         /book-cover-review  thumbnail + preflight gate
├── standards/
│   ├── cover-design-standard.md       the rules, incl. the art/type division
│   ├── cover-typography-standard.md   pairings, sizes, licensing, print
│   ├── cover-audience-standard.md     the four audience bands
│   ├── cover-channel-specs.md         KDP/Apple/Etsy/eBay/audiobook
│   └── cover-copy-standard.md         back cover + listing copy
├── schemas/cover-spec.schema.json
├── templates/cover-brief.template.yaml
├── assets/
│   ├── cover_channel_specs.json   print + channel constants (verify per release)
│   └── cover_style_packs.json     art direction packs per audience
└── scripts/cover/
    ├── cover_spec.py        geometry: spine, bleed, safe areas, barcode, ebook
    ├── cover_prompt.py      Klein prompts with reserved type zones + upscale plan
    ├── cover_compose.py     typography + wrap + ebook + SVG master
    ├── thumbnail_test.py    80/120/240px, greyscale, squint, heuristics
    └── cover_preflight.py   channel checks on the finished files
```

## 3. Where it sits in the lifecycle

| Stage | Cover work | Produces |
|---|---|---|
| `VISUAL_DEVELOPMENT` | `/book-cover-brief` → `/book-cover-art` | `spec.json`, `guides.svg`, `cover-brief.yaml`, `art-plan.json`, `art/*.png` |
| `LAYOUT_AND_FORMAT_BUILD` | `/book-cover-compose` | `wrap.pdf`, `wrap.png`, `ebook.jpg`, `front_only.png`, `wrap.svg`, `layout-report.json` |
| `METADATA_AND_COMMERCIAL_PACKAGE` | copywriter output → `/book-metadata`, `/book-marketing` | description, keywords, categories, AI disclosure |
| `FINAL_PROOF` | `/book-cover-review` | `thumbs/`, `preflight.json`, `cover-review.md` |
| `PLATFORM_PACKAGING` | existing `/book-package` | channel packages carrying the cover files |

Everything lands in `projects/<id>/visuals/cover/`, which already exists in the
project structure.

**The ordering constraint that matters**: the print wrap cannot be final until
the page count is final, because the spine width comes from it. Build the cover
brief early for direction, then recompute geometry after the interior is built.
`/book-cover-brief` marks the spec provisional when `page_count_is_final` is
false; `/book-cover-compose` refuses to treat a provisional spec as final.

## 4. Artefacts, approvals and gates

Register each deliverable as the repo already does, so approvals bind to hashes:

```bash
python .claude/scripts/ph_cli.py artifact register <id> \
  projects/<id>/visuals/cover/wrap.pdf --type cover --stage LAYOUT_AND_FORMAT_BUILD \
  --actor cover-typographer --provenance-json '{"model":"flux2-klein-4b","seeds":[...]}'

python .claude/scripts/ph_cli.py audit visuals <id>
python .claude/scripts/ph_cli.py rights check <id>
```

No cover skill grants a gate. The agents recommend a transition; a human runs
`/book-approve-final`. This matches the repo's existing rule that agents may
recommend but never bypass.

**Quality gate mapping.** The cover contributes to the final gate's dimensions:
thumbnail legibility, category fit, hierarchy, craft and series consistency each
at 4.0/5 or better, age fit at 4.5/5 for children's titles, and zero blockers
from `thumbnail_test.py` and `cover_preflight.py`.

## 5. Small edits worth making to existing files

These are the only touch points outside the new files. Each is additive.

- **`.claude/skills/book-visual-bible`** — extend the visual bible to record the
  locked cover look for a series: pack, palette, type zone, font pairing, title
  and author position, spine treatment. Book seven drifts otherwise.
- **`.claude/skills/book-metadata`** — take `title`, `subtitle`, `keywords`,
  `categories` and `ai_disclosure` from `visuals/cover/copy.json` rather than
  rewriting them. A cover/metadata title mismatch is a common rejection cause.
- **`.claude/skills/book-package`** — include the cover deliverable set per
  channel from `cover-channel-specs.md`, and refuse to package when
  `preflight.json` reports blockers.
- **`.claude/skills/book-final-proof`** — add "cover claims verified against the
  built interior" to the checklist.
- **`series/<id>/series.yaml`** — add a `cover_lock` block mirroring the art
  direction section of the brief template.
- **`.claude/config/company.local.json`** — imprint name, default author line,
  default fonts and their licences.

## 6. On marketing and advertising agents

Anthropic does not ship built-in advertising, media, marketing, designer or
publishing agents to reference — Claude Code has general-purpose subagents, and
Anthropic publishes document-format skills (docx, pptx, xlsx, pdf), but nothing
domain-specific to book marketing. Your repo, on the other hand, already has
`/book-marketing`, `/book-ad-creatives`, `/book-tiny-links`, `/book-analytics`
and `ph_cli.py marketing kit`.

So this pack deliberately does **not** add a marketing agent. `cover-copywriter`
produces one copy object — headline, blurb, bullets, keywords, categories — and
your existing marketing and metadata steps consume it. One source of selling
copy, several outputs. Building a second marketing system beside the one you have
would guarantee they disagree.

`front_only.png` is produced at print resolution specifically so the ad-creative
and listing steps have a clean source for mockups, Etsy listing images and social
crops.

## 7. Two things to verify before your first release

**Retailer specs drift.** `cover_channel_specs.json` records the month it was
verified. Re-check before a release batch, and always generate the channel's own
cover template for the exact trim, page count and paper and confirm the wrap
width matches `cover_spec.py`. Public sources disagree about whether KDP's
paperback spine includes a ~0.06 in cover-stock allowance; the default assumes
none, and `--cover-thickness 0.06` is there if your templates say otherwise.

**Klein cannot reach print resolution alone.** It is reliable to about 2 MP; a
300 DPI print front is 3–9 MP. `cover_prompt.py` emits the required upscale
factor and expects a ComfyUI upscale model in the chain. Flat vector and graphic
packs upscale almost perfectly, which is part of why those are the defaults for
activity and puzzle lines. Painted packs need the base variant first and still
lose more. The composer will upscale as a fallback and warn loudly — treat that
warning as a build defect, not a notice.
