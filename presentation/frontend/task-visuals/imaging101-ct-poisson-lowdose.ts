import sourceRaw from '../../task-explorer/imaging101-ct-poisson-lowdose/source.json?raw';
import referenceRaw from '../../task-explorer/imaging101-ct-poisson-lowdose/reference.json?raw';
import fixtureRaw from '../../task-explorer/imaging101-ct-poisson-lowdose/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  notice: { label: string; text: string; url: string; link_label: string };
};
export const reference = JSON.parse(referenceRaw) as {
  role: string;
  clean_image: null;
  expected_count_subset: { values: number[][]; units: string; I0: number };
};
export const fixture = JSON.parse(fixtureRaw) as {
  I0: number;
  line_integrals: number[];
  expected_counts: number[];
  illustrative_counts: number[];
  floored_counts: number[];
  postlog: number[];
  dose_shift: number;
  actual_output: null;
  clean_reference: null;
};
export const imagingPoissonPack = { source };
export type ImagingPoissonState = Extract<StoryState, { recipe: 'imaging101-poisson-v1' }>;
export const steps = ['Expected counts', 'Floor + log', 'Weighted TV'] as const;
export const branches = ['300 counts', '100 counts', 'Zero count'] as const;
export function operationIndex(s: ImagingPoissonState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function branchIndex(s: ImagingPoissonState) {
  return Math.min(2, Math.max(0, Math.round(s.detail * 2)));
}
export function operationFrame(p: StoryPlan, i: number, o = 0) {
  if (p.recipe !== 'imaging101-poisson-v1') throw new Error('Poisson recipe mismatch');
  if (!Number.isInteger(i) || i < 0 || i >= steps.length) throw new Error('Invalid operation step');
  if (!Number.isInteger(o) || o < 0 || o >= branches.length)
    throw new Error('Invalid count branch');
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
    // Prefer the earliest symmetric nearest frame across roundoff ties.
    if (v < d - 1e-12) {
      d = v;
      best = k;
    }
  }
  return b.startFrame + best;
}
export function referenceVisible(s: ImagingPoissonState, requested = false) {
  return requested && s.scene === 'reference' && s.reference > 0.5;
}

export function resetOnBackward(previous: number, current: number) {
  return current < previous;
}
export function illustrativePostlog(count: number, incident: number) {
  if (!Number.isFinite(count) || count < 0 || !Number.isFinite(incident) || incident <= 0)
    throw new Error('Invalid toy counts');
  return -Math.log(Math.max(count, 1) / incident);
}
export function illustrativeWeights(counts: number[], mode: 'counts' | 'uniform') {
  if (counts.some((x) => !Number.isFinite(x) || x < 1))
    throw new Error('Floored toy counts required');
  if (mode !== 'counts' && mode !== 'uniform') throw new Error('Invalid weight mode');
  const max = Math.max(...counts);
  return counts.map((x) => (mode === 'uniform' ? 1 : x / max));
}
export const metricRoutes = [
  'Filesystem full',
  'Task-aware crop',
  'No-filesystem fallback',
] as const;
