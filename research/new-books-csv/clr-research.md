I want you to do a comprehensive research and build a similar list of 50 series (each series with 5-8 volumes) but for another publishing company, where I want to publish puzzle books, coloring books, diaries, and any other kind of products. The main criteria is, they should be easy to create using autonomous claude agents that I can easily sell on platforms like Amazon, etsy, ebay, walmart, etc. The products should have a high selling prospect, or untapped niche categories with good demand, or if they are in high demand, then the demand should be high enough that I can easily get a good share of it (for example soduku puzzle books). But note that I have enough soduku puzzle books so don't include those in the list.

The generated CSV list should have these columns: Age Group, Genre (Topic), Set (Series) Name, Book Title, Number, Books in Set, priority

The priority should depend on things like demand, market saturation, etc

---

## Images and Book Cover Skills

I'm using Claude to give prompts to a local install of Klein-4B to generate via ComfyUI MCP Server to generate colored images for kids. The output quality is inconsistent. Sometimes it's good, sometimes bad. Can you think hard and create a "Claude skill" (including any klein-prompt-standards, prompt-audit-agent, python scripts, etc if needed) that would generate prompts for high quality results

---

I have a Claude framework for autonomously creating books for all ages here: https://github.com/PPCCo/publish-book

My book publishing company creates non-fiction books, puzzle books, coloring books, productivity books etc for all age groups.

These are the age groups (`audience`) I have defined in my framework:

- `early-reader-6-8`
- `middle-grade-9-12`
- `teen-13-17`
- `adult-general`

# TASK

Since I sell my books on Amazon/Etsy/ebay/KDP/AppleBooks/etc, and since book covers are the first impression, I need you to add to the above Klein-4B setup or modify any files you created above (to make the cover-generation compatable with the Klein setup), the tools/skills/agents/rules/standards/etc needed to design awesome covers for the books.

Create a comprehensive setup for whatever skills, agents, standards, rules, scripts etc that would be needed for Claude to autonomously create the best book covers (including front cover, back cover, and cover-spine). If there are Claude built in agents for advertizing, media, marketing, designer, publishing, etc, then refer to those skills in the requirements, otherwise create new agents and/or skills and/or standards etc
