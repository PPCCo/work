/**
 * @generated-by figma-to-react-lumen
 * @figma-file {{FILE_KEY}}
 * @figma-node {{NODE_ID}}
 * @figma-name {{FIGMA_NAME}}
 *
 * Generated from Figma; regenerate with the figma-to-react-lumen skill.
 * Hand edits to this file may be overwritten.
 */
{{USE_CLIENT_DIRECTIVE_IF_NEEDED}}
{{LUMEN_IMPORTS}}
{{OTHER_IMPORTS}}

export interface {{NAME}}Props {
  {{PROPS_INTERFACE_MEMBERS}}
}

export function {{NAME}}({{DESTRUCTURED_PROPS}}: {{NAME}}Props) {
  return (
    {{JSX_USING_ONLY_MCP_VERIFIED_LUMEN_COMPONENTS_AND_TOKENS}}
  );
}

<!--
  Template notes (delete from generated output):
  - {{LUMEN_IMPORTS}} must use the exact import path from lumen-resolution.json (components.<Name>.import).
  - Only props listed in lumen-resolution.json may appear on Lumen components.
  - No inline style, colours, raw px, any, or raw button/input/select/textarea.
  - Put "use client" first only when hooks/handlers require it.
-->
