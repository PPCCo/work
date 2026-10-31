# Pattern: Figma → Lumen mapping heuristics

Heuristics only. **Lumen facts always come from MCP**; this file never names real Lumen components, props or tokens.

## 1. Classifying Figma items

| Figma signal | Classification |
|---|---|
| Top-level frame sized like a device/page (mobile, tablet, desktop widths) or named like a page/screen/flow step | `screen` |
| Repeated page scaffold (header + content region + footer/nav) appearing across several screens | `layout` |
| Component, component set (variants) or reusable instance group | `component` |
| Cover pages, notes, redlines, archive/"old"/"WIP" pages, annotation frames, sticker sheets | `ignored` (always give a reason) |
| Instances of Lumen library components | Not new components: they map to Lumen directly; wrap them only when the designer composed them into a reusable pattern |
| Variant properties on a component set | `variants` → stories and props |

When unsure, classify as `component` if it appears in two or more places, otherwise as part of the enclosing screen. Record the reason.

## 2. Resolution order for a Figma element

1. Existing repo component or Code Connect mapping → **reuse**.
2. Lumen component found via MCP (search by Figma component name, then by role) → use it with MCP-verified props.
3. Composition of Lumen primitives (layout primitives, text, icon) that MCP shows as the recommended way → compose.
4. None of the above → **gap** (never invent).

## 3. Layout mapping

| Figma auto-layout concept | Mapping approach |
|---|---|
| Direction (horizontal / vertical) | Lumen layout primitive and prop from MCP |
| Gap, padding | Lumen spacing tokens/props from MCP; never convert pixel values by arithmetic guess |
| Alignment, distribution | The corresponding Lumen layout props from MCP |
| Hug / fill / fixed sizing | Lumen sizing props from MCP; fixed sizes only if the designer's frame requires and Lumen exposes a token |
| Wrap | Lumen's wrap/grid support from MCP |
| Absolute positioning | Flag for review; prefer a gap over fragile positioning |
| Constraints / responsive resizing | Use Lumen breakpoints/responsive props from MCP; record assumptions |

## 4. Variables and styles → tokens

1. Use the variable **name and collection** to query MCP for the Lumen token.
2. Variable modes (light/dark, brand) are preserved by using semantic tokens; never bake one mode's value in.
3. A Figma style or variable with no verified Lumen token → gap with the raw value recorded in the report (not in code).

## 5. Text

- Text content that is clearly data (names, amounts, dates, lists) → props, with realistic fixtures in stories.
- Static labels (button captions, headings) → props with defaults, so copy changes do not require code changes.
- Typography: Lumen text component/variant resolved via MCP; never size/weight by hand.

## 6. Interaction states

Figma prototypes and variants (hover, pressed, focus, disabled, error, loading, empty, selected) become: Lumen props where Lumen supports the state, otherwise component props plus a story. If the design shows a state that Lumen does not support → gap.

## 7. Naming

PascalCase from the Figma name; strip emojis/punctuation; resolve collisions by appending the numeric part of the node id; record the mapping `figmaName → componentName` in the manifest. Keep names stable across runs so re-runs make minimal diffs.
