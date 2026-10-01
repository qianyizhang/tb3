import sourceRaw from '../../task-explorer/bcer-short-superres/source.json?raw';
import referenceRaw from '../../task-explorer/bcer-short-superres/reference.json?raw';
import fixtureRaw from '../../task-explorer/bcer-short-superres/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  preview_data_uri: string;
  representative_input: { shape_xyz: number[]; spacing_xyz_mm: number[] };
  notice: { label: string; text: string; url: string; link_label: string };
};
export const reference = JSON.parse(referenceRaw) as {
  role: string;
  criteria: string[];
  clean_image: null;
};
export const fixture = JSON.parse(fixtureRaw) as {
  input_size: number[];
  input_spacing: number[];
  target_spacing: number[][];
  derived_size: number[][];
  rounded_spacing_example: { target: number[]; derived_size: number[] };
  actual_output: null;
  clean_reference: null;
};
export const bcerSuperresPack = { source };
export type BcerSuperresState = Extract<StoryState, { recipe: 'bcer-superres-v1' }>;
export const steps = ['Read source grid', 'Choose target', 'Interpolate'] as const;
export const branches = ['Same spacing', 'Half z-spacing', 'Half all spacing'] as const;
export function operationIndex(s: BcerSuperresState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function branchIndex(s: BcerSuperresState) {
  return Math.min(2, Math.max(0, Math.round(s.detail * 2)));
}
export function operationFrame(p: StoryPlan, i: number, o = 0) {
  if (p.recipe !== 'bcer-superres-v1') throw new Error('BCER superres recipe mismatch');
  if (!Number.isInteger(i) || i < 0 || i >= steps.length) throw new Error('Invalid operation step');
  if (!Number.isInteger(o) || o < 0 || o >= branches.length) throw new Error('Invalid grid branch');
  const b = p.beats.find(
    (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - Math.round(i) / 2) < 1e-6,
  );
  if (!b) throw new Error('Missing operation beat');
  if (i !== 1) return b.startFrame;
  const t = Math.min(2, Math.max(0, Math.round(o))) / 2;
  let best = 0,
    d = Infinity;
  for (let k = 0; k < b.frames; k++) {
    const u = k / Math.max(1, b.frames - 1),
      z = u * u * (3 - 2 * u),
      v = Math.abs(z - t);
    // Symmetric midpoint distances differ only by floating-point roundoff.
    if (v < d - 1e-12) {
      d = v;
      best = k;
    }
  }
  return b.startFrame + best;
}
export function referenceVisible(s: BcerSuperresState, requested = false) {
  return requested && s.scene === 'reference' && s.reference > 0.5;
}

export function resetOnBackward(previous: number, current: number) {
  return current < previous;
}
export const interpolationModes = ['linear', 'nearest', 'bspline'] as const;
export function gridCount(size: number[]) {
  return size.reduce((n, x) => n * x, 1);
}
