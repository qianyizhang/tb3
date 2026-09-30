import sourceRaw from '../../task-explorer/rexmle-ldct-iqa/source.json?raw';
import helperRaw from '../../task-explorer/rexmle-ldct-iqa/helper.json?raw';
import operationRaw from '../../task-explorer/rexmle-ldct-iqa/operation.json?raw';
import outputRaw from '../../task-explorer/rexmle-ldct-iqa/output.json?raw';
import imageUrl from '../../task-explorer/rexmle-ldct-iqa/image.png';
import type { StoryState } from './story-timeline';
export type RexLdctIqaState = Extract<StoryState, { recipe: 'rex-ldct-iqa-v1' }>;
export const rexLdctIqaPack = {
  imageUrl,
  source: JSON.parse(sourceRaw) as {
    title: string;
    image_size_px: number[];
    display_transform: string;
    notice: { label: string; text: string; url: string; link_label: string };
  },
  helper: JSON.parse(helperRaw) as {
    image_id: string;
    training_reader_score: number;
    units: string;
  },
  operation: JSON.parse(operationRaw) as {
    steps: string[];
    partitions: Record<'training' | 'inference' | 'evaluator', string[]>;
    preparation_split: string;
    sample_submission: string;
  },
  output: JSON.parse(outputRaw) as {
    columns: string[];
    image_id_rule: string;
    score_rule: string;
    overall_rule: string;
    limits: string[];
  },
};
