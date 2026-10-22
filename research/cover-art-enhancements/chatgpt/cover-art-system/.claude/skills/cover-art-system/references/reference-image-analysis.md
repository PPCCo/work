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
