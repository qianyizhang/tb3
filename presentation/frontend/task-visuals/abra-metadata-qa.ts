import sourceRaw from '../../task-explorer/abra-metadata-qa/source.json?raw';
import fixtureRaw from '../../task-explorer/abra-metadata-qa/formatting-fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../types';
export type AbraMetadataState = Extract<StoryState, { recipe: 'abra-metadata-qa-v1' }>;
export type MetadataSource = {
  notice: { label: string; text: string; url: string; link_label: string };
  actual_data_gap: string;
  source_example: {
    study_date: string;
    study_uid: string;
    series: { modality: string; num_instances: number; series_uid: string }[];
  };
};
export const abraMetadataPack = {
  source: JSON.parse(sourceRaw) as MetadataSource,
  fixture: JSON.parse(fixtureRaw) as {
    input_modalities: string[];
    illustrative_formatted_string: string;
    incorrect_order_control: string;
  },
};
export const queryLabels = [
  'CT instance count',
  'All-series count',
  'Distinct modalities',
  'Study date',
  'First CT UID',
] as const;
export function queryIndex(progress: number) {
  return Math.max(0, Math.min(4, Math.round(progress * 4)));
}
export function metadataCounts(source: MetadataSource) {
  return {
    study: 1,
    series: source.source_example.series.length,
    total: source.source_example.series.reduce((sum, s) => sum + s.num_instances, 0),
    ct: source.source_example.series
      .filter((s) => s.modality === 'CT')
      .reduce((sum, s) => sum + s.num_instances, 0),
  };
}
export function metadataValues(source: MetadataSource) {
  const firstCT = source.source_example.series.find((s) => s.modality === 'CT');
  return [
    String(firstCT?.num_instances ?? ''),
    String(source.source_example.series.length),
    [...new Set(source.source_example.series.map((s) => s.modality))].sort().join(', '),
    source.source_example.study_date,
    firstCT?.series_uid ?? '',
  ];
}
export function metadataReferenceVisible(state: AbraMetadataState) {
  return state.scene === 'reference' && state.reference > 0.5;
}
export function queryFrame(plan: StoryPlan, index: number) {
  if (plan.recipe !== 'abra-metadata-qa-v1') throw new Error('Metadata recipe mismatch');
  const beat = plan.beats.find(
    (b) => b.scene === 'operation' && queryIndex(b.channels.progress[0]) === index,
  );
  if (!beat) throw new Error('Missing canonical query beat');
  return beat.startFrame;
}
