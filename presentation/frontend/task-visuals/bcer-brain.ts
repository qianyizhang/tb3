import diagramRaw from '../../task-explorer/bcer-brain/diagram.json?raw';
import contractRaw from '../../task-explorer/bcer-brain/contract.json?raw';

export type BcerBrainScene = 'inputs' | 'identify' | 'segment' | 'labels' | 'checks' | 'limits';
export type BcerBrainState = {
  recipe: 'bcer-brain-v1';
  scene: BcerBrainScene;
  view: number;
};

export const brainDiagram = JSON.parse(diagramRaw) as {
  kind: string;
  case_pixels: false;
  coordinates: string;
  modalities: { name: string; alias: string; tone: string; slot: number }[];
  label_key: { value: number; name: string; color: string }[];
  whole_tumor_labels: number[];
};

export const brainContract = JSON.parse(contractRaw) as {
  source_commit: string;
  task: string;
  contract: {
    required_modalities_all_of: string[];
    required_stage_success: string[];
    required_artifacts: string[];
    invariants: string[];
    semantic_fault: string;
  };
  tool_behavior: { normal: string; fallback: string; observed_execution: false };
  evaluator_limit: string;
};
