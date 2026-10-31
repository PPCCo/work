# STD-OFFER — Digital Offer Architecture Contract

Defines what a sellable digital-printable/kit offer SHALL contain. Applies to Etsy, Gumroad,
and generic digital-download channels. Complements rule 10 (digital printables) and
rule 16 (Etsy/Gumroad packages); it does not replace them.

## Offer structure

- Every offer SHALL declare a **core product** and MAY declare tiers (core, upsell, bundle). Each tier lists contents, purpose, and (optionally) a price *hypothesis*. Prices are advisory until a human commits them.
- Every offer SHALL state the **buyer-vs-user** distinction (e.g. host buys, guests use) because file formats, page counts, and instructions depend on it.
- Bundles SHALL be assembled from files that each stand on their own value; do not pad a bundle with filler pages to inflate page count.

## Required files in every download

1. **Product file(s)** — the printable/editable content, one file per logical use (e.g. games, invitations, signs), not one giant PDF unless the product is a single document.
2. **`START-HERE.pdf`** — buyer instructions (1–2 pages): what is included, how to download, how to print (page size, scaling "actual size / 100%", paper suggestions), how to open any editable link or file, and the support contact route. Written to the audience reading level.
3. **`LICENSE-AND-TERMS.pdf`** — personal vs commercial use stated plainly, what buyers may not do (resell, redistribute, claim as own), and credit/attribution requirements for third-party elements where applicable. Wording follows `digital-licensing-contract.md`; it is not legal advice and SHALL be human-reviewed.
4. **`bundle_index.json`** — each file with page range, description, and SHA-256 (rule 10).

## Format rules

- **Print files:** US Letter and/or A4 per `project.yaml`. If both sizes are sold, ship them as separate clearly named files or folders; do not mix sizes within one PDF (rule 10).
- **Editable files:** declare the editable method (`canva-template-link`, `docx`, `pptx`, `google-slides-copy`) in the dossier/brief. Delivery method and licensing status SHALL be recorded and satisfy `digital-licensing-contract.md`.
- **Template-link delivery:** a PDF containing the link and numbered open-and-copy steps. The link target SHALL be verified by a human to open a copy flow (not an edit-original flow) before the listing gate.
- **Fillable PDFs:** form fields SHALL work in common free viewers, have meaningful tab order, and be tested before packaging.
- **File names:** human-readable, ASCII, ordered (`01-…`, `02-…`), no personal or internal identifiers.

## Buyer-experience requirements

- A buyer SHALL be able to print the first usable page within three steps of opening the download.
- Every craft/activity that involves scissors, heat, glue guns, or small parts SHALL carry explicit supervision guidance appropriate to the audience (rule 06).
- Hosts/parents SHALL get a one-page "how to run it" guide when the product is an event kit (timing, supplies, setup).
- Supply lists SHALL separate "must have" from "nice to have" and avoid brand names unless essential.

## Listing-image alignment

The offer SHALL be representable by the standard image slots in the `listing-mockup-brief` skill:
hero, what's-included, how-it-works, size-and-format, use-in-context, license. If an offer cannot
fill these truthfully (e.g. nothing to show in context), reduce scope or fix the offer; do not fake
mockups that overstate contents.

## Truthfulness

- Counts (pages, files, templates) stated anywhere SHALL come from `bundle_index.json`, not from the plan.
- A mockup SHALL NOT show items that are not in the download.
- Preview images SHALL NOT expose the full-resolution printable in a form that defeats purchase.

## Acceptance tests

- `bundle_index.json` hashes match the delivered files.
- `START-HERE.pdf` and `LICENSE-AND-TERMS.pdf` exist and are referenced in the index.
- Every file opens, prints at the declared size, and has fonts embedded (rule 10).
- Every editable link or file has a recorded human open-test.
