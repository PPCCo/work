#!/usr/bin/env python3
"""Single source of truth -> emits the guide (markdown) and the rules (JSON)."""
import json, re

MODEL = "qwen_image_2512_bf16_q8p.ckpt"
OUT_DIR_EXPR = "$HOME/Dev/tmp"

SAMPLERS = {
    0: "DPM++ 2M Karras", 1: "Euler A", 2: "DDIM", 3: "PLMS", 4: "DPM++ SDE Karras",
    5: "UniPC", 6: "LCM", 7: "Euler A Substep", 8: "DPM++ SDE Substep", 9: "TCD",
    10: "Euler A Trailing", 11: "DPM++ SDE Trailing", 12: "DPM++ 2M AYS", 13: "Euler A AYS",
    14: "DPM++ SDE AYS", 15: "DPM++ 2M Trailing", 16: "DDIM Trailing", 17: "UniPC Trailing",
    18: "UniPC AYS", 19: "TCD Trailing",
}
def sn(i): return f"{SAMPLERS[i]} [{i}]"

UPSCALERS = {
    "realesrgan_x2plus_f16.ckpt": (2, "General 2x. Safe default for painterly, photo, mixed content."),
    "realesrgan_x4plus_f16.ckpt": (4, "General 4x. Photos and realism when >2x is needed."),
    "realesrgan_x4plus_anime_6b_f16.ckpt": (4, "4x for flat colour, anime, cel shading, clean line art."),
    "4x_ultrasharp_f16.ckpt": (4, "4x crisp edges. Best for ink line art, mandalas, graphic type."),
    "remacri_4x_f16.ckpt": (4, "4x texture reconstruction. Good for photo/oil/canvas texture."),
}

# ---------- text clause ----------
def text_clause(t):
    return (f'Title "{t["title"]}" {t["ts"]}; series name "{t["series"]}" {t["ss"]}; '
            f'publisher name "{t["pub"]}" {t["ps"]}. All text spelled exactly as written, sharp and legible.')

PUB = "Maple Lane Press"

def T(title, series, pub, ts, ss, ps):
    return dict(title=title, series=series, pub=pub, ts=ts, ss=ss, ps=ps)

PROFILES = []
def add(**k): PROFILES.append(k)

# ---------------- COVERS: kids / teens ----------------
add(id="kids_picture_book_3_5", name="Picture / early-reading book, ages 3-5", mode="cover",
    ages=["3-5"], genres=["kids reading book", "picture book", "board book", "nursery"],
    kw=["picture book", "toddler", "preschool", "nursery", "bedtime", "ages 3", "board book", "early reader", "simple story"],
    w=1024, h=1536, dw=640, dh=960, steps=32, cfg=4.0, sampler=10, alt=15, up="realesrgan_x2plus_f16.ckpt", alt_up="realesrgan_x4plus_anime_6b_f16.ckpt",
    scene="Children's picture book cover for ages 3 to 5, flat gouache illustration with thick soft outlines. A smiling round baby fox in a red scarf waves from a green hill under a big yellow sun, with a few simple clouds and three flowers. Warm primary colors, one big central character, plenty of empty sky at the top.",
    text=T("Finn the Brave Little Fox", "Little Woodland Tales", PUB,
           "in large bold rounded hand-lettered capitals in the sky", "in small rounded letters at the very top",
           "in small letters at the bottom center"),
    neg="scary, dark, realistic, photograph, sharp teeth, clutter, tiny details, misspelled text, garbled letters, extra words, watermark, blurry, deformed hands",
    why="Euler A Trailing gives soft, forgiving shapes. CFG 4 keeps the exact text and single-subject layout. 2x general upscaler avoids over-sharpening flat colour.",
    tune=["Letters wrong: shorten title to <=4 words, steps 40, CFG 3.5.", "Too busy: add 'minimal background, one subject' to prompt."],
    conf=(0.72, 0.55, 0.65, 0.78))
add(id="kids_storybook_6_8", name="Illustrated storybook, ages 6-8", mode="cover",
    ages=["6-8"], genres=["storybook", "illustrated book", "fairy tale", "chapter book"],
    kw=["storybook", "fairy tale", "chapter book", "ages 6", "illustrated story", "adventure", "bedtime story"],
    w=1024, h=1536, dw=640, dh=960, steps=34, cfg=4.0, sampler=10, alt=15, up="realesrgan_x2plus_f16.ckpt", alt_up="remacri_4x_f16.ckpt",
    scene="Storybook cover for ages 6 to 8, painterly digital illustration in a soft watercolor-gouache style. Two children and a small owl carrying a lantern walk down a mossy path into a glowing moonlit forest with fireflies and tiny lit cottage windows. Warm golden light against deep teal shadows, layered trees for depth, room for the title in the upper third.",
    text=T("The Lantern Owl of Hollow Wood", "Hollow Wood Tales, Book 2", PUB,
           "in whimsical serif lettering across the upper third", "in small clean letters above the title",
           "in small letters at the bottom center"),
    neg="horror, gore, photorealistic, harsh shadows, muddy colors, crowded composition, misspelled text, garbled letters, extra words, watermark, deformed hands, extra fingers",
    why="Richer scene than 3-5 so steps 34. Euler A Trailing keeps painterly softness. CFG 4 balances scene detail and title accuracy.",
    tune=["Characters distorted: steps 40 and reduce to 2 characters.", "Flat look: add lighting words (rim light, glow)."],
    conf=(0.72, 0.55, 0.65, 0.78))
add(id="kids_nonfiction_8_12", name="Informative non-fiction for kids, ages 8-12", mode="cover",
    ages=["8-12"], genres=["non-fiction", "informative", "science", "history", "educational"],
    kw=["non-fiction", "nonfiction", "informative", "educational", "science", "facts", "ages 8", "ages 9", "ages 10", "discover", "encyclopedia"],
    w=1024, h=1536, dw=640, dh=960, steps=36, cfg=4.0, sampler=15, alt=10, up="realesrgan_x2plus_f16.ckpt", alt_up="4x_ultrasharp_f16.ckpt",
    scene="Informative non-fiction book cover for ages 8 to 12 about volcanoes. Clean educational illustration of a cutaway volcano showing the magma chamber, rock layers, lava and an ash cloud, with a small curious explorer kid in a helmet pointing at it. Bright saturated flat colors, crisp outlines, bold orange and blue palette, uncluttered composition.",
    text=T("Volcanoes Up Close", "Discover Science Series", PUB,
           "in chunky sans-serif capitals at the top", "in a small colored band above the title",
           "in small letters at the bottom center"),
    neg="photograph, gore, scary, dense paragraphs, tiny captions, misspelled text, garbled letters, extra words, watermark, blurry, muddy colors, low contrast",
    why="DPM++ 2M Trailing converges cleanly for crisp outlines and sharp lettering. Steps 36 for diagram-like detail. CFG 4 for accuracy.",
    tune=["Soft outlines: alt sampler Euler A Trailing is NOT better here; raise steps to 42 instead.", "Lettering weak: use 4x_ultrasharp upscaler."],
    conf=(0.7, 0.5, 0.6, 0.75))
add(id="teen_nonfiction_13_17", name="Teen non-fiction / informative, ages 13-17", mode="cover",
    ages=["13-17"], genres=["non-fiction", "self-help", "teen", "informative", "psychology", "science"],
    kw=["teen", "teenager", "young adult non-fiction", "ages 13", "ya non-fiction", "self-help teens", "modern", "graphic design"],
    w=1024, h=1536, dw=640, dh=960, steps=36, cfg=4.0, sampler=15, alt=17, up="4x_ultrasharp_f16.ckpt", alt_up="realesrgan_x2plus_f16.ckpt",
    scene="Modern teen non-fiction book cover about the psychology of sleep and the teenage brain. Bold graphic design with a stylized glowing brain made of layered paper-cut shapes over a deep indigo and electric coral gradient, a crescent moon, minimal clean composition with generous negative space, contemporary editorial poster look.",
    text=T("WIDE AWAKE", "The Mind Lab Series", "North Harbor Books",
           "in huge condensed sans-serif capitals across the middle", "in small spaced capitals above the title",
           "in small capitals at the bottom center"),
    neg="childish, cartoon mascot, clip art, stock photo look, cluttered, rainbow colors, misspelled text, garbled letters, extra words, watermark, low contrast, blurry",
    why="Graphic poster style benefits from DPM++ 2M Trailing precision. 4x ultrasharp keeps typography edges crisp (downscale after).",
    tune=["Output too large: downscale to print size.", "Too childish: add 'sophisticated, restrained palette'."],
    conf=(0.7, 0.5, 0.6, 0.75), up_scale_note=True)

# ---------------- COVERS: coloring ----------------
add(id="kids_coloring_cover", name="Kids coloring book cover (colour cover)", mode="cover",
    ages=["3-5", "6-8", "9-12"], genres=["coloring book", "kids coloring"],
    kw=["coloring book cover", "colouring book cover", "kids coloring book", "crayon", "coloring book for kids"],
    w=1024, h=1536, dw=640, dh=960, steps=32, cfg=4.0, sampler=10, alt=15, up="realesrgan_x2plus_f16.ckpt", alt_up="realesrgan_x4plus_anime_6b_f16.ckpt",
    scene="Cover of a children's coloring book. A cheerful friendly dinosaur holding a giant crayon, bold black outlines with bright flat colors on a pale yellow background, with three uncolored black-and-white line-art dinosaur outlines floating around to hint at the pages inside. Playful, simple, high contrast.",
    text=T("Dino Colors", "Crayon Club", PUB,
           "in big bubbly multicolor capitals at the top", "in small letters above the title",
           "in small letters at the bottom center"),
    neg="scary teeth, realistic, photograph, gradient shading, dark background, clutter, misspelled text, garbled letters, extra words, watermark, blurry",
    why="Colour cover with line-art teasers. Same recipe as picture-book covers; short 2-word title is the most reliable text case.",
    tune=["Teaser outlines coloured in: add 'pure white uncolored outlines' and lower CFG slightly is NOT needed; raise CFG to 4.5."],
    conf=(0.7, 0.55, 0.65, 0.75))
add(id="adult_coloring_cover", name="Adult coloring book cover (colour cover)", mode="cover",
    ages=["adult"], genres=["coloring book", "adult coloring", "stress relief"],
    kw=["adult coloring book cover", "stress relief coloring", "mindful coloring", "calm coloring", "coloring book for adults cover"],
    w=1024, h=1536, dw=640, dh=960, steps=36, cfg=4.5, sampler=15, alt=10, up="4x_ultrasharp_f16.ckpt", alt_up="realesrgan_x2plus_f16.ckpt",
    scene="Elegant cover for an adult coloring book. A rich, fully colored, highly detailed owl-and-moon mandala centered on a deep navy background with gold accents, plus a small framed inset of the same design as black outline line art on cream paper. Refined symmetrical layout, premium feel.",
    text=T("Midnight Mandalas", "Calm Hours Coloring Series", "Juniper & Ash Press",
           "in elegant gold serif capitals at the top", "in small gold capitals under the title",
           "in small gold letters at the bottom center"),
    neg="childish, cartoon, messy lines, muddy colors, flat clip art, cluttered, misspelled text, garbled letters, extra words, watermark, blurry",
    why="Fine ornament needs precise convergence (DPM++ 2M Trailing) and 36 steps. CFG 4.5 enforces symmetry and inset. Ultrasharp keeps gold linework crisp.",
    tune=["Inset missing: describe it earlier in the prompt.", "Output 4x large: downscale after."],
    conf=(0.68, 0.5, 0.6, 0.72), up_scale_note=True)

# ---------------- INTERIOR coloring pages ----------------
add(id="kids_coloring_page_3_6", name="Kids coloring page (interior), ages 3-6", mode="interior",
    ages=["3-5", "6-8"], genres=["coloring book", "kids coloring", "line art"],
    kw=["coloring page", "colouring page", "kids coloring", "simple line art", "thick lines", "toddler coloring", "ages 3", "easy coloring"],
    w=768, h=1024, dw=576, dh=768, steps=28, cfg=5.0, sampler=15, alt=10, up="realesrgan_x4plus_anime_6b_f16.ckpt", alt_up="4x_ultrasharp_f16.ckpt",
    scene="Children's coloring book page for ages 3 to 6. A single big happy elephant holding a balloon, very thick clean black outlines, simple large shapes, pure white background, no shading, no fill, centered with wide white margins, easy to color.",
    text=None,
    neg="color, gray, shading, gradient, shadows, texture, tiny details, background scenery, text, watermark, sketchy lines, broken lines",
    why="Higher CFG 5 enforces pure white background and no fill. 28 steps is enough for few shapes. Anime 6B 4x keeps thick lines clean. Base 768x1024 x4 = 3072x4096 (>8.5x11 at 300dpi).",
    tune=["Gray fills appear: CFG 5.5 and add 'solid black lines only' to prompt.", "Lines too thin: add 'extra thick bold outline'."],
    conf=(0.75, 0.55, 0.7, 0.8))
add(id="kids_coloring_page_7_12", name="Kids coloring page (interior), ages 7-12", mode="interior",
    ages=["9-12", "6-8"], genres=["coloring book", "kids coloring", "line art"],
    kw=["coloring page ages 7", "tween coloring", "medium detail coloring", "kids line art", "ages 8", "ages 10"],
    w=768, h=1024, dw=576, dh=768, steps=32, cfg=5.0, sampler=15, alt=10, up="realesrgan_x4plus_anime_6b_f16.ckpt", alt_up="4x_ultrasharp_f16.ckpt",
    scene="Coloring book page for ages 7 to 12. A friendly dragon curled around a castle tower with scales, clouds and stars, medium-detail clean black line art, uniform line weight, pure white background, closed shapes ready to color, no shading.",
    text=None,
    neg="color, gray fill, shading, gradients, shadows, sketchy, messy overlapping lines, text, watermark, blurry, cropped",
    why="Same recipe as 3-6 with more steps for medium detail. Closed shapes cue prevents open regions that are hard to colour.",
    tune=["Too complex: say 'fewer, larger shapes'.", "Open shapes: add 'every shape fully closed'."],
    conf=(0.75, 0.55, 0.7, 0.8))
add(id="adult_coloring_line_art", name="Adult coloring page (interior), intricate line art", mode="interior",
    ages=["adult", "13-17"], genres=["coloring book", "adult coloring", "line art"],
    kw=["adult coloring page", "intricate line art", "detailed coloring", "floral coloring", "animal coloring adult", "zentangle", "ink line art"],
    w=1024, h=1344, dw=640, dh=832, steps=36, cfg=5.5, sampler=15, alt=0, up="4x_ultrasharp_f16.ckpt", alt_up="realesrgan_x4plus_anime_6b_f16.ckpt",
    scene="Intricate adult coloring page. A mystical owl perched on a crescent moon surrounded by floral mandala patterns, feathers drawn with fine repeating patterns, fine uniform black ink lines, pure white background, no shading, symmetrical balanced composition, closed shapes, high detail.",
    text=None,
    neg="3d render, color, grayscale shading, gray shadows, sketch, charcoal, messy lines, blurry, text, watermark, bg color, cropped",
    why="1024 base keeps fine lines separate. CFG 5.5 pushes strict black-on-white. Ultrasharp 4x preserves hairlines; downscale 4096x5376 to 2550x3300.",
    tune=["Lines merge: raise base to 1152x1536 (needs ~tiledDecoding true).", "Gray tone: CFG 6 and add 'high contrast pure black ink'."],
    conf=(0.72, 0.5, 0.7, 0.8), up_scale_note=True)
add(id="adult_mandala", name="Adult mandala coloring page (interior)", mode="interior",
    ages=["adult"], genres=["mandala", "coloring book", "line art"],
    kw=["mandala", "radial", "symmetrical pattern", "meditation coloring", "geometric coloring", "lotus mandala"],
    w=1024, h=1024, dw=640, dh=640, steps=36, cfg=5.5, sampler=15, alt=0, up="4x_ultrasharp_f16.ckpt", alt_up="realesrgan_x4plus_anime_6b_f16.ckpt",
    scene="Circular mandala coloring page, perfectly symmetrical radial design with layered petals, paisley, geometric lotus rings and fine dot borders, fine black linework, pure white background, centered with white margin all around, no shading.",
    text=None,
    neg="color, shading, gradient, asymmetry, off-center, messy lines, blurry, text, watermark, background texture, cropped",
    why="Square canvas suits radial symmetry. DPM++ 2M Trailing yields stable repeating geometry. 4096x4096 output exceeds 8.5in square at 300dpi; downscale.",
    tune=["Asymmetry: CFG 6 and add 'exact radial symmetry, 12-fold'.", "Fill artefacts: DPM++ 2M Karras [0] as alt sampler."],
    conf=(0.72, 0.5, 0.7, 0.8), up_scale_note=True)

# ---------------- FINE ART / MEDIA ----------------
add(id="pencil_sketch", name="Pencil / graphite artistic sketch book", mode="cover",
    ages=["adult", "13-17"], genres=["sketchbook", "art book", "pencil", "drawing"],
    kw=["pencil", "graphite", "charcoal sketch", "sketchbook", "cross-hatching", "drawing book", "art of sketching"],
    w=1024, h=1536, dw=640, dh=960, steps=36, cfg=4.0, sampler=10, alt=15, up="realesrgan_x2plus_f16.ckpt", alt_up="remacri_4x_f16.ckpt",
    scene="Book cover in the style of a graphite pencil sketch on cream paper. An old fisherman mending nets on a harbor pier at dawn, expressive cross-hatching, soft smudged shading, visible paper grain, loose construction lines, monochrome graphite tones.",
    text=T("The Harbor Sketchbook", "Studio Notes Series", PUB,
           "in hand-lettered pencil capitals at the top", "in small pencil letters under the title",
           "in small pencil letters at the bottom center"),
    neg="color, saturated, digital gloss, 3d render, cartoon, vector, photograph, clean outlines, misspelled text, garbled letters, extra words, watermark",
    why="Euler A Trailing preserves organic grain and loose strokes. CFG 4 keeps tone monochrome. 2x general upscaler keeps grain rather than smoothing.",
    tune=["Too clean/digital: lower CFG 3.5, add 'rough, imperfect, hand-drawn'.", "Colour leaks: add 'monochrome only' and CFG 4.5."],
    conf=(0.68, 0.5, 0.6, 0.72))
add(id="watercolor", name="Watercolor painting book", mode="cover",
    ages=["adult", "13-17", "6-8", "9-12"], genres=["art book", "watercolor", "painting", "storybook"],
    kw=["watercolor", "watercolour", "wash", "wet-on-wet", "aquarelle", "soft painting"],
    w=1024, h=1536, dw=640, dh=960, steps=34, cfg=3.5, sampler=10, alt=15, up="realesrgan_x2plus_f16.ckpt", alt_up="remacri_4x_f16.ckpt",
    scene="Watercolor painting book cover. A misty lavender field with a lone cottage at sunrise, wet-on-wet washes, soft bleeding edges, pigment blooms, visible cold-press paper texture, white paper left unpainted near the edges, soft peach and lavender palette.",
    text=T("Lavender Mornings", "The Wash Series", PUB,
           "in delicate hand-painted serif letters in the sky", "in small painted letters above the title",
           "in small painted letters at the bottom center"),
    neg="vector, hard outlines, digital gradient, oversharpened, plastic, photograph, airbrushed, muddy colors, misspelled text, garbled letters, extra words, watermark",
    why="Lower CFG 3.5 allows soft bleeding and pigment variation; higher CFG makes it look digital. Euler A Trailing keeps loose edges.",
    tune=["Text too rigid or garbled: CFG 3.8, steps 40.", "Too sharp: skip upscaler or use x2plus only."],
    conf=(0.68, 0.5, 0.6, 0.72))
add(id="oil_painting", name="Oil painting book", mode="cover",
    ages=["adult"], genres=["art book", "oil painting", "classical", "fine art"],
    kw=["oil painting", "impasto", "canvas", "classical painting", "palette knife", "renaissance", "baroque"],
    w=1024, h=1536, dw=640, dh=960, steps=36, cfg=3.5, sampler=10, alt=15, up="remacri_4x_f16.ckpt", alt_up="realesrgan_x2plus_f16.ckpt",
    scene="Oil painting book cover. A stormy sea with a lone sailing ship at golden hour, thick impasto brushstrokes, palette-knife highlights, rich warm ochre and deep prussian blue, visible canvas weave, dramatic chiaroscuro, classical composition with calm sky area at the top.",
    text=T("Storm Light", "Masters of the Sea", "Juniper & Ash Press",
           "in engraved gold serif capitals in the sky area", "in small gold capitals above the title",
           "in small gold capitals at the bottom center"),
    neg="flat vector, airbrushed, plastic, cgi, photograph, digital noise, oversaturated, cartoon, misspelled text, garbled letters, extra words, watermark",
    why="CFG 3.5 keeps brushwork natural. Remacri 4x reconstructs canvas/paint texture; downscale 4096x6144 to target.",
    tune=["Smooth/plastic: add 'visible brushstrokes, thick paint'.", "Large file: swap to realesrgan_x2plus."],
    conf=(0.68, 0.5, 0.6, 0.72), up_scale_note=True)

# ---------------- ANIME / DIGITAL ----------------
add(id="anime_2d", name="2D anime illustration book / light novel", mode="cover",
    ages=["13-17", "adult"], genres=["anime", "light novel", "manga-style", "YA"],
    kw=["anime", "light novel", "manga", "cel shaded", "2d anime", "visual novel", "waifu", "shonen", "shojo"],
    w=832, h=1216, dw=576, dh=832, steps=32, cfg=4.0, sampler=15, alt=10, up="realesrgan_x4plus_anime_6b_f16.ckpt", alt_up="4x_ultrasharp_f16.ckpt",
    scene="2D anime key visual style book cover for a teen light novel. A girl with short silver hair and a school uniform holds a glowing paper lantern on a rooftop at twilight, sakura petals drifting, vivid cel shading, clean linework, detailed twilight sky gradient, dynamic low angle.",
    text=T("The Lantern Girl", "Sakura Nights, Vol. 1", "Kitsune Press",
           "in large stylized brush-script capitals at the top", "in small clean letters above the title",
           "in small capitals at the bottom center"),
    neg="3d render, photorealistic, western comic style, bad anatomy, extra fingers, deformed hands, blurry, jpeg artifacts, misspelled text, garbled letters, extra words, watermark",
    why="Anime 6B 4x suits cel shading and line clarity. 832x1216 base x4 = 3328x4864. DPM++ 2M Trailing for clean lines.",
    tune=["Hands wrong: hide hands (behind back, holding object) in prompt.", "Too soft: alt upscaler 4x_ultrasharp."],
    conf=(0.68, 0.5, 0.7, 0.75))
add(id="anime_3d", name="3D stylized / animated-film look illustration", mode="cover",
    ages=["6-8", "9-12", "13-17"], genres=["3d illustration", "animated", "kids"],
    kw=["3d anime", "3d render", "3d animated", "pixar-like", "cgi cartoon", "clay render", "3d character", "stylized 3d"],
    w=1024, h=1536, dw=640, dh=960, steps=34, cfg=4.0, sampler=15, alt=10, up="realesrgan_x2plus_f16.ckpt", alt_up="realesrgan_x4plus_f16.ckpt",
    scene="Stylized 3D animated feature-film look book cover. A cheerful young inventor girl with a goggle headband and a small round robot companion in a cozy workshop, soft global illumination, gentle subsurface scattering, rounded appealing character design, shallow depth of field, warm teal and orange palette.",
    text=T("Zoe and the Gizmo", "Workshop Friends", PUB,
           "in chunky 3D beveled letters at the top", "in small rounded letters above the title",
           "in small letters at the bottom center"),
    neg="photorealistic skin pores, uncanny valley, flat 2d, line art, harsh noise, bad anatomy, extra fingers, misspelled text, garbled letters, extra words, watermark",
    why="General 2x upscaler preserves smooth shaded surfaces. Do not name studios or characters (IP). CFG 4 balances look and text.",
    tune=["Too realistic: add 'toy-like, exaggerated proportions'.", "Flat look: add 'soft volumetric light'."],
    conf=(0.68, 0.5, 0.65, 0.75))
add(id="digital_painting", name="Digital painting / concept art (fantasy, sci-fi, YA)", mode="cover",
    ages=["13-17", "adult"], genres=["fantasy", "sci-fi", "digital art", "YA"],
    kw=["digital painting", "digital art", "concept art", "fantasy", "sci-fi", "epic", "cinematic illustration", "matte painting"],
    w=1024, h=1536, dw=640, dh=960, steps=36, cfg=4.0, sampler=15, alt=10, up="realesrgan_x2plus_f16.ckpt", alt_up="4x_ultrasharp_f16.ckpt",
    scene="Epic digital painting fantasy book cover. A lone armored traveler stands on a cliff overlooking a floating-island kingdom at dawn, volumetric light rays, painterly brushwork, dramatic scale, rich color grading, cinematic composition with clear space at the top for the title.",
    text=T("EMBERFALL", "The Shattered Crown, Book 1", "Raven Gate Publishing",
           "in large metallic engraved capitals at the top", "in small capitals under the title",
           "in small capitals at the bottom center"),
    neg="photograph, flat vector, cartoon, low detail, muddy, oversaturated, extra limbs, deformed hands, misspelled text, garbled letters, extra words, watermark",
    why="DPM++ 2M Trailing gives detailed, stable painterly output. Single-word title is the most reliable for stylised lettering.",
    tune=["Title lost in art: reserve 'dark calm sky area' behind text.", "More texture: alt upscaler 4x_ultrasharp (downscale)."],
    conf=(0.7, 0.5, 0.6, 0.75))
add(id="photography", name="Photography book / documentary / travel / nature", mode="cover",
    ages=["adult", "13-17"], genres=["photography", "travel", "nature", "documentary"],
    kw=["photography", "photo book", "landscape photo", "travel photo", "nature photography", "documentary", "35mm", "film photo"],
    w=1024, h=1536, dw=640, dh=960, steps=36, cfg=3.5, sampler=15, alt=17, up="realesrgan_x2plus_f16.ckpt", alt_up="remacri_4x_f16.ckpt",
    scene="Photographic book cover. A misty alpine lake at sunrise, shot on a full-frame camera with a 35mm lens, natural light, soft fog, true-to-life color, fine film grain, calm sky area at the top for the title.",
    text=T("Silent Peaks", "Wild Places Series", "Juniper & Ash Press",
           "in thin elegant white sans-serif capitals in the sky", "in small white capitals above the title",
           "in small white capitals at the bottom center"),
    neg="illustration, painting, cgi, oversaturated hdr, plastic, heavy vignette, oversharpened, lens flare, misspelled text, garbled letters, extra words, watermark",
    why="CFG 3.5 avoids over-contrasty HDR look. Camera/lens words anchor photo realism. Light, thin lettering fits photo covers.",
    tune=["Too CGI: add film stock, 'natural imperfections'.", "Soft: remacri upscaler."],
    conf=(0.7, 0.5, 0.6, 0.75))
add(id="photorealism", name="Photorealism / hyperreal portraits and still life", mode="cover",
    ages=["adult"], genres=["photorealism", "portrait", "still life", "biography", "memoir"],
    kw=["photorealistic", "photorealism", "hyperrealistic", "hyperreal", "realistic portrait", "memoir cover", "biography", "lifelike"],
    w=1024, h=1536, dw=640, dh=960, steps=40, cfg=3.5, sampler=15, alt=17, up="realesrgan_x4plus_f16.ckpt", alt_up="remacri_4x_f16.ckpt",
    scene="Hyperrealistic photoreal cover photograph. A weathered elderly potter with clay-dusted hands at a wheel, natural window light, visible skin texture and fine hair, 85mm portrait lens, shallow depth of field, muted earthy tones, clear dark wall area at the top for the title.",
    text=T("Hands of Clay", "Lives Well Lived", "North Harbor Books",
           "in refined cream serif capitals at the top", "in small cream capitals above the title",
           "in small cream capitals at the bottom center"),
    neg="plastic skin, airbrushed, cartoon, illustration, uncanny, extra fingers, deformed hands, oversmoothed, beauty filter, misspelled text, garbled letters, extra words, watermark",
    why="Steps 40 and CFG 3.5 favour natural skin and fine texture. Use only fictional people (no real named persons).",
    tune=["Waxy skin: CFG 3.0, add 'pores, natural imperfections'.", "4x file large: downscale or use x2plus."],
    conf=(0.65, 0.5, 0.6, 0.72), up_scale_note=True)
add(id="editorial_illustration", name="Illustration book / editorial / risograph style", mode="cover",
    ages=["adult", "13-17", "9-12"], genres=["illustration book", "editorial", "graphic", "art book"],
    kw=["illustration book", "editorial illustration", "risograph", "gouache", "ink and wash", "limited palette", "poster style", "flat illustration"],
    w=1024, h=1536, dw=640, dh=960, steps=34, cfg=4.0, sampler=10, alt=15, up="realesrgan_x2plus_f16.ckpt", alt_up="realesrgan_x4plus_anime_6b_f16.ckpt",
    scene="Editorial book illustration cover in ink and gouache with a limited four-color risograph palette of teal, coral, mustard and cream. A surreal giant paper boat carries a tiny city across the night sky, bold simple shapes, subtle paper grain, flat color layers with slight misregistration.",
    text=T("Paper Skies", "The Atlas of Dreams", "Juniper & Ash Press",
           "in bold hand-cut sans-serif capitals at the top", "in small capitals above the title",
           "in small capitals at the bottom center"),
    neg="photorealistic, 3d render, glossy gradient, cluttered, generic stock art, extra colors, misspelled text, garbled letters, extra words, watermark, blurry",
    why="Named limited palette controls colour; Euler A Trailing keeps hand-made feel. CFG 4 holds palette and text.",
    tune=["Too many colours: repeat palette in prompt end.", "Too clean: add 'misregistered print, grain'."],
    conf=(0.7, 0.55, 0.65, 0.75))

# ---------------- build helpers ----------------
def conf_overall(c):
    s, sa, u, p = c
    return round(0.4*s + 0.2*sa + 0.2*u + 0.2*p, 2)

def prompt_of(p):
    return p["scene"] + (" " + text_clause(p["text"]) if p["text"] else "")

def esc(s):
    for bad in ("$", "`", "!"):
        assert bad not in s, f"unsafe char {bad!r} in prompt: {s[:50]}"
    return s.replace("\\", "\\\\").replace('"', '\\"')

def cmd(p, tier="final"):
    up = p["up"]; scale = UPSCALERS[up][0]
    return (
        "draw-things-cli generate \\\n"
        f"--model {MODEL} \\\n"
        f'--output "{OUT_DIR_EXPR}/qwen_{p["id"]}.png" \\\n'
        f'--prompt "{esc(prompt_of(p))}" \\\n'
        f'--negative-prompt "{esc(p["neg"])}" \\\n'
        f'--width {p["w"]} --height {p["h"]} --steps {p["steps"]} --cfg {p["cfg"]} \\\n'
        "--config-json '{\n"
        f'"sampler": {p["sampler"]},\n'
        f'"upscaler": "{up}",\n'
        f'"upscalerScaleFactor": {scale}\n'
        "}'"
    )

def draft_cmd(p):
    return (
        "draw-things-cli generate \\\n"
        f"--model {MODEL} \\\n"
        f'--output "{OUT_DIR_EXPR}/qwen_{p["id"]}_draft.png" \\\n'
        f'--prompt "{esc(prompt_of(p))}" \\\n'
        f'--negative-prompt "{esc(p["neg"])}" \\\n'
        f'--width {p["dw"]} --height {p["dh"]} --steps 20 --cfg {p["cfg"]} \\\n'
        "--config-json '{\n"
        f'"sampler": {p["sampler"]}\n'
        "}'"
    )

def out_px(p):
    s = UPSCALERS[p["up"]][0]
    return [p["w"]*s, p["h"]*s]

# ================= JSON =================
def build_json():
    profiles = []
    for p in PROFILES:
        s, sa, u, pr = p["conf"]
        ov = conf_overall(p["conf"])
        up_scale = UPSCALERS[p["up"]][0]
        is_cover = p["mode"] == "cover"
        pre = ["intent_resolved_to_this_profile", "aspect_ratio_matches_target_trim"]
        post = ["output_exists", f"output_px_equals_{p['w']*up_scale}x{p['h']*up_scale}"]
        if is_cover:
            pre += ["text_elements<=3", "each_text_string_in_double_quotes_in_prompt", "title<=6_words", "no_real_brand_character_or_living_artist_names", "'text' NOT in negative prompt"]
            post += ["ocr_text_matches_title_series_publisher_exact", "no_extra_or_duplicate_text", "no_text_cropped_at_edges", "title_contrast_legible_at_thumbnail_200px"]
        else:
            pre += ["no_text_requested", "'text' and 'watermark' present in negative prompt", "pure_white_background_requested"]
            post += ["grayscale_mean>=235", "mid_gray_pixel_fraction<=0.08 (heuristic)", "no_filled_black_regions>25%", "all_outlines_closed_visual_check", "no_text_or_signature"]
        pr_obj = {
            "id": p["id"], "name": p["name"], "goal": f"Generate a print-ready {p['mode']} image: {p['name']}.",
            "mode": p["mode"], "aspect_ratio": f"{p['w']}:{p['h']}",
            "match": {"keywords_any": p["kw"], "genres_any": p["genres"], "age_groups_any": p["ages"],
                      "mode_hint_words": (["cover", "title", "series", "publisher"] if is_cover else ["page", "interior", "inside", "pages to color", "line art"])},
            "candidate_settings": [
                {"tier": "draft", "purpose": "prompt/composition check", "width": p["dw"], "height": p["dh"], "steps": 20, "cfg": p["cfg"],
                 "sampler": {"id": p["sampler"], "name": SAMPLERS[p["sampler"]]}, "upscaler": None},
                {"tier": "final", "recommended": True, "width": p["w"], "height": p["h"], "steps": p["steps"], "cfg": p["cfg"],
                 "sampler": {"id": p["sampler"], "name": SAMPLERS[p["sampler"]]},
                 "upscaler": {"file": p["up"], "scale": up_scale, "config_keys": {"upscaler": p["up"], "upscalerScaleFactor": up_scale}},
                 "output_px": out_px(p)},
                {"tier": "alt_sampler", "same_as": "final", "sampler": {"id": p["alt"], "name": SAMPLERS[p["alt"]]},
                 "use_when": "final output shows sampler-specific artefacts or user wants a different look"},
                {"tier": "alt_upscaler", "same_as": "final",
                 "upscaler": {"file": p["alt_up"], "scale": UPSCALERS[p["alt_up"]][0]},
                 "use_when": "edges too soft/hard or texture wrong"},
            ],
            "tuning_ranges": {"steps": [max(20, p["steps"]-6), p["steps"]+8], "cfg": [round(p["cfg"]-0.5, 1), round(p["cfg"]+1.0, 1)],
                              "samplers_allowed": sorted({p["sampler"], p["alt"]})},
            "constraints": {
                "model": MODEL,
                "width_height_multiple_of": 64,
                "max_text_elements": 3 if is_cover else 0,
                "text_in_negative_prompt": "forbidden" if is_cover else "required",
                "downscale_after_4x_upscale": bool(p.get("up_scale_note")) or up_scale == 4,
                "print_note": "Front-cover image only; spine/back/bleed assembled in layout software.",
            },
            "prompt": {"example": prompt_of(p), "scene_style": p["scene"],
                       "text_clause_template": (text_clause(p["text"]) if p["text"] else None),
                       "structure": ["medium/format", "subject+action", "composition+text space", "palette/lighting/texture", "text clause"] if is_cover
                                    else ["format (coloring page)", "subject", "line rules (weight, white bg, closed shapes)", "composition/margins"],
                       "length_words": [60, 150] if is_cover else [35, 90]},
            "negative_prompt": {"recommended": p["neg"],
                                "never_include": (["text", "letters", "typography", "words", "title"] if is_cover else []),
                                "rule": "Negate only things absent from the positive prompt; <=25 terms."},
            "confidence": {"overall": ov, "settings": s, "sampler": sa, "upscaler": u, "prompt": pr,
                           "basis": "Steps/CFG from community Qwen-Image-2512 ranges; sampler/upscaler genre mapping is heuristic. A/B test 3 seeds."},
            "tips": p["tune"], "why": p["why"],
            "validation": {"pre_run": pre, "post_run": post,
                           "pass_rule": "all post_run checks pass on >=1 of 4 seeds",
                           "max_retries": 3},
            "example_command_final": cmd(p), "example_command_draft": draft_cmd(p),
        }
        profiles.append(pr_obj)

    doc = {
        "schema_version": "1.0",
        "generated_for": "AI agent / recommendation engine",
        "target": {"tool": "draw-things-cli generate", "model": MODEL, "hardware": "MacBook Pro M4, 12-core, 48GB unified memory"},
        "facts": {
            "verified": [
                "Sampler integer enum (Draw Things SamplerType) as listed in enums.samplers, from mirrored Draw Things source (3 sources agree).",
                "config-json carries sampler as integer (Draw Things config docs/clients).",
                "Qwen-Image-2512 community ranges: steps 20-50 (30-40 typical), CFG ~2.5-4 base model, euler-family samplers; lower CFG first if letters deform.",
                "Known issue: qwen_image_2512 q8p can yield NaN/blue/black final image for some prompts (draw-things-community #136).",
            ],
            "unverified_must_check_once": [
                "config-json keys 'upscaler' and 'upscalerScaleFactor' accepted by the installed CLI; fallback flags: --upscaler <file> --upscaler-scale <2|4>.",
                "Exact upscaler filenames; list with: ls ~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models | grep -i -E 'esrgan|sharp|remacri'",
                "Precedence when both flag and config-json set the same field (examples never duplicate fields).",
                "Per-genre sampler choice and CFG offsets are heuristics, not benchmarks.",
            ],
        },
        "enums": {
            "samplers": {str(k): v for k, v in SAMPLERS.items()},
            "preferred_samplers": {"10": "soft/painterly/organic", "15": "crisp lines, text, detail", "17": "alt for photo", "0": "legacy alt for line art"},
            "upscalers": {k: {"scale": v[0], "best_for": v[1]} for k, v in UPSCALERS.items()},
            "aspect_sizes_px": {
                "2:3 final": [1024, 1536], "2:3 draft": [640, 960], "0.69 anime": [832, 1216],
                "3:4 interior": [768, 1024], "0.76 interior large": [1024, 1344], "1:1": [1024, 1024],
            },
            "print_targets_px_300dpi": {"6x9in": [1800, 2700], "8.5x11in": [2550, 3300], "8.5in_square": [2550, 2550], "8x10in": [2400, 3000]},
        },
        "global_defaults": {
            "model": MODEL, "seed": "random; store used seed", "batch": "4 seeds at draft tier, pick best",
            "output_dir": OUT_DIR_EXPR, "output_path_note": "Use double-quoted $HOME; '~' is not expanded inside single quotes.",
            "memory_notes": ["48GB handles 1024x1536 comfortably", "set tiledDecoding true if either side >1280", "close other heavy apps for 4x upscales"],
            "fallback_if_blue_or_black_output": ["change seed", "reword prompt slightly", "try alt sampler", "lower resolution one step", "see draw-things-community #136"],
        },
        "age_modifiers": {
            "3-5": {"text": "<=4 words title, huge rounded letters", "palette": "primary, high contrast", "composition": "one subject, simple background", "negative_add": ["scary", "dark", "realistic", "clutter", "sharp teeth"], "cfg_delta": 0},
            "6-8": {"text": "<=6 words, whimsical serif/rounded", "palette": "warm, saturated, soft light", "composition": "1-2 characters, layered depth", "negative_add": ["horror", "gore", "harsh shadows"], "cfg_delta": 0},
            "9-12": {"text": "<=6 words, bold sans", "palette": "vivid, high contrast", "composition": "dynamic, informative", "negative_add": ["gore", "dense paragraphs"], "cfg_delta": 0},
            "13-17": {"text": "short punchy, condensed caps", "palette": "stylised, restrained or neon", "composition": "poster-like, negative space", "negative_add": ["childish", "clip art"], "cfg_delta": 0},
            "adult": {"text": "refined serif/metal/thin sans", "palette": "premium, restrained", "composition": "symmetry/space/elegance", "negative_add": ["childish", "cartoon (unless wanted)"], "cfg_delta": 0},
        },
        "profiles": profiles,
        "selection_rules": {
            "algorithm": [
                "1. Extract: mode (cover vs interior page), medium/style, genre, age group, text strings, size/print target, speed vs quality.",
                "2. mode: words 'page/interior/inside/pages to colour' => interior; 'cover/title/series/publisher' or any text request => cover. Interior profiles never contain text.",
                "3. Style beats genre: explicit medium (watercolor, oil, pencil, anime, photo) selects that profile; genre/age then tunes prompt and negatives.",
                "4. Score each profile: +3 style keyword, +2 genre match, +2 age match, +1 mode hint; pick highest, list runner-up.",
                "5. Apply age_modifiers to prompt and negative; keep within profile.tuning_ranges.",
                "6. If user wants speed/preview => draft tier; if print/final => final tier incl. upscaler; if low memory => draft dims, no upscaler.",
                "7. Emit command from example_command_final with user's text substituted; run validation.pre_run.",
            ],
            "tie_breakers": ["prefer higher confidence.overall", "prefer profile with matching age group", "prefer cover over interior if text requested"],
            "conflicts": [
                {"if": "coloring book + wants title text", "then": "use kids_coloring_cover or adult_coloring_cover; interior pages separately"},
                {"if": "photorealistic + children's book", "then": "use kids_storybook_6_8 and warn photoreal is unusual for ages <9"},
                {"if": "anime + adult coloring", "then": "use adult_coloring_line_art with anime subject in prompt"},
                {"if": "more than 3 text elements or title>6 words", "then": "shorten or move extra text to layout software"},
                {"if": "real brand, character, person or living-artist style requested", "then": "decline that element; substitute original description"},
            ],
            "ask_user_only_when": ["overall confidence <0.6 and mode ambiguous", "no title/series/publisher text given for a cover", "print size unknown and user wants print-ready"],
            "default_when_unknown": {"profile": "editorial_illustration", "mode": "cover", "age": "adult"},
        },
        "validation_global": {
            "ocr": "If tesseract is available: compare recognised text to requested strings (case-insensitive, edit distance <=1 per string).",
            "line_art_check": "Convert to grayscale; require mean>=235 and mid-gray fraction (30-220) <=8%.",
            "visual_checks": ["hands/fingers", "faces", "text edge crop", "stray symbols"],
            "iteration_policy": "Up to 3 retries: new seed -> alt sampler -> steps+6/cfg-0.5 (text) or cfg+0.5 (line art).",
        },
        "failure_playbook": [
            {"symptom": "garbled/misspelled text", "actions": ["shorten strings", "cfg -0.5", "steps +6", "move text to simple area", "new seed"]},
            {"symptom": "blurry/soft", "actions": ["steps +6", "switch sampler 10->15", "alt upscaler 4x_ultrasharp", "raise base resolution"]},
            {"symptom": "gray fills in line art", "actions": ["cfg +0.5", "add 'solid pure black ink lines only'", "add color/shading/gray to negative"]},
            {"symptom": "over-smooth plastic look", "actions": ["cfg -0.5", "add texture words", "remacri or x2plus upscaler"]},
            {"symptom": "blue/black/noise image", "actions": ["new seed", "reword prompt", "alt sampler", "lower resolution", "ref draw-things-community #136"]},
            {"symptom": "wrong colour/medium", "actions": ["put medium first in prompt", "strengthen negative for wrong medium", "cfg +0.5"]},
        ],
    }
    return doc

# ================= MARKDOWN =================
def build_md():
    L = []
    A = L.append
    A("# Qwen-Image-2512 Book Cover Settings Guide for draw-things-cli\n")
    A(f"Target: `{MODEL}` on MacBook Pro M4 (48 GB). Consumer: AI agent / recommendation engine. Companion file: `book-cover-recommendation-rules.json` (same data, machine-readable).\n")
    A("## 1. Confidence legend\n")
    A("- **Verified**: sampler integers; Qwen-Image-2512 community ranges (steps 20-50, CFG ~2.5-4, euler-family samplers).")
    A("- **Unverified, check once**: `upscaler` / `upscalerScaleFactor` config keys; exact upscaler filenames; flag-vs-config precedence. Fallback flags: `--upscaler <file> --upscaler-scale <2|4>`.")
    A("- **Heuristic**: per-genre sampler, CFG offsets, upscaler pairing. A/B test 3 seeds before trusting.")
    A("- Known issue: q8p Qwen 2512 can output NaN/blue/black for some prompts (draw-things-community #136). Change seed/prompt, alt sampler, or lower resolution.\n")
    A("## 2. Sampler reference (numeric value in brackets)\n")
    A("| Sampler | Use for |\n|---|---|")
    for i, why in [(10, "Soft, painterly, organic, storybook, watercolor, oil, pencil (default for soft styles)"),
                   (15, "Crisp lines, typography, line art, anime, photo, concept art (default for sharp styles)"),
                   (17, "Alt for photo/realism"), (0, "Legacy alt for line art/mandala"), (1, "More random variety; less repeatable")]:
        A(f"| {sn(i)} | {why} |")
    A("\nFull enum: " + ", ".join(sn(i) for i in SAMPLERS) + ".\n")
    A("## 3. Upscaler reference (set in `--config-json`)\n")
    A("| File | Scale | Best for |\n|---|---|---|")
    for k, (s, d) in UPSCALERS.items():
        A(f"| `{k}` | {s}x | {d} |")
    A("\nVerify filenames: `ls ~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models | grep -i -E 'esrgan|sharp|remacri'`. After 4x, downscale to print size.\n")
    A("## 4. Universal defaults\n")
    A("- Sizes: multiples of 64. Cover 2:3 = 1024x1536 (draft 640x960). Interior 3:4 = 768x1024 or 1024x1344. Mandala 1024x1024.")
    A("- Steps 28-40 final, 20 draft. CFG 3.5-5.5 (lower = organic, higher = strict/line art). Qwen uses true CFG, so negative prompts matter.")
    A("- Workflow: draft 4 seeds -> pick -> rerun final with that `seed` in config-json -> upscale. Composition may shift across resolutions; re-draft at final size if it matters.")
    A("- `tiledDecoding: true` in config-json if any side >1280. Output paths use `\"$HOME/...\"` because `~` does not expand in single quotes. Run `mkdir -p \"$HOME/Dev/tmp\"` once.")
    A("- Print px at 300 dpi: 6x9in = 1800x2700; 8.5x11in = 2550x3300; 8.5in square = 2550x2550. Image is front cover only; spine/back/bleed in layout software.\n")
    A("## 5. Prompt strategy\n")
    A("1. Natural sentences, not tag soup (Qwen text encoder is an LLM). 60-150 words for covers, 35-90 for line-art pages.")
    A("2. Order: medium -> subject/action -> composition (reserve text area) -> palette/lighting/texture -> text clause.")
    A("3. Text: exact strings in double quotes, position + typography style for each, max 3 elements (title, series, publisher), title <=6 words, end with `All text spelled exactly as written`.")
    A("4. Medium words first and repeated once at the end for painterly styles.")
    A("5. Line art: always state `pure white background, no shading, closed shapes, uniform line weight`.")
    A("6. No real brands, characters, people, or living-artist styles. Describe original look instead.")
    A("7. Avoid `$`, backticks, `!` in prompts (shell-safe). Avoid weight syntax like `(word:1.3)`; unverified for Qwen.\n")
    A("## 6. Negative prompt strategy\n")
    A("1. 10-25 terms in four groups: wrong-medium, quality artefacts, text-failure, audience-safety.")
    A("2. Covers: NEVER put `text`, `letters`, `words` alone in the negative. Use `misspelled text, garbled letters, extra words, watermark`.")
    A("3. Interior pages: DO include `text, watermark` plus `color, gray, shading, gradient`.")
    A("4. Never negate something the positive prompt asks for. Add terms only after seeing a failure.")
    A("5. Age tuning: young kids add `scary, dark, realistic, sharp teeth`; teens add `childish, clip art`; adult art adds `cartoon` unless wanted.\n")
    A("## 7. Age modifiers\n")
    A("| Age | Text | Palette | Composition | Negative add |\n|---|---|---|---|---|")
    A("| 3-5 | <=4 words, huge rounded | primary, high contrast | one subject | scary, dark, realistic, clutter |")
    A("| 6-8 | <=6 words, whimsical | warm saturated | 1-2 characters, depth | horror, gore, harsh shadows |")
    A("| 9-12 | <=6 words, bold sans | vivid | dynamic, informative | gore, dense paragraphs |")
    A("| 13-17 | short, condensed caps | stylised/neon or restrained | poster-like space | childish, clip art |")
    A("| adult | refined serif/thin sans | premium restrained | symmetry, space | childish |\n")
    A("## 8. Profiles (settings + executable example)\n")
    A("Each example is the **final** tier. Draft = same prompt, width/height from table, `--steps 20`, no upscaler.\n")
    for p in PROFILES:
        up = p["up"]; sc = UPSCALERS[up][0]
        A(f"### `{p['id']}`: {p['name']}\n")
        A(f"- **Mode**: {p['mode']} | **Ages**: {', '.join(p['ages'])} | **Confidence**: {conf_overall(p['conf'])}")
        A(f"- **Final**: {p['w']}x{p['h']}, steps {p['steps']}, CFG {p['cfg']}, sampler {sn(p['sampler'])}, upscaler `{up}` x{sc} -> {p['w']*sc}x{p['h']*sc}")
        A(f"- **Draft**: {p['dw']}x{p['dh']}, steps 20 | **Alt sampler**: {sn(p['alt'])} | **Alt upscaler**: `{p['alt_up']}`")
        A(f"- **Why**: {p['why']}")
        A("- **Tune**: " + " ".join(p["tune"]))
        A("")
        A("```bash\n" + cmd(p) + "\n```\n")
    A("## 9. Troubleshooting\n")
    A("| Symptom | Actions (in order) |\n|---|---|")
    for f in build_json()["failure_playbook"]:
        A(f"| {f['symptom']} | {'; '.join(f['actions'])} |")
    A("\n## 10. Agent decision procedure (short)\n")
    A("Resolve mode (cover vs interior) -> style/medium -> genre -> age -> pick profile (see JSON `selection_rules`) -> apply age modifiers -> choose tier (draft/final/lowmem) -> emit command -> validate (OCR for covers, whiteness check for line art) -> retry up to 3 times using the failure playbook.\n")
    return "\n".join(L)

if __name__ == "__main__":
    doc = build_json()
    with open("book-cover-recommendation-rules.json", "w") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    with open("draw-things-qwen-book-cover-guide.md", "w") as f:
        f.write(build_md())
    print("profiles:", len(PROFILES))
