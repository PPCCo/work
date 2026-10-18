#!/usr/bin/env bash
set -euo pipefail

# Run from any working directory. The current Draw Things CLI syntax is used.
# Model files must already be available in the CLI's configured models directory.
CLI="${DRAW_THINGS_CLI:-draw-things-cli}"
MODEL="${MODEL:-qwen_image_2512_bf16_q8p.ckpt}"
SEED="${SEED:-8062512}"
OUT_DIR="${1:-./qwen-position-test-results}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPT_DIR="$SCRIPT_DIR/prompts"

if ! command -v "$CLI" >/dev/null 2>&1; then
  echo "ERROR: Cannot find CLI '$CLI'. Set DRAW_THINGS_CLI to its full path." >&2
  exit 127
fi
mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"

printf 'CLI: '; "$CLI" --version 2>/dev/null || true
printf 'Model: %s\nSeed: %s\nOutput: %s\n' "$MODEL" "$SEED" "$OUT_DIR"
printf 'If your model is outside the CLI default models directory, set DRAWTHINGS_MODELS_DIR before running.\n\n'

run_one() {
  local name="$1"
  local prompt="$PROMPT_DIR/$name.txt"
  local output="$OUT_DIR/${name%.txt}.png"
  echo "=== Generating ${name%.txt} ==="
  "$CLI" generate \
    --model "$MODEL" \
    --prompt-file "$prompt" \
    --width 1024 \
    --height 1536 \
    --seed "$SEED" \
    --no-download-missing \
    --output "$output"
  test -s "$output" || { echo "ERROR: Missing/empty output: $output" >&2; exit 1; }
  echo "Wrote: $output"
  echo
}

run_one 01_semantic_anchors.txt
run_one 02_relative_constraints.txt
run_one 03_percentage_regions.txt
run_one 04_absolute_pixel_coordinates.txt
run_one 05_explicit_bounding_boxes.txt
run_one 06_structured_layout.txt

echo "All six runs completed. Open the PNGs side by side; then run the OCR position report:"
echo "  swift \"$SCRIPT_DIR/analyze_positions.swift\" \"$OUT_DIR\"/*.png"
