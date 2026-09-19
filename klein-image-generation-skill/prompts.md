#

## Klein Prompt

I'm using Claude to give prompts to a local install of Klein-4B to generate via ComfyUI MCP Server to generate colored images for kids. The output quality is inconsistent. Sometimes it's good, sometimes bad. Can you think hard and create a "Claude skill" (including any klein-prompt-standards, prompt-audit-agent, python scripts, etc if needed) that would generate prompts for high quality results

## Klein Prompt Response

Klein-4B is FLUX.2 [klein] — which changes almost everything about how you should be prompting it. Let me check one thing before I build, then I'll write the skill.Now the reference docs and the SKILL.md itself.Now let me actually test the scripts end to end, including against a fake ComfyUI workflow.The `.skill` file is above — click **Save skill** on that card to install it, or use the loose folder if you'd rather edit it first.

**What I found first, because it changes the diagnosis:** Klein-4B is FLUX.2 [klein] 4B, a rectified-flow transformer paired with a **Qwen3 4B text encoder** — not CLIP. Three things follow that are almost certainly behind your inconsistency:

- **Negative prompts don't work.** Black Forest Labs says FLUX.2 doesn't support them. On the distilled variant there's no unconditional pathway to attach one to. So "no scary faces" just feeds "scary face" to a language model, which sometimes draws it. That alone produces good-run/bad-run behaviour.
- **Tag soup has nothing holding it still.** `masterpiece, best quality, 8k, (thick lines:1.3)` is grammar-free to a language encoder, so each seed interprets it differently. Word order is the weighting mechanism now, not `(word:1.2)`.
- **You're probably drafting and finishing on the same variant.** The 4-step distilled model mangles line art and painted texture; the base model at ~24 steps doesn't. Drafting on distilled and re-rendering the keeper on base _with the same seed_ is the biggest single fix.

**What the skill does about it.** An 11-slot prompt contract with fixed order, six style packs whose signature block gets pasted verbatim into every image in a set (this is what stops page 7 looking like a different book), and three age bands that cap subject counts — a 4B model fuses repeated characters past two or three.

Three scripts, all tested here:

- `audit_prompt.py` — a hard gate. Blocks negations, SD syntax, quality tags, missing style signature, colour words leaking into line art, over-count scenes, floating hex codes, and unsafe-for-kids content. Exit code 1 on failure so you can wire it into a pipeline.
- `build_prompt.py` — assembles prompts from a brief, emits runtime params, deterministic seeds (same brief regenerates the same candidates tomorrow) and the audit result. All 18 pack×age combinations currently score 97–100 against the auditor.
- `batch_generate.py` — posts an API-format workflow to ComfyUI, polls, downloads, and writes a `manifest.jsonl` recording which prompt and seed made which file. Stdlib only.

Two things to check on your end: the parameter defaults are starting points, so trust your ComfyUI template's shipped values over mine and record the real ones in `runtime.local.md`. And ComfyUI MCP servers vary a lot — the skill tells Claude to inspect the tool signature before the first call rather than assuming.

One thing I guessed at: "colored images for kids" could mean colouring-in sheets or full-colour illustrations, so I built both. If you're only doing one, delete the packs you don't need.

---

## Klein cover Prompt

I have a Claude framework for autonomously creating books for all ages here: https://github.com/PPCCo/publish-book

My book publishing company creates non-fiction books, puzzle books, coloring books, productivity books etc for all age groups.

These are the age groups (`audience`) I have defined in my framework:

- `early-reader-6-8`
- `middle-grade-9-12`
- `teen-13-17`
- `adult-general`

### TASK

Since I sell my books on Amazon/Etsy/ebay/KDP/AppleBooks/etc, and since book covers are the first impression, I need you to add to the above Klein-4B setup or modify any files you created above (to make the cover-generation compatable with the Klein setup), the tools/skills/agents/rules/standards/etc needed to design awesome covers for the books.

Create a comprehensive setup for whatever skills, agents, standards, rules, scripts etc that would be needed for Claude to autonomously create the best book covers (including front cover, back cover, and cover-spine). If there are Claude built in agents for advertizing, media, marketing, designer, publishing, etc, then refer to those skills in the requirements, otherwise create new agents and/or skills and/or standards etc

## Klein cover Prompt Response

Let me look at your framework and verify the current KDP/retailer specs before I build anything.Now I'll build the cover system. First the spec/data layer and scripts, then standards, agents and skills.Scripts all work. Now the standards, agents and skills that make them usable autonomously.Now the integration guide that ties it into your lifecycle and CLI.Final end-to-end run to confirm everything still works together, then packaging.I read your repo first, and it changed the shape of the answer: you don't need a standalone cover skill, you need a `.claude/` extension that obeys your existing lifecycle, gates and artefact hashing. That's what the zip is — copy `.claude/` over yours, nothing collides.

**The central decision: Klein renders artwork, never the title.**

FLUX.2 can produce legible text, but a cover title must be exact at every size, in a named typeface, matching your metadata record character for character, and editable when the subtitle changes. A diffusion model can promise none of that. So art prompts reserve an empty _type zone_, and `cover_compose.py` sets every word from real font files at 300 DPI. `cover_prompt.py` blocks any prompt that asks for text.

**Four new `/book-*` skills** slotting into your lifecycle: `/book-cover-brief` (VISUAL_DEVELOPMENT), `/book-cover-art`, `/book-cover-compose` (LAYOUT_AND_FORMAT_BUILD), `/book-cover-review` (before FINAL_PROOF). Four agents behind them — art director, typographer, copywriter, critic. Five standards. All outputs land in `projects/<id>/visuals/cover/`, which already exists in your structure. No skill grants a gate; they recommend, humans approve the hash.

**Five scripts, all tested end to end here.** `cover_spec.py` does the geometry once — spine from page count × paper thickness, bleed, safe areas, barcode zone, hardcover hinges — and everything downstream reads it rather than retyping a spine width. `cover_compose.py` builds the wrap, composes the ebook cover _separately_ (different aspect; a scaled print front crops the type badly), and fails the build if text leaves the safe area or back copy reaches the barcode zone. `thumbnail_test.py` renders 80/120/240px plus greyscale and squint. `cover_preflight.py` catches what a retailer would bounce. I rendered two complete covers through the chain — an 8.5×11 kids' colouring wrap and a 6×9 adult journal — and fixed three real bugs the renders exposed.

**Three things you should know before running it:**

Klein tops out around 2MP; a 300 DPI print front is 3–9MP. `cover_prompt.py` emits the required upscale factor and expects a ComfyUI upscale model in your chain. Flat vector and graphic packs survive it almost perfectly, which is why they're the defaults for activity and puzzle lines.

Public sources disagree on whether KDP's paperback spine includes a ~0.06″ cover-stock allowance. The default assumes none; `--cover-thickness 0.06` is there if your generated templates say otherwise. Every script tells you to diff against KDP's own template before export.

`fc-match` always returns _something_, so a missing font silently becomes DejaVu. The composer now detects that and warns loudly — a substituted font means the cover you built isn't the one you specified and your licence record is wrong.

On built-in agents: Anthropic ships no advertising, media, marketing or designer agents to reference — general subagents and document-format skills, nothing domain-specific. You already have `/book-marketing`, `/book-ad-creatives` and `marketing kit`, so I deliberately didn't add a marketing agent. `cover-copywriter` produces one copy object (headline, blurb, bullets, keywords, categories) that your existing steps consume. A second marketing system would only disagree with the first.

Section 5 of INTEGRATION.md lists six small additive edits to your existing files — mainly teaching `/book-metadata` to take title and keywords from `copy.json` rather than rewriting them, since a cover/metadata title mismatch is a common rejection cause.
