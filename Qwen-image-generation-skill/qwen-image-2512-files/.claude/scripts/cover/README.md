# Cover scripts

Deterministic, network-free, stdlib + Pillow (+ optional pypdf). Run in this
order; each reads the previous one's output.

| Script | Does | Fails when |
|---|---|---|
| `cover_spec.py` | spine, bleed, safe areas, barcode zone, ebook size, guide SVG | trim/paper unknown, page count below the binding minimum |
| `cover_prompt.py` | Qwen-Image-2512 prompts per face (positive + negative), seeds, params, upscale plan | a prompt asks for text, has negation in the positive prompt, or has no type zone |
| `cover_compose.py` | sets type, builds wrap + ebook + front + SVG master | text leaves the safe area, back copy hits the barcode zone |
| `thumbnail_test.py` | 80/120/240px, greyscale, squint, contrast + busyness | title band under 4.5:1, cover too busy or too pale |
| `cover_preflight.py` | dimensions, DPI, colour mode, file size, barcode fill | anything a retailer would bounce |

Smoke test with no project:

```bash
python cover_spec.py --trim 8.5x11 --pages 108 --paper white --out /tmp/spec.json --guides /tmp/g.svg
QWEN_SKILL_PATH=/path/to/qwen-kids-art python cover_prompt.py --spec /tmp/spec.json \
  --audience early-reader-6-8 --subject "a friendly cartoon triceratops" \
  --action "waving one hand" --setting "a sunny meadow" --variant full --print
```
