import brainGradeSource from '../../task-explorer/bcer-medium-brain-grade-classify/source.json?raw';
import brainGradeOperation from '../../task-explorer/bcer-medium-brain-grade-classify/operation.json?raw';
import brainGradeOutput from '../../task-explorer/bcer-medium-brain-grade-classify/output.json?raw';
import cardiacSource from '../../task-explorer/bcer-long-cardiac-full/source.json?raw';
import cardiacOperation from '../../task-explorer/bcer-long-cardiac-full/operation.json?raw';
import cardiacOutput from '../../task-explorer/bcer-long-cardiac-full/output.json?raw';
import brainFullSource from '../../task-explorer/bcer-long-brain-full/source.json?raw';
import brainFullOperation from '../../task-explorer/bcer-long-brain-full/operation.json?raw';
import brainFullOutput from '../../task-explorer/bcer-long-brain-full/output.json?raw';
import type { StoryState } from './story-timeline';

export type InterpretationBState = Extract<
  StoryState,
  { recipe: 'bcer-brain-grade-v1' | 'bcer-cardiac-full-v1' | 'bcer-brain-full-v1' }
>;
export type InterpretationBRecipe = InterpretationBState['recipe'];
type Source = {
  notice: { label: string; text: string; url: string; link_label: string };
  role: string;
  modalities: string[];
};
export type BrainGradeStage = { id: string; input: string; produces: string; check: string };
export type CardiacPhaseMode = { id: string; label: string; behavior: string };
export type BrainFullOperation = {
  stages: string[];
  conditional_branch: string;
  report_consumption: { reads: string; does_not_directly_read: string; caution: string };
};
type Output = {
  role: string;
  path: string;
  schema: Record<string, unknown>;
  prediction: null;
  score: null;
  reference: null;
};
type Pack = { source: Source; output: Output; basis: 'symbolic' };
type BrainGradePack = Pack & {
  key: 'brain-grade';
  operation: { stages: string[]; stage_details: BrainGradeStage[]; conditional_branch: string };
};
type CardiacPack = Pack & {
  key: 'cardiac-full';
  operation: { stages: string[]; conditional_branch: string; phase_modes: CardiacPhaseMode[] };
};
type BrainFullPack = Pack & { key: 'brain-full'; operation: BrainFullOperation };
export type InterpretationBPack = BrainGradePack | CardiacPack | BrainFullPack;

const brainGradeOperationData = JSON.parse(brainGradeOperation) as { stages: BrainGradeStage[] };
export const interpretationBPacks: {
  'bcer-brain-grade-v1': BrainGradePack;
  'bcer-cardiac-full-v1': CardiacPack;
  'bcer-brain-full-v1': BrainFullPack;
} = {
  'bcer-brain-grade-v1': {
    key: 'brain-grade',
    source: JSON.parse(brainGradeSource),
    operation: {
      stages: brainGradeOperationData.stages.map((s) => s.id),
      stage_details: brainGradeOperationData.stages,
      conditional_branch:
        'Segmentation may use a dependency-triggered heuristic fallback; no stage was executed.',
    },
    output: JSON.parse(brainGradeOutput),
    basis: 'symbolic',
  },
  'bcer-cardiac-full-v1': {
    key: 'cardiac-full',
    source: JSON.parse(cardiacSource),
    operation: JSON.parse(cardiacOperation),
    output: JSON.parse(cardiacOutput),
    basis: 'symbolic',
  },
  'bcer-brain-full-v1': {
    key: 'brain-full',
    source: JSON.parse(brainFullSource),
    operation: JSON.parse(brainFullOperation),
    output: JSON.parse(brainFullOutput),
    basis: 'symbolic',
  },
};
