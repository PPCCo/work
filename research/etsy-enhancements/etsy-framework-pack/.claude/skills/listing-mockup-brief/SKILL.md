---
name: listing-mockup-brief
description: >-
  Produce a truthful listing-image plan and per-image briefs (hero, what's-included, how-it-works, size-and-format, use-in-context, licence) for an Etsy/Gumroad digital product, with exact on-image copy drawn from the built bundle, so mockups can be rendered without overstating contents; performs no external writes.
argument-hint: "<project-id> [--channel <etsy|gumroad>]"
user-invocable: true
effort: medium
allowed-tools:
  - Read
  - Write
  - Bash
  - Agent
  - Skill
  - "Bash(${CLAUDE_PROJECT_DIR}/.venv/bin/python3 .claude/scripts/ph_cli.py *)"
---

# /listing-mockup-brief

## Goal

Digital-product listings sell on their images. This skill turns the approved product, its
`bundle_index.json`, and the dossier's visual direction into a **brief for each listing image**
so the images are consistent, readable at thumbnail size, and strictly truthful.

## Arguments

Use `$ARGUMENTS` exactly. Resolve a project ID first. Do not invent counts, claims, or contents.

## Entry criteria

- The project has a registered `bundle_index.json` (or equivalent) so counts are verifiable.
- Cover/art-direction source is registered. Listing-kit copy exists or is in progress.
- Rule 08 (visuals) and rule 16 (Etsy/Gumroad packages) are loaded.

## Delegation

- `art-director` — slot concepts, composition, palette, type, thumbnail legibility.
- `cover-designer` — the hero image and consistency with the cover.
- `commercial-writer` — on-image copy (short, truthful, no superlatives, no unsupported claims).
- `quality-lead` — independent truthfulness check of the finished brief.

## Standard image slots (adapt count to the live listing form limits; verify before the listing gate)

1. **Hero** — legible at thumbnail size; one idea; product name/outcome; no clutter.
2. **What's included** — exact files/counts from `bundle_index.json`.
3. **How it works** — download → print → (open editable link) → use, in 3–4 steps.
4. **Size and format** — page sizes, file types, "digital download — no physical item".
5. **Use in context** — realistic scene of the product in use; props SHALL NOT imply extra items are included.
6. **Licence and support** — personal vs commercial use, what is not allowed, how to get help.
7. Optional: **preview pages** (cropped/watermarked so the full-resolution file is not reproduced), **bundle/tier comparison**, **seasonal/occasion banner**.

## Procedure

1. Read dossier visual direction, `bundle_index.json`, and listing-kit copy. Extract verified counts and formats.
2. For each slot, write a brief: purpose, composition, exact on-image text, assets used (with asset source records), safe-area notes, thumbnail-legibility check, alt text.
3. Mark every counted claim with its source (`bundle_index.json` path + field).
4. Check against `offer-architecture-contract.md`: no item shown that is not in the download; no preview that defeats purchase.
5. Delegate an independent truthfulness check to `quality-lead`; fix findings (max 2 cycles).
6. Write `marketing/listing-image-brief-<channel>.yaml` and `.md`; register the artifacts.
7. Hand off to the rendering step (`printable-designer`/`cover-designer` or the build skill). This skill renders nothing and uploads nothing.

## Required outputs

- Per-slot briefs with exact on-image copy and alt text.
- A truthfulness report mapping every count/claim to its source.
- A thumbnail-legibility note for the hero image.

## Stop conditions

Stop on missing `bundle_index.json`, unresolved rights for any element appearing in an image, or
any request to depict contents that are not in the download.

## Completion report

State project, channel, slots covered, files and hashes created, truthfulness-check result, open
findings, and the next valid action.
