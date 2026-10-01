import sourceRaw from '../../task-explorer/bcer-short-denoise/source.json?raw';
import referenceRaw from '../../task-explorer/bcer-short-denoise/reference.json?raw';
import fixtureRaw from '../../task-explorer/bcer-short-denoise/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  representative_input: { shape_xyz: number[]; spacing_xyz_mm: number[] };
  notice: { label: string; text: string; url: string; link_label: string };
};
export const reference = JSON.parse(referenceRaw) as {
  role: string;
  criteria: string[];
  clean_image: null;
};
export const fixture = JSON.parse(fixtureRaw) as {
  raw: number[];
  normalized: number[];
  sigma: number[];
  raw_sigma: number[];
  actual_output: null;
  clean_reference: null;
};
export const bcerDenoisePack = { source };
export type BcerDenoiseState = Extract<StoryState, { recipe: 'bcer-denoise-v1' }>;
export const steps = ['Normalize volume', 'Sigma estimate', 'Slices + geometry'] as const;
export const branches = ['0.03', '0.08 default', '0.15'] as const;
export function operationIndex(s: BcerDenoiseState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function branchIndex(s: BcerDenoiseState) {
  return Math.min(2, Math.max(0, Math.round(s.detail * 2)));
}
export function operationFrame(p: StoryPlan, i: number, o = 0) {
  if (p.recipe !== 'bcer-denoise-v1') throw new Error('BCER denoise recipe mismatch');
  if (!Number.isInteger(i) || i < 0 || i > 2 || !Number.isInteger(o) || o < 0 || o > 2)
    throw new Error('Invalid BCER denoise selection');
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
    if (v < d) {
      d = v;
      best = k;
    }
  }
  return b.startFrame + best;
}
export function referenceVisible(s: BcerDenoiseState, readerRequested = false) {
  return readerRequested && s.scene === 'reference' && s.reference > 0.5;
}

export function resetOnBackward(previous: number, current: number) {
  return current < previous;
}
