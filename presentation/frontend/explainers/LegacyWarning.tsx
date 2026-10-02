import type { StoryPlan } from '../types';
import { storyPresentation } from '../task-visuals/story-recipes';
import { SourceWarning } from '../task-visuals/SourceWarning';
export default function LegacyWarning({ plan }: { plan: StoryPlan }) {
  return <SourceWarning warning={storyPresentation(plan).warning} />;
}
