# Workflow Catalogue Addition — Etsy Digital Product

The prose workflow lives at `.claude/skills/etsy-digital-product/workflows/etsy-launch-workflow.md` and can be followed by the `etsy-digital-product` skill.

If implementing a dynamic workflow, add a separate `.claude/workflows/etsy-digital-product-launch.js` using the runtime pattern specified in the existing `.claude/workflows/README.md` and `EXTENSION_GUIDE.md`. It should:

- delegate the product-brief/component work to `etsy-product-architect`;
- route content generation and independent verification to existing agents;
- invoke the proposed validator only after it is implemented and exposed in `ph_cli.py`;
- use an independent `etsy-bundle-auditor` pass;
- prepare evidence and stop at each human gate;
- never grant approvals, freeze artifacts, authorize release, use Etsy credentials, or perform live writes.

Do not register the `.md` runbook as a runnable dynamic workflow; the dynamic workflow runtime expects a `.js` file.
