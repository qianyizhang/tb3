import raw from '../../task-explorer/automedbench-full-synthrad2025-mrct-task/source.json?raw';
import ref from '../../task-explorer/automedbench-full-synthrad2025-mrct-task/reference.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export const source = JSON.parse(raw) as {
  notice: { label: string; text: string; url: string; link_label: string };
  actual_data_gap: string;
  task_contract: { metrics: string; rating: string; assistance: string };
};
export const reference = JSON.parse(ref) as {
  rules: string;
  rating: string;
  clean_image: null;
  actual_metric: null;
};
export const automedSynthradMrctPack = { source };
export type AutomedSynthradMrctState = Extract<
  StoryState,
  { recipe: 'automedbench-full-synthrad2025-mrct-task-v1' }
>;
export const steps = [
  'MR and mask',
  'Same grid, new domain',
  'Tier and format',
  'Metric denominators',
] as const;
export function operationIndex(s: AutomedSynthradMrctState) {
  return Math.min(3, Math.max(0, Math.round(s.progress * 3)));
}
export function operationFrame(p: StoryPlan, i: number) {
  if (!Number.isInteger(i) || i < 0 || i > 3) throw new Error('Invalid step');
  if (p.recipe !== 'automedbench-full-synthrad2025-mrct-task-v1')
    throw new Error('MRCT recipe mismatch');
  const b = p.beats.find(
    (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - i / 3) < 1e-6,
  );
  if (!b) throw new Error('Missing operation beat');
  return b.startFrame;
}
export function referenceVisible(s: AutomedSynthradMrctState, revealed = false) {
  return s.scene === 'reference' && revealed;
}
export function resetOnBackward(previous: number, current: number) {
  return current < previous;
}

export function canonicalMetric(v: string) {
  return ['MAE', 'PSNR', 'SSIM'].includes(v) ? v : null;
}
