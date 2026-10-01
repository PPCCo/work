Claude Opus-5-5 is consuming much more tokens than Opus-4-8. What's the reason and how can I optimize token-spending. Also, would it help if I stop fanning out separate agents, and do everything in one session?

---

I don't have reliable details on Opus 5.5's token behavior, so I'll check Anthropic's current documentation and your orchestrator setup.I couldn't find an official explanation for Opus 5.5 using more tokens than Opus 4.8, so the causes below are the likely candidates rather than confirmed. The sources also conflict on 5.5 pricing, so check your own usage numbers.

**Likely reasons**

- **It's probably not the tokenizer.** One third-party reference says the tokenizer changed from Opus 4.7 onward, producing roughly 30 percent more tokens for the same text. 4.8 already has that, so it shouldn't explain a 4.8 → 5.5 jump.
- **Thinking and effort.** Anthropic's Opus 5 notes say thinking is on by default, and low and medium effort deliver strong quality at a fraction of the tokens and latency of higher settings. If your effort is high or max, you're likely paying for much more reasoning output than before.
- **Hard tasks cost more.** One comparison suggests budgeting for higher output-token volume on your hardest 20% of tasks on Opus 5. That fits agentic coding work.
- **Cache misses.** When the cache expires or a configuration change invalidates it, rewriting costs 1.25 to 2 times the normal input price. Changing rules, skills or CLAUDE.md mid-session can trigger this.

**First step: find out which tokens grew.** Run `/usage` in Claude Code to see token consumption and cache share. If output or thinking tokens grew, lower the effort. If input grew, look at context size and cache misses. One third-party source reports Opus 5.5 at $4/$20 per million tokens, 20% below Opus 5, so a higher bill means a real consumption increase.

**Ways to cut spending**

- Default to low or medium effort and raise it only for hard architecture or debugging work.
- Use `/clear` between unrelated tasks and `/compact` during long ones.
- Keep CLAUDE.md and your rules files lean. Everything in them is loaded into every session and every subagent.
- Avoid editing config files mid-session, to protect the cache.

**Would one session be cheaper than fanning out?** Sometimes, but not as a rule.

- Every subagent starts with its own context, so it re-loads CLAUDE.md, rules, skills and tool definitions. Parallel agents with different prefixes also share less cache. Total tokens usually go up.
- A single long session avoids that duplication, but its context keeps growing and gets re-read every turn. Cache reads are cheap, but past a point you pay for dragging old history along.

A middle path for your orchestrator:

- Keep tightly coupled, sequential work in one session. A contract change that flows through the API, then the worker, then the frontend is a good example.
- Use subagents only for independent or read-heavy jobs such as codebase exploration, review, or work in separate repos. Have them return short summaries, not full transcripts.
- Run subagents that don't need top reasoning, like the reviewer, on a cheaper model or lower effort.
- Don't spawn three agents for something one agent can do in a few turns.

If you share a `/usage` breakdown from a typical run, I can say which of these matters most for you.

---

I have a `.claude/` full-stack software development Agentic framework in my repository at `https://github.com/qaisr/cams` with AI agents, assets, commands, hooks, patterns, scripts, standards, templates, and workflows. The purpose of the framework is to use ClaudeCode to do full stack development in an automated and autonomous fashion.

My framework's token consumption has increased a lot, specially since I moved from Claude Opus-4-8 Opus-5-5 so I want to optimize token-spending. Can you modify the relevant files, **make them lean and more optimized** (without compromising quality)

Claude suggested these Ways to cut spending:

- Default to low or medium effort and raise it only for hard architecture or debugging work.
- Use `/clear` between unrelated tasks and `/compact` during long ones.
- Keep CLAUDE.md and your rules files lean. Everything in them is loaded into every session and every subagent.
- Avoid editing config files mid-session, to protect the cache.
- Keep tightly coupled, sequential work in one session. A contract change that flows through the API, then the worker, then the frontend is a good example.
- Use subagents only for independent or read-heavy jobs such as codebase exploration, review, or work in separate repos. Have them return short summaries, not full transcripts.
- Run subagents that don't need top reasoning, like the reviewer, on a cheaper model or lower effort.
- Don't spawn three agents for something one agent can do in a few turns.

Generate a complete zip file containing all the files that I should add or replace
