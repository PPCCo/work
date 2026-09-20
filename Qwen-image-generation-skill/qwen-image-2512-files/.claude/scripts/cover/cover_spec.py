#!/usr/bin/env python3
"""
cover_spec.py - deterministic cover geometry for print wraps and ebook covers.

Every downstream step (art prompts, typography, preflight) reads this file's
output, so the arithmetic happens exactly once and nothing is retyped by hand.
Most cover rejections are a mistyped spine width.

  python cover_spec.py --trim 8.5x11 --pages 108 --paper white \
      --binding paperback --audience early-reader-6-8 --out spec.json --guides guides.svg

Output: JSON with every rectangle in inches and in 300-DPI pixels - full wrap,
back, spine, front, bleed, safe areas, barcode zone, hinges (hardcover), plus
the ebook cover size and a list of warnings.

The generated SVG is a guide sheet: trim, bleed, safe and barcode rectangles,
for dropping under artwork in any editor.

This is a planning calculation. Before exporting a final print file, generate
Amazon's own template for the same trim/pages/paper and confirm the full-wrap
width matches. If it does not, the page count or paper type changed.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPECS = os.path.join(HERE, "..", "..", "assets", "cover_channel_specs.json")
DPI = 300


def px(inches, dpi=DPI):
    return int(round(inches * dpi))


def rect(x, y, w, h, dpi=DPI):
    return {
        "x_in": round(x, 4), "y_in": round(y, 4),
        "w_in": round(w, 4), "h_in": round(h, 4),
        "x_px": px(x, dpi), "y_px": px(y, dpi),
        "w_px": px(w, dpi), "h_px": px(h, dpi),
    }


def build(trim, pages, paper="white", binding="paperback", dpi=DPI,
          cover_thickness=None, data=None, audience=None, book_type=None,
          title=None, channel_set=None):
    data = data or json.load(open(SPECS, encoding="utf-8"))
    warn = []

    if trim in data["trim_sizes"]:
        tw, th = data["trim_sizes"][trim]
    else:
        try:
            tw, th = [float(v) for v in trim.lower().split("x")]
            warn.append("Trim %s is not in the standard list; confirm the channel offers it." % trim)
        except ValueError:
            raise SystemExit("Could not parse trim '%s'. Use 6x9 or 8.5x11." % trim)

    b = data["binding"][binding]
    bleed = b["bleed"]
    safe = b["safe_margin"]
    thick = data["paper_thickness_per_page"].get(paper)
    if thick is None:
        raise SystemExit("Unknown paper '%s'. Options: %s"
                         % (paper, ", ".join(data["paper_thickness_per_page"])))

    allowance = b["cover_thickness_allowance"] if cover_thickness is None else cover_thickness
    spine = pages * thick + allowance

    if pages < b["min_pages"]:
        warn.append("%d pages is below the %d-page minimum for %s."
                    % (pages, b["min_pages"], binding))
    spine_text_ok = pages >= b["min_pages_for_spine_text"]
    if not spine_text_ok:
        warn.append("Spine is too narrow for text at %d pages (needs %d+). Carry the "
                    "background colour or artwork across the spine instead."
                    % (pages, b["min_pages_for_spine_text"]))

    if binding == "hardcover":
        wrap, hinge = b["wrap"], b["hinge"]
        total_w = 2 * wrap + 2 * bleed + 2 * tw + 2 * hinge + spine
        total_h = 2 * wrap + 2 * bleed + th
        back_x = wrap + bleed
        spine_x = back_x + tw + hinge
        front_x = spine_x + spine + hinge
        content_y = wrap + bleed
        warn.append("Hardcover: keep important elements %.3f in clear of the spine on both "
                    "sides - the hinge crease distorts artwork there." % b["spine_clearance"])
    else:
        wrap, hinge = 0.0, 0.0
        total_w = 2 * bleed + 2 * tw + spine
        total_h = 2 * bleed + th
        back_x = bleed
        spine_x = back_x + tw
        front_x = spine_x + spine
        content_y = bleed

    bz = data["barcode_zone"]
    barcode = rect(back_x + bz["margin_from_trim"],
                   content_y + th - bz["margin_from_trim"] - bz["height"],
                   bz["width"], bz["height"], dpi)
    # Barcode sits bottom-right of the back cover; the back cover is on the LEFT
    # of the wrap, so "right" means towards the spine.
    barcode = rect(spine_x - bz["margin_from_trim"] - bz["width"],
                   content_y + th - bz["margin_from_trim"] - bz["height"],
                   bz["width"], bz["height"], dpi)

    front = rect(front_x, content_y, tw, th, dpi)
    back = rect(back_x, content_y, tw, th, dpi)
    spine_r = rect(spine_x, content_y, spine, th, dpi)

    def safe_of(r, extra_left=0.0, extra_right=0.0):
        return rect(r["x_in"] + safe + extra_left, r["y_in"] + safe,
                    r["w_in"] - 2 * safe - extra_left - extra_right,
                    r["h_in"] - 2 * safe, dpi)

    hinge_clear = b.get("spine_clearance", 0.0) if binding == "hardcover" else 0.0

    eb = data["channels"]["kdp-ebook"]
    spec = {
        "schema": "cover-spec/1",
        "title": title,
        "audience": audience,
        "book_type": book_type,
        "input": {"trim": trim, "trim_w_in": tw, "trim_h_in": th, "pages": pages,
                  "paper": paper, "binding": binding, "dpi": dpi,
                  "paper_thickness_per_page": thick,
                  "cover_thickness_allowance": allowance},
        "spine": {"width_in": round(spine, 4), "width_px": px(spine, dpi),
                  "text_allowed": spine_text_ok,
                  "text_clearance_in": b.get("spine_text_clearance", 0.0625)},
        "wrap": {"total_w_in": round(total_w, 4), "total_h_in": round(total_h, 4),
                 "total_w_px": px(total_w, dpi), "total_h_px": px(total_h, dpi),
                 "bleed_in": bleed, "safe_margin_in": safe,
                 "hardcover_wrap_in": wrap, "hardcover_hinge_in": hinge},
        "zones": {
            "front": front, "back": back, "spine": spine_r,
            "front_safe": safe_of(front, extra_left=hinge_clear),
            "back_safe": safe_of(back, extra_right=hinge_clear),
            "barcode": barcode,
        },
        "ebook": {"w_px": eb["pixels"][0], "h_px": eb["pixels"][1],
                  "ratio": eb["ratio"], "color": eb["color"]},
        "art_targets": {
            "front_art_px": [front["w_px"] + px(bleed, dpi), front["h_px"] + px(2 * bleed, dpi)],
            "back_art_px": [back["w_px"] + px(bleed, dpi), back["h_px"] + px(2 * bleed, dpi)],
            "note": "Generate art larger than these numbers and crop in, never upscale to reach them.",
        },
        "warnings": warn,
        "verify": "Generate the channel's own cover template for this trim/page count/paper "
                  "and confirm the full-wrap width matches %.4f in before exporting." % total_w,
    }
    return spec


def guides_svg(spec):
    w, h = spec["wrap"]["total_w_in"], spec["wrap"]["total_h_in"]
    z = spec["zones"]

    def r(rc, colour, dash="", label=""):
        return ('<rect x="%.4f" y="%.4f" width="%.4f" height="%.4f" fill="none" '
                'stroke="%s" stroke-width="0.01" %s/>\n<text x="%.4f" y="%.4f" '
                'font-size="0.12" fill="%s">%s</text>'
                % (rc["x_in"], rc["y_in"], rc["w_in"], rc["h_in"], colour,
                   'stroke-dasharray="0.06 0.04"' if dash else "",
                   rc["x_in"] + 0.06, rc["y_in"] + 0.18, colour, label))

    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.4fin" height="%.4fin" '
             'viewBox="0 0 %.4f %.4f">' % (w, h, w, h),
             '<rect width="%.4f" height="%.4f" fill="#ffffff"/>' % (w, h),
             r(z["back"], "#d33", "", "BACK (trim)"),
             r(z["spine"], "#39c", "", "SPINE"),
             r(z["front"], "#d33", "", "FRONT (trim)"),
             r(z["front_safe"], "#3a3", "dash", "front safe"),
             r(z["back_safe"], "#3a3", "dash", "back safe"),
             r(z["barcode"], "#f80", "", "BARCODE - keep light and empty"),
             '</svg>']
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trim", required=True)
    ap.add_argument("--pages", type=int, required=True)
    ap.add_argument("--paper", default="white")
    ap.add_argument("--binding", default="paperback", choices=["paperback", "hardcover"])
    ap.add_argument("--dpi", type=int, default=DPI)
    ap.add_argument("--cover-thickness", type=float, default=None,
                    help="Override the cover-stock allowance added to the spine.")
    ap.add_argument("--audience")
    ap.add_argument("--book-type")
    ap.add_argument("--title")
    ap.add_argument("--specs", default=SPECS)
    ap.add_argument("--out")
    ap.add_argument("--guides")
    a = ap.parse_args()

    data = json.load(open(a.specs, encoding="utf-8"))
    spec = build(a.trim, a.pages, a.paper, a.binding, a.dpi, a.cover_thickness,
                 data, a.audience, a.book_type, a.title)

    if a.out:
        json.dump(spec, open(a.out, "w", encoding="utf-8"), indent=2)
    if a.guides:
        open(a.guides, "w", encoding="utf-8").write(guides_svg(spec))

    print("Wrap      : %.4f x %.4f in  (%d x %d px @ %d dpi)"
          % (spec["wrap"]["total_w_in"], spec["wrap"]["total_h_in"],
             spec["wrap"]["total_w_px"], spec["wrap"]["total_h_px"], a.dpi))
    print("Spine     : %.4f in (%d px) - text %s"
          % (spec["spine"]["width_in"], spec["spine"]["width_px"],
             "allowed" if spec["spine"]["text_allowed"] else "NOT allowed"))
    print("Front trim: %d x %d px    Ebook: %d x %d px"
          % (spec["zones"]["front"]["w_px"], spec["zones"]["front"]["h_px"],
             spec["ebook"]["w_px"], spec["ebook"]["h_px"]))
    for w in spec["warnings"]:
        print("WARN: %s" % w)
    print(spec["verify"])
    if a.out:
        print("Wrote %s" % a.out)
    if a.guides:
        print("Wrote %s" % a.guides)
    return 0


if __name__ == "__main__":
    sys.exit(main())
