#!/usr/bin/env python3
"""
build_prompt.py - assemble FLUX.2 [klein] 4B prompts for children's images.

Why this exists: Klein's output quality is mostly a function of prompt *shape*,
not prompt cleverness. The same slots, in the same order, with the style block
pasted verbatim, is what makes a set of twelve pages look like one artist drew
them. This script enforces that shape and then runs audit_prompt.py on the
result, so nothing ill-formed reaches the queue.

Single image:
  python build_prompt.py --pack chunky_vector --age 5-7 \
      --subject "a round orange cat" --action "balancing on a beach ball" \
      --setting "a sunny back garden" --props "daisies,a red bucket" --print

Whole series from a brief (recommended for books and card sets):
  python build_prompt.py --brief ../assets/brief.example.json --out plan.json --print

Output is JSON: one entry per image with prompt, runtime params, seed plan and
audit result. Feed the prompt + params straight into the ComfyUI MCP tools, or
into batch_generate.py.
"""

import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from audit_prompt import audit, load_packs, PACKS_PATH, render  # noqa: E402

# Runtime starting points. The values shipped inside your ComfyUI template
# workflow always win over these - overwrite them in references/runtime.local.md
# once you have measured what your install actually likes.
RUNTIME = {
    "distilled": {"steps": 4, "cfg": 1.0, "sampler": "euler", "scheduler": "simple", "denoise": 1.0},
    "base": {"steps": 24, "cfg": 4.0, "sampler": "euler", "scheduler": "simple", "denoise": 1.0},
}


def stable_seed(text, i):
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return (int(h[:12], 16) + i * 9973) % (2 ** 31 - 1)


def join_clauses(parts):
    out = []
    for p in parts:
        if not p:
            continue
        p = p.strip().rstrip(".,")
        if p:
            out.append(p)
    text = ", ".join(out)
    return text[0].upper() + text[1:] + "." if text else text


def build_one(item, pack_name, age, data, character_sheet=None,
              palette_override=None, aspect=None, variant=None):
    pack = data["packs"][pack_name]
    band = data["age_bands"][age]

    signature = pack["signature"].replace("{line_weight}", band["line_weight"])

    props = item.get("props") or []
    if isinstance(props, str):
        props = [p.strip() for p in props.split(",") if p.strip()]
    props = props[:band["max_props"]]

    palette = palette_override if palette_override is not None else pack["palette"]
    palette_clause = ""
    if palette and pack_name != "coloring_page":
        named = item.get("palette_targets") or []
        if named and len(named) == len(palette):
            palette_clause = ", ".join("%s in color %s" % (n, c) for n, c in zip(named, palette))
        else:
            palette_clause = "colour palette of %s" % " ".join(palette[:5])

    text_clause = ""
    if item.get("text"):
        text_clause = "the word \"%s\" hand-lettered in the %s" % (
            item["text"], item.get("text_position", "upper area"))

    setting = item.get("setting", pack["background"])
    if props:
        setting = "%s with %s" % (setting, " and ".join(props))

    # Slot order matters: Klein attends most strongly to the opening words.
    # Subject -> action -> expression -> identity -> style -> scene -> light
    # -> colour -> framing -> text.
    prompt = join_clauses([
        item["subject"],
        item.get("action"),
        item.get("expression", "with a warm friendly expression"),
        character_sheet,
        signature,
        band["detail_phrase"],
        setting,
        item.get("light", pack["light"]),
        palette_clause,
        item.get("composition", pack["composition"]),
        text_clause,
    ])

    variant = variant or pack["runtime"]["variant"]
    aspect = aspect or pack["runtime"]["aspect"]
    w, h = data["aspect_presets"][aspect]
    params = dict(RUNTIME[variant])
    if pack_name == "coloring_page" and variant == "base":
        params["steps"] = 28
    params.update({"width": w, "height": h, "variant": variant, "aspect": aspect})

    n = int(item.get("candidates", 4))
    seeds = [stable_seed(prompt, i) for i in range(n)]

    result = audit(prompt, pack_name, age, data)
    stem = "%s_%s_%s" % (pack_name, item.get("id", "img"),
                         hashlib.sha256(prompt.encode()).hexdigest()[:6])

    return {
        "id": item.get("id", "img"),
        "prompt": prompt,
        "params": params,
        "seeds": seeds,
        "filename_stem": stem,
        "audit": result,
    }


def main():
    ap = argparse.ArgumentParser(description="Build Klein kids'-art prompts.")
    ap.add_argument("--brief", help="JSON brief (see assets/brief.example.json)")
    ap.add_argument("--pack")
    ap.add_argument("--age", default="5-7", choices=["2-4", "5-7", "8-10"])
    ap.add_argument("--subject")
    ap.add_argument("--action")
    ap.add_argument("--expression")
    ap.add_argument("--setting")
    ap.add_argument("--props")
    ap.add_argument("--text", help="Short word to render in the image (3 words max)")
    ap.add_argument("--character-sheet", dest="character_sheet")
    ap.add_argument("--aspect", choices=["square", "portrait", "landscape", "spread", "page"])
    ap.add_argument("--variant", choices=["distilled", "base"])
    ap.add_argument("--candidates", type=int, default=4)
    ap.add_argument("--packs", default=PACKS_PATH)
    ap.add_argument("--out")
    ap.add_argument("--print", dest="do_print", action="store_true")
    ap.add_argument("--force", action="store_true", help="Emit even if the audit fails.")
    a = ap.parse_args()

    data = load_packs(a.packs)

    if a.brief:
        brief = json.load(open(a.brief, "r", encoding="utf-8"))
        pack = a.pack or brief["pack"]
        age = brief.get("age", a.age)
        items = brief["images"]
        character_sheet = a.character_sheet or brief.get("character_sheet")
        palette = brief.get("palette")
        aspect = a.aspect or brief.get("aspect")
        variant = a.variant or brief.get("variant")
    else:
        if not (a.pack and a.subject):
            ap.error("give --brief, or at least --pack and --subject")
        pack, age = a.pack, a.age
        character_sheet, palette = a.character_sheet, None
        aspect, variant = a.aspect, a.variant
        items = [{
            "id": "single", "subject": a.subject, "action": a.action,
            "expression": a.expression, "setting": a.setting, "props": a.props,
            "text": a.text, "candidates": a.candidates,
        }]

    built = [build_one(i, pack, age, data, character_sheet, palette, aspect, variant)
             for i in items]
    plan = {"pack": pack, "age": age, "character_sheet": character_sheet, "images": built}

    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(plan, fh, indent=2, ensure_ascii=False)

    failed = [b for b in built if not b["audit"]["status"].startswith("PASS")]
    if a.do_print or not a.out:
        for b in built:
            print()
            print(render(b["audit"], b["prompt"]))
            print("PARAMS: %s" % json.dumps(b["params"]))
            print("SEEDS : %s" % b["seeds"])
    if a.out:
        print("\nWrote %s (%d images, %d need fixing)" % (a.out, len(built), len(failed)))

    if failed and not a.force:
        print("\n%d prompt(s) failed the audit. Fix them before queueing, or pass "
              "--force if you know what you are doing." % len(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
