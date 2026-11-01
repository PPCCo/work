# `/create-animation` — Implementation Plan for Claude Code

**Audience:** Claude Code, working inside the existing `.claude/` publishing framework (WebSearch is disabled — this document is self-contained).
**Written:** 2026-10-31. Platform specs in §3 were verified against current public sources on this date and are stored as *data* (YAML) so a human can update them without code changes.
**Owner:** Q (Qaiser Abbas). Hardware: MacBook Pro M4, 12-core, 48 GB unified memory, macOS (Apple Silicon).

---

## 0. How to execute this plan (read first)

1. **No web access.** Never try to look anything up. Everything you need is here. When something is unknown (e.g. exact `draw-things-cli` video flags), **probe the local machine** (`--help`, `ffmpeg -h`, `ls`), record what you found in a reference file, and build on that — never guess flags.
2. **Follow existing conventions over this document.** Phase 0 inspects the repo. If the repo already has a convention for skills/agents/rules/standards/workflows/manifests/AskUserQuestion/state machines/commit style, use it, and note each deviation from this plan in `IMPLEMENTATION-NOTES.md`.
3. **Work phase by phase** (§17). Each phase has acceptance criteria. Run tests, commit at each phase boundary, and don't start the next phase until the current one passes.
4. **Deterministic and auditable.** Q's framework philosophy: deterministic state machines, artifact-hash-gated steps, human authorization before anything is published externally. This pipeline **creates files only — it never uploads or publishes anything.**
5. **Token-aware.** Keep `SKILL.md` files lean (<400 lines), push detail into `reference/` files loaded on demand. Images shown to agents are always downscaled contact sheets, never raw frame dumps.
6. **Keep human-editable things human-editable:** platform specs, templates, and recommendation rules are YAML/Markdown, not buried in Python.

---

## 1. Goal and decisions summary

Build a reusable animation pipeline that turns finished artwork (covers, pages, colored counterparts, brand assets) into short promo videos and GIFs for Etsy listings, Instagram, Facebook Ads, and a personal website.

| Decision | Choice | Why |
|---|---|---|
| Timeline engine | **Pure Python/Pillow(+numpy) frame renderer** where every scene is a function of time `t` | Deterministic, testable, templateable, no AI needed |
| Encoder | **FFmpeg** via raw-RGB pipe (PNG-sequence debug mode available) | No intermediate lossy steps; single final H.264 encode |
| Camera moves | Pillow `resize(box=float_box)` straight from the **original** source | Sub-pixel crop = no zoom jitter; single resample = no cumulative softening |
| Transitions | Computed in Pillow (blend/mask/slide) | One engine for everything; FFmpeg `xfade` only used for AI-clip joins if needed |
| Templates | **Declarative YAML** with a `params:` block of human knobs | Easy to edit by hand; validated by schema |
| Platform specs | **YAML data file** (`platform-specs.yaml`) | Update specs without touching code |
| Template selection | **A/B tournament** (automated gates + AI judges + human vote) → freeze 4 finalists per platform | Per Q's requirement |
| AI video (Mode B) | Optional, gated, benchmarked; **background layer only** | Keeps product art crisp; AI video is atmosphere, not the product |
| Audio | None by default (Etsy strips audio anyway); only user-supplied licensed audio | Licensing safety |
| Publishing | Never automated | Human gate |

**Two render modes** (as Q specified):
- **Mode A — Standard:** existing artwork + Pillow + FFmpeg only. Fast, predictable, batchable. Default.
- **Mode B — AI-enhanced:** Draw Things video model generates a short atmospheric clip, composited *behind/before* the real artwork. Only when it adds real value.

**Three use cases** (all served by one skill, §10): (1) step in the book pipeline, (2) standalone `/create-animation`, (3) brand/message ad (e.g. "Smoking is bad for health" with `[Company-ABC]` branding).

---

## 2. Architecture

```
                       ┌──────────────────────────────────────────┐
 Use case 1 (book) ───▶│                                          │
 Use case 2 (args) ───▶│  /create-animation  (SKILL.md)           │
 Use case 3 (brand) ──▶│   intake → brief → director → render →   │
                       │   QA → reviewer loop → deliver           │
                       └───────┬───────────────┬──────────────────┘
                               │               │
              ┌────────────────▼───┐   ┌───────▼─────────────────────┐
              │ Agents             │   │ scripts/animation (Python)  │
              │ animation-director │   │ specs · templates · scenes  │
              │ animation-qc-      │   │ timeline · encode · qa ·    │
              │   reviewer         │   │ contact_sheet · ab · gif    │
              │ animation-ab-judge │   └───────┬─────────────────────┘
              └────────────────────┘           │
                                   ┌───────────▼───────────┐
   Draw Things (stills/AI video) ─▶│ Pillow frames → FFmpeg │──▶ MP4 / GIF / poster / contact sheet / qa.json
                                   └───────────────────────┘
```

State machine per animation job (persisted in `animation-job.json`, hash-gated):

`BRIEF_DRAFT → BRIEF_CONFIRMED → STORYBOARD → DRAFT_RENDER → QC → FINAL_RENDER → QC_FINAL → DELIVERED`

A step is skipped on re-run only if the SHA-256 of its inputs (manifest, template version, platform-spec version, params, source-art hashes) is unchanged.

---

## 3. Platform specs (verified 2026-10-31) — goes into `platform-specs.yaml`

Create `.claude/skills/create-animation/reference/platform-specs.yaml` exactly as below. `reverify_after` is a prompt for a human to re-check; the doctor script warns when it has passed.

```yaml
schema: anim-platform-specs/1
verified: 2026-10-31
reverify_after: 2027-04-30
notes: >
  Specs change. Treat as defaults. Etsy help pages disagree slightly on minimum length
  (3s vs 5s) and videos per listing (1 vs 2) — we design for 5–15s and ONE required video,
  optionally a second.

common:
  container: mp4
  video_codec: h264        # libx264, yuv420p, High profile, +faststart, even dimensions
  fps: 30
  color: bt709

platforms:
  etsy_listing:
    label: "Etsy listing video"
    duration_s: {min: 5, target: 10, max: 15}
    max_file_mb: 100          # we target <= 40
    audio: none               # Etsy strips audio; always encode with -an
    formats: [mp4, mov]
    min_short_edge_px: 500
    ideal_short_edge_px: 1080
    aspect_range: {min: "1:2", max: "2:1"}
    canvases:                 # first entry = default
      - {id: square,    w: 1080, h: 1080, ratio: "1:1",  note: "Recommended default; performs well on mobile + desktop"}
      - {id: landscape, w: 1920, h: 1080, ratio: "16:9", note: "Widescreen alternative"}
      - {id: portrait,  w: 1080, h: 1350, ratio: "4:5",  note: "Vertical alternative"}
    design_notes:
      - "Frame 0 is the poster/thumbnail on many surfaces: it must be a strong, product-clear frame (never black, never a fade-in from black)."
      - "Desktop search results autoplay the video on hover, silently: communicate with visuals + short text only."
      - "Keep key content in the central 80%; thumbnails are cropped."
      - "Up to two videos per listing may be allowed: video 1 = hero promo, video 2 = 'what's inside' detail."
    safe_zone: {top: 0.05, bottom: 0.05, left: 0.05, right: 0.05}

  instagram_reel:
    label: "Instagram Reel / promo (organic)"
    duration_s: {min: 5, target: 12, max: 30}   # platform allows up to 90s; short loops perform best
    max_file_mb: 4096         # we target <= 50
    audio: optional           # AAC if present
    canvases:
      - {id: portrait, w: 1080, h: 1920, ratio: "9:16", note: "Recommended"}
    min_resolution: {w: 720, h: 1280}
    fps_range: [23, 60]
    design_notes:
      - "UI overlays cover the top ~14% and bottom ~35% in Reels: keep text/logos out of those bands."
      - "Hook in the first 1–2 seconds."
    safe_zone: {top: 0.14, bottom: 0.35, left: 0.06, right: 0.06}

  instagram_feed:
    label: "Instagram feed video"
    duration_s: {min: 5, target: 12, max: 30}
    canvases:
      - {id: portrait, w: 1080, h: 1350, ratio: "4:5", note: "Recommended"}
      - {id: square,   w: 1080, h: 1080, ratio: "1:1", note: "Fallback"}
    safe_zone: {top: 0.05, bottom: 0.08, left: 0.05, right: 0.05}

  instagram_story:
    label: "Instagram Story"
    duration_s: {min: 5, target: 10, max: 60}
    canvases:
      - {id: portrait, w: 1080, h: 1920, ratio: "9:16"}
    safe_zone: {top: 0.14, bottom: 0.20, left: 0.06, right: 0.06}

  facebook_feed_ad:
    label: "Facebook feed ad / promo"
    duration_s: {min: 5, target: 15, max: 30}   # ~15s is the commonly cited sweet spot
    max_file_mb: 4096
    formats: [mp4, mov, gif]
    audio: optional
    canvases:
      - {id: portrait, w: 1080, h: 1350, ratio: "4:5", note: "Recommended for mobile feed (Meta suggests 1440x1800 for extra sharpness; 1080 is fine)"}
      - {id: square,   w: 1080, h: 1080, ratio: "1:1", note: "Works across placements"}
    design_notes:
      - "Design sound-off: burn in captions/text; most viewers watch muted."
      - "Hook within the first 3 seconds."
      - "Meta crops when ratio mismatches the placement; export per-placement ratios deliberately."
    safe_zone: {top: 0.06, bottom: 0.10, left: 0.05, right: 0.05}

  facebook_reel_story_ad:
    label: "Facebook Reels / Stories ad"
    duration_s: {min: 5, target: 12, max: 30}
    canvases:
      - {id: portrait, w: 1080, h: 1920, ratio: "9:16"}
    safe_zone: {top: 0.14, bottom: 0.35, left: 0.06, right: 0.06}

  tiktok_in_feed:
    label: "TikTok in-feed"
    duration_s: {min: 5, target: 12, max: 30}
    canvases:
      - {id: portrait, w: 1080, h: 1920, ratio: "9:16"}
    safe_zone: {top: 0.10, bottom: 0.30, left: 0.06, right: 0.12}

  pinterest_video:
    label: "Pinterest video pin"
    status: unverified_from_training_knowledge   # human: verify before relying on it
    duration_s: {min: 4, target: 10, max: 30}
    canvases:
      - {id: portrait, w: 1000, h: 1500, ratio: "2:3"}
    safe_zone: {top: 0.08, bottom: 0.12, left: 0.05, right: 0.05}

  website_loop:
    label: "Website hero / inline loop"
    duration_s: {min: 3, target: 6, max: 12}
    formats: [mp4, webm, gif]
    canvases:
      - {id: landscape, w: 1920, h: 1080, ratio: "16:9"}
      - {id: square,    w: 1080, h: 1080, ratio: "1:1"}
    loop: seamless            # last frame must visually flow into first frame
    audio: none
    safe_zone: {top: 0.05, bottom: 0.05, left: 0.05, right: 0.05}

  gif_social:
    label: "GIF (generic social / email / site)"
    duration_s: {min: 2, target: 5, max: 8}
    formats: [gif]
    gif: {width: 640, fps: 15, max_colors: 128, max_file_mb: 8, loop: 0}
    canvases:
      - {id: square, w: 640, h: 640, ratio: "1:1"}
      - {id: landscape, w: 640, h: 360, ratio: "16:9"}
    safe_zone: {top: 0.04, bottom: 0.04, left: 0.04, right: 0.04}
```

Observation from Q's reference URLs: they contain `du_15` (15 s cap), `q_auto:good` (Etsy re-encodes) and `ac_none` (audio removed). Consequence: don't over-invest in bitrate; **do** invest in clean source frames and avoid fine detail that shimmers under re-compression.

---

## 4. Phase 0 — Repo discovery (do this before writing anything)

Run and record results in `IMPLEMENTATION-NOTES.md`:

```bash
ls -la .claude/ .claude/skills .claude/agents .claude/rules .claude/workflows .claude/standards .claude/scripts 2>/dev/null
claude --version
python3 --version && which ffmpeg ffprobe draw-things-cli parallel caffeinate gifsicle
ffmpeg -hide_banner -version | head -1
ffmpeg -hide_banner -encoders | grep -E "libx264|libvpx-vp9|h264_videotoolbox"
python3 -c "import PIL, sys; print('Pillow', PIL.__version__)"; python3 -c "import numpy, yaml; print('numpy/yaml ok')"
python3 -c "from PIL import features; print('raqm', features.check('raqm'))"
draw-things-cli --help
```

Then answer these questions from the repo itself (grep/Read), and mirror what you find:

1. Where do skills/agents/rules/standards/workflows/scripts live, and what do their frontmatter and naming look like? **Copy the style of one existing skill and one existing agent.**
2. How does the book pipeline represent a finished book (folder layout, manifest/metadata file, page file naming, cover path, series/publisher fields, colored counterparts if any)? Where is the final "book complete" step where the video offer should hook in?
3. How do existing skills call `AskUserQuestion` (option wording, how "Recommended" is expressed)? Match it.
4. Is there a font registry with license info (OFL etc.)? **Use only registered fonts.** If none, create `animation` font list from fonts already used for covers; do not introduce unlicensed fonts.
5. How are `draw-things-cli` calls wrapped today (script, config JSON, output dirs)? Reuse the wrapper for Mode B.
6. Is there a state-machine/hash-gate helper already? Reuse it for `animation-job.json`.
7. Git conventions (branch/commit style), `.gitignore` for large outputs, existing test runner.
8. Does a `settings.json` permission allowlist exist? Add the commands this pipeline needs (`python3 scripts/animation/...`, `ffmpeg`, `ffprobe`, `gifsicle`) in the repo's style.

Create `.claude/skills/create-animation/reference/drawthings-capabilities.md` by running `scripts/animation/probe_drawthings.sh` (written in Phase 0): it dumps `draw-things-cli --help`, every subcommand's `--help`, the model list/dir, and notes which video models (SkyReels-V1, Wan Video, LTX-2.3 22B Distilled 8-bit S) are present and which flags control frames/fps/input-image/seed. **Do not hard-code video flags anywhere until this file exists.**

**Reference videos:** Q's four Etsy example URLs (listed in §19) can't be fetched by the planner. Try `curl -L -o animation-lab/references/ref-N.mp4 <url>`; if the network blocks it, ask Q to drop the files in `animation-lab/references/`. Then run `anim analyze-ref` (§7.9) on each to extract structure (cut times, motion type, pacing, dominant colors) into `reference-analysis.md`. **Take structure and pacing ideas only — never copy any creator's artwork, text or branding** (same principle as Q's cover-art reference mode).

---

## 5. File inventory to create

Adapt directory names to what Phase 0 finds. Defaults:

```
.claude/
├── skills/
│   ├── create-animation/
│   │   ├── SKILL.md                         # entry skill (§10)
│   │   └── reference/
│   │       ├── platform-specs.yaml          # §3
│   │       ├── intake-protocol.md           # AskUserQuestion rounds, gap logic (§10.2)
│   │       ├── recommendation-rules.md      # default-selection table (§10.3)
│   │       ├── template-catalog.md          # archetypes + knobs (§9)
│   │       ├── ffmpeg-recipes.md            # §8 (verbatim commands)
│   │       ├── pillow-recipes.md            # §7 snippets
│   │       ├── qc-checklist.md              # §13 thresholds
│   │       ├── brand-message-ads.md         # use case 3 (§10.5)
│   │       ├── drawthings-capabilities.md   # generated by probe (Phase 0)
│   │       └── template-ranking.json        # produced by A/B (Phase 4)
│   ├── animation-ab-test/SKILL.md           # tournament runner (§14)
│   ├── animation-template/SKILL.md          # create/edit/validate/list templates in plain English
│   └── animation-ai-footage/SKILL.md        # Mode B generation + benchmark (§15)
├── agents/
│   ├── animation-director.md
│   ├── animation-qc-reviewer.md
│   └── animation-ab-judge.md
├── rules/
│   ├── animation-pipeline.md
│   ├── animation-platform-compliance.md
│   ├── animation-ai-footage.md
│   └── animation-brand-ads.md
├── standards/
│   ├── animation-output-standard.md
│   └── animation-template-standard.md
├── workflows/
│   ├── animation-from-book.md               # use case 1 hook (§16)
│   └── animation-ab-selection.md
├── templates/animation/                     # (or wherever templates live; see Phase 0)
│   ├── schema/anim-template.schema.json
│   ├── candidates/*.yaml                    # ~10 archetypes (§9), status: candidate
│   ├── final/<platform>/*.yaml              # 4 per platform, after A/B
│   └── brand-message/*.yaml
└── scripts/animation/                       # Python package + shell helpers (§7)
```

Plus, outside `.claude/`: `animation-lab/` (A/B workspace, `fixtures/`, `references/`, `results/`; heavy renders git-ignored, `results/summary.md` and `template-ranking.json` committed), and `IMPLEMENTATION-NOTES.md`.

---

## 6. Data contracts

### 6.1 Product manifest (`anim-product/1`) — the engine's only view of a product

Built from the book folder by `anim build-manifest <book_dir>` (adapting to the repo's real layout), or passed explicitly. Never hand-written by the engine's scenes.

```json
{
  "schema": "anim-product/1",
  "product_id": "majestic-queen-grayscale-v1",
  "product_type": "coloring_book_grayscale",
  "audience": "adults",
  "title": "Majestic Queens",
  "subtitle": "Grayscale Coloring Book",
  "series": "Royal Portraits",
  "publisher": "PPCCo",
  "headline": "MAJESTIC GRAYSCALE COLORING",
  "page_count": 30,
  "badges": ["INSTANT DOWNLOAD", "30 DESIGNS"],
  "cta": "Download & start coloring today",
  "assets": {
    "cover": "path/cover.png",
    "pages": [
      {"index": 3,  "path": "path/p03.png", "kind": "line_art", "orientation": "portrait", "color_counterpart": "path/p03_color.png"},
      {"index": 8,  "path": "path/p08.png", "kind": "line_art", "orientation": "portrait", "color_counterpart": null}
    ],
    "logo": null
  },
  "theme": {"bg_a": "#1B1030", "bg_b": "#3A1F5C", "accent": "#E8C27A", "text": "#FFFFFF", "font_display": "<registered-font-id>", "font_body": "<registered-font-id>"},
  "brand": {"name": "PPCCo", "logo": null, "claims_allowed": ["INSTANT DOWNLOAD"]},
  "sources": {"manifest_sha256": "<filled by script>", "asset_sha256": {"path/cover.png": "..."}}
}
```

`product_type` enum (extend as the framework grows): `coloring_book_kids`, `coloring_book_grayscale`, `coloring_book_mandala`, `kids_reading`, `storybook`, `illustration_book`, `sketch_collection`, `art_book`, `printable_pack`, `puzzle_book`, `brand_message` (use case 3).

### 6.2 Animation brief (`anim-brief/1`) — the output of intake

```yaml
schema: anim-brief/1
use_case: book_pipeline | standalone | brand_message
product_manifest: path-or-null
platforms: [etsy_listing, instagram_reel]       # one render set per platform+canvas
canvas_overrides: {}                            # e.g. {etsy_listing: landscape}
outputs: [mp4, gif]                             # per platform defaults from specs
template: <template-id>|auto
template_params: {}                             # overrides of template params:
mode: A | B
pages: auto | [3, 8, 14, 22]
copy: {headline: ..., subline: ..., cta: ..., badges: [...]}
audio: {path: null, license: null}
duration_s: auto | 8
brand_message: {topic: ..., audience: ..., tone: ..., facts: [{text:, source:}], logo: path, helpline: null}
review: draft_first | final_only
unresolved: []                                  # must be empty before BRIEF_CONFIRMED
```

### 6.3 Template schema (`anim-template/1`) — human-editable

Constraints: **no code execution in YAML.** Only `{{ref}}` substitution (`book.*`, `param.*`, `theme.*`, `spec.*`) and a `foreach` expansion. Validate with JSON Schema (`schema/anim-template.schema.json`) in `anim template validate`.

```yaml
schema: anim-template/1
id: page-flip-showcase
version: 1.0.0
status: candidate            # candidate | final | retired
name: Page Flip Showcase
family: product-promo        # product-promo | brand-message
archetype: showcase
summary: Title card, N hero pages with soft shadow, branded end card.
platforms: [etsy_listing, instagram_reel, instagram_feed, facebook_feed_ad]
requires: {pages_min: 3}                 # hard requirements; director filters on these
optional_assets: [cover, color_counterpart, logo]
universal: true                          # works with art only (no counterpart/AI)

# ─── HUMAN KNOBS: edit these, nothing else needed ───
params:
  page_indices: auto          # auto = director picks; or [3, 8, 14, 22]
  page_count: 4               # used when page_indices: auto
  hold_s: 1.5                 # seconds each page stays on screen
  transition: crossfade       # crossfade | slide_left | slide_up | wipe | dip_to_color | none
  transition_s: 0.4
  intro_s: 1.6                # 0 = start directly on product (recommended for Etsy)
  outro_s: 2.0
  zoom_in: 1.06               # slow push-in per page (1.0 = none)
  easing: ease_in_out_cubic
  background: {style: radial_gradient, colors: ["{{theme.bg_a}}", "{{theme.bg_b}}"], grain: 0.015}
  shadow: {blur: 28, dx: 0, dy: 18, opacity: 0.35}
  headline: "{{book.headline}}"
  end_card_text: "{{book.page_count}} DESIGNS · INSTANT DOWNLOAD"
  show_logo: false

# duration is derived; engine scales hold_s within fit_to if the total is outside it
fit_to: {min_s: "{{spec.duration_s.min}}", max_s: "{{spec.duration_s.max}}"}

layout:                       # normalized rects in [0,1] of the safe area; per canvas profile
  portrait:  {stage: [0.08, 0.12, 0.84, 0.70], headline: [0.08, 0.04, 0.84, 0.10]}
  square:    {stage: [0.12, 0.10, 0.76, 0.72], headline: [0.10, 0.03, 0.80, 0.08]}
  landscape: {stage: [0.28, 0.08, 0.44, 0.84], headline: [0.05, 0.38, 0.22, 0.24]}

timeline:
  - scene: title_card         # skipped when intro_s == 0
    when: "{{param.intro_s}} > 0"
    duration: "{{param.intro_s}}"
    text: "{{param.headline}}"
    layers: [background]
  - foreach: page_indices
    scene: page_stage
    duration: "{{param.hold_s}}"
    page: "{{item}}"
    zoom: ["1.0", "{{param.zoom_in}}"]
    transition_in: {type: "{{param.transition}}", duration: "{{param.transition_s}}"}
  - scene: end_card
    duration: "{{param.outro_s}}"
    text: "{{param.end_card_text}}"
    show: [cover, badges]
```

Conditions (`when`) accept only: numeric comparisons, `==`/`!=`, `and`/`or`/`not`, and presence tests (`has(asset.cover)`). Implement with a tiny whitelist parser — **no `eval`**.

### 6.4 Run record (`render.json`) written beside every output

Platform, canvas, template id+version, resolved params, spec version, source-art SHA-256s, ffmpeg command, encoder settings, Pillow/ffmpeg versions, render seconds, QA summary, `mode`, any AI-footage provenance (model, seed, prompt, `commercial_rights_verified`).

### 6.5 Output layout (`standards/animation-output-standard.md`)

```
<book_dir>/animation/<platform>/<canvas>/<template-id>/<YYYYMMDD-HHMMSS>-<hash8>/
    <product_id>__<platform>__<canvas>__<template-id>.mp4
    <...>.gif                      # when requested
    poster.jpg                     # frame 0 (or chosen hero frame), for listing thumbnails
    contact_sheet.png              # 8–12 frames, downscaled
    qa.json
    layout_report.json
    render.json
    draft/                         # draft-quality renders, kept until final QC passes
latest -> symlink to newest passing run
```
Never overwrite a prior run; never write into source-art folders.

---

## 7. Script engine design (`scripts/animation/`)

Python ≥ 3.10, venv-local. `requirements.txt`: `pillow>=10.1`, `numpy`, `pyyaml`, `jsonschema`; **optional** `scipy` (only for the stretch `auto-color-fill` scene). No other dependencies.

```
scripts/animation/
├── anim.py                      # CLI entry: python3 scripts/animation/anim.py <cmd>
├── README.md
├── requirements.txt
├── probe_drawthings.sh
├── batch_render.sh              # GNU parallel wrapper, caffeinate -i, --jobs 2 default
├── make_fixtures.py             # synthetic fixture art (no Draw Things needed) for tests/CI
├── anim/
│   ├── cli.py                   # subcommands (below)
│   ├── doctor.py                # environment + spec freshness + font check
│   ├── manifest.py              # build/validate product manifest
│   ├── specs.py                 # load platform-specs.yaml, resolve canvas, safe zones
│   ├── templates.py             # load, schema-validate, substitute, foreach, when
│   ├── timeline.py              # schedule scenes, transitions, fit_to duration scaling
│   ├── easing.py
│   ├── camera.py                # subpixel crop/zoom helpers
│   ├── background.py            # gradients, grain, paper textures
│   ├── text.py                  # fit, wrap, tracking, stroke, contrast, bbox logging
│   ├── fonts.py                 # registry lookup (licensed fonts only)
│   ├── scenes/                  # one file per scene type (registry pattern)
│   │   ├── base.py  title_card.py  page_stage.py  zoom_detail.py  color_reveal.py
│   │   ├── cover_hero.py  grid_build.py  fan_stack.py  split_compare.py
│   │   ├── kinetic_text.py  end_card.py  ai_clip.py  message_stack.py  ink_reveal.py
│   ├── render.py                # frame loop → ffmpeg pipe (multiprocessing, ordered)
│   ├── encode.py                # ffmpeg command builders, size guard, GIF, WebM, audio
│   ├── qa.py                    # ffprobe checks, blackdetect, freezedetect, SSIM, layout
│   ├── contact_sheet.py
│   ├── analyze_ref.py           # reference video structure extraction
│   ├── ab.py                    # job matrix, scoring ingestion, Bradley–Terry, review gallery
│   └── ai_video.py              # Draw Things wrappers (written AFTER the probe)
└── tests/
```

### 7.1 CLI surface

```
anim doctor
anim build-manifest <book_dir> [--out manifest.json]
anim specs list | show <platform>
anim template list|validate|show|params <id>
anim render --manifest M --template T --platform P [--canvas C] [--param k=v ...]
            [--preview] [--scale 0.5] [--seed N] [--frames-dir DIR] [--workers N]
            [--formats mp4,gif] [--audio file --audio-license "..."] [--out DIR]
anim qa <run_dir>
anim contact-sheet <mp4> [--frames 10] [--width 1600]
anim analyze-ref <mp4>
anim ab plan|render|collect|rank|gallery   # §14
anim batch <jobs.yaml>
```
Every command prints machine-readable JSON on stdout (human text on stderr) so agents can parse results.

### 7.2 Scene contract

```python
class Scene:
    type: str                                   # registry key
    def prepare(self, ctx) -> None: ...         # load/resize/cache assets ONCE (per worker)
    def render(self, t: float, ctx) -> Image: ...   # t in [0, duration]; returns RGB at canvas size
    def text_boxes(self, t, ctx) -> list[dict]  # optional: for layout report (bbox, role, color)
```
Transitions are functions `(frame_a, frame_b, p) -> frame` applied over the overlap window of adjacent scenes; the timeline decides which scenes are alive at time `t`. Rendering is a pure function of `(spec, t, seed)` — same inputs, same bytes.

### 7.3 Camera / zoom (the sharpness-critical bit)

```python
from PIL import Image
LANCZOS = Image.Resampling.LANCZOS

def camera_crop(src, out_size, center, zoom, fit="cover"):
    """Single-resample, sub-pixel camera move straight from the ORIGINAL source."""
    W, H = out_size; sw, sh = src.size
    base = max(W / sw, H / sh) if fit == "cover" else min(W / sw, H / sh)
    s = base * zoom                      # output px per source px
    cw, ch = W / s, H / s                # crop size in source px (float!)
    cx, cy = center
    x0 = min(max(cx - cw / 2, 0), max(sw - cw, 0))
    y0 = min(max(cy - ch / 2, 0), max(sh - ch, 0))
    return src.resize((W, H), LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
```
Rules: pass a **float box** to `resize` (avoids integer-crop jitter); never resize an already-resized frame; cap `zoom` so the crop is never smaller than the output (don't upscale past source resolution — if the source is too small, upscale **once** up front with the framework's Draw Things upscaler (Remacri/NMKD per existing tooling notes), not per frame). For "contain" stages (page on background), cache a pre-sized page card per scene and rescale from the original only when zoom ≠ 1.

### 7.4 Reveal / mask / shadow / easing

```python
import numpy as np
from PIL import Image, ImageFilter

def wipe_mask(size, progress, feather=0.08, direction="lr"):
    w, h = size
    x = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    m = np.clip((progress * (1 + feather) - x) / feather, 0, 1)      # 0 at p=0, 1 at p=1
    m = np.broadcast_to(m, (h, w))
    img = Image.fromarray((m * 255).astype("uint8"), "L")
    return img.transpose(Image.FLIP_LEFT_RIGHT) if direction == "rl" else img
# frame = Image.composite(colored, gray, wipe_mask(...))

def drop_shadow(card_rgba, blur=28, dx=0, dy=18, opacity=0.35):
    a = card_rgba.getchannel("A")
    sh = Image.new("RGBA", card_rgba.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * opacity)))
    return sh.filter(ImageFilter.GaussianBlur(blur)), (dx, dy)

def ease_in_out_cubic(p): return 4*p**3 if p < .5 else 1 - (-2*p + 2)**3 / 2
def ease_out_cubic(p):    return 1 - (1 - p)**3
def smoothstep(p):        return p*p*(3 - 2*p)
```
Implement also: `radial_reveal` (circular mask from a seed point — used by `ink_reveal`), `slide`, `dip_to_color`, `card_flip` (horizontal squash of outgoing page to 0, then incoming from 0), `fan` (rotated cards with alpha), `stagger(i, n, overlap)` helper.

### 7.5 Backgrounds, banding, grain

H.264 bands smooth gradients. Build gradients in float32, add **static** low-amplitude noise (σ ≈ 1–2 LSB; one noise tile generated once from the seed and reused every frame — animated grain bloats bitrate), then quantize to uint8. Backgrounds are cached per scene.

### 7.6 Text (`text.py`)

Auto-fit (shrink font until bbox fits the layout rect), wrap by words, optional per-character tracking, outline/stroke, drop shadow, anchor control. Every text draw registers `{role, text, bbox, fg, bg_sample_luma}` for the **layout report** (§13). Use only fonts from the registry (`fonts.py` raises if a font lacks a license record). If `features.check("raqm")` is true, use `ImageFont.Layout.RAQM` for Arabic/complex scripts, else fall back to basic layout and warn (Q has multilingual/Arabic content elsewhere in the framework).

### 7.7 Frame loop and parallelism

```python
# render.py (sketch)
from multiprocessing import Pool
def _init(spec_json): global TL; TL = Timeline.from_json(spec_json); TL.prepare()   # per worker (macOS = spawn)
def _frame(n):        return TL.render(n / FPS).convert("RGB").tobytes()

with Pool(workers, initializer=_init, initargs=(spec_json,)) as pool:
    for buf in pool.imap(_frame, range(n_frames), chunksize=4):   # imap preserves order
        ff.stdin.write(buf)
```
- Default `workers = max(1, cpu_count() - 4)` (leave headroom — Draw Things may be using GPU/RAM). Never run a render batch at the same time as Draw Things image/video generation (§15).
- **Identical-frame dedupe:** if a scene is static for a span, render once and repeat bytes (hold segments are cheap).
- `--frames-dir` writes lossless PNGs instead of piping, for debugging a single frame (`--only-frame N`).
- Dimensions must be even; the engine rounds and logs if a canvas isn't.

### 7.8 Preview / draft mode

`--preview` renders the *canvas scaled by 0.5* (not a post-resize), 15 fps, `-preset veryfast -crf 24` — roughly 6–10× faster. Drafts are for storyboard confirmation and A/B round 1; final output always re-renders from sources at full size.

### 7.9 Reference-video analysis (`analyze_ref.py`)

Using ffprobe/ffmpeg only: duration, fps, resolution; scene cuts via `ffmpeg -i in.mp4 -vf "select='gt(scene,0.30)',showinfo" -f null -` (parse `pts_time`); a contact sheet at 0.5 s steps; dominant colors via Pillow `quantize`; estimated motion type per segment (frame-diff + global-shift heuristic: zoom/pan/static/cut). Output `reference-analysis.md` with a pacing table. The director agent reads the contact sheet visually.

---

## 8. FFmpeg recipes (put verbatim in `reference/ffmpeg-recipes.md`)

**Final MP4 (frames piped as raw RGB):**
```bash
ffmpeg -hide_banner -y -f rawvideo -pix_fmt rgb24 -s ${W}x${H} -r ${FPS} -i - \
  -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" \
  -c:v libx264 -preset slow -crf 17 -profile:v high -level 4.1 -tune animation \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  -g $((FPS*2)) -movflags +faststart -an out.mp4
```
- CRF 16–18 for line art; fine lines are the first casualty of compression. **A/B `-tune animation` vs no tune and CRF 15/17/19** in the Phase 4 lab, on thin-line fixtures.
- Etsy and any platform marked `audio: none` → `-an` always.
- **Size guard:** after encoding, if size > 95% of the platform cap (or > the self-imposed target), re-encode with CRF+2 (max 3 retries). Etsy target ≤ 40 MB (cap 100 MB).
- Drafts: `-preset veryfast -crf 24`.
- Optional fast hardware draft encode: `-c:v h264_videotoolbox -b:v 8M` (never for finals; quality per bit is lower).

**With audio (only when user supplies a licensed track and the platform allows it):**
```bash
ffmpeg -y -i silent.mp4 -i music.mp3 -filter_complex "[1:a]atrim=0:${DUR},afade=t=in:d=0.4,afade=t=out:st=$((DUR-1)):d=1[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest out_with_audio.mp4
```
Stream-copy the video; never re-encode video just to add audio.

**GIF (two-pass palette; crisp for line art):**
```bash
ffmpeg -y -i in.mp4 -vf "fps=15,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=none:diff_mode=rectangle" -loop 0 out.gif
# optional: gifsicle -O3 --lossy=30 out.gif -o out.opt.gif   (if installed)
```
Use `dither=none` for line art/grayscale; try `dither=bayer:bayer_scale=5` for colored artwork. Reduce `fps`, width, or `max_colors` until ≤ the spec's `max_file_mb`.

**WebM loop (website):**
```bash
ffmpeg -y -i in.mp4 -c:v libvpx-vp9 -crf 32 -b:v 0 -row-mt 1 -an out.webm
```

**Poster frame:** `ffmpeg -y -i in.mp4 -vf "select=eq(n\,0)" -frames:v 1 -q:v 2 poster.jpg` (or the chosen hero frame index).

**Probe / validate:**
```bash
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,pix_fmt,duration:format=size,duration -of json out.mp4
ffmpeg -v info -i out.mp4 -vf "blackdetect=d=0.1:pic_th=0.98" -an -f null - 2>&1 | grep black_
ffmpeg -v info -i out.mp4 -vf "freezedetect=n=-60dB:d=1.6" -an -f null - 2>&1 | grep freeze_
ffmpeg -i out.mp4 -i keyframe.png -lavfi "[0:v][1:v]ssim" -f null -        # fidelity (see §13)
```

**AI-clip normalization (Mode B):**
```bash
ffmpeg -y -i ai_raw.mp4 -vf "fps=30,scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},format=yuv420p" -an ai_norm.mp4
# loop by ping-pong: ffmpeg -y -i ai_norm.mp4 -filter_complex "[0:v]split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1[v]" -map "[v]" ai_loop.mp4
# slow-down (e.g. 2x): -vf "setpts=2.0*PTS" ; smooth with minterpolate only if QC shows stutter (slow)
```
The engine reads the normalized clip as a frame source (decoded to raw frames through an ffmpeg pipe) for the `ai_clip` scene, so everything is composited in one timeline.

---

## 9. Template catalog

Create ~10 candidate archetypes plus brand-message ones. **All are candidates until the A/B (§14) freezes four finalists per platform.** The mapping below is a *hypothesis*, not a fixed answer.

| ID | Archetype | What the viewer sees | Needs | Based on |
|---|---|---|---|---|
| `page-flip-showcase` | showcase | (title) → N pages crossfade/slide with shadow → end card | pages ≥3 | Example C+D |
| `zoom-detail-hero` | detail | full page → slow push-in on intricate detail → pull back → title | 1 page (best detail) | Example A |
| `color-reveal-wipe` | transformation | grayscale → colored wipe left→right → title | color counterpart **or** duotone fallback | Example B |
| `cover-spotlight` | premium | dark/cream gradient, cover with soft shadow + gentle parallax, title, badge | cover | Example E |
| `grid-mosaic-build` | abundance | pages pop into a 2×2 / 3×3 grid with stagger, then "30 DESIGNS" | pages ≥4 | new |
| `stack-fan-reveal` | bundle | cover → pages fan out like cards, counter ticks up | cover + pages ≥3 | new |
| `ink-reveal` | craft | line art "draws itself in" via radial/ordered mask; ends full + title | 1 page | new |
| `before-after-split` | transformation | vertical slider sweeps gray ↔ color, then hold | color counterpart or duotone | new |
| `benefit-kinetic-text` | ad | punchy kinetic words ("RELAX · FOCUS · CREATE") over page snippets | pages ≥2 | ad-style |
| `ai-atmosphere-opener` | cinematic (Mode B) | AI mist/particles 0–2 s → cover → pages → end card | AI clip + cover/pages | Q's 8-s fantasy example |
| `message-statement-stack` | brand-message | bold statement → supporting fact (with source line) → brand end card | brand assets | use case 3 |
| `message-visual-metaphor` | brand-message | generated/typographic visual metaphor → statement → CTA + logo | brand assets | use case 3 |

Stretch (Phase 8): `auto-color-fill` — simulate "coloring in progress" by labeling white regions of the line art (`scipy.ndimage.label`), assigning palette colors, and animating region fills in a pleasing order. High marketing value for coloring books; optional because it needs `scipy` and region-quality tuning.

**Shared design rules for all templates** (put in `animation-template-standard.md`):
- Every template declares `params:` (all human knobs), `requires`, `universal`, `layout` for portrait/square/landscape, and `fit_to` from the platform spec.
- Frame 0 must already show product (Etsy poster rule). Templates for Etsy default `intro_s: 0` or a title card that *includes* the artwork.
- Minimum page hold ≥ 1.0 s (buyers must see the page); ≥ 1.4 s recommended.
- On-screen text: ≤ 8 words per card, ≥ 4.5% of canvas height, contrast ≥ 4.5:1, inside the safe zone.
- Typical total text per video ≤ 2 lines headline + 1 end-card line.
- Template files include a `changelog:` list; bump `version` on any edit.
- Brand/theme come from `theme` in the manifest; never hard-code colors in a template except as fallbacks.

**Platform-fit hypotheses (to be tested, not assumed):**
- *Etsy listing:* showcase, detail, transformation (color reveal), premium/bundle. Silent; first frame = product; 8–12 s.
- *Instagram promo (9:16):* hook-heavy — ink-reveal, kinetic text, color reveal, fan reveal; 8–12 s; text outside top 14% / bottom 35%.
- *Facebook ad (4:5 / 1:1):* sound-off clarity, benefit text, strong CTA end card, first 3 s hook; 12–15 s.
- *Website loop / GIF:* cover-spotlight, ink-reveal, before-after (seamless loop); small file size.

---

## 10. Skills

### 10.1 `/create-animation` — `SKILL.md` content

Adapt frontmatter to the repo's existing skills (Phase 0). Intended shape:

```markdown
---
name: create-animation
description: Create promo videos/GIFs (Etsy listing, Instagram, Facebook ads, website) from book artwork or a brand message, using Pillow + FFmpeg templates, with optional AI-generated atmosphere. Use after a book is finished, or on request, or for brand message ads.
argument-hint: "[free-text brief, e.g. 'etsy video for books/queens, color reveal, 10s'] [--from-manifest path] [--platforms a,b] [--template id]"
---
# /create-animation

Arguments: $ARGUMENTS

## Procedure
1. **Detect use case** from context: invoked by the book pipeline (manifest path or `--from-manifest`) → `book_pipeline`; free text/standalone → `standalone`; message/brand text without product art ("ad for X with [Brand]") → `brand_message`.
2. **Parse ARGUMENTS into an `anim-brief/1` draft.** Resolve everything you can from the manifest, arguments, and repo context. Anything unresolved goes in `unresolved`.
3. **Run `anim doctor`.** Stop with a clear fix list if ffmpeg/libx264/Pillow/fonts are missing.
4. **Intake** per `reference/intake-protocol.md`: ask ONLY about `unresolved` items via AskUserQuestion; max 4 questions per call; 2–4 options; the Recommended option FIRST, labelled "(Recommended)"; compute recommendations from `reference/recommendation-rules.md` and `template-ranking.json` (if present).
5. **Select pages/assets** (director agent): view a downscaled contact sheet of candidate pages, choose the most visually distinct/high-detail pages, record indices in the brief.
6. **Storyboard** (director agent): short shot list with timings and exact on-screen copy; show it to the user only when `review: draft_first` or the use case is `brand_message`.
7. **Draft render** (`anim render --preview`), then QC agent on the contact sheet + `qa.json`. Loop at most 2 revisions (apply param patches only).
8. **Final render** for each platform × canvas × format; run `anim qa`; QC agent verdict.
9. **Deliver**: print paths, durations, sizes, QA summary, and what was NOT done (no upload). Update `animation-job.json`.

## Hard rules
(see .claude/rules/animation-*.md — load them; do not restate here)
```
Keep the body lean; details live in `reference/`.

### 10.2 Intake protocol (`reference/intake-protocol.md`)

**Principles:** Ask only what can't be inferred. Batch related questions (≤4). Always list a Recommended option first. Users can always type "Other". In `book_pipeline` mode, product facts come from the manifest, so ask about *video intent*, not about images.

**Round 1 — Intent** (skip anything already given):

| Question | Options (first = Recommended, rule-driven) |
|---|---|
| Which video(s) do you need? (multiSelect) | Etsy listing video · Instagram promo (Reel) · Facebook ad · Website loop / GIF |
| Output formats? | MP4 only (Rec. for Etsy/IG/FB) · MP4 + GIF · GIF only |
| Mode? | Standard (art only) (Rec.) · AI-enhanced atmosphere (only offered if AI video capability + rights flags are OK and product type benefits) |
| Source art? (standalone only) | Use latest finished book (Rec. if one is detected) · Pick a folder/book · I'll paste image paths |

**Round 2 — Look & content:**

| Question | Options |
|---|---|
| Template? (filtered by platform, `requires`, and ranking) | 4 finalist templates, best-ranked first (Rec.), each with a one-line description |
| Which pages? | Let the agent pick the most distinct pages (Rec.) · Evenly spaced · I'll give page numbers |
| On-screen copy? | Generate from book metadata (Rec.) · I'll write it · No text |
| Duration? | Platform default (Rec.) · Shorter · Longer |

**Round 3 — Confirmation:** summarize the brief in ≤10 lines. Options: "Render draft first (Rec.)", "Render final now", "Change something". In batch/pipeline automation, `--yes` accepts all Recommended answers.

**Gap-only mode:** if ARGUMENTS fully specify the brief, ask nothing except Round 3 (or nothing with `--yes`).

### 10.3 Recommendation rules (`reference/recommendation-rules.md`)

A table the skill consults to pick the "(Recommended)" option. Initial rules (superseded per platform×product_type by `template-ranking.json` after A/B):

| Condition | Recommend |
|---|---|
| Platform = etsy_listing & universal needed | `page-flip-showcase` |
| Has color counterpart for ≥1 selected page | add `color-reveal-wipe` as top alternative |
| Product = mandala | `zoom-detail-hero` / `ink-reveal` |
| Product = storybook / kids reading | `stack-fan-reveal` / `page-flip-showcase` |
| Platform = instagram_reel | hook-first templates (`ink-reveal`, `benefit-kinetic-text`) |
| Platform = facebook_feed_ad | clarity + CTA templates (`benefit-kinetic-text`, `page-flip-showcase`) |
| Mode B offered only if | AI capability probed OK **and** a model has `commercial_rights_verified: true` **and** product type ∈ {fantasy/atmospheric genres} |
| Audio | Default none; offer only for IG/FB when user supplies a licensed file |

### 10.4 Use case 1 — inside the book pipeline

Add a final optional gate to the book workflow (see §16): after the book is complete and its manifest is written, the publishing agent asks (AskUserQuestion, multiSelect): *"Create promo animation(s) for this book?"* → options: **Etsy listing video (Recommended)**, Instagram promo, Facebook ad, GIF/website loop, **Not now**. On any selection it invokes `/create-animation --from-manifest <path> --platforms <list>`. The skill then asks only Round 2/3 items (template, pages, copy) unless `--yes`.

### 10.5 Use case 3 — brand message ad (`reference/brand-message-ads.md`)

Example input: `"show an ad for 'Smoking is bad for health' with [Company-ABC] branding"`.

Flow:
1. Classify as `brand_message`; draft brief with `topic`, `brand = Company-ABC`.
2. Ask about gaps (AskUserQuestion), with Recommended options:
   - **Platform & ratio** (IG Reel 9:16 Rec. / FB feed 4:5 / both).
   - **Brand assets:** logo file path, brand colors, approved font (if none supplied: neutral palette + registered font; flag as placeholder).
   - **Tone:** Informative & calm (Rec.) · Hard-hitting · Hopeful/quit-focused.
   - **Facts:** *Do you have a statistic or message to include, and its source?* Options: "Use message only, no statistics (Rec.)" · "I'll supply facts + sources" . **Never invent statistics, studies or quotes.** Without a supplied source, use non-quantified statements only.
   - **Call to action / support line:** supply a helpline or URL (Rec.), or none. Do not invent phone numbers. (For Australia an official quit-support line exists — ask Q to supply the exact current number rather than relying on memory.)
   - **Imagery:** typographic only (Rec.) · generated illustration via Draw Things (stills) · user-supplied images.
3. Template: `message-statement-stack` or `message-visual-metaphor`; 9–15 s; sound-off with burned-in captions.
4. Always `review: draft_first`. Show storyboard + draft; final only on approval.
5. Compliance flags (see `animation-brand-ads.md`): health claims need substantiation; ads about social issues/public health may fall under platform "social issue" ad authorization and AI-disclosure rules on Meta — **flag to user, don't assume**; no depiction of minors smoking; no real people's likenesses; no real third-party brand/trademark imagery (e.g. actual cigarette brands); logos only as supplied.

### 10.6 `/animation-template` skill

Natural-language template maintenance: "make a copy of page-flip-showcase with 5 pages, 1 s each, slide-left transitions" → copies to a new id, edits `params:`, bumps version, runs `anim template validate`, renders a one-frame preview. Also `list` (shows id, status, platforms, requires) and `show-params`. Humans can also edit YAML directly; `anim template validate` is the safety net.

### 10.7 `/animation-ab-test` skill — see §14. `/animation-ai-footage` — see §15.

---

## 11. Agents

Match the repo's agent frontmatter. Model suggestions are defaults — make them configurable and note cost: use the cheaper model class for bulk screening, the strongest for finals and creative direction.

**`animation-director`** (strongest model; read-only + Bash for `anim` commands)
- Inputs: brief draft, manifest, `template-catalog.md`, `template-ranking.json`, `reference-analysis.md` (if present), contact sheets of candidate pages.
- Duties: choose template; choose pages (distinct composition, high detail, not near-duplicates, crisp at output size); write copy within limits (≤8 words/card; use metadata; no unsubstantiated claims; platform-appropriate tone); set `params` overrides; produce a storyboard (timings + copy); explain recommendations in one line each for AskUserQuestion options.
- Output: updated `anim-brief/1` + storyboard markdown. Never invents assets.

**`animation-qc-reviewer`** (mid-tier model; vision)
- Inputs: `contact_sheet.png` (+ optional motion strip at 0.25 s), `qa.json`, `layout_report.json`, the brief.
- Checks (rubric in `qc-checklist.md`): product clarity, crispness, text legibility/safe zones, pacing/holds, motion plausibility (from strips), first-frame strength, artifact spotting (distorted line art, ghosting, AI-clip weirdness), brand/claims issues.
- Output JSON: `{verdict: pass|revise|fail, issues: [...], param_patch: {...}}`. Only `params` patches — never code changes. Max 2 revision loops per job.

**`animation-ab-judge`** (see §14): blind, rubric-based scorer; sees anonymized IDs only; returns structured scores + a one-line justification per criterion; never sees template names or other judges' scores.

---

## 12. Rules and standards (content to write)

**`rules/animation-pipeline.md`** — MUST/NEVER list:
- Source art is read-only; work on copies; outputs only under the run folder; never overwrite prior runs.
- One final encode: no encode→decode→re-encode chains, no repeated resizes; all geometry derives from the original source via a single resample.
- Use `anim` scripts for rendering; do not hand-run ad-hoc ffmpeg for finals (drafts for debugging are fine).
- Even dimensions, yuv420p, H.264 High, `+faststart`, BT.709 tags; `-an` for `audio: none` platforms.
- Resolve canvas/duration/safe zones from `platform-specs.yaml`; never hard-code.
- Deterministic: seed everything; record seeds in `render.json`.
- Fonts: registry only; log font ids.
- No uploads, no posting, no external API calls; human gate stays outside this pipeline.
- Do not run renders concurrently with Draw Things generation.
- If `platform-specs.yaml` is past `reverify_after`, warn in the final summary.

**`rules/animation-platform-compliance.md`**:
- Etsy: 5–15 s, ≤100 MB, silent, frame 0 = product, no misleading depiction (the video must show what's actually sold), no third-party IP/characters/trademarks.
- Meta/IG: sound-off design, captions burned in, safe-zone compliance, no before/after claims that misrepresent the product, no unsubstantiated health/financial claims.
- Audio: none unless user supplies a track **and** a license note; never use random "royalty-free" assumptions; record license in `render.json`.
- AI-generated imagery/video in ads: flag that platforms may require an AI-content disclosure label for realistic synthetic media in some ad categories — surface this to the user at delivery time as a checklist item.
- Product honesty: the artwork shown must be the product (real pages/covers). AI atmosphere cannot depict features the product lacks.

**`rules/animation-ai-footage.md`** — §15 gating rules.

**`rules/animation-brand-ads.md`** — §10.5 compliance list: no fabricated statistics/quotes/endorsements; sourced facts only (source line on screen or in the description); no real-person likeness; no real tobacco/alcohol/pharma brand marks; no minors in harmful depictions; logos only from supplied files; always draft-first; flag possible platform ad-category authorization requirements to the user.

**`standards/animation-output-standard.md`** — §6.4/§6.5 content (layout, naming, run record, poster, contact sheet, QA files, retention: keep final + draft of latest run, prune older drafts).
**`standards/animation-template-standard.md`** — §6.3 schema rules, §9 shared design rules, versioning, `status` lifecycle `candidate → final → retired`, change-log requirement, "no code in templates".

If the repo scopes rules by path (frontmatter `paths:`), scope these to `scripts/animation/**`, `templates/animation/**`, and `**/animation/**`.

---

## 13. QA and QC

**Automated hard gates (`anim qa`; any failure = job fails, no delivery):**
- ffprobe: codec h264, `yuv420p`, even dimensions, resolution == canvas, fps ≈ target, duration within the spec's `min..max`, file size ≤ cap (and ≤ our lower target), audio stream absent where `audio: none`.
- Frame 0: not near-black (mean luma > 20) and has content (luma std-dev > threshold).
- `blackdetect`: no black runs > 0.1 s (except where the template declares them).
- `freezedetect`: no unintended freeze longer than the template's `max_hold_s` (a deliberate hold is OK; compare against the timeline schedule).
- Fidelity: for each *hold* keyframe, render the engine's reference PNG and compare to the decoded MP4 frame with SSIM; **≥ 0.97** (line-art sensitive). Below that → raise bitrate/CRF down and re-encode, else fail.
- Safe zone: no text/logo bbox outside the platform's `safe_zone`.
- Text: min height ≥ 4.5% of canvas height (≥ 5% for 9:16), contrast ≥ 4.5:1 against sampled background, word count per card ≤ 8.
- Loop gate (loop-type outputs): SSIM(last frame, first frame) ≥ 0.9 or crossfade-loop flag.
- GIF: ≤ `max_file_mb`, width/fps per spec.

**Warnings (reported, not failing):** scene hold < 1.2 s, dense on-screen text, high frame-to-frame luma flicker in static holds (compression shimmer), render time anomalies, spec file past `reverify_after`.

**Visual QC (agent):** contact sheet (10 frames at even spacing + the first frame at large size) and a motion strip (frames every 0.25 s around transitions). Reviewer looks for what numbers can't: composition, taste, artifacts. Verdict loop capped at 2.

**Line-art shimmer note:** fine 1-px lines moving sub-pixel can crawl/shimmer after H.264 and after Etsy/Meta re-encode. Mitigations to test in the lab: slower/eased zooms, slightly heavier line weight in the output scale (render art at 1.0× only, no unsharp), larger canvas supersample then downscale, CRF 15–17, `-tune animation`, avoiding long slow zooms on the densest pages (use holds + cuts instead).

---

## 14. A/B selection — choosing the four final templates per platform

**Be honest about what this is:** an *offline* tournament (objective gates + AI judges + Q's taste) that picks the best candidates *before* launch. Real buyer behavior can only be measured live (Phase 8). AI judges can't "watch" video; they score sampled frames + objective motion metrics. Q's vote is the final authority.

### 14.1 Setup (`animation-lab/`)

**Fixtures (≥ 6, covering the catalog):**
1. Grayscale portrait page set (the "majestic queen" book), with colored counterparts for ≥3 pages
2. Mandala set (square, very fine detail)
3. Kids coloring (bold lines, portrait)
4. Kids storybook / illustration (full-color, landscape spreads)
5. Sketch/art collection (grayscale/painting, landscape + portrait mix)
6. Digital-download printable page set (A4/Letter portrait)

Use real finished books from the repo outputs (copy, don't move). Where none exist, generate small sets via the existing draw-things-cli wrapper (4–6 pages each) — or use `make_fixtures.py` synthetic art for harness testing only (never for judging taste).

**Candidate pool:** every template in §9 marked as compatible with the platform (~10 per platform; `requires` filter applies per fixture).
**Platforms in the tournament:** `etsy_listing`, `instagram_reel`, `facebook_feed_ad`, `website_loop` (the GIF set derives from website_loop winners). Brand-message templates get a lighter 2-candidate check on IG/FB.

### 14.2 Rounds

1. **Smoke & gates (automatic):** render all candidates × fixtures at draft quality. Drop any candidate that fails hard gates on >1 fixture; record why.
2. **Round 1 — screen (pointwise AI scoring):** per video, build the contact sheet + motion strip + metrics; `animation-ab-judge` scores 1–5 on the rubric below, in batches (several videos per call, randomized order, anonymized IDs). Aggregate per candidate (mean, min, agreement). Keep the top 6 per platform.
3. **Round 2 — tuned finals (full res + parameter A/B):** for each of the top 6, test **one factor at a time** against its default, using pairwise judging with position swap (each pair judged twice, A/B swapped; accept only if both agree, else call it a tie):
   - `hold_s` 1.0 / 1.5 / 2.0
   - `transition` crossfade vs slide vs none, `transition_s` 0.3 / 0.5
   - `zoom_in` 1.0 / 1.06 / 1.15
   - background dark vs light vs theme gradient
   - intro title card vs none (Etsy: product-first)
   - encoder: CRF 15/17/19 × `-tune animation` on/off (objective: SSIM + file size, no judge needed)
   Adopt winning params as the template's tuned defaults (bump version, changelog).
4. **Round 3 — human vote:** `anim ab gallery` creates a local `review.html` (no external assets): side-by-side `<video>` players per platform, autoplay muted, keyboard shortcuts to rank/reject, writes `human-votes.json` (download button; no server needed). Q ranks the top 6 per platform and optionally comments.
5. **Selection with diversity constraint:** final four = highest combined rank (AI 40% / human 60%) **subject to**: ≥1 *universal* template (works with art only); ≥1 *transformation* archetype *or* a duotone-fallback-capable one; no two finalists of the same archetype; at least one with strong first-frame (Etsy poster rule). Document exclusions and why.
6. **Freeze:** set `status: final`, write `final/<platform>/`, produce `template-ranking.json` (per platform × product_type ranking with scores and the recommended default), update `recommendation-rules.md`, and write `animation-lab/results/summary.md` (method, scores, decisions, known weaknesses). Previously-rejected candidates → `status: retired` (kept for history).

### 14.3 Judge rubric (`animation-ab-judge.md`)

Score 1–5 each, with one-sentence evidence per criterion: **(1) First-frame/hook strength · (2) Product clarity (artwork visible, crisp, prominent) · (3) Text legibility & restraint · (4) Pacing (enough time to see pages; no rush/drag) · (5) Visual polish (composition, background, shadows, consistency) · (6) Persuasion for the platform (would a buyer understand what they get?) · (7) Artifact/risks (ghosting, distortions, misleading depiction)**. Weights default: 1:20%, 2:25%, 3:10%, 4:15%, 5:15%, 6:10%, 7:5% (configurable). The judge gets anonymous IDs, the platform, the fixture's product description, and objective metrics — never template names.

**Bias controls:** randomized order and labels; position swapping in pairwise rounds; ≥2 independent judge instances on finals with agreement reported (Cohen's κ or simple % agreement); lower-confidence results flagged for human attention; no judge sees another's scores.

**Token budget guidance:** pointwise screening in batches, contact sheets ≤1600 px wide, finals only get pairwise passes. Target ≤ ~250 judge calls for the whole tournament; report actual usage in `summary.md`. Wrap long runs in `caffeinate -i`.

### 14.4 Ranking math (`ab.py`)

Pointwise: weighted mean + variance. Pairwise: Bradley–Terry via simple iterative MM updates (≈30 lines, no deps); ties count as half-wins. Final combined score = 0.4·z(AI) + 0.6·z(human).

### 14.5 Reproducibility

`anim ab plan` emits `jobs.yaml` (candidate × fixture × platform × params × seed); `anim ab render` executes it via `batch_render.sh` (default 2 jobs in parallel, workers per job reduced accordingly); results in `animation-lab/results/<date>/` with a hash manifest.

---

## 15. Mode B — AI-enhanced footage (Draw Things video)

Installed video models (per Q): **SkyReels-V1, Wan Video, LTX-2.3 22B Distilled (8-bit S)**. Keep this stage optional and gated.

**Gate 0 — capability probe (Phase 0 output):** `drawthings-capabilities.md` lists how the CLI generates video (text-to-video / image-to-video), frame-count and fps controls, seed, and output format. If the CLI lacks video support, Mode B is **disabled** and the skill says so (do not invent a workaround without telling Q).

**Gate 1 — rights flag:** each model gets `commercial_rights_verified: true|false` in a small registry (same pattern the book framework already uses for image models). Default **false** for all three until Q verifies each model's license for commercial use (license terms for video models vary — and some have territorial or revenue conditions — so this must be checked against the actual license text by Q, not assumed). The AI-footage skill refuses to produce footage for a *sold* deliverable from a model with `false`. Experiments for A/B/benchmark stay local and clearly marked "NOT FOR USE".

**Gate 2 — benchmark (`anim ai-bench`, runs once per model):** with a fixed prompt set (misty fantasy atmosphere, floating particles, drifting clouds, soft light rays, abstract ink flow), record per model: peak memory (`/usr/bin/time -l`), wall time per clip, clip length/fps/resolution achievable, flicker (frame-diff stats), temporal morphing (visual review), text/face artifacts, loop-ability. Write `animation-lab/results/ai-bench.md`; choose the default model; record limits. Test on the M4 48 GB **before** any production use; the 22B model may need smaller resolution/frames.

**Gate 3 — production constraints:**
- Footage is **background atmosphere only**: darkened/blurred/vignetted behind the real artwork or as a 1–2.5 s opener; never replace or alter the product pages/cover.
- Prompts: no text, no logos, no recognizable people/characters, no depictions of product features; style words only ("slow drifting mist, soft particles, deep purple, cinematic, subtle motion").
- Prefer text-to-video or image-to-video from a **background-only still** (not from the cover/pages — i2v warps fine line art).
- Normalize (§8), loop (ping-pong or crossfade), then ingest as an `ai_clip` layer.
- AI QC: flicker metric + visual review of the motion strip; reject on morphing, banding, or anything distracting.
- Never run concurrently with image generation or batch rendering; use `caffeinate -i`; cap clip length (≈2–5 s) and reuse clips across products of the same genre (a small library: `animation-lab/ai-footage-library/` with prompt, seed, model, rights flag).
- Log everything in `render.json`.

---

## 16. Integration with the book pipeline (use case 1)

`workflows/animation-from-book.md`:
1. After the book reaches its "complete" state and the manifest is final, the publishing agent runs `anim build-manifest <book_dir>` (add the adapter for the repo's real layout), writing `manifest.json` beside the book (hash-recorded in the book's state).
2. Offer gate (AskUserQuestion, see §10.4). "Not now" is a valid terminal state and is recorded so the offer isn't repeated each run.
3. On accept → `/create-animation --from-manifest … --platforms …`.
4. Output is attached to the book's `animation/` folder; the book's listing-assets checklist gains "promo video created (Y/N)" with paths. **Uploading stays manual** (human authorization checkpoint).
5. Hash gating: if cover/pages change after videos exist, mark videos `STALE` (manifest hash mismatch) and offer a re-render.

Also add a batch entry (`anim batch jobs.yaml`) for catalog-wide renders across hundreds of products: skip unchanged hashes, `--jobs 2`, resumable, summary CSV (product, platform, template, status, size, duration, qa).

---

## 17. Phases and acceptance criteria

| Phase | Deliverables | Acceptance |
|---|---|---|
| **0. Discovery & doctor** | `IMPLEMENTATION-NOTES.md`; `doctor.py`; `probe_drawthings.sh` + `drawthings-capabilities.md`; `platform-specs.yaml`; reference downloads/analysis | `anim doctor` green (ffmpeg+libx264, Pillow, numpy, yaml, fonts); capabilities file exists; conventions documented |
| **1. Core engine MVP** | specs/templates loader, timeline, camera/easing/background/text, scenes: `title_card`, `page_stage`, `end_card`, `zoom_detail`; render→ffmpeg pipe; encode+size guard; contact sheet; `qa.py` gates; `make_fixtures.py`; tests | One synthetic-fixture Etsy MP4 (1080×1080, ≈10 s) passes all hard gates; re-render is byte-identical (same seed); unit tests green; frame 0 is product |
| **2. Scenes + candidate templates** | remaining scenes (`color_reveal`, `cover_hero`, `grid_build`, `fan_stack`, `split_compare`, `kinetic_text`, `ink_reveal`, `message_stack`) ; ~10 candidate YAMLs + schema; `anim template validate/list` | Every candidate renders on every compatible synthetic fixture for all platform canvases without error; schema validation passes; portrait/square/landscape layouts verified by layout report |
| **3. Skill, intake, agents, rules, standards** | `create-animation` SKILL + reference files, 3 agents, 4 rules, 2 standards, `/animation-template` | Dry-run of all three use cases (book pipeline manifest, free-text args, "Smoking is bad for health" + `[Company-ABC]`) asks only gap questions, each with a Recommended first option, and produces a confirmed brief + draft render |
| **4. A/B lab & freeze** | fixtures, `ab.py`, gallery, `animation-ab-test` skill, judge agent; run rounds 1–3; freeze finals; `template-ranking.json`; `results/summary.md` | 4 finals per platform with documented scores, diversity constraint satisfied, human votes recorded, tuned defaults committed |
| **5. Pipeline integration** | `animation-from-book.md`, manifest adapter, offer gate, STALE handling, `batch` | End-to-end on one real book: finish → offer → Etsy MP4 + poster + GIF delivered into the book's `animation/` folder; nothing uploaded |
| **6. Mode B (AI footage)** | `animation-ai-footage` skill, `ai_video.py`, bench, rights registry, `ai-atmosphere-opener` | Bench report complete; at least one verified-rights model (or Mode B explicitly disabled with reason); a QC-passing 8-s AI-enhanced promo on a fantasy fixture |
| **7. Brand-message hardening** | brand templates finalized, compliance checklist at delivery, source-line support | "Smoking is bad for health" + `[Company-ABC]` produces a draft-first, sourced-or-unquantified, sound-off 9:16 and 4:5 ad with delivery checklist |
| **8. Optional/stretch** | `auto-color-fill`, live-performance log, spec re-verification reminder, library of AI footage | Documented; not blocking |

**Live validation (post-launch, optional):** can't be randomized inside an Etsy listing. Use sequential windows (e.g. 14 days per variant across comparable listings) and compare Etsy Stats (views→visits→favorites→orders); for Facebook use Meta's built-in A/B test on creatives. Log to `animation-lab/results/live-performance.csv`; feed learnings back into `template-ranking.json`.

---

## 18. Testing

- **Unit:** easing curves (monotonic, endpoints), `camera_crop` bounds/zoom cap, wipe mask endpoints (0 → all-gray, 1 → all-color), template substitution/`foreach`/`when` parser (incl. rejection of anything not whitelisted), spec resolution (canvas, safe zones), duration fitting, text fit, manifest validation.
- **Golden frames:** for each scene at fixed `t` and seed, compare to stored PNG with a small tolerance (guards against accidental visual regressions).
- **Smoke matrix:** every template × {square, portrait, landscape} on synthetic fixtures, preview mode, in CI/pytest (`-m smoke`).
- **Determinism:** same inputs → identical frame hashes and mp4 stream hash (modulo container metadata).
- **Encode tests:** ffprobe assertions; size-guard path forced by a tiny cap; GIF palette path; `-an` for Etsy.
- **QA tests:** deliberately broken videos (black first frame, oversized, wrong ratio, audio present) must fail the right gate.
- **No network, no Draw Things** in tests; Mode B tests use a stub generator.

---

## 19. Risks, assumptions, open questions

**Reference URLs from Q (for structural analysis; do not copy content):**
```
https://v.etsystatic.com/c/video/upload/ac_none,du_15,q_auto:good/gzxvrj5syfqfonh0qqzl.mp4
https://v.etsystatic.com/c/video/upload/ac_none,du_15,q_auto:good/Majestic_Rivers_Etsy_fzlx33.mp4
https://v.etsystatic.com/c/video/upload/ac_none,du_15,q_auto:good/0119_vcoatd.mp4
https://v.etsystatic.com/c/video/upload/ac_none,du_15,q_auto:good/0119_1_qyjdoj.mp4
```

| Risk | Mitigation |
|---|---|
| Spec drift (Etsy/Meta change rules) | Specs are data with `verified`/`reverify_after`; doctor warns |
| Fine line art shimmers after re-encode | CRF 15–17, tune A/B, ease/hold instead of long creeping zoom; QC strips |
| Draw Things video flags unknown | Probe first; Mode B disabled if unsupported |
| Video-model licenses unclear | `commercial_rights_verified` gate, default false; Q verifies |
| AI judges can't see motion | Motion strips + objective metrics; human vote has 60% weight |
| Memory/time contention with image generation | Never run concurrently; worker cap; `caffeinate -i` |
| Over-claiming in ads (use case 3) | No invented stats/quotes; source line; draft-first; compliance checklist |
| Template sprawl | Only 4 finals per platform exposed; others `candidate`/`retired` |

**Assumptions (change if wrong):** Python 3.10+ available; Homebrew ffmpeg includes libx264; the repo has (or can get) a font registry with license data; the book pipeline has a discoverable "book complete" step; Etsy square (1080×1080) is the default canvas.

**Open questions for Q (non-blocking — defaults chosen):**
1. Default Etsy canvas: square 1080×1080 (chosen) vs 16:9 vs 4:5?
2. Should video 2 on Etsy ("what's inside") be generated automatically alongside video 1? (Default: offer, not auto.)
3. Brand-message ads: which fonts/colors/logo for `[Company-ABC]` placeholders, and any official helpline/URL to show?
4. Which of the three AI video models do you want benchmarked first? (Default: all three, smallest first.)
5. Are any music tracks you own/licensed available for IG/FB variants? (Default: silent.)

---

## 20. Definition of done

- `/create-animation` works in all three use cases, asks only for gaps, always lists a Recommended option first.
- Four final templates per platform, chosen via the documented A/B process, with human-editable `params:`.
- Mode A produces QA-passing MP4 (+GIF/poster/contact sheet) deterministically; Mode B is either working under all gates or explicitly disabled.
- All rules/standards/agents/skills/scripts above exist, follow repo conventions, and are covered by tests.
- Nothing is ever uploaded or published automatically; spec freshness and rights flags are visible in every delivery summary.
