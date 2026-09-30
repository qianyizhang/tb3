import sourceRaw from '../../task-explorer/abra-viewer-control/source.json?raw';
import operationRaw from '../../task-explorer/abra-viewer-control/operation.json?raw';
import outputRaw from '../../task-explorer/abra-viewer-control/output.json?raw';
import type { StoryState } from './story-timeline';

export type AbraViewerState = Extract<StoryState, { recipe: 'abra-viewer-control-v1' }>;
export type AbraViewerSource = {
  notice: { label: string; text: string; url: string; link_label: string };
  title: string;
  instance_count: number;
  initial_slice_index: number;
  study_uid: string;
  series_uid: string;
  observed_viewport: null;
  viewer_index_mapping_verified: false;
  preview: {
    data_uri: string;
    archive_member: string;
    dicom_instance_number: number;
    viewer_slice_index: null;
    window_center_hu: number;
    window_width_hu: number;
    pixel_spacing_mm: [number, number];
  };
};
export type AbraViewerOperation = {
  target_formula: string;
  target_slice_index: number;
  state_key: string;
  candidate_min: number;
  candidate_max: number;
  input_action: string;
};
export const abraViewerPack = {
  basis: 'mixed' as const,
  source: JSON.parse(sourceRaw) as AbraViewerSource,
  operation: JSON.parse(operationRaw) as AbraViewerOperation,
  output: JSON.parse(outputRaw) as {
    path: string;
    requested_state: { sliceIndex: number };
    observed_state: null;
    prediction: null;
    reference: null;
    score: null;
  },
};
