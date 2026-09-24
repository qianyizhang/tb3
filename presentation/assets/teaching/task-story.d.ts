import type { VisualEntry } from '../../frontend/task-visuals/types';
export interface TaskStory {
  action: string;
  cue: string;
  form: string;
  context: string;
  stages: [string, string, string];
}
export const TaskTeachingStory: { describe(entry: VisualEntry): TaskStory };
