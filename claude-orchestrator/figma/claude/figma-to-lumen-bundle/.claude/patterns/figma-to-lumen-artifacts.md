# Pattern: pipeline artifact contracts

All artifacts live in `design-sync/<fileKey>/`. The scripts read these shapes; keep them stable. Fields marked (opt) are optional.

## `source-snapshot.json`

```json
{
  "fileKey": "AbC123",
  "fileName": "My App",
  "nodeId": null,
  "capturedAt": "ISO-8601",
  "mcp": { "server": "figma-dev-access", "tools": ["<tool names used>"] },
  "limitations": ["e.g. variables not available"],
  "inventory": [
    {
      "id": "12:34",
      "name": "Login",
      "type": "FRAME",
      "page": "Onboarding",
      "classification": "screen",
      "expected": true,
      "size": { "w": 390, "h": 844 },
      "variants": ["Default", "Error"],
      "screenshot": "path-or-ref (opt)",
      "codeConnect": "src/components/... (opt)",
      "ignoreReason": "required when classification is ignored"
    }
  ],
  "styles": {},
  "variables": {}
}
```

Rules: every item has a `classification`. `ignored` items need `ignoreReason` and `expected:false`.

## `lumen-resolution.json`

```json
{
  "fileKey": "AbC123",
  "resolvedAt": "ISO-8601",
  "components": {
    "<ExportName>": {
      "import": "<exact import path from MCP>",
      "props": ["propA", "propB"],
      "propTypes": { "propA": "'x' | 'y'" },
      "variants": ["..."],
      "mcpTool": "<tool name>",
      "query": "<what was asked>",
      "figmaPatterns": ["12:34"]
    }
  },
  "tokens": { "<figma variable>": { "lumen": "<token>", "mcpTool": "...", "query": "..." } },
  "gaps": [ { "pattern": "Legacy Banner", "figmaNodeIds": ["2:1"], "reason": "...", "suggestion": "..." } ]
}
```

The validator reads `components.*.import` and `components.*.props`.

## `manifest.json`

```json
{
  "fileKey": "AbC123",
  "generatedAt": "ISO-8601",
  "entries": [
    {
      "name": "LoginScreen",
      "kind": "screen",                 // component | layout | screen
      "status": "generated",            // generated | reused | skipped
      "figmaNodeIds": ["12:34"],
      "figmaName": "Login",
      "variants": ["Default", "Error"],
      "viewport": { "w": 390, "h": 844 },   // required for screens
      "files": { "component": "src/screens/Login/Login.tsx", "story": "src/screens/Login/Login.stories.tsx" },
      "reusedFrom": "src/components/X (required when status=reused)",
      "reason": "required when status=skipped"
    }
  ],
  "gaps": [ { "figmaNodeId": "2:1", "name": "Legacy Banner", "reason": "...", "suggestion": "..." } ],
  "waivers": [ { "file": "...", "rule": "...", "line": 12, "reason": "..." } ],
  "checks": {
    "compliance": "pass | fail | not-run",
    "manifest": "pass | fail | not-run",
    "typecheck": "pass | fail | not-run",
    "lint": "pass | fail | not-run",
    "storybookBuild": "pass | fail | not-run",
    "visualDiff": "pass | fail | not-run"
  }
}
```

`verify-manifest.mjs` fails when: an `expected` inventory item is neither in an entry nor in `gaps`; a generated file is missing; a story lacks a default export or named stories; named stories < `variants`; a screen has no `viewport` or its title does not start with `Screens/`; a layout title does not start with `Layouts/`; gaps/skips lack reasons.
