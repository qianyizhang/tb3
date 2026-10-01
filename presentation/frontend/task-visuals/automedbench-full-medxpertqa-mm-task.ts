import sourceRaw from '../../task-explorer/automedbench-full-medxpertqa-mm-task/source.json?raw';
import referenceRaw from '../../task-explorer/automedbench-full-medxpertqa-mm-task/reference.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;

  source_question: {
    id: string;
    question: string;
    options: Record<string, string>;
    images: string[];
  };
  notice: { label: string; text: string; url: string; link_label: string };
};
export const reference = JSON.parse(referenceRaw) as {
  label: string;
  option_text: string;
  role: string;
};
export const automedMedxpertPack = { source };
export type AutomedMedxpertState = Extract<StoryState, { recipe: 'automed-medxpert-mm-v1' }>;
export const steps = ['Question + image', 'Option mapping', 'Output schema'] as const;
export const letters = ['A', 'B', 'C', 'D', 'E'] as const;
export function operationIndex(s: AutomedMedxpertState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function optionIndex(s: AutomedMedxpertState) {
  return Math.min(4, Math.max(0, Math.round(s.detail * 4)));
}
export function operationFrame(p: StoryPlan, i: number, o = 0) {
  if (!Number.isInteger(i) || i < 0 || i > 2 || !Number.isInteger(o) || o < 0 || o > 4)
    throw new Error('Invalid operation/option');
  if (p.recipe !== 'automed-medxpert-mm-v1') throw new Error('MedXpert recipe mismatch');
  const b = p.beats.find(
    (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - Math.round(i) / 2) < 1e-6,
  );
  if (!b) throw new Error('Missing operation beat');
  if (i !== 1) return b.startFrame;
  const t = Math.min(4, Math.max(0, Math.round(o))) / 4;
  let best = 0,
    d = Infinity;
  for (let k = 0; k < b.frames; k++) {
    const u = k / b.frames,
      z = u * u * (3 - 2 * u),
      v = Math.abs(z - t);
    if (v < d) {
      d = v;
      best = k;
    }
  }
  return b.startFrame + best;
}
export function referenceVisible(s: AutomedMedxpertState, readerRevealed = false) {
  return s.scene === 'reference' && readerRevealed;
}
export function resetOnBackward(previous: number, current: number) {
  return current < previous;
}
