import sourceRaw from '../../task-explorer/imaging101-mri-pnp-admm/source.json?raw';
import referenceRaw from '../../task-explorer/imaging101-mri-pnp-admm/reference.json?raw';
import fixtureRaw from '../../task-explorer/imaging101-mri-pnp-admm/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
import maskRandom from '../../task-explorer/imaging101-mri-pnp-admm/mask-random.png?inline';
import maskRadial from '../../task-explorer/imaging101-mri-pnp-admm/mask-radial.png?inline';
import maskCartesian from '../../task-explorer/imaging101-mri-pnp-admm/mask-cartesian.png?inline';
export const maskImages = [maskRandom, maskRadial, maskCartesian];
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  notice: { label: string; text: string; url: string; link_label: string };
  masks: { counts: number[] };
};
export const reference = JSON.parse(referenceRaw) as {
  role: string;
  clean_image: null;
  criteria: string[];
};
export const fixture = JSON.parse(fixtureRaw) as {
  branches: number[];
  toy_sampled: number[];
  actual_output: null;
  clean_reference: null;
};
export const imagingPnpAdmmPack = { source };
export type ImagingPnpAdmmState = Extract<StoryState, { recipe: 'imaging101-pnp-admm-v1' }>;
export const steps = ['Synthesize + initialize', 'Fourier consistency', 'Denoiser + dual'] as const;
export const branches = ['Random', 'Radial grid', 'Cartesian'] as const;
export function operationIndex(s: ImagingPnpAdmmState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function branchIndex(s: ImagingPnpAdmmState) {
  return Math.min(2, Math.max(0, Math.round(s.detail * 2)));
}
export function operationFrame(p: StoryPlan, i: number, o = 0) {
  if (p.recipe !== 'imaging101-pnp-admm-v1') throw new Error('PnP-ADMM recipe mismatch');
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
export function referenceVisible(s: ImagingPnpAdmmState, requested = false) {
  return requested && s.scene === 'reference' && s.reference > 0.5;
}
