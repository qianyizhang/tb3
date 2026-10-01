import sourceRaw from '../../task-explorer/imaging101-plane-wave-ultrasound/source.json?raw';
import referenceRaw from '../../task-explorer/imaging101-plane-wave-ultrasound/reference.json?raw';
import fixtureRaw from '../../task-explorer/imaging101-plane-wave-ultrasound/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
import fibersImage from '../../task-explorer/imaging101-plane-wave-ultrasound/rf-fibers.png?inline';
import cystsImage from '../../task-explorer/imaging101-plane-wave-ultrasound/rf-cysts.png?inline';
export { fibersImage, cystsImage };
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  notice: { label: string; text: string; url: string; link_label: string };
  native_profiles: {
    profiles: {
      phantom: string;
      element: number;
      angle_deg: number;
      t0_seconds: number;
      values: number[];
      global_mean: number;
    }[];
    dt_seconds: number;
  };
};
export const reference = JSON.parse(referenceRaw) as {
  role: string;
  clean_image: null;
  criteria: string[];
};
export const fixture = JSON.parse(fixtureRaw) as {
  branches: number[];
  toy_mean_envelopes: number;
  actual_output: null;
  clean_reference: null;
};
export const imagingPlaneWavePack = { source };
export type ImagingPlaneWaveState = Extract<
  StoryState,
  { recipe: 'imaging101-plane-wave-ultrasound-v1' }
>;
export const steps = ['RF + steering', 'Native traces', 'Compound + envelope'] as const;
export const branches = ['Fibers −1.5°', 'Fibers 0°', 'Cysts 0°'] as const;
export function operationIndex(s: ImagingPlaneWaveState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function branchIndex(s: ImagingPlaneWaveState) {
  return Math.min(2, Math.max(0, Math.round(s.detail * 2)));
}
export function operationFrame(p: StoryPlan, i: number, o = 0) {
  if (p.recipe !== 'imaging101-plane-wave-ultrasound-v1')
    throw new Error('Plane-wave recipe mismatch');
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
export function referenceVisible(s: ImagingPlaneWaveState, requested = false) {
  return requested && s.scene === 'reference' && s.reference > 0.5;
}
