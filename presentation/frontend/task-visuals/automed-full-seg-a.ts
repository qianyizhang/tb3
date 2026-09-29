import aeropathSourceRaw from '../../task-explorer/automedbench-full-aeropath-seg-task/source.json?raw';
import aeropathOutputRaw from '../../task-explorer/automedbench-full-aeropath-seg-task/output.json?raw';
import aeropathReferenceRaw from '../../task-explorer/automedbench-full-aeropath-seg-task/reference.json?raw';
import aeropathImage0 from '../../task-explorer/automedbench-full-aeropath-seg-task/slice-0.png?url';
import aeropathLabel0 from '../../task-explorer/automedbench-full-aeropath-seg-task/source-label-0.png?url';
import aeropathImage1 from '../../task-explorer/automedbench-full-aeropath-seg-task/slice-1.png?url';
import aeropathLabel1 from '../../task-explorer/automedbench-full-aeropath-seg-task/source-label-1.png?url';
import aeropathImage2 from '../../task-explorer/automedbench-full-aeropath-seg-task/slice-2.png?url';
import aeropathLabel2 from '../../task-explorer/automedbench-full-aeropath-seg-task/source-label-2.png?url';
import colonSourceRaw from '../../task-explorer/automedbench-full-colon-seg-task/source.json?raw';
import colonOutputRaw from '../../task-explorer/automedbench-full-colon-seg-task/output.json?raw';
import colonReferenceRaw from '../../task-explorer/automedbench-full-colon-seg-task/reference.json?raw';
import colonImage0 from '../../task-explorer/automedbench-full-colon-seg-task/slice-0.png?url';
import colonLabel0 from '../../task-explorer/automedbench-full-colon-seg-task/source-label-0.png?url';
import colonImage1 from '../../task-explorer/automedbench-full-colon-seg-task/slice-1.png?url';
import colonLabel1 from '../../task-explorer/automedbench-full-colon-seg-task/source-label-1.png?url';
import colonImage2 from '../../task-explorer/automedbench-full-colon-seg-task/slice-2.png?url';
import colonLabel2 from '../../task-explorer/automedbench-full-colon-seg-task/source-label-2.png?url';
import fetaSourceRaw from '../../task-explorer/automedbench-full-feta-seg-task/source.json?raw';
import fetaOutputRaw from '../../task-explorer/automedbench-full-feta-seg-task/output.json?raw';
import fetaReferenceRaw from '../../task-explorer/automedbench-full-feta-seg-task/reference.json?raw';
import heartSourceRaw from '../../task-explorer/automedbench-full-heart-seg-task/source.json?raw';
import heartOutputRaw from '../../task-explorer/automedbench-full-heart-seg-task/output.json?raw';
import heartReferenceRaw from '../../task-explorer/automedbench-full-heart-seg-task/reference.json?raw';
import heartImage0 from '../../task-explorer/automedbench-full-heart-seg-task/slice-0.png?url';
import heartLabel0 from '../../task-explorer/automedbench-full-heart-seg-task/source-label-0.png?url';
import heartImage1 from '../../task-explorer/automedbench-full-heart-seg-task/slice-1.png?url';
import heartLabel1 from '../../task-explorer/automedbench-full-heart-seg-task/source-label-1.png?url';
import heartImage2 from '../../task-explorer/automedbench-full-heart-seg-task/slice-2.png?url';
import heartLabel2 from '../../task-explorer/automedbench-full-heart-seg-task/source-label-2.png?url';
export type AutoMedSegARecipe =
  | 'automed-full-aeropath-seg-v1'
  | 'automed-full-colon-seg-v1'
  | 'automed-full-feta-seg-v1'
  | 'automed-full-heart-seg-v1';
export type AutoMedSegAScene = 'input' | 'stack' | 'labels' | 'schema' | 'reference' | 'limits';
export type AutoMedSegAState = {
  recipe: AutoMedSegARecipe;
  scene: AutoMedSegAScene;
  slice: number;
  format: number;
  reference: number;
};
type Slice = { image: string; native_k: number };
type Source = {
  role: string;
  title: string;
  input_filename: string;
  shape_ijk: number[] | null;
  voxel_spacing_mm: number[] | null;
  affine: number[][] | null;
  axis_codes: string | null;
  display_transform: string | null;
  intensity_window: number[] | null;
  slices: Slice[];
  notice: { label: string; text: string; url: string; link_label: string };
  full_case_membership: 'unverified';
};
type Output = {
  path: string;
  status: 'not-retained';
  label_values: Record<string, string>;
  prediction: null;
  dice: null;
};
type Reference = {
  role: string;
  source_label_slices: string[];
  slice_label_voxels: Record<string, number>[];
  full_private_reference: null;
  label_values: Record<string, string>;
  fusion: string | null;
  warning: string;
};
export type SegAPack = {
  key: 'aeropath' | 'colon' | 'feta' | 'heart';
  source: Source;
  output: Output;
  reference: Reference;
  images: string[];
  labels: string[];
};
export const segAPacks: Record<AutoMedSegARecipe, SegAPack> = {
  'automed-full-aeropath-seg-v1': {
    key: 'aeropath',
    source: JSON.parse(aeropathSourceRaw),
    output: JSON.parse(aeropathOutputRaw),
    reference: JSON.parse(aeropathReferenceRaw),
    images: [aeropathImage0, aeropathImage1, aeropathImage2],
    labels: [aeropathLabel0, aeropathLabel1, aeropathLabel2],
  },
  'automed-full-colon-seg-v1': {
    key: 'colon',
    source: JSON.parse(colonSourceRaw),
    output: JSON.parse(colonOutputRaw),
    reference: JSON.parse(colonReferenceRaw),
    images: [colonImage0, colonImage1, colonImage2],
    labels: [colonLabel0, colonLabel1, colonLabel2],
  },
  'automed-full-feta-seg-v1': {
    key: 'feta',
    source: JSON.parse(fetaSourceRaw),
    output: JSON.parse(fetaOutputRaw),
    reference: JSON.parse(fetaReferenceRaw),
    images: [],
    labels: [],
  },
  'automed-full-heart-seg-v1': {
    key: 'heart',
    source: JSON.parse(heartSourceRaw),
    output: JSON.parse(heartOutputRaw),
    reference: JSON.parse(heartReferenceRaw),
    images: [heartImage0, heartImage1, heartImage2],
    labels: [heartLabel0, heartLabel1, heartLabel2],
  },
};
export const segAIndex = (s: AutoMedSegAState, p: SegAPack) =>
  Math.min(
    p.images.length - 1,
    Math.max(0, Math.round(Math.min(1, Math.max(0, s.slice)) * Math.max(0, p.images.length - 1))),
  );
export const segARevealed = (s: AutoMedSegAState, p: SegAPack) =>
  s.scene === 'reference' && s.reference > 0.5 && p.labels.length > 0;
