import sourceRaw from '../../task-explorer/radagent-vqa/source.json?raw';
import fixtureRaw from '../../task-explorer/radagent-vqa/formatting-fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../types';
export type RadagentVqaState = Extract<StoryState, { recipe: 'radagent-vqa-v1' }>;
export const radagentVqaPack = {
  source: JSON.parse(sourceRaw) as {
    notice: { label: string; text: string; url: string; link_label: string };
    actual_data_gap: string;
    source_roles: { scorer: string; reference: string };
  },
  fixture: JSON.parse(fixtureRaw) as {
    options: string[];
    teaching_selected_option: string;
    candidate_controls: { candidate: string; exact_toy_full_option: boolean }[];
  },
};
export const operationLabels = ['Whole volume', 'Selected slices', 'Reconcile evidence'] as const;
export function operationIndex(progress: number) {
  return Math.max(0, Math.min(2, Math.round(progress * 2)));
}
export function operationFrame(plan: StoryPlan, index: number) {
  if (plan.recipe !== 'radagent-vqa-v1') throw new Error('VQA recipe mismatch');
  const beat = plan.beats.find(
    (b) => b.scene === 'operation' && operationIndex(b.channels.progress[0]) === index,
  );
  if (!beat) throw new Error('Missing VQA operation beat');
  return beat.startFrame;
}
export function vqaReferenceVisible(state: RadagentVqaState) {
  return state.scene === 'reference' && state.reference > 0.5;
}
export function fullOptionFormatMatches(candidate: string, chosen: string) {
  return candidate.trim().toLowerCase() === chosen.trim().toLowerCase();
}
