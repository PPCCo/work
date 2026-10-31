---
paths:
  - "projects/**/kit/**"
  - "projects/**/niche/**"
  - "projects/**/marketing/**"
---

# Seasonal timing

Seasonal products have a hard commercial window. Timing is evidence, not a feeling.

- A seasonal kit SHALL record `season.occasion`, `season.target_date` (the date the buyer uses it, e.g. a party date or 25 Dec), and `season.latest_list_date` (the last date a live listing is still commercially useful) in `kit.yaml`. Dates are ISO-8601 and set by a human or a cited source.
- `kit seasonal --today <date>` SHALL compute slack = `latest_list_date − today − remaining_effort_days` from an **explicit** `--today` argument. Core modules SHALL NOT read the system clock.
- Remaining effort is estimated from the planner's remaining states plus a fixed allowance for each human-decided gate (compliance, release) and for manual upload. The estimate and its inputs are recorded.
- **Negative slack escalates.** The Publisher-in-Chief SHALL present the human with options via `AskUserQuestion`: fast path, scope reduction, or defer to next season. It SHALL NOT silently drop checks to recover time.
- **Fast path** is permitted and consists of: ship the Standard SKU first; reduce age versions or themes to those with verified content; defer the Expanded SKU to a later listing update; run variant builds in parallel. It SHALL NOT skip: compliance gate, release gate, rights clearance, safety review, Etsy preflight, count/claim verification.
- Demand and competition claims for a season require dated evidence (rule 14 and `market-analyst` procedure). Seasonal demand curves SHALL be recorded as hypotheses unless a dated source supports them. Do not assert "peak weeks" without a source.
- Listing copy SHALL NOT use false urgency ("last chance", countdowns) unless a documented real constraint exists (rule 21). "Instant download, even at the last minute" is an honest benefit statement and is permitted when true.
- After the season, the kit enters `EDITION_MAINTENANCE`; archive listing performance in the lifecycle report so the next year's plan starts from evidence.
