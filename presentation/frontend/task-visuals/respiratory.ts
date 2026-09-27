import raw from '../../task-explorer/respiratory/geometry.json?raw';
import output from '../../task-explorer/respiratory/output.json?raw';
import reference from '../../task-explorer/respiratory/reference.json?raw';
import type { StoryState } from './story-timeline';
export type RespiratoryState = Extract<StoryState, { recipe: 'respiratory-v1' }>;
export type CTPlane = {
  name: string;
  width: number;
  height: number;
  origin_world_mm: number[];
  dx_world_mm: number[];
  dy_world_mm: number[];
  gray_u8: string;
  png: string;
};
type Answer = { query_ids: string[]; points_world_mm: number[][] };
type View = {
  plane: CTPlane;
  pixels_uv: number[][];
  source_world_mm: number[][];
  query_ids: string[];
};
export const respiratory = JSON.parse(raw) as {
  views: { patient1: View; patient3: View };
  source_sections: CTPlane[];
  target_sections: CTPlane[];
  target_returned_patch: CTPlane[];
  volume_shape: number[];
};
export const respiratoryOutput = (JSON.parse(output) as { answer: Answer }).answer;
export const respiratoryReference = JSON.parse(reference) as {
  truth: Answer & { rms_tolerance_mm: number; max_tolerance_mm: number };
  conditions: {
    condition: string;
    answer: Answer;
    grade: { rms_mm: number; max_mm: number; per_point_mm: number[] };
  }[];
};
export const respiratoryColors = { query: '#efa933', returned: '#41c5b6', reference: '#e880ad' };
export const focusQuery = 5;
export const q06Error = Math.hypot(
  ...respiratoryOutput.points_world_mm[focusQuery].map(
    (v, i) => v - respiratoryReference.truth.points_world_mm[focusQuery][i],
  ),
);
export const planePoint = (plane: CTPlane, u: number, v: number) =>
  plane.origin_world_mm.map((x, i) => x + u * plane.dx_world_mm[i] + v * plane.dy_world_mm[i]);
export function planePixels(plane: CTPlane, point: number[]) {
  const d = point.map((v, i) => v - plane.origin_world_mm[i]);
  return [plane.dx_world_mm, plane.dy_world_mm].map(
    (axis) =>
      d.reduce((sum, v, i) => sum + v * axis[i], 0) / axis.reduce((sum, v) => sum + v * v, 0),
  );
}
export const isRespiratoryCloseup = (scene: RespiratoryState['scene']) =>
  ['reference', 'judgment'].includes(scene);
/** A proper display rotation, shared within each source/target frame. No estimated registration. */
export function respiratoryDisplay(p: number[], center: number[], shift = 0) {
  const [x, y, z] = p.map((v, i) => (v - center[i]) * (i === 0 ? 1 : -1));
  const a = 0.7,
    b = -0.6,
    xx = Math.cos(a) * x + Math.sin(a) * z,
    zz = -Math.sin(a) * x + Math.cos(a) * z;
  return [xx + shift, Math.cos(b) * y - Math.sin(b) * zz, Math.sin(b) * y + Math.cos(b) * zz];
}
export function respiratoryPlacement(
  scene: RespiratoryState['scene'],
  side: 'source' | 'target',
  p: number[],
) {
  const close = isRespiratoryCloseup(scene);
  return respiratoryDisplay(
    p,
    close ? respiratoryOutput.points_world_mm[focusQuery] : [167.125, 119.375, 181.125],
    close ? 0 : side === 'source' ? -225 : 225,
  );
}
export function respiratoryRows(state: RespiratoryState) {
  const count = Math.floor(state.output * 8 + 1e-8);
  return respiratoryOutput.query_ids.map((id, i) => ({
    id,
    point: i < count ? respiratoryOutput.points_world_mm[i] : null,
    reference: state.reference > 0.5 ? respiratoryReference.truth.points_world_mm[i] : null,
    error: state.reference > 0.5 ? respiratoryReference.conditions[1].grade.per_point_mm[i] : null,
  }));
}
