import n01Raw from '../../task-explorer/aneurysm-localization/n01.json?raw';
import n02Raw from '../../task-explorer/aneurysm-localization/n02.json?raw';
import n03Raw from '../../task-explorer/aneurysm-localization/n03.json?raw';
import outputRaw from '../../task-explorer/aneurysm-localization/output.json?raw';
import referenceRaw from '../../task-explorer/aneurysm-localization/reference.json?raw';
import type { StoryState } from './story-timeline';
export type AneurysmState = Extract<StoryState, { recipe: 'aneurysm-localization-v1' }>;
export type AneurysmCase = 'n01' | 'n02' | 'n03';
export type AneurysmPlane = {
  axis: number;
  index: number | null;
  bounds: number[];
  kind: 'mip' | 'slice';
  volume: string;
  window: number[];
  width: number;
  height: number;
  u_axis: number;
  v_axis: number;
  extent_mm: number[];
  png: string;
  selection: string;
};
type Case = {
  shape: number[];
  spacing_mm: number[];
  affine: number[][];
  axes: string[];
  display_high: number;
  views: Record<string, AneurysmPlane>;
};
export const aneurysmCases = {
  n01: JSON.parse(n01Raw),
  n02: JSON.parse(n02Raw),
  n03: JSON.parse(n03Raw),
} as Record<AneurysmCase, Case>;
export const aneurysmOutputs = JSON.parse(outputRaw) as {
  cases: Record<
    AneurysmCase,
    {
      answer: { aneurysms: number[][] };
      trace: {
        annotation_inventory_exposed: boolean;
        public_source_match_observed: boolean;
        agent_seconds: number;
        output_tokens: number;
      };
    }
  >;
};
export type AneurysmContour = { paths: number[][][]; pixels: number };
export const aneurysmReference = JSON.parse(referenceRaw) as {
  views: Record<string, { weak: AneurysmContour; accepted: AneurysmContour }>;
  cases: Record<
    AneurysmCase,
    {
      regions: { center_ijk: number[]; source_voxels: number; accepted_voxels: number }[];
      subject: string;
      group: string;
    }
  >;
  n02_point_to_centroid_mm: number;
  n02_inside_source_region: boolean;
};
export const aneurysmColors = { output: '#32d8e2', weak: '#9beb72', accepted: '#f5d76e' };
export const aneurysmDepths = [84, 88, 92, 94, 96, 100, 104] as const;
export function aneurysmSelection(s: AneurysmState) {
  const index = (n: number) => Math.min(n - 1, Math.floor(s.view * n));
  const caseId: AneurysmCase = ['miss', 'coverage'].includes(s.scene)
    ? 'n01'
    : s.scene === 'negative'
      ? 'n03'
      : 'n02';
  return {
    caseId,
    slab: index(12),
    depth: aneurysmDepths[index(7)],
    reference: s.reference > 0.5,
    output: s.output > 0.5,
  };
}
export function aneurysmPixel(p: AneurysmPlane, point: number[], spacing: number[]) {
  return {
    x: point[p.u_axis] - p.bounds[p.u_axis * 2] + 0.5,
    y: p.bounds[p.v_axis * 2 + 1] - point[p.v_axis] - 0.5,
    offset_mm: p.index === null ? null : (point[p.axis] - p.index) * spacing[p.axis],
  };
}
export const aneurysmPath = (r: AneurysmContour) =>
  r.paths.map((p) => p.map(([x, y], i) => `${i ? 'L' : 'M'}${x} ${y}`).join('') + 'Z').join('');
