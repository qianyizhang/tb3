import inputs from '../../task-explorer/automed-multiorgan/inputs.json?raw';
import reference from '../../task-explorer/automed-multiorgan/reference.json?raw';
import contract from '../../task-explorer/automed-multiorgan/contract.json?raw';
import type { StoryState } from './story-timeline';
export type AutomedState = Extract<StoryState, { recipe: 'automed-multiorgan-v1' }>;
export const automedInputs = JSON.parse(inputs) as {
  views: { y: number; width: number; height: number; png: string }[];
};
export const automedReference = JSON.parse(reference) as {
  structures: {
    name: string;
    model_id: number;
    benchmark_id: number;
    color: string;
    png: string;
    plane_voxels: number;
    volume_voxels: number;
  }[];
};
export const automedContract = JSON.parse(contract) as {
  remap: { name: string; model_id: number; benchmark_id: number }[];
  examples: {
    id: string;
    format_valid: boolean;
    completed: number;
    total: number;
    raw_dice: number;
    task_score: number;
    rating: string;
    workflow_score: number;
  }[];
};
export function automedSelection(s: AutomedState) {
  const count =
    s.scene === 'inputs'
      ? 3
      : s.scene === 'coverage'
        ? 7
        : s.scene === 'geometry' || s.scene === 'scoring'
          ? 2
          : 5;
  const progress = s.scene === 'reference' ? Math.max(0, (s.view - 0.5) * 2) : s.view;
  return Math.min(count - 1, Math.floor(progress * count));
}
