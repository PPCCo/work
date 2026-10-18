I'll research how Draw Things CLI handles text and layout positioning for Qwen Image 2512, then check what can be tested. One limit up front: my workspace is a cloud Linux sandbox and can't reach your Mac, so I can't run `draw-things-cli` myself. I'll build a test harness you can run locally instead.

Research is done; I found no coordinate flags in the CLI, so I'm building the test harness around that finding.

**There is no way to give `draw-things-cli` coordinates for text, and I couldn't test the model itself.** My workspace can't reach your Mac or the model, so I built a test harness for you to run. I did check the harness itself here, and its self-test passes.

## What the research found

I read the CLI source (`DrawThingsCLI.swift` and `ScriptModels.swift` in `drawthingsai/draw-things-community`, main branch). Your installed version may differ.

- **No position flags exist.** `generate` takes `--prompt`, `--width`, `--height`, `--seed`, `--steps`, `--cfg`, `--strength`, `--image`, `--config-json` and `--config-file`. Nothing positions text.
- **No mask or hint input.** The generate call hard-codes `mask: nil`, so inpainting a title region isn't available from the CLI.
- **The config JSON can't place text.** `cropTop`, `cropLeft` and `targetImageWidth` are SDXL conditioning and do nothing for Qwen.
- **Typos in `--config-json` fail silently.** Unknown keys are ignored without an error, so a "working" config can mean nothing happened.
- **`--image` is center-cropped.** Your template must match the output aspect ratio exactly, or the layout shifts.

So the only real channels are prompt wording, a layout image passed with `--image` and `--strength`, and compositing text yourself.

## Methods the harness tests

| Method | Idea | Expectation |
|---|---|---|
| `prose`, `zones`, `thirds`, `band` | Describe regions in words (top edge, 13–40% of height, a navy band) | Qwen is documented as good at this. Third-party guides say naming each block's location works best. |
| `coords_px`, `coords_pct` | Literal pixel or percent coordinates in the prompt | Unproven. May be read as loose hints. |
| `bbox_plain`, `bbox_tokens` | Bounding boxes, plus Qwen2.5-VL's `<\|box_start\|>` grounding tokens | Speculative. I found no evidence the image model responds to these. |
| `i2i_050/070/085` | Render a Pillow template with the text at exact pixels, then use it as `--image` at strength 0.5, 0.7 and 0.85 | The closest thing to real coordinates. Lower strength keeps the layout but restyles less. |
| `composite` | Generate art with empty space, then overlay the text in Pillow | Exact placement and spelling by construction, and you control the font. Use an OFL-licensed one for commercial covers. |

## What I validated

The harness's own checks all pass:

- **Commands:** every flag it emits is one I confirmed in the source.
- **Template and OCR:** the template renders at the right size and OCR reads it back inside the target zones.
- **Composite:** it scores a full pass.
- **Failure cases:** a misplaced title, a blank image, and 3-letter and 1-letter misspellings are all caught.

The scoring first let a 3-letter misspelling through, so I made it require an exact text match.

## What you need to run

```
brew install tesseract
python3 covertest.py selftest
python3 covertest.py preflight
caffeinate -i python3 covertest.py run --only prose,i2i_070,composite --seeds 1   # trial run
caffeinate -i python3 covertest.py run                                            # full sweep
python3 covertest.py score
```

The full sweep is 12 methods across 2 seeds, which is a lot of Qwen runs, so start with the trial. Scoring writes `report.md`, `results.csv` and `contact_sheet.png`. OCR can miss stylised lettering, so check the contact sheet too.

My prediction, which your run will confirm or refute: the word-based prompts and the img2img template will be the usable ones, and `composite` will win on accuracy.

Sources: [Qwen Image 2512 text rendering guide (WaveSpeed)](https://wavespeed.ai/blog/posts/qwen-image-2512-text-rendering/), [Qwen Image 2512 poster tutorial (DataCamp)](https://www.datacamp.com/tutorial/qwen-image-2512-tutorial), [dt-cli-wrapper MANUAL.md and AGENTS.md](https://github.com/Wujidadi/dt-cli-wrapper), [draw-things-community source](https://github.com/drawthingsai/draw-things-community).