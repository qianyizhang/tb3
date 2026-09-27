import raw from '../../task-explorer/prototype-identity/geometry.json?raw';
import reference from '../../task-explorer/prototype-identity/reference.json?raw';
import vocabulary from '../../task-explorer/prototype-identity/vocabulary.json?raw';
import type { StoryState } from './story-timeline';

export type PrototypeIdentityState = Extract<StoryState, { recipe: 'prototype-identity-v1' }>;
export const prototypeObjects = (
  JSON.parse(raw) as {
    objects: { object_id: string; points_lps_mm: number[][]; centroid_lps_mm: number[] }[];
  }
).objects;
const referenceRows = (
  JSON.parse(reference) as {
    assignments: { object_id: string; label: string }[];
  }
).assignments;
export const prototypeVocabulary = JSON.parse(vocabulary) as string[];
// One proper rotation for the whole assembly: display axes = L, S, -P.
export const prototypeDisplay = (p: number[]) => [p[0], p[2], -p[1]];
export const prototypePoints = prototypeObjects.map((o) => o.points_lps_mm.map(prototypeDisplay));
const points = prototypePoints.flat();
const low = [0, 1, 2].map((axis) => Math.min(...points.map((p) => p[axis])));
const high = [0, 1, 2].map((axis) => Math.max(...points.map((p) => p[axis])));
const span = Math.max(...high.map((v, i) => v - low[i]));
export const prototypeProjection = prototypePoints.map((points) =>
  points
    .map((p) => {
      const x = 300 + ((p[0] - (low[0] + high[0]) / 2) / span) * 340;
      const y = 210 - ((p[1] - (low[1] + high[1]) / 2) / span) * 340;
      return `M${x.toFixed(2)},${y.toFixed(2)}h.1`;
    })
    .join(''),
);
export function prototypeRows(state: PrototypeIdentityState) {
  const count = Math.floor(state.reveal * prototypeObjects.length + 1e-8);
  const selected =
    state.reveal > 0
      ? Math.max(0, count - 1)
      : Math.min(prototypeObjects.length - 1, Math.floor(state.focus * prototypeObjects.length));
  return prototypeObjects.map((object, i) => ({
    objectId: object.object_id,
    selected: i === selected,
    label: i < count ? referenceRows.find((r) => r.object_id === object.object_id)!.label : null,
  }));
}
