# Standard: Storybook stories for Figma-derived code

Targets Storybook **v8** with CSF3 (confirm in Phase 0 that the repo's Storybook major and framework package, typically the Next.js one, match; flag if not).

## Coverage

- One story file for **every** generated component, layout and screen, colocated with the code as `<Name>.stories.tsx`.
- One named story for **every** Figma variant/state (default, hover/focus if designed, active, disabled, loading, error, empty, populated, light/dark modes where designed). `verify-manifest.mjs` fails when named stories < recorded variants.
- Every screen the designer produced has a screen story at the designer's frame size.

## Structure

```tsx
const meta = {
  title: 'Lumen/Components/<Name>',   // layouts: 'Layouts/<Name>', screens: 'Screens/<Flow or Page>/<Name>'
  component: Name,
  tags: ['autodocs'],
  args: { /* realistic defaults */ },
  argTypes: { /* controls for dynamic props; actions via `fn()` where the repo has @storybook/test */ },
} satisfies Meta<typeof Name>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {};
```

Rules:
1. Story names mirror Figma variant names, converted to PascalCase identifiers (`Disabled`, `LoadingWithError`). Keep the original Figma name in `parameters.docs.description.story` for traceability.
2. Screens: `parameters: { layout: 'fullscreen' }` and a viewport matching the frame (via the repo's configured viewports, or an explicit `viewport.defaultViewport` that the story registers). Record the frame width/height in the manifest as `viewport`.
3. Data: realistic fixtures in a colocated `<Name>.fixtures.ts`. Never real customer data, account numbers or personal information. Use clearly fake values.
4. Provider/theme: supply Lumen's provider/theme once in `.storybook/preview.tsx` as the app does. Do not wrap each story individually.
5. If designs exist for multiple Lumen themes or modes, expose them via a global toolbar toggle, and add stories per mode only where the designer drew them.
6. Link back: `parameters.design = { type: 'figma', url: '<node url>' }` only if the `@storybook/addon-designs` addon is already installed; otherwise put the Figma node URL in the docs description. Do not add the addon without reporting it.
7. Stories must pass the same compliance checks as components (no hex, no inline style, Lumen only). Story-only imports from `@storybook/*` are allowed.
8. Interaction tests (`play`) only when the repo already uses `@storybook/test`; keep them minimal.

## Build and verification

- `storybook build` (or the repo's script) must succeed. If it cannot run in the environment, report "not run" and why.
- Visual comparison with Figma screenshots runs only when a browser test tool is already present; otherwise the report lists a manual checklist.
