import sourceRaw from '../../task-explorer/imaging101-mri-grappa/source.json?raw';
import measurementRaw from '../../task-explorer/imaging101-mri-grappa/measurement.json?raw';
import helperRaw from '../../task-explorer/imaging101-mri-grappa/helper.json?raw';
import operationRaw from '../../task-explorer/imaging101-mri-grappa/operation.json?raw';
import outputRaw from '../../task-explorer/imaging101-mri-grappa/output.json?raw';
import type { StoryState } from './story-timeline';
import type { GrappaMethod } from './imaging-grappa-controls';
export type ImagingGrappaState = Extract<StoryState, { recipe: 'imaging-grappa-v1' }>;
export const imagingGrappaPack = {
  source: JSON.parse(sourceRaw) as {
    notice: { label: string; text: string; url: string; link_label: string };
    geometry: string;
    sampling: string;
    units: string;
    visibility: string;
  },
  measurement: JSON.parse(measurementRaw) as {
    shape: number[];
    native_center_kspace: number[][];
    native_center_sensitivity: number[][];
    symbolic_rule_retained_rows: number[];
    retained_line_count: number;
    symbolic_rule: string;
  },
  helper: JSON.parse(helperRaw) as {
    native_full_target_pairs: number[][];
    target_role: string;
    tiers: Record<'L1' | 'L2' | 'L3', string>;
    acs: string;
  },
  operation: JSON.parse(operationRaw) as {
    steps: string[];
    methods: Record<GrappaMethod, string>;
    kernel: string;
  },
  output: JSON.parse(outputRaw) as {
    path: string;
    format: string;
    metric: string;
    task_metric: string;
    reference_selection: string;
    threshold: string;
    limits: string;
  },
};
