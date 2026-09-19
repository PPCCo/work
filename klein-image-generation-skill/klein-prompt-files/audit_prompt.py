#!/usr/bin/env python3
"""
audit_prompt.py - deterministic gate for FLUX.2 [klein] 4B kids'-art prompts.

Catches the mechanical failures that cause "sometimes good, sometimes bad":
leftover Stable Diffusion habits, negations (which Klein cannot honour and
often renders literally), missing style-pack signature, bad word order,
over-stuffed scenes, unattached hex codes, and content that isn't fit for kids.

Usage
-----
  python audit_prompt.py --pack coloring_page --age 5-7 --prompt "..."
  python audit_prompt.py --pack chunky_vector --age 2-4 --file prompt.txt
  echo "..." | python audit_prompt.py --pack storybook_gouache --age 5-7 --stdin
  python audit_prompt.py ... --json          # machine-readable
  python audit_prompt.py ... --quiet         # exit code only

Exit codes: 0 = PASS (score >= 80, no blockers), 1 = FIX REQUIRED, 2 = usage error.

This is a lint, not a judge. It cannot tell whether the image will be charming.
Run it first, then apply the human/model judgement in
references/prompt-audit-agent.md.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PACKS_PATH = os.path.join(HERE, "..", "assets", "style_packs.json")

BLOCKER = "blocker"   # never queue this prompt
WARNING = "warning"   # usually worth fixing
NOTE = "note"         # informational

PENALTY = {BLOCKER: 34, WARNING: 10, NOTE: 3}

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "twelve": 12,
    "dozen": 12, "many": 99, "lots of": 99, "a group of": 99,
    "a crowd of": 99, "several": 99, "countless": 99, "swarm of": 99,
}

HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b")
QUOTED_RE = re.compile(r"[\"'\u2018\u2019\u201c\u201d]([^\"'\u2018\u2019\u201c\u201d]{1,60})[\"'\u2018\u2019\u201c\u201d]")


def load_packs(path=PACKS_PATH):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _find(patterns, text, regex=False):
    """Return the patterns that match text. Plain patterns match on word
    boundaries so that 'red' does not fire inside 'centred'."""
    hits = []
    for p in patterns:
        if regex:
            if re.search(p, text, flags=re.IGNORECASE):
                hits.append(p)
        else:
            if re.search(r"\b%s\b" % re.escape(p), text, flags=re.IGNORECASE):
                hits.append(p)
    return hits


def audit(prompt, pack_name, age_band, data=None, is_edit=False):
    """Return a dict: {score, status, issues[], stats{}}."""
    data = data or load_packs()
    packs = data["packs"]
    bans = data["banned_everywhere"]
    issues = []

    def add(level, code, message, fix):
        issues.append({"level": level, "code": code, "message": message, "fix": fix})

    if pack_name not in packs:
        return {
            "score": 0, "status": "FIX",
            "issues": [{"level": BLOCKER, "code": "unknown_pack",
                        "message": "Unknown style pack: %s" % pack_name,
                        "fix": "Use one of: %s" % ", ".join(sorted(packs))}],
            "stats": {},
        }

    pack = packs[pack_name]
    band = data["age_bands"].get(age_band) or data["age_bands"]["5-7"]
    text = prompt.strip()
    low = text.lower()
    words = re.findall(r"[\w'#-]+", text)
    wc = len(words)

    # ---------- 1. Safety first ----------
    hits = _find(bans["unsafe_for_kids"], low)
    if hits:
        add(BLOCKER, "unsafe_content",
            "Content not suitable for a children's image: %s" % ", ".join(hits),
            "Remove it. If the story needs tension, describe a gentle version "
            "(a surprised face, a rain cloud) rather than a frightening one.")

    hits = _find(bans["real_person_risk"], low)
    if hits:
        add(BLOCKER, "real_child_likeness",
            "Prompt reaches for a real or photoreal child: %s" % ", ".join(hits),
            "Do not generate likenesses of real children or photoreal children. "
            "Describe an invented, clearly illustrated character instead.")

    hits = _find(bans["brand_names"], low)
    if hits:
        add(BLOCKER, "licensed_character",
            "Named copyrighted character or brand: %s" % ", ".join(hits),
            "Describe the qualities you actually want (a round yellow robot with "
            "big eyes) instead of borrowing someone's character.")

    # ---------- 2. Klein-specific prompt mechanics ----------
    hits = _find(bans["negation_patterns"], text, regex=True)
    if hits:
        add(BLOCKER, "negation",
            "Contains negation. Klein has no negative pathway; the encoder sees the "
            "noun and often draws it. Matched: %s" % ", ".join(h.strip("\\b") for h in hits),
            "Restate as the positive fact. 'no shadows' -> 'flat even lighting'; "
            "'not scary' -> 'smiling and friendly'; 'no text' -> describe the surface as blank.")

    hits = _find(bans["sd_syntax"], text, regex=True)
    if hits:
        add(BLOCKER, "sd_syntax",
            "Stable-Diffusion-era syntax found (weights, alternation, BREAK, lora tags). "
            "Klein reads plain language through a Qwen3 text encoder and treats this as literal junk.",
            "Delete the syntax and express emphasis by word order instead: "
            "put what matters most in the first ten words.")

    hits = _find(bans["quality_tags"], low)
    if hits:
        add(WARNING, "quality_tag_soup",
            "Booru/quality tags: %s. These add nothing on Klein and dilute the "
            "real description." % ", ".join(hits),
            "Delete them. Describe the medium instead (gouache, cut paper, flat vector).")

    # ---------- 3. Style pack integrity ----------
    missing = [t for t in pack.get("require_tokens", []) if t.lower() not in low]
    if missing:
        add(BLOCKER, "signature_missing",
            "Missing the pack's signature terms: %s" % ", ".join(missing),
            "Paste the pack signature from assets/style_packs.json verbatim. "
            "Rewording it per image is the main reason a set drifts.")

    hits = _find(pack.get("forbid_tokens", []), low)
    if hits:
        add(WARNING, "cross_pack_contamination",
            "Terms that fight this pack: %s" % ", ".join(hits),
            "Drop them. Mixing two media descriptions gives Klein a contradiction to "
            "average out, which is exactly what produces the mushy in-between look.")

    if pack_name == "coloring_page":
        colour_words = ["red", "blue", "green", "yellow", "orange", "purple", "pink",
                        "golden", "turquoise", "brown fur", "colourful", "colorful"]
        hits = _find(colour_words, low) + HEX_RE.findall(text)
        if hits:
            add(BLOCKER, "colour_in_line_art",
                "Colour words in a coloring page: %s" % ", ".join(hits),
                "Strip every colour reference. The child supplies the colour; the model "
                "should only be told about black lines on white.")
        if "closed" not in low and "fully enclosed" not in low:
            add(WARNING, "open_shapes",
                "No instruction that shapes are closed.",
                "Add 'every shape fully closed' so crayon and bucket-fill stay inside the lines.")

    # ---------- 4. Word order and length ----------
    lo, hi = pack.get("word_budget", [40, 90])
    if wc < lo:
        add(WARNING, "too_short",
            "%d words; this pack wants %d-%d." % (wc, lo, hi),
            "Add setting, light and composition. Under-specified prompts are the "
            "single biggest source of run-to-run variance.")
    elif wc > hi + 25:
        add(WARNING, "too_long",
            "%d words; this pack wants %d-%d." % (wc, lo, hi),
            "Cut secondary detail from the tail. Klein weights early words heavily, "
            "so a long tail mostly adds noise.")
    elif wc > hi:
        add(NOTE, "slightly_long", "%d words (target %d-%d)." % (wc, lo, hi),
            "Fine, but trim the tail if results wander.")

    head = " ".join(words[:4]).lower()
    style_lead = any(k in head for k in
                     ["illustration", "line art", "render", "watercolor", "gouache",
                      "collage", "vector illustration", "style", "coloring book",
                      "picture book", "drawing of", "artwork"])
    if style_lead and not is_edit:
        add(WARNING, "style_first",
            "The prompt opens with style, not subject.",
            "Open with the subject and what it is doing. Klein pays most attention to "
            "the front of the prompt; style belongs in the middle.")

    # ---------- 5. Scene load for the age band ----------
    # Trailing "(?!-)" keeps compound modifiers like "three-quarter view" and
    # "one-piece" out of the subject count.
    over = []
    for w, n in NUMBER_WORDS.items():
        if re.search(r"\b%s\b(?!-)" % re.escape(w), low) and n > band["max_subjects"]:
            over.append(w)
    for m in re.finditer(r"\b(\d+)(?!-)\s+\w+", low):
        if int(m.group(1)) > band["max_subjects"]:
            over.append(m.group(1))
    if over:
        add(WARNING, "too_many_subjects",
            "Counts above this age band's limit of %d: %s. A 4B model loses track of "
            "repeated characters and starts fusing them." % (band["max_subjects"], ", ".join(sorted(set(over)))),
            "Reduce the count, or say 'a few' and accept whatever it gives you.")

    conj = len(re.findall(r"\bwhile\b|\bas\b|\band then\b|\bbehind\b|\bin front of\b", low))
    if conj >= 3:
        add(WARNING, "spatial_overload",
            "Several simultaneous spatial/temporal clauses.",
            "One action, one spatial relation. Split extra ideas into a second image.")

    # ---------- 6. Colour and text handling ----------
    hexes = HEX_RE.findall(text)
    if len(hexes) > 6:
        add(WARNING, "too_many_hex",
            "%d hex codes; colour accuracy degrades as they pile up." % len(hexes),
            "Keep four or five, each attached to one named object.")
    for h in hexes:
        i = text.find(h)
        before = text[max(0, i - 40):i].lower()
        if HEX_RE.search(before):
            continue  # part of a palette list; the first code anchors the run
        if not re.search(r"(color|colour|hex|in|is|painted|fill|background|fur|shirt|sky|walls?)\s*[\w\s]{0,20}$", before):
            add(NOTE, "floating_hex",
                "Hex %s is not clearly attached to an object." % h,
                "Write 'the hat is color %s' rather than dropping the code loose." % h)

    quotes = QUOTED_RE.findall(text)
    if len(quotes) > 1:
        add(WARNING, "multiple_text_strings",
            "%d quoted strings. Klein renders text well for its size but degrades fast "
            "past one short string." % len(quotes),
            "Keep one quoted string, three words or fewer.")
    for q in quotes:
        if len(q.split()) > 3:
            add(WARNING, "long_text_string",
                "Quoted text '%s' is long; expect malformed letters." % q,
                "Shorten to three words, or add the text afterwards in a layout tool "
                "where it will be perfect and editable.")

    # ---------- 7. Composition safety net ----------
    if not any(k in low for k in ["centred", "centered", "full body", "in frame",
                                  "close-up", "close up", "wide", "framing", "view",
                                  "portrait", "margin", "space around", "foreground",
                                  "three-quarter", "front-on"]):
        add(NOTE, "no_composition",
            "No framing instruction.",
            "Add one ('full body, centred, space around it'). Cropped heads and "
            "cut-off feet are the most common reason a kids' image is unusable.")

    # ---------- score ----------
    score = 100
    for it in issues:
        score -= PENALTY[it["level"]]
    score = max(0, score)
    blocked = any(i["level"] == BLOCKER for i in issues)
    if blocked or score < 70:
        status = "FIX"          # do not queue
    elif score >= 88:
        status = "PASS"
    else:
        status = "PASS_WITH_NOTES"   # queue it, but read the notes

    return {
        "score": score,
        "status": status,
        "issues": issues,
        "stats": {
            "word_count": wc,
            "pack": pack_name,
            "age_band": age_band,
            "hex_codes": len(hexes),
            "quoted_strings": len(quotes),
        },
    }


def render(result, prompt):
    icon = {BLOCKER: "BLOCK", WARNING: " WARN", NOTE: " NOTE"}
    out = []
    out.append("=" * 68)
    out.append("PROMPT AUDIT  %s   score %d/100   %d words"
               % (result["status"], result["score"], result["stats"].get("word_count", 0)))
    out.append("=" * 68)
    if not result["issues"]:
        out.append("Clean. Nothing mechanical left to fix - now judge it on taste.")
    for it in result["issues"]:
        out.append("[%s] %s" % (icon[it["level"]], it["message"]))
        out.append("        -> %s" % it["fix"])
    out.append("-" * 68)
    out.append("PROMPT: %s" % prompt.strip())
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Audit a Klein kids'-art prompt.")
    ap.add_argument("--pack", required=True)
    ap.add_argument("--age", default="5-7", choices=["2-4", "5-7", "8-10"])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt")
    src.add_argument("--file")
    src.add_argument("--stdin", action="store_true")
    ap.add_argument("--edit", action="store_true",
                    help="Prompt is an image-edit instruction, not a generation prompt.")
    ap.add_argument("--packs", default=PACKS_PATH)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    if a.prompt:
        prompt = a.prompt
    elif a.file:
        prompt = open(a.file, "r", encoding="utf-8").read()
    else:
        prompt = sys.stdin.read()

    result = audit(prompt, a.pack, a.age, load_packs(a.packs), is_edit=a.edit)
    if a.json:
        print(json.dumps(result, indent=2))
    elif not a.quiet:
        print(render(result, prompt))
    return 0 if result["status"].startswith("PASS") else 1


if __name__ == "__main__":
    sys.exit(main())
