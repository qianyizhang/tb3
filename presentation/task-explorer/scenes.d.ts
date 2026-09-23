import type { TaskEntry } from '../frontend/contracts.generated';

export const TaskScenes: {
  figure(entry: TaskEntry, locale?: 'en' | 'zh-CN'): string;
  mount(root: Element, entry: TaskEntry, locale?: 'en' | 'zh-CN'): () => void;
};
