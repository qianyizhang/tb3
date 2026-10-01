import sourceRaw from '../../task-explorer/imaging101-mri-noncartesian-cs/source.json?raw';
import referenceRaw from '../../task-explorer/imaging101-mri-noncartesian-cs/reference.json?raw';
import fixtureRaw from '../../task-explorer/imaging101-mri-noncartesian-cs/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
import trajectoryImage from '../../task-explorer/imaging101-mri-noncartesian-cs/trajectory.png?inline';
export { trajectoryImage };
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  notice: { label: string; text: string; url: string; link_label: string };
  trajectory: { points: number[][]; stride: number };
};
export const reference = JSON.parse(referenceRaw) as {
  role: string;
  clean_image: null;
  criteria: string[];
};
export const fixture = JSON.parse(fixtureRaw) as {
  branches: number[];
  toy_complex: number[];
  toy_threshold: number;
  toy_shrunk: number[];
  actual_output: null;
  clean_reference: null;
};
export const imagingNoncartesianPack = { source };
export type ImagingNoncartesianState = Extract<
  StoryState,
  { recipe: 'imaging101-noncartesian-v1' }
>;
export const steps = ['Trajectory + coils', 'NUFFT + density', 'Complex wavelet prior'] as const;
export const branches = ['Show 1 spoke', 'Show 16 spokes', 'Show 64 spokes'] as const;
export function operationIndex(s: ImagingNoncartesianState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function branchIndex(s: ImagingNoncartesianState) {
  return Math.min(2, Math.max(0, Math.round(s.detail * 2)));
}
export function operationFrame(p: StoryPlan, i: number, o = 0) {
  if (p.recipe !== 'imaging101-noncartesian-v1')
    throw new Error('Non-Cartesian MRI recipe mismatch');
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
    if (v < d - 1e-12) {
      d = v;
      best = k;
    }
  }
  return b.startFrame + best;
}
export function referenceVisible(s: ImagingNoncartesianState, requested = false) {
  return requested && s.scene === 'reference' && s.reference > 0.5;
}
