# Maple Grove Press — FLUX.1-Schnell & SDXL Prompts for ComfyUI

A single complete and comprehensive copy-paste prompt specifically for FLUX 1 Schnell (covering all four concepts, negative guidance, and aspect ratios in plain language it can actually act on), including Stable Diffusion specificall formatted for ComfyUI

One thing worth flagging up front: FLUX.1-schnell's default ComfyUI graph doesn't have a working negative-conditioning path (it's guidance-distilled and typically run at 1–4 steps), so a comma-list negative prompt just won't do anything there — the file folds every exclusion into plain affirmative language inside each positive prompt instead, since that's what FLUX's T5 text encoder actually responds to. The SDXL section uses a real negative prompt since that pipeline supports it properly.

## A quick technical note before you paste anything

FLUX.1-schnell is guidance-distilled and typically run at very low step counts
(1–4). In the standard ComfyUI FLUX workflow there's usually only a single
positive `CLIPTextEncode` node feeding the sampler — there's no working
negative-conditioning pathway the way there is for SDXL, so a traditional
comma-list negative prompt won't do anything meaningful here. To get the same
effect, every FLUX prompt below folds exclusions directly into the
description as plain, affirmative language ("with no text anywhere," "with
no gradients or shadows") — FLUX's text encoder (T5) reads full natural
sentences well, so this is the "negative guidance" pathway that actually
works for this model. The SDXL section further down uses a real, separate
negative prompt instead, since SDXL's CFG pipeline supports it properly.

---

## PART 1 — FLUX.1-Schnell (paste into the positive `CLIPTextEncode` node)

### Concept 1: Icon Only

```
A flat, minimalist vector-style logo icon for an independent publishing
house named Maple Grove Press. The icon shows a single stylized maple leaf
merging seamlessly into the silhouette of an open book, rendered with
clean, confident, even-weight linework and a symmetrical, balanced
composition with generous negative space. The color palette is deep forest
green and warm burnt-amber orange on a soft cream background. The style is
entirely flat two-dimensional vector illustration, like a timeless
publishing house crest or seal — with absolutely no photorealistic
rendering, no 3D or clay-like shading, no gradients, no drop shadows, no
glossy or shiny surfaces, no background clutter, no extra unrelated
objects, no human figures, hands, or faces, and no text or lettering of any
kind anywhere in the image. The linework should stay crisp, high-contrast,
and legible even when the image is shrunk down to a tiny icon size.
```

### Concept 2: Icon + Wordmark

```
A flat, minimalist vector-style logo for an independent publishing house
named Maple Grove Press, combining an icon with a text wordmark. The icon
shows a single stylized maple leaf merging seamlessly into the silhouette
of an open book, positioned above the words "Maple Grove Press" set in a
warm, classic serif typeface. The overall composition is balanced and
symmetrical with generous negative space. The color palette is deep forest
green and warm burnt-amber orange on a soft cream background. The style is
flat two-dimensional vector illustration, like a timeless publishing house
crest — with no photorealistic rendering, no 3D or clay-like shading, no
gradients, no drop shadows, no glossy surfaces, no background clutter, no
extra unrelated objects, and no human figures, hands, or faces. Keep the
wordmark text large, clean, and legible, with no distorted or warped
lettering.
```

_Heads up: diffusion models, including FLUX, still render text unreliably. If the wordmark comes out garbled, generate the icon-only version instead and typeset "Maple Grove Press" separately in vector software._

### Concept 3: Abstract Grove Mark

```
A flat, minimalist vector-style logo icon for an independent publishing
house named Maple Grove Press. The icon shows a small cluster of exactly
three simplified, geometric maple trees standing side by side, arranged so
that the negative space between and around them suggests the shape of an
open book. The linework is clean, even-weight, and confident, with a
symmetrical, balanced composition and generous negative space. The color
palette is deep forest green and warm burnt-amber orange on a soft cream
background. The style is flat two-dimensional vector illustration, like a
timeless publishing house crest or seal — with absolutely no photorealistic
rendering, no 3D or clay-like shading, no gradients, no drop shadows, no
glossy surfaces, no background clutter, no extra unrelated objects, no
human figures, hands, or faces, and no text or lettering of any kind. Keep
the design simple enough to stay legible when shrunk down to a tiny icon
size.
```

### Concept 4: Monogram Mark

```
A flat, minimalist vector-style logo icon for an independent publishing
house named Maple Grove Press. The icon is an interlocking monogram built
from the letters "M," "G," and "P," designed as a single unified emblem,
with a small stylized maple leaf worked into the negative space of one of
the letters. The linework is clean, even-weight, and geometric, with a
symmetrical, balanced composition and generous negative space. The color
palette is deep forest green and warm burnt-amber orange on a soft cream
background. The style is flat two-dimensional vector illustration, like a
timeless publishing house crest or seal — with absolutely no photorealistic
rendering, no 3D or clay-like shading, no gradients, no drop shadows, no
glossy surfaces, no background clutter, no extra unrelated objects, no
human figures, hands, or faces, and no additional text beyond the three
monogram letters. Keep the design simple enough to stay legible when
shrunk down to a tiny icon size.
```

### ComfyUI node settings — FLUX.1-schnell

| Node                                                  | Setting                                                                                                                 |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `CLIPTextEncode` (positive)                           | One of the four prompts above                                                                                           |
| Negative conditioning                                 | Leave unwired, or wire `ConditioningZeroOut` if your graph requires an input — a text negative prompt won't have effect |
| `KSampler` — steps                                    | 4 (schnell is optimized for 1–4 steps; more rarely helps)                                                               |
| `KSampler` — sampler_name                             | `euler`                                                                                                                 |
| `KSampler` — scheduler                                | `simple`                                                                                                                |
| `KSampler` — cfg                                      | 1.0 (guidance-distilled — classic CFG scaling doesn't apply)                                                            |
| `FluxGuidance` (if present in your graph)             | ~3.5 as a starting point                                                                                                |
| `EmptyLatentImage` — square (concepts 1, 3, 4)        | width `1024`, height `1024`                                                                                             |
| `EmptyLatentImage` — banner (concept 2, wide variant) | width `1536`, height `512`                                                                                              |
| Seed                                                  | Randomize and batch 6–8 per concept rather than fixating on one seed                                                    |

---

## PART 2 — SDXL (Stable Diffusion), ComfyUI-formatted

Unlike FLUX.1-schnell, SDXL's pipeline supports real negative conditioning — paste this into the **negative** `CLIPTextEncode` node once and reuse it for all four concepts:

```
text, letters, words, watermark, signature, blurry, photorealistic, 3D
render, gradient, drop shadow, noisy background, cluttered, extra leaves,
asymmetrical, human face, hands, low contrast, jpeg artifacts, low
resolution, sketchy hand-drawn lines, glossy, realistic wood texture
```

### Concept 1: Icon Only — positive prompt

```
flat vector logo icon, publishing house emblem, stylized maple leaf merging
with open book silhouette, clean geometric linework, even line weight,
symmetrical composition, generous negative space, deep forest green and
burnt amber-orange palette, cream background, minimalist, timeless crest
style, flat 2D illustration, high-contrast silhouette, centered, scalable
icon design
```

### Concept 2: Icon + Wordmark — positive prompt

```
flat vector logo, publishing house emblem, stylized maple leaf merging with
open book silhouette, paired with the text "Maple Grove Press" in a warm
classic serif typeface, clean geometric linework, symmetrical composition,
deep forest green and burnt amber-orange palette, cream background,
minimalist, timeless crest style, flat 2D illustration
```

_As with FLUX, expect text rendering to be the weak point — treat this run as a layout reference and typeset the real wordmark separately._

### Concept 3: Abstract Grove Mark — positive prompt

```
flat vector logo icon, publishing house emblem, three simplified geometric
maple trees arranged so their negative space forms an open book shape,
clean geometric linework, even line weight, symmetrical composition,
generous negative space, deep forest green and burnt amber-orange palette,
cream background, minimalist, timeless crest style, flat 2D illustration,
scalable icon design
```

### Concept 4: Monogram Mark — positive prompt

```
flat vector logo icon, interlocking monogram of the letters M G P, small
stylized maple leaf integrated into the negative space of one letter, clean
geometric linework, symmetrical composition, generous negative space, deep
forest green and burnt amber-orange palette, cream background, minimalist,
timeless crest style, flat 2D illustration, scalable icon design
```

### ComfyUI node settings — SDXL

| Node                                                  | Setting                                                                                                                        |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `KSampler` — steps                                    | 30                                                                                                                             |
| `KSampler` — cfg                                      | 7                                                                                                                              |
| `KSampler` — sampler_name                             | `dpmpp_2m`                                                                                                                     |
| `KSampler` — scheduler                                | `karras`                                                                                                                       |
| `EmptyLatentImage` — square icons (1, 3, 4)           | width `1024`, height `1024`                                                                                                    |
| `EmptyLatentImage` — banner (concept 2, wide variant) | width `1344`, height `768` _(SDXL trained on this bucket more reliably than a true 3:1 — crop afterward for a slimmer banner)_ |
| Seed                                                  | Randomize and batch 6–8 per concept                                                                                            |

Either way, treat the winning result as a concept sketch: vectorize and hand-clean it before it becomes the permanent mark.
