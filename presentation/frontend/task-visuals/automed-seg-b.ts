import hepaticSourceRaw from '../../task-explorer/automedbench-full-hepaticvessel-seg-task/source.json?raw';
import hepaticOutputRaw from '../../task-explorer/automedbench-full-hepaticvessel-seg-task/output.json?raw';
import kidneySourceRaw from '../../task-explorer/automedbench-full-kidney-seg-task/source.json?raw';
import kidneyOutputRaw from '../../task-explorer/automedbench-full-kidney-seg-task/output.json?raw';
import kidneyReferenceRaw from '../../task-explorer/automedbench-full-kidney-seg-task/reference.json?raw';
import liverSourceRaw from '../../task-explorer/automedbench-full-liver-seg-task/source.json?raw';
import liverOutputRaw from '../../task-explorer/automedbench-full-liver-seg-task/output.json?raw';
import liverReferenceRaw from '../../task-explorer/automedbench-full-liver-seg-task/reference.json?raw';
import pancreasSourceRaw from '../../task-explorer/automedbench-full-pancreas-oar-seg-task/source.json?raw';
import pancreasOutputRaw from '../../task-explorer/automedbench-full-pancreas-oar-seg-task/output.json?raw';

export type AutomedSegBKey = 'hepaticvessel' | 'kidney' | 'liver' | 'pancreas-oar';
export type AutomedSegBSceneName =
  'inputs' | 'mapping' | 'output' | 'reference' | 'scorer' | 'limits';
export type AutomedSegBState = {
  recipe:
    | 'automed-full-hepaticvessel-v1'
    | 'automed-full-kidney-v1'
    | 'automed-full-liver-v1'
    | 'automed-full-pancreas-oar-v1';
  scene: AutomedSegBSceneName;
  view: number;
  class: number;
  reference: number;
};
export type SourceDoc = {
  entry_id: string;
  role: string;
  native_geometry: null | {
    shape_ijk: number[];
    voxel_spacing_mm: number[];
    affine_first_three_rows: number[][];
    slice_axis_ijk: number;
    axis_display: string;
    window_hu: number[];
  };
  views: { native_index: number; ct_png: string }[];
  notice: { label: string; text: string; url: string };
  license: string;
};
export type OutputDoc = {
  role: string;
  paths: string[];
  labels: Record<string, string>;
  mask_layout: 'separate-binary' | 'combined-integer';
  prediction: null;
  score: null;
  scorer_checks_affine: false;
  scoring_note: string;
};
export const segBData: Record<
  AutomedSegBKey,
  { source: SourceDoc; output: OutputDoc; title: string; short: string }
> = {
  hepaticvessel: {
    source: JSON.parse(hepaticSourceRaw),
    output: JSON.parse(hepaticOutputRaw),
    title: 'Hepatic vessels and tumor',
    short: 'MSD Task08 CT',
  },
  kidney: {
    source: JSON.parse(kidneySourceRaw),
    output: JSON.parse(kidneyOutputRaw),
    title: 'Kidney and lesion',
    short: 'KiTS19 CT',
  },
  liver: {
    source: JSON.parse(liverSourceRaw),
    output: JSON.parse(liverOutputRaw),
    title: 'Liver and lesion',
    short: 'MSD Task03 CT',
  },
  'pancreas-oar': {
    source: JSON.parse(pancreasSourceRaw),
    output: JSON.parse(pancreasOutputRaw),
    title: '21 pancreas-region structures',
    short: 'PanTS contract',
  },
};
export type SegBReaderReference = {
  role: string;
  views: { index: number; overlay_png: string; organ_voxels: number; lesion_voxels: number }[];
  mapping: { target: string; rule: string; color: string }[];
  full_private_reference: null;
  prediction: null;
};
export const segBKidneyReference = JSON.parse(kidneyReferenceRaw) as SegBReaderReference;
export const segBLiverReference = JSON.parse(liverReferenceRaw) as SegBReaderReference;
export const segBIndex = (value: number, length: number) =>
  Math.min(length - 1, Math.max(0, Math.floor(value * length)));
