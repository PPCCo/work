I'll build this as a single implementation plan in markdown that Claude Code can work from. First I'm checking your existing framework notes and verifying current platform specs, since Claude Code can't search for them.

I've written the plan as a single markdown file, `create-animation-plan.md` (about 1,000 lines), for you to give to Claude Code. I haven't run any of the pipeline itself. Besides the file-size count, my only check was a quick test that the reveal-mask and easing snippets in it behave correctly at their endpoints.

It's self-contained, so Claude Code won't need WebSearch. I verified the Etsy, Instagram and Facebook video specs today and stored them as a YAML data file with a re-check date. I wasn't able to confirm Pinterest's specs, so that entry is flagged unverified.

**What's in the plan:**
- **Phase 0 discovery:** before building, Claude Code inspects your existing `.claude/` conventions and probes what `draw-things-cli` can actually do for video. Neither is guessed.
- **Build:** the Pillow/FFmpeg engine, the scripts, the agents (director, QC reviewer, A/B judge), rules, standards, skills (including `/create-animation`) and the machine-readable data formats.
- **Templates:** 12 candidates, with every setting a human might change (pages, hold time, transitions) in one editable block per template.
- **All three use cases:** each has an intake flow that asks only for what's missing, with a "Recommended" option listed first. The "Smoking is bad for health" ad follows a draft-first, no-invented-statistics flow.
- **Phased build:** 8 phases, each with its own acceptance test.

**Things to know before you hand it over:**
- **A/B testing:** this is an offline tournament (automated checks, AI judges, then your vote at 60% weight), not live buyer testing. AI judges can't watch motion, only sampled frames and metrics. The plan includes an optional post-launch phase for real performance data.
- **AI video licensing:** all three video models start with `commercial_rights_verified: false` until you check their licences. I didn't want to assume this.
- **Your Etsy reference videos:** neither I nor Claude Code could analyse them. The plan has Claude Code download them, or you drop them in `animation-lab/references/`. It then extracts timing and pacing for ideas only, not content.
- **Nothing publishes automatically:** the pipeline creates files and never uploads them.

**Questions for you:**
- Is a square 1080×1080 canvas the right default for Etsy? I chose it because the sources I found said it performs well on mobile and desktop. 16:9 and 4:5 are the alternatives.
- Should the pipeline automatically make a second Etsy "what's inside" video alongside the main one? The plan currently offers it rather than doing it automatically.