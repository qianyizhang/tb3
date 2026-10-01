import sourceRaw from '../../task-explorer/automedbench-full-mri-sr-task/source.json?raw';
import helperRaw from '../../task-explorer/automedbench-full-mri-sr-task/helper.json?raw';
import operationRaw from '../../task-explorer/automedbench-full-mri-sr-task/operation.json?raw';
import outputRaw from '../../task-explorer/automedbench-full-mri-sr-task/output.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export type AutomedMriSrState = Extract<StoryState, { recipe: 'automed-mri-sr-v1' }>;
export const automedMriSrPack = {
  source: JSON.parse(sourceRaw) as {
    notice: { label: string; text: string; url: string; link_label: string };
    input: string;
    units: string;
    simulation: string;
    excluded: string;
  },
  helper: JSON.parse(helperRaw) as {
    lite: string;
    standard: string;
    window: string;
    source_claims: string;
  },
  operation: JSON.parse(operationRaw) as { steps: string[]; limitations: string },
  output: JSON.parse(outputRaw) as {
    path: string;
    format: string;
    coverage: string;
    rules: Record<'raw' | 'lpips' | 'rating' | 'normalization' | 'pass', string>;
    boundary: string;
  },
};
export function operationIndex(p: number): number {
  return Math.max(0, Math.min(3, Math.round(p * 3)));
}
export function operationFrame(plan: StoryPlan, index: number): number {
  if (plan.recipe !== 'automed-mri-sr-v1' || !Number.isInteger(index) || index < 0 || index > 3)
    throw new Error('Invalid operation');
  const beat = plan.beats.find((b) => b.scene === 'operation');
  if (!beat) throw new Error('Operation absent');
  let best = beat.startFrame;
  let distance = Infinity;
  for (let k = 0; k < beat.frames; k++) {
    const u = beat.frames <= 1 ? 1 : k / (beat.frames - 1);
    const eased = u * u * (3 - 2 * u);
    const progress =
      beat.channels.progress[0] + (beat.channels.progress[1] - beat.channels.progress[0]) * eased;
    const candidate = Math.abs(progress - index / 3);
    if (candidate < distance - 1e-12) {
      distance = candidate;
      best = beat.startFrame + k;
    }
  }
  return best;
}
export function canonicalRule(
  r: string,
): 'raw' | 'lpips' | 'rating' | 'normalization' | 'pass' | null {
  return ['raw', 'lpips', 'rating', 'normalization', 'pass'].includes(r)
    ? (r as 'raw' | 'lpips' | 'rating' | 'normalization' | 'pass')
    : null;
}
export function formatRequirement(mode: 'declared' | 'checked'): string {
  return mode === 'declared'
    ? '720×512 float32 normalized[0,1] requested'
    : 'Finite floating 2D; reference shape; no intensity/dtype-width guard';
}
export function resetOnBackward(prev: number, next: number): boolean {
  return next < prev;
}
