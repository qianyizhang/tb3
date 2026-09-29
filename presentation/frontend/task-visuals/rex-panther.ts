import task1Raw from '../../task-explorer/rex-panther-task1/source.json?raw';
import task2Raw from '../../task-explorer/rex-panther-task2/source.json?raw';
import output1Raw from '../../task-explorer/rex-panther-task1/output.json?raw';
import output2Raw from '../../task-explorer/rex-panther-task2/output.json?raw';
import diagram1Raw from '../../task-explorer/rex-panther-task1/diagram.json?raw';
import diagram2Raw from '../../task-explorer/rex-panther-task2/diagram.json?raw';

export type RexPantherSceneName = 'input' | 'geometry' | 'output' | 'reference' | 'limits';
export type RexPantherState = {
  recipe: 'rex-panther-task1-v1' | 'rex-panther-task2-v1';
  scene: RexPantherSceneName;
  grid: number;
  reference: number;
};
export type PantherSource = {
  entry_id: string;
  source_status: string;
  acquisition_route: string;
  variant: {
    name: string;
    modality: string;
    scanner: string;
    image_pattern: string;
    label_pattern: string;
    annotated_source_count: number;
    conditional_train_count: number;
    conditional_test_count: number;
    helper: string;
    domain_boundary: string;
  };
  label_semantics: Record<string, string>;
  mha_geometry: {
    dimensions: null;
    spacing_mm: null;
    origin_mm: null;
    direction: null;
  };
};
export type PantherOutput = {
  status: 'not-retained';
  prediction: null;
  submission: null;
  score: null;
  csv: string;
  csv_columns: string[];
  relative_prediction_pattern: string;
  grader: {
    metrics: string[];
    shape_mismatch: string;
    spacing: string;
    affine_origin_direction_equality_checked: false;
    task2_latency_measured: false;
  };
};
export type PantherDiagram = {
  index_grid: number[];
  world_formula: string;
  target_grid: string;
};
const source1 = JSON.parse(task1Raw) as PantherSource;
const source2 = JSON.parse(task2Raw) as PantherSource;
const output1 = JSON.parse(output1Raw) as PantherOutput;
const output2 = JSON.parse(output2Raw) as PantherOutput;
const diagram1 = JSON.parse(diagram1Raw) as PantherDiagram;
const diagram2 = JSON.parse(diagram2Raw) as PantherDiagram;
export function pantherTask(state: RexPantherState): 1 | 2 {
  return state.recipe === 'rex-panther-task1-v1' ? 1 : 2;
}
export function pantherRecords(state: RexPantherState) {
  return pantherTask(state) === 1
    ? { source: source1, output: output1, diagram: diagram1 }
    : { source: source2, output: output2, diagram: diagram2 };
}
export const pantherRevealed = (state: RexPantherState) =>
  state.scene === 'reference' && state.reference > 0.5;
