# Etsy extension pack for `publish-puzzle` — integration guide

Unzip at the repo root; paths mirror `.claude/`. Nothing here modifies existing files.

## What is in the pack

| Path | Purpose |
|---|---|
| `.claude/skills/idea-research/SKILL.md` | `/idea-research "<idea>"` → concept dossier (validation, positioning, offer, content plan, SEO, visual direction, risks) |
| `.claude/templates/concept-dossier.yaml` | The dossier spec |
| `.claude/skills/etsy-policy-check/SKILL.md` | Dated recheck of official Etsy/Canva policy pages |
| `.claude/skills/listing-mockup-brief/SKILL.md` | Truthful listing-image plan and per-image briefs |
| `.claude/skills/buyer-experience-qa/SKILL.md` | Independent buyer-journey QA on the final package |
| `.claude/standards/offer-architecture-contract.md` | What every digital offer must contain (START-HERE, LICENSE, bundle index, format rules) |
| `.claude/standards/digital-licensing-contract.md` | Fonts, elements, Canva/editable-template delivery matrix |
| `.claude/standards/etsy-seo-and-listing-research-contract.md` | How SEO candidates are researched, labelled and verified |
| `.claude/rules/23-idea-research.md` | Guardrails for idea research |

## Decisions you need to make

1. **Command name.** Your repo already has `/research "<category>"` (maps a category to 15–20 products). I named the new skill `/idea-research` to avoid a collision. Options: (A) keep both names; (B) add `--idea` mode to the existing `research` skill so you type `/research --idea "Friendsmas party games"`; (C) rename in the Etsy profile only. I recommend A or B: auto-detecting idea vs category from free text will misfire.
2. **Where the dossier plugs in.** It is designed to feed the *existing* stages, not add new states: dossier → `/product-brief` + niche assessment (niche gate), and the content plan approval → `PLANNING`. Tune `auto_approve_gates` rather than adding Etsy-only gates.
3. **Model pins.** Existing skills pin a model in frontmatter. I left the `model:` line out of the new skills; add your standard pin.

## Engineering work I could not do (I did not read `ph_cli.py` or the Python package)

Verify these exist or add them before the skills run end-to-end:

- `ph_cli.py research idea init | validate | log` (mirror the existing `research init | validate | log`).
- `concept-dossier.schema.json` in `.claude/schemas/` generated from the template, and a validator that checks every `evidence_ref` resolves in `findings.json`.
- A product family and audience handling for kits/party/keepsake products in `project.schema.json`, `design_policy.json` and `age_bands.json`. Check how hard a new `product_type` is; this is the main unknown that decides the effort.
- Etsy platform config values (title/tag/image limits) in `.claude/config/platforms/etsy.json`. Note: rule 16 says "up to 10 listing images"; I did not verify the current Etsy limit, so confirm it on the live listing form and keep the number in config, not prose.
- Conditional-stage settings so KDP-only stages (prepress, spine/bleed) are skipped for an Etsy profile.

## Suggested build order

1. Schema + `research idea` CLI subcommands; run `/idea-research` on one real idea end to end.
2. Add the kit product family and Etsy config; run one product through the whole lifecycle with auto-approval on the craft gates.
3. `buyer-experience-qa` and `listing-mockup-brief` wired into `LISTING_APPROVAL`/`FINAL_PROOF`.
4. Only then add the backlog items below.

## Honest limits to design around

- **Demand validation is only as good as the data you feed it.** Etsy search, EverBee/eRank and Trends are typically manual in your research ladder; the skill pauses with a query pack and labels pasted numbers unverified. Expect `NEEDS-DATA` verdicts often. That is the correct behaviour.
- **Canva editable delivery:** I verified only the licensing rule (Pro content → template link only), not whether a template can be created automatically. Treat creating the Canva template as a manual step until you confirm otherwise, or prefer editable formats you control (DOCX/PPTX/Google Slides copy).
- **Etsy rules change.** `etsy-policy-check` exists so nothing downstream relies on remembered policy. Run it at idea stage and again before the listing gate.
- The lead-time rule for seasonal products is an assumption in the dossier (`lead_time_verified: false`) until you confirm it from your own Etsy stats.

## Backlog (worth building later, not in this pack)

- `shop-portfolio-planner` — decides what to make next across the shop (cross-sell, bundle, seasonal calendar, series), using `product-analytics` history.
- `seasonal-calendar` config — dated peak windows and your own lead-time evidence per occasion.
- `trademark-screen` skill — systematic search for marks/prominent listings for coined names and theme terms; output is evidence for `rights-manager`.
- `listing-refresh` — after `product-analytics`, propose title/tag/image changes with confidence labels (no live writes).
- `customer-support-kit` — templates for download problems, licence questions, and review replies (extends `review-responder`).
- `competitor-gap-miner` — structured review-complaint mining with a quotation-free output format.
- `bundle-and-tier-planner` — decides tier structure and upsells from dossier data; feeds `pricing-strategist`.
- `design-system-brief` standard — a shop-level visual identity so every listing set looks like one brand.
