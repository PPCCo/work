/**
 * @generated-by figma-to-react-lumen
 * @figma-file {{FILE_KEY}}
 * @figma-node {{NODE_ID}}
 */
import type { Meta, StoryObj } from '{{STORYBOOK_FRAMEWORK_PACKAGE}}';
import { {{NAME}} } from './{{NAME}}';

const meta = {
  title: '{{STORY_TITLE}}', // components: Lumen/Components/<Name>, layouts: Layouts/<Name>
  component: {{NAME}},
  tags: ['autodocs'],
  args: {
    {{DEFAULT_ARGS}}
  },
  argTypes: {
    {{ARG_TYPES_FOR_DYNAMIC_PROPS}}
  },
} satisfies Meta<typeof {{NAME}}>;

export default meta;
type Story = StoryObj<typeof meta>;

// One named story per Figma variant/state. Keep the Figma variant name in the description.
{{NAMED_STORIES}}
<!--
  Template notes (delete from generated output):
  - Example named story:
      export const Disabled: Story = {
        args: { disabled: true },
        parameters: { docs: { description: { story: 'Figma variant: State=Disabled' } } },
      };
  - Story count must be >= number of variants recorded in manifest.json.
-->
