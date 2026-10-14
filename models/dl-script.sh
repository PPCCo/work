pip install -U "huggingface_hub[cli]"        # provides the `hf` command (older versions: `huggingface-cli download`)
export LORA_DIR="$HOME/Documents/dev/_new_2/publish/loras"  # change to your LoRA folder
mkdir -p "$LORA_DIR"

# Kids reading book illustrations
hf download artificialguybr/StoryBookRedmond-V2 redmondv2_kids_storybook_lora_f16.ckpt --local-dir "$LORA_DIR"

# Kids and adult coloring books, line art, mandala (see note below)
hf download artificialguybr/ColoringBookRedmond-V2 redmond_coloringbook_lora_f16.ckpt --local-dir "$LORA_DIR"

# Manga/anime line art (Animagine slot)
hf download artificialguybr/LineAniRedmond-LinearMangaSDXL-V2 redmondv2_lineart_lineani_lora_f16.ckpt --local-dir "$LORA_DIR"

# Detail Tweaker XL (third-party mirror)
hf download highscoregames12018/add-detail-xl add_detail_xl_lora_f16.ckpt --local-dir "$LORA_DIR"

# Film/grain slot in photography
hf download artificialguybr/analogredmond-v2 redmondv2_analog_lora_f16.ckpt --local-dir "$LORA_DIR"

# 3D renders
hf download goofyai/3d_render_style_xl 3d_render_style_xl_lora_f16.ckpt --local-dir "$LORA_DIR"
hf download ntc-ai/SDXL-LoRA-slider.pixar-style pixar_style_lora_f16.ckpt --local-dir "$LORA_DIR"

# Oil painting (filenames contain spaces, so rename them)
hf download ntc-ai/SDXL-LoRA-slider.oil-painting "oil painting.safetensors" --local-dir "$LORA_DIR"
hf download ntc-ai/SDXL-LoRA-slider.epic-oil-painting "epic oil painting.safetensors" --local-dir "$LORA_DIR"
mv "$LORA_DIR/oil painting.safetensors" "$LORA_DIR/oil_painting_slider_lora_f16.ckpt"
mv "$LORA_DIR/epic oil painting.safetensors" "$LORA_DIR/oil_painting_slider_epic_lora_f16.ckpt"

# Pencil / sketch
hf download Linaqruf/sketch-style-xl-lora sketch_style_lora_f16.ckpt --local-dir "$LORA_DIR"