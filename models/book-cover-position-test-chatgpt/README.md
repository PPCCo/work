# Qwen Image 2512 — Book-cover text-position test kit

This kit is intended for macOS with `draw-things-cli` and the model file `qwen_image_2512_bf16_q8p.ckpt` already installed. It compares six prompt encodings with the same art brief, output dimensions, and seed. It does **not** assume that coordinates in prose are a native layout API.

## What is tested

1. `01_semantic_anchors`: normal top-centre / below-title / bottom-centre instructions.
2. `02_relative_constraints`: spatial relationships, aligned centreline and reserved bands.
3. `03_percentage_regions`: normalized percentage regions.
4. `04_absolute_pixel_coordinates`: absolute pixel ranges with top-left origin.
5. `05_explicit_bounding_boxes`: `[x1,y1,x2,y2]` syntax.
6. `06_structured_layout`: labelled row-based layout specification.

Every prompt asks for the same artwork and exactly the same three strings. The common output size is 1024×1536; all dimensions are multiples of 64. The seed is fixed to 8062512 for a controlled comparison.

## Run

```bash
cd /path/to/book-cover-position-test-kit

# Optional: point to the directory containing the model file.
export DRAWTHINGS_MODELS_DIR="$HOME/Documents/Models"

# Optional: if the CLI binary isn't named draw-things-cli or isn't on PATH:
# export DRAW_THINGS_CLI="/full/path/to/draw-things-cli"

./run_position_tests.sh ./results
```

If the model is stored inside Draw Things' application container rather than `~/Documents/Models`, set `DRAWTHINGS_MODELS_DIR` to the actual directory where the CLI expects to find it. The script uses `--no-download-missing` to avoid an unexpected model download. If your installed CLI predates that flag, check `draw-things-cli generate --help` and remove the flag or update the CLI.

The script intentionally relies on the model's recommended default sampling settings instead of imposing an unverified step/CFG recipe. Same seed does not make outputs identical when prompts differ; it reduces one source of variation.

## Measure text positions with macOS Vision OCR

After generation, run:

```bash
swift analyze_positions.swift ./results/*.png > ./results/ocr-report.tsv
```

The report gives each recognized line's approximate bounding box as percentages of the full image, using a top-left origin. It marks exact recognized title, series and publisher strings when they are recognized together. If OCR splits a string across lines or misses stylized lettering, inspect the PNG manually; OCR is a measurement aid, not definitive proof of legibility.

## How to judge the results

- **Text correctness:** exact spelling, capitalization, word order, no extra text.
- **Role order:** title above series; publisher near the bottom.
- **Horizontal alignment:** all three text centres should be near x=50% if centred layout is intended.
- **Vertical placement:** compare OCR `CENTER_Y_%` against the target zones: title roughly 6–18%, series roughly 21–26%, publisher roughly 93–98%. These are target bands, not guarantees.
- **Repeatability:** take the two best methods and rerun them with 2–3 other seeds before concluding. One seed per method is a screening test only.

A method is useful only if the images and OCR report show a consistent improvement over the semantic-anchor baseline. If coordinates produce no systematic improvement, treat them as decorative prompt text rather than control inputs.

## Important limitation

This is a **local test harness**, not a claim that generation was executed on your Mac. The source audit can establish which interfaces are documented; empirical placement success must be measured from the PNGs produced by your installed CLI/model build.
