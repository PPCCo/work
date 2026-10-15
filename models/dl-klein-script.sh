# pip install -U "huggingface_hub[cli]"        # provides the `hf` command (older versions: `huggingface-cli download`)
export LORA_DIR="$HOME/Documents/dev/_new_2/publish/loras"  # change to your LoRA folder
mkdir -p "$LORA_DIR"

pip install -U "huggingface_hub[cli]"
mkdir -p ~/Documents/dev/_new_2/publish/loras-klein && cd ~/Documents/dev/_new_2/publish/loras-klein

hf download goumsss/numzoo-flux2-klein-lora numzoo_klein.safetensors --local-dir ./numzoo
hf download Barath/flux2-klein-yarn-art-lora klein4b_yarn_art_lora_v1.safetensors --local-dir ./yarn
hf download noema-art/ohiseeflux-klein ohiseeflux_klein.safetensors --local-dir ./ohisee
hf download noema-art/dutchbaroqueflux-klein dutchbaroqueflux_klein.safetensors --local-dir ./dutchbaroque
hf download giannisan/light-fantasy-flux2-klein-base-lora pytorch_lora_weights.safetensors --local-dir ./lightfantasy
hf download devon7y/WikiQwen-Illustrator pytorch_lora_weights.safetensors --local-dir ./wikiqwen
hf download Limbicnation/pixel-art-lora pytorch_lora_weights.safetensors --local-dir ./pixel
hf download radames/FLUX.2-klein-Sana-Sprint pytorch_lora_weights.safetensors --local-dir ./sprint

# rename filenames BEFORE importing/converting
mv lightfantasy/pytorch_lora_weights.safetensors klein_light_fantasy.safetensors
mv wikiqwen/pytorch_lora_weights.safetensors klein_wikiqwen_illustrator.safetensors
mv pixel/pytorch_lora_weights.safetensors klein_pixel_art.safetensors
mv sprint/pytorch_lora_weights.safetensors klein_sana_sprint.safetensors
mv numzoo/numzoo_klein.safetensors klein_numzoo.safetensors
mv yarn/klein4b_yarn_art_lora_v1.safetensors klein_yarn_art_lora_v1.safetensors
mv ohisee/ohiseeflux_klein.safetensors klein_ohiseeflux.safetensors
mv dutchbaroque/dutchbaroqueflux_klein.safetensors klein_dutchbaroqueflux.safetensors

Flux_klein_4b_anime_Koni.safetensors
pixelart_lora.safetensors
