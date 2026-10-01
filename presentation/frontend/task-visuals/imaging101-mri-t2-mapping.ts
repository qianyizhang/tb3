import sourceRaw from '../../task-explorer/imaging101-mri-t2-mapping/source.json?raw';
import referenceRaw from '../../task-explorer/imaging101-mri-t2-mapping/reference.json?raw';
import fixtureRaw from '../../task-explorer/imaging101-mri-t2-mapping/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
import echo10 from '../../task-explorer/imaging101-mri-t2-mapping/echo-10.png?inline';
import echo50 from '../../task-explorer/imaging101-mri-t2-mapping/echo-50.png?inline';
import echo100 from '../../task-explorer/imaging101-mri-t2-mapping/echo-100.png?inline';
export const echoImages = [echo10, echo50, echo100];
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  notice: { label: string; text: string; url: string; link_label: string };
};
export const reference = JSON.parse(referenceRaw) as {
  role: string;
  clean_image: null;
  criteria: string[];
};
export const fixture = JSON.parse(fixtureRaw) as {
  branches: number[];
  toy_signal: number[];
  actual_output: null;
  clean_reference: null;
};
export const imagingT2MappingPack = { source };
export type ImagingT2MappingState = Extract<StoryState, { recipe: 'imaging101-t2-mapping-v1' }>;
export const steps = ['Signal + noise', 'Native echoes', 'Log + nonlinear fit'] as const;
export const branches = ['TE 10 ms', 'TE 50 ms', 'TE 100 ms'] as const;
export function operationIndex(s: ImagingT2MappingState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function branchIndex(s: ImagingT2MappingState) {
  return Math.min(2, Math.max(0, Math.round(s.detail * 2)));
}
export function operationFrame(p: StoryPlan, i: number, o = 0) {
  if (p.recipe !== 'imaging101-t2-mapping-v1') throw new Error('T2 mapping recipe mismatch');
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
export function referenceVisible(s: ImagingT2MappingState, requested = false) {
  return requested && s.scene === 'reference' && s.reference > 0.5;
}
