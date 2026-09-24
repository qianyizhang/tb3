import type { VisualEntry } from '../../frontend/task-visuals/types';
export const TaskTeachingArt: {
  render(entry: VisualEntry, output?: boolean): string;
  scan(subject: string): string;
};
