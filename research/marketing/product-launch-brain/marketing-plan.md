# Marketing plan (per book) and product-launch-brain (PLB)

The two frameworks `pub-clr` (for multiple product types) and `publish-bk` (for only books) are designed to create products in an autonomous fashion using Claude AI tools and to sell these products on Etsy KDP, Payhip, Gumroad, Shopify, etc.

I asked Claude and ChatGPT to create a comprehensive business plan with a heavy focus on customer demand, feasibility analysis, market fit, and that will be easy to automate using my AI framework (maybe with a bit of enhancement). The plans created by them are in `./business-plan-chatgpt.md` and `./business-plan-claude.md`

## Product-launch-brain (PLB)

Similar to the Image Brain (already exists) and the video generation pipeline, I'm thinking maybe we can enhance the release stage by adding a product-launch-brain (PLB) that will help selecting the right products to create, the content and type of activities, where to publish them and where to market/advertize them, etc.

I also want you to think hard and make a plan how the suggestions and findings in ChatGPT and Claude's business plan can be integrated as part of both the frameworks, The only difference would be, `pub-clr` will have all product types, and `publish-bk` will only have for books. For instance, these research findings can go into the discovery/plan phase so that product is evaluated for feasibility and what content/features should be included in the product, the products to include in a bundle, which platforms to launch on, what kind of ads/videos need to be generated (Instagram, Etsy listing video, Facebook ads and videos, etc), and so on. Those findings will go into the final package, for example, which platforms to advertise on. 

The PLB will also evaluate and select the social/marketing platforms for each product, and build content for the selected platforms post Facebook, Pinterest, TikTok, Instagram Reels and YouTube Shorts as free marketing tools, and whether it's feasible to do paid ads, since the profit margin per item doesn't justify the marketing cost.

For examples, these findings can be really helpful in product selection and market positioning:

- Demand is concentrated in DIY and activity products, not in books
- Price discipline decides whether a KDP book can ever be advertised
- Etsy ads only work above ~$12 for single printables, so maybe bundles are a good idea.

Similarly, other factors that can be to decide the product that will be profitable. For example, we know that most markets are saturated, so PLB can come up with 

## `/launch-new` skill

One of the ways to implement this could be a `/launch-new` skill that can take an open prompt as ARGUMENTS, which may be a path to a file containing pre-researched product or multiple products, or it could be just a hint or product description, or a product category. Here are some basic examples, which by no means is an exhaustive list of examples:

- `/launch-new christmas ideas`
- `/launch-new New Years Activities bundle`
- `/launch-new DIY Holiday Activities`
- `/launch-new Books series for kids learning`

Based on the ARGUMENTS, PLB can use it's own knowledge-base (grounded on the ChatGPT and Claude's business plan) and do further research if needed, and interactively AskUserQuestion if needed to come up with the whole business plan (including research, ideation, creation of product content and advertizing content, audit, audience/SEO strategy, platforms to launch on, platforms to advertize on, video generation for the different platforms, pricing, Build order, Operations, legal, tax and risk, etc)

## Features (Skills & Commands) Consolidation

There might be some parts that are already there in the two frameworks. See if they can be consolidated into the one product-launch-brain (PLB) that you will create, or remove them entirely if they are being superseded by the functionality you're adding to this enhancement (`/launch-new` + PLB).

This might mean either integrating or completely removing some existing commands like `new-product`, or some existing skills like `product-generate`, `product-new`, `product-plan`, `research`, etc. Or they may be kept if it makes sense.

If there is stale info or legacy features that are being superseded by these enhancements, just remove the stale/legacy parts completely as if they were never there. No need to add to memory or add comments on removed or stale parts of the framework

---
