import sourceRaw from '../../task-explorer/imaging101-ultrasound-sos-tomography/source.json?raw';
import measurementRaw from '../../task-explorer/imaging101-ultrasound-sos-tomography/measurement.json?raw';
import helperRaw from '../../task-explorer/imaging101-ultrasound-sos-tomography/helper.json?raw';
import operationRaw from '../../task-explorer/imaging101-ultrasound-sos-tomography/operation.json?raw';
import outputRaw from '../../task-explorer/imaging101-ultrasound-sos-tomography/output.json?raw';
import type { StoryState } from './story-timeline';
import type { SosMethod } from './imaging-ultrasound-sos-controls';
export type ImagingUltrasoundSosState = Extract<
  StoryState,
  { recipe: 'imaging-ultrasound-sos-v1' }
>;
export const imagingUltrasoundSosPack = {
  source: JSON.parse(sourceRaw) as {
    notice: { label: string; text: string; url: string; link_label: string };
    geometry: string;
    sampling: string;
    units: string;
    visibility: string;
  },
  measurement: JSON.parse(measurementRaw) as {
    shape: number[];
    angles: number[];
    native_detector_trace: number[];
    noisy_range: number[];
    units: string;
  },
  helper: JSON.parse(helperRaw) as {
    native_clean_detector_trace: number[];
    source_center_speed: number;
    source_center_delta_slowness: number;
    target_role: string;
    tiers: Record<'L1' | 'L2' | 'L3', string>;
  },
  operation: JSON.parse(operationRaw) as {
    steps: string[];
    methods: Record<SosMethod, string>;
    formula: string;
    sign: string;
    adjoint: string;
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
