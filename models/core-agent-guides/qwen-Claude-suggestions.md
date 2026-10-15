# Qwen / upscaler / settings / prompt playbook

I'll check the current draw-things-cli options first, then build the guide and the rules JSON as two files.

I've written the guide and the rules JSON, covering 19 profiles. I couldn't run `draw-things-cli` here (Linux sandbox, no Draw Things), so none of the settings are tested. What I did check is that all 19 example commands parse in bash, their `--config-json` blocks are valid JSON, and sizes are multiples of 64. Covers never put "text" in the negative prompt, and coloring pages always do.

The sampler numbers come from the Draw Things source enum, and the steps and CFG ranges from Qwen-Image-2512 community guidance. Two things need checking on your machine before you trust the examples:

- **Upscaler keys:** I couldn't confirm that `upscaler` and `upscalerScaleFactor` are accepted inside `--config-json`. If the CLI rejects them, use `--upscaler <file> --upscaler-scale <2|4>` instead.
- **Upscaler filenames:** the names are my best guess. List what you have with `ls ~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models | grep -i -E 'esrgan|sharp|remacri'` and adjust.

Two other things you might not expect:

- **Output path:** the examples use `"$HOME/Dev/tmp/..."` , because `~` isn't expanded inside single quotes. Run `mkdir -p "$HOME/Dev/tmp"` once.
- **Blank images:** q8p Qwen 2512 can occasionally return a blue, black or noisy image for some prompts (draw-things-community issue #136). Change the seed or reword the prompt; the failure table covers this.

The per-genre sampler, CFG offsets and upscaler pairings are my judgment, not benchmarks, so try each profile on about three seeds first. Each profile carries a confidence score and tuning ranges so the agent can see how firm each recommendation is.

Covers use 1024x1536 for 2:3 trim, with 640x960 for fast drafts. Coloring pages use 768x1024 or 1024x1344, and mandalas use 1024x1024. 4x upscales need downscaling to print size afterwards. The image is the front cover only; spine and bleed are for your layout software.

Files generated are:

- `qwen-book-cover-guide.md`
- `qwen-book-cover-recommendation-rules.json`
- `build_docs.py` (the generator that produces both. You only need it if you want to change a profile’s settings or prompts and regenerate both files so they stay consistent. For just using the guide and the JSON, the two earlier files are enough.)