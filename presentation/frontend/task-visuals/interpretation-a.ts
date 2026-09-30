import healthagentbench_source from '../../task-explorer/healthagentbench/source.json?raw';
import healthagentbench_operation from '../../task-explorer/healthagentbench/operation.json?raw';
import healthagentbench_output from '../../task-explorer/healthagentbench/output.json?raw';
import radagent_source from '../../task-explorer/radagent/source.json?raw';
import radagent_operation from '../../task-explorer/radagent/operation.json?raw';
import radagent_output from '../../task-explorer/radagent/output.json?raw';
import healthagentbench_tumor_tiles_source from '../../task-explorer/healthagentbench-tumor-tiles/source.json?raw';
import healthagentbench_tumor_tiles_operation from '../../task-explorer/healthagentbench-tumor-tiles/operation.json?raw';
import healthagentbench_tumor_tiles_output from '../../task-explorer/healthagentbench-tumor-tiles/output.json?raw';
import healthagentbench_cxr_correction_source from '../../task-explorer/healthagentbench-cxr-correction/source.json?raw';
import healthagentbench_cxr_correction_operation from '../../task-explorer/healthagentbench-cxr-correction/operation.json?raw';
import healthagentbench_cxr_correction_output from '../../task-explorer/healthagentbench-cxr-correction/output.json?raw';

export type InterpretationARecipe =
  | 'healthagentbench-ct-findings-v1'
  | 'radagent-report-v1'
  | 'healthagentbench-tumor-tiles-v1'
  | 'healthagentbench-cxr-correction-v1';
export type InterpretationAScene =
  'input' | 'inspect' | 'operation' | 'schema' | 'reference' | 'limits';
export type InterpretationAState = {
  recipe: InterpretationARecipe;
  scene: InterpretationAScene;
  cursor: number;
  detail: number;
  reference: number;
};
type Source = {
  role: string;
  title: string;
  notice: { label: string; text: string; url: string; link_label: string };
  [key: string]: unknown;
};
type Operation = {
  type: string;
  checklist?: string[];
  tool_names?: string[];
  steps?: string[];
  step?: string;
  grid_formula?: string;
  grid_domain?: { x: number[]; y: number[] };
  tumor_threshold_from_public_row?: number;
  tile_semantics?: string;
  source_gold?: string;
  action_schema?: Record<string, string>;
  [key: string]: unknown;
};
type Output = {
  role: 'required-schema-only';
  path: string;
  schema: unknown;
  prediction: null;
  score: null;
  reference: null;
};
export type InterpretationAPack = {
  key:
    | 'healthagentbench'
    | 'radagent'
    | 'healthagentbench-tumor-tiles'
    | 'healthagentbench-cxr-correction';
  source: Source;
  operation: Operation;
  output: Output;
  overview?: string;
};
export const interpretationAPacks: Record<InterpretationARecipe, InterpretationAPack> = {
  'healthagentbench-ct-findings-v1': {
    key: 'healthagentbench',
    source: JSON.parse(healthagentbench_source),
    operation: JSON.parse(healthagentbench_operation),
    output: JSON.parse(healthagentbench_output),
  },
  'radagent-report-v1': {
    key: 'radagent',
    source: JSON.parse(radagent_source),
    operation: JSON.parse(radagent_operation),
    output: JSON.parse(radagent_output),
  },
  'healthagentbench-tumor-tiles-v1': {
    key: 'healthagentbench-tumor-tiles',
    source: JSON.parse(healthagentbench_tumor_tiles_source),
    operation: JSON.parse(healthagentbench_tumor_tiles_operation),
    output: JSON.parse(healthagentbench_tumor_tiles_output),
  },
  'healthagentbench-cxr-correction-v1': {
    key: 'healthagentbench-cxr-correction',
    source: JSON.parse(healthagentbench_cxr_correction_source),
    operation: JSON.parse(healthagentbench_cxr_correction_operation),
    output: JSON.parse(healthagentbench_cxr_correction_output),
  },
};
export function inspectionTile(cursor: number) {
  const index = Math.max(0, Math.min(699, Math.round(Math.max(0, Math.min(1, cursor)) * 699)));
  return { x: index % 28, y: Math.floor(index / 28), index };
}
