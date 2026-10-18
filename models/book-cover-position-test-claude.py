#!/usr/bin/env python3
"""
covertest.py - test every practical way of positioning text on a book cover
with draw-things-cli + Qwen Image 2512.

draw-things-cli has NO text-position / coordinate flag, so "coordinates" are
tested through the only channels that exist:
  * prompt wording (prose, zones, thirds, band, pixel/percent coords, bbox forms)
  * img2img from a Pillow-rendered layout template (--image + --strength)
  * deterministic Pillow compositing (control; exact coordinates)

Subcommands:
  preflight   check CLI, model file, and config-json parsing (generates nothing)
  run         generate all methods x seeds (use --dry-run to only print commands)
  score       OCR each image, measure text accuracy + position, write report
  selftest    validate the harness itself without draw-things-cli

Requires: Python 3.9+, Pillow, tesseract on PATH (brew install tesseract).
"""
import argparse, csv, difflib, json, os, re, shlex, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

MODEL_DEFAULT = "qwen_image_2512_bf16_q8p.ckpt"

# Normalised zones (x0, y0, x1, y1) as fractions of the canvas. Used for the
# template, the compositor, and the pass/fail position check.
ZONES = {
    "series":    (0.08, 0.03, 0.92, 0.12),
    "title":     (0.06, 0.13, 0.94, 0.40),
    "publisher": (0.15, 0.88, 0.85, 0.97),
}
ZONE_TOL = 0.03          # tolerance (fraction of canvas) when testing "inside zone"
                         # text counts as correct only on an exact OCR match (see best_match)

# Every flag the harness may emit; verified against DrawThingsCLI.swift (generate).
KNOWN_FLAGS = {
    "--model", "--prompt-file", "--width", "--height", "--seed", "--output",
    "--image", "--strength", "--steps", "--cfg", "--config-json",
    "--no-download-missing", "--negative-prompt", "--negative-prompt-file",
    "--models-dir", "--disable-preview",
}

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
]


# --------------------------------------------------------------------------
# text / prompt definitions
# --------------------------------------------------------------------------
def texts(args):
    return {"series": args.series.upper(), "title": args.title, "publisher": args.publisher}


def art_prompt(args):
    return args.art


def prompts(args, W, H):
    t = texts(args)
    S, T, P = t["series"], t["title"], t["publisher"]
    art = art_prompt(args)
    cx = W // 2
    return {
        "prose": (
            f'A children\'s picture book cover. {art} '
            f'At the very top edge, small text reads "{S}". '
            f'Below it, in the upper third, the large centered title reads "{T}" in bold serif letters. '
            f'At the very bottom edge, small text reads "{P}".'),
        "zones": (
            f'Portrait book cover, {art} Layout from top to bottom: '
            f'top band (0-12% of height): small centered text "{S}". '
            f'upper area (13-40% of height): large centered title text "{T}". '
            f'middle and lower area (40-86%): the illustration. '
            f'bottom band (88-97%): small centered text "{P}".'),
        "thirds": (
            f'Book cover split into three horizontal thirds. {art} '
            f'Upper third: the series name "{S}" in small letters above the large title "{T}". '
            f'Middle third: illustration only, no text. '
            f'Lower third: illustration, with the publisher name "{P}" in small letters along the bottom edge.'),
        "band": (
            f'Book cover. {art} A solid dark navy band covers the top 40% of the cover; '
            f'inside the band, centered: "{S}" in small cream capital letters, then the title "{T}" in large cream letters. '
            f'A thin navy band runs along the bottom edge with "{P}" in small cream letters. '
            f'The illustration fills the area between the bands.'),
        "coords_px": (
            f'Book cover, {W}x{H} pixels. {art} '
            f'Text "{S}" centered at pixel ({cx}, {int(H*0.075)}). '
            f'Text "{T}" centered at pixel ({cx}, {int(H*0.265)}), large. '
            f'Text "{P}" centered at pixel ({cx}, {int(H*0.925)}).'),
        "coords_pct": (
            f'Book cover. {art} '
            f'Text "{S}" at x=50%, y=7.5% (small). '
            f'Text "{T}" at x=50%, y=26.5% (large). '
            f'Text "{P}" at x=50%, y=92.5% (small).'),
        "bbox_plain": (
            f'Book cover. {art} Text placement as bounding boxes [x1,y1,x2,y2] on a 0-1000 grid: '
            f'"{S}" [80,30,920,120]; "{T}" [60,130,940,400]; "{P}" [150,880,850,970].'),
        "bbox_tokens": (  # speculative: Qwen2.5-VL grounding syntax; may be ignored
            f'Book cover. {art} '
            f'<|object_ref_start|>text "{S}"<|object_ref_end|><|box_start|>(80,30),(920,120)<|box_end|> '
            f'<|object_ref_start|>text "{T}"<|object_ref_end|><|box_start|>(60,130),(940,400)<|box_end|> '
            f'<|object_ref_start|>text "{P}"<|object_ref_end|><|box_start|>(150,880),(850,970)<|box_end|>'),
        # i2i methods reuse this prompt; the template supplies the geometry
        "i2i": (
            f'Book cover. {art} The text "{S}" at the top, the large title "{T}" below it, '
            f'and "{P}" at the bottom, exactly as laid out in the reference image.'),
        # composite background: art only, with calm space reserved for text
        "bg": (
            f'{art} Composition with calm, uncluttered sky in the top 40% and calm foreground in the bottom 12%. '
            f'No text, no letters, no logos.'),
    }


# method id -> (kind, params)
METHODS = {
    "prose":       ("t2i", {"prompt": "prose"}),
    "zones":       ("t2i", {"prompt": "zones"}),
    "thirds":      ("t2i", {"prompt": "thirds"}),
    "band":        ("t2i", {"prompt": "band"}),
    "coords_px":   ("t2i", {"prompt": "coords_px"}),
    "coords_pct":  ("t2i", {"prompt": "coords_pct"}),
    "bbox_plain":  ("t2i", {"prompt": "bbox_plain"}),
    "bbox_tokens": ("t2i", {"prompt": "bbox_tokens"}),
    "i2i_050":     ("i2i", {"prompt": "i2i", "strength": 0.50}),
    "i2i_070":     ("i2i", {"prompt": "i2i", "strength": 0.70}),
    "i2i_085":     ("i2i", {"prompt": "i2i", "strength": 0.85}),
    "composite":   ("composite", {"prompt": "bg"}),
}


# --------------------------------------------------------------------------
# drawing helpers (template + compositor)
# --------------------------------------------------------------------------
def find_font(user_font):
    for p in ([user_font] if user_font else []) + FONT_CANDIDATES:
        if p and Path(p).exists():
            return p
    sys.exit("No usable bold font found; pass --font /path/to/font.ttf (use an OFL-licensed font for commercial covers).")


def wrap_fit(draw, text, box_w, box_h, font_path, max_size):
    """Largest font size at which greedy-wrapped text fits the box."""
    for size in range(max_size, 8, -2):
        font = ImageFont.truetype(font_path, size)
        lines, cur = [], ""
        for w in text.split():
            trial = (cur + " " + w).strip()
            if draw.textlength(trial, font=font) <= box_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        lh = int(size * 1.18)
        if (all(draw.textlength(l, font=font) <= box_w for l in lines)
                and lh * len(lines) <= box_h):
            return font, lines, lh
    return ImageFont.truetype(font_path, 10), [text], 12


def draw_block(draw, text, zone, W, H, font_path, fill, max_frac):
    x0, y0, x1, y1 = (zone[0]*W, zone[1]*H, zone[2]*W, zone[3]*H)
    font, lines, lh = wrap_fit(draw, text, x1 - x0, y1 - y0, font_path, int(max_frac * H))
    y = y0 + ((y1 - y0) - lh * len(lines)) / 2
    for line in lines:
        w = draw.textlength(line, font=font)
        draw.text(((x0 + x1) / 2 - w / 2, y), line, font=font, fill=fill)
        y += lh


def draw_all_text(img, tx, font_path, fill=(245, 236, 210)):
    d = ImageDraw.Draw(img)
    W, H = img.size
    draw_block(d, tx["series"], ZONES["series"], W, H, font_path, fill, 0.040)
    draw_block(d, tx["title"], ZONES["title"], W, H, font_path, fill, 0.110)
    draw_block(d, tx["publisher"], ZONES["publisher"], W, H, font_path, fill, 0.040)


def make_template(path, W, H, tx, font_path):
    img = Image.new("RGB", (W, H), (20, 36, 66))
    draw_all_text(img, tx, font_path)
    img.save(path)
    return path


def make_composite(bg_path, out_path, tx, font_path):
    img = Image.open(bg_path).convert("RGB")
    draw_all_text(img, tx, font_path)
    img.save(out_path)


# --------------------------------------------------------------------------
# command assembly
# --------------------------------------------------------------------------
def build_cmd(args, prompt_file, out, W, H, seed, image=None, strength=None):
    cmd = [args.cli, "generate", "--model", args.model,
           "--prompt-file", str(prompt_file), "--width", str(W), "--height", str(H),
           "--seed", str(seed), "--output", str(out), "--no-download-missing"]
    if args.steps:
        cmd += ["--steps", str(args.steps)]
    if args.cfg:
        cmd += ["--cfg", str(args.cfg)]
    if args.config_json:
        cmd += ["--config-json", args.config_json]
    if image:
        cmd += ["--image", str(image), "--strength", str(strength)]
    return cmd


def check_flags(cmd):
    bad = [t for t in cmd if t.startswith("--") and t not in KNOWN_FLAGS]
    return bad


def parse_size(s):
    W, H = (int(x) for x in s.lower().split("x"))
    if W % 64 or H % 64:
        sys.exit(f"--size must be multiples of 64 (CLI rejects otherwise), got {W}x{H}")
    return W, H


# --------------------------------------------------------------------------
# run
# --------------------------------------------------------------------------
def cmd_run(args):
    W, H = parse_size(args.size)
    out = Path(args.out)
    (out / "images").mkdir(parents=True, exist_ok=True)
    (out / "prompts").mkdir(exist_ok=True)
    tx = texts(args)
    font = find_font(args.font)
    tpl = make_template(out / "template.png", W, H, tx, font)
    P = prompts(args, W, H)
    for k, v in P.items():
        (out / "prompts" / f"{k}.txt").write_text(v + "\n")
    wanted = args.only.split(",") if args.only else list(METHODS)
    unknown = [m for m in wanted if m not in METHODS]
    if unknown:
        sys.exit(f"unknown methods: {unknown}; choose from {list(METHODS)}")
    seeds = [101, 202, 303, 404][:args.seeds]
    log = open(out / "commands.sh", "w")
    failures = 0
    for m in wanted:
        kind, prm = METHODS[m]
        for seed in seeds:
            target = out / "images" / f"{m}__s{seed}.png"
            pf = out / "prompts" / f"{prm['prompt']}.txt"
            if kind == "composite":
                bg = out / "images" / f"composite_bg__s{seed}.png"
                cmd = build_cmd(args, pf, bg, W, H, seed)
            elif kind == "i2i":
                cmd = build_cmd(args, pf, target, W, H, seed, image=tpl, strength=prm["strength"])
            else:
                cmd = build_cmd(args, pf, target, W, H, seed)
            bad = check_flags(cmd)
            if bad:
                sys.exit(f"harness bug: unknown flags {bad}")
            line = " ".join(shlex.quote(c) for c in cmd)
            log.write(line + "\n")
            if args.dry_run:
                print(line)
                continue
            gen_target = bg if kind == "composite" else target
            if gen_target.exists() and not args.force:
                print(f"skip (exists) {gen_target.name}")
            else:
                print(f"[{m} seed {seed}] generating ...", flush=True)
                r = subprocess.run(cmd, capture_output=True, text=True)
                if r.returncode != 0 or not gen_target.exists():
                    failures += 1
                    print(f"  FAILED rc={r.returncode}\n  {r.stderr.strip()[-400:]}")
                    continue
            if kind == "composite":
                make_composite(bg, target, tx, font)
    log.close()
    print(f"\nCommands logged to {out/'commands.sh'}; failures: {failures}")
    if not args.dry_run:
        print(f"Next: python3 {sys.argv[0]} score --out {out}")


# --------------------------------------------------------------------------
# preflight
# --------------------------------------------------------------------------
def cmd_preflight(args):
    ok = True
    r = subprocess.run([args.cli, "models", "list", "--downloaded-only"], capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL: could not run draw-things-cli:", r.stderr.strip()[:300]); ok = False
    elif args.model in r.stdout:
        print(f"OK   model present: {args.model}")
    else:
        print(f"WARN model '{args.model}' not in downloaded list (check name / --models-dir)")
    # Config probe (from verified CLI behaviour): a nonexistent --image makes the CLI stop
    # after config parsing, so nothing is generated.
    probe_cfg = args.config_json or "{}"
    r = subprocess.run([args.cli, "generate", "--model", args.model, "--prompt", "x",
                        "--config-json", probe_cfg, "--image", "/nonexistent/probe.png",
                        "--no-download-missing"], capture_output=True, text=True)
    blob = r.stdout + r.stderr
    if "Failed to parse configuration override JSON" in blob:
        print("FAIL config-json did not parse"); ok = False
    else:
        print("OK   config-json parsed (CLI stopped at the missing probe image, as expected)")
        print("     note: unknown keys in --config-json are silently ignored, so this proves syntax, not effect.")
    sys.exit(0 if ok else 1)


# --------------------------------------------------------------------------
# OCR + scoring
# --------------------------------------------------------------------------
def norm(s):
    return re.sub(r"[^a-z0-9 ]+", "", s.lower()).strip()


def ocr_words(img_path, psm, invert=False):
    tmp = Path(img_path)
    src = tmp
    if invert:
        from PIL import ImageOps
        im = ImageOps.invert(Image.open(tmp).convert("RGB"))
        src = tmp.with_suffix(".inv.png")
        im.save(src)
    r = subprocess.run(["tesseract", str(src), "stdout", "--psm", str(psm), "tsv"],
                       capture_output=True, text=True)
    if invert and src.exists():
        src.unlink()
    words = []
    for row in r.stdout.splitlines()[1:]:
        p = row.split("\t")
        if len(p) < 12 or p[0] != "5":
            continue
        txt, conf = p[11].strip(), float(p[10])
        if txt and conf > 20:
            l, t, w, h = (int(p[i]) for i in (6, 7, 8, 9))
            words.append((norm(txt), (l, t, l + w, t + h)))
    return [w for w in words if w[0]]


def best_match(words, expected):
    """Return (fuzzy ratio, bbox, exact) for the best OCR window.
    exact = identical to the expected text ignoring case/punctuation/spaces,
    so a single wrong letter fails (that is a real defect on a book cover)."""
    exp = norm(expected)
    n = len(exp.split())
    best = (0.0, None, False)
    for size in {max(1, n - 1), n, n + 1}:
        for i in range(0, max(1, len(words) - size + 1)):
            win = words[i:i + size]
            if len(win) < size:
                continue
            joined = " ".join(w[0] for w in win)
            ratio = difflib.SequenceMatcher(None, joined, exp).ratio()
            exact = joined.replace(" ", "") == exp.replace(" ", "")
            if (exact, ratio) > (best[2], best[0]):
                xs = [b for _, b in win]
                box = (min(b[0] for b in xs), min(b[1] for b in xs),
                       max(b[2] for b in xs), max(b[3] for b in xs))
                best = (ratio, box, exact)
    return best


def score_image(path, tx):
    W, H = Image.open(path).size
    candidates = [ocr_words(path, psm, inv) for psm in (11, 3) for inv in (False, True)]
    res = {}
    for key, text in tx.items():
        ratio, box, exact = max((best_match(w, text) for w in candidates),
                                key=lambda x: (x[2], x[0]))
        z = ZONES[key]
        row = {"ratio": round(ratio, 3), "text_ok": exact, "in_zone": False,
               "err": None, "box": box}
        if box and ratio >= 0.5:
            cx, cy = (box[0] + box[2]) / 2 / W, (box[1] + box[3]) / 2 / H
            zx, zy = (z[0] + z[2]) / 2, (z[1] + z[3]) / 2
            row["err"] = round(((cx - zx) ** 2 + (cy - zy) ** 2) ** 0.5, 3)
            row["in_zone"] = (z[0] - ZONE_TOL <= cx <= z[2] + ZONE_TOL and
                              z[1] - ZONE_TOL <= cy <= z[3] + ZONE_TOL)
        res[key] = row
    return res


def contact_sheet(results, out_png, W, H, methods, seeds):
    tw, th = 192, int(192 * H / W)
    pad, label = 6, 22
    sheet = Image.new("RGB", (len(seeds) * (tw + pad) + 150, len(methods) * (th + label + pad)), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    for r, m in enumerate(methods):
        y = r * (th + label + pad)
        d.text((6, y + 6), m, fill=(255, 255, 255))
        for c, s in enumerate(seeds):
            key = f"{m}__s{s}"
            p = Path(results["_dir"]) / "images" / f"{key}.png"
            x = 150 + c * (tw + pad)
            if not p.exists():
                continue
            im = Image.open(p).convert("RGB").resize((tw, th))
            dd = ImageDraw.Draw(im)
            for k, z in ZONES.items():
                info = results.get(key, {}).get(k)
                good = info and info["text_ok"] and info["in_zone"]
                dd.rectangle([z[0]*tw, z[1]*th, z[2]*tw, z[3]*th],
                             outline=(0, 220, 0) if good else (230, 40, 40), width=1)
            sheet.paste(im, (x, y))
            d.text((x, y + th + 4), f"s{s}", fill=(200, 200, 200))
    sheet.save(out_png)


def cmd_score(args):
    out = Path(args.out)
    tx = texts(args)
    imgs = sorted((out / "images").glob("*__s*.png"))
    imgs = [p for p in imgs if not p.name.startswith("composite_bg")]
    if not imgs:
        sys.exit("no images found; run `run` first")
    results, rows = {"_dir": str(out)}, []
    for p in imgs:
        key = p.stem
        results[key] = score_image(p, tx)
        m, s = key.split("__s")
        for blk, r in results[key].items():
            rows.append({"method": m, "seed": s, "block": blk, "text_ratio": r["ratio"],
                         "text_ok": r["text_ok"], "in_zone": r["in_zone"], "pos_err": r["err"]})
    with open(out / "results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    methods = [m for m in METHODS if any(r["method"] == m for r in rows)]
    seeds = sorted({int(r["seed"]) for r in rows})
    lines = ["# Cover text positioning results", "",
             f"Pass = exact OCR match of the text (case/spacing ignored) AND text centre inside its zone (+/-{ZONE_TOL}).", "",
             "| method | blocks passed | text correct | in zone | mean pos err |", "|---|---|---|---|---|"]
    for m in methods:
        rr = [r for r in rows if r["method"] == m]
        n = len(rr)
        both = sum(1 for r in rr if r["text_ok"] and r["in_zone"])
        tok = sum(1 for r in rr if r["text_ok"])
        zin = sum(1 for r in rr if r["in_zone"])
        errs = [r["pos_err"] for r in rr if r["pos_err"] is not None]
        me = f"{sum(errs)/len(errs):.3f}" if errs else "n/a"
        lines.append(f"| {m} | {both}/{n} | {tok}/{n} | {zin}/{n} | {me} |")
    lines += ["", "OCR is a proxy: stylised lettering can fail OCR while looking fine, so check the contact sheet.",
              "pos err = distance of text centre from zone centre, as a fraction of canvas size."]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    W, H = Image.open(imgs[0]).size
    contact_sheet(results, out / "contact_sheet.png", W, H, methods, seeds)
    print("\n".join(lines))
    print(f"\nWrote {out/'report.md'}, {out/'results.csv'}, {out/'contact_sheet.png'}")


# --------------------------------------------------------------------------
# selftest: validate harness without draw-things-cli
# --------------------------------------------------------------------------
def cmd_selftest(args):
    import tempfile
    W, H = parse_size(args.size)
    font = find_font(args.font)
    tx = texts(args)
    fails = 0

    def check(name, cond, detail=""):
        nonlocal fails
        print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
        fails += 0 if cond else 1

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # 1. command assembly uses only verified flags, for every method
        args.out = str(td); args.dry_run = True; args.only = None; args.seeds = 1
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cmd_run(args)
        lines = [l for l in buf.getvalue().splitlines() if "generate" in l]
        check("dry-run emits a command per method", len(lines) == len(METHODS), f"{len(lines)} cmds")
        check("all emitted flags are in the verified set",
              all(not check_flags(shlex.split(l)) for l in lines))
        check("size multiple-of-64 guard works", subprocess.run(
            [sys.executable, __file__, "run", "--size", "770x1152", "--dry-run", "--out", str(td/"x")],
            capture_output=True).returncode != 0)
        # 2. template is the requested size and its text is where the zones say
        tpl = make_template(td / "t.png", W, H, tx, font)
        check("template size", Image.open(tpl).size == (W, H))
        res = score_image(tpl, tx)
        for k, r in res.items():
            check(f"template '{k}' read back + in zone", r["text_ok"] and r["in_zone"], f"ratio={r['ratio']} err={r['err']}")
        # 3. composite on a busy gradient background still scores as pass
        bg = Image.new("RGB", (W, H))
        px = bg.load()
        for y in range(H):
            for x in range(0, W):
                px[x, y] = (30 + 60 * y // H, 50 + 80 * x // W, 120)
        bg.save(td / "bg.png")
        make_composite(td / "bg.png", td / "c.png", tx, font)
        res = score_image(td / "c.png", tx)
        check("composite passes all three blocks",
              all(r["text_ok"] and r["in_zone"] for r in res.values()),
              ", ".join(f"{k}:{r['ratio']}" for k, r in res.items()))
        # 4. negative control: title drawn in the publisher zone must be flagged
        bad = Image.new("RGB", (W, H), (20, 36, 66))
        d = ImageDraw.Draw(bad)
        draw_block(d, tx["title"], ZONES["publisher"], W, H, font, (245, 236, 210), 0.04)
        draw_block(d, tx["series"], ZONES["series"], W, H, font, (245, 236, 210), 0.04)
        draw_block(d, tx["publisher"], ZONES["publisher"], W, H, font, (245, 236, 210), 0.04)
        bad.save(td / "bad.png")
        res = score_image(td / "bad.png", tx)
        check("misplaced title is detected (not in title zone)", not res["title"]["in_zone"],
              f"title in_zone={res['title']['in_zone']} err={res['title']['err']}")
        # 5. blank image: nothing found, nothing passes
        Image.new("RGB", (W, H), (0, 0, 0)).save(td / "blank.png")
        res = score_image(td / "blank.png", tx)
        check("blank image scores zero", not any(r["text_ok"] for r in res.values()))
        # 6. misspelled title is caught
        mis = Image.new("RGB", (W, H), (20, 36, 66))
        tx2 = dict(tx); tx2["title"] = "The Litle Lighthose Keper"
        draw_all_text(mis, tx2, font)
        mis.save(td / "mis.png")
        res = score_image(td / "mis.png", tx)
        check("3-letter misspelling is caught", not res["title"]["text_ok"],
              f"ratio={res['title']['ratio']}")
        one = Image.new("RGB", (W, H), (20, 36, 66))
        tx3 = dict(tx); tx3["title"] = "The Little Lighthouse Keepor"
        draw_all_text(one, tx3, font)
        one.save(td / "one.png")
        res = score_image(td / "one.png", tx)
        check("single-letter typo is caught", not res["title"]["text_ok"],
              f"ratio={res['title']['ratio']}")
    print("\nselftest:", "ALL PASS" if fails == 0 else f"{fails} FAILED")
    sys.exit(1 if fails else 0)


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--out", default="cover_pos_test")
        p.add_argument("--cli", default="draw-things-cli")
        p.add_argument("--model", default=MODEL_DEFAULT)
        p.add_argument("--size", default="768x1152", help="WxH, multiples of 64 (default 2:3 portrait)")
        p.add_argument("--title", default="The Little Lighthouse Keeper")
        p.add_argument("--series", default="Harbor Tales")
        p.add_argument("--publisher", default="Willow Press")
        p.add_argument("--art", default="Watercolor illustration of a cozy lighthouse on a rocky coast at dusk, warm light in the windows.")
        p.add_argument("--font", default=None, help="TTF path; use an OFL-licensed font for commercial covers")
        p.add_argument("--steps", type=int, default=None, help="omit to use the model's recommended steps")
        p.add_argument("--cfg", type=float, default=None, help="omit to use the model's recommended cfg")
        p.add_argument("--config-json", default=None, help="extra JSGenerationConfiguration JSON (camelCase keys)")

    for name, fn in (("preflight", cmd_preflight), ("run", cmd_run), ("score", cmd_score), ("selftest", cmd_selftest)):
        p = sub.add_parser(name); common(p); p.set_defaults(fn=fn)
        if name == "run":
            p.add_argument("--only", default=None, help="comma list of method ids")
            p.add_argument("--seeds", type=int, default=2, help="1-4 (default 2)")
            p.add_argument("--dry-run", action="store_true")
            p.add_argument("--force", action="store_true", help="regenerate existing images")
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
