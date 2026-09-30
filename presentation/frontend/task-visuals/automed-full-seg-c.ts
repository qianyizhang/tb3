import pancreas_source from '../../task-explorer/automedbench-full-pancreas-seg-task/source.json?raw';
import pancreas_operation from '../../task-explorer/automedbench-full-pancreas-seg-task/operation.json?raw';
import pancreas_output from '../../task-explorer/automedbench-full-pancreas-seg-task/output.json?raw';
import pancreas_helper from '../../task-explorer/automedbench-full-pancreas-seg-task/helper.json?raw';
import pancreas_ct_0 from '../../task-explorer/automedbench-full-pancreas-seg-task/ct-0.png?url';
import pancreas_ct_1 from '../../task-explorer/automedbench-full-pancreas-seg-task/ct-1.png?url';
import pancreas_ct_2 from '../../task-explorer/automedbench-full-pancreas-seg-task/ct-2.png?url';
import panther_t1_source from '../../task-explorer/automedbench-full-panther-t1-seg-task/source.json?raw';
import panther_t1_operation from '../../task-explorer/automedbench-full-panther-t1-seg-task/operation.json?raw';
import panther_t1_output from '../../task-explorer/automedbench-full-panther-t1-seg-task/output.json?raw';
import panther_t1_helper from '../../task-explorer/automedbench-full-panther-t1-seg-task/helper.json?raw';
import panther_t2_source from '../../task-explorer/automedbench-full-panther-t2-seg-task/source.json?raw';
import panther_t2_operation from '../../task-explorer/automedbench-full-panther-t2-seg-task/operation.json?raw';
import panther_t2_output from '../../task-explorer/automedbench-full-panther-t2-seg-task/output.json?raw';
import panther_t2_helper from '../../task-explorer/automedbench-full-panther-t2-seg-task/helper.json?raw';
import prostate_source from '../../task-explorer/automedbench-full-prostate-seg-task/source.json?raw';
import prostate_operation from '../../task-explorer/automedbench-full-prostate-seg-task/operation.json?raw';
import prostate_output from '../../task-explorer/automedbench-full-prostate-seg-task/output.json?raw';
import prostate_helper from '../../task-explorer/automedbench-full-prostate-seg-task/helper.json?raw';
import prostate_t2_0 from '../../task-explorer/automedbench-full-prostate-seg-task/t2-0.png?url';
import prostate_t2_1 from '../../task-explorer/automedbench-full-prostate-seg-task/t2-1.png?url';
import prostate_t2_2 from '../../task-explorer/automedbench-full-prostate-seg-task/t2-2.png?url';
import prostate_adc_0 from '../../task-explorer/automedbench-full-prostate-seg-task/adc-0.png?url';
import prostate_adc_1 from '../../task-explorer/automedbench-full-prostate-seg-task/adc-1.png?url';
import prostate_adc_2 from '../../task-explorer/automedbench-full-prostate-seg-task/adc-2.png?url';
import prostate_label_0 from '../../task-explorer/automedbench-full-prostate-seg-task/training-label-0.png?url';
import prostate_label_1 from '../../task-explorer/automedbench-full-prostate-seg-task/training-label-1.png?url';
import prostate_label_2 from '../../task-explorer/automedbench-full-prostate-seg-task/training-label-2.png?url';

export type AutoMedSegCRecipe =
  | 'automed-full-pancreas-seg-v1'
  | 'automed-full-panther-t1-seg-v1'
  | 'automed-full-panther-t2-seg-v1'
  | 'automed-full-prostate-seg-v1';
export type AutoMedSegCScene = 'input' | 'channels' | 'mapping' | 'output' | 'helper' | 'limits';
export type AutoMedSegCState = {
  recipe: AutoMedSegCRecipe;
  scene: AutoMedSegCScene;
  slice: number;
  helper: number;
  output: number;
};
type Slice = { native_k: number; t2_image?: string; adc_image?: string; ct_image?: string };
type Geometry = {
  shape_ijk_channels?: number[];
  shape_ijk?: number[];
  voxel_spacing_mm: number[];
  axis_codes: string;
  affine: number[][];
  display_transform: string;
  window_stored_intensity?: number[];
  intensity_units?: string;
};
type Source = {
  title: string;
  role: string;
  input_filename: string;
  geometry: Geometry | null;
  slices: Slice[];
  notice: { label: string; text: string; url: string; link_label: string };
  full_case_membership: false;
};
type Operation = {
  type: 'two-channel-zonal-segmentation' | 'dual-binary-organ-lesion';
  input_channels?: { index: number; name: string }[];
  spatial_operation: string;
  labels?: Record<string, string>;
  modality?: string;
  source_mapping?: string;
  binary_outputs?: { file: string; foreground: string; values: number[] }[];
  training_helper?: string;
};
type Output = {
  type: string;
  files: string[];
  label_values: Record<string, string>;
  same_spatial_shape_required: boolean;
  affine_alignment_required_for_interpretation: boolean;
  prediction: null;
  dice: null;
  score_contract: string;
};
type Helper = {
  role: string;
  slices: string[];
  slice_label_voxels: { peripheral_zone: number; transition_zone: number }[];
  full_private_reference: null;
  prediction: null;
  warning: string;
};
export type SegCPack = {
  key: 'pancreas' | 'panther-t1' | 'panther-t2' | 'prostate';
  source: Source;
  operation: Operation;
  output: Output;
  helper: Helper;
  ct: string[];
  t2: string[];
  adc: string[];
  labels: string[];
};
export const segCPacks: Record<AutoMedSegCRecipe, SegCPack> = {
  'automed-full-pancreas-seg-v1': {
    key: 'pancreas',
    source: JSON.parse(pancreas_source),
    operation: JSON.parse(pancreas_operation),
    output: JSON.parse(pancreas_output),
    helper: JSON.parse(pancreas_helper),
    ct: [pancreas_ct_0, pancreas_ct_1, pancreas_ct_2],
    t2: [],
    adc: [],
    labels: [],
  },
  'automed-full-panther-t1-seg-v1': {
    key: 'panther-t1',
    source: JSON.parse(panther_t1_source),
    operation: JSON.parse(panther_t1_operation),
    output: JSON.parse(panther_t1_output),
    helper: JSON.parse(panther_t1_helper),
    ct: [],
    t2: [],
    adc: [],
    labels: [],
  },
  'automed-full-panther-t2-seg-v1': {
    key: 'panther-t2',
    source: JSON.parse(panther_t2_source),
    operation: JSON.parse(panther_t2_operation),
    output: JSON.parse(panther_t2_output),
    helper: JSON.parse(panther_t2_helper),
    ct: [],
    t2: [],
    adc: [],
    labels: [],
  },
  'automed-full-prostate-seg-v1': {
    key: 'prostate',
    source: JSON.parse(prostate_source),
    operation: JSON.parse(prostate_operation),
    output: JSON.parse(prostate_output),
    helper: JSON.parse(prostate_helper),
    ct: [],
    t2: [prostate_t2_0, prostate_t2_1, prostate_t2_2],
    adc: [prostate_adc_0, prostate_adc_1, prostate_adc_2],
    labels: [prostate_label_0, prostate_label_1, prostate_label_2],
  },
};
export const segCIndex = (s: AutoMedSegCState, p: SegCPack) => {
  const n = p.ct.length || p.t2.length;
  return n
    ? Math.max(0, Math.min(n - 1, Math.round(Math.max(0, Math.min(1, s.slice)) * (n - 1))))
    : 0;
};
export const segCHelperRevealed = (s: AutoMedSegCState, p: SegCPack) =>
  s.scene === 'helper' && s.helper > 0.5 && p.labels.length > 0;
