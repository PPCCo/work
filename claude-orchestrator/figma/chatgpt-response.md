The most important architectural decision is to build this as a design-system-aware autonomous engineering pipeline, not simply a Figma-to-React code generator.

Your Claude Code framework should treat three sources as authoritative:

1. Figma — the source of truth for the UI designer's intended screens, layouts, visual hierarchy, component variants, assets and design properties.
2. Lumen via MCP — the source of truth for approved CommBank React components, component APIs, tokens, accessibility requirements, usage patterns and design-system conventions.
3. The existing Next.js repository — the source of truth for the application's architecture, existing components, routing, TypeScript configuration, styling conventions, dependencies and Storybook setup.

The pipeline must reconcile all three before writing code.

One particularly important distinction: Figma's MCP server supplies structured design context to an AI agent; it does not independently produce finished, production-ready React code. The agent must perform the synthesis, component selection, implementation and validation. Figma's Code Connect capability can also help connect Figma components to their actual code implementations

For your CommBank use case, I would make the workflow Lumen-first, repository-aware, screen-complete, test-driven and incrementally autonomous, with explicit human approval gates for consequential changes rather than allowing an agent to make unverified assumptions.

# Master prompt: Autonomous Figma-to-React with CommBank Lumen

The following is the prompt I recommend giving your existing Claude Code publishing/engineering framework. It covers two connected objectives:

- Framework engineering: Install a new autonomous Figma-to-Lumen skill into the existing `.claude/` framework, together with only the necessary agents, workflows, rules, scripts, configuration, templates and standards.
- First production implementation: Use that newly established workflow against the supplied Figma high-fidelity designs and existing Next.js repository, implementing the React components, layouts, screens and Storybook documentation.

It deliberately does not assume that Lumen exports a particular component library, that particular MCP tool names exist, or that Storybook v8 is installed. Those must be discovered and verified in the actual environment.

## Master prompt (Framework enhancement + execution)

- `chatgpt-mega-prompt.md`

## Important architectural decisions built into the prompt

There are five decisions I would particularly preserve.

1. Dynamic MCP discovery instead of static mapping dictionaries

Claude must discover the available Figma and Lumen tools and their actual schemas. It should resolve components on each implementation run. This is consistent with Figma's current MCP architecture, which provides design context, variables, Code Connect information and other structured design resources

2. Do not force Storybook v8

Your example specifies Storybook v8. I have deliberately changed this to version detection and compatibility. Storybook currently recommends its Next.js Vite integration for most compatible Next.js projects, but an existing application's working configuration should take precedence

3. Keep Claude Code's native architecture separate from your custom framework

The existing `.claude/` directory may contain custom workflow and configuration conventions. Claude Code also supports its own skills, agents and hooks. The new implementation needs to integrate both correctly rather than create files that look appropriate but are never loaded

4. Generate stories for screens, not just components

This is especially important. A typical component-generation workflow can create dozens of component stories while failing to represent the actual screens designed in Figma. The prompt explicitly requires screen-level coverage and a traceability manifest.

5. Verify the actual outcome

The workflow is not complete when Claude has written files. It must build the application, build Storybook, compare the rendered screens against Figma, validate accessibility, and report coverage.

## Recommended execution

Give Claude Code these three inputs:

1. The master prompt above

2. Your UI designer's Figma file URL

3. The existing Next.js application repository and `.claude/` framework

I recommend initially running the entire workflow on one real Figma feature, rather than an artificially simplified design. That gives you a meaningful end-to-end test of MCP discovery, Lumen component resolution, responsive layouts, Storybook integration and framework compatibility.

The CommBank/Figma case study you referenced describes how Dev Mode and shared design tokens improve collaboration between designers and engineers. The proposed architecture builds on that approach by adding autonomous implementation and engineering validation

My recommendation: Make this the foundation of a reusable `/figma-to-lumen` engineering skill, so future feature development becomes a repeatable Figma-to-implementation-to-Storybook pipeline rather than a one-off Claude Code exercise.