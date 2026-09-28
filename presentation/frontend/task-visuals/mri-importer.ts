import inputs from '../../task-explorer/mri-importer/inputs.json?raw';
import output from '../../task-explorer/mri-importer/output.json?raw';
import reference from '../../task-explorer/mri-importer/reference.json?raw';
import type { StoryState } from './story-timeline';
export type MriImporterState = Extract<StoryState, { recipe: 'mri-importer-v1' }>;
export interface MriFrame {
  storage: number;
  target: number[];
  time: number;
  echo_ms: number;
  projection_mm: number;
  position_lps: number[];
  ordinals: number[];
  pixels: number[][];
}
export interface MriCase {
  name: string;
  shape: number[];
  rows: MriFrame[];
  temporal_indices: number[];
  echo_ms: number[];
  orientation: number[];
  spacing_row_column_mm: number[];
  normal: number[];
  levels_mm: number[];
  descriptors: { keyword: string; ordinal_to_actual: Record<string, number> }[];
  geometry_placement: string;
}
export const mriInputs = JSON.parse(inputs) as { cases: MriCase[]; window: number[] };
export const mriOutput = JSON.parse(output) as {
  cases: {
    pixels: number[][][][][];
    affine_lps: number[][];
    temporal_indices: number[];
    echo_ms: number[];
  }[];
  relocation: { max_affine_entry_error: number; max_landmark_error_mm: number };
};
export const mriReference = JSON.parse(reference) as {
  results: Record<string, { passed: number; report: { passed: string[]; failures: string[] } }>;
  diagnostics: Record<string, { passed: string[]; failures: string[] }>;
  shapes: { name: string; shape: number[] }[];
};
export function mriIndex(value: number, count: number) {
  return Math.min(count - 1, Math.max(0, Math.floor(value * count)));
}
export function mriSelection(s: MriImporterState) {
  return {
    frame:
      s.scene === 'outputs'
        ? mriInputs.cases[1].rows.findIndex((f) => f.target.every((v) => v === 0))
        : mriIndex(s.view, 12),
    corner: mriIndex(s.view, 8),
    reference: s.reference > 0.5,
    output: s.output > 0.5,
  };
}
export function mriSlot(frame: MriFrame, shape: number[]) {
  return (frame.target[0] * shape[1] + frame.target[1]) * shape[2] + frame.target[2];
}
export function mriPoint(affine: number[][], point: number[]) {
  return affine
    .slice(0, 3)
    .map((row) => row[3] + row.slice(0, 3).reduce((sum, v, i) => sum + v * point[i], 0));
}
export function mriCorners(shape: number[]) {
  return [0, shape[4] - 1].flatMap((c) =>
    [0, shape[3] - 1].flatMap((r) => [0, shape[2] - 1].map((z) => [c, r, z])),
  );
}
export function mriGray(value: number) {
  return Math.round(Math.max(0, Math.min(1, (value + 3000) / 6000)) * 255);
}
