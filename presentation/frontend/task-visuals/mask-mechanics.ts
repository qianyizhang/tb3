import sourceRaw from '../../task-explorer/mask-mechanics/source.json?raw';
import outputRaw from '../../task-explorer/mask-mechanics/output.json?raw';
import referenceRaw from '../../task-explorer/mask-mechanics/reference.json?raw';

export type MaskMechanicsSceneName =
  | 'input-masks'
  | 'input-images'
  | 'mesh-construction'
  | 'fixed-connectivity'
  | 'deformation-gradient'
  | 'occupancy'
  | 'material-ambiguity'
  | 'reference-probes'
  | 'clinical-transfer'
  | 'limits';
export type MaskMechanicsState = {
  recipe: 'cardiac-mask-mechanics-v1';
  scene: MaskMechanicsSceneName;
  phase: number;
  condition: number;
  output: number;
  reference: number;
  clinical: number;
};
export type Condition = 'masks' | 'masks-images';
export const mmSource = JSON.parse(sourceRaw) as {
  frame: string;
  spacing_mm: number;
  origin_xyz_mm: number[];
  array_order: string;
  semantics: string;
  phase_count: number;
  physical_timestamps_s: null;
  slice_zyx: number[];
  views: string[];
  input_masks_png: string[][];
  input_images_png: string[][];
  input_contours_px: string[][];
  image_display: string;
  analytic_ambiguity: { geometry: string; twisted_J: number; conclusion: string };
  clinical: {
    frame: string;
    origin_xyz_mm: number[];
    spacing_mm: number;
    semantics: string;
    slice_zyx: number[];
    times_seconds: number[];
    mask_png: string[][];
  };
};
type AnswerCondition = {
  vertices: number;
  tetrahedra: number;
  sample_rule: string;
  sampled_points_mm: number[][][];
  selected_cell_index: number;
  selected_cell_vertex_indices: number[];
  selected_vertices_mm: number[][][];
  selected_F: number[][][];
  selected_E_fraction: number[][][];
  selected_J: number[];
  saved_sections_px: string[][];
  mask_dice: number[];
  construction_reward: number;
};
export const mmOutput = JSON.parse(outputRaw) as {
  frame: string;
  conditions: Record<Condition, AnswerCondition>;
  clinical: Record<
    'clinical-masks' | 'clinical-masks-images',
    {
      volume_ml: number[];
      mask_volume_ml: number[];
      ef_pct: number;
      myocardial_strain_supported: false;
      construction_reward: number;
    }
  >;
};
export const mmReference = JSON.parse(referenceRaw) as {
  role: string;
  source_cell: number;
  source_AHA_label: number;
  source_reference_weight: number;
  source_trajectory_mm: number[][];
  source_engineering_strain_pp: number[][];
  conditions: Record<
    Condition,
    {
      fixed_answer_tetra_for_source_probe: number;
      barycentric_weights: number[];
      predicted_probe_trajectory_mm: number[][];
      predicted_engineering_strain_pp: number[][];
      material_coverage_pct: number;
      motion_rmse_mm: number;
      radial_mae_pp: number;
    }
  >;
  controls: Record<string, { role: string; construction_reward: number }>;
  missing_direction: string;
};
export const mmFrame = (state: MaskMechanicsState) =>
  Math.max(
    0,
    Math.min(
      state.scene === 'clinical-transfer' ? 17 : 29,
      Math.round(state.phase * (state.scene === 'clinical-transfer' ? 17 : 29)),
    ),
  );
export const mmCondition = (state: MaskMechanicsState): Condition =>
  state.condition > 0.5 ? 'masks-images' : 'masks';
export const mmReveal = (state: MaskMechanicsState) =>
  state.reference > 0.5 && (state.scene === 'reference-probes' || state.scene === 'limits');
export const mmColors = {
  input: '#f4bc49',
  output: '#22d7e0',
  reference: '#b797f0',
  images: '#b9c5d0',
};
