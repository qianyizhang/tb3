import source from '../../task-explorer/history-sourcing/source.json?raw';
import reference from '../../task-explorer/history-sourcing/reference.json?raw';
import type { StoryState } from './story-timeline';
export type HistorySourcingState = Extract<StoryState, { recipe: 'history-sourcing-v1' }>;
export const historySource = JSON.parse(source) as {
  counts: Record<string, number>;
  excerpts: {
    id: string;
    session_id: string;
    line: number;
    raw_record_sha256: string;
    role: string;
    excerpt: string;
    evidence_class: string;
  }[];
  candidates: {
    id: string;
    task: string | null;
    label: string;
    lead: string;
    source_strength: string;
    input: string;
    output: string;
    reference: string;
    limit: string;
    endpoint: string;
    source_ids: string[];
  }[];
};
export const historyReference = JSON.parse(reference) as {
  tasks: {
    task: string;
    source_files: number;
    task_checksum: string;
    freeze: string;
    trials: {
      agent: string;
      reward: number;
      task_checksum: string;
      agent_seconds: number;
      report: { minimum_dice?: number };
    }[];
  }[];
  controls: { id: string; error: string; evidence: string; meaning: string }[];
};
export function historyIndex(value: number, count: number) {
  return Math.min(count - 1, Math.max(0, Math.floor(value * count)));
}
export function historySelection(s: HistorySourcingState) {
  return {
    excerpt: historyIndex(s.view, 8),
    candidate: historyIndex(s.view, 5),
    task: historyIndex(s.view, 4),
    reference: s.reference > 0.5,
  };
}
