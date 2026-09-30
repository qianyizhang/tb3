import { canonicalCheckpointClass } from './automed-skin-lesion-controls';
export { abbreviations } from './automed-skin-lesion-controls';
import sourceRaw from '../../task-explorer/automedbench-full-skin-lesion-cls-task/source.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  prompt_conflict: string;
  preview_data_uri: string;
  source_mapping: Record<string, string>;
  processor_config: {
    size: { height: number; width: number };
    rescale_factor: number;
    image_mean: number[];
    image_std: number[];
  };
  notice: { label: string; text: string; url: string; link_label: string };
};
export const automedSkinLesionPack = { source };
export type AutomedSkinLesionState = Extract<StoryState, { recipe: 'automed-skin-lesion-cls-v1' }>;
export const steps = ['RGB processor settings', 'Seven-class remap', 'Canonical files'] as const;

export function operationIndex(s: AutomedSkinLesionState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function mappingIndex(s: AutomedSkinLesionState) {
  return Math.min(6, Math.max(0, Math.round(s.detail * 6)));
}
export function canonicalForIndex(i: number) {
  return canonicalCheckpointClass(i, source.source_mapping);
}
export function operationFrame(plan: StoryPlan, i: number, mapIndex = 0) {
  if (plan.recipe !== 'automed-skin-lesion-cls-v1') throw new Error('Skin recipe mismatch');
  const n = Math.min(2, Math.max(0, Math.round(i)));
  const b = plan.beats.find(
    (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - n / 2) < 1e-6,
  );
  if (!b) throw new Error('Missing canonical operation');
  if (n !== 1) return b.startFrame;
  const target = Math.min(6, Math.max(0, Math.round(mapIndex))) / 6;
  let best = 0,
    error = Infinity;
  for (let j = 0; j < b.frames; j++) {
    const t = j / Math.max(1, b.frames - 1);
    const d = t * t * (3 - 2 * t);
    const e = Math.abs(d - target);
    if (e < error) {
      best = j;
      error = e;
    }
  }
  return b.startFrame + best;
}
export function referenceVisible(s: AutomedSkinLesionState) {
  return s.scene === 'reference' && s.reference > 0.5;
}
