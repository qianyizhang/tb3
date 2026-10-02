import type { StoryPlan } from '../../types';
import { sampleStory } from '../../task-visuals/story-timeline';

export function operationIndex(progress: number, count: number): number {
  return Math.max(0, Math.min(count - 1, Math.round(progress * (count - 1))));
}
/** Seek through the canonical sampler; no duplicated easing or independent interaction clock. */
export function operationFrame(plan: StoryPlan, index: number, count: number): number {
  if (!Number.isInteger(index) || index < 0 || index >= count)
    throw new RangeError('Invalid operation');
  const beat = plan.beats.find((beat) => 'scene' in beat && beat.scene === 'operation');
  if (!beat) throw new Error('Operation chapter is absent');
  let frame = beat.startFrame,
    distance = Infinity;
  for (let at = beat.startFrame; at < beat.endFrame; at++) {
    const state = sampleStory(plan, at);
    if (!('progress' in state)) throw new Error('Restoration progress channel is absent');
    const candidate = Math.abs(state.progress - index / Math.max(1, count - 1));
    if (candidate < distance - 1e-12) {
      frame = at;
      distance = candidate;
    }
  }
  return frame;
}
