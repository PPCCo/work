/**
 * @generated-by figma-to-react-lumen
 * @figma-file abc123
 * @figma-node 1:2
 */
import type { Meta, StoryObj } from '@storybook/react';
import { Demo } from './Demo';

const meta = {
  title: 'Lumen/Components/Demo',
  component: Demo,
  tags: ['autodocs'],
  args: { title: 'Welcome', ctaLabel: 'Continue' },
} satisfies Meta<typeof Demo>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Loading: Story = { args: { loading: true } };
