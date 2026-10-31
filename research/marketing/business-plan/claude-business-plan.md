# Business Plan: AI-Native Publishing Studio for Printable & Print-on-Demand Products

**Prepared:** 26 October 2026 · **Planning horizon:** Nov 2026 – Oct 2027 · **Operator:** solo founder with an agentic (Claude) production framework

> **How to read this plan.** Every material claim carries an evidence grade:
> **[A]** industry or primary data (Circana/Publishers Weekly, Authors Guild, Chalkbeat, TechCrunch, platform or regulator documents) ·
> **[B]** platform documentation as relayed by a secondary source ·
> **[C]** vendor blog, tool maker or agency estimate (useful, but self-interested and often unsourced) ·
> **[D]** my inference or modelling. Scores, scenarios and forecasts are **[D]**: they are judgement and arithmetic, not measurements.
> I could not read Amazon or Etsy sales data directly. Every Amazon/Etsy sales figure below is a third-party estimate. The first job of the plan is to replace those estimates with your own data.

---

## 1. Executive summary

**The opportunity is real but narrower than the pitch.** Print activity books (coloring, puzzles) are one of the few growing pockets in a shrinking print market. Etsy digital downloads carry ~85–90% gross margins. AI cuts production cost per product toward zero. But the same facts are true for every competitor, and platforms are tightening rules against exactly this kind of volume publishing. The durable advantage is **niche selection, quality control, compliance, brand and a data feedback loop**, not generation speed.

**Five findings that shape everything else**

1. **Demand is concentrated in activity products, not in books generally.** Circana: US print unit sales fell 3.1% in Q1 2026 and adult non-fiction fell 8.8%, yet crafts/hobbies/games grew 9.6%, and kids' coloring/activity books were the headline growth story of 2025 **[A]**. Reported children's coloring/activity units: 16.7M in 2025, +18% **[C, relayed from PW; verify at source]**.
2. **Price discipline decides whether a KDP book can ever be advertised.** Since 10 June 2025 KDP pays 60% at ≥$9.99 and 50% at ≤$9.98 **[B]**. A 104-page 8.5×11 coloring book earns **$2.15 at $9.98 but $3.15 at $9.99** (printing cost $2.84) and **$1.16 at $7.99** **[D, from published costs]**. At $7.99 the book can't survive paid ads; at $9.99+ it barely can.
3. **Etsy ads only work above ~$12 for single printables.** At an $8 price the net after fees is ~$6.79. At a 3% conversion rate the break-even click cost is ~$0.20, at or below the typical $0.20–0.50 Etsy CPC **[D, using C-grade CPC data]**. The model is bundles, kits and organic Pinterest/Etsy search, not paid traffic on $4 files.
4. **Platform policy is the biggest single risk.** KDP requires disclosure of AI-generated text, images and translations and is enforcing it harder in 2026 **[B/C]**; Etsy allows AI work only under "Designed by a seller" with disclosure and tightened its rules in June 2025 **[C]**; **Teachers Pay Teachers announced a ban on AI-generated resources on 15 Oct 2026** **[A]**. One account suspension can end a catalog.
5. **AI-generated images are not copyrightable by themselves in the US** (Copyright Office, Jan 2025; human selection/arrangement can be protected) **[A]**. Competitors can legally copy your raw pages. Your moat is brand, series, bundles, speed to the next trend and data, not exclusivity of the images.

**Recommended portfolio (scores in §4)**

| Tier | Product line | Why |
|---|---|---|
| **A: launch now** | Niche kids' coloring & activity books, each with a printable twin | Strongest demand evidence, easiest to automate, two channels from one asset |
| **A** | Themed and large-print puzzle books (sudoku, word search, mixed) | Evergreen gift demand, deterministic generation with verified solutions, strong policy fit |
| **A/B** | Seasonal printable kits for Etsy/Gumroad (Christmas, Valentine's, Easter, Halloween) | No print lead time, high margin; peaks are sharp |
| **B: pilot** | Cozy-niche adult coloring (not generic mandalas), kids how-to-draw workbooks, wall-decor printables, letter/stationery printables | Real demand but saturated or heavier QA |
| **C: defer** | Photography/oil/photorealism books, teen non-fiction, TPT resources, standalone sketch-art books | Weak unit economics, policy hostility, or low automation fit |

**12-month outlook (§5).** Base case: ~96 KDP titles and ~240 Etsy listings, ≈$10.8k revenue after platform fees, ≈$7.4k after tooling/ads/inference costs (excluding your time and tax) **[D]**. Conservative case: ≈$1.5k revenue. Self-reported indie data says 44% of authors earn ≤$100/month and the median is ~$13.5k/year **[C]**. Treat the base case as a target that needs execution, and the conservative case as the cash plan.

**Do this week (Oct 26–Nov 2)**
- Complete KDP/Etsy tax setup (ABN, W-8BEN/tax interview).
- List 20–30 Christmas printable SKUs on Etsy/Gumroad: no print lead time, and Etsy search peaks in December.
- Submit 3–5 KDP Christmas titles at **$9.99+**. KDP review can take 72 hours to 3–4 weeks, so treat these as a bonus, not the plan **[C]**.
- Stand up the compliance gate (§9) before volume, not after.

---

## 2. Business definition and honest test of the thesis

**What you sell.** A *production-and-intelligence system* that turns a validated micro-niche into a finished product (interior, cover, listing, marketing assets) at near-zero marginal cost, sold as (1) your own catalog on KDP/Etsy/your store, and later (2) a productized service or tool to other publishers (B2B, §10).

**Customer segments and the pain each solves**

| Segment | Pain | Evidence |
|---|---|---|
| Gift buyers & hobbyists (adult coloring, puzzles, seniors, parents of 3–10-year-olds) | Generic mass-market titles; want a theme that matches *them* or the recipient | Specialised sub-niches face less competition than generic ones **[C]**; large-print/senior puzzles are bought mostly as gifts by adult children **[C]** |
| Parents/grandparents | Screen-free activities | Circana attributes children's market growth to coloring/puzzle/sticker activity books **[A]** |
| Aspiring self-publishers (B2B) | Cost, skill, time: freelancer packages of cover + formatting + metadata are quoted at $600–$2,000+ **[C]**; illustrated picture books $2,000–$10,000 **[C]** | Matches your $500–$2,000 figure, though the sources are tool vendors |

**Claims in the pitch, tested**

| Pitch claim | Verdict |
|---|---|
| "Hyper-specific micro-niches are underserved" | **Mostly supported [C].** But "nobody wins the generic term" cuts both ways: micro-niches have small audiences, so you need volume *and* a cheap way to validate before building (§4.3). |
| "Trend-jacking beats human speed" | **Partly.** Seasonal books win when live 6–8 weeks before the holiday **[C]**; but KDP review is 72 hours to 3–4 weeks and standard accounts are capped at 3 new titles/day **[B/C]**. Printables (Etsy/Gumroad) are the genuinely fast channel. |
| "Sellers with zero talent can compete" | **Risky.** Etsy and TPT are moving against low-effort AI output; buyers report errors ("an alphabet without an F") in AI classroom material **[A, Chalkbeat]**. Human curation is a requirement, not a luxury. |
| "Enterprise-grade" | Not yet a market fact. Competing tools are cheap and plentiful (§10). It becomes true only through compliance, QA and provenance features. |

---

## 3. Market evidence

### 3.1 Macro: print is flat to down; activity is the exception

| Metric | Figure | Grade |
|---|---|---|
| US print unit sales, Q1 2026 | −3.1% to 163.5M | **[A]** PW/Circana |
| Adult non-fiction, Q1 2026 | 63.4M → 57.8M units (−8.8%) | **[A]** |
| Crafts/hobbies/antiques/games, Q1 2026 | +9.6% (one of only two adult non-fiction subcategories to grow, with religion +1.6%) | **[A]** |
| Juvenile fiction / non-fiction, Q1 2026 | +5.9% / +4.9% | **[A]** |
| Juvenile non-fiction / fiction, Q3 2025 | +6% / +1%; infant books +13% | **[A]** |
| "Return to growth for children's market" in 2025, driven by coloring, puzzles, stickers, licensed content | Circana's books analyst, PW Winter 2026 | **[A]** |
| Children's coloring & activity units | 16.7M in 2025 (+18%), still ~+18% through 23 May 2026 | **[C]**, relayed from a PW piece dated 14 Aug 2026; confirm at source |
| Adult non-fiction themes | "Cozy crafting", comfort, screen-free; hands-on categories (journaling, coloring, puzzles) rising | **[A/C]** |
| Young adult fiction, Q1 2026 | −28.7% | **[A]** |

*Data note:* the PW table's young-adult non-fiction row is internally inconsistent (stated −11.2%, computes to −1.4%), so I don't use it.

### 3.2 Category by category

| Category | Demand signal | Competition / saturation | Notes |
|---|---|---|---|
| **Kids' coloring & activity books** | Circana growth (above); coloring books a top gifting category **[C]** | Licensed characters dominate big houses **[C]**; generic titles crowded | Strongest evidence base. Specific age + theme + occasion wins. Never use licensed characters (§11). |
| **Adult coloring** | Search interest peaks in **January** (Google Trends, via **[C]**); gift demand year-round | 100,000+ titles on Amazon **[C]**; "generic adult coloring competes against thousands" | **Market-size reports disagree wildly** (US$151M in 2024 to US$13.76B in 2025) **[C]**, so ignore top-down sizes. PW's 2026 activity recap points to "cozy simplicity", not denser mandalas **[C]**. |
| **Puzzle books** | Large-print sudoku/word search for seniors is the "demand engine" **[C]**; a top large-print word-search ASIN is estimated at ~900 units/month, top-10 average ~300/month **[C]** | "Nobody wins 'word search book' anymore; 'gardening word search large print' is winnable" **[C]** | KDP itself says puzzle and coloring books are **not** "low-content" **[B]**, which lowers policy risk. |
| **Kids' picture/story books** | Juvenile market growing **[A]** | Dominated by traditional publishers and licensed IP; reviews gate sales; character consistency is the hardest AI problem **[C]** | Premium-colour cost makes margins thin (§5). Fully-illustrated story books are high-QA, lower-fit. |
| **Printable wall art / planners / templates (Etsy)** | "Printables": ~823,000 avg monthly searches; digital downloads called the most-sold Etsy category **[C]** | **7.0M listings** for "printables", 4.1M for "printable download"; difficulty 62/100 **[C]**. "Printable" listings flat YoY, demand peaks December **[C]** | Highest-volume and most saturated. Win via narrow sub-niche and bundles. |
| **Greeting cards / keepsakes / stationery** | Pinterest Predicts 2026: a letter-writing revival (searches for pretty stamps +105%, handwritten letters +45%, mail gifts +110%) **[A/B]**, from a French-language summary of Pinterest data | Crowded on Etsy | Good fit for the printable engine; seasonal. |
| **Art books (pencil/oil/photo)** | No category-level demand evidence found | Premium colour printing makes unit economics poor (§5) | Sell as digital prints/wall art, not KDP books. |
| **Teachers' resources (TPT)** | Large buyer base (85% of US pre-K–12 educators per TPT's own 2023 claim **[A]**) | **AI-generated resources are being banned** (Oct 2026) **[A]** | Avoid. |
| **Religion-adjacent activity (e.g. Bible-verse word search)** | Adult non-fiction religion grew in 2025 (+5.4%) **[C]** and in Q1 2026 (+1.6%) **[A]** | Moderate | Easy variants for Christmas/Easter; content accuracy matters. |

### 3.3 Reality check on sales expectations

- Written Word Media 2025 survey (n=1,346, self-reported, mostly Amazon authors): **44% earn ≤$100/month; 20% earn $500–$5,000; 13% >$5,000; 8% >$10,000**; marketing spend averages **$636/month** **[C]**. Income follows a power law, so the mean is a poor guide.
- Authors with more titles earn more (2024 survey: those earning >$20k/month averaged 61 books) **[C]**, which is correlation, but it supports a catalog strategy.
- A vendor model suggests **~2 copies/title/month** for a journal/coloring catalog as a *starting* assumption, "probably not a cautious one" **[C]**.
- Etsy: conversion averages ~3.2% platform-wide (estimate) **[C]**; 2–3% is average for an established shop, 3–5% strong **[C]**; new shops convert lower; listings with fewer than 5 reviews convert at less than half the rate of those with 10+ **[C]**. Median-seller income claims conflict (under $500/year vs £400–800/month for digital) **[C]**, so I plan on the low end.

---

## 4. Product selection

### 4.1 Method

Seven criteria, scored 1–5 by me from the evidence above **[D]**:

| Criterion | Weight |
|---|---|
| Demand evidence | 25 |
| Competition headroom (5 = open) | 15 |
| Unit economics | 15 |
| Automation fit | 15 |
| Platform-policy safety | 15 |
| Time-to-first-sale | 10 |
| Differentiation potential | 5 |

### 4.2 Results

| Rank | Product line | Score /100 | Demand | Comp. | Econ. | Auto. | Policy | Speed | Diff. |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Niche kids' coloring & activity books (+ printable twin) | **82** | 5 | 3 | 3 | 5 | 4 | 4 | 4 |
| 2 | Themed / large-print puzzle books | **76** | 4 | 2 | 3 | 5 | 5 | 4 | 3 |
| 3 | Holiday & seasonal printable kits (Etsy) | **72** | 4 | 2 | 4 | 4 | 3 | 5 | 3 |
| 4 | Wall-decor printables / digital art | **71** | 4 | 1 | 4 | 5 | 3 | 5 | 2 |
| 5 | Kids how-to-draw & learning workbooks | **69** | 4 | 3 | 3 | 4 | 3 | 3 | 4 |
| 5 | Adult "cozy" niche coloring (non-mandala) | **69** | 3 | 2 | 3 | 5 | 4 | 4 | 4 |
| 7 | Faith-based family activity books | **64** | 3 | 3 | 3 | 4 | 3 | 3 | 4 |
| 8 | Greeting, keepsake & stationery printables | **62** | 3 | 2 | 3 | 4 | 3 | 4 | 3 |
| 9 | Teacher resources on TPT | **58** | 3 | 2 | 4 | 4 | **1** | 4 | 2 |
| 9 | Standalone pencil/sketch art books | **58** | 2 | 3 | 3 | 4 | 3 | 3 | 3 |
| 11 | Kids' picture / story books | **55** | 3 | 2 | 3 | 3 | 3 | 2 | 3 |
| 12 | Photography / oil / photorealism books | **43** | 2 | 2 | 2 | 3 | 2 | 2 | 2 |
| 13 | Teen non-fiction | **41** | 1 | 3 | 3 | 2 | 2 | 2 | 2 |

Sensitivity: weights shift ranks 3–5 around, but ranks 1–2 and 11–13 are stable under any reasonable reweighting. That is the decision-relevant output.

### 4.3 Micro-niche validation system (the heart of your "long-tail" advantage)

A niche idea is a combination: **Audience × Theme × Format × Occasion × Level**. Example: *seniors × backyard birds × large-print coloring × Mother's Day gift × easy*. Your "steampunk greyhound pencil-sketch book" is Audience (greyhound owners) × Theme (steampunk) × Format (sketch book): a legitimate probe, but a small audience, so it must be **cheap to test** (a listing and three pins, not a finished book).

**Scorecard before building anything** (automate in the framework):

1. **Demand proxies** (pull from several; none is truth): Amazon autocomplete, Etsy search suggestions, Pinterest Trends, Google Trends, and "Pinterest Predicts" (the 2027 edition should publish around early December, as the 2026 edition did on 9 Dec 2025 **[A]**).
2. **Pain/occasion:** is there a recipient or trigger (a gift for seniors, a screen-free break, a breed owner, a holiday)? Gift searches are unbranded and recipient-led, which favours small shops on Pinterest **[C]**.
3. **Competition:** count of results, top-10 review counts and covers; prefer niches where top listings look generic.
4. **Economics:** can it be priced ≥$9.99 (KDP) or as a ≥$12 bundle (Etsy)?
5. **Risk flags:** IP, trademark, health claims, kids' safety, factual accuracy.
6. **Test:** publish a *minimum asset* (cover mockup + 5 sample pages + listing) to Etsy/Pinterest first; build the full book only after signals (saves, clicks, favorites).

**Caution on BSR/sales estimates:** KDP says Best Seller Rank reflects recent customer activity and isn't an accurate sales tracker **[B]**. One bestseller is not a market; look at the top 20 and at year-over-year seasonality.

### 4.4 Starter niche backlog (hypotheses to test, each ties to evidence)

| Niche hypothesis | Evidence hook | Channel |
|---|---|---|
| Large-print sudoku/word search for seniors (themes: gardening, birds, travel, nostalgia) | Year-round "demand engine" **[C]**, gift buyers | KDP |
| Bible-verse / faith word search (Christmas, Easter, year-round) | Religion print growth **[A/C]** | KDP + Etsy |
| Toddler / ages 4–8 holiday activity books (mazes, simple word search, coloring) | Children's activity growth **[A]**; "Christmas coloring book for toddlers" cited as winnable vs. saturated head term **[C]** | KDP + Etsy kits |
| Cozy-nature adult coloring (quiet scenes, bold lines, no treatment claims) | PW 2026 recap "cozy simplicity" **[C]** | KDP + Etsy |
| Pet-breed coloring/sketch bundles (named breed, steampunk or cozy styling) | Pet products are a recognised Etsy category **[C]** | Etsy first |
| Travel word-search (compact, giftable) | Seasonal travel demand **[C]** | KDP |
| Letter-writing / pen-pal stationery printable kits | Pinterest letter-writing trend **[A/B]** | Etsy + Pinterest |
| Afro-bohemian, Neo-Deco, "FunHaus" circus wall-art sets | Pinterest Predicts 2026 trend names (afrobohemian decor searches +220%) **[A]** | Etsy wall art |
| Kids' how-to-draw workbooks (animals, vehicles) | Illustration-book demand **[D]**; strict QA needed | KDP + printable |

---

## 5. Feasibility and unit economics

### 5.1 KDP print economics (Amazon.com, USD)

Rules used: royalty = rate × list price − printing cost; rate 60% at ≥$9.99, 50% at ≤$9.98, 40% via Expanded Distribution **[B]**. B&W cost for regular trim: $2.30 flat for 24–109 pages, then $1.00 + $0.012/page; large trim costs more; standard colour $1.00 + $0.0255/page (regular) or $0.0402 (large); premium colour $1.00 + $0.065/page (regular) or $0.080 (large) **[B]**. Costs for the 8.5×11 rows are the published $2.84 (104 pp) and $3.04 (120 pp) examples **[C]**.

| Product | Price | Print cost | Royalty | Break-even ACoS | Max CPC at 10% CVR |
|---|---|---|---|---|---|
| Coloring, 104 pp, 8.5×11 B&W | $7.99 | $2.84 | **$1.16** | 14.5% | $0.12 |
| Same | $9.98 | $2.84 | $2.15 | 21.5% | $0.22 |
| Same | **$9.99** | $2.84 | **$3.15** | 31.6% | $0.32 |
| Same | $11.99 | $2.84 | $4.35 | 36.3% | $0.44 |
| Puzzle, 120 pp, 8.5×11 B&W | $8.99 | $3.04 | $1.46 | 16.2% | $0.15 |
| Same | $9.99 | $3.04 | $2.95 | 29.6% | $0.30 |
| Same | **$12.99** | $3.04 | **$4.75** | 36.6% | $0.48 |
| Picture book, 32 pp premium colour, large trim | $12.99 | $4.20 | $3.59 | 27.7% | $0.36 |
| Same | $14.99 | $4.20 | $4.79 | 32.0% | $0.48 |
| Workbook, 100 pp standard colour, large trim | $16.99 | $5.02 | $5.17 | 30.5% | $0.52 |
| Art/photo book, 200 pp premium colour, regular | $24.99 | $14.00 | **$0.99** | 4.0% | $0.10 |
| Same | $34.99 | $14.00 | $6.99 | 20.0% | $0.70 |

*Premium colour 24–40 page fixed costs ($3.60 regular / $4.20 large) come from a third-party guide **[C]**. All other costs are from KDP's published tables as relayed **[B]**.* Expanded Distribution roughly halves the margin (e.g. $1.16 on the $9.99 coloring book), so keep it off unless you want bookstore reach.

**Advertising reality check.** Books average ~19% ACoS and ~$0.38 CPC in agency aggregates **[C]**; KDP-focused calculators assume 5–10% conversion **[C]**. At $0.38 CPC the $9.99 coloring book needs ~12% conversion to break even on ads; the $12.99 puzzle book needs ~8%; the $7.99 coloring book would need ~33%, which is infeasible. **Rules that follow: (1) never price a KDP book below $9.99; (2) prefer $12.99+ for puzzles, large-print and workbooks; (3) expect paid ads to be a thin-margin accelerator for proven winners, not a growth engine.**

### 5.2 Etsy / digital economics

Fees: $0.20 listing (renews every 4 months or on sale), 6.5% transaction, 3% + $0.25 processing; **Offsite Ads 15% (12% once a shop passes $10k/year, capped at $100/order); sellers under $10k can opt out** **[C/B]**.

| Price | Fees (no ads) | Net | With Offsite Ads: net |
|---|---|---|---|
| $5 | 18.5% | $4.08 | $3.33 |
| $8 | 15.1% | $6.79 | $5.59 |
| $12 | 13.2% | $10.41 | $8.61 |
| $20 | 11.8% | $17.65 | $14.65 |

Break-even Etsy Ads cost per click (no Offsite Ads): $8 item at 3% conversion = **$0.20**; $12 = $0.31; $15 = $0.39; $20 = $0.53 **[D]**. Typical Etsy Ads CPC is $0.20–$0.50 (lower for digital) **[C]**. **Conclusion: bundle to $12–$25 and rely on organic search/Pinterest; run Etsy Ads only on listings with proven conversion, and opt out of Offsite Ads until the shop is over $10k.** Selling direct (Payhip free plan 5%, Gumroad 10%, Sellfy $22/month at 0% **[C]**) saves fees but forfeits Etsy's built-in buyer traffic.

### 5.3 Production cost

Marginal cost per product is dominated by inference/compute and your review time, not licences. Your local, Apache-2.0 image models (FLUX.2 klein 4B, Qwen-Image 2512 line, Z-Image) have no per-image fee and permit commercial use **[B/C]**. Budget **$2–6 per book in LLM/inference cost as an assumption to measure** ($4 used below) **[D]**. Research tooling: KDSPY $79 or Publisher Rocket $199 (one-time) **[C]**. The real constraint is **human QA minutes per title**; track it.

### 5.4 Twelve-month scenarios **[D]**

Assumptions: titles earn 50% in their first month and 100% thereafter; no seasonality (it concentrates revenue, see §7); costs exclude your labour and income tax.

| | Conservative | Base (target) | Upside |
|---|---|---|---|
| New KDP titles / month | 4 | 8 | 15 |
| New Etsy listings / month | 10 | 20 | 40 |
| Copies per KDP title / month | 0.8 | 2.0 | 4.0 |
| Avg royalty per copy | $3.00 | $3.50 | $4.00 |
| Sales per Etsy listing / month | 0.3 | 0.8 | 1.5 |
| Avg Etsy price | $6 | $9 | $12 |
| Ads budget / month | $0 | $150 | $400 |
| **Catalog at month 12** | 48 titles, 120 listings | 96 titles, 240 listings | 180 titles, 480 listings |
| **12-month revenue (after platform fees)** | **≈$1,485** | **≈$10,837** | **≈$52,308** |
| 12-month tooling + ads + inference | ≈$831 | ≈$3,462 | ≈$7,836 |
| **12-month net (before labour/tax)** | **≈$654** | **≈$7,375** | **≈$44,472** |
| Month-12 run-rate revenue | ≈$258/mo | ≈$1,881/mo | ≈$9,078/mo |

Caveats: the base case's month-12 run-rate (~$1,900/month) sits in the band that only about a third of surveyed authors report (≥$500/month, per the self-reported survey in §3.3). Per-title outcomes follow a power law (e.g. 10% of titles at 15 copies/month, 30% at 3, 60% at 0.5 gives a mean of 2.7) **[D]**, so expect a few winners to carry the catalog, which is why **hit-rate tracking and fast pruning matter more than volume**. Etsy sales/listing assumptions have no solid evidence base; validate with your first 60 days of data.

---

## 6. Platforms

### 6.1 Policy matrix (the constraint set the automation must obey)

| Platform | AI rule | Enforcement / limits | Implication |
|---|---|---|---|
| **Amazon KDP** | Disclose AI-**generated** text, images and translations at upload; AI-**assisted** (brainstorming, editing, refinement) needs no disclosure **[A, Authors Guild]** | Disclosure is private to Amazon (no public badge) **[C]**; enforcement escalated 2025–26 with removals and suspensions for non-disclosure **[C]**; **3 new titles/day** cap since late 2024 **[C]**; scrutiny of duplicative/low-quality books **[C]** | Treat nearly all your image output as "AI-generated". Disclose honestly; log it per title. |
| **Etsy** | Creativity Standards (July 2024): AI work goes under "Designed by a seller" with disclosure in the listing description; listing photos must show the real item **[C]** | June 2025 tightening removed a "templated design" allowance and targets resold templates/clip-art close to as-is **[C]**; removals of Handmade-policy violations rose fourfold **[A, TechCrunch 2024]**; suspensions for mass-listing uncurated AI output **[C]** | Add genuine human contribution (concept, curation, editing) and keep per-listing provenance. One source debunks a rumoured July 2026 "AI checkbox"; check the live Seller Handbook. |
| **Teachers Pay Teachers** | Announced ban on AI-generated classroom resources (15 Oct 2026) **[A, Chalkbeat]** | Seller petition calls it a retroactive ban on AI-assisted content **[advocacy claim]** | Exclude. |
| **Apple Books** | AI disclosure required in publishing interface **[C]** | n/a | Relevant only if you go wide. |
| **TikTok** | Label realistic AI-generated content **[C]** | n/a | Label any AI video/imagery. |
| **Gumroad / Payhip / Sellfy / Shopify** | No comparable AI rules found | You own the customer list | Use for fee savings and email capture. |

### 6.2 Creation stack (what to build with)

| Layer | Recommendation | Notes |
|---|---|---|
| Image generation | Local **FLUX.2 klein 4B** (Apache 2.0, released Jan 2026), **Qwen-Image 2512 line** (Apache 2.0), **Z-Image** (Apache 2.0) **[C]** | **Avoid FLUX.2 klein 9B / dev (non-commercial licence) and Ideogram 4 weights (non-commercial)** for commercial output **[B/C]**. Record model + version + licence per asset; recheck licences at build time. |
| Coloring line art | Generate, then enforce vector-like clean lines (threshold/trace), min line weight, closed shapes, ink-coverage limits | Single-sided pages are the norm in top adult coloring titles **[C]**. |
| Puzzles | **Deterministic generators with a solver** (verify unique solutions; large-print layouts; answer keys); LLM only for themes/word lists | Competitors advertise "verified unique solutions" **[C]**, so correctness is table stakes. |
| Text (kids' non-fiction, activity instructions) | LLM drafting + separate fact-check/readability agent + human spot check | Accuracy errors are what buyers and platforms punish **[A]**. |
| Layout/export | Scripted PDF generation (trim, bleed, spine from page count) → KDP interior/cover; ZIP + PDF bundles for Etsy | Order **proof copies** before each new template/format. |
| Fonts | Commercially licensed or OFL only; log licences | |
| Mockups | Accurate mockups only; follow Etsy photo rules | |

### 6.3 Distribution stack

| Channel | Role | Entry |
|---|---|---|
| KDP print (+Kindle where suitable) | Core book revenue; Amazon ad inventory | $9.99+ pricing; standard distribution |
| Etsy | Printable kits, bundles, wall art | Bundles ≥$12; Etsy search + Pinterest |
| Own store (Payhip/Shopify) | Email capture, direct sales, cross-sell | Free sample packs → list |
| Gumroad | Quick drop channel | 10% fee **[C]** |
| IngramSpark / Draft2Digital / B&N Press | Wide distribution | **Not researched here; evaluate in Phase 3** |

---

## 7. Marketing, advertising and buyer acquisition

### 7.1 Funnel

```
DISCOVER → CLICK → CONVERT → ONBOARD → REVIEW/REPEAT
 Pinterest   Cover/thumbnail   Listing   Email list    Review prompt (compliant)
 Etsy/Amazon search  Title/keywords  Price/bundle  Welcome sequence   Series cross-sell
 Short video   Free sample pack  Mockups   Occasion reminders   Seasonal relist
```

### 7.2 Channel plan

| Channel | Role | Tactics | Budget guide |
|---|---|---|---|
| **Pinterest (organic first)** | Primary discovery for printables, decor, gifts, crafts. It's a search-and-save platform, so products that solve a future project travel furthest **[C]** | 6–8 distinct pins per listing aimed at different searches (nursery decor, gift for a plant lover); pin 6–8 weeks before the occasion; use Pinterest Predicts/Trends as an early signal **[C]** | $0 time-only; later $100/month on proven pins |
| **Etsy SEO** | Conversion engine | Title written as a search; 13 tags; first 10 reviews matter; bundles; consistent shop theme | $0 |
| **Etsy Ads** | Accelerator | Only on listings with proven conversion; target ROAS 3–4× **[C]**; break-even is far lower for digital goods (~1.2×) but click costs dominate (§5.2) | $5–15/day for tests after ~50 sales **[C]** |
| **Amazon Ads (Sponsored Products)** | Accelerator for winners | Only titles with royalty ≥$3 and ≥10 reviews; start with exact-match keywords; weekly bid review; kill if ACoS > break-even for 3 weeks | Start $5–10/day per proven title |
| **Email list** | Owned channel | Free sample pack on your own store (parent/adult audience, not children); welcome sequence; seasonal and series launches. Authors' newsletters are still the top owned-channel investment among optimistic authors (WWM mid-2026) **[C]** | $0–$20/month |
| **Short video** | Social proof | Flip-through, coloring time-lapse, puzzle solving; label AI-generated realistic content (TikTok rule) **[C]** | Time only |
| **Reviews / social proof** | Conversion lever | Ask buyers politely; never offer incentives for Amazon reviews (verify current Amazon rules); ARC copies to genuine niche hobbyists | $0 |

*Paid traffic is secondary by design: the unit economics in §5 leave little room for ads on single low-priced items.*

### 7.3 Seasonal calendar (US-centric; Etsy/Gumroad lead time ≈ 0, KDP lead time 6–8+ weeks)

| Occasion (date) | Etsy/Gumroad live by | KDP live by | Note |
|---|---|---|---|
| **Christmas 2026 (25 Dec)** | **now** | ~10 Nov **[C]**, i.e. submit within days; review can take up to 3–4 weeks | Window ~15 Oct–18 Dec holds ~80% of a Christmas book's sales **[C]**; Etsy "printable" demand peaks in December **[C]** |
| **New Year / January peak** | mid-Dec | late Nov | "Adult coloring book" search interest peaked in Jan 2026 **[C]**; vision-board/goal themes spike **[C]** |
| Valentine's (14 Feb) | early Jan | mid-Dec | |
| Easter (28 Mar 2027) | late Feb | mid-Jan | |
| Mother's Day (9 May 2027) / Father's Day (20 Jun 2027) | 6–8 weeks ahead | 8 weeks ahead | |
| Back to school / summer travel | June | May | Travel word search, kids' activity |
| Halloween (31 Oct 2027) | late Aug | mid-Aug | |
| **Christmas 2027** | mid-Oct | **publish by September** | Relist and refresh winners annually |

Seasonal revenue is lumpy: a vendor estimate says 70–80% of a seasonal title's annual revenue lands in a ~6-week window **[C]**. Plan cash for it, and build a catalog of evergreen themes between peaks.

### 7.4 Onboarding new buyers

1. **First touch:** free 5-page sample on your own store (adult/parent-directed; avoid collecting kids' data, see COPPA in §11).
2. **Welcome email:** delivery instructions, printing tips, one related product.
3. **Post-purchase:** polite review request; QR/link to bonus pages (**check KDP content rules on external links before putting a URL in a book**).
4. **Retention:** series and occasion reminders ("Mother's Day kits go live in 6 weeks").
5. **Reorder logic:** make every product a numbered series entry with a visible "next book".

---

## 8. Monitoring and continuous improvement

### 8.1 KPI tree

| Stage | Metric | Source | Healthy range (hypothesis **[D]**) |
|---|---|---|---|
| Discover | Pinterest impressions, saves, outbound clicks; Etsy impressions | Platform analytics | Rising week over week |
| Click | Etsy listing click-through; Amazon CTR | Etsy Stats; Ads console | Amazon CTR 0.3–0.5% **[C]** |
| Convert | Etsy conversion; Amazon CVR | Same | Etsy 2–3% ok, 3–5% strong **[C]**; Amazon 8–12%+ for ad-supported books (§5.1) |
| Economics | Royalty per copy, net per Etsy sale, ACoS vs break-even, cost per title | Reports + your cost log | ACoS < break-even ACoS |
| Quality | Review rating, refund/complaint rate, QA fail rate | Platforms + QA log | ≥4.3★ average |
| Portfolio | **Hit rate** (% of titles reaching ≥5 copies/month by month 3), revenue per title-hour | Warehouse | ≥10% hit rate |

### 8.2 Operating cadence

- **Weekly:** pull KDP, Etsy, Pinterest and Ads reports into one store; flag winners and laggards.
- **Monthly:** portfolio review; kill/refresh/scale; check policy pages for changes (platform rules changed several times in 2025–26).
- **Quarterly:** re-score niches; refresh the seasonal pipeline; revisit pricing.

### 8.3 Decision rules (starting points, tune with data)

| Condition | Action |
|---|---|
| Etsy listing: ≥300 impressions and <1% click-through after 21 days | Rework thumbnail/title; retest |
| Etsy listing: ≥100 visits and <1% conversion | Rework price/bundle/description; if still weak, retire |
| KDP title: <1 copy/month after 90 days, no seasonal reason | Revise cover/keywords once; otherwise freeze (no ads), don't expand series |
| Title: ≥5 copies/month and ≥10 reviews | Scale: variants, series, bundle, controlled ads |
| Ad campaign: ACoS above break-even for 3 weeks | Pause or cut bids |
| Seasonal winner | Relist and refresh annually |

### 8.4 Experiments to run first

Cover A/B (Etsy thumbnails), price at $9.99 vs $10.99 vs $12.99 (KDP cliff), bundle size, title formats, Pinterest pin styles, sample-pack opt-in rates.

---

## 9. Automation blueprint

### 9.1 Pipeline

```
Intelligence → Niche scoring → Brief → Generate → QA gate → Compliance gate
     ↓                                                         ↓
Evidence ledger                                   Package (KDP / Etsy / PDF)
                                                              ↓
                      Listings + metadata → Human review queue → Publish (semi-manual)
                                                              ↓
          Marketing assets (pins, emails, video) → Analytics warehouse → Decision rules
                                                              ↑__________________________|
```

### 9.2 Modules and what's new

| Module | Function | Status |
|---|---|---|
| Market intelligence | Collect demand/competition proxies, Circana/PW headlines, Pinterest trends; prefer official APIs, exports or licensed tools. **Scraping Amazon/Etsy search may breach their terms; check first.** | Exists in part → extend |
| **Niche scorer + evidence ledger** | Implements the §4 matrix; stores each claim's source and grade | **New** |
| Brief generator | Audience, pain point, title/subtitle, keywords, price tier, risk flags | Exists → add price guardrail (≥$9.99) |
| Generators | Coloring pipeline; **deterministic puzzle engine + solver**; kids' text with fact-check agent; cover system | Puzzle engine **new/verify** |
| **QA gate** | Resolution/line weight/ink coverage; anatomy/hand/extra-finger VLM checks; OCR typo scan; puzzle uniqueness; readability; **near-duplicate detection across your own catalog** (perceptual hash/embeddings, because KDP penalises duplicative books **[C]**) | **New** |
| **Compliance gate** | IP/trademark/"in the style of" screen; medical-claim lint ("stress relief" ok, "treats anxiety" not); kids' safety; **per-platform disclosure generator** (KDP AI answers; Etsy description line + "Designed by a seller"); licence/provenance manifest (model, version, licence, prompt hash) | **New (highest priority)** |
| Packaging | Spine from page count, bleed, KDP-compliant PDFs; Etsy ZIP/PDF bundles | Exists → verify with proofs |
| Listing agents | KDP title/7 keywords/categories; Etsy title + 13 tags + description; Pinterest pin variants | Exists → extend |
| **Human review queue** | Spot-check UI; target ≤10 minutes per title; samples every N pages | **New** |
| Publish | Etsy via its API (verify scopes); **KDP upload: I could not confirm an official publishing API, so assume semi-manual with the 3 titles/day cap; browser automation may breach terms. Check KDP terms.** | Decision needed |
| Analytics warehouse | Ingest KDP/Etsy/Pinterest/Ads exports into Postgres; compute §8 KPIs; run decision rules; emit a weekly action list | **New** |
| Marketing automation | Pin scheduling, email sequences, short-video storyboards | **New** |

### 9.3 Build order (value first)

1. Compliance gate + provenance log (protects the whole business).
2. QA gate (duplicates, puzzle solver, line-art checks).
3. Niche scorer + evidence ledger.
4. Analytics warehouse + weekly report.
5. Pinterest/email automation.
6. Human-review queue polish.
7. B2B packaging (white-label export, client workspaces).

---

## 10. B2B opportunity (phase 3+, gated)

**Market reality.** The "AI KDP/ebook creator" space is crowded and cheap: KDP Builder (≈$19–$249/month tiers depending on source, credit packs from $10.99, $499 lifetime offer), Inkfluence ($9.99/$19.99 per month), Book Bolt ($89.99–$199.99/year), Publisher Rocket ($199 one-time), KDSPY ($79 one-time) **[C]**. Tools claim per-book costs of $5–$40 against $600–$2,000+ freelancer packages **[C]**. Competing on generic generation means competing against $10-a-month products.

**Where a defensible wedge could exist**

| Angle | Why it's different |
|---|---|
| **Compliance-first publishing** | Disclosure automation, provenance logs, IP screening, and audit trails: aimed at sellers worried about suspensions. Your background in regulated, audit-friendly systems fits this. Customer demand is unproven, so validate with interviews. |
| **Quality-gated "done-for-you" production** | A productized service for niche publishers/agencies: they supply the niche and brand, you deliver QA'd packages. Higher price, lower scale, closer to the "freelancer replacement" pain. |
| **Niche intelligence** | Evidence-scored niche briefs. Competes with research tools; only valuable if your scoring beats theirs. |

**Gate:** start B2B only after (a) your own catalog shows a ≥10% hit rate, (b) you know your real cost and QA time per title, and (c) at least five target customers say they'd pay for compliance/QA features. Pilot as a service for 3–5 customers before any SaaS build.

---

## 11. Operations, legal, tax and risk

### 11.1 Compliance and legal

| Area | Position |
|---|---|
| **AI disclosure** | Disclose on KDP (text/images/translations that AI generated), Etsy (description + "Designed by a seller"), Apple Books if used. When in doubt, disclose. |
| **Copyright** | Raw AI images are not protectable in the US (Copyright Office Part 2, Jan 2025; D.C. Circuit's *Thaler* decision, March 2025, upheld the human-authorship requirement) **[A]**. Selection and arrangement of AI material can be protected, and AI used as a tool in a human-authored work doesn't bar protection **[A]**. **Expect copying;** protect via brand, series, bundles and compilation. Don't claim copyright in individual raw images. |
| **Third-party IP** | No licensed characters, brand names, or "in the style of" living artists. Etsy prohibits copyrighted/trademarked characters **[C]**. Fan-art coloring books for hit properties (e.g. a chart-topping animated franchise) are an infringement trap. Run title/keyword trademark screens; consider registering your own brand names. |
| **Health claims** | Keep language to "relaxing/screen-free"; no therapeutic or treatment claims. |
| **Kids' content** | Aim marketing at parents; avoid collecting data from children (US COPPA). Fact-check all educational content. |
| **Model licences** | Use only Apache-2.0 (or equivalent) checkpoints; log version and licence; recheck on updates. |

### 11.2 Tax and structure (Australia-based seller; **not tax advice, confirm with an accountant**)

- **ABN** to trade; GST registration applies once you meet the ATO turnover threshold (check the current figure with the ATO). If registered, you charge 10% GST on taxable Australian sales; Etsy fees to Australian sellers include GST **[C]**.
- **US tax forms:** complete KDP's tax interview/W-8BEN; without it Amazon applies a 30% default withholding to US-source royalties **[C]**. A treaty rate for royalties of 5% is reported for Australia **[C]**, but sources conflict (another cites 15% for other income types), so ask your accountant. The W-8BEN does not replace your Australian return; worldwide income is declared in Australia.
- **KDP and GST:** ebooks sold to Australian customers carry 10% GST that KDP deducts before computing royalties **[B]**.
- **Entity:** sole trader vs. Pty Ltd, professional indemnity/insurance, and record-keeping (log AI provenance as evidence).

### 11.3 Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | Platform suspension / policy change (KDP, Etsy, TPT precedent) | Med-High | **Severe** | Compliance gate; honest disclosure; diversify channels (own store + email); monthly policy check; don't run duplicate accounts |
| 2 | Low-quality "AI slop" → refunds, reviews, removals | High | High | QA gate, human spot checks, proof copies, solver-verified puzzles |
| 3 | Saturation / no-demand niches | High | Med | Pre-validate with minimum assets; kill rules; hit-rate tracking |
| 4 | Thin margins (price cliff, ads) | High | Med | Price ≥$9.99/$12.99, bundles, organic-first |
| 5 | Copying by competitors (no copyright on raw images) | High | Med | Brand, series, speed, bundles, community |
| 6 | IP infringement claim | Low-Med | High | IP/trademark screens, no characters, own trademarks |
| 7 | Seasonal lumpiness / cash flow | High | Med | Evergreen backbone; low fixed costs |
| 8 | Tool/model licence changes | Med | Med | Provenance manifest; keep two Apache-2.0 model options |
| 9 | Operator bottleneck (QA, uploads, 3/day cap) | High | Med | Review queue; batch scheduling |
| 10 | Wrong data (third-party estimates, BSR) | High | Med | Replace with own data by month 2 |

---

## 12. Roadmap

### Next 7 days (26 Oct – 2 Nov)

- [ ] KDP/Etsy tax setup and ABN checks
- [ ] Compliance gate v0: disclosure text generator + provenance log
- [ ] 20–30 Christmas printable SKUs (bundles ≥$12) to Etsy/Gumroad; 3–5 Pinterest pins each
- [ ] 3–5 KDP Christmas titles at $9.99+ (toddler/senior/faith themes), with proof copies if timing allows

### Phase 1 (Nov–Dec 2026): Pilot and measure

- Publish 10 KDP titles and 30–40 Etsy SKUs across 5–6 niche hypotheses; stand up the QA gate; begin weekly reporting.
- Capture Pinterest Predicts 2027 (early December); start January/Valentine's pipeline.

### Phase 2 (Jan–Mar 2027): Learn and scale winners

- **Gate 1 (31 Jan 2027, my proposal):** ≥10 KDP titles and ≥40 Etsy listings live; ≥1,000 Etsy visits with conversion ≥2%; ≥1 KDP title ≥10 copies/month; documented QA minutes per title. If missed: fix listing/niche quality before adding volume.
- Build the analytics warehouse; scale winners to variants/series; Valentine's and Easter launches; test small Amazon/Etsy ad budgets on proven titles only.

### Phase 3 (Apr–Jun 2027): Systematise and explore B2B

- **Gate 2 (30 Apr 2027):** hit rate ≥10%; net positive after costs; run-rate ≥$1,000/month (base-case path). If below $300/month, cut to the best two niches and reduce spend.
- Interview 10 potential B2B customers; pilot a compliance-first service with 3–5 customers; evaluate wide distribution.

### Phase 4 (Jul–Oct 2027): Seasonal engine

- Christmas 2027 pipeline live by September; relist all seasonal winners; decide on a SaaS build only if the B2B gate passes.

---

## 13. Gap analysis: what the brief didn't cover

| # | Gap | Why it matters | Action |
|---|---|---|---|
| 1 | **Platform-policy fragility** is not a footnote: KDP enforcement, Etsy's tightening and TPT's ban show a direction of travel | A suspension removes the business | Compliance gate; policy watchlist; channel diversification |
| 2 | **Quality/"slop" backlash** from buyers and educators | Refunds, reviews, removals | QA gate; human review; proof copies |
| 3 | **No copyright on raw AI images** | Copying is legal and easy | Brand/series/bundles; don't rely on exclusivity |
| 4 | **Third-party IP and trend-jacking drift** (hit franchises dominate bestseller lists) | Infringement strikes | IP screen; no character names; generic themes |
| 5 | **Price cliffs and ad economics** | Many books can't be advertised profitably | Pricing rules (≥$9.99, ≥$12.99); organic-first |
| 6 | **Third-party sales estimates are unreliable** | Bad niche choices | Pre-test with minimum assets; own data by month 2 |
| 7 | **Saturation of head terms** (millions of "printable" listings) | Nothing ranks | Stack qualifiers; bundles; narrow audiences |
| 8 | **Seasonality and cash flow** | Revenue is lumpy | Calendar; evergreen backbone |
| 9 | **Tax, entity and payout mechanics** (ABN/GST, W-8BEN, withholding) | Avoidable tax leakage and compliance risk | Accountant; set up before first payout |
| 10 | **Print quality and proofing** | Rejections and bad reviews | Proof copies; template library; colour caution (KDP colour is poor for photography/fine art **[C]**) |
| 11 | **Catalog duplication across your own books** | KDP scrutiny of duplicative content **[C]** | Near-duplicate detector |
| 12 | **No customer feedback loop** | Can't improve | Reviews, email replies, surveys, analytics warehouse |
| 13 | **Owned audience** (email) | Platform dependence | Sample-pack opt-in; newsletters |
| 14 | **Brand and trademark** | Moat; Amazon Brand Registry needs a registered mark (verify) | Register 1–2 brand names |
| 15 | **Human-in-the-loop capacity** | You are the bottleneck | Review queue; time-per-title KPI |
| 16 | **Localisation** | Translated editions extend each asset's life, but KDP counts AI translations as AI-generated, so disclosure applies **[B]** | Pilot Spanish/German on top sellers |
| 17 | **Accessibility** | Large-print and clear layouts are the winning puzzle niche | Large-print templates with defined minimum font size |
| 18 | **Support, refunds, delivery issues** | Etsy ranks on customer experience | Templates; FAQ; fast response |
| 19 | **B2B realism** | Cheap competitors | Gate B2B; position on compliance/QA |
| 20 | **Ethical/brand positioning around AI** | Some buyers dislike AI art; Etsy's "Keep Commerce Human" posture | Transparent "human-directed, AI-assisted" positioning; real curation |
| 21 | **Product extensions not covered** | Possible later upside | Physical POD merch, stickers, subscriptions: out of scope until Gate 2 |

---

## 14. What I could not verify (assumptions to resolve)

- Real Amazon/Etsy sales volumes for any niche; all such numbers are tool-vendor estimates.
- The 16.7M children's coloring/activity unit figure (relayed secondhand from PW).
- Exact current KDP rules on external URLs/QR codes in books and on review solicitation.
- Whether KDP offers an official bulk-upload API (assume not).
- IngramSpark/Draft2Digital/B&N Press terms and AI rules.
- Current ATO GST threshold and treaty withholding specifics for your situation.
- Your measured per-title inference cost and QA time.
- Etsy conversion/sales-per-listing for your own shop (assumptions in §5.4 are placeholders).

---

## 15. Sources

**Primary / high-grade [A]**
- Publishers Weekly: [First-quarter print sales fell 3.1% (Circana BookScan)](https://www.publishersweekly.com/pw/print/20260406/100067-first-quarter-print-sales-fell-3-1.html)
- Publishers Weekly: [Passion purchases, analog living trend up (2026 outlook, children's activity books)](https://www.publishersweekly.com/pw/by-topic/industry-news/bookselling/article/99800-wi2026-passion-purchases-analog-living-trend-up.html)
- Circana Q3 2025 via [InfoDocket](https://www.infodocket.com/2025/10/27/circana-bookscan-reports-u-s-book-market-sales-hold-steady-in-q3/)
- Authors Guild: [Amazon's disclosure policy for AI-generated content](https://authorsguild.org/?p=21833)
- Chalkbeat: [TPT to ban AI-generated resources (15 Oct 2026)](https://www.chalkbeat.org/2026/10/15/teachers-pay-teachers-to-ban-ai-generated-teaching-resources/) · [AI slop on TPT (3 Aug 2026)](https://www.chalkbeat.org/2026/08/03/ai-slop-on-teachers-curriculum-marketplace/)
- TechCrunch: [Etsy Creativity Standards (July 2024)](https://techcrunch.com/2024/07/09/etsy-new-seller-policy-2024-generative-ai)
- US Copyright Office, AI Report Part 2 (Jan 2025): [report PDF](https://copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf) · summaries: [Authors Alliance](https://www.authorsalliance.org/2025/02/20/copyrightability-and-artificial-intelligence-a-new-report-from-the-u-s-copyright-office/), [DLA Piper/JD Supra](https://www.jdsupra.com/topics/copyright-registration/artificial-intelligence/copyright-litigation)
- Amazon KDP help: [GST in Australia](https://kdp.amazon.com/en_US/help/topic/A2HKGG0QNTNHU8) · [standard vs premium colour](https://kdp.amazon.com/en_US/help/topic/GX56BFPW4BKNPGFW) · [paper/ink options](https://kdp.amazon.com/help/topic/G201834180)
- Black Forest Labs: [FLUX.2 repository (licences)](https://github.com/brookman/flux2)
- Etsy: [Creativity Standards / House Rules](https://www.etsy.com/ca/new-guidelines)

**Vendor / secondary [B/C], use with caution**
- KDP AI policy & enforcement: [Univers Studio timeline](https://univers.studio/blog/kdp-ai-content-policy-2026/) · [Writeo on enforcement](https://writeo.app/news/amazon-kdp-ai-disclosure-enforcement-2026) · [BuiltWritten](https://www.builtwritten.com/blog/disclose-ai-in-your-book-kdp-policy-2026) · [Scribecount](https://scribecount.com/author-resource/protecting-books/kdp-ai-content-policy-the-compliance-guide)
- KDP low-content definition: [Inkfluence](https://www.inkfluenceai.com/blog/low-content-books-kdp-2026) · income table: [Inkfluence](https://www.inkfluenceai.com/blog/low-content-book-income-2026)
- KDP royalties/printing: [Vappingo](https://www.vappingo.com/word-blog/kdp-print-royalties/) · [BestWriting](https://bestwriting.com/kdp-royalties) · [Cambric](https://cambric.pub/guides/kdp-printing-cost-guide/) · [Author Central colour costs](https://theauthorcentral.com/blog/?p=1141)
- Etsy policy interpretation: [EcomCrew](https://www.ecomcrew.com/etsy-calls-itself-human-centered-its-sellers-have-a-more-complicated-story-to-tell/) · [Listadum](https://www.listadum.com/blog/etsy-creativity-standards) · [PromptlessPress](https://www.promptlesspress.com/blog-etsy-ai-policy-2026-digital-products) · [FindSkill (rumour check)](https://findskill.ai/blog/etsy-shopify-ai-photos-disclosure-rules/)
- Etsy fees/ads/conversion: [CheckoutPage](https://checkoutpage.com/blog/etsy-fees) · [Marmalead](https://blog.marmalead.com/etsy-fees-explained/) · [ListingView](https://listingview.io/blogs/how-etsy-ads-work-in-2026-and-when-to-turn-them-off) · [ECDB](https://ecdb.com/resources/sample-data/retailer/Etsy/transaction-kpis) · [ListingView conversion benchmarks](https://listingview.io/blogs/what-is-a-good-conversion-rate-on-etsy-in-2026)
- Etsy keyword/competition: [RankHero "printables"](https://www.rankhero.com/keywords/printables) · [RankHero "printable download"](https://www.rankhero.com/keywords/printable-download) · [ListifyAI "printable"](https://www.listifyai.net/keyword/printable)
- Category demand: [KDP Builder puzzle niches](https://kdpbuilder.com/blog/best-puzzle-book-niches) · [ASInsight word search large print](https://www.asinsight.com/report/US/word-search-large-print) · [KDP Builder seasonal calendar](https://kdpbuilder.com/blog/seasonal-kdp-niches) · [Inkfluence KDP calendar](https://www.inkfluenceai.com/kdp-publishing-calendar) · [KDPEasy seasonal](https://www.kdpeasy.com/blog/seasonal-activity-books-kdp) · [Low-competition niches (cites PW/Circana)](https://bookcoverslab.com/blog/low-competition-kdp-niches-2026)
- Coloring market sizes (conflicting): [TechSci via GII](https://gii.tw/report/tsci1714537-adult-coloring-book-market-global-industry-size.html) · [Accio trends](https://www.accio.com/business/new_coloring_book_trend) · [WisePPC low-content niches](https://wiseppc.com/blog/best-selling-low-content-books-amazon-kdp/)
- Pinterest: [Axios on Pinterest Predicts 2026](https://axios.com/2025/12/09/2026-pinterest-trend-report) · [CBNews (letter-writing trend data)](https://www.cbnews.fr/node/97374) · [Delzonic on Pinterest for Etsy](https://delzonic.com/blogs/best-etsy-niches-for-pinterest-2026/)
- Amazon Ads: [Eightx ACoS by vertical](https://eightx.co/blog/average-ecommerce-acos-amazon-by-vertical-2026) · [Univers KDP ads calculator](https://univers.studio/ads-calculator/) · [Vappingo Amazon Ads guide](https://www.vappingo.com/word-blog/amazon-ads-kdp-complete-guide/)
- Indie income: [Inkfluence on Written Word Media survey](https://www.inkfluenceai.com/blog/how-much-do-kdp-authors-make-2026) · [Self-publishing statistics](https://www.inkfluenceai.com/self-publishing-statistics) · [Written Word Media mid-2026](https://www.writtenwordmedia.com/how-authors-are-growing-in-2026-mid-year-survey-results/amp/)
- Competitor tools & pricing: [KDP Builder](https://kdpbuilder.com/kdpbuilder-pricing) · [Capterra KDP Builder](https://www.capterra.co.uk/software/1222074/KDP-Builder) · [Inkfluence pricing](https://www.inkfluenceai.com/pricing) · [iWrity KDP tools](https://www.iwrity.com/tools/best/kdp-keyword-research-tools) · [Nichepursuits Book Bolt vs Publisher Rocket](https://www.nichepursuits.com/?p=28995)
- Image-model licences: [Invideo licence matrix (Aug 2026)](https://invideo.io/blog/open-source-image-models-licenses/) · [VentureBeat on FLUX.2 klein](https://venturebeat.com/technology/black-forest-labs-launches-open-source-flux-2-klein-to-generate-ai-images-in)
- Direct-sales platforms: [InstantDM Gumroad alternatives](https://instantdm.com/blog/gumroad-alternatives-for-digital-products)
- Australia tax: [Sprintlaw ABN for Etsy](https://sprintlaw.com.au/articles/do-you-need-an-abn-for-etsy-in-australia/) · [Sprintlaw Etsy GST](https://sprintlaw.com.au/articles/etsy-gst-in-australia-do-you-need-to-charge-it/) · [Vappingo KDP non-US authors](https://www.vappingo.com/word-blog/kdp-for-non-us-authors/) · [ATO community thread](https://community.ato.gov.au/s/question/a0J9s0000001DmlEAE/p00029298)
- Illustrator costs and AI picture books: [Neolemon](https://www.neolemon.com/blog/hire-an-illustrator-or-use-ai-childrens-book-guide) · [Dupple](https://dupple.com/learn/how-to-illustrate-a-childrens-book-with-ai)
