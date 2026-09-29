import segSourceRaw from '../../task-explorer/rex-vascular-seg-a/source.json?raw';
import segOutputRaw from '../../task-explorer/rex-vascular-seg-a/output.json?raw';
import segHelperRaw from '../../task-explorer/rex-vascular-seg-a/helper.json?raw';
import ctSourceRaw from '../../task-explorer/rex-vascular-topbrain-ct/source.json?raw';
import ctOutputRaw from '../../task-explorer/rex-vascular-topbrain-ct/output.json?raw';
import ctHelperRaw from '../../task-explorer/rex-vascular-topbrain-ct/helper.json?raw';
import mrSourceRaw from '../../task-explorer/rex-vascular-topbrain-mr/source.json?raw';
import mrOutputRaw from '../../task-explorer/rex-vascular-topbrain-mr/output.json?raw';
import mrHelperRaw from '../../task-explorer/rex-vascular-topbrain-mr/helper.json?raw';
import cowSourceRaw from '../../task-explorer/rex-vascular-topcow-mr-seg/source.json?raw';
import cowOutputRaw from '../../task-explorer/rex-vascular-topcow-mr-seg/output.json?raw';
import cowReferenceRaw from '../../task-explorer/rex-vascular-topcow-mr-seg/reference.json?raw';

export type RexVascularSegRecipe =
  'rex-seg-a-v1' | 'rex-topbrain-ct-v1' | 'rex-topbrain-mr-v1' | 'rex-topcow-mr-seg-v1';
export type RexVascularSegSceneName =
  'inputs' | 'geometry' | 'operation' | 'output' | 'helper' | 'reference' | 'limits';
export type RexVascularSegState = {
  recipe: RexVascularSegRecipe;
  scene: RexVascularSegSceneName;
  slice: number;
  reference: number;
};
export type VascularSample = {
  file: string;
  native_k_zero_based: number;
  center_world_mm: number[];
  display_shape_xy: number[];
};
export type VascularSource = {
  entry_id: string;
  case_id: string;
  modality: string;
  source_role: string;
  native_input_sha256: string;
  geometry: {
    shape_ijk: number[];
    spacing_ijk_mm: number[];
    orientation: string;
    affine_ijk_to_ras_mm?: number[][];
    affine_ijk_to_lps_mm?: number[][];
  };
  fixed_window_scaled_native_values: number[];
  samples: VascularSample[];
  source_split: Record<string, number | string>;
};
export type VascularOutput = {
  status: 'not-retained';
  participant_prediction: null;
  score: null;
  columns: string[];
  relative_prediction_pattern: string;
  required_file: string;
};
export type VascularSupport = {
  role: string;
  source_sha256: string;
  classes_present: number[];
  class_colors: Record<string, string>;
  samples: {
    file: string;
    native_k_zero_based: number;
    nonzero_display_pixels: number;
    visible_label_values: number[];
  }[];
};
export type VascularRecord = {
  source: VascularSource;
  output: VascularOutput;
  support: VascularSupport;
  pack: string;
  title: string;
  sourceLink: string;
  license: string;
  privateReference: boolean;
  taskType: string;
  scorer: string;
  caveat: string;
};
const parse = <T>(raw: string) => JSON.parse(raw) as T;
const records: Record<RexVascularSegRecipe, VascularRecord> = {
  'rex-seg-a-v1': {
    source: parse(segSourceRaw),
    output: parse(segOutputRaw),
    support: parse(segHelperRaw),
    pack: 'rex-vascular-seg-a',
    title: 'SEG.A · aortic vessel tree',
    sourceLink:
      'https://figshare.com/articles/dataset/Aortic_Vessel_Tree_AVT_CTA_Datasets_and_Segmentations/14806362',
    license: 'CC BY 4.0',
    privateReference: false,
    taskType: 'binary aorta mask',
    scorer: 'Mean Dice, then Hausdorff on the adapted base test cases.',
    caveat:
      'The pinned ReX grader does not implement the original Sobol perturbation sensitivity; its case split mixes institutions.',
  },
  'rex-topbrain-ct-v1': {
    source: parse(ctSourceRaw),
    output: parse(ctOutputRaw),
    support: parse(ctHelperRaw),
    pack: 'rex-vascular-topbrain-ct',
    title: 'TopBrain · CTA vessel classes',
    sourceLink: 'https://zenodo.org/records/16878417',
    license: 'Noncommercial with attribution',
    privateReference: false,
    taskType: '40-class vessel mask',
    scorer: 'Class Dice, clDice, B0, HD95, invalid-neighbor error and side-road F1.',
    caveat:
      '2025 v1 labels differ from TopCoW. The grader copies GT physical metadata onto predictions; a score is not affine validation.',
  },
  'rex-topbrain-mr-v1': {
    source: parse(mrSourceRaw),
    output: parse(mrOutputRaw),
    support: parse(mrHelperRaw),
    pack: 'rex-vascular-topbrain-mr',
    title: 'TopBrain · MRA vessel classes',
    sourceLink: 'https://zenodo.org/records/16878417',
    license: 'Noncommercial with attribution',
    privateReference: false,
    taskType: '42-class vessel mask',
    scorer: 'Class Dice, clDice, B0, HD95, invalid-neighbor error and side-road F1.',
    caveat:
      'Exact 2025 v1 training labels. The grader copies GT physical metadata onto predictions; a score is not affine validation.',
  },
  'rex-topcow-mr-seg-v1': {
    source: parse(cowSourceRaw),
    output: parse(cowOutputRaw),
    support: parse(cowReferenceRaw),
    pack: 'rex-vascular-topcow-mr-seg',
    title: 'TopCoW · MRA CoW segmentation',
    sourceLink: 'https://zenodo.org/records/15692630',
    license: 'Noncommercial with attribution',
    privateReference: true,
    taskType: 'multiclass Circle of Willis mask',
    scorer: 'Class overlap, centerline/boundary distance, group detection and CoW topology.',
    caveat:
      'The grader resamples shape mismatches and overwrites same-shape prediction physical metadata with GT metadata; an array score is not affine validation.',
  },
};
export function vascularRecord(recipe: RexVascularSegRecipe): VascularRecord {
  return records[recipe];
}
export function vascularSample(source: VascularSource, progress: number): VascularSample {
  const index = Math.max(
    0,
    Math.min(source.samples.length - 1, Math.round(progress * (source.samples.length - 1))),
  );
  return source.samples[index];
}
export function vascularRevealed(state: RexVascularSegState): boolean {
  return (
    state.recipe === 'rex-topcow-mr-seg-v1' && state.scene === 'reference' && state.reference > 0.5
  );
}
const images = import.meta.glob<string>('../../task-explorer/rex-vascular-*/images/*.png', {
  eager: true,
  query: '?url',
  import: 'default',
});
export function vascularImage(pack: string, file: string): string {
  const key = `../../task-explorer/${pack}/${file}`;
  const url = images[key];
  if (!url) throw new Error(`Missing vascular image ${key}`);
  return url;
}
