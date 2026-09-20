#!/usr/bin/env python3
"""
cover_preflight.py - last gate before a cover file goes into a channel package.

Checks the finished files against the spec that produced them and against the
channel rules. It is deliberately boring: dimensions, resolution, colour mode,
file size, barcode-zone clearance. These are the things that get a book bounced
back a week after upload, and every one of them is machine-checkable.

  python cover_preflight.py --spec spec.json --wrap cover-out/wrap.pdf \
      --ebook cover-out/ebook.jpg --channel kdp-print --json

Exit codes: 0 all clear, 1 findings. Run it again after any edit, including
edits made by a human designer - hand-tweaked files are where the surprises are.
"""

import argparse
import json
import os
import sys

try:
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
except ImportError:
    Image = None

HERE = os.path.dirname(os.path.abspath(__file__))
SPECS = os.path.join(HERE, "..", "..", "assets", "cover_channel_specs.json")
TOL_IN = 0.02  # inches of slack on wrap dimensions


def mb(path):
    return os.path.getsize(path) / (1024.0 * 1024.0)


def check_wrap(path, spec, data, findings):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    pf = data["print_file"]
    if ext not in pf["formats"]:
        findings.append(("blocker", "Wrap format .%s is not accepted (%s)."
                         % (ext, ", ".join(pf["formats"]))))
    if mb(path) > pf["max_file_mb"]:
        findings.append(("blocker", "Wrap file is %.1f MB, above the %d MB limit."
                         % (mb(path), pf["max_file_mb"])))

    want_w, want_h = spec["wrap"]["total_w_in"], spec["wrap"]["total_h_in"]
    dpi = spec["input"]["dpi"]

    if ext == "pdf":
        try:
            from pypdf import PdfReader
            page = PdfReader(path).pages[0]
            w_in = float(page.mediabox.width) / 72.0
            h_in = float(page.mediabox.height) / 72.0
        except Exception as exc:
            findings.append(("warning", "Could not measure the PDF (%s). Check it by hand." % exc))
            return
        if abs(w_in - want_w) > TOL_IN or abs(h_in - want_h) > TOL_IN:
            findings.append(("blocker", "Wrap PDF is %.4f x %.4f in; the spec says %.4f x %.4f in."
                             % (w_in, h_in, want_w, want_h)))
        findings.append(("note", "PDF measured %.4f x %.4f in. Confirm fonts are embedded or "
                                 "outlined, and that the export preserved 300 DPI images."
                         % (w_in, h_in)))
        return

    if Image is None:
        findings.append(("warning", "Pillow missing; raster wrap not measured."))
        return
    im = Image.open(path)
    got_dpi = im.info.get("dpi", (0, 0))[0] or 0
    eff_dpi = im.width / want_w
    if eff_dpi < pf["dpi"] - 1:
        findings.append(("blocker", "Effective resolution is %.0f DPI at final size; %d DPI is "
                         "the minimum." % (eff_dpi, pf["dpi"])))
    if abs(im.width - spec["wrap"]["total_w_px"]) > 6 or \
       abs(im.height - spec["wrap"]["total_h_px"]) > 6:
        findings.append(("blocker", "Wrap is %dx%d px; the spec says %dx%d px."
                         % (im.width, im.height, spec["wrap"]["total_w_px"],
                            spec["wrap"]["total_h_px"])))
    if im.mode not in ("RGB", "CMYK"):
        findings.append(("blocker", "Colour mode is %s; use RGB or CMYK." % im.mode))
    if got_dpi and got_dpi < pf["dpi"]:
        findings.append(("warning", "Embedded DPI tag says %d. Harmless if pixel dimensions are "
                         "right, but some tools read it." % got_dpi))

    bc = spec["zones"]["barcode"]
    region = im.convert("RGB").crop((bc["x_px"], bc["y_px"],
                                     bc["x_px"] + bc["w_px"], bc["y_px"] + bc["h_px"]))
    r, g, b = region.resize((1, 1), Image.BILINEAR).getpixel((0, 0))
    luma = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
    lo, hi = region.convert("L").getextrema()
    if luma < 0.85:
        findings.append(("blocker", "Barcode zone is too dark (mean luminance %.2f). It must be a "
                         "solid light fill." % luma))
    elif hi - lo > 40:
        findings.append(("warning", "Barcode zone is not a flat fill (range %d). Artwork or text "
                         "there will sit under the printed barcode." % (hi - lo)))


def check_ebook(path, data, channel, findings):
    if Image is None:
        findings.append(("warning", "Pillow missing; ebook cover not measured."))
        return
    ch = data["channels"][channel]
    im = Image.open(path)
    w, h = im.size
    if "pixels" in ch:
        tw, th = ch["pixels"]
        if (w, h) != (tw, th):
            level = "warning" if min(w, h) >= ch.get("min_long_edge_px", 1000) else "blocker"
            findings.append((level, "Ebook cover is %dx%d px; %s recommends %dx%d."
                             % (w, h, ch["label"], tw, th)))
    if "ratio" in ch and isinstance(ch["ratio"], (int, float)):
        got = h / float(w)
        if abs(got - ch["ratio"]) > 0.02:
            findings.append(("warning", "Aspect ratio is %.3f; %s expects %.2f. Retailers letterbox "
                             "or crop mismatches." % (got, ch["label"], ch["ratio"])))
    if "min_short_edge_px" in ch and min(w, h) < ch["min_short_edge_px"]:
        findings.append(("blocker", "Short edge is %d px; %s requires at least %d."
                         % (min(w, h), ch["label"], ch["min_short_edge_px"])))
    if im.mode != "RGB":
        findings.append(("blocker", "Ebook cover mode is %s; must be RGB." % im.mode))
    if "max_file_mb" in ch and mb(path) > ch["max_file_mb"]:
        findings.append(("blocker", "Ebook cover is %.1f MB, above the %d MB limit."
                         % (mb(path), ch["max_file_mb"])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec")
    ap.add_argument("--wrap")
    ap.add_argument("--ebook")
    ap.add_argument("--channel", default="kdp-ebook")
    ap.add_argument("--specs", default=SPECS)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    data = json.load(open(a.specs, encoding="utf-8"))
    findings = []

    if a.wrap:
        if not a.spec:
            ap.error("--wrap needs --spec")
        spec = json.load(open(a.spec, encoding="utf-8"))
        check_wrap(a.wrap, spec, data, findings)
        for w in spec.get("warnings", []):
            findings.append(("note", "From the spec: %s" % w))
        findings.append(("note", spec["verify"]))
    if a.ebook:
        ch = a.channel if a.channel in data["channels"] else "kdp-ebook"
        check_ebook(a.ebook, data, ch, findings)

    blockers = [f for f in findings if f[0] == "blocker"]
    out = {"findings": [{"level": l, "message": m} for l, m in findings],
           "blockers": len(blockers),
           "status": "FAIL" if blockers else "PASS"}
    if a.json:
        print(json.dumps(out, indent=2))
    else:
        print("PREFLIGHT %s (%d blockers)" % (out["status"], len(blockers)))
        for l, m in findings:
            print("  [%s] %s" % (l, m))
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
