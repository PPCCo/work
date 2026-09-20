# Standard: cover copy

Covers the words on the back cover and the words that travel with the cover into
a listing. Written by the `cover-copywriter` agent, consumed by
`cover_compose.py` (back cover) and by the framework's existing metadata and
marketing steps (`/book-metadata`, `/book-marketing`, `/book-ad-creatives`,
`ph_cli.py marketing kit`). Do not build a second marketing system — this
standard produces the inputs those already take.

---

## Back cover structure

In order, and no other elements:

1. **Headline** — 4 to 10 words. The promise, not a summary. It is read in the
   half-second after the shopper flips the book.
2. **Blurb** — one or two short paragraphs, 40 to 90 words total. Second person
   for practical books ("you"), third person for narrative.
3. **Bullets** — three to five, each under 60 characters, each a concrete,
   checkable fact: counts, page size, paper, age range, difficulty.
4. **Publisher line** — imprint name, optionally a one-line about-the-author.

Then nothing else. No review quotes that do not exist. No "coming soon". No price.

## Rules

- **Every claim is checkable against the built interior.** "100 puzzles" means
  the interior has 100 puzzles. The review gate verifies this, and a mismatch is
  a blocker.
- **No invented endorsements, awards, bestseller claims or review quotes.** Ever,
  in any form, including "readers love". If a real review exists, quote it
  accurately with attribution and record the source.
- **No comparison to named books, authors, or brands** ("the next X", "better
  than Y").
- **Reading level matches the audience of the book's buyer, not its reader.** A
  6-8 activity book's back cover is written for the adult buying it.
- **Keep it plain.** Short sentences. Concrete nouns. Cut every adjective that
  survives deletion.

## Length budget by audience

| Audience | Headline | Blurb | Bullets |
|---|---|---|---|
| early-reader-6-8 | 4–8 words | 40–60 words | 3, very concrete |
| middle-grade-9-12 | 5–10 words | 60–90 words | 3–4 |
| teen-13-17 | 5–10 words | 60–90 words | 3–4 |
| adult-general | 4–8 words | 70–110 words | 4–5, benefit-led |

## What travels onward

The same copy object feeds the listing. Produce these fields once and pass them
to the metadata step rather than rewriting them:

- `title`, `subtitle` — exactly as set on the cover, character for character. A
  mismatch between cover art and metadata is a common rejection cause.
- `headline`, `blurb`, `bullets` — the retailer description is built from these,
  expanded, not reinvented.
- `keywords` — seven phrases a buyer would actually type. Not a bag of single
  words, not a repetition of the title, no other publisher's brand names.
- `categories` — two or three, chosen against the channel's current category
  tree, matched to the real content.
- `audience` and `age_range` — carried through from `project.yaml`.
- `ai_disclosure` — model, version, and which assets were generated. Channels
  ask during publishing; the answer is prepared here, not improvised.

## Series copy

A series shares its headline pattern and bullet structure across every title.
Only the specifics change. Write the pattern once with the first book, record it
in the series record, and apply it — consistent back covers are one of the
cheapest signals of a real publisher.
