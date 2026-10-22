# Evaluation: `publish-puzzle` for Etsy digital products

# Cover Art System for your autonomous publishing framework

The main change I recommend is to separate cover-art direction from image-prompt generation.

Your existing recommendation engine can already choose settings and assemble prompts for Qwen Image. The missing layer is the creative decision-making that should happen before a prompt is written: understanding the book’s promise, choosing a distinctive visual concept, directing composition and typography, balancing visual hierarchy, and evaluating whether the proposed cover would stand out in a retail thumbnail.

A stronger system should make Claude behave like an art director working with an illustrator and an independent design critic, not like a form that fills in prompt parameters.

I’ve checked the published architecture of your [`publish-book`](https://github.com/PPCCo/publish-book?utm_source=chatgpt.com) and [`publish-puzzle`](https://github.com/PPCCo/publish-puzzle?utm_source=chatgpt.com) repositories. They already separate reusable Claude instructions from project assets and preserve distinct cover-approval gates. The design below follows that structure.&#x20;

## 1. The design principle

The system should answer these questions before constructing the image prompt:

- What must this cover make the reader feel or expect? Curiosity, delight, sophistication, calm, discovery, challenge, wonder, or something else appropriate to the actual book.
- What is the central visual idea? A memorable scene, a striking symbol, an unusual juxtaposition, an expressive character, a visual metaphor, or an art-directed pattern.
- Why will this composition work? Clear focal point, deliberate negative space, convincing depth, a controlled palette, and a title area that belongs to the composition.
- Why this design for this book? It must reflect the actual manuscript or book concept, not just its genre.
- What makes it distinctive? A deliberate creative choice—not a generic checklist of adjectives such as “beautiful, professional, modern, artistic, high quality.”
- How will it survive real-world use? The title must remain legible at thumbnail size, the illustration must support rather than compete with the title, and the design must suit the audience and publishing format.

The system should create several genuinely different art-directed concepts when appropriate, evaluate them independently, and only then prepare the prompts for Qwen Image.

## 2. Proposed file structure

This is a focused subsystem, not a second publishing framework. It uses two specialist agents, one principal skill, one reference standard, one machine-readable policy, and one deterministic preflight script.

```
.claude/
├── agents/
│   └── visual/
│       ├── cover-art-director.md
│       └── cover-art-critic.md
├── config/
│   └── cover-art-policy.json
├── scripts/
│   └── cover_art_preflight.py
└── skills/
    └── cover-art-system/
        ├── SKILL.md
        └── references/
            ├── cover-design-standard.md
            └── reference-image-analysis.md

docs/
└── COVER-ART-SYSTEM.md
```

The files have distinct responsibilities:

| File                          | Purpose                                                                         |
| ----------------------------- | ------------------------------------------------------------------------------- |
| `SKILL.md`                    | Runs the end-to-end process and produces the prompt package                     |
| `cover-design-standard.md`    | Defines the creative and commercial quality standard                            |
| `reference-image-analysis.md` | Governs reference analysis, abstraction, and originality                        |
| `cover-art-director.md`       | Creates book-specific concepts and image-generation prompts                     |
| `cover-art-critic.md`         | Independently scores concepts and identifies weak designs                       |
| `cover-art-policy.json`       | Makes non-negotiable rules and thresholds explicit                              |
| `cover_art_preflight.py`      | Checks the output structure, required metadata, and prompt-package completeness |
| `COVER-ART-SYSTEM.md`         | Explains installation, integration, operation, and acceptance tests             |

The script will validate the prompt package, not pretend to measure artistic quality mechanically. Visual judgment stays with Claude; final publishing and approval remain governed by your existing framework.

## 3. Download the system

Cover Art System — complete source bundle

7 files · Claude Code skill, critic, policy, validator, design standards and integration guide

Download the ZIP bundle

The system is designed as an additive extension for your existing repositories. The book framework already has a visual `art-director` and `book-generate-assets` skill, while the puzzle framework has a visual `art-director` and `product-build-cover` skill. I’ve designed this package to reuse those components rather than introduce a competing art director.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

+2



The contents below are the actual source files in the bundle. I have not committed changes to either GitHub repository.

## 4. Full contents of every generated file

### File 1 — `SKILL.md`

Path: `.claude/skills/cover-art-system/SKILL.md`

This is the main workflow Claude follows, from book analysis through concept generation, independent critique, prompt validation, candidate inspection, and handoff.

Open the file

````
---
name: cover-art-system
description: Art-directs distinctive, book-specific front-cover concepts and Qwen Image prompts for draw-things-cli; supports original concepts or user-supplied visual references, independent critique, and preflight validation.
---

# Cover Art System

## Purpose

Create a cover that feels designed for this particular book, not like a generic genre template. Treat image generation as the execution stage of an art direction process, not as the process itself. The publishing repositories already provide a shared visual `art-director` agent; use that agent as the creative lead and this skill/standard as the cover-specific brief. Do not add a duplicate art-director agent.

Use this skill whenever a project needs a new front cover, when existing cover prompts are bland or repetitive, or when the user supplies reference covers whose design principles should inform new work.

## Read these references

1. Read `references/cover-design-standard.md` for the craft standard, audience and product-specific guidance, prompt composition, and review rubric.
2. When one or more reference images are supplied, also read `references/reference-image-analysis.md`.
3. Read `.claude/config/cover-art-policy.json` before creating the final package. Treat it as the machine-readable source for thresholds and non-negotiable checks.

## Inputs and source of truth

Use the current project's approved brief, manuscript or content outline, audience, product type, trim/ratio, series metadata, publisher name, visual bible, and existing design constraints. Read the source artifacts rather than relying only on an old prompt. Do not invent book facts, series branding, publisher names, quotes, endorsements, badges, or credentials.

If the project files are incomplete, make reasonable design assumptions only when they do not alter factual metadata. Record assumptions in the package. Do not ask the user questions that the project files already answer. If the exact title or publisher identity is unavailable, stop before final prompt generation and report the missing source field.

The default output location is the current project’s `visuals/cover/` folder:

- `cover_prompt_package.json` — final structured brief, directions, prompts, reference analysis, critic scores, and generation plan.
- `cover_art_direction.md` — concise human-readable concept and art-direction summary.
- Keep generated candidate images and any image-review notes in the same cover folder, following the project's existing naming convention.

Do not overwrite existing approved cover assets or approvals. Create versioned candidates or ask the framework's existing artifact workflow to register a new version. Respect the existing project state machine and cover-approval gate.

## Operating modes

### Mode A — art direction from the book brief (default)

Use when there are no supplied reference images. Create **three materially different cover directions** before writing the full generation prompts. Vary the underlying creative idea, not just the colors or adjective list. Suitable directions might include a narrative moment, an evocative symbol, an editorial illustration, a graphic/typographic concept, a visual metaphor, a surprising scale shift, or an art-directed pattern—but choose only approaches that suit the actual book.

### Mode B — reference-inspired art direction

Use when the user supplies one or more images. Analyse each image separately and create **one distinct cover direction per supplied reference image** by default. Three references therefore produce three separately art-directed prompts for the same book. If a supplied image is unreadable or cannot be inspected, state that limitation and do not pretend to have analysed it.

For each reference, extract only abstract design lessons such as the role of negative space, contrast rhythm, visual density, palette relationship, depth, balance, shape language, texture, or the way typography is separated from imagery. Translate those lessons into imagery and meaning that belong to the book currently being published. Do not recreate the reference's specific subject, characters, signature composition, unique motifs, exact typography, logos, wording, or other distinctive expression. Never trace or closely imitate a supplied cover. See `references/reference-image-analysis.md`.

Reference images guide the design reasoning; they do not replace reading the book brief. The new cover must still make sense if the reference images are removed.

## Workflow

### 1. Build the creative brief

Extract and record:

- exact visible title, subtitle if any, series name if any, and publisher/imprint name;
- actual content promise, main subject, differentiator, audience age/experience, and intended emotional response;
- product type (for example, picture book, educational nonfiction, puzzle book, coloring book, workbook, mandala collection, art collection, anime illustration book, photography collection, or adult nonfiction);
- target format, aspect ratio, trim, bleed/print constraints if known, and whether this is a series cover;
- any established series visual language that must remain consistent;
- content, accessibility, cultural-sensitivity, safety, and factual constraints.

Write a one-sentence **cover promise** and a one-sentence **visual thesis**. The visual thesis must describe an actual image idea, not a list of styles. Example form: “A tiny botanist stands beneath an oversized glasshouse leaf, making the book’s promise of discovery visible through a playful scale contrast.” Make the content-specific idea different for every book.

### 2. Choose the design strategy before the rendering style

Use the existing `.claude/agents/visual/art-director.md` as the creative lead. Give it the current book brief, this skill’s `cover-design-standard.md`, the policy JSON, and (when present) the reference-analysis results. Ask it to return book-specific concepts and prompts using these additional cover requirements; do not replace or duplicate its wider visual-system responsibilities.

Decide the focal subject, the visual hook, the composition, the title-safe region, the palette logic, the depth/lighting, and the image-making medium. Select a medium because it strengthens the concept—do not default to “digital art, highly detailed, professional.” Avoid contradictory style stacks (for example, photorealistic watercolor anime vector art).

Each direction must name its intended reader response, the reason its image belongs to this specific book, the main focal point, composition, palette, typography relationship, and how it differs from the other directions. If the directions would look nearly identical as thumbnails, revise them before prompting.

### 3. Plan text as part of the composition

The exact title is the primary text element. Subtitle, series name, and publisher/imprint name follow the project’s hierarchy. Reserve a visually quiet area with sufficient contrast; make the text placement feel intentional rather than pasted into an accidental gap. Use exact supplied strings only—do not “improve” spelling, punctuation, capitalisation, or line breaks without permission.

Prompt Qwen Image to render the exact visible text, with explicit labels for each text line. Do not request additional words, fake publisher marks, random letters, price stickers, bestseller badges, barcodes, or decorative pseudo-text. A barcode belongs in the production layout stage, not the illustration prompt.

Text fidelity is a hard review gate. If the generated image contains wrong or garbled text after targeted retries, preserve the strongest artwork with a deliberate title-safe area and hand off the exact type to the existing layout/typesetting stage. Do not silently approve incorrect text merely because the art is strong. Record the fallback clearly; the user’s requested end state remains an accurate, integrated title, series line, and publisher line.

### 4. Write compact, art-directed prompts

Each prompt should follow this order:

1. **Book-specific visual idea** — what the image communicates about this exact book.
2. **Focal subject and action** — what the reader should notice first and why.
3. **Composition** — placement, scale, negative space, depth, foreground/background, eye path, and title-safe zone.
4. **Palette and light** — a coherent palette with a clear value/contrast plan.
5. **Rendering language** — a consistent medium, mark-making, texture, material, or photographic treatment.
6. **Typography plan and exact text** — title first, followed by subtitle/series/publisher as applicable.
7. **Cover-specific constraints** — portrait front-cover art, crop-safe margins, no mockup, no spine/back cover unless explicitly required.
8. **Exclusions** — only negatives that prevent likely failure; avoid a bloated generic negative-prompt list.

Write as an art director giving precise instructions to an illustrator. Name observable design choices rather than generic quality adjectives. Keep each prompt internally coherent and specific enough that a different image model could execute it.

Keep the negative prompt in its own field because draw-things-cli wrappers can differ in how they pass it. Do not invent unsupported CLI flags or alter the user’s configured model/sampler settings. This system creates the creative prompt package; existing draw-things-cli invocation and parameter-selection logic remains responsible for actual CLI arguments.

### 5. Run an independent critique

After the existing `art-director` has developed the directions, ask the new `cover-art-critic` agent to assess every direction against `references/cover-design-standard.md` and the policy JSON. The critic must not simply praise the director’s work or select the most elaborate prompt. It should judge the proposed image, not the amount of prompt text.

Score all dimensions from 1 to 5 and compute the weighted score from policy weights. A direction passes only when:

- it has no blocker;
- every critical dimension meets the policy threshold;
- its weighted score meets the policy minimum;
- its title hierarchy, thumbnail readability, audience fit, book specificity, and originality are convincing.

If a direction fails, revise the underlying concept rather than merely adding adjectives. Re-review after each revision. Limit the loop to the configured maximum; never hide a failed gate. Every candidate intended for generation must pass. If unresolved blockers remain, deliver the failed review and do not represent the package as production-ready.

### 6. Preflight the package

Create `cover_prompt_package.json` using the output contract below, then run:

```bash
python3 .claude/scripts/cover_art_preflight.py <project>/visuals/cover/cover_prompt_package.json
```

Use the actual project root and path as appropriate. Fix all errors and rerun the script. A passing script proves structure and declared constraints—not artistic quality. The independent critique remains required.

#### Output contract

The JSON object must contain:

- `schema_version`: currently `1.0`;
- `book`: `project_id`, `title`, `subtitle`, `series_name`, `publisher_name`, `product_type`, `audience`, `book_summary`, `cover_promise`, `visual_thesis`, `format`, `text_to_render`, and `assumptions`;
- `mode`: `brief` or `reference_inspired`;
- `reference_analysis`: `references` array plus `synthesis`; use an empty array in brief mode;
- `directions`: concept objects containing `id`, `concept_name`, `reader_effect`, `book_specific_rationale`, `visual_hook`, `focal_subject`, `composition`, `palette`, `rendering_language`, `typography_plan`, `prompt`, `negative_prompt`, `reference_id` (null in brief mode), and `distinctiveness_note`;
- `critic_review`: `ratings` array, `selected_direction_id`, and `selection_rationale`;
- `generation_plan`: `model`, `backend`, `requested_variants`, `max_revision_cycles`, and `text_fidelity_policy`.

Each `critic_review.ratings[]` entry must contain `direction_id`, `dimension_scores`, `weighted_score`, `blockers`, `revision_actions`, and `decision`. `decision` must be `pass` for every direction in a production-ready package. Use the dimension names and weights in `cover-art-policy.json` exactly.

The `book.text_to_render` object must include exact string fields `title`, `subtitle`, `series_name`, and `publisher_name`; empty strings are allowed only for genuinely absent subtitle or series metadata. The prompt must include every non-empty required visible string exactly as supplied. Never use a placeholder as if it were final metadata.

### 7. Generate and inspect candidates

Pass each approved direction’s `prompt` and, where supported by the current wrapper, `negative_prompt` to the configured draw-things-cli/Qwen Image workflow. Generate the number of candidates dictated by the existing generation policy; unless an existing policy says otherwise, make one first-pass image per direction so the concept comparison stays fair.

Inspect all outputs at full cover size and at a small retail-thumbnail size. Confirm the actual rendered text, focal hierarchy, crop, contrast, audience fit, visual polish, absence of unwanted objects/text, and distinctness among variants. Do not infer visual quality from prompt quality alone.

If a generated candidate fails, state the visible defect, change the prompt to address that defect, and regenerate only the affected direction when the pipeline allows. Do not keep adding random adjectives or change several unrelated variables in one revision. If accurate embedded lettering remains unreliable, use the title-safe-area fallback described in Step 3 and route the final typography through the framework’s layout stage.

### 8. Handoff

Save the package, art-direction summary, generated candidates, and any review notes using project conventions. Return:

- the concept names and the reason each belongs to this book;
- the prompt package path and preflight result;
- the candidate image paths and a brief comparison;
- any text-rendering or design limitation that still needs layout or human review.

Do not grant a cover approval, freeze an artifact, update lifecycle state, or release a book unless the framework’s existing approved workflow explicitly authorises that action. A cover-art pass is not a publishing approval.
````

### File 2 — `cover-design-standard.md`

Path: `.claude/skills/cover-art-system/references/cover-design-standard.md`

This is the core art-direction standard. It gives Claude concrete guidance on concept development, composition, typography, palettes, rendering styles, age groups, book categories, and visual review.

Open the file

```
# Cover Design Standard

## 1. The cover is a designed promise

A cover is not a decorative illustration with a title placed on it afterward. It is a single visual communication system: subject, metaphor, composition, colour, surface, typography, and negative space work together to tell the reader what kind of experience the book offers.

A strong cover is specific before it is stylish. “Whimsical”, “cinematic”, “minimal”, or “premium” are not concepts. They become useful only when translated into visible decisions that communicate this book’s actual subject and promise.

## 2. The design brief

Before concepting, answer the following in project notes:

- **Reader:** Who is expected to pick this up? Use the real age band and interests, not an undifferentiated “all ages”.
- **Promise:** What experience, knowledge, transformation, delight, or challenge does the book deliver?
- **One-sentence hook:** What makes this book materially different from a generic book in its category?
- **Emotional target:** What should the reader feel in the first second?
- **Focal subject:** What must be seen first?
- **Secondary read:** What additional meaning or story should reward a closer look?
- **Retail read:** What is still recognisable when the cover is a small thumbnail?
- **Text hierarchy:** What is the title, and which details are subordinate?
- **Format:** Portrait ratio, crop-safe space, trim/bleed requirements, and series continuity.

If these answers do not point to a particular image idea, the brief is not yet art-directed.

## 3. Non-negotiable craft principles

### A. One dominant idea

Use one primary visual hook and a deliberately limited set of supporting elements. Complexity is welcome when the hierarchy is controlled; indiscriminate detail is not. Every major element must support the book promise, provide useful atmosphere, or guide the eye.

### B. Deliberate visual hierarchy

Establish a clear first, second, and third read. Usually the title and the main visual hook dominate, with series/publisher information subordinate. Do not let decorative flourishes, background clutter, or secondary characters steal attention without a reason.

### C. Composition with intention

Direct attention through scale, placement, direction, shape, contrast, overlap, rhythm, and negative space. Avoid defaulting every cover to a centered subject with generic background particles. Explore asymmetry, framing, cropped forms, diagonals, silhouettes, layered depth, close-ups, visual tension, or calm expanses when these serve the concept.

### D. A palette with a job

Choose a limited, coherent colour relationship. Define the dominant colour, supporting colour(s), accent, and value contrast. Colours should reinforce mood, separate major forms, and protect title legibility. “Vibrant colours” alone is not a palette direction.

### E. Specific light, surface, and material

Use lighting and texture to create depth and emotional tone: diffused morning light, crisp hard-edged shadows, layered gouache, dry pencil grain, translucent watercolor blooms, matte screenprint shapes, tactile paper, luminous night contrast, or a photographic lens treatment. Select one coherent rendering language unless a deliberate mixed-media contrast is the concept.

### F. Typography belongs to the art direction

Specify the title's scale, placement, contrast, line breaks, spacing character, and relationship to the focal image. Be clear whether the desired impression is playful, literary, scholarly, elegant, energetic, hand-crafted, contemporary, or utilitarian. Do not ask the model to imitate a protected logo or a specific commercial book's lettering. Use exact title strings, protect clear space, and reject inaccurate generated text.

### G. Distinctiveness over decoration

The cover should contain a memorable decision: an unexpected but relevant metaphor, unusual scale, fresh silhouette, striking crop, strong negative-space shape, surprising colour relationship, emotionally meaningful action, or a composition that reflects the content. Effects such as glow, sparkles, lens flare, random geometric accents, and ornamental borders are not substitutes for a concept.

### H. Small-size recognition

Check a thumbnail simulation. The focal shape should remain identifiable; the title should not disappear into the background; fine details should not carry the whole concept; and the cover should have a clear silhouette/value structure even on a small screen.

### I. Audience respect

Avoid infantilising teens, making adult topics look like children’s activity books, or using visual stereotypes about age, culture, gender, disability, or subject matter. For younger audiences, clarity and emotional warmth usually matter more than dense detail. For adult markets, specificity and restraint are often stronger than generic ornament—but do not force minimalism onto a book whose appeal is exuberant.

### J. Honest content signalling

The image must represent the actual contents. Do not suggest skills, characters, subjects, guarantees, educational outcomes, or story events that the book does not provide. A beautiful but misleading cover is a failed cover.

## 4. Adapt the principles to the book type

These are starting points, not mandatory genre recipes. Always adapt them to the book brief.

| Product family | Design opportunities | Common failure to avoid |
|---|---|---|
| Early-childhood and picture books | Expressive character or object, emotionally readable action, bold silhouettes, simplified shapes, playful scale, warmth, generous title space | Too many small elements, generic smiling-character collage, type competing with faces |
| Early readers and chapter books | Clear story moment, lively silhouette, character relationship, sense of adventure, controlled detail | Stock fantasy props or scattered objects unrelated to the story |
| Middle-grade fiction and nonfiction | Wonder, discovery, layered visual clues, strong central metaphor, more sophisticated colour and depth | Cover looks too young, or too dense to read at thumbnail size |
| Teen / YA | Confident graphic idea, current editorial energy, striking symbolism, mood, typography as a strong design element | Infantilising illustration, trend imitation, overused dramatic fog and floating fragments |
| Educational / informational books for children | Clear subject cue plus a specific curiosity hook; accurately rendered objects, diagrams, environments or visual comparisons | School worksheet aesthetic, arbitrary icons, inaccurate science or misleading visual claims |
| Adult nonfiction / reference | Precise metaphor, strong editorial hierarchy, considered typography, material/photographic specificity, restraint where useful | Generic stock-photo layout, too many callouts, pseudo-academic badges |
| Puzzle, activity, and workbook books | Immediate category recognition, clear promise, energetic but controlled arrangement, legibility, visual clue or pattern | A collage of unrelated puzzle icons, crowded title block, tiny unreadable selling points |
| Children's coloring books | Strong recognisable subject, simple high-contrast line work or a colourful preview motif, friendly scale, age-appropriate complexity | The whole cover resembles an interior page without sales hierarchy; confusing line density |
| Adult coloring books and mandalas | Intricate but ordered pattern, deliberate symmetry or controlled asymmetry, tactile line quality, elegant negative space, sophisticated palette or monochrome | Generic mandala template, excessive micro-detail, pattern that obscures the title |
| Pencil / artistic sketch collections | Visible mark-making, paper character, purposeful unfinished edges, credible subject detail, gallery/editorial composition | Fake “hand-drawn” filters over digital images, random sketch clutter |
| Oil and watercolor painting collections | Medium-specific surface, pigment/brush behaviour, tonal structure, painterly focal hierarchy, authentic atmosphere | A generic filter that does not behave like the stated medium |
| Anime / 2D and 3D illustration collections | Strong pose/silhouette, expressive face or form, coherent art direction, controlled colour and cinematic/graphic staging where suitable | Unrequested fan art, derivative character designs, generic neon effects, conflicting 2D/3D cues |
| Photography / photorealism | Specific subject, considered lens perspective, believable light, decisive crop, intentional depth of field, editorial colour grade | Generic stock-photo look, accidental distortions, busy background, false documentary claims |
| Journals, planners, guided workbooks | Strong type system, tactile motif or symbolic object, usable simplicity, series consistency, appropriate calm/energy | Filler flourishes, faux luxury for its own sake, poor contrast, misleading productivity claims |

## 5. Audience calibration

### Preschool / early childhood

Prioritise instantly readable shapes, expressive gesture, friendly scale, controlled detail, warmth, and large high-contrast title treatment. One scene or character relationship is usually stronger than many competing objects.

### Primary / elementary-age readers

Use energy, narrative clues, discovery, playful contrast, and an illustration with enough detail to reward inspection. Keep the title/focal subject relationship clear and avoid generic sticker-like object piles.

### Middle grade

Allow richer world-building, layered clues, intricate textures, and more nuanced colour. Retain a simple dominant shape or story question at thumbnail size.

### Teen / YA

Use confident art direction, graphic impact, emotional atmosphere, symbolism, and typography that feels age-appropriate. Avoid defaulting to either childish character art or a generic dark, cinematic template.

### Adult general audience

Choose the visual register from the subject and the reader promise: editorial, literary, exuberant, intimate, technical, playful, contemplative, or premium. “Adult” does not automatically mean dark, minimal, or restrained.

### Senior readers / large-print products

Use stronger value contrast, less dependence on fine detail, clean hierarchy, and larger readable text in the eventual production layout. Ensure the artwork never makes the title harder to see.

## 6. Prompt-writing standard

A high-performing prompt is a compact design brief with executable visual instructions. Include the following, as applicable:

- book-specific meaning and intended emotional response;
- the main subject, action, and unique hook;
- precise composition and title-safe area;
- palette logic and value contrast;
- one coherent medium/rendering language;
- texture and lighting only where meaningful;
- exact visible text and relative hierarchy;
- portrait cover format, crop-safe edges, and exclusion of mockups;
- a short list of likely failure modes to avoid.

Avoid these prompt habits:

- piling on synonyms such as “masterpiece, award-winning, best quality, stunning, beautiful, professional”;
- listing many incompatible media or styles;
- generic atmosphere with no scene, subject, or relationship;
- “lots of details” without focal hierarchy;
- asking for “perfect typography” without specifying actual text and placement;
- overloading the negative prompt with unrelated failure terms;
- copying a reference cover's specific subject/composition rather than translating abstract design principles.

## 7. Review scorecard

Score every dimension from 1 to 5. Use the exact dimension names and weights in `.claude/config/cover-art-policy.json`.

- **1 — Failed:** major mismatch or unusable.
- **2 — Weak:** several significant problems; substantial redesign needed.
- **3 — Adequate:** workable, but ordinary or with clear unresolved weaknesses.
- **4 — Strong:** convincing, coherent, book-specific and close to production quality.
- **5 — Exceptional:** memorable, unusually well resolved, with strong control across the design.

Never inflate scores to pass a gate. Explain each score briefly with visible evidence. A prompt may be articulate while its concept is weak; judge the anticipated visual outcome. When actual candidate images are available, evaluate the images themselves rather than assuming the model followed the prompt.

## 8. Hard blockers

A direction cannot pass if it has any of the following:

- incorrect or invented required text, a missing required text line, or text placed where it cannot be read;
- material mismatch with the actual book or target reader;
- no clear visual hierarchy or no credible focal idea;
- a close imitation of a reference cover or use of unapproved protected marks/characters;
- age-inappropriate, offensive, misleading, or culturally stereotyped imagery;
- composition that leaves no workable way to place the required title and publisher information;
- unsupported marketing claims, fake awards/badges, or random extra lettering;
- a prompt package that fails deterministic preflight.

If a blocker cannot be resolved within the allowed revision cycle, report the blocker and stop treating the direction as production-ready.
```

### File 3 — `reference-image-analysis.md`

Path: `.claude/skills/cover-art-system/references/reference-image-analysis.md`

This implements the reference-image mode. For three supplied images, Claude analyses them individually and generates three new book-specific directions. It transfers abstract ideas such as negative space, contrast, balance, surface, and visual hierarchy—not the source covers' distinctive expression.

Open the file

```
# Reference Image Analysis and Originality Protocol

## Purpose

Use supplied images as evidence of design preferences, not as templates to reproduce. The goal is to discover which abstract visual principles appeal to the user and then invent a new cover that belongs to the current book.

## 1. Inventory and inspect each reference separately

Assign stable IDs in supplied order: `REF-01`, `REF-02`, and so on. For every image, record only what is actually visible:

- broad category and likely design intent (without assuming the reference book's content is the current book's content);
- primary and secondary focal points;
- composition and eye path;
- balance, symmetry/asymmetry, scale relationships, framing, and negative space;
- dominant/support/accent palette and value contrast;
- depth, lighting, texture, mark-making, and degree of detail;
- where title, subtitle, series and imprint information sit in the hierarchy;
- what makes the design feel distinctive at thumbnail size;
- any visible feature that should **not** be carried into the new cover.

Separate observation from interpretation. Example: “The upper third is a low-detail pale field” is observation; “the quiet upper field protects title legibility” is interpretation. Do not claim to read tiny or illegible wording.

## 2. Extract transferable principles

Good abstractions include:

- bold focal subject against a quieter field;
- strong diagonal movement balanced by a stable title block;
- limited warm/cool palette with one high-chroma accent;
- generous negative space and clear scale hierarchy;
- layered paper texture or visible painterly marks;
- tightly cropped subject with an unexpected point of view;
- symmetrical pattern balanced by asymmetric typography;
- a small human figure used to communicate scale or wonder;
- large simple silhouettes with richer detail concentrated at the focal point.

Do not treat these as a compulsory checklist. Extract only what is present in the image and useful for the current book.

## 3. Translate through the new book's meaning

For each reference, explicitly answer:

1. What abstract design lesson is worth retaining?
2. What element of the current book should become the new focal subject?
3. How should composition, palette, subject matter, and rendering change so the result communicates this book rather than the reference?
4. Which distinctive features of the reference are being deliberately avoided?
5. What would make this variant recognisably different from the variants derived from the other references?

Do not simply replace a reference's subject with a new subject while preserving the same distinctive arrangement. Transform several major axes—such as layout, camera/viewpoint, subject silhouette, colour relationship, and visual metaphor—so the result is independently art-directed.

## 4. Similarity boundaries

The following may be discussed at an abstract level: visual density, contrast, balance, colour relationships, medium, texture, negative space, broad genre conventions, and general typographic hierarchy.

Do not reproduce or instruct the image model to reproduce:

- the reference's exact or recognisably close composition, crop, or placement of distinctive objects;
- a specific character, mascot, proprietary illustration, unique motif, or identifiable fictional character;
- logos, wordmarks, author names, publisher names, or exact lettering from the reference;
- unique ornamental details, signatures, watermarks, or text placement that forms a distinctive overall trade dress;
- a named living artist's style or a prompt designed to make the output pass as a specific artist's work.

A user supplying a reference does not automatically make its protected expressive details safe to copy. Work from abstract traits and original subject matter. If a reference contains a logo or text treatment the user owns and explicitly needs to reuse, preserve it as a separately supplied approved brand asset through the normal design/layout path rather than asking the image model to redraw it.

## 5. One reference, one direction

When there are N supplied images, create N direction records by default, one inspired by each reference's abstract design principles. The book brief remains constant across all N directions. The variants should share the required metadata, audience, book promise, and production constraints, but differ in concept, subject treatment, composition, or rendering approach—not just palette.

For each direction, include:

- `reference_id` linking it to its source analysis;
- `book_specific_rationale` explaining how it reflects the actual book;
- `distinctiveness_note` explaining how it departs from the reference and from other variants;
- the specific transferable principles used;
- the major source features deliberately not copied.

If several references are nearly identical, still account for each by ID but find a genuinely different transferable lesson in each image. Do not invent differences that cannot be observed. If the references provide no useful design clue for the book, say so and use only the limited, abstract lessons that are supportable.

## 6. Keep reference mode honest

The final cover prompt must stand on the current book's own brief. It should contain enough book-specific subject matter that it would not plausibly be used unchanged for the reference's original book. Do not include phrases such as “same as reference”, “identical layout”, “replicate this cover”, or “make it look exactly like image 1”. Use concrete abstract instructions instead: for example, “retain the high-level balance of a dense lower focal area and a quiet title field, but build a new scene using the book's own subject, a different point of view, an original silhouette and a new colour relationship.”
```

### File 4 — `cover-art-critic.md`

Path: `.claude/agents/visual/cover-art-critic.md`

This is the new specialist agent. Its role is independent criticism, not duplicate art direction. It identifies weak concepts, provides evidence-based scores, enforces the originality boundary, and prevents a concept from passing merely because its prompt sounds sophisticated.

Open the file

````
---
name: cover-art-critic
description: Independently critiques book-cover concepts and generated candidates for specificity, hierarchy, composition, text accuracy, audience fit, originality, and thumbnail readability.
effort: high
permissionMode: default
maxTurns: 30
tools:
  - Read
  - Grep
  - Glob
memory: project
background: false
color: purple
---

# Cover Art Critic

## Role

Act as an independent, demanding creative director and retail-cover reviewer. Your task is to find why a proposed cover might look generic, fail the book, lose impact at thumbnail size, or be difficult to execute—not to validate the creator's effort.

## Required reading

Read `cover-design-standard.md` and `.claude/config/cover-art-policy.json`. In reference-inspired mode, inspect `reference-image-analysis.md` and the reference-to-direction mappings. Use the actual book brief and visible candidate images when available.

## Review method

Evaluate every direction independently. If rendered candidates exist, judge the image itself; a well-written prompt is not evidence of a well-executed design. If no image exists yet, judge the design proposal and identify likely execution risks without pretending to know how the model will render it.

Ask:

- Does this idea belong to this specific book, or could the prompt be reused for hundreds of unrelated books?
- Is there a memorable visual hook that can be named in one sentence?
- Is the first-read hierarchy clear? Is the title the right scale relative to the image?
- Is composition deliberately art-directed, with purposeful negative space, eye path, depth, scale, and crop?
- Does the palette have a clear relationship and sufficient value contrast?
- Is the rendering medium coherent and meaningful rather than an arbitrary style tag?
- Does it signal the right audience and product type without relying on cliché or stereotype?
- Will the main idea survive a retail thumbnail?
- Are exact title/subtitle/series/publisher strings preserved, with no invented lettering or marks?
- In reference mode, are the borrowed lessons abstract, and have distinctive source features been changed rather than copied?
- Are the directions materially different from one another, not simply alternate colourways?

## Scorecard

For each direction, supply all eight dimensions from 1 to 5 using the exact keys in the policy:

- `book_specificity`
- `visual_hook`
- `composition`
- `palette_and_rendering`
- `typography`
- `audience_fit`
- `thumbnail_readability`
- `originality`

Compute `weighted_score` as the sum of `(dimension_score / 5) * dimension_weight`, rounded to one decimal. Use the policy's weights. Apply the critical-dimension floor and weighted minimum exactly. Do not inflate scores because the prompt is eloquent.

## Blockers

A blocker is a concrete failure that prevents a direction from passing: wrong/missing text, book-content mismatch, weak or absent hierarchy, audience mismatch, close copying, false claims/marks, no viable title-safe space, or another item listed as a hard blocker in the standard. Record blockers as concise strings. If none exist, use an empty array.

For every direction return:

```json
{
  "direction_id": "A",
  "dimension_scores": {
    "book_specificity": 4,
    "visual_hook": 4,
    "composition": 4,
    "palette_and_rendering": 4,
    "typography": 4,
    "audience_fit": 4,
    "thumbnail_readability": 4,
    "originality": 4
  },
  "weighted_score": 80.0,
  "blockers": [],
  "revision_actions": ["A specific improvement if needed; otherwise leave the array empty."],
  "decision": "revise"
}
```

The values above are a format example only; recalculate scores for the actual direction. `decision` must be `pass`, `revise`, or `reject`. Passing requires no blockers, every critical dimension at or above the policy floor, and the weighted score at or above the policy minimum.

## Useful criticism, not vague criticism

Weak feedback: “Make it more artistic.”

Useful feedback: “The central object is the same size as the background decorations, so the eye has no entry point. Increase the focal object's scale, move the secondary objects to the perimeter, and keep the upper 25% low-detail for the two-line title.”

A revision must address the cause of the weakness. Do not recommend piling on more quality adjectives or generic negative tokens.

## Final selection

Select a preferred direction only from those that pass. If the task requires multiple reference-derived variants, all requested variants must pass individually; do not hide a failed variant by selecting just one winner. If no direction passes after the allowed revision cycle, return the failures and advise that the package is not production-ready. Never grant framework-level cover approval or release permission.
````

### File 5 — `cover-art-policy.json`

Path: `.claude/config/cover-art-policy.json`

This holds the numerical thresholds and non-negotiable rules in one machine-readable place. Changing the scoring thresholds here updates the preflight validator's expected values too.

Open the file

```
{
  "schema_version": "1.0",
  "description": "Creative and structural policy for book-cover prompt packages targeting draw-things-cli with Qwen Image.",
  "modes": {
    "brief": {
      "minimum_directions": 3,
      "direction_rule": "Create at least three materially different art directions from the current book brief. Differences must be conceptual, compositional, or representational, not just palette changes."
    },
    "reference_inspired": {
      "minimum_references": 1,
      "directions_per_reference": 1,
      "direction_rule": "Create one distinct book-specific direction for each supplied reference image, preserving source IDs and abstract design lessons while changing distinctive expression."
    }
  },
  "review": {
    "score_scale": {
      "minimum": 1,
      "maximum": 5,
      "descriptions": {
        "1": "Failed: major mismatch or unusable.",
        "2": "Weak: several significant problems; substantial redesign needed.",
        "3": "Adequate: workable, but ordinary or with meaningful weaknesses.",
        "4": "Strong: convincing, coherent, book-specific and close to production quality.",
        "5": "Exceptional: memorable and unusually well resolved."
      }
    },
    "dimension_weights": {
      "book_specificity": 20,
      "visual_hook": 15,
      "composition": 15,
      "palette_and_rendering": 10,
      "typography": 15,
      "audience_fit": 10,
      "thumbnail_readability": 10,
      "originality": 5
    },
    "critical_dimensions": [
      "book_specificity",
      "visual_hook",
      "composition",
      "typography",
      "audience_fit",
      "thumbnail_readability",
      "originality"
    ],
    "minimum_critical_score": 4.0,
    "minimum_weighted_score": 84.0,
    "maximum_revision_cycles": 2,
    "all_requested_directions_must_pass": true
  },
  "references": {
    "one_direction_per_image": true,
    "copy_policy": "Transfer only abstract design principles such as contrast, negative space, visual density, broad palette relationships, surface, depth, balance, and typographic hierarchy. Re-invent subject, silhouette, viewpoint, distinctive arrangement, motifs, typography and wording for the current book.",
    "do_not_copy": [
      "exact or recognisably close composition, crop, or placement of distinctive objects",
      "specific characters, mascots, proprietary illustrations, or identifiable fictional characters",
      "logos, wordmarks, author or publisher text, or exact lettering from a reference",
      "distinctive ornamental motifs, signatures, watermarks, or identifiable trade dress",
      "a named living artist's style or an instruction to pass off the work as that artist's work"
    ]
  },
  "text": {
    "required_fields": [
      "title",
      "subtitle",
      "series_name",
      "publisher_name"
    ],
    "always_require_title_and_publisher": true,
    "allow_empty_subtitle": true,
    "allow_empty_series_name": true,
    "exact_text_required": true,
    "no_unrequested_text": true,
    "garbled_or_incorrect_required_text_is_blocker": true,
    "fallback": "If embedded text remains inaccurate after targeted retries, preserve a deliberate title-safe area and hand exact typography to the established layout/typesetting stage. Do not silently accept incorrect lettering."
  },
  "generation": {
    "model_family": "qwen_image_2512",
    "backend": "draw-things-cli",
    "do_not_invent_cli_flags": true,
    "preserve_existing_sampler_and_parameter_policy": true,
    "one_first_pass_image_per_direction_unless_existing_policy_overrides": true,
    "inspect_full_size_and_thumbnail": true
  },
  "package": {
    "schema_version": "1.0",
    "required_top_level_keys": [
      "schema_version",
      "book",
      "mode",
      "reference_analysis",
      "directions",
      "critic_review",
      "generation_plan"
    ],
    "required_book_keys": [
      "project_id",
      "title",
      "subtitle",
      "series_name",
      "publisher_name",
      "product_type",
      "audience",
      "book_summary",
      "cover_promise",
      "visual_thesis",
      "format",
      "text_to_render",
      "assumptions"
    ],
    "required_direction_keys": [
      "id",
      "concept_name",
      "reader_effect",
      "book_specific_rationale",
      "visual_hook",
      "focal_subject",
      "composition",
      "palette",
      "rendering_language",
      "typography_plan",
      "prompt",
      "negative_prompt",
      "reference_id",
      "distinctiveness_note"
    ],
    "required_rating_keys": [
      "direction_id",
      "dimension_scores",
      "weighted_score",
      "blockers",
      "revision_actions",
      "decision"
    ],
    "passing_decision": "pass"
  }
}
```

### File 6 — `cover_art_preflight.py`

Path: `.claude/scripts/cover_art_preflight.py`

This is the deterministic quality gate. It checks package structure, exact required text strings in prompts, direction uniqueness, reference-to-direction mapping, score calculations, unresolved review blockers, and generation settings. It intentionally does not claim to score artistic quality by code.

Open the file

```
#!/usr/bin/env python3"""Validate the structure and declared quality gates of a cover prompt package.This checker is intentionally deterministic and dependency-free. It cannot assesswhether an image is beautiful or whether Qwen followed a prompt; Claude's independentcover-art critique and visual review remain mandatory."""from __future__ import annotationsimport argparseimport jsonimport reimport sysfrom pathlib import Pathfrom typing import AnySCRIPT_DIR = Path(__file__).resolve().parentDEFAULT_POLICY = SCRIPT_DIR.parent / "config" / "cover-art-policy.json"PLACEHOLDER_RE = re.compile(    r"\[(?:BOOK\s+)?(?:TITLE|SERIES\s+NAME|PUBLISHER\s+NAME|INSERT[^\]]*)\]"    r"|\b(?:TODO|TBD|INSERT\s+TITLE|BOOK\s+TITLE\s+HERE|REPLACE\s+ME)\b",    re.IGNORECASE,)class PackageValidationError(Exception):    """Raised when package/policy files cannot be processed."""def load_json(path: Path) -> dict[str, Any]:    try:
```

### File 7 — `COVER-ART-SYSTEM.md`

Path: `docs/COVER-ART-SYSTEM.md`

This explains how to install and connect the new system to your current framework, including the reference-image workflow, running preflight, the scoring gates, and acceptance tests.

Open the file

````
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

The director creates concepts; the critic scores them independently. The current policy weights total 100 points:

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
````

## 5. Validation results

Python validator compiled successfully

Standard-library only; no additional packages required.

Brief-mode test passed

Validated a package with three distinct cover directions and complete scoring.

Reference-mode test passed

Three reference images mapped to three cover directions.

Negative test passed

An unresolved title placeholder correctly caused validation failure.

## 6. Recommended integration order

First, copy the new files into your framework. Then route the existing cover-generation stage through `cover-art-system` before its current Qwen Image / `draw-things-cli` invocation. In `publish-book`, that means integrating with `book-generate-assets`; in `publish-puzzle`, integrate with `product-build-cover`.

The bundle includes the new subsystem and its integration guide, but does not automatically patch those existing skill files. That final wiring should preserve each framework's current provider invocation, provenance records, state transitions, and approval requirements.

One key design decision is deliberate: the system doesn't assume that a longer prompt will produce a better cover. It requires Claude to develop the visual idea first, get independent criticism, and then construct the generation prompt. This is the part intended to address the bland, mechanical output you described.

The complete source bundle is available here again for convenience:
