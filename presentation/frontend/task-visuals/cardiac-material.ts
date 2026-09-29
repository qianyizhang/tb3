import sourceRaw from '../../task-explorer/cardiac-material/source.json?raw';
import outputRaw from '../../task-explorer/cardiac-material/output.json?raw';
import referenceRaw from '../../task-explorer/cardiac-material/reference.json?raw';

export type MaterialScene =
  'inputs' | 'initial' | 'tracking' | 'tetra' | 'strain' | 'comparison' | 'controls' | 'limits';
export type MaterialMethod = 'video_affine' | 'tissue_fit';
export type CardiacMaterialState = {
  recipe: 'cardiac-material-v1';
  scene: MaterialScene;
  phase: number;
  helper: number;
  output: number;
  reference: number;
};
export type Point3 = [number, number, number];
export type Point2 = [number, number];
export type MaterialSeries = {
  sample_points_mm: Point3[][];
  tracked_seed_projected_pixels: Point2[][][];
  tetra_vertices_mm: Point3[][];
  F: number[][][];
  E_green_lagrange: number[][][];
  J: number[];
  engineering_strain: (number | null)[][];
  missing_axis: { J: number[]; engineering_strain: [null, null, null] };
  global_engineering_percent: number[][];
  tissue_volume_ml: number[];
};
export const materialSource = JSON.parse(sourceRaw) as {
  frame_count: number;
  image_size: number;
  spacing_mm_per_pixel: number;
  pixel_center: number;
  sample_vertex_ids: number[];
  initial_points_mm: Point3[];
  views: {
    name: string;
    origin_mm: Point3;
    u: Point3;
    v: Point3;
    seed_ids: number[];
    images: string[];
  }[];
  tetra: {
    id: number;
    aha: number;
    vertex_ids: number[];
    initial_vertices_mm: Point3[];
    directions: Point3[];
  };
  missing_axis_cell: { id: number; aha: number; direction_supported: false };
};
export const materialOutput = JSON.parse(outputRaw) as {
  sample_vertex_ids: number[];
  selected_tetra_id: number;
  missing_axis_cell_id: number;
  methods: Record<MaterialMethod, MaterialSeries>;
};
export const materialReference = JSON.parse(referenceRaw) as {
  sample_vertex_ids: number[];
  sample_points_mm: Point3[][];
  tetra_vertices_mm: Point3[][];
  engineering_strain: (number | null)[][];
  global_engineering_percent: number[][];
  tissue_volume_ml: number[];
  directional_coverage: {
    positive_aha_cells: number;
    usable_axes: number;
    missing_cell_ids: number[];
    aha0_excluded: number;
  };
  metrics: Record<
    'static' | MaterialMethod,
    {
      rmse_mm: number;
      tissue_volume_error_percent: number;
      directional_mae_pp?: number[];
    }
  >;
};
export const materialFrame = (phase: number) => Math.min(29, Math.max(0, Math.round(phase * 29)));
export const materialReveal = (state: CardiacMaterialState) =>
  state.reference > 0.5 && ['comparison', 'controls', 'limits'].includes(state.scene);
export const materialMethod = (scene: MaterialScene): MaterialMethod =>
  scene === 'tracking' ? 'video_affine' : 'tissue_fit';
export const materialColors = {
  input: '#9caaba',
  affine: '#37b8ec',
  tissue: '#18c6d4',
  reference: '#f4bc49',
};
