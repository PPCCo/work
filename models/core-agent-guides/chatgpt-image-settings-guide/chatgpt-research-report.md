# Research report: precise text positioning with Qwen Image 2512 in Draw Things CLI

# The key finding

For your MacBook Pro M4 with 48 GB unified memory, using `draw-things-cli` with `qwen_image_2512_bf16_q8p.ckpt`, there is an important distinction between telling the model where text should appear and giving the model coordinates it must obey.

The official Qwen Image 2512 prompt guidance recommends specifying each text element's exact wording, position, typography and layout. Examples use natural-language locations such as “top left,” “top center” and “bottom right.” The guidance does not document a dedicated pixel-coordinate syntax or a bounding-box control for text placement.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

+1



The published Draw Things CLI generation interface likewise exposes a prompt, image dimensions, seed, sampling settings and configuration overrides—not dedicated `title_x`, `title_y`, `text_bbox` or equivalent parameters.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub

+1



What this means: you can experiment with numeric coordinates inside the prompt, but we should not assume that `x=512, y=150`, `(50%, 10%)`, or `[120, 80, 900, 260]` functions as a binding layout instruction. These are prompt text unless the model's learned behaviour gives them meaning.

For book covers, I would investigate two separate approaches:

- Prompt-controlled placement: use explicit position words, percentages, pixel coordinates, bounding-box descriptions and relative layout constraints, then measure what the model actually produces.
- Exact placement: generate the cover artwork and place the title, series name and publisher text in known positions using a deterministic layout step. This is the reliable route when a cover must meet a particular design specification.

The research and test plan below distinguishes established capabilities from hypotheses that need an actual generation run on your Mac.

## 1. What the source research establishes

The official sources establish three important facts.

Qwen Image 2512 is designed to render text and layout. Qwen's model documentation describes improvements in text rendering and text–image composition, including more accurate layouts. This makes it a reasonable model for book-cover typography.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



Its documented prompt technique is descriptive, not coordinate-driven. The Qwen Image 2512 prompt helper instructs users to put exact visible text in quotation marks and describe its location, font style, size and layout. Its examples use relative positions such as top-left and bottom-right. I found no documented pixel-based text-placement API in that guidance.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

+1



Draw Things CLI does not expose individual text-element coordinates as generation parameters. The published interface provides `--prompt`, `--prompt-file`, `--width`, `--height`, `--seed`, `--cfg`, `--image` and `--strength`, among other options. There are no documented dedicated title, series or publisher coordinate arguments.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub

+1



Consequently, putting coordinates inside `--prompt` is a valid experiment, but it is not equivalent to passing structured coordinates to a layout engine.

## 2. The different positioning methods, ranked

The following is my expected ranking for prompt-only control, based on the documented prompting approach and how the instructions communicate spatial relationships. It is a hypothesis to validate on your installation, not a ranking established by measured image-generation results.

| Method                                         | Example                                                        | Expected usefulness                             |
| ---------------------------------------------- | -------------------------------------------------------------- | ----------------------------------------------- |
| 1. Spatial anchors                             | “Title at the top centre”                                      | High                                            |
| 2. Relative constraints                        | “Series name directly below the title, sharing its centreline” | High                                            |
| 3. Defined layout regions                      | “Title in the top band; publisher in the bottom band”          | High                                            |
| 4. Percentage coordinates                      | “Title box spans x=10–90%, y=6–18%”                            | Experimental                                    |
| 5. Absolute pixel coordinates                  | “Title box: x=102–922, y=92–276”                               | Experimental; no native pixel-control guarantee |
| 6. Bounding-box notation                       | `[102, 92, 922, 276]`                                          | Experimental; the notation is still prompt text |
| 7. Structured layout or JSON-like instructions | Rows, fields, roles and coordinates described in the prompt    | Experimental                                    |

### Method 1: Spatial anchors

This uses the positions that ordinary visual descriptions communicate clearly.

```
The main title "THE SILENT ATLAS" appears at the top centre
in large uppercase gold serif lettering.

The series name "THE WAYFINDER CHRONICLES" appears directly
below the main title, centred horizontally.

The publisher name "NORTH STAR PRESS" appears near the
bottom centre in small uppercase ivory lettering.
```

This should be your baseline. It follows the documented Qwen prompt guidance without depending on an undocumented coordinate convention.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

+1



Limitation: “Top centre” is a semantic region. It does not define an exact pixel position or constrain the text to a precise bounding rectangle.

### Method 2: Relative coordinates and spatial relationships

Instead of specifying independent positions, define how the text elements relate to each other.

```
All three text elements share the exact horizontal centreline
of the cover.

The main title is the highest text element and occupies the
upper title band.

The series name sits immediately beneath the title, with a
clear gap and no overlap.

The publisher is the lowest text element, centred inside
the bottom imprint band.

Keep the illustration between the series name and publisher.
```

This approach is particularly useful when your actual goal is consistent hierarchy and alignment. It tells the model what the composition should look like, rather than asking it to interpret mathematical notation.

### Method 3: Percentage-based coordinates

Here, you define a normalized layout, which can remain meaningful when the output dimensions change.

For a 1024 × 1536 cover, a proposed specification is:

| Text element | Horizontal range | Vertical range |
| ------------ | ---------------- | -------------- |
| Title        | 10–90%           | 6–18%          |
| Series name  | 18–82%           | 21–26%         |
| Publisher    | 25–75%           | 93–98%         |

The coordinate origin is the top-left corner. The horizontal axis increases toward the right; the vertical axis increases downward.

A prompt could contain:

```
Use the following intended percentage regions:
- Title: x=10–90%, y=6–18%.
- Series name: x=18–82%, y=21–26%.
- Publisher: x=25–75%, y=93–98%.

Centre every line horizontally within its assigned region.
These regions describe intended placement, not visible text.
```

This has two practical advantages over pixels: it's resolution-independent, and the specified regions are easy to compare across portrait covers.

However, the percentages are not automatically interpreted as coordinates by Qwen Image 2512. The model could place the title in the correct general region without respecting the boundaries.

### Method 4: Absolute pixel coordinates

Pixel coordinates define a fixed layout for a particular image size.

For the same 1024 × 1536 cover, you could express the title region as:

```
Image size: 1024 x 1536 pixels.
Coordinate origin: top-left corner (0,0).

Title "THE SILENT ATLAS":
x=102 to 922, y=92 to 276.

Series "THE WAYFINDER CHRONICLES":
x=184 to 840, y=322 to 399.

Publisher "NORTH STAR PRESS":
x=256 to 768, y=1430 to 1505.
```

Those values correspond to the percentage regions above, rounded to pixel coordinates.

This representation is useful for documenting a design specification and gives us a measurable test. But it isn't inherently more enforceable than the natural-language version. It is possible for the model to ignore the numbers, misunderstand them, or treat them as incidental details.

Also, coordinates only make sense alongside image dimensions and a declared origin. Coordinates measured from the bottom-left corner would mean something different from coordinates measured from the top-left.

### Method 5: Explicit bounding boxes

You can express the regions as rectangles:

```
TITLE:     [102, 92, 922, 276]
SERIES:    [184, 322, 840, 399]
PUBLISHER: [256, 1430, 768, 1505]
```

Specify that the values use the convention `[x1, y1, x2, y2]`, where the first pair is the top-left corner and the second pair is the bottom-right corner.

This is precise as a human-readable specification. It is not a native Qwen Image 2512 text-layout input format documented by the official sources.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

+1



I would therefore test bounding-box notation against ordinary spatial language before investing effort in building prompts around it.

### Method 6: Structured layout instructions

You could describe the cover as a sequence of layout rows:

```
ROW 1 — MAIN TITLE
Text: "THE SILENT ATLAS"
Position: upper title band
Alignment: horizontal centre
Style: large uppercase gold serif

ROW 2 — SERIES NAME
Text: "THE WAYFINDER CHRONICLES"
Position: directly below row 1
Alignment: horizontal centre
Style: smaller uppercase ivory serif

ROW 3 — PUBLISHER
Text: "NORTH STAR PRESS"
Position: bottom imprint band
Alignment: horizontal centre
Style: small uppercase ivory
```

This combines structure, text identity, typography and placement. It may be useful for complex covers, although there is no evidence that adding labels such as `ROW 1`, or using a JSON-like structure, activates a special layout parser in this model.

The most sensible experiment is to compare this structured version with the semantic baseline using identical model settings.

## 3. My recommended prompt for your book covers

Rather than using numeric coordinates alone, I recommend combining spatial anchors + relative constraints + percentage regions in one prompt. This is the strongest prompt-only candidate to test because the natural-language instructions describe the visual result while the numbers add another level of detail.

Use this as your starting template:

Create a premium illustrated fantasy book-cover front in a portrait 2:3 composition, 1024 × 1536 pixels. The artwork depicts a mysterious silver observatory above an ancient pine forest beneath an indigo star-filled sky, with a narrow luminous path leading toward the observatory. Use refined cinematic lighting, intricate painterly detail, and professional publishing-quality composition.

**Typography layout**

Coordinate system: origin at the top-left corner, x increases to the right, and y increases downward. Use the following regions as intended layout guidance.

**Main title:** The exact text is "THE SILENT ATLAS". Use very large uppercase gold serif lettering, horizontally centred at x=50%. Position it in the upper title band, approximately x=10–90% and y=6–18%.

**Series name:** The exact text is "THE WAYFINDER CHRONICLES". Use smaller uppercase ivory serif lettering, horizontally centred at x=50%. Place it directly beneath the main title, approximately x=18–82% and y=21–26%, with a clear gap and no overlap.

**Publisher:** The exact text is "NORTH STAR PRESS". Use small uppercase ivory lettering, horizontally centred at x=50%. Position it in the bottom imprint band, approximately x=25–75% and y=93–98%.

Maintain clear visual hierarchy: main title first, series name second, publisher third. Keep all text horizontal, legible, correctly spelled, and separated from the main illustration. Reserve sufficient negative space behind each text element for strong contrast.

The coordinate values are intended layout instructions and must not appear as visible text. Render only the three specified text elements. No additional words, letters, numbers, logos, labels, or watermarks. Preserve the exact text, capitalization and word order.

How to improve it: if the numbers appear to make no difference, simplify the prompt to the natural-language anchors and relationships. Longer prompts are not automatically more controllable. If the numbers help only in some seeds, treat them as a weak preference rather than a constraint.

## 4. A different approach: use a visual layout reference

You can also create a simple wireframe image showing the intended title, series and publisher regions. For example, the wireframe could be a blank 1024 × 1536 cover with three outlined rectangles marking those regions.

Draw Things CLI has image-input and denoising-strength options in its published interface, so image-conditioned generation is an avenue to investigate.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub

+1



The idea is to provide both a visual composition and a prompt describing the text that belongs in each region. However, this should be a separate experiment: image-conditioned generation can alter the supplied composition or fail to reproduce the text faithfully. Confirm that your installed model supports the image-input workflow before depending on it.

There is also a more reliable option for production covers:

[AI Generated Observatory Photos and Artwork | Deep Dream Generator](https://images.openai.com/static-rsc-4/vh9fmvpmWXpqQE9ZgBqNyZokGa0YaOJI72Nfy4A_F69nBbxvjW7cNhjcC6F59t00PcRnC_CdvQ7N2lU-gFpFwHVMDrT86P1dCWxQMF8Zp4QMNd4f-CV_YNsNWTetGj4NuBUw7sMfzizY_7U-YVb0_KNnI87TtQnjFStW6jSW2zM?purpose=inline)

Step 1 — Generate the artwork

Ask Qwen Image 2512 for the illustration and reserve clear title and imprint areas. Instruct it not to render any lettering.

Step 2 — Place the typography

Draw the exact title, series and publisher text using a deterministic layout tool such as SVG, a graphics editor, or a script. Set the bounding boxes, font sizes, alignments, and margins explicitly.

Step 3 — Validate the final cover

Check the exact spelling, font rendering, safe margins and text alignment before exporting the finished image.

This is the approach I recommend when cover titles must be exact and coordinates must be reproducible across a book series. It does not sacrifice artistic quality: Qwen still produces the illustration, while a layout step controls the typography. It also lets you reuse one series template across many books.

## 5. Test the coordinate methods on your Mac

I prepared a test kit for your specified model. It contains six prompts that keep the cover concept and three text strings constant while varying how placement is specified.

Qwen Image 2512 — Book-cover positioning tests

ZIP archive · six prompts, shell runner, macOS Vision OCR analyzer and instructions

&#x20;Download

The kit is configured for `qwen_image_2512_bf16_q8p.ckpt` and uses a fixed seed and 1024 × 1536 output for the first comparison.

Read the test instructions

The test variants are:

| Test                            | What it measures                                       |
| ------------------------------- | ------------------------------------------------------ |
| `01_semantic_anchors`           | Top-centre, below-title and bottom-centre instructions |
| `02_relative_constraints`       | Relative placement and shared alignment                |
| `03_percentage_regions`         | Percentage-based regions                               |
| `04_absolute_pixel_coordinates` | Absolute x/y pixel ranges                              |
| `05_explicit_bounding_boxes`    | `[x1,y1,x2,y2]` notation                               |
| `06_structured_layout`          | Labelled rows and roles                                |

### Run the tests

Extract the ZIP, open Terminal in the extracted `book-cover-position-test-kit` directory, and run:

```
./run_position_tests.sh ./results
```

The script invokes your `draw-things-cli`, uses your specified model, fixes the seed at `8062512`, and writes six PNG files into `results`. If your CLI cannot find the model in its configured models directory, set `DRAWTHINGS_MODELS_DIR` to the appropriate directory before running it.

The script uses the model's recommended default sampling settings rather than assuming an unverified steps/CFG combination.

### Measure the actual text positions

The kit includes a Swift OCR analyzer using Apple's Vision framework, which is available on macOS. Run:

```
swift analyze_positions.swift ./results/*.png \
  > ./results/ocr-report.tsv
```

The report contains recognized text and approximate bounding boxes expressed as percentages of the image, measured from the top-left origin. This lets you check whether the title, series name and publisher appear in their intended regions.

The target regions are:

- Title: approximately 6–18% down the image.
- Series name: approximately 21–26% down the image.
- Publisher: approximately 93–98% down the image.

OCR is a measurement aid, not a guarantee. Highly stylized lettering might be split into multiple OCR regions or missed. Inspect the images as well as the report.

## 6. What has actually been validated?

I reviewed the published Qwen Image 2512 prompt guidance and the current Draw Things CLI source interface. I also checked the test runner's shell syntax and exercised its execution/output-file flow using a mock CLI.

I have not executed Qwen Image 2512 inference on your MacBook. I cannot truthfully report that any of the six coordinate methods has succeeded or failed empirically on your local installation without the generated images. The test kit is intended to establish that result on your actual model and runtime.

For a meaningful conclusion, treat the initial six images as a screening test. Then rerun the two best prompt variants with two or three additional seeds each. A positioning method is genuinely useful only if its measured results consistently outperform the semantic-anchor baseline.

My recommendation: start with natural-language anchors plus relative constraints. Run the six-way comparison before investing in pixel-coordinate or bounding-box prompting. If you need repeatable, production-quality book-cover typography with precise placement, use Qwen for the artwork and apply the text in a deterministic layout step.