import ctBoxSourceRaw from '../../task-explorer/rex-topcow-ct-box/source.json?raw';
import ctBoxOutputRaw from '../../task-explorer/rex-topcow-ct-box/output.json?raw';
import ctBoxReferenceRaw from '../../task-explorer/rex-topcow-ct-box/reference.json?raw';
import ctBoxDiagramRaw from '../../task-explorer/rex-topcow-ct-box/diagram.json?raw';
import mrBoxSourceRaw from '../../task-explorer/rex-topcow-mr-box/source.json?raw';
import mrBoxOutputRaw from '../../task-explorer/rex-topcow-mr-box/output.json?raw';
import mrBoxReferenceRaw from '../../task-explorer/rex-topcow-mr-box/reference.json?raw';
import mrBoxDiagramRaw from '../../task-explorer/rex-topcow-mr-box/diagram.json?raw';
import ctEdgesSourceRaw from '../../task-explorer/rex-topcow-ct-edges/source.json?raw';
import ctEdgesOutputRaw from '../../task-explorer/rex-topcow-ct-edges/output.json?raw';
import ctEdgesReferenceRaw from '../../task-explorer/rex-topcow-ct-edges/reference.json?raw';
import ctEdgesDiagramRaw from '../../task-explorer/rex-topcow-ct-edges/diagram.json?raw';
import mrEdgesSourceRaw from '../../task-explorer/rex-topcow-mr-edges/source.json?raw';
import mrEdgesOutputRaw from '../../task-explorer/rex-topcow-mr-edges/output.json?raw';
import mrEdgesReferenceRaw from '../../task-explorer/rex-topcow-mr-edges/reference.json?raw';
import mrEdgesDiagramRaw from '../../task-explorer/rex-topcow-mr-edges/diagram.json?raw';

export type RexTopcowLocalRecipe =
  | 'rex-topcow-ct-box-v1'
  | 'rex-topcow-mr-box-v1'
  | 'rex-topcow-ct-edges-v1'
  | 'rex-topcow-mr-edges-v1';
export type RexTopcowLocalSceneName =
  'inputs' | 'geometry' | 'operation' | 'output' | 'reference' | 'limits';
export type RexTopcowLocalState = {
  recipe: RexTopcowLocalRecipe;
  scene: RexTopcowLocalSceneName;
  slice: number;
  step: number;
  reference: number;
};
export type TopcowLocalSample = {
  file: string;
  native_k_zero_based: number;
  center_ras_mm: number[];
  display_shape_xy: number[];
};
export type TopcowLocalSource = {
  entry_id: string;
  case_id: string;
  modality: string;
  source_role: string;
  geometry: {
    shape_ijk: number[];
    spacing_ijk_mm: number[];
    affine_ijk_to_ras_mm: number[][];
    native_axis_basis: string;
  };
  fixed_window_scaled_native_values: number[];
  samples: TopcowLocalSample[];
};
export type TopcowLocalOutput = {
  status: 'not-retained';
  participant_prediction: null;
  score: null;
  columns: string[];
  relative_prediction_pattern: string;
  required_json_schema: Record<string, unknown> | string;
  coordinate_units: string;
};
export type TopcowBoxReference = {
  role: string;
  size_voxels: number[];
  location_voxels: number[];
  scorer_interpreted_min_corner_voxels: number[];
  scorer_interpreted_max_corner_inclusive_voxels: number[];
  description_calls_location_center: true;
  samples: { file: string; native_k_zero_based: number; intersects_scorer_box: boolean }[];
};
export type TopcowEdgeReference = {
  role: string;
  anterior: Record<string, 0 | 1>;
  posterior: Record<string, 0 | 1>;
};
export type TopcowLocalRecord = {
  source: TopcowLocalSource;
  output: TopcowLocalOutput;
  reference: TopcowBoxReference | TopcowEdgeReference;
  diagram: Record<string, unknown>;
  pack: string;
  kind: 'box' | 'edges';
  title: string;
  scorer: string;
};

const parse = <T>(raw: string): T => JSON.parse(raw) as T;
const records: Record<RexTopcowLocalRecipe, TopcowLocalRecord> = {
  'rex-topcow-ct-box-v1': {
    source: parse(ctBoxSourceRaw),
    output: parse(ctBoxOutputRaw),
    reference: parse(ctBoxReferenceRaw),
    diagram: parse(ctBoxDiagramRaw),
    pack: 'rex-topcow-ct-box',
    kind: 'box',
    title: 'TopCoW CTA · 3D ROI box',
    scorer:
      'The pinned scorer treats location as minimum corner. Boundary IoU expands each box by ceil(0.2 × size); its metric named IoU expands by ceil(0.5 × size).',
  },
  'rex-topcow-mr-box-v1': {
    source: parse(mrBoxSourceRaw),
    output: parse(mrBoxOutputRaw),
    reference: parse(mrBoxReferenceRaw),
    diagram: parse(mrBoxDiagramRaw),
    pack: 'rex-topcow-mr-box',
    kind: 'box',
    title: 'TopCoW MRA · 3D ROI box',
    scorer:
      'The pinned scorer treats location as minimum corner. Boundary IoU expands each box by ceil(0.2 × size); its metric named IoU expands by ceil(0.5 × size).',
  },
  'rex-topcow-ct-edges-v1': {
    source: parse(ctEdgesSourceRaw),
    output: parse(ctEdgesOutputRaw),
    reference: parse(ctEdgesReferenceRaw),
    diagram: parse(ctEdgesDiagramRaw),
    pack: 'rex-topcow-ct-edges',
    kind: 'edges',
    title: 'TopCoW CTA · eight named connections',
    scorer:
      'The grader converts four anterior bits and four posterior bits to variant classes; balanced accuracy is computed separately across cases, not per edge.',
  },
  'rex-topcow-mr-edges-v1': {
    source: parse(mrEdgesSourceRaw),
    output: parse(mrEdgesOutputRaw),
    reference: parse(mrEdgesReferenceRaw),
    diagram: parse(mrEdgesDiagramRaw),
    pack: 'rex-topcow-mr-edges',
    kind: 'edges',
    title: 'TopCoW MRA · eight named connections',
    scorer:
      'The grader converts four anterior bits and four posterior bits to variant classes; balanced accuracy is computed separately across cases, not per edge.',
  },
};
export function topcowLocalRecord(recipe: RexTopcowLocalRecipe): TopcowLocalRecord {
  return records[recipe];
}
export function topcowLocalSample(source: TopcowLocalSource, progress: number): TopcowLocalSample {
  const index = Math.max(
    0,
    Math.min(source.samples.length - 1, Math.round(progress * (source.samples.length - 1))),
  );
  return source.samples[index];
}
export function topcowLocalRevealed(state: RexTopcowLocalState): boolean {
  return state.scene === 'reference' && state.reference > 0.5;
}
const images = import.meta.glob<string>('../../task-explorer/rex-topcow-*-*/images/*.png', {
  eager: true,
  query: '?url',
  import: 'default',
});
export function topcowLocalImage(pack: string, file: string): string {
  const key = `../../task-explorer/${pack}/${file}`;
  const url = images[key];
  if (!url) throw new Error(`Missing TopCoW localization image ${key}`);
  return url;
}
