import tissueSourceRaw from '../../task-explorer/rexmle-puma-track1-task1/source.json?raw';
import tissueHelperRaw from '../../task-explorer/rexmle-puma-track1-task1/helper.json?raw';
import tissueOutputRaw from '../../task-explorer/rexmle-puma-track1-task1/output.json?raw';
import tissueMetricRaw from '../../task-explorer/rexmle-puma-track1-task1/metric.json?raw';
import tissueImage from '../../task-explorer/rexmle-puma-track1-task1/training-roi.png?url';
import tissueZoom from '../../task-explorer/rexmle-puma-track1-task1/training-zoom.png?url';
import tissueOverlay from '../../task-explorer/rexmle-puma-track1-task1/training-tissue-overlay.png?url';
import coarseSourceRaw from '../../task-explorer/rexmle-puma-track1-task2/source.json?raw';
import coarseHelperRaw from '../../task-explorer/rexmle-puma-track1-task2/helper.json?raw';
import coarseOutputRaw from '../../task-explorer/rexmle-puma-track1-task2/output.json?raw';
import coarseMetricRaw from '../../task-explorer/rexmle-puma-track1-task2/metric.json?raw';
import coarseImage from '../../task-explorer/rexmle-puma-track1-task2/training-roi.png?url';
import coarseZoom from '../../task-explorer/rexmle-puma-track1-task2/training-zoom.png?url';
import fineSourceRaw from '../../task-explorer/rexmle-puma-track2-task2/source.json?raw';
import fineHelperRaw from '../../task-explorer/rexmle-puma-track2-task2/helper.json?raw';
import fineOutputRaw from '../../task-explorer/rexmle-puma-track2-task2/output.json?raw';
import fineMetricRaw from '../../task-explorer/rexmle-puma-track2-task2/metric.json?raw';
import fineImage from '../../task-explorer/rexmle-puma-track2-task2/training-roi.png?url';
import fineZoom from '../../task-explorer/rexmle-puma-track2-task2/training-zoom.png?url';

export type RexPumaRecipe =
  'rexmle-puma-track1-task1-v1' | 'rexmle-puma-track1-task2-v1' | 'rexmle-puma-track2-task2-v1';
export type RexPumaSceneName =
  'input' | 'helper' | 'operation' | 'submission' | 'scoring' | 'limits';
export type RexPumaState = {
  recipe: RexPumaRecipe;
  scene: RexPumaSceneName;
  helper: number;
  focus: number;
  metric: number;
};
export type PumaPoint = {
  source_index: number;
  x_px: number;
  y_px: number;
  source_class: string;
  class: string;
};
type PumaSource = {
  case_id: string;
  width_px: number;
  height_px: number;
  split: {
    matched_image_tissue_nuclei_cases: number;
    reconstructed_public_train: number;
    reconstructed_private_label_test: number;
    selected_role: string;
    preparer_executed: false;
  };
  notice: { label: string; text: string; url: string; link_label: string };
};
type PumaHelper = {
  role: string;
  pixels_by_id?: Record<string, number>;
  selected_source_classes?: string[];
  class_ids?: Record<string, number>;
  feature_count?: number;
  accepted_polygon_count?: number;
  source_feature_count?: number;
  skipped?: Record<string, number>;
  class_counts?: Record<string, number>;
  class_mapping?: Record<string, string>;
  zoom?: { x_px: number; y_px: number; width_px: number; height_px: number; selection: string };
  points?: PumaPoint[];
};
type PumaOutput = {
  role: string;
  status: 'not-retained';
  csv_columns: string[];
  row_template: Record<string, string>;
  mask_values?: Record<string, string>;
  mask_shape_px?: number[];
  json_template?: { polygons: [] };
  prediction: null;
  score: null;
};
type PumaMetric = {
  primary: string;
  foreground_ids?: number[];
  secondary?: string;
  distance_px?: number;
  distance_rule?: string;
  match_policy?: string;
  result: null;
};
export type PumaPack = {
  source: PumaSource;
  helper: PumaHelper;
  output: PumaOutput;
  metric: PumaMetric;
  image: string;
  zoom: string;
  overlay?: string;
  task: 'tissue' | 'coarse-nuclei' | 'fine-nuclei';
};
export const pumaPacks: Record<RexPumaRecipe, PumaPack> = {
  'rexmle-puma-track1-task1-v1': {
    source: JSON.parse(tissueSourceRaw),
    helper: JSON.parse(tissueHelperRaw),
    output: JSON.parse(tissueOutputRaw),
    metric: JSON.parse(tissueMetricRaw),
    image: tissueImage,
    zoom: tissueZoom,
    overlay: tissueOverlay,
    task: 'tissue',
  },
  'rexmle-puma-track1-task2-v1': {
    source: JSON.parse(coarseSourceRaw),
    helper: JSON.parse(coarseHelperRaw),
    output: JSON.parse(coarseOutputRaw),
    metric: JSON.parse(coarseMetricRaw),
    image: coarseImage,
    zoom: coarseZoom,
    task: 'coarse-nuclei',
  },
  'rexmle-puma-track2-task2-v1': {
    source: JSON.parse(fineSourceRaw),
    helper: JSON.parse(fineHelperRaw),
    output: JSON.parse(fineOutputRaw),
    metric: JSON.parse(fineMetricRaw),
    image: fineImage,
    zoom: fineZoom,
    task: 'fine-nuclei',
  },
};
