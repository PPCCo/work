/**
 * @generated-by figma-to-react-lumen
 * @figma-file {{FILE_KEY}}
 * @figma-node {{NODE_ID}}
 * @figma-url {{FIGMA_NODE_URL}}
 */
import type { Meta, StoryObj } from '{{STORYBOOK_FRAMEWORK_PACKAGE}}';
import { {{NAME}} } from './{{NAME}}';
import { {{FIXTURE_EXPORTS}} } from './{{NAME}}.fixtures';

const meta = {
  title: 'Screens/{{FLOW_OR_PAGE}}/{{NAME}}',
  component: {{NAME}},
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    // Designer frame size: {{VIEWPORT_W}} x {{VIEWPORT_H}}. Register/select a matching viewport per the repo's Storybook config.
  },
  args: {
    {{DEFAULT_ARGS_FROM_FIXTURES}}
  },
} satisfies Meta<typeof {{NAME}}>;

export default meta;
type Story = StoryObj<typeof meta>;

// One story per Figma frame variant of this screen (default, error, empty, loading, ...).
{{NAMED_STORIES}}
<!--
  Template notes (delete from generated output):
  - Fixtures live in {{NAME}}.fixtures.ts and use obviously fake data only.
  - Lumen provider/theme comes from .storybook/preview.tsx, not from this file.
-->
