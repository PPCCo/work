I'll check what Draw Things CLI currently supports for upscaling and how Civitai downloads work from the command line.

https://raw.githubusercontent.com/wyattowalsh/agents/main/skills/draw-thing/SKILL.md

Draw Things upscaling is less settled than it looks, so I've separated what I could confirm from what you'll need to check on your machine.

## Check this first: CLI support

A third-party skill written against the current CLI says `generate --help` no longer exposes a direct `--upscaler` flag, and upscaling has to go through `--config-json` / `--config-file` once you've verified the schema. Run these to see what your version supports:

```bash
draw-things-cli generate --help | grep -i upscal
draw-things-cli models list
draw-things-cli models import --help
```

I couldn't confirm the exact list of bundled upscalers or the config key names, so treat any `upscaler` / `upscalerScaleFactor` JSON key as something to verify. The easiest way is to export a config from the Draw Things app with the upscaler set, then pass it with `--config-file`.

A second caveat is that Civitai upscalers are mostly ESRGAN `.pth` files, and Draw Things uses its own converted `.ckpt` format. Whether `models import` accepts these is something I couldn't verify, so check that help output before downloading anything.

## Which upscalers suit which job

These are the models people commonly use. I couldn't verify how each performs inside Draw Things.

| Use                                 | Pick                                                            | Notes                                                                                                              |
| ----------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Coloring books (clean line art)** | RealESRGAN x4plus anime 6B, 4x-AnimeSharp, 4x_IllustrationJaNai | Anime and illustration models keep lines crisp. Avoid photo-trained models, which add texture to flat white areas. |
| **Sketches**                        | 4x_NMKD-Siax_200k, 4x-AnimeSharp                                | Siax is a general upscaler for clean to lightly compressed images. Pick it if you want to keep pencil texture.     |
| **Colored images**                  | 4x-UltraSharp, 4x_foolhardy_Remacri, IllustrationJaNai          | UltraSharp is the usual choice for AI-generated art.                                                               |

Two practical tips for coloring-book pages. First, upscale 2x rather than 4x, since pixel upscalers run out of information on small sources. Second, threshold the result back to pure black and white afterwards to remove grey halos.

**Licensing:** Many people sell coloring books, so this matters. UltraSharp, AnimeSharp, Remacri and IllustrationJaNai are CC-BY-NC-SA-4.0 (non-commercial), while RealESRGAN_x4plus and the NMKD models are BSD-3 or WTFPL. For commercial output, use the Real-ESRGAN or NMKD models.

## Downloading from Civitai with curl

1. **Get a token.** Create an API key in your Civitai account settings. The API accepts it as a Bearer token in the Authorization header.

2. **Find the model version ID.** It's the `modelVersionId=` value in the model page URL. You can also search for upscalers through the API:

   ```bash
   curl "https://civitai.com/api/v1/models?types=Upscaler&query=anime&limit=10" | jq '.items[] | {name, id, versions: [.modelVersions[] | {id, name}]}'
   ```

3. **Download.** `-L` follows the redirect to the file host, and `-J -O` saves it under its real filename:

   ```bash
   export CIVITAI_TOKEN="your_key_here"
   curl -L -J -O -H "Authorization: Bearer $CIVITAI_TOKEN" \
     "https://civitai.com/api/download/models/<VERSION_ID>"
   ```

   If a version requires auth, the API says so, and the token can also be passed as a `?token=` query parameter. Prefer the header, since query tokens end up in shell history and logs.

4. **Check the file** with `shasum -a 256 file` against the hash in the model version's API response. Prefer `.safetensors` where offered, since `.pth` files are pickles and can run code when loaded.

If you tell me which upscaler you want to try, I can write the exact `models import` or `--config-file` steps once you've pasted your `--help` output.

Sources:

- [AI Upscalers license table (easygoing0114, Hugging Face)](https://huggingface.co/easygoing0114/AI_upscalers)
- [draw-thing skill (wyattowalsh/agents)](https://raw.githubusercontent.com/wyattowalsh/agents/main/skills/draw-thing/SKILL.md)
- [Civitai public REST API](https://developer.civitai.com/docs/api/public-rest)
- [Civitai model versions reference](https://developer.civitai.com/site/reference/model-versions.md)
