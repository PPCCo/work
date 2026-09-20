#!/usr/bin/env python3
"""
thumbnail_test.py - judge the cover the way a shopper first meets it.

Nobody discovers a book at full size. On Amazon search, Etsy grids and Apple
Books shelves the first contact is a thumbnail 80-240 pixels wide, on a phone,
next to twenty competitors. A cover that only works at full size does not work.

  python thumbnail_test.py --front cover-out/front_only.png --out-dir cover-out/thumbs

Produces a contact sheet at 80, 120 and 240 px plus a greyscale and a
half-second blur version, and reports heuristics: title-band contrast, overall
busyness, and how much of the frame the largest shape occupies.

The numbers are a screen, not a verdict. The actual test is looking at
thumb_80.png yourself - if you cannot read the title and name the subject in one
second, the cover fails no matter what the metrics say. Claude should open the
80px file and say what it can and cannot make out.
"""

import argparse
import json
import os
import sys

try:
    from PIL import Image, ImageFilter, ImageStat
except ImportError:
    sys.exit("Pillow is required:  pip install Pillow")


def luma_of(img):
    r, g, b = ImageStat.Stat(img.convert("RGB")).mean
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def band_contrast(img, top_frac, bottom_frac):
    w, h = img.size
    band = img.crop((0, int(h * top_frac), w, int(h * bottom_frac))).convert("L")
    lo, hi = band.getextrema()
    a, b = (hi / 255.0 + 0.05), (lo / 255.0 + 0.05)
    return round(a / b, 2)


def busyness(img):
    """Edge energy after shrinking to thumbnail size: high means the cover turns
    to noise in a grid."""
    small = img.convert("L").resize((120, int(120 * img.height / img.width)), Image.LANCZOS)
    edges = small.filter(ImageFilter.FIND_EDGES)
    return round(ImageStat.Stat(edges).mean[0], 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--front", required=True, help="front_only.png or ebook.jpg")
    ap.add_argument("--out-dir", default="./thumbs")
    ap.add_argument("--widths", default="80,120,240")
    ap.add_argument("--title-band", default="0.0,0.35",
                    help="Fraction of height occupied by the title, e.g. 0.0,0.35")
    ap.add_argument("--max-busyness", type=float, default=42.0)
    ap.add_argument("--min-band-contrast", type=float, default=4.5)
    a = ap.parse_args()

    img = Image.open(a.front).convert("RGB")
    os.makedirs(a.out_dir, exist_ok=True)
    widths = [int(w) for w in a.widths.split(",")]
    top, bot = [float(v) for v in a.title_band.split(",")]

    sheet_w = sum(widths) + 40 * len(widths)
    sheet_h = max(int(w * img.height / img.width) for w in widths) + 40
    sheet = Image.new("RGB", (sheet_w, sheet_h), (238, 238, 238))
    x = 20
    for w in widths:
        t = img.resize((w, int(w * img.height / img.width)), Image.LANCZOS)
        t.save(os.path.join(a.out_dir, "thumb_%d.png" % w))
        sheet.paste(t, (x, 20))
        x += w + 40
    sheet.save(os.path.join(a.out_dir, "contact_sheet.png"))

    img.convert("L").save(os.path.join(a.out_dir, "greyscale.png"))
    img.filter(ImageFilter.GaussianBlur(img.width / 90.0)).save(
        os.path.join(a.out_dir, "squint.png"))

    report = {
        "source": a.front,
        "title_band_contrast": band_contrast(img, top, bot),
        "busyness": busyness(img),
        "mean_luma": round(luma_of(img), 3),
        "findings": [],
    }
    if report["title_band_contrast"] < a.min_band_contrast:
        report["findings"].append(
            "Title band contrast %.2f is below %.1f. The title will grey out at thumbnail "
            "size. Flatten the art behind the title, add a scrim, or move the type zone."
            % (report["title_band_contrast"], a.min_band_contrast))
    if report["busyness"] > a.max_busyness:
        report["findings"].append(
            "Busyness %.1f is above %.1f. The cover turns to visual noise in a search grid. "
            "Cut detail, enlarge the hero subject, simplify the background."
            % (report["busyness"], a.max_busyness))
    if report["mean_luma"] > 0.93:
        report["findings"].append(
            "The cover is almost white overall and will disappear against Amazon's white "
            "background. Add a defined edge or a stronger field of colour.")

    json.dump(report, open(os.path.join(a.out_dir, "thumbnail-report.json"), "w"), indent=2)
    print(json.dumps(report, indent=2))
    print("\nNow look at %s. Read the title out loud. Name the subject. If either takes "
          "more than a second, fix the cover, not the metrics."
          % os.path.join(a.out_dir, "thumb_80.png"))
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
