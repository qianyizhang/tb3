import sourceRaw from '../../task-explorer/imaging101-xray-tooth-gridrec/source.json?raw';
import referenceRaw from '../../task-explorer/imaging101-xray-tooth-gridrec/reference.json?raw';
import fixtureRaw from '../../task-explorer/imaging101-xray-tooth-gridrec/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
import row0 from '../../task-explorer/imaging101-xray-tooth-gridrec/counts-row0.png?inline';
import row1 from '../../task-explorer/imaging101-xray-tooth-gridrec/counts-row1.png?inline';
export const images = [row0, row1];
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  notice: { label: string; text: string; url: string; link_label: string };
  native_display: {
    raw_min: number;
    raw_max: number;
    calibration_profiles: { key: string; frame: number; row: number; values: number[] }[];
    no_native_log_filter_inverse_or_reconstruction: boolean;
  };
};
export const reference = JSON.parse(referenceRaw) as {
  role: string;
  clean_image: null;
  criteria: string[];
};
export const fixture = JSON.parse(fixtureRaw) as {
  branches: number[];
  toy_transmission: number;
  actual_output: null;
  clean_reference: null;
};
export const imagingToothGridrecPack = { source };
export type ImagingToothGridrecState = Extract<
  StoryState,
  { recipe: 'imaging101-xray-tooth-gridrec-v1' }
>;
export const steps = ['Counts → transmission', 'Native inputs', 'Centre + FBP rules'] as const;
export const branches = ['Detector row 0', 'Detector row 1', 'Flat / dark frames'] as const;
export function operationIndex(s: ImagingToothGridrecState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function branchIndex(s: ImagingToothGridrecState) {
  return Math.min(2, Math.max(0, Math.round(s.detail * 2)));
}
export function operationFrame(p: StoryPlan, i: number, o = 0) {
  if (p.recipe !== 'imaging101-xray-tooth-gridrec-v1') throw new Error('Tooth recipe mismatch');
  if (!Number.isInteger(i) || i < 0 || i > 2 || !Number.isInteger(o) || o < 0 || o > 2)
    throw new Error('Invalid operation or branch');
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
export function referenceVisible(s: ImagingToothGridrecState, requested = false) {
  return requested && s.scene === 'reference' && s.reference > 0.5;
}
