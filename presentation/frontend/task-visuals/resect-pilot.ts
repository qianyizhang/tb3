import geometry from '../../task-explorer/resect-pilot/geometry.json?raw';
import trace from '../../task-explorer/resect-pilot/trace.json?raw';
import output from '../../task-explorer/resect-pilot/output.json?raw';
import reference from '../../task-explorer/resect-pilot/reference.json?raw';
import type { StoryState } from './story-timeline';
import type { ResectPlane } from './resect';
export type PilotState = Extract<StoryState, { recipe: 'resect-pilot-v1' }>;
export const pilotGeometry = (
  JSON.parse(geometry) as {
    cases: {
      case_id: string;
      source_case: string;
      mri_world_mm: number[];
      initial_us_world_mm: number[];
      modalities: Record<
        'mri' | 'us',
        { native: ResectPlane; ras: ResectPlane[]; shape: number[] }
      >;
    }[];
  }
).cases;
export const pilotTrace = JSON.parse(trace) as {
  cue_world_mm: number[];
  cue_views: { png: string }[];
  slabs: { png: string }[][];
  slab_offsets_mm: number[];
  peaks: {
    case_id: string;
    radius_mm: number;
    top_world_mm_rounded: number[];
    score_rounded: number;
  }[];
};
export const pilotAnswers = (
  JSON.parse(output) as {
    cases: { case_id: string; us_world_mm: number[]; confidence: number; evidence: string }[];
  }
).cases;
export const pilotReference = JSON.parse(reference) as {
  cases: {
    initial_world_mm: number[];
    returned_world_mm: number[];
    reference_world_mm: number[];
    initial_error_mm: number;
    final_error_mm: number;
    movement_mm: number;
  }[];
  cue_error_mm: number;
};
export const pilotSlabIndex = (view: number) => Math.round(4 * Math.max(0, Math.min(1, view)));
export const pilotReveal = (state: PilotState) => state.reference > 0.5;
export const pilotOutput = (state: PilotState) => (state.output > 0.5 ? pilotAnswers : null);
export const pilotColors = {
  initial: '#efa933',
  cue: '#697be8',
  returned: '#41c5b6',
  reference: '#e880ad',
};
