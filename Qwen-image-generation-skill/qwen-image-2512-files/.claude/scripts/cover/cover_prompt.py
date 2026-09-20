#!/usr/bin/env python3
"""
cover_prompt.py - build Qwen-Image-2512 (Q8_0) prompts for cover artwork.

The rule this script exists to enforce: **the image model renders artwork,
never the title.** Cover typography is set later by cover_compose.py from
real font files, because a title has to be exactly right at every size,
match the metadata record character for character, and be editable when the
subtitle changes - none of which a diffusion model can promise, however good
it has gotten at in-image text. So every prompt here asks for art with a
deliberate empty type zone, and no prompt asks for words.

  python cover_prompt.py --spec spec.json --audience early-reader-6-8 \
      --book-type coloring-book --subject "a friendly cartoon triceratops" \
      --action "waving one hand" --variant lightning --out art-plan.json --print

  # whole series, sharing one look:
  python cover_prompt.py --brief cover-brief.yaml --out art-plan.json

Reuses the qwen-kids-art auditor when it can find it (set QWEN_SKILL_PATH or
pass --qwen-path) so cover prompts are held to the same standard as interior
art - including the negative-prompt checks, which are new since this pack
moved from FLUX.2 [klein] to Qwen-Image-2512. Without the auditor, a reduced
built-in check runs and says so.
"""

import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PACKS = os.path.join(HERE, "..", "..", "assets", "cover_style_packs.json")

# "full" = 50-step model, real CFG, negative prompt works. "lightning" = 4/8-
# step distilled LoRA overlay, CFG forced to 1.0, negative prompt inert. See
# the qwen-kids-art skill's qwen-prompt-standards.md #3 for why this matters.
RUNTIME = {
    "full": {"steps": 50, "cfg": 4.0, "sampler": "euler", "scheduler": "simple", "denoise": 1.0},
    "lightning": {"steps": 8, "cfg": 1.0, "sampler": "euler", "scheduler": "simple", "denoise": 1.0},
}

# Qwen-Image-2512's trained aspect ratios (native resolution). Cover art is
# generated at the closest of these and then cropped to the exact pixel
# rectangle from cover_spec.py - never upscaled to reach it at this stage.
# Native tops out around 1.3-1.8MP, well under a 300-DPI print front's 3-9MP,
# so the upscale step below is still required even though this is a much
# larger model than the old 4B one was.
GEN_SIZES = {
    "cover_front_3_4": (1104, 1472),   # 3:4, native - fits 8x10 / 8.5x11 crops
    "cover_front_2_3": (1056, 1584),   # 2:3, native - closer to the ebook ratio, 6x9-ish
    "cover_back": (1104, 1472),
    "cover_square": (1328, 1328),      # 1:1, native
    "spine": (256, 1600),              # custom - not a native ratio, and doesn't need to be
}


def load_packs(path=PACKS):
    return json.load(open(path, encoding="utf-8"))


def find_qwen_auditor(explicit=None):
    cands = [explicit, os.environ.get("QWEN_SKILL_PATH"),
             os.path.join(HERE, "..", "..", "skills", "qwen-kids-art"),
             os.path.expanduser("~/.claude/skills/qwen-kids-art")]
    for c in cands:
        if not c:
            continue
        p = os.path.join(c, "scripts")
        if os.path.isfile(os.path.join(p, "audit_prompt.py")):
            sys.path.insert(0, p)
            try:
                import audit_prompt  # noqa
                return audit_prompt
            except Exception:
                return None
    return None


FALLBACK_BANS = [
    (r"\bno \b|\bnot \b|\bwithout\b|\bavoid\b|\bnever\b",
     "negation in the positive prompt - Qwen-Image has a real negative-prompt "
     "channel, so this belongs in --negative-extra instead, not as \"no X\" here"),
    (r"\(\s*[^)]*:\s*[0-9.]+\s*\)|\bBREAK\b|<lora:",
     "Stable-Diffusion-era syntax - the Qwen2.5-VL text encoder reads this as literal text"),
    (r"\bmasterpiece\b|\bbest quality\b|\b8k\b|\bultra detailed\b", "dead quality tags"),
    (r"[\"\u201c\u201d]", "quoted text - covers get their type set later, never generated"),
    (r"\btitle\b|\blettering\b|\bthe word\b|\btext reading\b|\bwritten on\b", "asks the model for words"),
]


def fallback_audit(prompt, negative="", variant="full"):
    issues = []
    for pat, why in FALLBACK_BANS:
        if re.search(pat, prompt, flags=re.IGNORECASE):
            issues.append({"level": "blocker", "code": "fallback", "message": why, "fix": "Rewrite."})
    if variant == "lightning" and negative and negative.strip():
        issues.append({"level": "warning", "code": "fallback_inert_negative",
                       "message": "Negative prompt set but variant is lightning - it will be ignored.",
                       "fix": "Switch to --variant full, or clear the negative prompt."})
    wc = len(prompt.split())
    if wc < 40:
        issues.append({"level": "warning", "code": "too_short",
                       "message": "%d words - under-specified prompts swing seed to seed" % wc,
                       "fix": "Fill in setting, light, palette and composition."})
    score = max(0, 100 - 34 * sum(1 for i in issues if i["level"] == "blocker")
                - 10 * sum(1 for i in issues if i["level"] == "warning"))
    return {"score": score, "status": "FIX" if score < 70 else "PASS", "issues": issues,
            "stats": {"word_count": wc, "auditor": "fallback", "variant": variant,
                      "negative_prompt": negative}}


def stable_seed(text, i):
    return (int(hashlib.sha256(text.encode()).hexdigest()[:12], 16) + i * 9973) % (2 ** 31 - 1)


def join(parts):
    out = [p.strip().rstrip(".,") for p in parts if p and p.strip()]
    t = ", ".join(out)
    return (t[0].upper() + t[1:] + ".") if t else t


def build_negative(pack, item, face, variant):
    """Negative prompt only does anything on the full model - see
    qwen-prompt-standards.md #3. On lightning it's deliberately left blank."""
    if variant == "lightning":
        return ""
    base = pack.get("negative", "")
    extra = item.get("%s_negative_extra" % face) or item.get("negative_extra") or ""
    parts = [p.strip() for p in [base, extra] if p and p.strip()]
    return ", ".join(parts)


def build_face(face, item, pack, band, data, gen_key, candidates=4, type_zone=None,
               variant="full"):
    sig = pack["signature"]
    zone_key = type_zone or pack.get("type_zone", "top-third")
    zone = data["type_zones"].get(zone_key, "")

    palette = item.get("palette") or pack["palette"]
    palette_clause = "colour palette of %s" % " ".join(palette[:5]) if palette else ""

    if face == "front":
        subject = item["subject"]
        action = item.get("action", "facing the viewer")
        comp = item.get("composition", pack["composition"])
        detail = band["detail_phrase"]
        scene = item.get("setting", pack["background"])
        extra = ("%s, the hero subject reads clearly as a solid silhouette even when the "
                 "image is shrunk very small" % zone)
    elif face == "back":
        subject = item.get("back_subject") or ("a quiet wide view of %s" % item.get("setting", pack["background"]))
        action = "empty and calm"
        comp = ("an even low-contrast field with the lower right corner kept plain and light, "
                "shapes small and evenly spread")
        detail = "simplified and low contrast so overlaid text stays legible"
        scene = item.get("setting", pack["background"])
        extra = "the whole image stays soft and even in tone with a single quiet focal area"
    else:  # spine
        subject = "a simple repeating decorative motif"
        action = "arranged as a narrow vertical band"
        comp = "a tall narrow vertical strip, motif repeating evenly from top to bottom"
        detail = "very simple, readable at a glance on a thin spine"
        scene = "a plain flat background"
        extra = "the band stays visually calm along its whole length"

    prompt = join([subject, action, pack["light"] if face == "front" else "even flat lighting",
                   sig, detail, scene, palette_clause, comp, extra])
    negative = build_negative(pack, item, face, variant)

    w, h = GEN_SIZES[gen_key]
    params = dict(RUNTIME[variant])
    params.update({"width": w, "height": h, "variant": variant})
    seeds = [stable_seed(prompt, i) for i in range(candidates)]
    return {"face": face, "prompt": prompt, "negative": negative, "params": params, "seeds": seeds,
            "type_zone": zone_key if face == "front" else "none",
            "filename_stem": "cover_%s_%s" % (face, hashlib.sha256(prompt.encode()).hexdigest()[:6])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", help="cover_spec.py output, used to pick the generation aspect")
    ap.add_argument("--brief", help="JSON cover brief (series-aware)")
    ap.add_argument("--audience", choices=["early-reader-6-8", "middle-grade-9-12",
                                           "teen-13-17", "adult-general"])
    ap.add_argument("--book-type")
    ap.add_argument("--pack")
    ap.add_argument("--subject")
    ap.add_argument("--action")
    ap.add_argument("--setting")
    ap.add_argument("--type-zone", choices=["top-third", "top-half", "bottom-third",
                                            "center-band", "none"])
    ap.add_argument("--faces", default="front,back",
                    help="Comma list of front,back,spine (default front,back)")
    ap.add_argument("--variant", default="full", choices=["full", "lightning"],
                    help="full = 50-step, real negative prompt. lightning = fast draft, "
                         "negative prompt inert. Default full: cover art is usually a keeper, "
                         "not a draft.")
    ap.add_argument("--negative-extra", dest="negative_extra",
                    help="Extra negative-prompt terms appended to the pack's starter list "
                         "for every face. Ignored on --variant lightning.")
    ap.add_argument("--candidates", type=int, default=4)
    ap.add_argument("--packs", default=PACKS)
    ap.add_argument("--qwen-path", dest="qwen_path")
    ap.add_argument("--out")
    ap.add_argument("--print", dest="do_print", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    data = load_packs(a.packs)
    auditor = find_qwen_auditor(a.qwen_path)

    if a.brief:
        brief = json.load(open(a.brief, encoding="utf-8"))
        audience = a.audience or brief["audience"]
        item = brief
        faces = brief.get("faces", a.faces.split(","))
        pack_name = a.pack or brief.get("pack")
        variant = a.variant or brief.get("variant", "full")
    else:
        if not (a.audience and a.subject):
            ap.error("give --brief, or --audience and --subject")
        audience = a.audience
        item = {"subject": a.subject, "action": a.action, "setting": a.setting,
                "negative_extra": a.negative_extra}
        faces = a.faces.split(",")
        pack_name = a.pack
        variant = a.variant

    merged = None
    if auditor:
        try:
            merged = auditor.load_packs()
            merged["packs"].update(data["packs"])
            merged["age_bands"].update(data["audience_bands"])
        except Exception:
            merged = None

    band = data["audience_bands"][audience]
    pack_name = pack_name or band["default_pack"]
    pack = data["packs"][pack_name]
    if audience not in pack.get("audiences", [audience]):
        print("NOTE: pack %s is not a default for %s - intentional?" % (pack_name, audience))

    spec = json.load(open(a.spec, encoding="utf-8")) if a.spec else None
    gen_key = "cover_front_3_4"
    if spec:
        r = spec["zones"]["front"]["h_in"] / spec["zones"]["front"]["w_in"]
        gen_key = "cover_front_2_3" if r > 1.4 else "cover_front_3_4"

    built = []
    for face in [f.strip() for f in faces if f.strip()]:
        key = {"front": gen_key, "back": "cover_back", "spine": "spine"}[face]
        b = build_face(face, item, pack, band, data, key, a.candidates, a.type_zone, variant)
        b["audit"] = (auditor.audit(b["prompt"], pack_name, audience, merged,
                                    negative=b["negative"], variant=variant)
                      if (auditor and merged) else fallback_audit(b["prompt"], b["negative"], variant))
        # Pack-specific checks the generic auditor does not know about
        extra = []
        if re.search(r"[\"\u201c\u201d]", b["prompt"]) or re.search(
                r"\btitle\b|\bthe word\b|\blettering\b|\btext reading\b", b["prompt"], re.I):
            extra.append("Cover art prompts never request text; the title is set in "
                         "cover_compose.py from a real font.")
        if face == "front" and b["type_zone"] == "none":
            extra.append("No type zone reserved. The title will have to fight the art.")
        for e in extra:
            b["audit"]["issues"].append({"level": "blocker", "code": "cover_rule",
                                         "message": e, "fix": "Rebuild the prompt."})
            b["audit"]["score"] = max(0, b["audit"]["score"] - 34)
            b["audit"]["status"] = "FIX"
        built.append(b)

    up = None
    if spec:
        need_w, need_h = spec["art_targets"]["front_art_px"]
        gw, gh = GEN_SIZES[gen_key]
        factor = max(need_w / gw, need_h / gh)
        up = {"required_factor": round(factor, 2),
              "target_front_px": [need_w, need_h],
              "method": "ComfyUI upscale model (4x-UltraSharp or RealESRGAN x4) then resize "
                        "down to the target, or a second full-model pass at a larger canvas "
                        "with the kept image as input and denoise ~0.4-0.5 (hi-res fix style)",
              "note": "Composer-side Lanczos upscaling is a fallback, not a plan."}

    plan = {"schema": "cover-art-plan/1", "audience": audience, "pack": pack_name,
            "variant": variant, "upscale": up,
            "book_type": a.book_type, "auditor": "qwen-kids-art" if auditor else "fallback",
            "spec_ref": a.spec, "faces": built}

    if a.out:
        json.dump(plan, open(a.out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    if a.do_print or not a.out:
        for b in built:
            print("\n--- %s  [%s %d/100]  %s"
                  % (b["face"].upper(), b["audit"]["status"], b["audit"]["score"],
                     json.dumps(b["params"])))
            for i in b["audit"]["issues"]:
                print("    [%s] %s" % (i["level"], i["message"]))
            print(b["prompt"])
            if b["negative"]:
                print("negative: %s" % b["negative"])
            print("seeds: %s" % b["seeds"])
    if not auditor:
        print("\nNOTE: qwen-kids-art auditor not found; used the reduced built-in check. "
              "Set QWEN_SKILL_PATH for the full lint (including the negative-prompt checks).")
    if a.out:
        print("\nWrote %s" % a.out)

    bad = [b for b in built if not b["audit"]["status"].startswith("PASS")]
    return 1 if (bad and not a.force) else 0


if __name__ == "__main__":
    sys.exit(main())
