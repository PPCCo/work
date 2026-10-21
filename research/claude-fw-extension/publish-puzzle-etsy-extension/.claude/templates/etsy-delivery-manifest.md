# Etsy Delivery Manifest Template

> Field-definition template for one manifest per listing/tier. The implementation should serialize a machine-readable `delivery-manifest.yaml` or JSON from these fields; do not point the validator at this Markdown template. Replace all placeholders in project copies. Do not mark files `verified` until the referenced artifact exists and its hash/size has been checked.

## Listing package identity

- Project ID:
- Listing/tier ID:
- Product archetype:
- Fulfillment mode:
- Manifest version:
- Generated at (UTC):
- Current Etsy policy snapshot date:
- Package status: `DRAFT`

## Uploaded top-level files

| File ID | Buyer-visible filename | Relative path | Format | Bytes | SHA-256 | Purpose | Included component IDs | Required? | Validation status |
|---|---|---|---|---:|---|---|---|---|---|
| FILE-001 |  |  |  |  |  |  |  | yes | pending |

Check current Etsy file count, size, and supported file type limits before marking the package ready. Nested archive members should be inventoried separately below.

## Archive members (if any)

| Parent file ID | Member path/name | Bytes | Format | SHA-256 | Component ID | Opens/extracts? |
|---|---|---:|---|---|---|---|
| FILE-001 |  |  |  |  |  | pending |

## Component-to-file reconciliation

| Component ID | Expected count | Actual count | Required variant(s) | Files covering component | Pass? | Evidence |
|---|---:|---:|---|---|---|---|
| COMP-001 |  |  |  |  | pending |  |

## Buyer instructions and prerequisites

- START-HERE file included:
- Download/access instructions:
- Printing instructions:
- Editable template instructions:
- Software/account/printer prerequisites:
- File extraction instructions (if ZIP):
- Usage licence text included:
- AI disclosure required and accounted for:
- Personalization/made-to-order steps (if relevant):
- Fallback when links/files fail:
- Physical item shipped? (must be `no` for digital-only listings):

## Listing consistency

- Listing title:
- Title character count:
- Number of tags:
- Per-tag character counts checked:
- Description version/hash:
- Gallery asset IDs/hashes:
- Price/tier scope matches this manifest:
- Every advertised count maps to a verified component:

## Technical validation

- Manifest/file reconciliation:
- Hash verification:
- ZIP integrity:
- PDF page-size and page-count check:
- PDF fonts/text/render preflight:
- PNG/SVG/DPI/dimension check where relevant:
- Editable link/permission check:
- Current platform hard-limit check:
- Validator name/version/exit code/report hash:

## Sign-off record

- Independent auditor:
- Audit result:
- Open blockers/majors:
- Human gate decision and approver:
- Release authorization artifact/hash:
