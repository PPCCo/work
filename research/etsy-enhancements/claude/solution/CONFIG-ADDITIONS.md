# Config additions

Copy each JSON block into the named file. Blocks marked **new file** are standalone; blocks marked **merge** are keys to add inside the existing file. All blocks are valid JSON and are checked by `framework validate` once saved.

## 1. `config/kit_components.json` (new file)

```json
{
  "schema_version": "1.0",
  "notes": "Component catalogue for digital-kit products. 'verifier' is the primary route; 'generator' names a deterministic generator when one exists, else an authoring agent.",
  "components": {
    "craft-card":        {"label": "Guided craft card",        "author": "craft-designer",      "generator": null,             "verifier": "desk-check", "hazard_tags_allowed": ["scissors","craft-knife","hot-glue","heat","small-parts","paint","glitter","sharp-point","edible","allergen","water"]},
    "gift-project":      {"label": "DIY gift project",         "author": "craft-designer",      "generator": null,             "verifier": "desk-check", "hazard_tags_allowed": ["scissors","craft-knife","hot-glue","heat","small-parts","paint","glitter","sharp-point","edible","allergen","water"]},
    "gift-tag":          {"label": "Printable gift tag",       "author": "keepsake-designer",   "generator": "cutgrid",        "verifier": "code"},
    "keepsake-card":     {"label": "Keepsake card",            "author": "keepsake-designer",   "generator": "cutgrid",        "verifier": "code"},
    "ornament-template": {"label": "Ornament design template", "author": "keepsake-designer",   "generator": null,             "verifier": "desk-check"},
    "host-guide":        {"label": "Host guide",               "author": "kit-architect",       "generator": null,             "verifier": "desk-check"},
    "checklist":         {"label": "Checklist",                "author": "kit-architect",       "generator": "checklist",      "verifier": "code"},
    "shopping-list":     {"label": "Shopping list",            "author": null,                  "generator": "shopping_list",  "verifier": "code"},
    "schedule":          {"label": "Activity schedule",        "author": null,                  "generator": "schedule",       "verifier": "code"},
    "safety-notes":      {"label": "Safety notes page",        "author": "craft-safety-reviewer","generator": null,            "verifier": "desk-check"},
    "certificate":       {"label": "Certificate",              "author": "keepsake-designer",   "generator": null,             "verifier": "code", "editable_default": true},
    "passport":          {"label": "Holiday passport",         "author": "keepsake-designer",   "generator": null,             "verifier": "code", "editable_default": true},
    "profile-sheet":     {"label": "Keepsake profile sheet",   "author": "keepsake-designer",   "generator": null,             "verifier": "code", "editable_default": true},
    "wish-list-page":    {"label": "Wish list page",           "author": "keepsake-designer",   "generator": null,             "verifier": "desk-check", "editable_default": true},
    "photo-frame":       {"label": "Photo frame page",         "author": "keepsake-designer",   "generator": null,             "verifier": "code"},
    "memory-tracker":    {"label": "Annual memory tracker",    "author": "keepsake-designer",   "generator": "tracker",        "verifier": "code"},
    "letter-template":   {"label": "Letter template",          "author": "keepsake-designer",   "generator": null,             "verifier": "desk-check", "editable_default": true},
    "invitation":        {"label": "Invitation",               "author": "keepsake-designer",   "generator": null,             "verifier": "code", "editable_default": true},
    "rsvp-tracker":      {"label": "RSVP tracker",             "author": null,                  "generator": "tracker",        "verifier": "code", "editable_default": true},
    "signup-sheet":      {"label": "Contribution sign-up",     "author": null,                  "generator": "checklist",      "verifier": "code", "editable_default": true},
    "game-bingo":        {"label": "Bingo",                    "author": null,                  "generator": "bingo",          "verifier": "code"},
    "game-trivia":       {"label": "Trivia",                   "author": "party-game-designer", "generator": null,             "verifier": "fact-check"},
    "game-charades":     {"label": "Charades prompts",         "author": "party-game-designer", "generator": null,             "verifier": "desk-check"},
    "game-host-quiz":    {"label": "Who knows the host?",      "author": "party-game-designer", "generator": null,             "verifier": "desk-check"},
    "game-gift-exchange":{"label": "Gift-exchange game",       "author": "party-game-designer", "generator": "gift_exchange",  "verifier": "code"},
    "secret-santa-form": {"label": "Secret Santa form",        "author": null,                  "generator": "form",           "verifier": "code", "editable_default": true},
    "label-sheet":       {"label": "Gift labels",              "author": null,                  "generator": "cutgrid",        "verifier": "code"},
    "photo-prop-sign":   {"label": "Photo-prop sign",          "author": "keepsake-designer",   "generator": null,             "verifier": "code"},
    "answer-key":        {"label": "Answer key",               "author": null,                  "generator": "answer_key",     "verifier": "code"},
    "start-here":        {"label": "Start-Here guide",         "author": "kit-architect",       "generator": null,             "verifier": "desk-check"},
    "terms-of-use":      {"label": "Terms of Use",             "author": "kit-architect",       "generator": null,             "verifier": "desk-check"}
  },
  "field_stress_values": [
    "Al", "Bartholomew-Wigglesworth", "Dr. Fluffington III", "Zoë", "Siobhán", "José Luis", "Mr. Whiskers McFluff", "Ñandú", "Ōtāhuhu", "O'Brien-Nguyen"
  ]
}
```

## 2. `config/platforms/etsy.json` (merge)

```json
{
  "limits": {
    "title_max_chars": 140,
    "tags_max": 13,
    "tag_max_chars": 20,
    "images_max": 10,
    "digital_files_max": 5,
    "digital_file_max_mb": 20,
    "verified_on": null,
    "source_url": "https://help.etsy.com/hc/en-us/articles/115015628367",
    "verify_before_release": true
  },
  "image_spec": {"aspect": "4:3", "width_px": 3000, "height_px": 2400, "colour_space": "sRGB", "verified_on": null},
  "per_sku_outputs": [
    "etsy-listing-<sku>.json",
    "listing-checklist-<sku>.md",
    "files/Start-Here.pdf",
    "files/Terms-of-Use.pdf",
    "files/bundle_index.json"
  ],
  "constraints": {"max_tags": 13, "max_tag_chars": 20, "delivery": "instant-download", "one_listing_per_sku": true}
}
```

`verified_on: null` makes `etsy_validate` return WARNING until a human records a date (rule 26).

## 3. `config/design_policy.json` (merge under `book_type_overrides`)

```json
{
  "digital-kit": {
    "visual_density": "medium",
    "pedagogy_approach": "progressive",
    "colour_interior": true,
    "ink_friendly_required": true,
    "ink_coverage_pct_max": 15,
    "page_sizes": ["us-letter", "a4"],
    "min_safe_margin_in": 0.25,
    "rationale": "Kits are sold as full-colour printables with an ink-friendly variant; page size and ink mode are render transforms (STD-VARIANT-MATRIX)."
  }
}
```

`production.colour_interior` stays true for kits (digital editions are colour by rule 22); the ink-friendly variant is a render mode, not a colour-policy override.

## 4. Age versions: no change to `age_bands.json`

Map product age versions onto existing bands in `kit.yaml`:

| Version label | Band |
|---|---|
| Ages 4–7 | `kids-4-8` |
| Ages 8–12 | `tween-8-12` |
| Teens | `teen-13-17` |
| Mixed-age family | most-restrictive-wins across included bands (STD-VARIANT-MATRIX §3) |
| Adult / workplace | `adult-general` |

Set the project's `audience` to the **primary** band and keep `project.schema.json`'s `audience` enum unchanged.

## 5. Workflow adapter (recommended, no new states)

- Set kit projects' `formats: ["digital-pdf"]`.
- In `state_playbook.json` → `VISUAL_DEVELOPMENT.conditional_on_formats` add `"digital-pdf"` **only if** you want existing `digital-printable` projects to also produce listing images (rule 16 already asks for mockups). Otherwise add a `conditional_on_book_types: ["digital-kit"]` key and teach `planner.py` to read it.
- `kit images` writes `outputs/proof/cover-proof-report.json` (STD-LISTING-IMAGES §5), so `gate_reports` for `VISUAL_DEVELOPMENT->COVER_APPROVAL` and `FINAL_PROOF->PLATFORM_PACKAGING` pass without edits.
- `kit render` writes `outputs/proof/interior-proof-report.json` aggregated over all variants (PASS only if every variant passes).
- **Open check (gap G13):** dry-run a stub kit through `project plan` to confirm the skip/require behaviour before depending on this.

## 6. `.claude/agents/kit/CATALOG-additions.md`

See batch 3.
