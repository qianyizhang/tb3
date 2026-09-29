import sourceRaw from '../../task-explorer/cardiac-real-echo/source.json?raw';
import outputRaw from '../../task-explorer/cardiac-real-echo/output.json?raw';
import reviewRaw from '../../task-explorer/cardiac-real-echo/review.json?raw';

export type CardiacRealEchoState = {
  recipe: 'cardiac-real-echo-v1';
  scene:
    | 'inputs'
    | 'geometry'
    | 'interpretation'
    | 'reconstruction'
    | 'alternatives'
    | 'review'
    | 'controls'
    | 'limits';
  phase: number;
  planes: number;
  output: number;
  alternative: number;
  review: number;
  control: number;
};

type Plane = { name: string; origin: number[]; u: number[]; v: number[] };
type View = { name: string; frames: string[]; plane: Plane };
export const realEchoSource = JSON.parse(sourceRaw) as {
  frame: string;
  source_shape_T_rho_phi_theta: number[];
  image_shape_hw: number[];
  spacing_mm: number;
  pixel_center: number;
  times_seconds: number[];
  task_axes: Record<'depth' | 'transverse_1' | 'transverse_2', number[]>;
  views: View[];
  roles: string;
};
export const realEchoOutput = JSON.parse(outputRaw) as {
  frame: string;
  ring_sample_rule: string;
  primary_rings_mm: number[][][][];
  basal_alternative_rings_mm: number[][][][];
  primary_sections_px: string[][];
  basal_alternative_plane0_sections_px: string[];
  volume_ml: number[];
  alternative_volume_ml: number[][];
  static_control_volume_ml: number[];
  artifact_reward: Record<string, number>;
  replay: {
    static: {
      changed_pngs: number;
      total_pngs: number;
      primary_and_alternatives_exactly_unchanged: boolean;
      retained_motion_rms_mm: number;
    };
    pose: { points_rmse_mm: number };
  };
};
export const realEchoReview = JSON.parse(reviewRaw) as {
  role: string;
  views: View[];
  primary_sections_px: string[][];
  intersection_frames: Record<string, number[]>;
};
export const realEchoFrame = (phase: number) => Math.max(0, Math.min(17, Math.round(phase * 17)));
export const realEchoRevealed = (state: CardiacRealEchoState) =>
  state.review > 0.5 && (state.scene === 'review' || state.scene === 'limits');
export const realEchoColors = {
  output: '#22d7e0',
  alternative: '#f3ad73',
  review: '#e7be5c',
  control: '#9daec2',
};
