import sourceRaw from '../../task-explorer/rexmle-neurips-cellseg/source.json?raw';
import helperRaw from '../../task-explorer/rexmle-neurips-cellseg/helper.json?raw';
import outputRaw from '../../task-explorer/rexmle-neurips-cellseg/output.json?raw';
import metricRaw from '../../task-explorer/rexmle-neurips-cellseg/metric.json?raw';
import imageUrl from '../../task-explorer/rexmle-neurips-cellseg/cell_00944.png?url';
import instanceMapUrl from '../../task-explorer/rexmle-neurips-cellseg/instance-map.png?url';
import foregroundMapUrl from '../../task-explorer/rexmle-neurips-cellseg/foreground-map.png?url';

export type RexCellsegSceneName =
  'input' | 'helper' | 'instances' | 'submission' | 'scoring' | 'limits';
export type RexCellsegState = {
  recipe: 'rexmle-neurips-cellseg-v1';
  scene: RexCellsegSceneName;
  helper: number;
  instance: number;
  metric: number;
};
export type CellInstance = {
  id: number;
  pixels: number;
  bbox_xyxy_inclusive: [number, number, number, number];
  color_rgb: [number, number, number];
  focus_image: string | null;
};
export const cellsegSource = JSON.parse(sourceRaw) as {
  role: string;
  image_id: string;
  width_px: number;
  height_px: number;
  split: {
    source_training_pairs: number;
    source_tuning_pairs: number;
    reconstructed_public_train: number;
    reconstructed_private_test: number;
    sample_role: string;
    preparer_executed: false;
  };
  notice: { label: string; text: string; url: string; link_label: string };
};
export const cellsegHelper = JSON.parse(helperRaw) as {
  role: string;
  instance_count: number;
  foreground_pixel_count: number;
  total_pixel_count: number;
  focus_ids: number[];
  instances: CellInstance[];
  meaning: string;
};
export const cellsegOutput = JSON.parse(outputRaw) as {
  role: string;
  status: 'not-retained';
  csv_columns: string[];
  row_template: { image_id: string; predicted_mask_path: string };
  prediction_mask: null;
  f1: null;
};
export const cellsegMetric = JSON.parse(metricRaw) as {
  thresholds_iou: number[];
  boundary_margin_px: number;
  large_image_branch: { at_least_pixels: number; roi_size_px: number[] };
  shape_mismatch: string;
  score: null;
};
export const cellsegImage = imageUrl;
export const cellsegInstanceMap = instanceMapUrl;
export const cellsegForegroundMap = foregroundMapUrl;
const focusImages = import.meta.glob<string>(
  '../../task-explorer/rexmle-neurips-cellseg/cells/*.png',
  { eager: true, query: '?url', import: 'default' },
);
export function cellsegFocusImage(instance: CellInstance): string {
  if (!instance.focus_image) throw new Error(`No teaching crop for instance ${instance.id}`);
  const url = focusImages[`../../task-explorer/rexmle-neurips-cellseg/${instance.focus_image}`];
  if (!url) throw new Error(`Missing source training instance ${instance.id}`);
  return url;
}
export function cellsegSelectedInstance(value: number): CellInstance {
  const choices = cellsegHelper.focus_ids;
  const index = Math.max(0, Math.min(choices.length - 1, Math.round(value * (choices.length - 1))));
  return cellsegHelper.instances[choices[index] - 1];
}
