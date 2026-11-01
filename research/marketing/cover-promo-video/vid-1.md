# `/create-animation` skill + pipeline

I have built a sophisticated AI-driven (Claude/Agentic) publishing framework for automatically and autonomously generating all kinds of digital/printable products, like Kids Reading Books, Illustrations books, Storybooks, Kids and adults Coloring Books, adults grayscale and Mandala Coloring Books, and so on. Coloring Books would have an alternate version of digital download of individual coloring pages as pdf. My framework uses "draw-things-cli" with qwen_image_2512 and Flux.2-Klein to create book cover images and inner images.

Similar to how `draw-things-cli` is being used for generating the artwork and cover images, I want to create a new separate automated skill+pipeline to create the animated videos (GIFs, mp4, etc) that will be used on Etsy listing mp4 video, Instagram posts, Facebook Ads, etc.

The animation generator should be reusable across the entire publishing business. The same infrastructure can showcase coloring books, mandalas, sketch collections, children's illustrated books and other digital products, with different templates selected by the publishing agent.

## animation pipeline Use cases

I want this new skill to run the animation pipeline in multiple ways, and with each different way,  Claude will ask (using AskUserQuestion tool, always give "Recommended" option where applicable) for different information that will help the skill figure out how the animation, for example whether it's meant for Etsy, Facebook, or personal website, whether the animation should be gif, video, or both, and so on.

Three use cases I can think of:

1. As part of the book/pages creation pipeline, once the book is created, Claude would ask if a video is needed (and which kind is needed, listing video for Etsy, Ad/Promo video for Instagram, Facebook, etc) so that it can kick off with correct framework specific requirements like dimensions etc. It will AskUserQuestions for other generic factors as well, for example, selecting the correct template.

2. Using the skill+pipeline as completely independent `/create-animation` skill, in which case the skill would AskUserQuestion on the platform, the template, images to use, etc. Alternative, the user can just give all the information as prompt text ARGUMENTS to `/create-animation`, and Claude would ask only for any missing info, gaps or clarifications.

3. show an ad for "Smoking is bad for health" with [Company-ABC] Branding, and Claude will figure out what to do, and AskUserQuestion for any gaps or clarifications.

## video templates

The framework would implement four separate video templates for each platform (Etsy listing, Instagram promo, etc) final solution should end up with that can be selected for the specific platform. Before selecting the four final templates for each platform, that should be become part of the framework to chose from, Claude should do A/B testing to reach the final solution+templates.

## Suggested tools

Python/Pillow can be used for image logic, FFmpeg for MP4 export

Python/Pillow can be used for image logic, and then, FFmpeg puts the frames in motion. So what will happen is:
- Draw Things: creates the artwork.
- Pillow: creates or modifies the individual pictures.
- FFmpeg: turns those pictures into a video.
- AI agent: decides which workflow to run and with what settings.

For coloring pages, we can use high-quality source images, resize them with Pillow's Lanczos resampling where appropriate, generate clean animation frames, and encode the final video with FFmpeg using H.264 at a sensible bitrate. Avoid repeatedly resizing and re-encoding the same images, as that can degrade fine details.


# image logic and video options

Imagine we have generated a beautiful grayscale coloring page of a majestic queen using Qwen or Klein. We want to turn that single image into an attractive 8-second promotional video.

Each tool will have a different job:

- The input image: One finished grayscale illustration from Draw Things.
- Python/Pillow decides what each frame looks like: Full grayscale image, Cropped detail or zoom, etc
- FFmpeg puts the frames in motion, and generates the Final MP4 video - Timed frames, smooth transitions, music if desired, and final encoding.

Pillow is a good image-manipulation library. It can resize, crop, blend and combine images. It doesn't need to understand video; it just prepares the pictures that will become the video.

Think of it this way:

- Draw Things: creates the artwork.
- Pillow: creates or modifies the individual pictures.
- FFmpeg: turns those pictures into a video.
- The AI agent: decides which workflow to run and with what settings.

## Five concrete examples of image logic

### Example A — Slowly zoom into the artwork

We have one image. We want the camera to move closer to the queen's face over three seconds.

Frame 1: 100% view
Frame 36: Closer crop

The logic is simply:

```
Load the original illustration.

For each video frame:
    Calculate the zoom amount.
    Crop a slightly smaller area around the face.
    Resize the crop to the video dimensions.
    Save the frame.

Ask FFmpeg to combine the frames at 24 fps.
```

We haven't generated any new artwork. We've created the illusion of camera movement from one image.

### Example B — Reveal a colored version from left to right

Suppose we have two images of the same queen:

- `grayscale.png`
- `colored.png`

The logic is:

```
For each frame:
    Calculate how far the reveal has progressed.
    Keep the left portion of the colored image visible.
    Keep the remaining portion grayscale.
    Combine both portions into one image.
    Save the frame.

Encode all frames as an MP4.
```

Pillow can create the composite using masks.

For example, the reveal might progress through 0%, 10%, 20% ... to 100% over the animation. The result is a smooth transition, provided both images are aligned.

### Example C — Flip through four coloring pages

Imagine selling a 30-page grayscale coloring book. We want to showcase four of its best pages.

```
Select pages 3, 8, 14 and 22.

For each selected page:
    Resize it to fit the video canvas.
    Add a subtle shadow and background.
    Display it for 1.5 seconds.
    Crossfade into the next page.

Add a branded closing frame.
Export the sequence as MP4.
```

The background, shadow and layout are generated by the code. The artwork itself remains unchanged.

### Example D — Add a branded title and end card

- We want the video to begin with: `MAJESTIC GRAYSCALE COLORING`
- Then show three pages and finish with: `30 INTRICATE DESIGNS · INSTANT DOWNLOAD`

The Python code draws the text over a designed background, positions the book cover and adds the appropriate images. FFmpeg controls how long each composition appears.

This is especially useful because the agent can populate the text automatically from each book's metadata.

### Example E — Create a subtle premium background

We want a decorative background behind a coloring page instead of plain white.

The code could:

1. Create a dark purple or cream background.
2. Add a soft gradient or subtle texture.
3. Place the cover or page in the center.
4. Add a shadow and a gentle zoom.
5. Add a title and export the video.

We can create the gradient and composite the artwork using Pillow, then animate the background or camera movement with FFmpeg. No AI video generation is necessary for this effect.

## Draw Things for generating AI video

Draw Things supports image-to-video and text-to-video workflows. The video models I have installed are SkyReels-V1, Wan Video, and LTX-2.3 22B Distilled (8 bit S).

### Should we generate background videos with Draw Things?

Yes, but selectively. I would add it as an optional creative stage in the pipeline rather than use AI video generation for every product.

For example, an AI-generated video could provide:

- A softly moving, magical background behind a fantasy coloring-book cover.
- Floating particles, drifting mist or subtle atmospheric movement.
- A cinematic fantasy scene that sets the mood before the coloring pages appear.
- An animated opening shot for a collection of mandalas or artistic sketches.

Then FFmpeg could combine that video with the actual coloring pages, title, transitions and end card.

### Suggestion for combining all four tools

Here is the architecture I would use for the publishing framework.

- AI publishing agent: Recommends the animation style based on book type and marketing goal, and confirms with user.
- Draw Things (Qwen/Klein) creates stills, artwork, covers and colored counterparts.
- Draw Things — AI video — Optional atmospheric footage or short animated opening.
- Python/Pillow: Prepare images, compose layouts, create masks, generate zooms and reveal frames.
- FFmpeg: Combine the AI footage and still-image sequences, add transitions, set timing and encode MP4.
- Final listing media: MP4 for Etsy, optional GIF for other promotional channels, and static listing images.

### Example: an 8-second fantasy coloring-book promo

| Time    | What the buyer sees                           | How it's created              |
| ------- | --------------------------------------------- | ----------------------------- |
| 0–2 sec | Magical, misty fantasy atmosphere             | Optional Draw Things AI video |
| 2–4 sec | Book cover and title appear                   | Pillow composition + FFmpeg   |
| 4–6 sec | Grayscale illustration with a slow zoom       | Pillow frames + FFmpeg        |
| 6–8 sec | A color reveal, followed by the product title | Pillow masks + FFmpeg         |

These timings are illustrative. We/Claude might produce a completely professional version without any AI-generated video at all.

## My recommendation for the first implementation

We can build two rendering modes:

Mode A — Standard automated promo

- Uses existing book artwork.
- Generates zooms, wipes, page flips, titles and end cards.
- Requires Python/Pillow and FFmpeg only.
- Fast, predictable and easy to batch across hundreds of products.

Mode B — AI-enhanced promo

- Uses Draw Things to generate a short atmospheric video.
- Combines that footage with the actual product artwork using FFmpeg.
- Applies quality checks for distracting motion, text readability and artwork fidelity.
- Runs only for products where cinematic motion adds real value.

Keep the actual coloring pages crisp and prominent. Use AI-generated video as supporting atmosphere, not as a replacement for showing buyers the product they will receive.

One final distinction: AI-generated video is more computationally expensive and less predictable than simple frame animation. On the M4 MacBook Pro with 48 GB of unified memory, test the chosen video model's memory requirements, generation time and output quality before adding it to a high-volume production workflow.

## Inspirational mp4 videos

Here are some example videos as an example of what the different videos might look like, based on the template selected. Note that these are just examples, and you might suggest 10 completely different variations as templates. These templates should be easy to modify by a human for example, the image numbers to include, the number of images to show, the time it 

https://v.etsystatic.com/c/video/upload/ac_none,du_15,q_auto:good/gzxvrj5syfqfonh0qqzl.mp4
https://v.etsystatic.com/c/video/upload/ac_none,du_15,q_auto:good/Majestic_Rivers_Etsy_fzlx33.mp4
https://v.etsystatic.com/c/video/upload/ac_none,du_15,q_auto:good/0119_vcoatd.mp4
https://v.etsystatic.com/c/video/upload/ac_none,du_15,q_auto:good/0119_1_qyjdoj.mp4

# TASK

I'm using ClaudeCode for my framework, but ClaudeCode has WebSearch disabled, so I want you to create a comprehensive plan for this that I can give to my ClaudeCode to implement without having to do a WebSearch.

Include any additional skills, agents, scripts, rules, standards, patterns, templates to be added to my existing `.claude/` framework