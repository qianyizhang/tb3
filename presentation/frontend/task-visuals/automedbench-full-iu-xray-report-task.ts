import sourceRaw from '../../task-explorer/automedbench-full-iu-xray-report-task/source.json?raw';
import fixtureRaw from '../../task-explorer/automedbench-full-iu-xray-report-task/fixture.json?raw';
import type { StoryState } from './story-timeline';
import type { StoryPlan } from '../contracts.generated';
export const source = JSON.parse(sourceRaw) as {
  actual_data_gap: string;
  runtime_discrepancy: string;
  notice: { label: string; text: string; url: string; link_label: string };
};
export const fixture = JSON.parse(fixtureRaw) as { text: string };
export const automedIuReportPack = { source };
export type AutomedIuReportState = Extract<StoryState, { recipe: 'automed-iu-xray-report-v1' }>;
export const steps = ['Study grouping', 'Text validity', 'Metric binding'] as const;
export function operationIndex(s: AutomedIuReportState) {
  return Math.min(2, Math.max(0, Math.round(s.progress * 2)));
}
export function operationFrame(p: StoryPlan, i: number) {
  if (p.recipe !== 'automed-iu-xray-report-v1') throw new Error('IU recipe mismatch');
  if (!Number.isInteger(i) || i < 0 || i > 2) throw new Error('Invalid operation index');
  const b = p.beats.find(
    (b) => b.scene === 'operation' && Math.abs(b.channels.progress[0] - Math.round(i) / 2) < 1e-6,
  );
  if (!b) throw new Error('Missing operation beat');
  return b.startFrame;
}
export function referenceVisible(s: AutomedIuReportState) {
  return s.scene === 'reference' && s.reference > 0.5;
}
