---
paths:
  - "projects/**/outputs/kit/**"
  - "projects/**/kit/templates/**"
---

# Editable and personalised files

Applies to products sold as "personalise with your name" or "editable template".

## Delivery modes

1. **Fillable PDF (framework-built, default).** Text fields built with embedded cleared fonts; validated by `kit_render`.
2. **Print-and-write PDF (always shipped alongside fillable).** Same layout with ruled write-in lines, so the product works on any viewer and when handwritten.
3. **Canva template (human-built, optional).** The framework outputs a Canva build pack (layout spec, cleared assets, copy). A human with a Canva account builds the template and records the share link and licence evidence. The framework SHALL NOT create accounts, log in, or publish. The delivered file is a PDF containing the template link; its presence requires the human evidence record, otherwise the SKU ships without Canva and the listing SHALL NOT mention it.

## Requirements

- Each field SHALL declare `name`, `max_chars`, `font_pt`, `alignment`, and `default_prompt`. `kit_render` SHALL verify that the longest realistic value fits at the declared size, using the stress list in `config/kit_components.json` (e.g. 24-character hyphenated names, accented characters). Fields that overflow fail the variant.
- Fillable PDFs SHALL work without a proprietary viewer feature beyond standard AcroForm text fields; the Start-Here guide SHALL state tested viewers only after a human test, otherwise say "most PDF viewers".
- Canva elements that require a paid Canva tier or Canva-owned stock SHALL NOT be used; use only cleared assets in the rights ledger (rule 12). Fonts used in a Canva build SHALL be recorded; Canva-library fonts have their own terms and require a human note.
- Personalised content (pet name, host name) is entered by the buyer offline. The framework SHALL NOT collect, store, or transmit buyer data. Forms like RSVP trackers are printed or typed locally.
- Editable files SHALL meet the same safe margins, DPI, accessibility, and A4/Letter rules as static pages.
- The licence (rule 29) SHALL state whether the editable file may be modified (yes, for the buyer's own use) and redistributed (no).
