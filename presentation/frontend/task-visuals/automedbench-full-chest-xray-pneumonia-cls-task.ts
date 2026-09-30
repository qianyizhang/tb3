import sourceRaw from '../../task-explorer/automedbench-full-chest-xray-pneumonia-cls-task/source.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export const source = JSON.parse(sourceRaw) as {
  native_example: { source_folder_label: string; canonical_helper_label: string };
  actual_data_gap: string;
  prompt_conflict: string;
  preview_data_uri: string;
  notice: { label: string; text: string; url: string; link_label: string };
};
export const automedPneumoniaPack = { source };
export type AutomedPneumoniaState = Extract<StoryState, { recipe: 'automed-pneumonia-cls-v1' }>;
export const steps = [
  'Training-only preprocessing',
  'Class index mapping',
  'All-case file output',
] as const;
export function operationIndex(s: AutomedPneumoniaState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function operationFrame(plan: StoryPlan, i: number) {
  if (plan.recipe !== 'automed-pneumonia-cls-v1') throw new Error('Pneumonia recipe mismatch');
  const n = Math.min(2, Math.max(0, Math.round(i)));
  const b = plan.beats.find(
    (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - n / 2) < 1e-6,
  );
  if (!b) throw new Error('Missing canonical operation');
  return b.startFrame;
}
export function referenceVisible(s: AutomedPneumoniaState) {
  return s.scene === 'reference' && s.reference > 0.5;
}

export function publicTrainingLabel(s: AutomedPneumoniaState) {
  return referenceVisible(s) ? source.native_example.canonical_helper_label : null;
}
