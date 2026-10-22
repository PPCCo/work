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
