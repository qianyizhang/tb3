import bccdSourceRaw from '../../task-explorer/automedbench-full-bccd-det-task/source.json?raw';
import bccdOutputRaw from '../../task-explorer/automedbench-full-bccd-det-task/output.json?raw';
import bccdReferenceRaw from '../../task-explorer/automedbench-full-bccd-det-task/reference.json?raw';
import bccdImage from '../../task-explorer/automedbench-full-bccd-det-task/BloodImage_00000.jpg?url';
import dentexSourceRaw from '../../task-explorer/automedbench-full-dentex-det-task/source.json?raw';
import dentexOutputRaw from '../../task-explorer/automedbench-full-dentex-det-task/output.json?raw';
import dentexReferenceRaw from '../../task-explorer/automedbench-full-dentex-det-task/reference.json?raw';
import dentexImage from '../../task-explorer/automedbench-full-dentex-det-task/train_266.png?url';
import grazSourceRaw from '../../task-explorer/automedbench-full-grazpedwri-det-task/source.json?raw';
import grazOutputRaw from '../../task-explorer/automedbench-full-grazpedwri-det-task/output.json?raw';
import grazReferenceRaw from '../../task-explorer/automedbench-full-grazpedwri-det-task/reference.json?raw';
import grazImage from '../../task-explorer/automedbench-full-grazpedwri-det-task/0001_1297860435_01_WRI-L2_M014.png?url';
import vindrSourceRaw from '../../task-explorer/automedbench-full-vindr-cxr-det-task/source.json?raw';
import vindrOutputRaw from '../../task-explorer/automedbench-full-vindr-cxr-det-task/output.json?raw';
import vindrReferenceRaw from '../../task-explorer/automedbench-full-vindr-cxr-det-task/reference.json?raw';

export type AutoMedDetectionRecipe =
  | 'automed-full-bccd-detection-v1'
  | 'automed-full-dentex-detection-v1'
  | 'automed-full-grazpedwri-detection-v1'
  | 'automed-full-vindr-cxr-detection-v1';
export type AutoMedDetectionSceneName =
  'input' | 'coordinate' | 'classes' | 'submission' | 'reference' | 'limits';
export type AutoMedDetectionState = {
  recipe: AutoMedDetectionRecipe;
  scene: AutoMedDetectionSceneName;
  scan: number;
  format: number;
  reference: number;
};
export type DetectionBox = {
  id: number;
  class: string;
  xyxy: [number, number, number, number];
  source_hierarchy?: { quadrant_id: number; tooth_id: number; disease_id: number };
};
type Source = {
  role: string;
  image: string | null;
  width_px: number | null;
  height_px: number | null;
  title: string;
  classes: string[];
  task_detail: string;
  upstream_annotation_role: string;
  full_data_dir: string;
  notice: { label: string; text: string; url: string; link_label: string };
};
type Output = {
  path: string;
  prediction_json: { boxes: [] };
  score_rule: string;
  coordinate_rule: string;
  prediction: null;
  mAP: null;
};
type Reference = {
  role: string;
  full_private_boxes: null;
  source_boxes: DetectionBox[];
  source_box_count: number;
  warning: string;
};
export type DetectionPack = {
  key: 'bccd' | 'dentex' | 'grazpedwri' | 'vindr-cxr';
  source: Source;
  output: Output;
  reference: Reference;
  image: string | null;
};
export const detectionPacks: Record<AutoMedDetectionRecipe, DetectionPack> = {
  'automed-full-bccd-detection-v1': {
    key: 'bccd',
    source: JSON.parse(bccdSourceRaw),
    output: JSON.parse(bccdOutputRaw),
    reference: JSON.parse(bccdReferenceRaw),
    image: bccdImage,
  },
  'automed-full-dentex-detection-v1': {
    key: 'dentex',
    source: JSON.parse(dentexSourceRaw),
    output: JSON.parse(dentexOutputRaw),
    reference: JSON.parse(dentexReferenceRaw),
    image: dentexImage,
  },
  'automed-full-grazpedwri-detection-v1': {
    key: 'grazpedwri',
    source: JSON.parse(grazSourceRaw),
    output: JSON.parse(grazOutputRaw),
    reference: JSON.parse(grazReferenceRaw),
    image: grazImage,
  },
  'automed-full-vindr-cxr-detection-v1': {
    key: 'vindr-cxr',
    source: JSON.parse(vindrSourceRaw),
    output: JSON.parse(vindrOutputRaw),
    reference: JSON.parse(vindrReferenceRaw),
    image: null,
  },
};
export const detectionReveal = (state: AutoMedDetectionState, pack: DetectionPack) =>
  state.scene === 'reference' && state.reference > 0.5 && pack.reference.source_box_count > 0;
