import sourceRaw from '../../task-explorer/imaging101-mri-varnet/source.json?raw';
import referenceRaw from '../../task-explorer/imaging101-mri-varnet/reference.json?raw';
import fixtureRaw from '../../task-explorer/imaging101-mri-varnet/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
import coil0 from '../../task-explorer/imaging101-mri-varnet/kspace-0.png?inline';
import coil7 from '../../task-explorer/imaging101-mri-varnet/kspace-7.png?inline';
import coil14 from '../../task-explorer/imaging101-mri-varnet/kspace-14.png?inline';
export const coilImages = [coil0, coil7, coil14];
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  notice: { label: string; text: string; url: string; link_label: string };
  native_mask: number[];
};
export const reference = JSON.parse(referenceRaw) as {
  role: string;
  clean_image: null;
  criteria: string[];
};
export const fixture = JSON.parse(fixtureRaw) as {
  branches: number[];
  toy_consistent: number[];
  actual_output: null;
  clean_reference: null;
};
export const imagingVarNetPack = { source };
export type ImagingVarNetState = Extract<StoryState, { recipe: 'imaging101-varnet-v1' }>;
export const steps = ['Complex encoding', 'Native samples + mask', 'Model boundary'] as const;
export const branches = ['Coil 0', 'Coil 7', 'Coil 14'] as const;
export function operationIndex(s: ImagingVarNetState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function branchIndex(s: ImagingVarNetState) {
  return Math.min(2, Math.max(0, Math.round(s.detail * 2)));
}
export function operationFrame(p: StoryPlan, i: number, o = 0) {
  if (p.recipe !== 'imaging101-varnet-v1') throw new Error('VarNet recipe mismatch');
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
export function referenceVisible(s: ImagingVarNetState, requested = false) {
  return requested && s.scene === 'reference' && s.reference > 0.5;
}
