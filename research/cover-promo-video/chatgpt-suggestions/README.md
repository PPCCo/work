# AI Animation Generator — `/create-animation` Skill & Pipeline



Recommended architecture

&#x20;Technical blueprint · 31 October 2026



My recommendation is to build this as a standalone, reusable animation production subsystem within your existing AI publishing framework, rather than as a collection of video-generation scripts.

The key architectural decision is to separate five concerns:

1. Creative direction: Claude determines what the video should communicate, who it is for, and which creative approach is appropriate.
2. Storyboard and templates: A structured storyboard describes each scene, its assets, text, duration, transitions and motion.
3. Asset preparation: Python/Pillow prepares artwork, layouts, page compositions, masks, backgrounds, overlays and animation frames.
4. Motion and rendering: FFmpeg assembles, animates, transitions, mixes audio and encodes the finished video.
5. Optional AI video generation: Draw Things supplies atmospheric footage or animated scenes where conventional animation would benefit from it.

This architecture means the same renderer can produce videos for a children's storybook, a grayscale coloring book, a mandala collection, a sketchbook, a digital art collection, or an unrelated advertisement such as a public-health campaign.

It also means that changing a video template does not require changing the rendering engine.

## 1. The most important architectural decisions

I would establish these principles before implementation:

| Decision                | Recommendation                                         |
| ----------------------- | ------------------------------------------------------ |
| Main rendering engine   | Python + Pillow + FFmpeg                               |
| AI image generation     | Existing Draw Things Qwen / Flux workflows             |
| AI video generation     | Optional Draw Things adapter                           |
| Animation definition    | JSON storyboard / scene specification                  |
| Template implementation | Reusable Python template classes                       |
| Platform requirements   | Versioned platform profiles                            |
| Creative selection      | Claude agent + template recommendation rules           |
| Human customization     | Editable JSON and optional CLI overrides               |
| Export                  | MP4 primary; GIF and WebM optional                     |
| Quality assurance       | Automated validation + contact sheets + human approval |
| A/B testing             | Structured experiments with versioned variants         |
| Batch processing        | Reusable job runner with resumable stages              |

One particularly important decision: Do not implement the templates as hardcoded FFmpeg command strings.

Instead, templates should produce a standardized animation specification. The rendering engine should interpret that specification.

For example, the same `page_gallery` template could be used with:

- An Etsy listing profile: landscape or portrait, short, silent.
- An Instagram Reel profile: vertical, sound-aware, safe-zone compliant.
- A Facebook Feed profile: feed-oriented 4:5.
- A website profile: configurable dimensions and bitrate.

The template describes the creative presentation; the platform profile describes how it must be delivered.

## 2. Platform requirements that the framework must know

There is an important distinction between technical upload requirements and creative recommendations.

As checked on 31 October 2026, Etsy's official help documentation specifies listing videos of 3–15 seconds, a maximum file size of 100 MB, a minimum resolution of 500 pixels, and an ideal resolution of at least 1080 pixels. It also specifies that audio is removed after upload. Etsy currently allows up to two listing videos per listing.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://help.etsy.com\&sz=32)

Etsy Help+1



This has an important consequence:

Your Etsy template must be designed as a silent product-demonstration video, not as a conventional advertisement that depends on music or narration.

Etsy also recommends showcasing product details, answering common buyer questions and demonstrating products in use. These recommendations are particularly applicable to digital books and printable collections.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.etsy.com\&sz=32)

Etsy



## 3. Deliverables

I've created two Markdown documents and packaged them together.

1\. Complete implementation blueprint

Primary document

Approximately 1,500 lines covering architecture, implementation, agents, skills, scripts, standards and testing.

Download animation implementation blueprint

2\. ClaudeCode implementation prompt

A ready-to-paste instruction document telling ClaudeCode how to inspect your existing framework and implement the blueprint incrementally.

Download ClaudeCode implementation prompt

3\. Complete package

Download both documents as ZIP

## 4. What's covered in the blueprint

The implementation specification includes:

| Area               | Coverage                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------ |
| Platform standards | Etsy, Instagram Reels, Instagram Feed, Facebook Feed and Reels                             |
| Creative templates | 18 initial candidates, six per channel                                                     |
| Template selection | Offline screening, A/B experiments and four final templates per channel                    |
| Claude skills      | `/create-animation`, `/animation-template-lab`, `/animation-review`                        |
| Agents             | Animation Director, Storyboard Architect, Render Engineer, QA Reviewer, Experiment Analyst |
| Python/Pillow      | Layouts, image processing, masks, text, backgrounds and frame preparation                  |
| FFmpeg             | Motion, transitions, video assembly, encoding, audio and GIF                               |
| Draw Things        | Optional AI-video provider and model benchmarking                                          |
| Integration        | Existing book-generation pipeline and independent campaign creation                        |
| Configuration      | JSON schemas, YAML profiles, templates and brand configurations                            |
| Quality            | FFprobe, asset fidelity, safe zones, contact sheets and human approval                     |
| Operations         | CLI, resumable jobs, error handling, batch rendering and output manifests                  |

## 5. Three important recommendations

First: implement standard rendering before AI video.

Get the Pillow/FFmpeg pipeline working perfectly. It should be capable of producing professional marketing videos without loading any AI video model.

Second: make storyboards the central abstraction.

This is probably the most important architectural decision. Claude generates a storyboard; your Python renderer interprets it. This allows you to create new templates without rewriting rendering functionality.

Third: keep template selection evidence-based.

Generate six initial candidates for each channel, evaluate them, select four provisional winners, and subsequently validate their performance using actual marketing metrics.

One technical caveat is documented in the blueprint: the public `draw-things-cli` documentation does not currently establish a supported video-generation CLI command, despite video generation being supported in Draw Things itself. The implementation must verify this rather than assume an interface exists.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+2



My suggested starting point: Give ClaudeCode both documents, start with repository discovery, and implement Phases 0–2 first. That establishes the core renderer and a production-quality Etsy pipeline before expanding into social advertising and AI-generated footage.

The four supplied Etsy video URLs are also recorded in the blueprint as references for later local inspection; I couldn't visually inspect their MP4 streams during this research session.