# cover-promo-video

I have built a sophisticated AI-driven (Claude/Agentic) publishing framework for automatically and autonomously generating all kinds of digital/printable products, like Kids Reading Books, Illustrations books, Storybooks, Kids and adults Coloring Books, adults grayscale and Mandala Coloring Books, and so on. Coloring Books would have an alternate version of digital download of individual coloring pages as pdf. My framework uses "draw-things-cli" with qwen_image_2512 and Flux.2-Klein to create book cover images and inner images.

Similar to how `draw-things-cli` is being used for generating the artwork and cover images, I want to create a new separate automated skill+pipeline to create the animated GIFs and mp4 videos that will be used on Etsy listing mp4 video.

I want this new skill to run the gif/video pipeline in multiple ways:

- As part of the book/pages creation pipeline, once the book is created, Claude would kick off so that Claude factors in that some of the images would be generated as color-filled. At the end of the creation of the coloring book and book cover, Claude could ask the user to select the template  could be selected 

The final solution should end up with four separate video templates that can be selected for Etsy listing preview. Similarly, four separate video templates can be created for instagram promo. Before selecting the final templates that should be become part of the framework to chose from, Claude should do A/B testing to reach the final solution+templates.

Python/Pillow for image logic, FFmpeg for MP4 export

Python/Pillow will be used for image logic, and then, FFmpeg puts the frames in motion. So what will happen is:
- Draw Things: creates the artwork.
- Pillow: creates or modifies the individual pictures.
- FFmpeg: turns those pictures into a video.
- Your AI agent: decides which workflow to run and with what settings.

---

I'm using ClaudeCode for my framework, but ClaudeCode has WesSearch disabled, so I want you to create a comprehensive plan for this that I 

Here are some example videos as an example of what the different videos might look like, based on the template selected. Note that these are just examples, and you might suggest 10 completely different variations as templates. These templates should be easy to modify by a human for example, the image numbers to include, the number of images to show, the time it 

https://v.etsystatic.com/c/video/upload/ac_none,du_15,q_auto:good/gzxvrj5syfqfonh0qqzl.mp4
https://v.etsystatic.com/c/video/upload/ac_none,du_15,q_auto:good/Majestic_Rivers_Etsy_fzlx33.mp4
https://v.etsystatic.com/c/video/upload/ac_none,du_15,q_auto:good/0119_vcoatd.mp4
https://v.etsystatic.com/c/video/upload/ac_none,du_15,q_auto:good/0119_1_qyjdoj.mp4

