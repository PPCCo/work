# Standard: cover design

Applies to every cover produced by this framework, in every format and on every
channel. Read with `cover-audience-standard.md` (who it is for),
`cover-typography-standard.md` (how the type is set) and
`cover-channel-specs.md` (what each retailer requires).

---

## 1. The division of labour

**The image model renders artwork. It never renders words.**

FLUX.2 [klein] can produce legible short text, but a cover title has to be
correct at every size, in a specified typeface, at a specified position, with the
same wording as the metadata record — and it has to be editable when the subtitle
changes. A diffusion model can promise none of that. So:

| Layer | Owner | Tool |
|---|---|---|
| Artwork | Klein 4B via ComfyUI | `cover_prompt.py` → the generation MCP |
| Geometry | deterministic arithmetic | `cover_spec.py` |
| Typography and assembly | real font files at 300 DPI | `cover_compose.py` |
| Verification | machine checks + human judgement | `thumbnail_test.py`, `cover_preflight.py` |

Any prompt that asks Klein for a title, a subtitle, an author name, a series
name, a price or a barcode is a defect, and `cover_prompt.py` blocks it.

## 2. The thumbnail is the product

A cover's first job is to survive at roughly 80 pixels wide, in a grid, on a
phone, beside twenty competitors. Everything else is secondary. Concretely:

- **One hero idea.** One subject, one action, one focal point. A cover that needs
  a second look to parse has already lost the sale.
- **Silhouette test.** Fill the hero subject with solid black. If it is still
  identifiable, the composition works. If it becomes a blob, simplify.
- **Title occupies at least 10% of cover height**, ideally 12–18% for children's
  and activity titles. `cover_compose.py` reports this number.
- **Contrast floor of 4.5:1** between title and whatever sits behind it. The
  composer measures it and drops a scrim if the art fails — but a scrim is a
  patch. The better fix is art with a genuinely calm type zone.
- **Maximum three type elements on the front**: title, subtitle, author. Series
  name counts as a fourth only when the series is the selling point.
- **No fine detail below about 2% of cover width.** It becomes noise in a grid.

## 3. The type zone is designed, not found

Cover art is generated with an explicit empty region reserved for type, named in
the art plan (`top-third`, `top-half`, `bottom-third`, `center-band`). This is
the difference between a cover and an illustration with words dropped on it.

Choose the zone before generating art, not after:

- **top-third** — default for children's and activity titles; the hero sits below
  the title and both get room.
- **top-half** — long titles, subtitle-heavy non-fiction, adult minimal covers.
- **bottom-third** — when the art needs the sky or upper field (landscapes,
  single tall objects), common for teen covers.
- **center-band** — type-led designs where art is decoration top and bottom.

## 4. Series consistency

Books are bought in sets. A series is recognisable when these are identical
across every title: style pack signature, palette, type zone, font pairing,
title position, author position, and the spine treatment. Only the hero subject,
the title words and one accent colour may vary.

Record the locked values in the series record so book seven does not drift. Any
change to a locked value is a decision about the whole series, and re-covering
the backlist is part of the cost.

## 5. Front, back and spine have different jobs

**Front** sells. Hero art, type zone, title, author. It is the only face that
must work as a thumbnail.

**Back** converts someone already interested. It carries a headline, a short
blurb, up to five bullets, and the publisher line. Its artwork is a quiet, low
contrast extension of the front so text stays legible. The lower-right corner of
the back cover (2 × 1.2 in, towards the spine) is reserved for the retailer
barcode: solid light fill, nothing else, ever.

**Spine** is for the shelf and for the product photo. Text is only permitted
above the channel's page minimum (79 pages on KDP). Below that, carry the
background colour across. Spine text reads top to bottom in English-language
markets.

## 6. What disqualifies a cover

- Any text rendered by the image model.
- Text outside the safe area, or artwork that stops before the bleed edge.
- Anything inside the barcode zone.
- A likeness of a real, identifiable person, or a real child.
- Named commercial characters, franchises, logos, or a style described by a
  living artist's name.
- Fonts without a licence that covers commercial book covers.
- A cover that materially misrepresents the interior: a puzzle book cover
  implying 200 puzzles when there are 60, or illustration style on the cover that
  does not appear inside.
- For a children's title: anything frightening, sexualised, or showing a child in
  unresolved danger.

## 7. Quality bar

A cover reaching the final gate scores at least 4.0/5 on each of: thumbnail
legibility, category fit, hierarchy, craft, and series consistency; and at least
4.5/5 on age fit for children's titles. Machine gates
(`thumbnail_test.py`, `cover_preflight.py`) must return zero blockers. A human
approves the final artefact hash before packaging, as with any other artefact.

## 8. Disclosure and rights

Generated cover artwork is disclosed as AI-assisted where the channel asks for it
(KDP asks during publishing; the disclosure is private to the retailer). Record
in the rights register: the model and version, the prompt, the seed, the font
families with their licences, and any stock or reference material used. A cover
with no recorded provenance cannot clear the rights check.
