import type { ComponentType } from 'react';
import type { RestorationView } from '../contracts.generated';
import type { ReaderProps } from '../explainer';
import { RestorationReader } from './shell/RestorationReader';

/** Closed composition root. Views receive selected content; this map imports no asset packs. */
export const views = {
  'restoration-protocol': RestorationReader,
} satisfies Record<RestorationView['family'], ComponentType<ReaderProps>>;
