# `.clauderc` additions (MERGE, do not replace)

Merge these keys into the existing `.claude/rules/.clauderc`. Keep every existing key.

```
[mcp]
default_servers = ["lumen-knowledgebase", "figma-dev-access"]

[generation]
framework = "React"
styling = "Lumen Design Tokens / Component Props"
storybook = "v8"
output_components = "src/components"     # adjust to ALIGNMENT-REPORT.md
output_layouts = "src/layouts"           # adjust
output_screens = "src/screens"           # adjust
artifact_dir = "design-sync"

[rules]
always_verify_lumen_props = true
prefer_atomic_lumen_imports = true
require_generated_header = true
forbid_web_search = true
max_build_verify_iterations = 3

[verification]
compliance_config = ".claude/rules/lumen-compliance.config.json"
compliance_script = ".claude/scripts/figma-to-lumen/validate-lumen-compliance.mjs"
manifest_script = ".claude/scripts/figma-to-lumen/verify-manifest.mjs"
```

## Important

- Phase 0 must find out whether the framework actually **reads** `.clauderc`. If nothing consumes it, these keys are documentation only. Enforcement then comes from `rules/figma-to-lumen.md`, the agent instructions, the validator scripts and the optional write hook. Say which case applies in `ALIGNMENT-REPORT.md`.
- `prefer_atomic_lumen_imports` is interpreted by the validator through `lumen-resolution.json`: each component must be imported from exactly the path MCP reported for it, and namespace imports of Lumen are rejected.
