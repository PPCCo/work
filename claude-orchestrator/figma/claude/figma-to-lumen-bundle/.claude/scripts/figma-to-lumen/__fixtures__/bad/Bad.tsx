import { Button, Fancy } from '@fixture/lumen';
import * as L from '@fixture/lumen';
import styled from 'styled-components';

export function Bad({ data }: { data: any }) {
  return (
    <div style={{ color: '#ff0000', padding: '16px' }}>
      <Button variant="primary" glow>Go</Button>
      <button>raw</button>
    </div>
  );
}
