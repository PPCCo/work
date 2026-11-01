# AI Animation Generator — Implementation Blueprint

**Target:** Existing Claude Code / Claude Agentic publishing framework  
**Command:** `/create-animation`  
**Snapshot date for platform specifications:** 31 October 2026  
**Primary stack:** Python 3 + Pillow + FFmpeg/FFprobe  
**Optional AI video provider:** Draw Things (capability-detected; do not assume a video CLI command exists)

---

## 0. Executive direction

Build a reusable **animation production subsystem**, not a set of one-off video scripts. It must serve every publishing category and also support generic branded campaigns and public-service announcements.

The subsystem has five separate responsibilities:

1. **Creative direction:** Claude decides the communication objective, audience, product story, tone, and suitable creative approach.
2. **Storyboard and template:** Claude produces a validated, data-driven scene/timeline specification.
3. **Asset preparation:** Python/Pillow prepares layouts, composites, masks, crops, backgrounds, text, shadows, page mockups, and still frames.
4. **Motion and delivery:** FFmpeg composes motion, transitions, sound, and output encoding; FFprobe validates the result.
5. **Optional AI footage:** A provider adapter may request short atmospheric clips from Draw Things, but AI video is never a mandatory dependency.

**Non-negotiable architecture rule:** templates must not contain hardcoded FFmpeg command strings. A template produces a platform-neutral storyboard; renderers interpret that storyboard. A platform profile determines dimensions, duration limits, safe zones, codecs, audio policy, and file-size constraints.

This separation allows the same `page_gallery` template to create an Etsy silent listing video, a vertical Instagram Reel, and a Facebook Feed ad without duplicating the rendering engine.

### Recommended implementation decisions

| Area | Decision |
|---|---|
| Standard renderer | Python + Pillow + FFmpeg |
| AI image source | Existing Draw Things Qwen / FLUX workflows and existing publishing assets |
| AI video | Optional provider adapter; disabled by default |
| Creative definition | JSON storyboard / scene schema |
| Platform rules | Versioned YAML profiles, with `verified_on` and source URLs |
| Templates | Reusable declarative templates + small Python effect implementations |
| User customization | Editable job JSON/YAML and CLI overrides |
| Main export | MP4 / H.264 |
| Optional exports | GIF, WebM, still thumbnails/contact sheets, SRT captions |
| QA | Programmatic checks + contact sheet + human approval gate |
| Experimentation | Versioned creative variants and measured results |
| Batch execution | Resumable jobs with stage manifests and asset hashes |

---

## 1. Platform output profiles (snapshot: 31 October 2026)

Treat these as **versioned configuration**, not constants scattered through code. A maintainer should be able to revise a profile without editing renderer logic.

### 1.1 Etsy listing video

Official Etsy help currently states:

- Video length: **3–15 seconds**.
- Maximum file size: **100 MB**.
- Accepted file types include MP4 and MOV (along with several other formats).
- Minimum resolution: **500 px**; Etsy says ideal resolution is at least **1080 px**.
- Audio is removed after upload; therefore the video must communicate without sound.
- Up to **two listing videos** can currently be added to a listing.
- The stated aspect ratio should be **2:1 or 1:2**.

**Recommended production profile:**

- MP4, H.264, 30 fps CFR, square pixels, progressive, `yuv420p`.
- No audio stream in the Etsy export.
- Duration default: 10–12 seconds; allow user override within 3–15 seconds.
- Default layout: `1:2` portrait, 1080 × 2160, for portrait book pages; use `2:1` landscape, 2160 × 1080, when the artwork/product is better presented horizontally. Validate the aspect ratio exactly against the current Etsy profile.
- Target file size: 80–90 MB maximum as a safety margin; aim much lower for short clips.
- Use short on-screen text sparingly because the video is viewed at listing size and must be immediately legible.
- Do not rely on music, voiceover, sound effects, or audio cues.

**Etsy creative principle:** clarify what the digital buyer receives. Show the actual cover/pages, page variety, detail quality, format/quantity only when metadata confirms it, and the distinction between a printable PDF, individual-page download, and a physical item. Do not imply a physical book is shipped when the listing is digital.

### 1.2 Instagram Reels / Stories

**Recommended organic master profile:**

- 9:16 vertical, 1080 × 1920.
- MP4, H.264, 30 fps CFR, square pixels, progressive, `yuv420p`.
- AAC stereo audio at 128 kbps or higher when audio is included.
- 10–20 seconds is a useful default creative range for this publishing use case; this is a creative default, not the platform's maximum duration.
- Include captions or burned-in subtitles when speech/voiceover is used.
- Keep important text, logos, products, and CTA clear of interface overlays. A current Meta placement guide recommends leaving approximately 14% at the top, 35% at the bottom, and 6% on each side free of important elements. Store these safe-zone values in profile config and render a safe-zone overlay in previews.

**Paid Reels variant:** the current ad guidance also recommends 9:16 high-resolution creative, with 1440 × 2560 appearing as a recommended size in current placement references. Do not blindly upsample every organic master; offer a separate higher-resolution export profile if a campaign actually requires it.

### 1.3 Instagram Feed video

- Recommended advertising canvas: 4:5, 1440 × 1800.
- 1:1 or 4:5 may be practical for feed-oriented product videos; profile controls exact choice.
- MP4, H.264, 30 fps CFR, AAC audio when needed.
- Create a dedicated feed crop/layout. Do not simply crop a 9:16 Reel, because title, artwork and CTA can be lost.

### 1.4 Facebook Feed video ads

- Recommended feed canvas: 4:5, 1440 × 1800.
- MP4 / H.264; AAC audio when included.
- 30 fps CFR, square pixels, progressive scan.
- Facebook placements may accept a wider range of aspect ratios and very long durations, but this framework should use short creative defaults (typically 10–30 seconds) for digital-product ads.
- Make the opening visual understandable with sound off; use captions if narration carries information.

### 1.5 Facebook Reels / Stories

- 9:16 vertical; use 1080 × 1920 as the reusable organic master and allow a higher-resolution paid-ad profile (for example 1440 × 2560) where justified.
- Follow the same Reels safe-zone strategy as Instagram.
- Sound can help, but the visual story must remain understandable with sound disabled.

### 1.6 GIF policy

- GIF is a **secondary derivative**, not the primary delivery format.
- Do not use GIF as the Etsy listing video export; it is not in Etsy's listed accepted video file types.
- Use GIF for lightweight website/email/product-preview loops where the destination supports it.
- GIF has no sound, limited palette, and can become very large. Use a palette-generation pass, controlled dimensions, reduced frame rate, and a strict byte-size budget.
- Always retain MP4 as the source deliverable; never use a GIF as the only master.

### 1.7 Profile config example

Store profiles in `config/platforms/`, not in Python conditionals:

```yaml
id: etsy_listing_portrait
platform: etsy
placement: listing_video
verified_on: "2026-10-31"
source_urls:
  - "https://help.etsy.com/hc/en-us/articles/360053206073-How-to-Add-Listing-Videos"
canvas:
  width: 1080
  height: 2160
  aspect_ratio: "1:2"
  fps: 30
  pixel_format: yuv420p
  sample_aspect_ratio: "1:1"
duration:
  min_seconds: 3
  max_seconds: 15
  default_seconds: 12
file:
  container: mp4
  video_codec: libx264
  audio: forbidden
  max_bytes: 100000000
  target_max_bytes: 85000000
safe_zones:
  enabled: false
validation:
  require_no_audio_stream: true
  require_exact_aspect_ratio: true
```

Use a separate `etsy_listing_landscape` profile with 2160 × 1080 and `2:1`. Keep the 100 MB limit in bytes and document whether the validator uses decimal MB (100,000,000 bytes) or MiB; do not mix units.

> Platform requirements can change. No WebSearch is required at runtime: the current rules and source URLs are embedded locally. Add a `profile-review` task to the release checklist and update `verified_on` whenever a person checks the official guidance.

---

## 2. Three entry paths and intake logic

The skill must support all three use cases through one normalized `AnimationJob` object.

### 2.1 Entry A — invoked after a book/product is created

Add an optional post-generation hook to the publishing pipeline:

1. Book pipeline completes content, cover, page assets, metadata, and downloadable PDFs.
2. Publishing agent checks whether the product is eligible for a promo video.
3. Claude asks whether to create video assets now. Include a clear **Recommended** choice (normally Yes for a new Etsy product, with No / Later alternatives).
4. If Yes, pre-fill everything available from the publishing manifest: product type, title, subtitle, cover path, page paths, page count, download types, product category, palette, series, brand, and existing metadata.
5. Ask only for missing creative decisions: destinations, number of outputs, template preference, and whether AI footage is permitted.
6. Generate a preview, show contact sheet / sample frames / MP4 preview, then ask for approval before final export.
7. Store the job manifest beside the published product and return final asset paths to the publishing pipeline.

The publishing pipeline should pass a structured product manifest, not ask Claude to rediscover files by guessing directory names.

### 2.2 Entry B — independent `/create-animation`

Support both natural-language arguments and structured flags. Parse the user prompt first; ask questions only for missing, ambiguous, conflicting, or high-impact fields.

Example invocations:

```text
/create-animation Make a 12-second silent Etsy listing video for the Majestic Queens grayscale coloring book. Use the cover plus pages 3, 8, 14 and 22. Template: page gallery. Export MP4.

/create-animation --platform instagram-reels --goal product-promo --assets ./products/queens/animation-assets.json --template auto

/create-animation Create an ad for Company ABC about the dangers of smoking. Use our brand assets, a serious but hopeful tone, vertical Instagram and Facebook Reels versions, 20 seconds, voiceover and captions.
```

**Do not ask the user to provide technical implementation details** such as frame rate, FFmpeg codec flags, resampling filter or bitrate unless they explicitly want control. The skill selects these from the platform profile.

### 2.3 Entry C — generic campaign / public-service ad

For a brief such as “Show an ad for Smoking is bad for health with Company-ABC branding”:

1. Classify as `campaign_ad` / `public_service` rather than product showcase.
2. Infer likely goal: awareness / education; do not assume conversion CTA.
3. Ask for audience, destination placement, desired tone, campaign CTA, logo/brand assets, and any required claims or source copy.
4. Propose a storyboard with hook → message → supporting visual → action/closing brand card.
5. Any specific health, legal, financial, safety, or comparative claim must be sourced from the user's provided references or approved copy. Never invent statistics, study names, medical advice, or product efficacy claims.
6. Show all factual on-screen text and narration for approval before rendering.
7. Keep company branding consistent and do not invent official affiliations, endorsements, government seals, or certifications.

### 2.4 AskUserQuestion policy

The `/create-animation` skill must use Claude Code's `AskUserQuestion` tool for material choices, and **always label the recommended option as `Recommended` wherever applicable**. Ask a compact set of grouped questions, not a long questionnaire. Prepopulate answers from prompt arguments, product manifests, brand config, and job defaults.

Suggested question groups:

| Question | Options / default logic |
|---|---|
| Where will this be published? | Etsy listing / Instagram Reels & Stories / Instagram Feed / Facebook Feed Ads / Facebook Reels / Website / Multiple platforms. Recommend from context. |
| What is the goal? | Product showcase / Sales promo / Brand awareness / Educational PSA / Process demonstration. Infer and confirm only if ambiguous. |
| What outputs? | MP4 / MP4 + GIF / MP4 + still thumbnails / Recommended bundle. Etsy always gets MP4. |
| Which creative template? | Recommend one named template plus alternatives. Include Auto / Recommended. |
| Which assets? | Use existing product manifest / choose files / generate missing assets. Never silently create substitute product artwork. |
| Sound? | Silent / Licensed music / Voiceover + captions / Voiceover + music. Etsy defaults to silent. |
| Brand style? | Existing brand profile / product-specific palette / campaign custom palette. |
| Review? | Generate preview first (Recommended) / render final directly only for trusted, repeatable batch jobs. |

Ask for brand logo, audience, CTA, or factual claims only when not already present in metadata/configuration. If the user gave enough detail in the command arguments, skip the questions and proceed to preview.

### 2.5 Normalized job fields

Every entry path must map to the same schema:

```json
{
  "job_id": "queens-etsy-20261031-001",
  "mode": "product_showcase",
  "product": {
    "id": "majestic-queens",
    "type": "grayscale_coloring_book",
    "title": "Majestic Queens",
    "subtitle": "30 Intricate Designs",
    "confirmed_facts": ["30 coloring pages", "PDF instant download"],
    "source_manifest": "./products/queens/product-manifest.json"
  },
  "campaign": {
    "objective": "product_clarity_and_conversion",
    "audience": "adult coloring enthusiasts",
    "message": "Explore the intricate designs inside",
    "cta": "Download instantly"
  },
  "platforms": ["etsy_listing_portrait", "instagram_reels"],
  "assets": {
    "cover": "./cover.png",
    "pages": ["./pages/page-003.png", "./pages/page-008.png"],
    "colored_pairs": [],
    "brand_logo": "./brand/logo.png"
  },
  "creative": {
    "template_id": "etsy_page_gallery_v1",
    "tone": "premium_editorial",
    "duration_seconds": 12,
    "ai_video_policy": "disabled",
    "audio_policy": "silent"
  },
  "outputs": ["mp4", "contact_sheet", "thumbnail"],
  "approval": {"required": true}
}
```

All claims in `confirmed_facts` must be traceable to the product metadata or explicitly approved copy. Avoid freeform inferred page counts, formats, included bonuses, instant-download claims, or licensing terms.

---

## 3. Creative template library

Start with a **candidate library of 18 creative archetypes (six per channel group)**. Test variants, then promote the best four per channel group into the default production set. The candidate library must remain larger than the production set so the experiment has meaningful choices. Four per platform is a selection outcome, not a reason to hardcode exactly four effects into the renderer.

### 3.1 Etsy — four candidate / final template slots

| ID | Template | Story structure | Strong use case |
|---|---|---|---|
| ETSY-01 | `page_gallery` | Cover → 3–5 actual pages → close-up → cover/end frame | Coloring books, mandalas, sketch books, illustration books |
| ETSY-02 | `intricate_detail_zoom` | Full page → 2–3 detail crops → return to full page | Detailed mandalas, grayscale artwork, pencil sketches |
| ETSY-03 | `grayscale_to_color` | Grayscale original → aligned color reveal → final colored result | Coloring books with genuine colored sample counterparts |
| ETSY-04 | `what_is_included` | Cover → page variety → confirmed page count/file formats → instant-download end card | Printable bundles, PDF page sets, digital books |
| ETSY-05 | `printable_in_context` | Real artwork → accurate tablet/printed-page mockup → close-up of actual design → digital-delivery reminder | Printable PDFs and individual-page downloads; mockup must not imply physical shipping |
| ETSY-06 | `buyer_question_answer` | One common buyer question → visual answer using actual files → product cover / key detail | “What do I receive?”, page-detail and format clarity |

**Etsy design rules:** silent-first; no critical text near the edge; no fast unreadable flashing; keep pages large; avoid presenting AI video as part of the purchased item; never show a colored counterpart as if it is included unless the listing metadata confirms it.

### 3.2 Instagram — four candidate / final template slots

| ID | Template | Story structure | Strong use case |
|---|---|---|---|
| IG-01 | `hook_then_reveal` | 0–2s hook → hero art → several quick reveals → CTA | Short-form product discovery |
| IG-02 | `transformation_reveal` | Line art / grayscale → progressive color or sketch-to-final transition → final image | Coloring books, art collections, process-based products |
| IG-03 | `satisfying_flipthrough` | Animated page stack / sliding cards / editorial cuts → detail → cover | Books, page collections, printable packs |
| IG-04 | `cinematic_world` | Optional AI atmospheric opening → real product artwork → brand/product close | Fantasy, storybooks, themed artwork |
| IG-05 | `mini_story` | Relatable moment / desired outcome → product reveal → actual pages → CTA | Children’s books, activity packs, relaxing creative products |
| IG-06 | `detail_satisfaction` | Rhythmic close-ups, page reveals and visual texture → hero image → CTA | Mandalas, intricate coloring pages, sketches and art collections |

### 3.3 Facebook — four candidate / final template slots

| ID | Template | Story structure | Strong use case |
|---|---|---|---|
| FB-01 | `problem_to_solution` | Buyer problem / desire → product solution → proof of contents → CTA | Educational packs, practical printables, gifts |
| FB-02 | `value_stack` | Cover / hero → multiple previews → confirmed bundle details → CTA | Multi-file bundles and collections |
| FB-03 | `before_after` | Initial state → transition or comparison → finished result → CTA | Coloring and drawing products |
| FB-04 | `product_demo` | Show product pages in use / tablet or print mockup → close-up → details → CTA | PDFs, workbooks, children's activities |

### 3.4 Reusable motion/effect primitives

Templates compose small reusable effects. Implement each effect once:

- `ken_burns`: slow zoom and/or pan with easing.
- `crop_push`: transition from complete page to detail crop.
- `wipe_reveal`: reveal a second aligned image through an animated mask.
- `crossfade`: blend between scenes.
- `slide_in` / `slide_out`: controlled card/page movement.
- `page_flip_simulated`: 2D sheet/card turn (do not claim physically accurate 3D page turning).
- `stack_fan`: fan out multiple page/cover assets.
- `parallax_layers`: move independently layered foreground/background at small offsets.
- `particle_overlay`: restrained dust, bokeh, sparkles or snowfall; optional and theme-specific.
- `text_reveal`: fade, mask reveal, or short movement with high legibility.
- `brand_end_card`: logo, title, CTA, URL/handle, approved brand colours.
- `audio_fade`: music/voiceover fade and ducking.

Each primitive needs parameter limits and defaults. Motion should support easing curves such as linear, ease-in-out, cubic-out, and spring-like easing only when appropriate. Avoid exaggerated motion that makes page artwork hard to inspect.

### 3.5 Template configuration, not code forks

Example template data:

```yaml
id: etsy_page_gallery_v1
name: Etsy Page Gallery
channel_group: etsy
objective: product_clarity
version: 1.0.0
eligible_product_types:
  - grayscale_coloring_book
  - mandala_coloring_book
  - sketch_collection
  - illustrated_book
  - printable_page_bundle
scene_plan:
  - type: cover_hero
    duration: 1.6
    motion: gentle_push_in
    text: "{{product.title}}"
  - type: page_gallery
    duration: 7.2
    asset_selection: curated_pages
    page_count: 4
    transition: crossfade
  - type: detail_crop
    duration: 1.8
    crop_anchor: configured_or_auto
  - type: end_card
    duration: 1.4
    fields: ["{{product.subtitle}}", "{{product.delivery_label}}"]
constraints:
  audio: forbidden
  max_duration_seconds: 15
  require_real_product_assets: true
human_editable:
  - asset_selection
  - page_count
  - scene_durations
  - crop_anchor
  - title_text
  - end_card_text
```

A human should be able to change image/page IDs, number of images, display order, scene duration, crop position, text, background theme, transition and output profile without editing Python.

---

## 4. Architecture and data flow

```text
Publishing Pipeline / User Prompt / Campaign Brief
                       |
                       v
             /create-animation Skill
                       |
           Intake + Product/Brand Resolver
                       |
                       v
              Animation Director Agent
                       |
                       v
                Storyboard JSON
                       |
              Schema + Constraint Check
                       |
                       v
          Template Engine / Scene Compiler
                       |
           +-----------+------------+
           |                        |
           v                        v
    Asset Preparation          AI Video Adapter
    Python + Pillow            (optional / opt-in)
           |                        |
           +-----------+------------+
                       |
                       v
               Scene/Clip Renderer
                   FFmpeg
                       |
                       v
             Platform Export Profiles
                       |
                       v
             FFprobe + Automated QA
                       |
                       v
           Contact Sheet / Preview MP4
                       |
                 Human Approval
                       |
                       v
              Final Render + Exports
                       |
                       v
       Job Manifest + Assets + Analytics IDs
```

### 4.1 Component boundaries

- **Claude skill:** orchestration, questions, creative reasoning, approvals, interpretation of QA, and delegation.
- **Python package:** all deterministic image composition, storyboard validation, render planning, and file operations.
- **FFmpeg:** temporal operations, filters, encoding, audio, muxing and media transforms.
- **FFprobe:** inspect streams, dimensions, duration, pixel format, frame rate, audio and file metadata.
- **Draw Things adapter:** a provider boundary only. It must not be imported directly by templates.
- **Platform profile registry:** authoritative local constraints for output generation and validation.
- **Job store:** records source assets, configuration, outputs, versions, checksums, QA and experiment data.

### 4.2 Keep the render pipeline deterministic

Given the same source assets, job config, profile, template version, fonts, music and renderer version, the pipeline should produce the same storyboard and substantially repeatable output. If an AI video stage is used, record its model, prompt, seed (if available), sampler/settings (if available), version and output hash. AI footage itself is not guaranteed to be bit-for-bit reproducible.

### 4.3 Job stages and resumability

Suggested stage IDs:

1. `intake`
2. `asset_discovery`
3. `asset_validation`
4. `creative_brief`
5. `storyboard_generation`
6. `storyboard_validation`
7. `ai_video_generation` (optional)
8. `asset_preparation`
9. `scene_rendering`
10. `video_assembly`
11. `platform_export`
12. `qa_validation`
13. `preview_approval`
14. `final_export`
15. `manifest_finalize`

Persist stage state (`pending`, `running`, `succeeded`, `failed`, `skipped`, `needs_review`), timestamps, logs, outputs and input hashes. If an input asset/template/profile is unchanged, a successful stage may be reused. Never reuse stale outputs when a dependency hash changes.

---

## 5. Asset discovery and product manifest integration

### 5.1 Preferred asset source

The publishing pipeline should emit or extend a `product-manifest.json` containing:

- Product ID, type, title, subtitle, description and intended audience.
- Cover file path and page file paths.
- Page numbers and semantic labels, if known.
- Whether a page is grayscale, line art, coloured, grayscale/colour matched pair, sketch or illustration.
- Which files are actually included in the buyer download.
- Page count, file formats, PDF file paths, ZIP paths and download labels.
- Series, publisher, brand profile and brand assets.
- Rights/provenance fields for images, fonts and audio.

Use a stable relative path from the publishing job root, plus an optional absolute resolved path at runtime. Validate every path; do not silently fall back to a similarly named asset.

### 5.2 Asset manifest example

```json
{
  "product_id": "majestic-queens",
  "product_type": "grayscale_coloring_book",
  "cover": {"path": "cover/cover.png", "role": "cover"},
  "pages": [
    {"page_number": 3, "path": "interior/page-003.png", "type": "grayscale", "selected_for_promo": true},
    {"page_number": 8, "path": "interior/page-008.png", "type": "grayscale", "selected_for_promo": true}
  ],
  "color_pairs": [],
  "deliverables": {
    "digital_only": true,
    "included_formats": ["PDF"],
    "page_count": 30
  },
  "brand_profile": "brands/main-publishing-brand.yaml"
}
```

### 5.3 Asset validation

Check before rendering:

- File exists, readable, and supported format.
- Dimensions and colour mode are known; normalize EXIF orientation before any crop or composite.
- PNG transparency is handled correctly; convert to RGBA/RGB as required.
- Image is not blank, corrupt or obviously unrelated to the product.
- Source resolution is adequate for the intended display size; upscale warnings should be explicit.
- If a grayscale/color comparison is selected, require an explicitly paired/aligned image or a user-approved mapping. Never pair images based only on filename similarity.
- Check duplicate images with perceptual hashes and report duplicates; do not remove without approval.
- For page IDs/numbers, preserve the original order and traceable page index.
- Store SHA-256 or another stable checksum for inputs used in a job.

### 5.4 No destructive edits

The source artwork is immutable. All crops, resize results, masks, shadows, frames, composites and thumbnails go into the job's generated-asset folder. Never overwrite Draw Things source images or final book PDFs.

---

## 6. Python/Pillow: what it should do

Pillow is the **image and layout preparation engine**, not the video timeline editor. It loads source pictures, computes/composes the visual layers and exports still assets or generated frames. FFmpeg controls video timing and motion wherever practical.

### 6.1 Layout operations

- `ImageOps.contain`: fit an image inside a target rectangle without cropping.
- `ImageOps.cover` / `ImageOps.fit`: fill a target rectangle with controlled crop.
- Lanczos resampling for high-quality downscaling/resizing where appropriate.
- Alpha compositing for transparent overlays, logos, page shadows and cards.
- Image masks for grayscale-to-colour reveals and shaped transitions.
- `ImageDraw` / `ImageFont` for titles, captions, page labels, badges and end cards.
- `ImageFilter` for restrained shadows, blur, glow and subtle texture.
- Gradients and background surfaces generated procedurally; do not make every background an AI image.
- Safe-zone guides and text-layout boxes for preview QA.

### 6.2 Example: prepare a page on a branded canvas

```python
from PIL import Image, ImageOps


def place_page(source_path: str, canvas_size: tuple[int, int], margin: int) -> Image.Image:
    canvas = Image.new("RGB", canvas_size, "#eee8df")
    with Image.open(source_path) as src:
        page = ImageOps.contain(
            src.convert("RGB"),
            (canvas_size[0] - 2 * margin, canvas_size[1] - 2 * margin),
            method=Image.Resampling.LANCZOS,
        )
    x = (canvas.width - page.width) // 2
    y = (canvas.height - page.height) // 2
    canvas.paste(page, (x, y))
    return canvas
```

This is a composition step. It does not animate or edit the source page.

### 6.3 Example: grayscale-to-colour reveal mask

Require two aligned images of the same dimensions. Create a mask `M(x, y, t)` where pixels left of the animated reveal boundary use the colour image and the remainder use grayscale. A soft boundary can be implemented as a narrow blurred mask. Do not use this effect when the pair is misaligned; it creates ghosting and a poor result.

### 6.4 Example: title fitting

Implement a `TextLayoutEngine` that:

1. Loads an approved font from the brand profile.
2. Measures text using `textbbox` / multiline measurement.
3. Reduces font size until it fits the available box, respecting a minimum size.
4. Applies line spacing, anchor, alignment, and padding.
5. Measures contrast against the background or adds a subtle backing plate/shadow.
6. Produces an overflow warning if the title still does not fit.

Never use AI-generated typography baked into the product artwork for important marketing copy. Draw title, publisher, CTA and claims as editable overlay text.

### 6.5 Where not to use Pillow

Do not render a full PNG file for every video frame by default. At 30 fps, a 15-second video has 450 frames. Writing hundreds or thousands of full-resolution images is slower and consumes disk. Prefer:

- Pillow for source still composition and complex layered graphics.
- FFmpeg filters for zoom/pan/fade/crossfade/audio timing when the effect is expressible safely.
- A streamed image pipe or temporary frame sequence only for effects that truly require custom per-frame pixel calculations (e.g. a complex animated matte or drawing reveal).

Never repeatedly upscale, downscale, encode, decode and resize the same artwork. Keep the highest-quality original and render each output size from that master once.

---

## 7. FFmpeg: motion, assembly and encoding

### 7.1 Main principles

- Use a single final encode per output profile where possible.
- Use FFmpeg filtergraphs for timing, fades, overlays, transitions and audio.
- Normalize every scene to the target dimensions, frame rate, sample aspect ratio and pixel format before concatenation.
- For MP4 exports, use H.264 (`libx264` default), `yuv420p`, fixed frame rate, square pixels and `+faststart`.
- For Etsy, produce no audio stream.
- For social, add licensed music/voiceover only when requested and rights are recorded.
- Verify final streams with FFprobe; successful FFmpeg exit code alone is not sufficient.

### 7.2 Recommended starting encode settings

Use as initial defaults, then tune with real test clips:

**MP4 H.264:**

- Video encoder: `libx264`.
- CRF: 18–22 for clean product artwork; 20 is a reasonable first test. Lower CRF gives larger/higher-quality output.
- Preset: `medium` initially; use `fast` for faster batch throughput if the quality/file-size trade-off is acceptable.
- Output pixel format: `yuv420p` for broad playback compatibility.
- Frame rate: 30 fps CFR for social; profile can allow 24 or 30 where needed.
- `-movflags +faststart` to place MP4 metadata for progressive web playback.
- `-pix_fmt yuv420p`, `-vf setsar=1`, and explicit output dimensions.
- Audio for social: AAC-LC stereo, 48 kHz, 160–192 kbps starting point.

**Hardware encoding:** offer an optional Apple VideoToolbox encoder path (`h264_videotoolbox`) only after testing its quality/size behavior on the local M4. Do not assume VideoToolbox uses the same CRF semantics as libx264. Keep `libx264` as the reproducible quality baseline.

**Etsy size management:** first render at target quality; if over the byte budget, reduce bitrate/CRF carefully, then consider lowering frame rate or dimensions only if the profile permits. Never silently degrade the source artwork or force the output below a configured visual-quality threshold.

### 7.3 Illustrative FFmpeg encode command

The exact filtergraph should be constructed by a typed command builder, not by interpolating arbitrary user text into a shell command.

```bash
ffmpeg -y -i composed-timeline.mov \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p" \
  -c:v libx264 -preset medium -crf 20 \
  -movflags +faststart -an \
  instagram-reel.mp4
```

For audio-enabled social output, map and encode the audio explicitly, for example AAC stereo at 48 kHz. Do not reuse `-an` for those profiles.

### 7.4 GIF encoding

Use FFmpeg `palettegen` + `paletteuse` rather than direct default GIF encoding. Configure:

- Maximum width/height per destination.
- Lower frame rate (e.g. 10–15 fps) unless smoothness matters.
- Looping policy.
- Dither method and palette strategy.
- Maximum output byte budget.

GIF QA should check playback duration, dimensions, frame count, file size and whether fine line art remains legible. Fine black-and-white line art can be damaged by aggressive palette reduction; prefer MP4 for detailed coloring-page previews.

### 7.5 Timeline model

Represent time in integer frames or rational timestamps rather than accumulating floating-point durations. At 30 fps, one frame is 1/30 second. Define scene start/end frames and transition overlap frames. The compiler should calculate the final duration and ensure the transition overlaps do not accidentally shorten the video or extend past platform limits.

### 7.6 Audio policy

- Etsy: no audio stream, no audio assets required.
- Social: audio optional; use only supplied, commissioned, properly licensed, or platform-cleared material.
- Track metadata should include title, artist, source, license type, allowed platforms, territory, expiry and attribution requirement.
- Store separate voiceover, music, sound effects and caption timing assets.
- Voiceover must not contain claims absent from the approved script.
- Duck background music under speech; apply fades and loudness normalization as part of the audio pipeline.
- Provide a sound-off review mode.

---

## 8. Optional Draw Things video generation

### 8.1 Important distinction: Draw Things app vs `draw-things-cli`

Draw Things supports video models in its application, and its release notes document video model support, LTX-2.3, Wan 2.x support and video export improvements. However, the currently published `draw-things-cli` README documents an image-generation `generate` command and LoRA training / model utilities; it does **not** document a stable video-generation CLI command in the inspected public command surface.

Therefore:

- Do not invent a CLI command such as `draw-things-cli video` or assume a hidden flag exists.
- At setup, run `draw-things-cli --help`, `draw-things-cli generate --help`, and any available model/help commands, record the CLI version, and test whether video is actually exposed.
- Implement an adapter interface, e.g. `VideoGenerationProvider.generate(request)`, with a `DrawThingsVideoAdapter` marked `experimental` until an official, tested command/API is available.
- If the installed Draw Things app can generate video but CLI cannot, use the app/manual export workflow or wait for a documented automation endpoint. Do not make GUI scripting a silent or mandatory dependency.
- The standard animation pipeline must operate completely when the video provider is unavailable.

### 8.2 Best use cases for AI footage

Use AI video only when it adds mood or motion that is not easily created from the real product artwork:

- Mist, clouds, drifting light, magical atmosphere behind fantasy covers.
- Subtle cinematic opening for a storybook or themed collection.
- A background environment for a campaign ad.
- Abstract particles, water, smoke or light where the content is decorative and not a factual representation of the product.

Do not use AI video to regenerate or replace the product pages shown to buyers. Keep real book pages, covers, text and printable assets crisp and untouched.

### 8.3 Model-selection policy

The user's installed candidates include SkyReels-V1, Wan Video and LTX-2.3 22B Distilled 8-bit S. Keep model-specific settings in provider config; do not hardcode a claim that one model is always fastest/best on this Mac.

Run a local benchmark on the exact M4 / 48 GB machine:

- one text-to-video test and one image-to-video test per model, where supported;
- short duration and conservative resolution first;
- measure wall-clock generation time, peak unified-memory pressure, output dimensions/fps, temporal stability, artifact rate and first/last-frame consistency;
- record whether the exported media is ProRes, HEVC or another format and normalize later through FFmpeg;
- test whether a model preserves the product's subject and composition without changing details;
- test thermal throttling and repeatability on more than one run.

Do not start with a long high-resolution generation. Treat 22B models on a 48 GB unified-memory machine as a measured capability, not a guaranteed throughput assumption. Model loading, video VAE decoding, resolution, frame count, quantization, other active applications and memory cache all affect viability.

### 8.4 AI-video quality constraints

- Prompt for **background/atmosphere only** where the product remains a separate overlay.
- No model-generated product text, pricing, page counts, logos or calls to action.
- Avoid generated hands manipulating books unless that action passes a visual QA check; generated hands and page geometry can distort.
- Analyze first, middle and last frames for flicker, scene changes, object deformation and unwanted text.
- Check every frame or representative sampled frames for embedded watermarks, logos, UI and unexpected text.
- Reject footage with uncanny or distracting motion.
- AI footage must be treated as a supporting layer, not evidence of the contents of the purchase.

### 8.5 Provider contract

```python
class VideoGenerationProvider(Protocol):
    def capabilities(self) -> ProviderCapabilities: ...
    def generate(self, request: VideoGenerationRequest) -> VideoGenerationResult: ...
    def health_check(self) -> ProviderHealth: ...
```

The adapter returns a clip path plus metadata (model ID, version, prompt, seed/settings if supported, duration, dimensions, frame rate, codec, generation time, warnings). It must return a structured `unsupported` result rather than inventing a fallback command.

---

## 9. Storyboard schema and scene compiler

A storyboard is a sequence of typed scenes; each scene references assets by manifest ID, not arbitrary filenames guessed by the renderer.

### 9.1 Scene types

Initial set:

- `cover_hero`
- `page_gallery`
- `detail_crop`
- `before_after`
- `color_reveal`
- `product_mockup`
- `bundle_overview`
- `text_card`
- `brand_end_card`
- `ai_background`
- `campaign_scene`
- `voiceover_caption`

Each scene defines:

- Stable `scene_id`.
- `type`.
- Duration as frame count or seconds with deterministic frame conversion.
- Asset references.
- Layer order and layout anchors.
- Motion/effect names and parameters.
- Text tokens/metadata placeholders.
- Transition in/out.
- Audio segment references.
- Platform-safe bounds.

### 9.2 Example storyboard

```json
{
  "schema_version": "1.0.0",
  "job_id": "majestic-queens-etsy-001",
  "profile_id": "etsy_listing_portrait",
  "template_id": "etsy_page_gallery_v1",
  "fps": 30,
  "scenes": [
    {
      "scene_id": "s01-cover",
      "type": "cover_hero",
      "duration_frames": 48,
      "assets": ["cover"],
      "motion": {"effect": "ken_burns", "zoom_start": 1.0, "zoom_end": 1.04, "anchor": "center"},
      "text": [{"value": "{{product.title}}", "style": "title"}],
      "transition_out": {"type": "crossfade", "duration_frames": 8}
    },
    {
      "scene_id": "s02-gallery",
      "type": "page_gallery",
      "duration_frames": 240,
      "assets": ["page-003", "page-008", "page-014", "page-022"],
      "layout": {"fit": "contain", "background": "warm-paper"},
      "motion": {"effect": "subtle_push_in", "max_zoom": 1.025},
      "transition_out": {"type": "crossfade", "duration_frames": 10}
    },
    {
      "scene_id": "s03-end",
      "type": "brand_end_card",
      "duration_frames": 72,
      "assets": ["brand-logo"],
      "text": [
        {"value": "{{product.subtitle}}", "style": "subtitle"},
        {"value": "{{product.delivery_label}}", "style": "caption"}
      ]
    }
  ]
}
```

Durations and transitions above are illustrative only. The scene compiler should calculate timeline overlaps and final total frames before rendering.

### 9.3 Validation

Use Pydantic or JSON Schema to validate:

- Supported schema/template/profile versions.
- Required keys for each scene type.
- No missing asset references.
- Positive frame counts and nonnegative transition durations.
- Total duration within platform profile.
- Scene count and asset count within configured limits.
- Text tokens resolve to approved metadata.
- Audio policy matches platform profile.
- AI video request is disabled when the user opted out or provider is unavailable.
- All user-provided file paths are within allowed project/input directories unless explicitly approved.

---

## 10. Brand system and text standards

Create a brand profile separate from template config:

```yaml
id: main-publishing-brand
logo: assets/brand/logo-transparent.png
colors:
  primary: "#29304A"
  secondary: "#D9C7A8"
  background: "#F4EFE7"
  text: "#1F1F1F"
fonts:
  heading: "fonts/BrandHeading.otf"
  body: "fonts/BrandBody.ttf"
voice:
  adjectives: ["premium", "clear", "warm", "trustworthy"]
  avoid: ["overhyped", "misleading", "fake urgency"]
logo_rules:
  min_clear_space_ratio: 0.5
  allow_recolor: false
```

Fonts and music must have usable licences for the target media and commercial use. The pipeline should not bundle fonts whose licences do not permit embedding/use, nor scrape songs from social channels.

### Copy rules

- Hook: one short idea; the first two seconds should make the product/campaign understandable.
- Use concrete facts, not unsupported adjectives or claims.
- Keep lines short and readable on a phone.
- One primary CTA; avoid multiple competing CTAs.
- Avoid placing important copy in platform UI zones.
- Keep spelling, punctuation and capitalization consistent with the brand profile.
- User can edit text in config or preview brief; never require Python changes for copy edits.

---

## 11. Suggested `.claude/` framework additions

Keep orchestration prompts in `.claude/`, but put executable Python in a normal source package. This separates Claude instructions from production code.

```text
.claude/
├── skills/
│   ├── create-animation/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── platform-profiles.md
│   │   │   ├── template-catalog.md
│   │   │   ├── storyboard-schema.md
│   │   │   ├── qa-rules.md
│   │   │   ├── brand-and-claims.md
│   │   │   └── draw-things-provider.md
│   │   └── examples/
│   │       ├── book-pipeline-example.md
│   │       ├── etsy-example.md
│   │       └── psa-example.md
│   ├── animation-template-lab/
│   │   └── SKILL.md
│   └── animation-review/
│       └── SKILL.md
├── agents/
│   ├── animation-director.md
│   ├── storyboard-architect.md
│   ├── animation-render-engineer.md
│   ├── animation-qa-reviewer.md
│   └── creative-experiment-analyst.md
├── rules/
│   ├── animation-core.md
│   ├── animation-assets.md
│   ├── animation-platform-exports.md
│   └── animation-brand-claims.md
└── settings.json                 # only add hooks if they are genuinely needed

config/
├── animation/
│   ├── platforms/
│   │   ├── etsy-listing-portrait.yaml
│   │   ├── etsy-listing-landscape.yaml
│   │   ├── instagram-reels.yaml
│   │   ├── instagram-feed.yaml
│   │   ├── facebook-feed-ads.yaml
│   │   ├── facebook-reels.yaml
│   │   └── website-generic.yaml
│   ├── templates/
│   │   ├── etsy/
│   │   ├── instagram/
│   │   ├── facebook/
│   │   └── generic-campaign/
│   ├── brands/
│   ├── themes/
│   ├── audio/
│   └── providers/
│
└── schemas/
    ├── animation-job.schema.json
    ├── asset-manifest.schema.json
    ├── storyboard.schema.json
    ├── platform-profile.schema.json
    └── template.schema.json

src/animation_pipeline/
├── __init__.py
├── cli.py
├── orchestrator.py
├── job_store.py
├── config_loader.py
├── models.py
├── validators/
│   ├── assets.py
│   ├── storyboard.py
│   ├── platform.py
│   └── output.py
├── assets/
│   ├── discovery.py
│   ├── manifest.py
│   └── image_analysis.py
├── creative/
│   ├── template_registry.py
│   ├── template_compiler.py
│   ├── storyboard_builder.py
│   └── copy_resolver.py
├── image/
│   ├── canvas.py
│   ├── layout.py
│   ├── text_layout.py
│   ├── masks.py
│   ├── shadows.py
│   ├── backgrounds.py
│   └── frame_stream.py
├── effects/
│   ├── base.py
│   ├── ken_burns.py
│   ├── reveal.py
│   ├── transitions.py
│   ├── page_gallery.py
│   └── particles.py
├── video/
│   ├── ffmpeg_builder.py
│   ├── timeline.py
│   ├── audio.py
│   ├── gif.py
│   ├── probe.py
│   └── export.py
├── providers/
│   ├── base.py
│   └── draw_things_video.py
├── qa/
│   ├── checks.py
│   ├── contact_sheet.py
│   ├── visual_report.py
│   └── scoring.py
└── experiments/
    ├── variants.py
    ├── ab_test.py
    └── results.py

tests/
├── unit/
├── integration/
├── golden_frames/
├── fixtures/
└── acceptance/

output/animation-jobs/<job_id>/
├── job.json
├── assets-manifest.json
├── storyboard.json
├── preview/
│   ├── contact-sheet.jpg
│   ├── preview.mp4
│   └── qa-report.json
├── generated-assets/
├── intermediate/
├── final/
│   ├── etsy-listing.mp4
│   ├── instagram-reel.mp4
│   ├── facebook-feed.mp4
│   └── preview.gif
└── logs/
```

### 11.1 Skill responsibilities

**`/create-animation`** is the user-facing orchestrator. Its SKILL.md should be relatively concise and load reference documents only as needed. It should:

1. Parse prompt arguments.
2. Discover product and brand manifests.
3. Infer job type and recommend a template/profile.
4. Ask only necessary `AskUserQuestion` questions.
5. Delegate storyboard design and QA.
6. Write `job.json` and `storyboard.json`.
7. Invoke Python CLI scripts.
8. Inspect preview/contact sheet/QA output.
9. Request human approval when required.
10. Render final deliverables and report paths, duration, dimensions, codec, file sizes and warnings.

**`/animation-template-lab`** designs candidate templates and experiment variants. It must not change a production template without version bump and test report.

**`/animation-review`** inspects a rendered output, contact sheet, metadata and QA report; it recommends fixes but does not silently alter approved product text or source assets.

### 11.2 Agent roles

| Agent | Responsibility | Must not do |
|---|---|---|
| `animation-director` | Goal, audience, creative strategy, template and platform recommendation | Invent product facts, technical capabilities, claims or brand details |
| `storyboard-architect` | Scene order, pacing, text placement, transitions, asset mapping | Write renderer code or fabricate assets |
| `animation-render-engineer` | Implement Python/Pillow/FFmpeg modules and performance optimizations | Change creative brief or relax profile constraints silently |
| `animation-qa-reviewer` | Inspect technical and visual output, verify platform compliance and asset fidelity | Approve unsupported facts or ignore blocking issues |
| `creative-experiment-analyst` | Design controlled variants, score candidates, analyze performance | Declare a winner without evidence or confuse correlation with causation |

Use subagents only for bounded, parallelizable work. The main skill remains accountable for the job state, user questions and final approval.

### 11.3 Rules files

- `animation-core.md`: immutable source assets, schema-first workflow, reproducibility, output manifests, no unsupported assumptions.
- `animation-assets.md`: file handling, path safety, checksums, page IDs, alignment requirements, fonts/music licensing.
- `animation-platform-exports.md`: platform-profile enforcement, safe zones, duration/aspect ratio/audio limits, mandatory FFprobe validation.
- `animation-brand-claims.md`: no invented claims, rights checks, approval for health/financial/legal/safety statements, accurate product representation.

Keep `CLAUDE.md` short. Add only a line directing Claude to `/create-animation` for marketing video generation and a reference to these rules. Do not dump the full animation specification into the always-loaded project instructions.

---

## 12. Initial SKILL.md content outline

Use this as the implementation brief for `.claude/skills/create-animation/SKILL.md`:

```markdown
---
name: create-animation
description: Plan, create, render, validate and export reusable promotional videos/GIFs for publishing products, Etsy listings, Instagram, Facebook and branded campaigns. Use when the user asks to create an animation, product promo, listing video, Reel, social ad or PSA.
---

# Create Animation

You are the orchestration layer for the reusable animation production pipeline.

## Required workflow
1. Parse all user-provided arguments before asking questions.
2. Detect whether this is a publishing-product showcase, an independent asset-based animation, or a generic campaign/PSA.
3. Load the product manifest and brand profile if supplied or discoverable from the current publishing job.
4. Use AskUserQuestion for only unresolved, material choices. Always mark a suitable default as Recommended.
5. Resolve platform profiles and template candidates from local config. WebSearch is not required.
6. Create a normalized AnimationJob and storyboard JSON. Validate both before rendering.
7. Keep the standard Pillow/FFmpeg renderer as the default. AI video is optional and must be explicitly enabled or accepted.
8. Generate a preview, contact sheet and QA report first unless the job is an approved repeatable batch.
9. Inspect the preview and enforce approval when required.
10. Render final exports, run FFprobe and platform validation, and produce a delivery manifest.

## Non-negotiable rules
- Never overwrite original book pages, covers, PDFs or brand source assets.
- Never invent product contents, page counts, included formats, results, claims, music rights or official affiliations.
- Do not use AI-generated text for logos, titles, prices, CTAs or facts. Render important text as editable overlays.
- Etsy exports must be silent and within the Etsy profile.
- Respect the chosen platform's aspect ratio, duration, file size and safe zones.
- Do not assume draw-things-cli can generate video; check its installed help/capabilities and use only a tested provider adapter.
- If a blocking QA check fails, fix it or report the blocker; never silently mark the job complete.

## Completion report
Return the output paths and a compact table of platform, dimensions, duration, fps, codecs, audio presence and file size. Include warnings, profile/template versions, approval state and QA report path.
```

Claude Code's skill discovery expects a directory under `.claude/skills/<skill-name>/` with a `SKILL.md` file. Use project-level skills for framework-specific workflows, subagents under `.claude/agents/`, and scoped rules under `.claude/rules/`.

---

## 13. A/B testing and template selection

Do not choose the final four templates by intuition alone, but do not pretend an offline visual score is proof of sales performance either. Separate **creative screening** from **live performance testing**.

### 13.1 Stage 1 — Candidate screening

Start with the 18 archetypes in Section 3. For each platform group:

1. Choose 2–3 representative products from different categories (e.g. coloring book, mandala, children's illustrated book, sketch collection, printable pack).
2. Generate comparable variants with identical product assets and verified facts.
3. Produce preview renders at the actual platform aspect ratio and mobile display size.
4. Use a blind review (human reviewers do not see template names) with this rubric, scoring 1–5:

| Criterion | Weight |
|---|---:|
| Product artwork remains clear and faithful | 25% |
| Product contents/value are easy to understand | 20% |
| First 1–2 seconds create attention / clear context | 15% |
| Platform fit and safe-zone compliance | 15% |
| Text readability and pacing | 10% |
| Brand coherence / visual quality | 10% |
| Technical robustness / rendering simplicity | 5% |

Calculate weighted score, record reviewer notes and reject any candidate with a blocking issue regardless of total score. Promote the best four per channel group as **provisional production templates**.

### 13.2 Stage 2 — Live experiments

**Meta Ads:** use Meta's available A/B or split-test capabilities where available. Keep audience, objective, placement, spend, schedule, copy and landing page comparable. Change one major creative variable at a time where possible. Record campaign/ad IDs and test window.

Suggested outcomes:
- 3-second video views / initial hold rate.
- Average watch time / video completion or ThruPlay where available.
- Outbound CTR and landing-page views.
- Add-to-cart / purchase conversion rate.
- CPA / ROAS when purchase tracking is valid.

**Organic Instagram/Facebook:** compare matched posts with similar timing, audience and copy. Record reach, watch time, saves, shares, profile activity, link clicks and attributable downstream outcomes where available. Do not compare unrelated posts and call it an A/B test.

**Etsy:** Etsy currently permits two listing videos, but the listing-level documentation does not describe a dedicated per-video A/B experiment or analytics attribution. If two videos appear together on one listing, it is not a clean randomized test of which video drove the purchase. Use a controlled sequential rotation or a matched-listing test only where appropriate, record date ranges and listing conditions, and label conclusions as directional. Control for seasonality, pricing, listing images, title/tags and promotional changes. Do not promise statistical certainty from small samples.

### 13.3 Experiment record

```json
{
  "experiment_id": "ig-reels-hook-test-001",
  "platform": "instagram_reels",
  "hypothesis": "A product-specific hook in the first 1.5 seconds improves early retention",
  "variants": ["IG-01-A", "IG-01-B"],
  "controlled_variables": ["audience", "budget", "caption", "landing_page", "schedule"],
  "changed_variable": "opening_scene",
  "start_date": "2026-11-01",
  "end_date": "2026-11-14",
  "metrics": ["three_second_views", "average_watch_time", "outbound_ctr", "purchases"],
  "result": "pending",
  "decision": "pending"
}
```

### 13.4 Winner logic

A template can be promoted from provisional to performance-validated only when:

- Technical QA passes consistently.
- Blind reviewer score is acceptable.
- Sample size / delivery is adequate for the platform and decision being made.
- Primary metric improves without unacceptable deterioration in purchase/conversion outcomes.
- Experiment record captures confounders and test conditions.

Keep the four production slots per platform, but maintain the candidate archive and version history. Re-test when platform profiles, brand identity, product category or template design changes materially.

---

## 14. Quality assurance gates

The QA system needs **blocking technical checks** and **creative review checks**.

### 14.1 Technical blocking checks

- Output exists and is non-empty.
- FFprobe can read it.
- Correct container/codec/pixel format/frame rate/dimensions.
- Correct exact aspect ratio (within profile tolerance; Etsy should use its specified ratio).
- Duration within minimum/maximum.
- File size below the platform maximum and internal target.
- Audio stream matches profile: absent for Etsy, as requested for social.
- No black frames at head/tail unless explicitly part of design.
- No unexpected blank frames, timestamp gaps or freeze sections.
- No clipped/off-canvas text and no text overlapping safe zones.
- No missing image, logo, font or music asset.
- No invalid or unsupported colour mode / alpha artefacts.
- All source product pages remain faithful and not visibly distorted.

### 14.2 Creative QA checks

- First frame tells the viewer what the product/campaign is.
- Product is visible for enough time to inspect; motion does not hide the content.
- Actual included pages are shown, not AI-invented substitutes.
- No misleading physical-product mockup for digital-only listings.
- Text is readable at phone size.
- Branding looks consistent.
- CTA is clear and accurate.
- AI video background does not compete with or modify the product artwork.
- Audio is rights-cleared and speech is intelligible.
- Claims and statistics match approved copy/source references.

### 14.3 QA scoring and decision

Return a machine-readable report:

```json
{
  "status": "passed_with_warnings",
  "checks": [
    {"id": "duration", "status": "passed", "actual": 12.0, "expected": "3–15s"},
    {"id": "audio", "status": "passed", "actual": "none", "expected": "none"},
    {"id": "file_size", "status": "passed", "actual_bytes": 18400000, "limit_bytes": 100000000},
    {"id": "safe_zone", "status": "not_applicable"},
    {"id": "page_fidelity", "status": "needs_human_review", "note": "Check detail crop around page 14"}
  ],
  "blocking_failures": [],
  "warnings": ["Human review requested for crop selection"],
  "preview_paths": ["preview/contact-sheet.jpg", "preview/preview.mp4"]
}
```

The final state must be one of `passed`, `passed_with_warnings`, `failed`, or `needs_human_review`. Never represent a warning as a pass without recording it.

### 14.4 Contact sheets and previews

For every job, generate:

- Storyboard timeline summary.
- Contact sheet of scene representative frames.
- Safe-zone overlay preview for vertical social profiles.
- Low-resolution preview MP4.
- Output metadata/FFprobe report.
- Optional side-by-side source-vs-render comparison for page artwork.

The contact sheet should show scene ID, duration, selected asset IDs and caption text so a person can quickly identify mistakes.

---

## 15. Security, reliability and rights

- Construct subprocess argument lists; do not concatenate user input into shell strings.
- Sanitize file names and reject path traversal.
- Validate all paths and restrict destructive operations to job output directories.
- Apply timeouts and capture stdout/stderr for FFmpeg and Draw Things processes.
- Use atomic writes for job/manifest updates.
- Support cancellation and clean up only intermediates owned by the current job.
- Do not delete source assets.
- Store licence/provenance for fonts, music, voiceover, photos and AI video inputs.
- Do not use third-party copyrighted music simply because it can be downloaded.
- For campaigns about health, smoking, medical products, financial matters or legal issues, require approved factual copy and a human review gate.
- No fabricated testimonials, endorsements, credentials, statistics, or government/charity affiliations.

---

## 16. CLI design

Expose a stable Python CLI; the skill should call it instead of embedding media logic in prompt instructions.

Suggested commands:

```bash
# Validate environment and tools
python -m animation_pipeline.cli doctor

# Show available profiles and templates
python -m animation_pipeline.cli profiles list
python -m animation_pipeline.cli templates list --platform etsy

# Create job from normalized JSON
python -m animation_pipeline.cli create --job ./job.json

# Generate/validate storyboard
python -m animation_pipeline.cli storyboard build --job-id <job_id>
python -m animation_pipeline.cli storyboard validate --job-id <job_id>

# Preview and final render
python -m animation_pipeline.cli preview --job-id <job_id>
python -m animation_pipeline.cli render --job-id <job_id> --quality final
python -m animation_pipeline.cli validate-output --job-id <job_id>

# Export additional formats
python -m animation_pipeline.cli export --job-id <job_id> --format gif

# Template experiments
python -m animation_pipeline.cli experiment create --config ./experiment.yaml
python -m animation_pipeline.cli experiment report --id <experiment_id>
```

`doctor` should check Python version, Pillow, FFmpeg, FFprobe, available FFmpeg encoders/filters, free disk space, writable output directory, fonts, optional AI provider availability, Draw Things CLI version/help, and model directory. It must not download models or change configuration without explicit permission.

---

## 17. Test strategy

### Unit tests

- Image contain/cover/fit math.
- Text overflow and safe-zone calculations.
- Crop anchor and Ken Burns coordinates.
- Reveal mask alignment and edge softness.
- Timeline frame conversion and transition overlaps.
- Template schema compatibility.
- Platform profile validation.
- File-size budget calculations.
- Audio policy enforcement.
- Path traversal and file validation.

### Integration tests

- Pillow scene asset → FFmpeg MP4 → FFprobe validation.
- Multiple page gallery crossfades.
- Audio and caption muxing.
- Silent Etsy export.
- GIF palette generation and file-size checks.
- Preview pipeline and final render equivalence.
- Resume after a failed stage.

### Golden-frame tests

Store small, deterministic source fixtures and approved reference frames. Compare generated frames with perceptual/image-diff thresholds. Do not use exact byte equality for all lossy encoded output; compare rendered frames before encoding or allow tolerances.

### Acceptance tests

1. Etsy job exports a 3–15 second, silent MP4 under 100 MB, with valid Etsy aspect ratio.
2. Instagram Reel exports at 9:16, 1080 × 1920, 30 fps, with safe-zone compliance.
3. Facebook Feed profile produces a separate feed composition, not a naive Reel crop.
4. An aligned grayscale/colour pair reveals cleanly with no double edges.
5. A misaligned grayscale/colour pair fails validation or asks for manual alignment.
6. An asset manifest with an incorrect page path fails before rendering.
7. A job can be resumed without regenerating unchanged AI artwork.
8. User can change page numbers, image count, timing and end card without code changes.
9. Draw Things video provider being unavailable does not prevent standard video output.
10. A health/PSA claim without approved source/copy requires review and is not autonomously embellished.

---

## 18. Implementation phases

Build the system in small, verifiable increments. Do not begin with AI video or A/B dashboards.

### Phase 0 — Repository and capability discovery

- Inspect existing `.claude/` layout, current publishing pipeline, product manifest format, existing Python environment and CLI conventions.
- Inspect installed FFmpeg/FFprobe versions and encoders/filters.
- Inspect `draw-things-cli --help` and `generate --help`; record actual installed version and documented capabilities.
- Identify how book pipeline emits product assets and where the post-generation hook belongs.
- Do not rename or restructure unrelated framework components.

**Deliverable:** discovery report + architecture decision record.

### Phase 1 — Core renderer foundation

- Create Python package, schemas, config loading, job store and CLI `doctor`.
- Implement source asset discovery and validation.
- Implement Pillow canvas/text/page composition.
- Implement one FFmpeg MP4 renderer and FFprobe validator.
- Add test fixtures and one basic gallery template.

**Deliverable:** one local MP4 generated from a cover and 3–4 page assets.

### Phase 2 — Etsy first production profile

- Implement both Etsy aspect ratio profiles from the current local profile snapshot.
- Add silent audio enforcement, 3–15s validation, 100 MB size cap and 1080 px+ working resolution.
- Build the six Etsy template candidates.
- Generate contact sheet and preview approval flow.

**Deliverable:** production-ready Etsy video flow.

### Phase 3 — Social outputs

- Add Instagram Reels, Instagram Feed, Facebook Feed and Facebook Reels profiles.
- Add safe-zone guides and text/caption layout.
- Add optional licensed audio and voiceover support.
- Add the six candidate templates for Instagram and six for Facebook; use the screening process to select the four initial production templates per group.
- Ensure each profile receives its own composition/crop; no blind resizing.

**Deliverable:** one job exports Etsy + Instagram + Facebook assets from one shared storyboard/creative brief where appropriate.

### Phase 4 — Publishing pipeline integration

- Add post-product-creation offer/trigger.
- Pass the product manifest to `/create-animation`.
- Save resulting paths and metadata back into the publishing record.
- Add a batch mode for trusted recurring outputs, with preview sampling and failure isolation.

**Deliverable:** book-to-promo automation.

### Phase 5 — Template lab and A/B workflow

- Generate variants from the initial candidate catalog.
- Implement blind review score sheets and report generation.
- Promote four provisional templates per channel group.
- Implement experiment metadata and import of platform metrics (manual CSV first; no need for API integration initially).
- Add promotion rules for performance-validated templates.

**Deliverable:** evidence-based template selection and versioning.

### Phase 6 — Draw Things AI video adapter

- Only after the standard renderer is stable, test a documented video interface.
- Benchmark SkyReels-V1, Wan and LTX-2.3 on the actual Mac.
- Build optional background generation, clip normalization and motion QA.
- Keep AI video off by default for bulk jobs.

**Deliverable:** opt-in AI-enhanced campaigns that do not destabilize the standard pipeline.

### Phase 7 — Expansion and operations

- Add website/WebM profiles and additional social destinations as needed.
- Optional subtitle files, thumbnail sets, language variants, localized text, template marketplace, analytics integrations.
- Add telemetry for render duration, failure rates, average file sizes, output profile, model generation time and acceptance score.

---

## 19. Recommended first end-to-end demonstration

Use an existing grayscale coloring-book product with a real cover plus four actual page images.

**Job:** `Majestic Queens — Etsy listing video`  
**Profile:** `etsy_listing_portrait`  
**Duration:** 12 seconds  
**Template:** `ETSY-01 page_gallery`  
**AI video:** disabled  
**Audio:** none

Suggested pacing:

| Time | Visual | Implementation |
|---|---|---|
| 0.0–1.5s | Cover and title, subtle push-in | Pillow cover composition + FFmpeg motion |
| 1.5–8.5s | Four actual pages, each with a readable display interval | Pillow page cards + FFmpeg crossfades |
| 8.5–10.5s | Detail crop of the strongest page | Crop anchor + subtle zoom |
| 10.5–12.0s | Cover / confirmed subtitle / digital-download label | Pillow text layout + final fade |

Then render an Instagram Reel from the same source assets with a different 9:16 storyboard and safe zones. The creative can be related, but the Reel should have a stronger opening hook, sound-aware design, and its own end card.

This first demo proves the most important thing: the system can make high-quality, repeatable marketing videos without AI video generation. Add the Draw Things video adapter only when the business case is clear.

---

## 20. Definition of done

The first production release is complete when:

- `/create-animation` works in all three entry modes.
- Prompt arguments are parsed before the skill asks questions.
- AskUserQuestion includes Recommended options and does not repeat known information.
- One product manifest can drive multiple platform exports.
- Templates are declarative and human-editable.
- A human can replace page IDs, image order, number of images, timing and text without code changes.
- Etsy exports comply with the local Etsy profile and contain no audio.
- Instagram and Facebook have distinct platform-aware compositions and safe-zone checks.
- MP4 is reliable; GIF is optional and secondary.
- Preview, contact sheet, QA report and manifest are generated for every job.
- Original book assets remain untouched.
- Jobs are resumable and failures are isolated.
- Four provisional production templates have been selected for Etsy, Instagram and Facebook from the six candidates per group through the documented screening process.
- The renderer works when Draw Things video generation is unavailable.
- The Draw Things adapter uses only a verified interface and reports unsupported status honestly.
- Final reports list paths, dimensions, duration, fps, codecs, audio status, file size, profile/template versions and QA status.

---

## 21. Local reference sources (checked 31 October 2026)

The implementation should not require Claude Code WebSearch. These local references are provided so an engineer can inspect the source if a policy/profile needs to be updated later.

### Etsy

- Etsy Help — How to Add Listing Videos: https://help.etsy.com/hc/en-us/articles/360053206073-How-to-Add-Listing-Videos
- Etsy Seller Handbook — 3 Types of Listing Videos That Online Shoppers Love: https://www.etsy.com/seller-handbook/article/3-types-of-listing-videos-that-online/821069530001
- Etsy Help — How to Create a Listing: https://help.etsy.com/hc/en-us/articles/115015628707-How-to-Create-a-Listing

### Meta / social placements

- Meta Ads Guide — Facebook Feed video: https://www.facebook.com/business/ads-guide/update/video
- Meta Ads Guide — Instagram Reels / video placements: https://www.facebook.com/business/ads-guide
- Media Cheat Sheet — Instagram specifications (reviewed 20 Aug 2026; summarizes Meta Ads Guide placement specs): https://mediacheatsheet.com/platform/instagram/
- AdTestBench — Meta ad specs with links to Meta Ads Guide pages (updated October 2026): https://adtestbench.com/guides/meta-ad-specs/

### Draw Things

- Draw Things community repository / README: https://github.com/drawthingsai/draw-things-community
- Draw Things release history: https://drawthings.ai/downloads/
- Draw Things CLI announcement: https://releases.drawthings.ai/p/draw-things-cli-local-media-generation

### Pillow

- Pillow Image module: https://pillow.readthedocs.io/en/latest/reference/Image.html
- Pillow ImageOps module: https://pillow.readthedocs.io/en/latest/reference/ImageOps.html
- Pillow ImageDraw module: https://pillow.readthedocs.io/en/latest/reference/ImageDraw.html

### FFmpeg

- FFmpeg Filters documentation: https://ffmpeg.org/ffmpeg-filters.html
- FFmpeg Formats documentation: https://ffmpeg.org/ffmpeg-formats.html
- FFmpeg FAQ (concatenation, filters and media handling): https://ffmpeg.org/faq.html

### Claude Code framework

- Claude Code skills documentation: https://code.claude.com/docs/en/skills
- Claude Code subagents documentation: https://code.claude.com/docs/en/sub-agents
- Anthropic — Steering Claude Code with skills, hooks, rules and subagents: https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more

---

## 22. Notes on the four supplied Etsy MP4 examples

The four supplied Etsy CDN URLs are retained as reference inputs in the original project brief. The web retrieval layer could not decode the MP4 streams in this research session, and the local runtime had no network access to download them. Consequently, this blueprint does **not** claim to have visually inspected or measured those four clips. During Phase 0, download them manually (where permitted) into `research/reference-videos/`, run FFprobe, extract representative frames/contact sheets, and record what works: pacing, number of pages, mockups, transitions, typography, music-independent storytelling and end-card design. Treat them as inspiration, not as templates to clone.

Suggested local analysis commands:

```bash
ffprobe -v error -show_streams -show_format -of json reference.mp4 > reference.probe.json
mkdir -p reference-frames
ffmpeg -i reference.mp4 -vf "fps=1,scale=640:-1" reference-frames/frame-%03d.jpg
```

This creates an inspectable frame sequence and metadata report that the template-lab agent can use without requiring WebSearch.
