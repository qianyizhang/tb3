import sourceRaw from '../../task-explorer/automedbench-full-pathology-caption-100-task/source.json?raw';
import fixtureRaw from '../../task-explorer/automedbench-full-pathology-caption-100-task/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  runtime_discrepancy: string;
  notice: { label: string; text: string; url: string; link_label: string };
};
export const fixture = JSON.parse(fixtureRaw) as { text: string };
export const automedPathology100Pack = { source };
export type AutomedPathology100State = Extract<
  StoryState,
  { recipe: 'automed-pathology-caption-100-v1' }
>;
export const steps = ['One-image unit', 'Caption syntax', 'Pathology metric gap'] as const;
export function operationIndex(s: AutomedPathology100State) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function operationFrame(p: StoryPlan, i: number) {
  if (!Number.isInteger(i) || i < 0 || i > 2) throw new Error('Invalid step');
  if (p.recipe !== 'automed-pathology-caption-100-v1')
    throw new Error('Pathology100 recipe mismatch');
  const b = p.beats.find(
    (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - Math.round(i) / 2) < 1e-6,
  );
  if (!b) throw new Error('Missing operation beat');
  return b.startFrame;
}
export function referenceVisible(s: AutomedPathology100State, readerRevealed = false) {
  return s.scene === 'reference' && readerRevealed;
}

export function resetOnBackward(previous: number, current: number) {
  return current < previous;
}
