import sourceRaw from '../../task-explorer/named-landmarks/source.json?raw';
import outputRaw from '../../task-explorer/named-landmarks/output.json?raw';
import referenceRaw from '../../task-explorer/named-landmarks/reference.json?raw';
import type { StoryState } from './story-timeline';
export type LandmarkState = Extract<StoryState, { recipe: 'named-landmarks-v1' }>;
export type LandmarkCase = 'full' | 'partial' | 'pddca' | 'mri';
export type LandmarkPoint = { status: string; ijk: number[] | null };
export type LandmarkPlane = {
  axis: number;
  index: number;
  u_axis: number;
  v_axis: number;
  origin_uv: number[];
  step: number;
  width: number;
  height: number;
  extent_mm: number[];
  png: string;
};
type NativeCase = {
  shape: number[];
  affine: number[][];
  spacing: number[];
  positive_axes: string[];
  queries: string[];
};
type Grade = {
  success_counts?: Record<string, number>;
  score: {
    errors_mm: Record<string, number>;
    mean_mm?: number;
    mean_localized_error_mm?: number;
    missed_visible?: number;
    localized_visible?: number;
    hallucinated?: { out_of_fov: number; absent: number };
  };
};
export const landmarkSource = JSON.parse(sourceRaw) as {
  cases: Record<LandmarkCase, NativeCase>;
  views: Record<string, LandmarkPlane[]>;
};
export const landmarkOutputs = JSON.parse(outputRaw) as Record<
  LandmarkCase,
  Partial<Record<'terra' | 'sol', Record<string, LandmarkPoint>>>
>;
export const landmarkReference = JSON.parse(referenceRaw) as {
  points: Record<LandmarkCase, Record<string, LandmarkPoint>>;
  grades: Record<LandmarkCase, Partial<Record<'terra' | 'sol', Grade>>>;
  rater_max_distance_mm: Record<string, number>;
};
export const landmarkColors = { terra: '#fb923c', sol: '#cf94ff', reference: '#54deaa' };
export const landmarkRevealed = (s: LandmarkState) => s.reference > 0.5;
export const landmarkReturned = (s: LandmarkState) => s.output > 0.5;
export function landmarkWorld(caseId: LandmarkCase, point: number[]) {
  return landmarkSource.cases[caseId].affine
    .slice(0, 3)
    .map((row) => row[3] + row.slice(0, 3).reduce((sum, v, i) => sum + v * point[i], 0));
}
export function landmarkProjection(plane: LandmarkPlane, caseId: LandmarkCase, point: number[]) {
  return {
    u: (point[plane.u_axis] - plane.origin_uv[0]) / plane.step + 0.5,
    v: plane.height - ((point[plane.v_axis] - plane.origin_uv[1]) / plane.step + 0.5),
    offset: (point[plane.axis] - plane.index) * landmarkSource.cases[caseId].spacing[plane.axis],
  };
}
export function landmarkSelection(s: LandmarkState) {
  const caseId: LandmarkCase =
    s.scene === 'condyle'
      ? 'pddca'
      : ['mri', 'counterexample'].includes(s.scene)
        ? 'mri'
        : 'partial';
  const key =
    s.scene === 'condyle'
      ? 'mand_r'
      : s.scene === 'mri'
        ? '20'
        : s.scene === 'counterexample'
          ? '1'
          : s.scene === 'availability'
            ? 'T5'
            : 'T4';
  const view =
    caseId === 'pddca' ? 'pddca-condyle' : caseId === 'mri' ? `mri-${key}` : 'partial-T5';
  const sweep = landmarkSource.views['partial-sweep'];
  return {
    caseId,
    key,
    referenceKey: caseId === 'partial' ? 'T5' : key,
    planes:
      s.scene === 'search'
        ? [sweep[Math.min(sweep.length - 1, Math.floor(s.view * sweep.length))]]
        : landmarkSource.views[view],
    reveal: landmarkRevealed(s),
    output: landmarkReturned(s),
  };
}
