import type { TaskEntry } from '../frontend/contracts.generated';

export const TaskScenes: {
  figure(entry: TaskEntry): string;
  mount(root: Element, entry: TaskEntry): () => void;
};
