import sourceRaw from '../../task-explorer/automedbench-full-msd-pancreas-ctsr-task/source.json?raw';
import helperRaw from '../../task-explorer/automedbench-full-msd-pancreas-ctsr-task/helper.json?raw';
import operationRaw from '../../task-explorer/automedbench-full-msd-pancreas-ctsr-task/operation.json?raw';
import outputRaw from '../../task-explorer/automedbench-full-msd-pancreas-ctsr-task/output.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export type AutomedMsdPancreasCtsrState = Extract<
  StoryState,
  { recipe: 'automed-msd-pancreas-ctsr-v1' }
>;
export const automedMsdPancreasCtsrPack = {
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
    rules: Record<'raw' | 'ssim' | 'rating' | 'completion' | 'workflow', string>;
    boundary: string;
  },
};
export function operationIndex(p: number): number {
  return Math.max(0, Math.min(3, Math.round(p * 3)));
}
export function operationFrame(plan: StoryPlan, index: number): number {
  if (
    plan.recipe !== 'automed-msd-pancreas-ctsr-v1' ||
    !Number.isInteger(index) ||
    index < 0 ||
    index > 3
  )
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
): 'raw' | 'ssim' | 'rating' | 'completion' | 'workflow' | null {
  return ['raw', 'ssim', 'rating', 'completion', 'workflow'].includes(r)
    ? (r as 'raw' | 'ssim' | 'rating' | 'completion' | 'workflow')
    : null;
}
export function formatRequirement(mode: 'declared' | 'checked'): string {
  return mode === 'declared'
    ? 'Same public/hidden HR grid; 3D NIfTI HU and affine preservation requested'
    : 'Finite 3D NIfTI; target shape if present; missing outputs do not invalidate present-format';
}
export function resetOnBackward(prev: number, next: number): boolean {
  return next < prev;
}
