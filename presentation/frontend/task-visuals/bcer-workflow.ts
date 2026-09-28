import inputs from '../../task-explorer/bcer-workflow/inputs.json?raw';
import contract from '../../task-explorer/bcer-workflow/contract.json?raw';
import type { StoryState } from './story-timeline';
export type BcerState = Extract<StoryState, { recipe: 'bcer-workflow-v1' }>;
export const bcerInputs = JSON.parse(inputs) as {
  case: string;
  sequences: {
    name: string;
    size_xyz: number[];
    spacing_xyz_mm: number[];
    slice_k: number;
    png: string;
  }[];
  witnesses: { lps_mm: number[]; native_ijk: number[][] }[];
};
export const bcerContract = JSON.parse(contract) as {
  contract: {
    required_stage_success: string[];
    required_artifacts: { id: string; tool: string; data_key: string }[];
    invariants: { id: string; type: string }[];
  };
  template: {
    nodes: {
      node_id: string;
      tool_name: string;
      required: boolean;
      depends_on: string[];
      arguments: Record<string, unknown>;
    }[];
  };
  validator_examples: {
    id: string;
    base_success_rule: boolean;
    tcr: { completed: number; total: number };
    invariants_passed: number;
    invariants: { id: string; ok: boolean }[];
  }[];
};
export function bcerSelection(s: BcerState) {
  const count =
    s.scene === 'dependencies' ? 8 : s.scene === 'artifacts' ? 4 : s.scene === 'metrics' ? 5 : 3;
  return Math.min(count - 1, Math.floor(s.view * count));
}
export function bcerPixel(point: readonly number[]) {
  return [point[0] + 0.5, point[1] + 0.5];
}
