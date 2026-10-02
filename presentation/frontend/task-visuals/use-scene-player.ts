import type { StoryPlan } from '../types';
import type { VisualEntry } from './types';
import { useFramePlayer } from '../explainers/player/use-frame-player';
import { nativeFactory, isPlanarStory, hasInteractiveProjection } from './story-recipes';
import { TaskSceneModels } from './recipes';
import { SceneStage } from './stage';
export type { PlayerActions } from '../explainers/player/use-frame-player';
const spatial = { create: SceneStage.create, native: nativeFactory, models: TaskSceneModels };
/** Compatibility adapter: all views share the same frame clock and resource lifetime. */
export function useScenePlayer(entry: VisualEntry, plan?: StoryPlan) {
  return useFramePlayer(entry, plan, {
    planar: !!plan && isPlanarStory(plan),
    interactiveProjection: !!plan && hasInteractiveProjection(plan),
    spatial,
  });
}
