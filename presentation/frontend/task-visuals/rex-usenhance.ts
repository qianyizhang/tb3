import sourceRaw from '../../task-explorer/rexmle-usenhance/source.json?raw';
import helperRaw from '../../task-explorer/rexmle-usenhance/helper.json?raw';
import operationRaw from '../../task-explorer/rexmle-usenhance/operation.json?raw';
import outputRaw from '../../task-explorer/rexmle-usenhance/output.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export type RexUsenhanceState = Extract<StoryState, { recipe: 'rex-usenhance-v1' }>;
export const rexUsenhancePack = {
  source: JSON.parse(sourceRaw) as {
    notice: { label: string; text: string; url: string; link_label: string };
    input: string;
    pairing: string;
    partition: string;
    units: string;
  },
  helper: JSON.parse(helperRaw) as {
    public_train: string;
    public_test: string;
    private_test: string;
    rule: string;
    model: string;
  },
  operation: JSON.parse(operationRaw) as { steps: string[]; limitations: string },
  output: JSON.parse(outputRaw) as {
    path: string;
    columns: string[];
    format: string;
    geometry: string;
    coverage: string;
    rules: Record<'lncc' | 'ssim_psnr' | 'rank' | 'fallback', string>;
    boundary: string;
  },
};
export function operationIndex(progress: number): number {
  return Math.min(3, Math.max(0, Math.round(progress * 3)));
}
export function operationFrame(plan: StoryPlan, index: number): number {
  if (plan.recipe !== 'rex-usenhance-v1') throw new Error('Recipe mismatch');
  if (!Number.isInteger(index) || index < 0 || index > 3) throw new Error('Invalid step');
  const b = plan.beats.find((b) => b.scene === 'operation');
  if (!b) throw new Error('Operation absent');
  const target = index / 3;
  let best = 0;
  let distance = Infinity;
  for (let k = 0; k < b.frames; k++) {
    const u = k / Math.max(1, b.frames - 1);
    const progress = u * u * (3 - 2 * u);
    const d = Math.abs(progress - target);
    if (d < distance - 1e-12) {
      distance = d;
      best = k;
    }
  }
  return b.startFrame + best;
}
export function canonicalRule(s: string): 'lncc' | 'ssim_psnr' | 'rank' | 'fallback' | null {
  return s === 'lncc' || s === 'ssim_psnr' || s === 'rank' || s === 'fallback' ? s : null;
}
export function resetOnBackward(prev: number, next: number): boolean {
  return next < prev;
}
