# Standard: cover typography

Type is the part of the cover a machine can get exactly right, so there is no
excuse for getting it wrong. All of it is set by `cover_compose.py` from real
font files.

---

## 1. Licensing comes first

A cover is commercial use, distributed worldwide, often embedded in a PDF. Before
a family is used at all, confirm the licence permits commercial use and
embedding, and record it in the rights register with the version.

Safe defaults: fonts under the SIL Open Font License, which permits commercial
use and embedding without a fee. The pairings below are all OFL. Never use a font
that shipped with an operating system or an office suite unless its EULA
explicitly covers redistribution inside a commercial cover file, and never use a
font found on a free-font aggregator without tracing it to its licence.

## 2. Pairings by audience

One display face for the title, one text face for everything else. Two families
maximum per cover.

| Audience | Title | Text | Character |
|---|---|---|---|
| early-reader-6-8 | Baloo 2, Fredoka, Poppins ExtraBold | Poppins, Nunito | round, thick, cheerful, high x-height |
| middle-grade-9-12 | Bangers, Luckiest Guy, Archivo Black | Nunito Sans, Source Sans 3 | energetic, slightly cinematic, never babyish |
| teen-13-17 | Archivo Black, Space Grotesk Bold, Anton | Inter, Work Sans | designed, editorial, confident |
| adult-general | Fraunces, Playfair Display, Source Serif 4, Inter Tight | Inter, Source Sans 3 | calm, credible, premium |

Activity and puzzle books for any age take the heaviest, plainest face available
— they are bought for utility, and legibility in a thumbnail is the whole pitch.

## 3. Sizing rules

The composer fits type automatically, then reports what it chose. The reported
numbers must land inside these bounds:

- **Title height**: 10–20% of cover height. Under 10% fails the thumbnail; over
  20% usually means the title is too short to need that much room or the art has
  been squeezed out.
- **Title lines**: one or two. Three only for a long non-fiction title, and then
  the subtitle should shrink or go.
- **Subtitle**: 35–50% of title size.
- **Author**: 30–45% of title size. Larger when the author name is the brand.
- **Back-cover body**: 10–12 pt for adult, 12–14 pt for children's and
  large-print titles. Below 10 pt is unreadable on a printed back cover.
- **Spine text**: fills the spine width minus 0.0625 in clearance each side.

## 4. Setting rules

- Title in title case or all caps; never sentence case with a full stop.
- Tracking: tighten display type slightly, open up all-caps text.
- One alignment per cover. Centre for children's and activity; left for teen and
  adult editorial.
- Never stretch or condense a face non-uniformly to fit. Pick a smaller size or a
  condensed cut.
- No drop shadows, bevels, outlines or gradients on type, with one exception: a
  single flat stroke or a flat scrim where contrast genuinely requires it.
- Hyphenation off. Break title lines on meaning, not on width — if the automatic
  wrap splits the title badly, pass the break explicitly.

## 5. Print production

- All text is drawn at 300 DPI in the composed raster, and appears as live text
  in the SVG master. If a PDF is produced by a design tool from the SVG, fonts
  must be embedded or converted to outlines before upload.
- Keep every element inside the safe area: 0.25 in from trim on all sides, and
  0.625 in clear of the spine on a hardcover, where the hinge crease distorts.
- Black text for print should be a single ink where the channel accepts CMYK, not
  a four-colour build, or it registers soft.

## 6. Checks the composer performs

`cover_compose.py` fails the build when text leaves the safe area or back-cover
copy reaches the barcode zone, and reports title size, title share of cover
height, and measured contrast. `thumbnail_test.py` then renders 80/120/240 px
versions. Look at the 80 px file. If the title cannot be read aloud in one
second, the typography is wrong regardless of what the numbers say.
