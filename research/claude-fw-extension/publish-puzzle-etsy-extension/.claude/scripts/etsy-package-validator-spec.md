# Proposed Script Spec — Etsy Package Validator

**Status: specification only. This is not an executable validator.** Implement under the repository's existing script architecture, add tests, and expose it through `ph_cli.py` only after code review. Do not treat the workflow as validated until the implementation exists and runs.

## Recommended location and invocation

- Implementation: `.claude/scripts/publishing_house/etsy_package_validator.py` (or the matching package location discovered in the checked-out repository).
- Proposed CLI: `python3 .claude/scripts/ph_cli.py etsy validate <project-id> --manifest <path>`.
- The CLI verb and flags above are proposals and must not be used until wired into `ph_cli.py` and documented there.
- Inputs: project directory, approved delivery manifest, component matrix, current platform snapshot, listing draft, and actual package directory.
- Outputs: machine-readable JSON report plus a human-readable Markdown summary; deterministic exit codes: `0` PASS, `1` validation/gate failure, `2` execution/configuration error, following repository conventions where compatible.

## Required checks

1. **Manifest schema:** required fields, unique file IDs, stable component IDs, legal relative paths, no path traversal, non-empty delivery mode, timestamp, and policy snapshot date.
2. **File presence and integrity:** every declared file exists; no undeclared top-level upload files; byte sizes and SHA-256 hashes match; paths remain inside the project/package root.
3. **Etsy upload constraints:** compare number of top-level uploaded files, each file's bytes, and file extensions against a dated configuration snapshot. Do not hardcode rules as permanent; fail with `STALE_POLICY_SNAPSHOT` when older than the configured release freshness window.
4. **ZIP checks:** safe member paths, no absolute paths or `..` traversal, no encrypted archives unless explicitly supported, archive can be opened/tested, extracted member count/size cap configured, clear top-level structure, and files are included in the component inventory.
5. **Component reconciliation:** sum actual component files/records and verify promised counts, page counts, audience versions, US Letter/A4 variants, color/ink-friendly variants, and tier contents.
6. **PDF preflight:** pages are non-empty; page size/orientation matches manifest; fonts are embedded where applicable; text not outside page bounds; page-count and basic raster/render checks pass. Use existing repo preflight tools rather than introducing duplicate dependencies without review.
7. **Image/vector preflight:** pixel dimensions / DPI metadata or physical dimensions satisfy the approved spec; SVGs parse and do not contain unsupported external dependencies; transparent/black-and-white assets match their stated purpose.
8. **Listing constraints:** current title hard limit; current maximum number of tags; every tag character count; mandatory fields; no claims whose component IDs are missing; digital-only reminder and AI disclosure when required by the compliance record.
9. **Editable-template checks:** link is present and matches the approved access record; link target cannot be reliably tested offline, so report `MANUAL_LINK_CHECK_REQUIRED` unless a separately approved safe fetch check is available. Never log private customer data or credentials.
10. **Rights and human gates:** no item with unknown rights status; required rights/safety/accessibility reports exist; release or approval authority remains external to this script. The script reports readiness but never approves, freezes, publishes, or authorizes release.
11. **Reproducibility:** output validator version, input manifest hash, package files/hashes, policy snapshot identifier, check results, and timestamp; register report as an artifact.

## Example finding structure

```json
{
  "check_id": "ETSY-TAG-CHAR-LIMIT",
  "severity": "BLOCKER",
  "status": "FAIL",
  "subject": "tag: christmas craft night",
  "expected": "at most 20 characters per tag under the current policy snapshot",
  "observed": 21,
  "evidence": ["projects/<id>/metadata/etsy-listing.json"],
  "remediation": "Rewrite the phrase naturally; do not truncate mid-word."
}
```

## Acceptance tests

- Passes a tiny complete fixture and produces stable JSON for identical inputs.
- Fails when any manifest file is missing, modified, duplicated, or outside the package root.
- Fails when file-count/byte/tag/title constraints are exceeded under the fixture policy snapshot.
- Fails on unknown rights or required missing specialist reports.
- Fails on broken ZIP integrity or unsafe archive paths.
- Flags rather than falsely passing an untestable external template link.
- Reconciles declared component counts with actual fixture files.
- Refuses stale/missing policy snapshot before release readiness.
- Does not perform network writes or change project lifecycle state.
- Is integrated into unit tests and `framework validate` where the existing architecture supports it.
