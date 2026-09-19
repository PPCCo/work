#!/usr/bin/env python3
"""
cover_compose.py - set the type and assemble the cover.

Klein makes the artwork; this makes the book. Every word on the cover is drawn
here from a real font file at 300 DPI, so titles are exact, kerning is sane,
text lands inside the safe area, and the barcode corner stays clear. Nothing
about the wording is left to a diffusion model.

  python cover_compose.py --spec spec.json --copy copy.json \
      --front-art front.png --back-art back.png \
      --title-font Poppins-Bold --body-font Poppins-Regular \
      --out-dir ./cover-out

Produces, in --out-dir:
  wrap.png / wrap.pdf   full print wrap at 300 DPI (back | spine | front)
  ebook.jpg             front-only ebook cover, 1600x2560, composed separately
  front_only.png        front face at print resolution, for mockups
  wrap.svg              editable master referencing the art files
  layout-report.json    measured positions, contrast readings, violations

Exits non-zero if any text falls outside the safe area or the barcode zone is
not clear - those are the two failures that get a cover rejected.

Dependencies: Pillow. Fonts: pass a path, or a family name that fontconfig or
one of the usual font directories can resolve.
"""

import argparse
import glob
import json
import os
import subprocess
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required:  pip install Pillow")

FONT_DIRS = ["/usr/share/fonts", "/usr/local/share/fonts",
             os.path.expanduser("~/.fonts"), os.path.expanduser("~/Library/Fonts"),
             "C:/Windows/Fonts", "/Library/Fonts"]


# ---------------------------------------------------------------- fonts

def _looks_like(requested, path):
    a = "".join(c for c in requested.lower() if c.isalnum())
    b = "".join(c for c in os.path.basename(path).lower() if c.isalnum())
    return a[:6] in b if a else False


def resolve_font(name):
    """fc-match always returns something, so verify the match actually is the
    family that was asked for. Silently substituting a font changes the cover and
    invalidates the licence record."""
    if name and os.path.isfile(name):
        return name
    try:
        out = subprocess.run(["fc-match", "-f", "%{file}", name], capture_output=True,
                             text=True, timeout=10)
        if out.returncode == 0 and os.path.isfile(out.stdout.strip()):
            hit = out.stdout.strip()
            if not _looks_like(name, hit):
                print("WARN: '%s' is not installed. fontconfig substituted %s. Install the "
                      "family or pass a full path - the cover you are building is not the "
                      "cover you specified, and the licence record will be wrong."
                      % (name, os.path.basename(hit)))
            return hit
    except Exception:
        pass
    for d in FONT_DIRS:
        for ext in ("ttf", "otf"):
            hits = glob.glob(os.path.join(d, "**", "%s.%s" % (name, ext)), recursive=True)
            if hits:
                return hits[0]
    raise SystemExit("Could not find font '%s'. Pass a full path to a .ttf/.otf, or "
                     "install the family. Cover type must come from a real font file."
                     % name)


def font_at(path, size):
    return ImageFont.truetype(path, size)


def text_size(draw, text, font):
    """Width and height measured from the drawing origin, so stacked lines never
    collide. Pillow's bbox top offset is part of the advance, not slack."""
    box = draw.textbbox((0, 0), text, font=font)
    return box[2], box[3]


def wrap_lines(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_size(draw, trial, font)[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_block(draw, text, font_path, box_w, box_h, max_size, min_size=12,
              leading=1.12, max_lines=4):
    """Largest size at which the wrapped text fits the box."""
    best = None
    lo, hi = min_size, max_size
    while lo <= hi:
        mid = (lo + hi) // 2
        f = font_at(font_path, mid)
        lines = wrap_lines(draw, text, f, box_w)
        h = int(sum(text_size(draw, l, f)[1] for l in lines) + (len(lines) - 1) * mid * (leading - 1))
        widest = max(text_size(draw, l, f)[0] for l in lines) if lines else 0
        if len(lines) <= max_lines and h <= box_h and widest <= box_w:
            best = (mid, lines, h)
            lo = mid + 1
        else:
            hi = mid - 1
    if best is None:
        f = font_at(font_path, min_size)
        lines = wrap_lines(draw, text, f, box_w)
        h = int(sum(text_size(draw, l, f)[1] for l in lines))
        best = (min_size, lines, h)
    return best


def draw_block(draw, lines, font_path, size, box, align="center", fill="#fff",
               leading=1.12, valign="top", stroke=0, stroke_fill="#000"):
    x, y, w, h = box
    f = font_at(font_path, size)
    heights = [text_size(draw, l, f)[1] for l in lines]
    total = sum(heights) + (len(lines) - 1) * size * (leading - 1)
    cy = y if valign == "top" else (y + (h - total) / 2 if valign == "middle" else y + h - total)
    placed = []
    for i, line in enumerate(lines):
        lw, lh = text_size(draw, line, f)
        lx = x if align == "left" else (x + (w - lw) / 2 if align == "center" else x + w - lw)
        draw.text((lx, cy), line, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        placed.append((lx, cy, lw, lh))
        cy += lh + size * (leading - 1)
    return placed


# ---------------------------------------------------------------- imaging

def cover_fill(img, w, h):
    """Scale to cover the box and centre-crop. Never upscales beyond 1.0 silently."""
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    if scale > 1.02:
        print("WARN: art %dx%d is smaller than the %dx%d slot; it is being upscaled "
              "%.2fx and will soften. Regenerate larger." % (iw, ih, w, h, scale))
    nw, nh = max(1, int(iw * scale + 0.5)), max(1, int(ih * scale + 0.5))
    img = img.resize((nw, nh), Image.LANCZOS)
    return img.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))


def mean_luma(img, box):
    x, y, w, h = [int(v) for v in box]
    x, y = max(0, x), max(0, y)
    region = img.convert("RGB").crop((x, y, min(img.width, x + w), min(img.height, y + h)))
    if region.width < 1 or region.height < 1:
        return 1.0
    r, g, b = region.resize((1, 1), Image.BILINEAR).getpixel((0, 0))
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def contrast_ratio(l1, l2):
    a, b = max(l1, l2), min(l1, l2)
    return (a + 0.05) / (b + 0.05)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------- layout

def zone_box(front, safe, zone):
    """Text box in wrap pixel coords for a named type zone."""
    fx, fy, fw, fh = front["x_px"], front["y_px"], front["w_px"], front["h_px"]
    sx, sy, sw, sh = safe["x_px"], safe["y_px"], safe["w_px"], safe["h_px"]
    bands = {
        "top-third": (fy, fh / 3.0),
        "top-half": (fy, fh / 2.0),
        "bottom-third": (fy + 2 * fh / 3.0, fh / 3.0),
        "center-band": (fy + fh / 3.0, fh / 3.0),
    }
    top, height = bands.get(zone, bands["top-third"])
    y0 = max(sy, top)
    y1 = min(sy + sh, top + height)
    return [sx, y0, sw, max(10, y1 - y0)]


def compose(args):
    spec = json.load(open(args.spec, encoding="utf-8"))
    copy = json.load(open(args.copy, encoding="utf-8"))
    z = spec["zones"]
    W, H = spec["wrap"]["total_w_px"], spec["wrap"]["total_h_px"]
    dpi = spec["input"]["dpi"]
    report = {"violations": [], "measurements": {}, "notes": []}

    title_font = resolve_font(args.title_font)
    body_font = resolve_font(args.body_font or args.title_font)

    bg = hex_rgb(copy.get("background_color", "#ffffff"))
    wrap = Image.new("RGB", (W, H), bg)

    # --- artwork -----------------------------------------------------
    spine_x, front_x = z["spine"]["x_px"], z["front"]["x_px"]
    if args.back_art:
        back_w = spine_x
        wrap.paste(cover_fill(Image.open(args.back_art).convert("RGB"), back_w, H), (0, 0))
    if args.spine_art:
        wrap.paste(cover_fill(Image.open(args.spine_art).convert("RGB"),
                              front_x - spine_x, H), (spine_x, 0))
    elif copy.get("spine_color"):
        ImageDraw.Draw(wrap).rectangle([spine_x, 0, front_x, H], fill=hex_rgb(copy["spine_color"]))
    if args.front_art:
        wrap.paste(cover_fill(Image.open(args.front_art).convert("RGB"), W - front_x, H), (front_x, 0))

    draw = ImageDraw.Draw(wrap, "RGBA")

    # --- front typography --------------------------------------------
    tbox = zone_box(z["front"], z["front_safe"], args.type_zone)
    pad = int(0.06 * dpi)
    tx, ty, tw, th = tbox[0] + pad, tbox[1] + pad, tbox[2] - 2 * pad, tbox[3] - 2 * pad

    luma = mean_luma(wrap, (tx, ty, tw, th))
    ink = copy.get("title_color") or ("#111111" if luma > 0.55 else "#FFFFFF")
    ratio = contrast_ratio(luma, mean_luma(Image.new("RGB", (4, 4), hex_rgb(ink)), (0, 0, 4, 4)))
    scrim = None
    if ratio < args.min_contrast:
        scrim = copy.get("scrim_color", "#000000" if luma > 0.5 else "#FFFFFF")
        ink = "#FFFFFF" if scrim == "#000000" else "#111111"
        report["notes"].append(
            "Type-zone contrast was %.1f:1, below the %.1f:1 floor, so a scrim was placed "
            "behind the title. If you would rather not have one, regenerate the art with a "
            "calmer type zone." % (ratio, args.min_contrast))

    series = copy.get("series")
    subtitle = copy.get("subtitle")
    author = copy.get("author", "")

    # budget the zone: series 10%, title 58%, subtitle 20%, author 12%
    y = ty
    title_h = int(th * (0.62 if (subtitle or series) else 0.85))
    t_size, t_lines, t_used = fit_block(draw, copy["title"], title_font, tw, title_h,
                                        max_size=int(th * 0.95), max_lines=args.max_title_lines)

    if scrim:
        s_alpha = int(255 * args.scrim_opacity)
        draw.rectangle([tbox[0], tbox[1], tbox[0] + tbox[2], tbox[1] + tbox[3]],
                       fill=hex_rgb(scrim) + (s_alpha,))

    if series:
        s_size, s_lines, s_used = fit_block(draw, series.upper(), body_font, tw,
                                            int(th * 0.10), max_size=int(th * 0.10), max_lines=1)
        draw_block(draw, s_lines, body_font, s_size, (tx, y, tw, s_used), args.align, ink)
        y += s_used + int(0.05 * dpi)

    placed = draw_block(draw, t_lines, title_font, t_size, (tx, y, tw, t_used), args.align, ink)
    y += t_used + int(0.06 * dpi)
    report["measurements"]["title_pt"] = round(t_size * 72.0 / dpi, 1)
    report["measurements"]["title_height_pct_of_cover"] = round(100.0 * t_used / z["front"]["h_px"], 1)

    if subtitle:
        sub_h = int(th * 0.20)
        sb_size, sb_lines, sb_used = fit_block(draw, subtitle, body_font, tw, sub_h,
                                               max_size=max(14, int(t_size * 0.45)), max_lines=2)
        draw_block(draw, sb_lines, body_font, sb_size, (tx, y, tw, sb_used), args.align, ink)
        y += sb_used + int(0.06 * dpi)
        placed += [(tx, y - sb_used, tw, sb_used)]

    if author and not args.author_bottom:
        a_size, a_lines, a_used = fit_block(draw, author, body_font, tw, int(th * 0.12),
                                            max_size=max(14, int(t_size * 0.38)), max_lines=1)
        draw_block(draw, a_lines, body_font, a_size, (tx, y, tw, a_used), args.align, ink)
        placed += [(tx, y, tw, a_used)]
    elif author:
        fs = z["front_safe"]
        a_size, a_lines, a_used = fit_block(draw, author, body_font, fs["w_px"], int(0.5 * dpi),
                                            max_size=max(14, int(t_size * 0.40)), max_lines=1)
        ay = fs["y_px"] + fs["h_px"] - a_used
        a_luma = mean_luma(wrap, (fs["x_px"], ay, fs["w_px"], a_used))
        draw_block(draw, a_lines, body_font, a_size, (fs["x_px"], ay, fs["w_px"], a_used),
                   args.align, "#111111" if a_luma > 0.55 else "#FFFFFF")
        placed += [(fs["x_px"], ay, fs["w_px"], a_used)]

    # --- back cover ---------------------------------------------------
    bs = z["back_safe"]
    bx, by, bw = bs["x_px"], bs["y_px"], bs["w_px"]
    back_luma = mean_luma(wrap, (bx, by, bw, bs["h_px"]))
    back_ink = copy.get("back_text_color") or ("#111111" if back_luma > 0.55 else "#FFFFFF")
    y = by + int(0.15 * dpi)

    if copy.get("back_headline"):
        h_size, h_lines, h_used = fit_block(draw, copy["back_headline"], title_font, bw,
                                            int(1.1 * dpi), max_size=int(0.34 * dpi), max_lines=3)
        draw_block(draw, h_lines, title_font, h_size, (bx, y, bw, h_used), "center", back_ink)
        y += h_used + int(0.22 * dpi)

    body_pt = int(args.back_body_pt * dpi / 72.0)
    for para in copy.get("blurb", []):
        f = font_at(body_font, body_pt)
        lines = wrap_lines(draw, para, f, bw)
        used = int(len(lines) * body_pt * 1.35)
        draw_block(draw, lines, body_font, body_pt, (bx, y, bw, used), "left", back_ink, leading=1.35)
        y += used + int(0.14 * dpi)

    for b in copy.get("bullets", []):
        f = font_at(body_font, body_pt)
        lines = wrap_lines(draw, "\u2022  " + b, f, bw)
        used = int(len(lines) * body_pt * 1.35)
        draw_block(draw, lines, body_font, body_pt, (bx, y, bw, used), "left", back_ink, leading=1.35)
        y += used + int(0.06 * dpi)

    bc = z["barcode"]
    barcode_limit = bc["y_px"] - int(0.12 * dpi)
    if y > barcode_limit:
        report["violations"].append(
            "Back-cover copy runs into the barcode zone (ends at %dpx, limit %dpx). Cut the "
            "blurb or drop the body size." % (y, barcode_limit))
    if y > by + bs["h_px"]:
        report["violations"].append("Back-cover copy overflows the safe area.")

    draw.rectangle([bc["x_px"], bc["y_px"], bc["x_px"] + bc["w_px"], bc["y_px"] + bc["h_px"]],
                   fill=hex_rgb(copy.get("barcode_fill", "#FFFFFF")))
    if copy.get("publisher"):
        p_size = int(9 * dpi / 72.0)
        draw_block(draw, [copy["publisher"]], body_font, p_size,
                   (bx, bc["y_px"] + bc["h_px"] - p_size, bc["x_px"] - bx - int(0.2 * dpi), p_size),
                   "left", back_ink)

    # --- spine ---------------------------------------------------------
    if spec["spine"]["text_allowed"] and copy.get("spine_text", copy["title"]):
        sp = z["spine"]
        clear = int(spec["spine"]["text_clearance_in"] * dpi)
        band_h = sp["w_px"] - 2 * clear
        if band_h < int(0.08 * dpi):
            report["notes"].append("Spine too narrow for comfortable text; left plain.")
        else:
            txt = copy.get("spine_text", copy["title"])
            if copy.get("author"):
                txt = "%s   \u2022   %s" % (txt, copy["author"])
            strip = Image.new("RGB", (sp["h_px"] - 2 * int(0.4 * dpi), sp["w_px"]),
                              hex_rgb(copy.get("spine_color", "#FFFFFF")))
            if args.spine_art or args.front_art:
                strip = wrap.crop((sp["x_px"], sp["y_px"] + int(0.4 * dpi),
                                   sp["x_px"] + sp["w_px"],
                                   sp["y_px"] + sp["h_px"] - int(0.4 * dpi))
                                  ).rotate(90, expand=True)
            sd = ImageDraw.Draw(strip)
            s_size, s_lines, s_used = fit_block(sd, txt, title_font, strip.width, band_h,
                                                max_size=band_h, max_lines=1)
            s_luma = mean_luma(strip, (0, 0, strip.width, strip.height))
            draw_block(sd, s_lines, title_font, s_size,
                       (0, (strip.height - s_used) / 2, strip.width, s_used), "center",
                       copy.get("spine_text_color") or ("#111111" if s_luma > 0.55 else "#FFFFFF"))
            wrap.paste(strip.rotate(-90, expand=True), (sp["x_px"], sp["y_px"] + int(0.4 * dpi)))
            report["measurements"]["spine_text_pt"] = round(s_size * 72.0 / dpi, 1)
    else:
        report["notes"].append("Spine text omitted (page count below the channel minimum).")

    # --- safe-area check ------------------------------------------------
    fs = z["front_safe"]
    for (px_, py_, pw_, ph_) in placed:
        if px_ < fs["x_px"] - 1 or px_ + pw_ > fs["x_px"] + fs["w_px"] + 1 \
           or py_ < fs["y_px"] - 1 or py_ + ph_ > fs["y_px"] + fs["h_px"] + 1:
            report["violations"].append("Front-cover text falls outside the safe area at "
                                        "(%d,%d %dx%d)." % (px_, py_, pw_, ph_))

    if report["measurements"].get("title_height_pct_of_cover", 0) > 20:
        report["notes"].append(
            "Title occupies %.1f%% of cover height, above the 20%% guidance. Either the "
            "title is short enough to want less room, or the art has been squeezed out."
            % report["measurements"]["title_height_pct_of_cover"])
    if report["measurements"].get("title_height_pct_of_cover", 0) < 8:
        report["notes"].append(
            "Title occupies under 8%% of cover height; it will be hard to read at thumbnail "
            "size. Shorten the title or give it more of the type zone.")

    # --- outputs ---------------------------------------------------------
    os.makedirs(args.out_dir, exist_ok=True)
    wrap.save(os.path.join(args.out_dir, "wrap.png"), dpi=(dpi, dpi))
    wrap.save(os.path.join(args.out_dir, "wrap.pdf"), "PDF", resolution=dpi)
    front_only = wrap.crop((z["front"]["x_px"], z["front"]["y_px"],
                            z["front"]["x_px"] + z["front"]["w_px"],
                            z["front"]["y_px"] + z["front"]["h_px"]))
    front_only.save(os.path.join(args.out_dir, "front_only.png"), dpi=(dpi, dpi))

    # Ebook cover is composed independently: different aspect, so a scaled print
    # front would crop the type badly.
    eb_w, eb_h = spec["ebook"]["w_px"], spec["ebook"]["h_px"]
    if args.front_art:
        eb = cover_fill(Image.open(args.front_art).convert("RGB"), eb_w, eb_h)
    else:
        eb = Image.new("RGB", (eb_w, eb_h), bg)
    ed = ImageDraw.Draw(eb, "RGBA")
    m = int(eb_w * 0.08)
    zh = {"top-third": (m, eb_h / 3 - m), "top-half": (m, eb_h / 2 - m),
          "bottom-third": (eb_h * 2 / 3, eb_h / 3 - m),
          "center-band": (eb_h / 3, eb_h / 3)}.get(args.type_zone, (m, eb_h / 3 - m))
    ebox = (m, int(zh[0]), eb_w - 2 * m, int(zh[1]))
    e_luma = mean_luma(eb, ebox)
    e_ink = copy.get("title_color") or ("#111111" if e_luma > 0.55 else "#FFFFFF")
    if scrim:
        ed.rectangle([0, ebox[1] - m // 2, eb_w, ebox[1] + ebox[3] + m // 2],
                     fill=hex_rgb(scrim) + (int(255 * args.scrim_opacity),))
    e_size, e_lines, e_used = fit_block(ed, copy["title"], title_font, ebox[2],
                                        int(ebox[3] * 0.7), max_size=int(ebox[3] * 0.8),
                                        max_lines=args.max_title_lines)
    draw_block(ed, e_lines, title_font, e_size, (ebox[0], ebox[1], ebox[2], e_used),
               args.align, e_ink)
    if author:
        a_size, a_lines, a_used = fit_block(ed, author, body_font, ebox[2], int(eb_h * 0.06),
                                            max_size=max(16, int(e_size * 0.40)), max_lines=1)
        ay = eb_h - m - a_used
        a_luma = mean_luma(eb, (m, ay, eb_w - 2 * m, a_used))
        draw_block(ed, a_lines, body_font, a_size, (m, ay, eb_w - 2 * m, a_used), args.align,
                   "#111111" if a_luma > 0.55 else "#FFFFFF")
    eb.save(os.path.join(args.out_dir, "ebook.jpg"), quality=94, dpi=(dpi, dpi))

    svg = svg_master(spec, copy, args, report)
    open(os.path.join(args.out_dir, "wrap.svg"), "w", encoding="utf-8").write(svg)

    report["outputs"] = {k: os.path.join(args.out_dir, k) for k in
                         ["wrap.png", "wrap.pdf", "front_only.png", "ebook.jpg", "wrap.svg"]}
    report["spec"] = {"wrap_px": [W, H], "dpi": dpi,
                      "spine_in": spec["spine"]["width_in"]}
    json.dump(report, open(os.path.join(args.out_dir, "layout-report.json"), "w",
                           encoding="utf-8"), indent=2)

    print("wrap  : %d x %d px @ %d dpi" % (W, H, dpi))
    print("title : %.1f pt, %.1f%% of cover height"
          % (report["measurements"].get("title_pt", 0),
             report["measurements"].get("title_height_pct_of_cover", 0)))
    for n in report["notes"]:
        print("NOTE : %s" % n)
    for v in report["violations"]:
        print("FAIL : %s" % v)
    print("Wrote %s" % args.out_dir)
    return 1 if report["violations"] else 0


def svg_master(spec, copy, args, report):
    """Editable master: art as linked images, type as real text. For a human
    designer to take over in Illustrator, Affinity or Inkscape."""
    w, h = spec["wrap"]["total_w_in"], spec["wrap"]["total_h_in"]
    z = spec["zones"]
    dpi = spec["input"]["dpi"]

    def img(path, r):
        if not path:
            return ""
        return ('<image href="%s" x="%.4f" y="%.4f" width="%.4f" height="%.4f" '
                'preserveAspectRatio="xMidYMid slice"/>' % (os.path.abspath(path),
                                                            r[0], r[1], r[2], r[3]))

    sx, fx = z["spine"]["x_in"], z["front"]["x_in"]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
             'width="%.4fin" height="%.4fin" viewBox="0 0 %.4f %.4f">' % (w, h, w, h),
             '<g id="artwork">',
             img(args.back_art, (0, 0, sx, h)),
             img(args.spine_art, (sx, 0, fx - sx, h)),
             img(args.front_art, (fx, 0, w - fx, h)),
             '</g>',
             '<g id="type" font-family="%s">' % os.path.basename(args.title_font),
             '<text x="%.4f" y="%.4f" font-size="%.3f" text-anchor="middle">%s</text>'
             % (z["front"]["x_in"] + z["front"]["w_in"] / 2,
                z["front_safe"]["y_in"] + 0.6,
                report["measurements"].get("title_pt", 48) / 72.0,
                (copy.get("title") or "").replace("&", "&amp;").replace("<", "&lt;")),
             '</g>',
             '<g id="guides" opacity="0.6">',
             '<rect x="%.4f" y="%.4f" width="%.4f" height="%.4f" fill="none" stroke="#3a3" '
             'stroke-width="0.01" stroke-dasharray="0.06 0.04"/>'
             % (z["front_safe"]["x_in"], z["front_safe"]["y_in"],
                z["front_safe"]["w_in"], z["front_safe"]["h_in"]),
             '<rect x="%.4f" y="%.4f" width="%.4f" height="%.4f" fill="none" stroke="#f80" '
             'stroke-width="0.01"/>' % (z["barcode"]["x_in"], z["barcode"]["y_in"],
                                        z["barcode"]["w_in"], z["barcode"]["h_in"]),
             '</g>', '</svg>']
    return "\n".join(p for p in parts if p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--copy", required=True)
    ap.add_argument("--front-art")
    ap.add_argument("--back-art")
    ap.add_argument("--spine-art")
    ap.add_argument("--title-font", required=True)
    ap.add_argument("--body-font")
    ap.add_argument("--type-zone", default="top-third",
                    choices=["top-third", "top-half", "bottom-third", "center-band"])
    ap.add_argument("--align", default="center", choices=["left", "center", "right"])
    ap.add_argument("--max-title-lines", type=int, default=3)
    ap.add_argument("--back-body-pt", type=float, default=11.0)
    ap.add_argument("--min-contrast", type=float, default=4.5)
    ap.add_argument("--scrim-opacity", type=float, default=0.55)
    ap.add_argument("--author-bottom", action="store_true",
                    help="Place the author line at the foot of the front cover.")
    ap.add_argument("--out-dir", default="./cover-out")
    return compose(ap.parse_args())


if __name__ == "__main__":
    sys.exit(main())
