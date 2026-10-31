/**
 * @generated-by figma-to-react-lumen
 * @figma-file abc123
 * @figma-node 1:2
 */
import { Button, Stack, Text } from '@fixture/lumen';

export interface DemoProps {
  title: string;
  ctaLabel: string;
  loading?: boolean;
  onCta?: () => void;
}

export function Demo({ title, ctaLabel, loading = false, onCta }: DemoProps) {
  return (
    <Stack gap="4" direction="column">
      <Text variant="heading">{title}</Text>
      <Button variant="primary" loading={loading} onClick={onCta} data-testid="cta">
        {ctaLabel}
      </Button>
    </Stack>
  );
}
