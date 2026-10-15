# FLUX.2 [klein] 4B on draw-things-cli — LoRA / upscaler / settings / prompt playbook

Audience: an AI agent + recommendation engine. Written 2026-10-15. Hardware: MacBook Pro M4 (12-core), 48 GB unified memory.
Confidence tags: **[V]** verified in a primary source this session · **[I]** inferred from evidence · **[H]** heuristic, not benchmarked on this machine (A/B test before trusting).

---

## 0. Critical corrections to the original setup (read first)

1. **`flux_2_klein_4b_q8p.ckpt` is not in Draw Things' official model list [V].** Official Klein 4B files are `flux_2_klein_4b_{q8p,q6p,i8x}.ckpt` (distilled) and `flux_2_klein_base_4b_{q8p,q6p,i8x}.ckpt` (base). The f16 file is therefore custom/self-converted and its variant (distilled vs base) is unknown. Run the variant test in §1.2.
2. **Your template (`--steps 28 --cfg 5.5`) is base-model style, and cfg 5.5 is high.** Distilled Klein = 4 steps, CFG 1.0 [V]. Base Klein = 28–50 steps, CFG ≈4.0 (BFL reference 4.0; community LoRA cards use 3.0–4.5) [V]. Do not use cfg > 4.5.
3. **`"schedule_sampler": 1` is not a field in Draw Things' config schema [V]** (checked `config.fbs`). Remove it. Valid keys used here: `sampler`, `loras`, `upscaler`.
4. **LoRAs must be in Draw Things' own `<name>_lora_f16.ckpt` format and registered in `custom_lora.json`. A raw `.safetensors` passed to the CLI runs with no error and no effect [V].** The app converts on import; the CLI does not. See §3.
5. **A LoRA is used only if its model version equals the base model's version; otherwise it is silently dropped [V].** Klein 4B distilled and Klein 4B Base share one version (`flux2_4b`) [V], so one 4B LoRA works on both. **9B LoRAs (`flux2_9b`) will be silently ignored.** Most "Klein" LoRAs on HF are 9B — check the model tree for `klein-4B` / `klein-base-4B`.
6. **No dedicated 4B coloring-book / line-art / mandala / watercolor / photoreal LoRA was found** (searched HF, 2026-10-15). The well-known ones (`artificialguybr/COLORINGBOOK-REDMOND-FLUXKLEIN9B`, `LineartAnime-Redmond-Flux9BKlein`) are **9B-only → do not use**. For those categories use prompt-only on the Base variant (§6), or train your own 4B LoRA (draw-things-cli supports Klein 4B LoRA training [V], train on Base).
7. **Draw Things-format upscalers are not hosted on Hugging Face as far as could be verified.** They ship from Draw Things' CDN; HF has only PyTorch `.pth` versions (unusable in Draw Things without conversion). See §4 for the CDN commands (URL pattern **[I]**; sandbox got HTTP 403, so test on the Mac).
8. **Negative prompts:** BFL states FLUX.2 does not support them. On Distilled there is no unconditional branch. On Base with CFG > 1 a negative *may* have weak effect. Treat as unavailable; write positive-only prompts (§6).

---

## 1. Environment facts

### 1.1 Paths and flags
- Models dir [V]: `~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models` (override: `--models-dir` or env `DRAWTHINGS_MODELS_DIR`). LoRAs, upscalers and `custom_lora.json` live here.
- `draw-things-cli models list --downloaded-only` lists installed models [V]. CLI auto-downloads missing official models on first use [V] (Klein also pulls `qwen_3_4b_q8p.ckpt` text encoder + `flux_2_vae_f16.ckpt` [V]).
- Flags used by the template (`--model --prompt --width --height --steps --cfg --seed --output --config-json`) are the user's working set [I]. `--config-json` takes the same JSON as the app's *Copy Configuration* (camelCase keys: `guidanceScale`, `sampler`, `loras`, `upscaler`, …) [V]. Run `draw-things-cli generate --help` once to confirm flag names on your build.
- Sizes: multiples of 16, ≲2 MP recommended; Klein supports up to ~4 MP [V]. Leave `shift` at default (resolution-dependent shift is on by default [V]).

### 1.2 Variant test (is my f16 file distilled or base?) [H]
```bash
# Distilled-style run. Clean, sharp output at 4 steps/CFG 1 => distilled. Mushy/under-denoised => base.
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output '~/Dev/t2/variant_test.png' \
--prompt "a red ceramic teapot on a wooden table, soft window light, clean studio composition" \
--width 768 --height 768 --steps 4 --cfg 1.0 --seed 7 \
--config-json '{"sampler": 10}'
```
Recommendation: keep **both** official variants installed (48 GB is plenty): `flux_2_klein_4b_q8p.ckpt` for drafts, `flux_2_klein_base_4b_q8p.ckpt` for finals. All examples below use these official names; swap in your f16 file only after the test.

### 1.3 Variant rules
| | Distilled (`flux_2_klein_4b_*`) | Base (`flux_2_klein_base_4b_*`) |
|---|---|---|
| Steps / CFG [V] | 4 / 1.0 | 28–50 / ≈4.0 (16 steps already close to 50 per WikiQwen card) |
| Use for | drafts, thumbnails, flat vector/cut-paper looks, speed | **line art, painted textures, photoreal, all finals** |
| LoRAs trained on Base | transfer (confirmed for yarn-art LoRA) [V] | native |
| Negative prompt | none | weak at best |

---

## 2. Sampler numeric values (Draw Things `SamplerType`) [V — from `config.fbs`]

| # | Sampler | # | Sampler |
|---|---|---|---|
| 0 | DPM++ 2M Karras | 10 | **Euler A Trailing** |
| 1 | Euler A | 11 | DPM++ SDE Trailing |
| 2 | DDIM | 12 | DPM++ 2M AYS |
| 3 | PLMS | 13 | Euler A AYS |
| 4 | DPM++ SDE Karras | 14 | DPM++ SDE AYS |
| 5 | UniPC | 15 | **DPM++ 2M Trailing** |
| 6 | LCM | 16 | DDIM Trailing |
| 7 | Euler A Substep | 17 | **UniPC Trailing** |
| 8 | DPM++ SDE Substep | 18 | UniPC AYS |
| 9 | TCD | 19 | TCD Trailing |

Rules: flow models (Klein) want **Trailing** samplers [V — Draw Things wiki]. Default **10 (Euler A Trailing)** for painterly, photo, anime, distilled. For crisp line art/diagrams try **15 (DPM++ 2M Trailing)** (more deterministic; ancestral samplers add noise every step and don't converge) [H]. Fallback if lines wobble: 15 ↔ 17. Avoid 0–9 and 12–14 for Klein [H].

---

## 3. LoRAs

### 3.1 Compatible 4B LoRAs (all verified to exist, base = FLUX.2 klein **4B**, 2026-10-15)
| Key | HF repo | File | Trigger / prompt pattern | Weight | Best for | License |
|---|---|---|---|---|---|---|
| `numzoo` | `goumsss/numzoo-flux2-klein-lora` | `klein_numzoo_lora_f16.ckpt` (92 MB) | prefix `NUMZOO.` (animals × places; caption-only, no style words) | 0.7–0.9 [H] | **Kids' kawaii storybook animals, ages 2–7** | Apache-2.0 |
| `yarn` | `Barath/flux2-klein-yarn-art-lora` | `klein_yarn_art_lora_f16.ckpt` (final, step 1800; `…_000001200` is lighter) | prefix `Y4RN_ART,`; weak on plain objects (trained on creatures/figures) | 0.8–1.0 [H] | Craft/felt/yarn looks, kids, tricky anatomy | Apache-2.0 |
| `ohisee` | `noema-art/ohiseeflux-klein` | `klein_ohiseeflux_lora_f16.ckpt` | prefix `ohisee,` ; "digital drawing in a soft pastel style" | 0.8–1.0 (card: 25 steps, cfg 4.0, 1024²) | 2D pastel anime/digital drawing, YA storybook | Apache-2.0 |
| `dutchbaroque` | `noema-art/dutchbaroqueflux-klein` | `klein_dutchbaroqueflux_lora_f16.ckpt` | prefix `dutchbaroque,` | 0.8–1.0 | **Oil painting** (old-master, chiaroscuro, still life) | Apache-2.0 |
| `lightfantasy` | `giannisan/light-fantasy-flux2-klein-base-lora` | `klein_light_fantasy_lora_f16.ckpt` (15.7 MB) | `light_fantasy, a detailed fantasy painting of <scene>` | 0.8–1.0 [H] | Fantasy painting/digital drawing, teens | "other" — read card before commercial use |
| `wikiqwen` | `devon7y/WikiQwen-Illustrator` | `klein_wikiqwen_illustrator_lora_f16.ckpt` | prompt = plain description of what is visible; never name an art style; card: 512×384, 16 steps, CFG 4.0, **Base only** | 1.0 [H] | Non-fiction how-to/instructional illustration | **CC BY-NC-SA 4.0 (non-commercial; credit line required)** |


Edit-only 4B LoRAs (need an input image; not for text-to-image): `fal/flux-2-klein-4B-outpaint-lora` (`flux-outpaint-lora.ckpt`), `fal/flux-2-klein-4B-zoom-lora`, `xocialize/spritesheet-FLUX.2-klein-4B-lora`, `HaaDeej/Flux2-3500K` (B&W colorize).
**Incompatible (9B; would be silently ignored):** `artificialguybr/COLORINGBOOK-REDMOND-FLUXKLEIN9B`, `artificialguybr/LineartAnime-Redmond-Flux9BKlein`, `neonforestmist/flux-storybook-anime-lora`, `SOLRICKS/Flux2-Klein-9B-Realistic-Detail`, everything in `Alex995647/loras-flux2-klein-9b`, `joyfox/FLUX.2-klein-AC-Style-LORA`.

**Always verify a LoRA is applied** (silent drop otherwise) [V method]:
```bash
M=flux_2_klein_base_4b_q8p.ckpt; P="a small red fox sitting in a meadow"
draw-things-cli generate --model $M --prompt "$P" --width 512 --height 512 --steps 12 --cfg 4.0 --seed 5 --output '~/Dev/t2/lora_off.png'
draw-things-cli generate --model $M --prompt "NUMZOO. $P" --width 512 --height 512 --steps 12 --cfg 4.0 --seed 5 --output '~/Dev/t2/lora_on.png' \
  --config-json '{"loras":[{"file":"numzoo_klein_lora_f16.ckpt","weight":0.8,"mode":"all"}]}'
python3 -c "from PIL import Image,ImageChops,ImageStat;import os;a,b=[Image.open(os.path.expanduser(p)).convert('RGB') for p in ('~/Dev/t2/lora_off.png','~/Dev/t2/lora_on.png')];print('mean pixel diff',sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3)"
# diff ≈ 0.0 => LoRA ignored (wrong version / not registered). Expect tens when applied.
```

### 3.2 LoRA rules of thumb
- Stack ≤2 LoRAs; style LoRA 0.7–1.0, never stack two *style* LoRAs (they fight) [H].
- Trigger word goes **first** in the prompt (word order = weight). Without the trigger most of these LoRAs stay inert (yarn card confirms).
- If a LoRA warps anatomy or overpowers the prompt: lower weight by 0.15 before changing the prompt.
- Distilled + Base-trained LoRA: works, but use 4 steps/CFG 1.0 and raise weight ~+0.1 [H].
- Train your own (Base, 20–60 captioned images, content-only captions + trigger) for line art / mandala / watercolor — the gap in §0.6.

---

## 4. Upscalers

Draw Things built-in upscalers [V — `UpscalerZoo.swift`]; use the filename in `--config-json` as `"upscaler"`. Scale is read from the model spec; **confirm the CLI applied it by checking output pixel dimensions** (not verified that the CLI honours `upscaler` — if the size is unchanged, upscale in the Draw Things app or via a second img2img/upscale pass).

| File | Scale | Best for | License note |
|---|---|---|---|
| `realesrgan_x2plus_f16.ckpt` | 2× | **default general, illustration, photo, painting** | BSD-3 (commercial OK) |
| `realesrgan_x4plus_anime_6b_f16.ckpt` | 4× | photo/painting when 4× needed | BSD-3 |
| `realesrgan_x4plus_anime_6b_f16.ckpt` | 4× (6 blocks, fast) | **line art, coloring pages, anime, flat color, diagrams** | BSD-3 |
| `esrgan_4x_universal_upscaler_v2_sharp_f16.ckpt` | 4× | extra crispness (can over-sharpen) | unverified |
| `remacri_4x_f16.ckpt` | 4× | painterly/photo texture | CC-BY-NC-SA (community card) → non-commercial |
| `4x_ultrasharp_f16.ckpt` | 4× | sharp AI art; **can halo on line art & skin** | CC-BY-NC-SA → non-commercial |

Defaults: line art → `realesrgan_x4plus_anime_6b_f16.ckpt`; everything else → `realesrgan_x2plus_f16.ckpt`; avoid UltraSharp/Remacri when the work is commercial.
Print math: 8.5×11 in @300 DPI = 2550×3300 px. Generate 1216×1568 (1.9 MP) → ×2 = 2432×3136 (≈286 DPI) or ×4 (anime-6B) then downsample.

Download (Draw Things format; **not on HF**). CDN pattern `https://static.libnnc.org/<file>` [I — JoyFusionAI's HF mirror documents byte-identical files from this host]. Easiest alternative: pick the upscaler once in the Draw Things app; it downloads it. SHA-256 values are from source [V]:
```bash
cd ~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models
for f in realesrgan_x2plus_f16.ckpt realesrgan_x4plus_anime_6b_f16.ckpt realesrgan_x4plus_anime_6b_f16.ckpt; do
  [ -f "$f" ] || curl -fL -o "$f" "https://static.libnnc.org/$f"
done
shasum -a 256 realesrgan_x2plus_f16.ckpt realesrgan_x4plus_anime_6b_f16.ckpt realesrgan_x4plus_anime_6b_f16.ckpt
# expected:
# 98ce77870b5ca059ec004fe8572182dc67ac8d6a2bba8a938df0ba44fbaccc66  realesrgan_x2plus_f16.ckpt
# 3db00086d999e590e313dbf45f0701cdf0e3bca3a66a201a3078423501cb58fd  realesrgan_x4plus_anime_6b_f16.ckpt
# 3ad598b21e888590d1bd239dc55675de11b245c691728b56859aa05038c69099  realesrgan_x4plus_anime_6b_f16.ckpt
# (non-commercial extras) remacri_4x_f16.ckpt 88d7ae8e…b70671 · 4x_ultrasharp_f16.ckpt c8e9a1ee…a9f0ec
```
HF `.pth` sources (reference only, NOT loadable by Draw Things): `uwg/upscaler` → `ESRGAN/4x-UltraSharp.pth`; `easygoing0114/AI_upscalers` (RealESRGAN_x4plus, anime_6B, Remacri).

---

## 5. Settings matrix (starting points; [H] unless noted)

Variant D = distilled, B = base. Sampler shown as name (number).

| Category | Var | Steps | CFG | Sampler | Size (WxH) | LoRA (weight) | Upscaler |
|---|---|---|---|---|---|---|---|
| Kids illustration 2–4 | B | 28 | 4.0 | Euler A Trailing (10) | 1024×768 | numzoo (0.8) or none | realesrgan_x2plus |
| Kids illustration 5–7 | B | 28 | 4.0 | 10 | 1024×768 | numzoo / yarn (0.8–0.9) | x2plus |
| Kids/YA storybook 8–10 | B | 25–28 | 4.0 | 10 | 1024×1024 | ohisee (0.85) / none | x2plus |
| Coloring kids 2–4 | B | 32 | 4.0 | DPM++ 2M Trailing (15) | 1024×1280 | none | x4plus_anime_6b |
| Coloring kids 5–7 | B | 32 | 4.0 | 15 | 1024×1280 | none | x4plus_anime_6b |
| Coloring kids 8–10 | B | 34 | 4.0 | 15 | 1216×1568 | none | x4plus_anime_6b |
| Adult coloring / line art | B | 36–40 | 4.0–4.5 | 15 | 1216×1568 | none | x4plus_anime_6b |
| Mandala (adult) | B | 40 | 4.0 | 15 | 1408×1408 | none | x2plus |
| Non-fiction kids/teens | B | 16–32 | 4.0 | 15 (diagram) / 10 | 512×384 (wikiqwen) or 1280×960 | wikiqwen (1.0, NC) or none | anime_6b / x2plus |
| Pencil/artistic sketch | B | 30 | 4.0 | 15 | 1152×896 | none | x2plus |
| Oil painting | B | 28 | 4.0 | 10 | 1024×1024 | dutchbaroque (0.85) / none | x2plus |
| Watercolor | B | 28 | 4.0 | 10 | 1152×896 | none | x2plus |
| 2D anime | B | 25 | 4.0 | 10 | 896×1152 | ohisee (0.9) | x4plus_anime_6b |
| 3D anime / toy render | B | 30 | 4.0 | 10 | 1024×1280 | none | x2plus |
| Digital drawing / fantasy | B | 28 | 4.0 | 10 | 1280×768 | lightfantasy (0.9) | x2plus |
| Photography / photoreal | B | 30 | 3.5 | 10 | 1024×1280 | none | x2plus (never UltraSharp on skin) |
| Drafts / thumbnails (any) | D | 4 | 1.0 | 10 | half final size | same LoRA as final | none |

Workflow [H]: draft 4 seeds on D (4 steps) → pick composition → finish on B. Composition is **not guaranteed** to carry over between D and B with the same seed; for exact reproduction draft on B at 12–16 steps and finish the same seed at 30–40.
Steps: below 24 on B loses edge integrity in line art; above ~40 gives diminishing returns [H]. Seeds: always pass `--seed` and log it.

---

## 6. Prompting without negative prompts

### 6.1 Contract (Klein reads sentences through a Qwen3 4B encoder; derived from the `klein-kids-art` skill [V])
Slot order, most important first (word order is the weighting mechanism):
`SUBJECT(+count) → ACTION → EXPRESSION → IDENTITY(character sheet, verbatim) → STYLE SIGNATURE(verbatim) → DETAIL LEVEL → SCENE/props → LIGHT → COLOUR(hex on named objects) → COMPOSITION/framing → TEXT(optional)`.
- Length: 45–90 words illustration, 40–85 line art. Under 30 words = seed-to-seed swing; over ~110 = tail ignored.
- Never: `(word:1.3)`, `BREAK`, `masterpiece/8k/best quality`, negations, `<lora:>` in text.
- LoRA trigger first; paste the style-signature block **verbatim** across a set.
- Hex codes work only when attached to an object: "the scarf is color #5B8E7D". ≤5 per image.
- Text in image: one quoted string ≤3 words, else leave empty space and typeset later (title/labels).
- Subject count by age: 2–4 → 1 subject, ≤2 props; 5–7 → ≤2 subjects, ≤3 props; 8–10 → ≤3 subjects, ≤5 props. Hands/feet are weak: paws, mittens, hands behind back, chunky shapes.
- Camera/lens words ("85mm, f/2") only for photoreal; they drag illustration toward photos.
- Kids' images: invented characters only; no real-child likeness, no photoreal children, no franchise characters.

### 6.2 Negation → positive conversion
| Want to avoid | Write instead |
|---|---|
| "no background" | "flat pure white background" |
| "no shading / no gray" | "uniform black outlines only, flat white fill inside every shape" |
| "no color" | "monochrome black ink on white" |
| "no text" | omit text entirely; "wordless illustration" only if needed |
| "not scary" | "friendly, rounded shapes, gentle smile, warm light" |
| "no extra fingers" | "paws tucked behind its back" / "holding a large balloon" |
| "no blur" | "crisp focus across the whole frame" |
| "not cropped" | "full body visible head to toe, wide margin around the edges" |
| "no clutter" | "single centred subject with a few simple props" |
| "no modern objects" | name the era's objects explicitly |
| "not photoreal" | name the medium (gouache, cut paper, graphite) |

### 6.3 Medium signature blocks (paste verbatim per set)
- Coloring page: `clean black-and-white coloring book line art, thick uniform black outlines, every shape fully closed, flat pure white background, large open areas left blank ready for colouring`
- Age 2–4 detail: `very simple clear shapes, huge friendly features, lots of empty space` · 5–7: `simple clear shapes with a few playful details` · 8–10: `richer decorative detail with patterned areas`
- Mandala: `twelve-fold radial symmetry … concentric rings … every shape fully closed`
- Watercolor: `loose wet-on-wet watercolor, soft pigment blooms, translucent layered washes, visible cold-press paper texture, unpainted white paper at the edges`
- Pencil: `graphite pencil sketch, visible hatching and cross-hatching, soft smudged tonal gradients, cream sketchbook paper with fine grain`
- Oil: `rich impasto brushwork, deep chiaroscuro lighting, warm earth palette`
- Photo: `photograph, 85mm lens at f/2.0, shallow depth of field, natural film-like colour, warm low sun`
- 3D toy: `cel-shaded 3D render with smooth soft shading and crisp outlines`

### 6.4 Failure → fix
| Symptom | Cause | Fix |
|---|---|---|
| Varying quality per seed | prompt <45 words | fill all slots |
| Gray shading in coloring page | color/light word leaked | strip colour/shadow/texture words; keep "even flat lighting" |
| Broken/doubled outlines | too few steps, wrong variant | Base, ≥32 steps, sampler 15, "every shape fully closed" |
| Fused characters / extra limbs | too many subjects | cut to age-band limit |
| LoRA has no effect | version mismatch or unregistered | §3.1 verify script |
| Washed-out/plasticky | distilled on painterly look | finish on Base |
| Gibberish text | long/multiple strings | ≤3 words or typeset later |
| Oversaturated/burnt | CFG too high | CFG 3.5–4.0 |
| Halos on lines after upscale | UltraSharp | use anime_6b |

---

## 7. Worked examples (each command is self-contained; replace names if `ls` shows different LoRA filenames)

### EX-01 Kids illustration, age 2–4 — kawaii animal (numzoo LoRA)
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_kids_2-4_kitten.png' \
--prompt "NUMZOO. A round orange kitten sitting upright, smiling warmly with big shiny eyes, soft kawaii storybook illustration, very simple clear shapes with huge friendly features, a sunny meadow with two white daisies, warm morning light, the kitten's scarf is color #5B8E7D, soft pastel palette, subject centred in the near foreground with generous space around it, whole body inside the frame." \
--width 1024 --height 768 --steps 28 --cfg 4.0 --seed 2101 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"loras": [
    {"file": "numzoo_klein_lora_f16.ckpt", "weight": 0.8, "mode": "all"}
  ]
}'
```
Why: 1 subject (age 2–4); trigger first; hex tied to one object; base+cfg 4.0 for soft texture; Trailing sampler for flow model; 2× general upscaler.

### EX-02 Kids illustration, age 5–7 — yarn/felt craft (yarn LoRA)
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_kids_5-7_fox_yarn.png' \
--prompt "Y4RN_ART, a pair of friendly fox cubs sitting side by side, one holding a small red mitten, both smiling gently, felted yarn picture book art with visible stitches and fuzzy fibre texture, simple clear shapes with a few playful details, a snowy pine forest with three small stars above, soft blue evening light, one fox is color #D9732B and the other fox is color #F2E3C6, warm cozy palette, both foxes fully visible and centred with space around them." \
--width 1024 --height 768 --steps 28 --cfg 4.0 --seed 2102 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"loras": [
    {"file": "klein4b_yarn_art_lora_v1_lora_f16.ckpt", "weight": 0.9, "mode": "all"}
  ]
}'
```
Why: 2 subjects (age 5–7); creatures match the LoRA's training data; mitten dodges hand anatomy; yarn texture survives the 2× upscaler.

### EX-03 Storybook, age 8–10 — pastel digital storybook (ohisee LoRA)
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_storybook_8-10_explorer.png' \
--prompt "ohisee, a young explorer with short teal hair and a yellow raincoat crouching beside a glowing blue mushroom, curious with wide eyes, soft pastel digital storybook drawing with gentle painterly linework, richer decorative detail, a mossy forest clearing with two ferns and a small lantern, warm dusk light with soft shadows, the raincoat is color #F2C94C and the mushroom is color #5BC0EB, three tiny fireflies hovering nearby, subject in the near foreground with a softly blurred background." \
--width 1024 --height 1024 --steps 25 --cfg 4.0 --seed 2103 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"loras": [
    {"file": "ohiseeflux_klein_lora_f16.ckpt", "weight": 0.85, "mode": "all"}
  ]
}'
```
Why: LoRA card settings (25 steps, cfg 4.0, 1024²); 5 props allowed at 8–10; invented character.

### EX-04 Coloring page, kids 2–4 (no LoRA)
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_coloring_2-4_cat.png' \
--prompt "A round fluffy cat sitting upright with its tail curled around its paws, with a warm friendly expression, clean black-and-white coloring book line art, very thick uniform black outlines, every shape fully closed, flat pure white background, huge open areas left blank ready for colouring, printable toddler coloring page, very simple clear shapes, one simple rug shape beneath the cat, even flat lighting, single centred subject, whole subject inside the frame, wide white margin around the edges." \
--width 1024 --height 1280 --steps 32 --cfg 4.0 --seed 2104 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt"
}'
```
Why: Base needed for closed outlines; sampler 15 for crisp edges; anime-6B upscaler keeps lines clean; every negation converted to positives.

### EX-05 Coloring page, kids 5–7
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_coloring_5-7_bunny_turtle.png' \
--prompt "A smiling bunny and a small turtle sitting side by side beside a big sunflower, both with happy expressions, clean black-and-white coloring book line art, thick uniform black outlines, every shape fully closed, flat pure white background, large open areas left blank ready for colouring, printable children's coloring page, simple clear shapes with a few playful details, a small garden path and three flowers, even flat lighting, two subjects centred together, everything inside the frame, wide white margin around the edges." \
--width 1024 --height 1280 --steps 32 --cfg 4.0 --seed 2105 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt"
}'
```
Why: two subjects, three props (age band); large blank areas for developing motor control.

### EX-06 Coloring page, kids 8–10
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_coloring_8-10_otters.png' \
--prompt "Three playful otters floating on their backs in a winding river, smiling happily with their paws linked together, clean black-and-white coloring book line art, medium-weight uniform black outlines, every shape fully closed, flat pure white background, richer decorative detail with patterned ripples, leaf shapes and small pebbles as colourable areas, printable children's coloring page, five lily pads and a few reeds along the banks, even flat lighting, group centred in the frame, whole scene inside the frame, wide white margin around the edges." \
--width 1216 --height 1568 --steps 34 --cfg 4.0 --seed 2106 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt"
}'
```
Why: three subjects/five props allowed; medium line weight; larger canvas for small areas; linked paws avoid finger rendering.

### EX-07 Adult mandala
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_mandala_adult_lotus.png' \
--prompt "A circular mandala with twelve-fold radial symmetry, a central lotus flower surrounded by concentric rings of petals, feathers, paisley teardrops and interlocking geometric lace, clean black-and-white coloring book line art, fine uniform black outlines, every shape fully closed, flat pure white background, intricate adult coloring page with small enclosed areas of varied sizes, perfectly centred circular composition, whole mandala inside the frame, wide white margin around the edges." \
--width 1408 --height 1408 --steps 40 --cfg 4.0 --seed 2107 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x2plus_f16.ckpt"
}'
```
Why: 40 steps for fine-detail convergence; ~2 MP square; 2× (not 4×) keeps size manageable (2816 px ≈ 9.4 in @300 DPI); explicit symmetry count gives structure.

### EX-08 Adult coloring page (your owl template, corrected)
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_coloring_adult_owl.png' \
--prompt "A wise owl perched on a crescent moon with its wings partly open, calm watchful expression, clean black-and-white coloring book line art, fine uniform black outlines, every shape fully closed, flat pure white background, intricate adult coloring page with feather patterns, mandala-style circles and floral swirls filling the wings and the moon, stars of different sizes in the sky, even flat lighting, single centred subject, whole subject inside the frame, wide white margin around the edges." \
--width 1216 --height 1568 --steps 38 --cfg 4.0 --seed 2108 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt"
}'
```
Why: cfg 4.0 (not 5.5) avoids burnt/over-contrasted lines; page-ratio canvas; owl + moon patterns give colourable regions.

### EX-09 Non-fiction for kids — how-to illustration (WikiQwen LoRA, non-commercial)
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_nonfiction_kids_watering.png' \
--prompt "A child gently pouring water from a small green watering can onto a seedling planted in a clay pot on a sunny windowsill, a second pot with a taller plant beside it, a closed window behind them with a few clouds visible outside." \
--width 512 --height 384 --steps 16 --cfg 4.0 --seed 2109 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"loras": [
    {"file": "wikiqwen_illustrator_lora_f16.ckpt", "weight": 1.0, "mode": "all"}
  ]
}'
```
Why: LoRA card settings (512×384, 16 steps, cfg 4.0, Base); describe visible content only, never the style; 4× anime-6B → 2048×1536. **License CC BY-NC-SA 4.0 — credit line required, not for commercial books.**

### EX-10 Non-fiction for teens — diagram-style (commercial-safe, no LoRA)
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_nonfiction_teen_volcano.png' \
--prompt "A cutaway illustration of a volcano showing a magma chamber, a central vent and layers of ash and lava, clean flat vector style with crisp dark outlines and a limited palette, the magma is color #E4572E and the rock layers alternate between #8D6E63 and #5D4037, a few ash clouds rising above the crater, even flat lighting, side view centred in the frame with clear empty space beside each part for labels added later." \
--width 1280 --height 960 --steps 32 --cfg 4.0 --seed 2110 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt"
}'
```
Why: sampler 15 + anime-6B suit crisp flat vector; labels are typeset in layout software (model text degrades with length).

### EX-11 Pencil / artistic sketch
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_pencil_lighthouse.png' \
--prompt "A graphite pencil sketch of an old lighthouse on a rocky headland, visible hatching and cross-hatching for shading, soft smudged tonal gradients, light construction lines left visible, on cream sketchbook paper with fine paper grain, a few gulls in the sky, soft overcast daylight, three-quarter view with the lighthouse in the left third and a generous paper margin around the drawing." \
--width 1152 --height 896 --steps 30 --cfg 4.0 --seed 2111 \
--config-json '{
"sampler": 15,
"upscaler": "realesrgan_x2plus_f16.ckpt"
}'
```
Why: hatching vocabulary + paper grain; base for fine line texture; 15 keeps strokes deterministic.

### EX-12 Oil painting (dutchbaroque LoRA)
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_oil_still_life.png' \
--prompt "dutchbaroque, an oil painting still life of a pewter jug, a halved lemon with a curling peel and a bunch of purple grapes on a dark wooden table, rich impasto brushwork, deep chiaroscuro lighting from a window on the left, warm earth palette with the lemon in color #E8C547, objects centred with a dark softly lit background." \
--width 1024 --height 1024 --steps 28 --cfg 4.0 --seed 2112 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"loras": [
    {"file": "klein_dutchbaroqueflux_lora_f16.ckpt", "weight": 0.85, "mode": "all"}
  ]
}'
```
Why: LoRA supplies old-master palette/lighting; for other oil looks (impasto landscape, modern) drop the LoRA and keep the medium block.

### EX-13 Watercolor (prompt-only)
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_watercolor_fox.png' \
--prompt "A loose wet-on-wet watercolor painting of a red fox sleeping curled up under a birch tree in autumn, soft pigment blooms and granulation, translucent layered washes, visible cold-press paper texture, unpainted white paper left around the edges, warm ochre and rust palette with the fox in color #C8553D, soft diffused morning light, subject slightly left of centre with a generous paper margin." \
--width 1152 --height 896 --steps 28 --cfg 4.0 --seed 2113 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x2plus_f16.ckpt"
}'
```
Why: no verified 4B watercolor LoRA; physical-process words (blooms, granulation, paper) carry the style; Euler A Trailing's looseness suits washes.

### EX-14 2D anime (ohisee LoRA)
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_anime2d_swordswoman.png' \
--prompt "ohisee, a digital drawing of a young swordswoman with long silver hair and a crimson scarf standing on a rooftop at sunset, calm confident expression, soft pastel anime illustration with clean linework and gentle gradients, a distant city skyline with two glowing windows, warm orange rim light, the scarf is color #C1272D and the sky is a gradient from #FFB88C to #8E7DBE, full body visible and centred in a vertical frame." \
--width 896 --height 1152 --steps 25 --cfg 4.0 --seed 2114 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt",
"loras": [
    {"file": "ohiseeflux_klein_lora_f16.ckpt", "weight": 0.9, "mode": "all"}
  ]
}'
```
Why: vertical canvas for a standing figure; gradient hex ends named; anime-6B upscaler tuned for anime.

### EX-15 3D anime / toy render (prompt-only)
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_anime3d_mechanic.png' \
--prompt "A 3D rendered anime-style character, a cheerful young mechanic with orange goggles on her forehead and a blue jumpsuit, smiling and resting a large wrench on her shoulder, cel-shaded 3D render with smooth soft shading and crisp outlines, a tidy workshop with a toolbox and a hovering drone, soft studio lighting with a warm rim light, the jumpsuit is color #3A6EA5 and the goggles are color #F28C28, full body visible and centred." \
--width 1024 --height 1280 --steps 30 --cfg 4.0 --seed 2115 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x2plus_f16.ckpt"
}'
```
Why: this look has the highest reject rate; Base only; wrench resting on the shoulder avoids a gripping-hand close-up.

### EX-16 Digital drawing — fantasy painting (light_fantasy LoRA)
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_digital_fantasy_castle.png' \
--prompt "light_fantasy, a detailed fantasy painting of a lighthouse castle on a cliff above a glowing sea, wildflowers in the foreground and a winding stone stair leading up to the gate, soft golden light breaking through low clouds, a palette of teal water and warm sandstone walls, wide landscape composition with the castle in the right third." \
--width 1280 --height 768 --steps 28 --cfg 4.0 --seed 2116 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x2plus_f16.ckpt",
"loras": [
    {"file": "light_fantasy_klein_lora_f16.ckpt", "weight": 0.9, "mode": "all"}
  ]
}'
```
Why: LoRA card prompt pattern kept intact; landscape ratio. Check the repo license before commercial use.

### EX-17 Photography (prompt-only, Base)
```bash
draw-things-cli generate \
--model flux_2_klein_base_4b_q8p.ckpt \
--output '~/Dev/t2/klein_photo_fisherman.png' \
--prompt "A photograph of an elderly fisherman mending a blue net on a wooden pier at golden hour, deep smile lines and a weathered wool cap, shot on an 85mm lens at f/2.0 with shallow depth of field, natural film-like colour, warm low sun from the left, a moored wooden boat and a coil of rope beside him, medium shot with the fisherman in the right third of the frame." \
--width 1024 --height 1280 --steps 30 --cfg 3.5 --seed 2117 \
--config-json '{
"sampler": 10,
"upscaler": "realesrgan_x2plus_f16.ckpt"
}'
```
Why: lens language is valid only here; CFG 3.5 keeps skin natural; x2plus (not UltraSharp) avoids plastic skin. Adult/animal/landscape subjects only — no photoreal children.

### EX-18 Draft pass (Distilled, 4 seeds) then finish on Base
```bash
for s in 301 302 303 304; do
draw-things-cli generate \
--model flux_2_klein_4b_q8p.ckpt \
--output "~/Dev/t2/draft_otter_$s.png" \
--prompt "NUMZOO. A smiling otter floating on its back in a calm river holding a small yellow flower, soft kawaii storybook illustration, simple clear shapes with a few playful details, a green riverbank with two lily pads, warm afternoon light, the flower is color #F2C94C, soft pastel palette, subject centred with generous space around it." \
--width 768 --height 512 --steps 4 --cfg 1.0 --seed $s \
--config-json '{
"sampler": 10,
"loras": [
    {"file": "numzoo_klein_lora_f16.ckpt", "weight": 0.9, "mode": "all"}
  ]
}'
done
```
Then re-run the chosen prompt on `flux_2_klein_base_4b_q8p.ckpt` with `--steps 28 --cfg 4.0 --width 1024 --height 768` (see EX-01 config). Why: 4 steps/CFG 1 is the distilled reference setting; sub-second drafts; same LoRA +0.1 weight on distilled.

---

## 8. Recommendation-engine layer

### 8.1 Machine-readable presets
```json
{
  "defaults": {"base_model": "flux_2_klein_base_4b_q8p.ckpt", "draft_model": "flux_2_klein_4b_q8p.ckpt", "cfg_base": 4.0, "cfg_distilled": 1.0, "steps_distilled": 4},
  "samplers": {"euler_a_trailing": 10, "dpmpp_2m_trailing": 15, "unipc_trailing": 17, "dpmpp_sde_trailing": 11},
  "presets": {
    "kids_illustration_2_4":  {"steps": 28, "sampler": 10, "size": [1024, 768],  "loras": [["numzoo_klein_lora_f16.ckpt", 0.8]], "upscaler": "realesrgan_x2plus_f16.ckpt", "subjects_max": 1, "commercial_ok": true},
    "kids_illustration_5_7":  {"steps": 28, "sampler": 10, "size": [1024, 768],  "loras": [["numzoo_klein_lora_f16.ckpt", 0.8]], "upscaler": "realesrgan_x2plus_f16.ckpt", "subjects_max": 2, "commercial_ok": true},
    "storybook_8_10":         {"steps": 25, "sampler": 10, "size": [1024, 1024], "loras": [["ohiseeflux_klein_lora_f16.ckpt", 0.85]], "upscaler": "realesrgan_x2plus_f16.ckpt", "subjects_max": 3, "commercial_ok": true},
    "craft_yarn":             {"steps": 28, "sampler": 10, "size": [1024, 768],  "loras": [["klein4b_yarn_art_lora_v1_lora_f16.ckpt", 0.9]], "upscaler": "realesrgan_x2plus_f16.ckpt", "commercial_ok": true},
    "coloring_2_4":           {"steps": 32, "sampler": 15, "size": [1024, 1280], "loras": [], "upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt", "subjects_max": 1, "commercial_ok": true},
    "coloring_5_7":           {"steps": 32, "sampler": 15, "size": [1024, 1280], "loras": [], "upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt", "subjects_max": 2, "commercial_ok": true},
    "coloring_8_10":          {"steps": 34, "sampler": 15, "size": [1216, 1568], "loras": [], "upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt", "subjects_max": 3, "commercial_ok": true},
    "coloring_adult":         {"steps": 38, "sampler": 15, "size": [1216, 1568], "loras": [], "upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt", "commercial_ok": true},
    "mandala_adult":          {"steps": 40, "sampler": 15, "size": [1408, 1408], "loras": [], "upscaler": "realesrgan_x2plus_f16.ckpt", "commercial_ok": true},
    "nonfiction_howto_nc":    {"steps": 16, "sampler": 10, "size": [512, 384],   "loras": [["wikiqwen_illustrator_lora_f16.ckpt", 1.0]], "upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt", "commercial_ok": false},
    "nonfiction_diagram":     {"steps": 32, "sampler": 15, "size": [1280, 960],  "loras": [], "upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt", "commercial_ok": true},
    "pencil_sketch":          {"steps": 30, "sampler": 15, "size": [1152, 896],  "loras": [], "upscaler": "realesrgan_x2plus_f16.ckpt", "commercial_ok": true},
    "oil_painting":           {"steps": 28, "sampler": 10, "size": [1024, 1024], "loras": [["klein_dutchbaroqueflux_lora_f16.ckpt", 0.85]], "upscaler": "realesrgan_x2plus_f16.ckpt", "commercial_ok": true},
    "watercolor":             {"steps": 28, "sampler": 10, "size": [1152, 896],  "loras": [], "upscaler": "realesrgan_x2plus_f16.ckpt", "commercial_ok": true},
    "anime_2d":               {"steps": 25, "sampler": 10, "size": [896, 1152],  "loras": [["ohiseeflux_klein_lora_f16.ckpt", 0.9]], "upscaler": "realesrgan_x4plus_anime_6b_f16.ckpt", "commercial_ok": true},
    "anime_3d":               {"steps": 30, "sampler": 10, "size": [1024, 1280], "loras": [], "upscaler": "realesrgan_x2plus_f16.ckpt", "commercial_ok": true},
    "fantasy_digital":        {"steps": 28, "sampler": 10, "size": [1280, 768],  "loras": [["light_fantasy_klein_lora_f16.ckpt", 0.9]], "upscaler": "realesrgan_x2plus_f16.ckpt", "commercial_ok": "check_license"},
    "photo":                  {"steps": 30, "sampler": 10, "size": [1024, 1280], "loras": [], "upscaler": "realesrgan_x2plus_f16.ckpt", "cfg": 3.5, "commercial_ok": true},
    "draft_any":              {"steps": 4,  "sampler": 10, "cfg": 1.0, "model": "flux_2_klein_4b_q8p.ckpt", "loras": "same as final (+0.1 weight)", "upscaler": null}
  }
}
```

#### 8.1.1 WikiQwen-Illustrator 4B License

**What WikiQwen-Illustrator-4B is.** It's a style LoRA for FLUX.2 [klein] base 4B, the same model family you already use. It was trained on about 588k wikiHow step illustrations licensed CC BY-NC-SA 3.0. The LoRA and the pictures it makes are released as CC BY-NC-SA 4.0, so the restriction comes from the training data, not the base model. The 7B version in its demo Space is built on Qwen-Image-2.1, which is also non-commercial.

**What this means for you:**

- **Don't retrain on that dataset.** A LoRA you train on wikiHow's illustrations would carry the same non-commercial and share-alike terms.
- **You lose only the style.** Klein 4B is Apache 2.0, so the base model is fine. What you can't use commercially is this particular LoRA's look.
- **The model card is only a preview.** It's a checkpoint at 8,000 of 18,000 training steps, so the final weights may change.

**Ways to get a similar look commercially:**

1. **Prompt the style directly.** Try something like "flat vector how-to step illustration, clean outlines, bright friendly colors, simple white background, hands only, no text", then describe the scene in one to three sentences. The model card says that format works well. Keep any words out of the images, because text inside pictures comes out garbled. Add lettering in your layout tool instead.
2. **Use Qwen-Image-Edit-2511 or Klein 4B's editing mode** for consistency. Generate one good character or object, then use it as a reference for each following step.
3. **Train your own LoRA on Klein 4B Base (Apache 2.0)**, using images you can legally train on. Good sources are your own drawings, commissioned art, public-domain or CC0 material, or a curated set generated with Apache-licensed models. Avoid any CC-NC or share-alike data. Check Draw Things' LoRA training for Klein support yourself. I haven't verified that, and training on 48 GB of unified memory should be feasible.

One more point: a LoRA trained on the base model may not behave identically on the distilled `flux_2_klein_4b_q8p.ckpt` you're running. Test your LoRA on that checkpoint, or switch to the Klein 4B Base file.

### 8.2 Decision rules
1. **Detect intent → preset**: coloring/line art/mandala → `coloring_*`/`mandala`; "informative/educational/diagram/how-to" → `nonfiction_*`; named medium (oil, watercolor, pencil) → matching preset; "anime/manga" → `anime_2d` (3D/render → `anime_3d`); "photo/realistic" → `photo`; otherwise kids illustration by age.
2. **Age band** decides subject count, prop count, line weight, detail phrase (§6.1). If age is unspecified, ask once; default 5–7.
3. **Commercial use unspecified → assume commercial.** Exclude `wikiqwen` (CC BY-NC-SA), `remacri`, `4x_ultrasharp` (NC). Flag `light_fantasy` (license "other"). Klein 4B itself and the Apache-2.0 LoRAs are fine.
4. **Print vs screen**: print → 300 DPI math (§4), use anime-6B for line art; screen → 2× upscaler is enough.
5. **Variant**: drafts/thumbnails/vector-flat → Distilled; line art, painted textures, photoreal, finals → Base.
6. **LoRA availability**: if the requested look has no 4B LoRA (coloring, watercolor, mandala, photoreal), use prompt-only on Base — never substitute a 9B LoRA.
7. **Uncertainty handling**: ambiguous style → generate 2 variants (e.g. sampler 10 vs 15, or LoRA 0.7 vs 0.9) with the same seed and compare; log seed/prompt/settings.
8. **Output QC (before presenting)**: cropped limbs, fused subjects, broken/doubled lines, gray fill in line art, gibberish text, faces that read distressed, any photoreal child → re-prompt (§6.4) rather than reroll.
9. **Stop conditions**: LoRA verify diff ≈ 0 → fix install before generating; output size unchanged after `upscaler` → upscaling not applied by CLI.
10. **Safety for children's content**: invented characters only; no real-child likeness, no photoreal children, no franchise characters, nothing frightening or sexualised.

### 8.3 Unverified items (agent: check before relying)
- Exact CLI flag names beyond the template (`--help`); whether `--negative` exists (seen in one third-party script) — irrelevant for Klein anyway.
- Whether the CLI applies the `upscaler` key post-generation.
- Exact Klein-4B `--version` string for `dtlora.py`; app-imported LoRA filenames.
- CDN URL pattern `static.libnnc.org/<file>` (sandbox got 403).
- Identity of `flux_2_klein_4b_q8p.ckpt` (distilled vs base).
- All step/CFG/weight values tagged [H]; no throughput benchmarks were run on the M4.
