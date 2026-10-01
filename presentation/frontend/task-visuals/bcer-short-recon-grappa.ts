import sourceRaw from '../../task-explorer/bcer-short-recon-grappa/source.json?raw';
import referenceRaw from '../../task-explorer/bcer-short-recon-grappa/reference.json?raw';
import fixtureRaw from '../../task-explorer/bcer-short-recon-grappa/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  notice: { label: string; text: string; url: string; link_label: string };
};
export const reference = JSON.parse(referenceRaw) as {
  role: string;
  criteria: string[];
  clean_image: null;
};
export const fixture = JSON.parse(fixtureRaw) as {
  kx: number;
  ky: number;
  coils: number;
  ACS_bounds: number[];
  ACS_lines: number;
  masks: boolean[][];
  sampled_lines: number[];
  sampled_fraction: number[];
  actual_output: null;
  clean_reference: null;
};
export const bcerGrappaPack = { source };
export type BcerGrappaState = Extract<StoryState, { recipe: 'bcer-grappa-v1' }>;
export const steps = ['Coils + axes', 'Calibration + mask', 'IFFT + output'] as const;
export const branches = ['Undersampled', 'Full sampling', 'If GRAPPA fails'] as const;
export function operationIndex(s: BcerGrappaState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function branchIndex(s: BcerGrappaState) {
  return Math.min(2, Math.max(0, Math.round(s.detail * 2)));
}
export function operationFrame(p: StoryPlan, i: number, o = 0) {
  if (p.recipe !== 'bcer-grappa-v1') throw new Error('BCER GRAPPA recipe mismatch');
  if (!Number.isInteger(i) || i < 0 || i > 2 || !Number.isInteger(o) || o < 0 || o > 2)
    throw new Error('Invalid BCER GRAPPA selection');
  const b = p.beats.find(
    (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - i / 2) < 1e-6,
  );
  if (!b) throw new Error('Missing operation beat');
  if (i !== 1) return b.startFrame;
  const t = o / 2;
  let best = 0,
    d = Infinity;
  for (let k = 0; k < b.frames; k++) {
    const u = b.frames > 1 ? k / (b.frames - 1) : 0,
      z = u * u * (3 - 2 * u),
      v = Math.abs(z - t);
    if (v < d - 1e-12) {
      d = v;
      best = k;
    }
  }
  return b.startFrame + best;
}
export function referenceVisible(s: BcerGrappaState, readerRequested = false) {
  return readerRequested && s.scene === 'reference' && s.reference > 0.5;
}

export function resetOnBackward(previous: number, current: number) {
  return current < previous;
}
