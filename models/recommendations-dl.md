# Commands for downloading the LoRAs

I'll verify the exact Hugging Face repos and filenames before giving you commands, since I don't want to hand you guessed repo IDs.

The searches confirmed most repos. I'll fetch the file listings for the ones where the exact filename wasn't visible.

Here are the commands. I checked each repo's file listing, so every command pulls an exact file, except the pencil LoRA, which uses a pattern because I couldn't see its filename.

```bash
pip install -U "huggingface_hub[cli]"        # provides the `hf` command (older versions: `huggingface-cli download`)
export LORA_DIR="$HOME/ComfyUI/models/loras"  # change to your LoRA folder
mkdir -p "$LORA_DIR"

# Kids reading book illustrations
hf download artificialguybr/StoryBookRedmond-V2 StorybookRedmondV2-KidsBook-KidsRedmAF.safetensors --local-dir "$LORA_DIR"

# Kids and adult coloring books, line art, mandala (see note below)
hf download artificialguybr/ColoringBookRedmond-V2 ColoringBookRedmond-ColoringBook-ColoringBookAF.safetensors --local-dir "$LORA_DIR"

# Manga/anime line art (Animagine slot)
hf download artificialguybr/LineAniRedmond-LinearMangaSDXL-V2 LineAniRedmondV2-Lineart-LineAniAF.safetensors --local-dir "$LORA_DIR"

# Detail Tweaker XL (third-party mirror)
hf download highscoregames12018/add-detail-xl add-detail-xl.safetensors --local-dir "$LORA_DIR"

# Film/grain slot in photography
hf download artificialguybr/analogredmond-v2 AnalogRedmondV2-Analog-AnalogRedmAF.safetensors --local-dir "$LORA_DIR"

# 3D renders
hf download goofyai/3d_render_style_xl 3d_render_style_xl.safetensors --local-dir "$LORA_DIR"
hf download ntc-ai/SDXL-LoRA-slider.pixar-style pixar-style.safetensors --local-dir "$LORA_DIR"

# Oil painting (filenames contain spaces, so rename them)
hf download ntc-ai/SDXL-LoRA-slider.oil-painting "oil painting.safetensors" --local-dir "$LORA_DIR"
hf download ntc-ai/SDXL-LoRA-slider.epic-oil-painting "epic oil painting.safetensors" --local-dir "$LORA_DIR"
mv "$LORA_DIR/oil painting.safetensors" "$LORA_DIR/oil-painting-slider.safetensors"
mv "$LORA_DIR/epic oil painting.safetensors" "$LORA_DIR/epic-oil-painting-slider.safetensors"

# Pencil / sketch
hf download Linaqruf/sketch-style-xl-lora sketch-style-xl.safetensors --local-dir "$LORA_DIR"
```

## Trigger words and weights

- **Coloring book:** The tags are ColoringBookAF and Coloring Book.
- **Storybook:** The trigger is KidsRedmAF, Kids Book.
- **LineAni:** The trigger is LineAniAF, lineart.
- **Analog:** The trigger is AnalogRedmAF, Analog. I haven't read this one's model card, so I'm inferring the film-grain look from the name and trigger.
- **3D (goofyai):** The triggers are 3d style, 3d, and 3d render.
- **Pixar and oil painting sliders:** The triggers are `pixar-style`, `oil painting` and `epic oil painting`. The Pixar slider's own example loads it at strength 2.0.
- **Pencil:** The Osipova LoRA is triggered by "sketch pencil drawing OSI style".

## Corrections to above table

- **Slider weights:** The ntc-ai LoRAs (Pixar, both oil paintings) are sliders that work on a wider scale than normal LoRAs. Their example applies the oil painting slider at 2.0. Use roughly 1.5–3 for them, not the 0.7–0.9 I listed.
- **Detail Tweaker XL:** Its description says it works from -3 to 3, with a suggested starting weight of 1.5. My 0.3–0.6 was a conservative guess, so tune it by eye. The Hugging Face copy is an unofficial re-upload. The original lives on Civitai (model 122359).
- **Mandala:** I found no dedicated SDXL mandala LoRA on Hugging Face, so I won't invent a repo. The coloring-book LoRA plus a prompt like "radially symmetric mandala, black and white line art" is the safest HF-only setup. Dedicated mandala LoRAs exist on Civitai if you want one.
- **Pencil and sketch:** Linaqruf's LoRA was built for Animagine XL 2.0 and targets monochrome sketch looks, so test it with Animagine 3.1 rather than Juggernaut.

Sources:

- [ColoringBookRedmond-V2](https://huggingface.co/artificialguybr/ColoringBookRedmond-V2)
- [StoryBookRedmond-V2](https://huggingface.co/artificialguybr/StoryBookRedmond-V2)
- [LineAniRedmond-LinearMangaSDXL-V2](https://huggingface.co/artificialguybr/LineAniRedmond-LinearMangaSDXL-V2)
- [add-detail-xl](https://huggingface.co/highscoregames12018/add-detail-xl)
- [analogredmond-v2](https://huggingface.co/artificialguybr/analogredmond-v2)
- [3d_render_style_xl](https://huggingface.co/goofyai/3d_render_style_xl)
- [SDXL-LoRA-slider.pixar-style](https://huggingface.co/ntc-ai/SDXL-LoRA-slider.pixar-style)
- [SDXL-LoRA-slider.oil-painting](https://huggingface.co/ntc-ai/SDXL-LoRA-slider.oil-painting)
- [sketch-style-xl-lora](https://huggingface.co/Linaqruf/sketch-style-xl-lora)

I can update the genre tables with the corrected weights and these exact filenames if you'd like.
