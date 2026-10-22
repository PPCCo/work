# Cover Quality Rubric

Used by the **cover-critic** agent (and by the director for self-checks). Score each generated cover against this rubric. Be strict: a bland but clean cover scores in the 60s, not the 80s.

---

## 1. Hard fails (any one = automatic REVISE, never SHIP)

| # | Hard fail |
|---|---|
| H1 | Any declared text layer is misspelled, missing, duplicated, or has altered characters |
| H2 | Any text appears that is **not** a declared layer (stray words, fake labels, gibberish letters) |
| H3 | Text is cut off by the edge, or sits inside the outer 8 % safe margin |
| H4 | Title is not readable at 160 px wide (use the thumbnail in the contact sheet) |
| H5 | Hero subject has obvious anatomical or structural defects (extra limbs/fingers, melted face, broken object) |
| H6 | Image shows a book mockup, 3D book, spine, drop-shadowed page or device frame instead of flat artwork |
| H7 | Contains a recognizable copyrighted character, brand mark or real person |
| H8 | Content inappropriate for the stated audience |
| H9 | Reference mode only: close copy of a reference (same subject **and** same layout **and** same palette; see §4) |

---

## 2. Scored criteria (100 points)

| Criterion | Pts | What earns the points |
|---|---|---|
| **Concept & originality** | 20 | One clear idea; a specific *moment* or metaphor; fresh, not stock; fits the book's actual content |
| **Focal clarity & composition** | 15 | A single focal point; value structure; archetype executed well; eye path title → subject → series → publisher; balanced; quiet zone respected |
| **Color & light** | 15 | Intentional 60/30/10 palette, clean harmony, an accent on the focal point, directional light, no mud |
| **Typography** | 20 | Correct spelling; clear hierarchy (title ≫ series ≫ publisher); lettering style matches the genre; good contrast; considered lockup; restrained effects |
| **Genre & audience fit** | 10 | Matches the playbook's promise; age-appropriate saturation and complexity; honest about the interior |
| **Craft & rendering** | 10 | Material and texture; consistent edges; detail economy; no artifacts or plastic skin |
| **Thumbnail impact** | 10 | At 160 px: subject silhouette and title survive; stands out among typical category covers |

**Typography is capped at 10/20 if any text error exists (H1/H2 also trigger a hard fail).**

---

## 3. Verdicts

| Total | Hard fails | Verdict | Action |
|---|---|---|---|
| ≥ 80 | none | **SHIP** | Final candidate |
| 70–79 | none | **REVISE** | Targeted prompt edits (≤ 3 changes), regenerate |
| < 70 | none | **REDO** | The concept or archetype is wrong; return to the concept step, not just prompt tweaks |
| any | ≥ 1 | **REVISE** (or **REDO** if the hard fail is concept-level, e.g. H7, H8, H9) | Fix the hard fail first |

Maximum **3 critique rounds** per variant. After the third, ship the best-scoring candidate, flag the remaining weaknesses in `cover_report.md`, and recommend a human look.

---

## 4. Bland detector (flag each; two or more flags caps *Concept & originality* at 10)

- Subject floating on a plain gradient or empty ground
- Everything at one scale; no depth planes
- Flat, directionless lighting
- Generic palette with no named accent
- Title looks pasted on rather than integrated into a lockup
- No story moment; the subject just faces the camera
- Material feels like plastic or airbrushed gloss
- Looks like something you would see on any stock-art cover in the category

---

## 5. Originality check (reference mode)

Put each output beside its source reference and answer:

1. Is the **subject** the same? (character, object, scene)
2. Is the **layout** the same? (focal placement, title position, framing)
3. Is the **palette** the same? (dominant hue family, accent)
4. Is the **lettering treatment** the same? (shape of lockup, effects)

- 0–1 "same": fine; the DNA was transferred, not copied.
- 2 "same": REVISE; change one more axis.
- 3–4 "same" or **same subject + same layout**: **H9 hard fail**, REDO the variant.

Shared DNA should be visible (mood, rendering approach, composition logic, typographic attitude). Shared *content* should not.

---

## 6. Critic output format

```json
{
  "id": "A",
  "total": 84,
  "scores": {
    "concept": 17, "composition": 13, "color_light": 13,
    "typography": 17, "genre_fit": 9, "craft": 8, "thumbnail": 7
  },
  "hard_fails": [],
  "bland_flags": [],
  "text_check": {
    "title":     {"expected": "…", "read": "…", "ok": true},
    "series":    {"expected": "…", "read": "…", "ok": true},
    "publisher": {"expected": "…", "read": "…", "ok": true}
  },
  "thumbnail_note": "Title legible; fox silhouette clear.",
  "originality_note": "n/a (no references)",
  "verdict": "SHIP",
  "fixes": []
}
```

`fixes` must be **prompt-level edits** drawn from the surgical fixes table in `qwen-prompt-craft.md` (maximum three per round), each naming the layer to change. Do not rewrite the whole prompt.
