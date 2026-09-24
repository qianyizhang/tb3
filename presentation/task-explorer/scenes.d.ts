import type { TaskEntry } from '../frontend/contracts.generated';

export const TaskScenes: {
  mode(entry: TaskEntry): '3d' | 'static';
  figure(entry: TaskEntry, locale?: 'en' | 'zh-CN'): string;
  mount(root: Element, entry: TaskEntry, locale?: 'en' | 'zh-CN'): () => void;
};
