import spleenSourceRaw from '../../task-explorer/automedbench-full-spleen-seg-task/source.json?raw';
import spleenOutputRaw from '../../task-explorer/automedbench-full-spleen-seg-task/output.json?raw';
import spleenReferenceRaw from '../../task-explorer/automedbench-full-spleen-seg-task/reference.json?raw';
import tsgSourceRaw from '../../task-explorer/automedbench-full-tsg-multiorgan-seg-task/source.json?raw';
import tsgOutputRaw from '../../task-explorer/automedbench-full-tsg-multiorgan-seg-task/output.json?raw';

export type AutomedSegDKey = 'spleen' | 'tsg-multiorgan';
export type AutomedSegDScene = 'inputs' | 'mapping' | 'output' | 'reference' | 'scorer' | 'limits';
export type AutomedSegDState = {
  recipe: 'automed-full-spleen-v1' | 'automed-full-tsg-multiorgan-v1';
  scene: AutomedSegDScene;
  view: number;
  label: number;
  reference: number;
};
export type SourceDoc = {
  entry_id: string;
  source_case: string;
  role: string;
  full_case_membership: 'unverified';
  native_geometry: { shape: number[]; spacing_mm: number[]; affine: number[][] };
  views: { index: number; width: number; height: number; png: string }[];
  display: string;
  selection: string;
  window_hu: number[];
  notice: { label: string; text: string; url: string };
};
export type OutputDoc = {
  path: string;
  labels: Record<string, string>;
  prediction: null;
  score: null;
  scorer_checks_affine: false;
  scorer_boundary: string;
};
export const segDData: Record<
  AutomedSegDKey,
  { source: SourceDoc; output: OutputDoc; title: string; license: string }
> = {
  spleen: {
    source: JSON.parse(spleenSourceRaw),
    output: JSON.parse(spleenOutputRaw),
    title: 'Spleen from CT',
    license: 'CC-BY-SA-4.0',
  },
  'tsg-multiorgan': {
    source: JSON.parse(tsgSourceRaw),
    output: JSON.parse(tsgOutputRaw),
    title: '117 CT structures',
    license: 'CC-BY-4.0',
  },
};
export const spleenTrainingLabel = JSON.parse(spleenReferenceRaw) as {
  role: string;
  source_case: string;
  views: { index: number; overlay_png: string; source_label_voxels: number }[];
};
export const segDIndex = (value: number, length: number) =>
  Math.min(length - 1, Math.max(0, Math.floor(value * length)));
