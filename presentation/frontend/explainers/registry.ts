import type { ComponentType } from 'react';
import type { ExplainerView } from '../contracts.generated';
import type { ReaderProps } from '../explainer';
import { RestorationReader } from './shell/RestorationReader';
import { NativeTraceReader } from './shell/NativeTraceReader';

/** Closed composition root. Views receive selected content; this map imports no asset packs. */
export const views = {
  'restoration-protocol': RestorationReader,
  'native-trace': NativeTraceReader,
} satisfies Record<ExplainerView['family'], ComponentType<ReaderProps>>;
