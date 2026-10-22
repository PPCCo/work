# STD-ETSY-003 — Etsy Bundle Release Gate

## Purpose

An Etsy-targeted digital product is releasable only when all promised components are present, independently checked, accessible to the buyer, appropriately licensed, and packaged to current platform constraints. This extends rather than replaces the existing six human approval gates.

## Gate evidence required

- Approved niche evidence and product brief.
- Component matrix with counts and acceptance criteria.
- Content and instruction verification report.
- Independent safety review for children/crafts or other risk-bearing uses.
- Independent answer-key/rules check for objective games or educational content.
- Visual proof and print preflight for every promised page-size/color variant.
- Accessibility/legibility review appropriate to each audience.
- Rights ledger and current AI-disclosure decision.
- Listing package, title/tag validation report, gallery plan, and claim-to-artifact traceability matrix.
- Delivery manifest listing all files, hashes, sizes, purposes, and included tier.
- Final assembled package report: file count, individual file byte sizes, ZIP integrity if present, required-file presence, and checksum verification.
- Release-time snapshots/links for the Etsy constraints used by the adapter, with checked date.

## Severity

- **BLOCKER:** missing/incorrect promised file; broken editable-template access; unlicensed content; unsupported/misleading listing claim; safety hazard presented as safe; invalid or unverified objective answer key; violated platform hard limit; corrupted/missing package; unresolved disclosure obligation.
- **MAJOR:** confusing instructions; illegible text; inconsistent variants; misleading gallery image; weak printability; missing important access/software prerequisite; significant mismatch between audience and complexity.
- **MINOR:** cosmetic inconsistency with no material usability or claim impact.

A BLOCKER must be corrected and rechecked before release. MAJOR findings require correction or documented human disposition under existing policy. An agent or workflow may not grant a human approval, freeze artifacts, authorize release, or submit the listing.

## Release is not automation permission

The packager produces a local upload-ready package only. Live Etsy listing creation, upload, edits, or credential use remain disabled unless a separate reviewed connector extension is authorized under the repository's security/release rules.
