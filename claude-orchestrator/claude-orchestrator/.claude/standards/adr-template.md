# ADR-NNNN: <decision title>

- **Status**: proposed | accepted | superseded by ADR-NNNN
- **Date**: YYYY-MM-DD
- **Deciders**: <names or roles>
- **Tier**: 2 | 3 (why this needs a recorded decision)

## Context
What forces are at play: requirement, constraints (regulated environment, data sensitivity, deploy independence), current architecture, what is not negotiable.

## Options considered
1. **Option A**: summary, pros, cons, cost, risk
2. **Option B**: ...
3. **Do nothing**: consequences

## Decision
What we chose and the main reason in two or three sentences.

## Consequences
Positive, negative, follow-up work, migration/rollout plan, what we will monitor, when to revisit.

## Impact checklist
- [ ] Contracts / events / topics
- [ ] PostgreSQL / S3
- [ ] Temporal workflows in flight
- [ ] Security and personal data
- [ ] CI / infra
- [ ] Runbooks and catalog updated

Save as `docs/adr/NNNN-slug.md` in the orchestrator repo. The `architect` agent writes ADRs for Tier 2+ decisions.
