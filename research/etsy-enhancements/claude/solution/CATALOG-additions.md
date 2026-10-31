# Agent catalogue additions

Append these rows to `.claude/agents/CATALOG.md` (after AGT-034) and update `.claude/agents/README.md`: "31 role-specific agents" becomes "39", and add the departments' new members. Keep this file **outside** `agents/` (the validator treats other `.md` files there as agents).

| ID | Agent | Department | Primary mission |
|---|---|---|---|
| AGT-035 | `kit-architect` | Content | Convert an approved niche and competitive report into a complete, feasible `kit.yaml`: promise-matched components, age versions, themes, Standard⊂Expanded SKUs, variant matrix, delivery strategy, and season feasibility. |
| AGT-036 | `craft-designer` | Content | Author original, age-differentiated craft cards and gift projects with accurate materials, safe steps, hazard tags, supply reuse, and code-drawable diagram briefs. |
| AGT-037 | `party-game-designer` | Content | Design original party games with sourced trivia, group-size scaling, workplace-safe variants, and generator parameters for bingo and gift exchange. |
| AGT-038 | `keepsake-designer` | Content | Design keepsakes, stationery, invitations, and templates with personalisation field specs, theme tokens, and original in-voice copy. |
| AGT-039 | `template-engineer` | Production | Render the full variant matrix (Letter/A4 × colour/ink-friendly × age × theme) from approved source with embedded fonts, cut grids, fillable fields, and per-variant checks. |
| AGT-040 | `listing-image-director` | Visual Production | Plan and build the Etsy gallery from real rendered pages with verified counts, thumbnail-legible headlines, alt text, and truthful depiction. |
| AGT-041 | `fact-checker` | Quality | Independently verify trivia and factual statements against cited sources; mark confirmed, disputed, or unverifiable. |
| AGT-042 | `craft-safety-reviewer` | Quality | Desk-check craft, gift, and pet-keepsake content for material/step consistency, hazards by age version, supervision, and make-test evidence status. |

## Existing agents: scope notes for kits

- `market-analyst`: use skill `kit-seasonal-plan` for season windows and dated evidence; competitive pass must include Etsy listing patterns per rule 14/24 and the validation angle.
- `commercial-writer`: Etsy copy must obey rule 26 limits (title ≤ 140; tags ≤ 20 characters each, ≤ 13) and read counts from the verification report; per-SKU, not per-project.
- `pricing-strategist`: produce a **ladder** (Standard/Expanded) with explicit basis; prices stay recommendations.
- `rights-manager`: run the trademark/association screen on coined seasonal terms (rule 28) and extended-licence compatibility (rule 29).
- `child-safety-reviewer`: unchanged; works alongside `craft-safety-reviewer`.
- `packaging-engineer`: calls `kit deliver` and `kit preflight` for `digital-kit` projects.
- `accessibility-auditor`: audits every variant's render report; ink-friendly variants need measured contrast.
- `art-director`: supplies style tokens per theme; approves scene providers used in listing images.
