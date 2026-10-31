# Figma → Lumen report: {{FILE_NAME}} ({{FILE_KEY}})

Run: {{TIMESTAMP}} · Scope: {{SCOPE}} · Figma URL: {{URL}}

## Verdict
{{PASS | PARTIAL | BLOCKED}}: {{one-sentence reason}}

## Generated
| Kind | Count | Notes |
|---|---|---|
| Components | {{N}} | |
| Layouts | {{N}} | |
| Screens | {{N}} | |
| Reused from repo | {{N}} | {{list}} |
| Gaps | {{N}} | see below |

File list: {{paths}}

## Gaps (need a human)
| Figma item | Reason | Suggested follow-up (designer / Lumen team / dev) |
|---|---|---|

## Waivers
{{none | list with rule, file, line, reason}}

## Checks
| Check | Result | Evidence |
|---|---|---|
| Lumen compliance validator | {{pass/fail/not-run}} | {{command + exit code}} |
| Manifest coverage | {{...}} | |
| Typecheck | {{...}} | |
| Lint | {{...}} | |
| Storybook build | {{...}} | |
| Visual diff | {{...}} | {{or "not run: no browser test tool; manual checklist below"}} |
| Independent review | {{pass / pass with notes / fail}} | `review.md` |

## Assumptions made
{{list}}

## Run it
```
{{package manager}} run storybook
```
