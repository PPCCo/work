---
paths:
  - "projects/**/content/kit/**"
  - "projects/**/kit/**"
  - "projects/**/outputs/kit/**"
---

# Craft, activity, and pet safety

Extends rule 06 (child and tween content). Safety guidance is general-purpose and non-medical; it is not a substitute for adult judgement or product labels.

## Craft and activity cards

- Every craft or activity card SHALL carry: `min_age`, `adult_supervision` (`none`, `nearby`, `hands-on`), `hazard_tags`, `materials` (with quantities), and `time_minutes`.
- Hazard tag vocabulary: `scissors`, `craft-knife`, `hot-glue`, `heat`, `small-parts`, `paint`, `glitter`, `sharp-point`, `edible`, `allergen`, `water`. A card using a hazard SHALL show a visible icon and a one-line precaution.
- **Age-version limits.** The ages 4–7 version SHALL NOT include `craft-knife`, `hot-glue`, `heat`, or `sharp-point` tasks. `scissors` requires `nearby` or `hands-on` supervision and blunt-tip guidance. Where a younger child cannot do a step, the card SHALL assign it to an adult explicitly.
- Materials SHALL be common and household-available; specify "non-toxic" for paint/glue/clay where the card involves children. Do not recommend specific branded products.
- Edible items or food-contact crafts SHALL list allergens and are out of scope for the 4–7 version unless a human approves.
- A host guide SHALL include a child-safety note covering supervision, small-parts awareness for younger siblings, and tidy-up of sharps and liquids.
- Gift-project instructions SHALL NOT recommend candle, flame, or heating-element use.

## Verification

- A card's steps SHALL be desk-checked (`craft-safety-reviewer`, `craft-designer`) for: every material used appears in the materials list; every listed material is used; quantities total correctly across steps; time estimate is plausible; no step is impossible or unsafe for the stated age.
- Physical make-testing is **evidence, not an assumption**. Record `make_tested: true|false`, tester, date, and notes per card. A card with `make_tested: false` SHALL be labelled in the verification report; the human decides at the interior gate whether untested cards ship. Marketing SHALL NOT claim "tested" for untested cards.

## Pet keepsakes

- Instructions involving animals (paw prints, photos, costumes) SHALL prioritise the animal's comfort: use pet-safe, non-toxic materials as labelled by the manufacturer; never force handling; stop if the animal is distressed.
- SHALL NOT give medical, dietary, or behavioural claims. SHALL NOT recommend food, treats, or substances for pets beyond "use treats your pet normally eats."
- SHALL NOT depict or instruct hazardous costuming, restraint, or placement of pets near decorations that pose a swallowing or entanglement risk.
- Pet-voice copy (e.g. "Dear Santa") SHALL be playful and harmless; no jokes about pet harm, abandonment, or illness.

## Escalation

- Any hazard the reviewer cannot bound, or any card that depends on a hazardous step for its core idea, escalates to a human and blocks the interior gate.
