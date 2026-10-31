# STD-ETSY-SEO — Etsy SEO and Listing Research Contract

Scope: the *research* feeding `product-listing-kit` and the `listing` gate. Hard limits
(140-char title, exactly 13 tags each ≤20 chars) are already enforced by `product-listing-kit`
and rule 16; this standard governs how candidates are researched and what must be verified by a human.

## Method

1. **Buyer-language first.** Build search-term clusters from how buyers describe the *occasion and outcome* (e.g. "friendsmas party games printable"), not from internal product jargon.
2. **Cluster by intent:** occasion/holiday, activity/format ("printable", "editable", "instant download"), audience ("for adults", "for kids"), theme/style. One cluster per distinct buyer intent.
3. **Front-load** the primary keyword in the title; keep titles readable by humans, not keyword-stuffed lists.
4. **Tags:** use distinct, multi-word buyer phrases; avoid near-duplicates; each tag SHALL carry an `intent` label and an `evidence_ref`.
5. **Attributes and category** (occasion, holiday, theme, etc.): record candidates, then confirm against the live Etsy listing form. The category tree and attribute lists change; stale values SHALL NOT pass the listing gate.
6. **Differentiation hooks:** convert the top competitor review complaints into listing-level promises only where the product genuinely fixes them.

## Evidence labels

- Search-volume, competition-count, and conversion figures from third-party tools are `unverified · <tool> · <date>` unless a human supplies an export they confirm.
- Etsy autosuggest or search-result observations are `manual` tier and carry capture date.
- Never state a volume, rank, or "top seller" claim in listing copy.

## Prohibited and flagged terms

- Trademarked brands, characters, franchise names, and celebrity names SHALL NOT appear in titles, tags, or descriptions without rights evidence. Flag for human review.
- Holiday/theme terms that are common words are usually fine; coined brand-like terms SHALL be screened (search for existing marks and prominent listings) and flagged if unclear.
- Do not use "AI-free", "handmade", or "hand-drawn" unless true and consistent with the platform's creation-method categories.

## Disclosures

- AI-assisted creation SHALL be disclosed in the listing description using the approved wording referenced by the dossier (`compliance.ai_disclosure_wording_ref`). Wording is human-approved once, then reused; it SHALL NOT be improvised per listing.
- The description SHALL state what is included (counts from `bundle_index.json`), file formats, page sizes, that it is a digital download with no physical item, and licence summary.

## Required human verification before the `listing` gate

- Title, tags, attributes, and category path confirmed against the live Etsy listing form.
- Current Etsy policy recheck recorded (`etsy-policy-check` output with date).
- Images meet current dimension/count guidance on the live form (limits change; see `listing-mockup-brief`).

## Acceptance tests

- Tag count = 13, each ≤20 chars, no duplicates, no flagged trademarks.
- Title ≤140 chars, primary keyword within the first ~40 characters.
- Every tag/title candidate has an evidence ref or is labelled `assumption`.
- `verified_against_live_etsy` set true only by a human action recorded in the event log.
