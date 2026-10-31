# STD-LICENSE — Digital Licensing and Editable-Template Contract

Governs third-party elements, fonts, and editable-template delivery in digital products.
Complements rule 12 (rights) and the asset source records in `source-and-claim-contract.md`.
Platform terms change; every statement below about a platform is a **recheck-before-use** item
(see `etsy-policy-check`), not a standing fact.

## Principles

- No asset enters a product without an asset source record: source, license reference, commercial-use confirmation, and archived evidence path.
- `unknown` or unresolvable license status blocks release; replace the asset.
- Licensing is evaluated per **delivery format**, not per product: the same asset can be allowed in one format and forbidden in another.
- Legal/rights agents identify issues and evidence; they are not counsel and never accept terms on the user's behalf.

## Delivery-format matrix (verify current terms before each use)

| Asset source | Flattened PDF/PNG allowed? | Editable template allowed? | Notes |
|---|---|---|---|
| Original art/text created for the product | Yes | Yes | Needs originality attestation for illustrations (rule 07) |
| Canva **Free** content or your own uploads | Per Canva terms (as last verified) | Per Canva terms | Record verification date |
| Canva **Pro** content | **No**, as last verified | **Template link only**, as last verified | Pro content in a template sold as PDF/files is the common violation |
| Fonts with a commercial/desktop license | Check license | Check license (embedding/redistribution differ) | Never assume "free font" means commercial-use free |
| Stock clip-art/elements marketplace | Check the specific licence tier | Usually restricted for editable redistribution | Many licences forbid delivering the source element in an editable file |
| Public-domain material | Yes (record provenance) | Yes | Confirm status; do not trace (rule 07) |
| AI-generated assets | Per platform disclosure rules and tool terms | Per tool terms | Record tool, version, prompt/inputs, seed where available |

The Canva rows were verified against Canva's "using Canva to create products for sale" help
article at the time this standard was drafted. Re-verify before each product; do not copy this
table into customer-facing text.

## Editable-template rules

- The dossier/brief SHALL declare `editable_delivery.method` and `licensing_status` (`clear`, `blocked-pro-content`, `unknown`). `unknown` blocks the listing gate.
- If any Pro or restricted-licence element is present, the editable method SHALL be limited to what the licence allows (for Canva Pro content: template link only) or the element SHALL be replaced.
- When feasible, prefer editable formats the seller fully controls (e.g. DOCX, PPTX, Google Slides copy link) built from original or cleanly licensed assets; this removes Canva-specific constraints.
- A human SHALL open every delivered template link and confirm it triggers a **copy** flow and does not grant edit access to the original. Record this test with date.
- Template links are stored in `START-HERE.pdf` (or a dedicated link PDF), never in the listing description.

## Fonts

- Record font family, foundry, licence type, and commercial/embedding permission in the asset source record.
- Embedded fonts in PDFs (rule 10) still require a licence that permits embedding.
- For editable files that rely on installed fonts, list required fonts in `START-HERE.pdf` with the licence/availability note, or substitute a permissively licensed alternative.

## Buyer licence text (LICENSE-AND-TERMS.pdf)

Plain-language terms covering: personal use, any permitted small-scale or commercial use,
prohibited redistribution/resale/claiming as own, third-party credits, and support route. The
text SHALL be human-reviewed and SHALL NOT claim rights the seller does not hold. It SHALL
reflect upstream licence limits (e.g. if an element forbids resale, the product cannot grant
resale rights).

## Evidence and gates

- Rights ledger entries SHALL exist for every font and third-party element before the `interior` gate.
- `compliance` gate (human-decided) SHALL see: asset source records, template-link open-tests, AI-disclosure wording, and licence text.
- Any unresolved licensing issue blocks release and escalates to a human.
