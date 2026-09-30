import sourceRaw from '../../task-explorer/abra-vision-probe/source.json?raw';
import previewsRaw from '../../task-explorer/abra-vision-probe/previews.json?raw';
import fixtureRaw from '../../task-explorer/abra-vision-probe/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  notice: { label: string; text: string; url: string; link_label: string };
};
export const fixture = JSON.parse(fixtureRaw) as {
  input_ramp_HU: number[][];
  lung_window: {
    center_HU: number;
    width_HU: number;
    low_HU: number;
    high_HU: number;
    cells: number[][];
  };
  soft_tissue_window: {
    center_HU: number;
    width_HU: number;
    low_HU: number;
    high_HU: number;
    cells: number[][];
  };
  replacement_noise: { cells: number[][] };
};
export const previews = JSON.parse(previewsRaw) as {
  instances: {
    index: number;
    member: string;
    instance_number: number;
    lung: { data_uri: string; center_HU: number; width_HU: number };
    soft: { data_uri: string; center_HU: number; width_HU: number };
  }[];
};
export const abraVisionProbePack = { source, fixture, previews };
export type AbraVisionProbeState = Extract<StoryState, { recipe: 'abra-vision-probe-v1' }>;
export const conditions = [
  'Modality · normal',
  'Modality · replacement noise',
  'Display · lung window',
  'Display · soft tissue',
  'Display · breast MRI',
  'Display · replacement noise',
] as const;
export const modalityOptions = ['CT', 'MRI', 'DX', 'N/A'];
export const displayOptions = ['Lung window', 'Soft tissue window', 'Breast MRI', 'N/A'];
export function conditionIndex(state: AbraVisionProbeState) {
  return Math.min(5, Math.max(0, Math.round(state.progress * 5)));
}
export function selectedIndexSlot(state: AbraVisionProbeState) {
  return Math.min(4, Math.max(0, Math.round(state.detail * 4)));
}
export function probeReferenceVisible(state: AbraVisionProbeState) {
  return state.scene === 'reference' && state.reference > 0.5;
}
export function probeOperationFrame(plan: StoryPlan, condition: number, indexSlot: number) {
  if (plan.recipe !== 'abra-vision-probe-v1') throw new Error('Probe recipe mismatch');
  const c = Math.min(5, Math.max(0, Math.round(condition)));
  const slot = Math.min(4, Math.max(0, Math.round(indexSlot)));
  const beat = plan.beats.find(
    (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - c / 5) < 1e-6,
  );
  if (!beat) throw new Error('Missing canonical probe condition');
  return beat.startFrame + Math.round((slot / 4) * (beat.frames - 1));
}
