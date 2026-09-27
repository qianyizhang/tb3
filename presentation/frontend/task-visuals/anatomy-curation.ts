import geometry from '../../task-explorer/anatomy-curation/geometry.json?raw';
import reference from '../../task-explorer/anatomy-curation/reference.json?raw';
import type { StoryState } from './story-timeline';

export type CurationState = Extract<StoryState, { recipe: 'anatomy-curation-v1' }>;
type PointObject = {
  id: string;
  points_int16le_lps_tenths_mm: string;
  centroid_lps_mm: number[];
  volume_ml: number;
};
const raw = (
  JSON.parse(geometry) as {
    scenes: Record<string, { objects: PointObject[]; spacing_mm: number[] }>;
  }
).scenes;
export const curationReference = (
  JSON.parse(reference) as {
    scenes: Record<
      string,
      {
        objects: { id: string; source: string; value: number }[];
        curation: { source_segmented_counts: number[]; status: string };
        multiset_correct: number;
        fixed_correct: number;
      }
    >;
  }
).scenes;
function decode(encoded: string) {
  const bytes = Uint8Array.from(atob(encoded), (c) => c.charCodeAt(0)),
    view = new DataView(bytes.buffer);
  return Array.from({ length: bytes.length / 6 }, (_, i) =>
    [0, 1, 2].map((j) => view.getInt16(i * 6 + j * 2, true) / 10),
  );
}
const display = (p: number[]) => [p[0], p[2], -p[1]];
export const curationGeometry = Object.fromEntries(
  Object.entries(raw).map(([key, scene]) => [
    key,
    {
      ...scene,
      objects: scene.objects.map((o) => ({
        id: o.id,
        volume_ml: o.volume_ml,
        centroid: display(o.centroid_lps_mm),
        points: decode(o.points_int16le_lps_tenths_mm).map(display),
      })),
    },
  ]),
);
export const curationKeys = {
  pair: ['sub-verse547', 'sub-verse585'],
  preservation: ['sub-verse406_split-verse261'],
  overlap: ['sub-verse406_split-verse214'],
  calibration: ['sub-verse823_dir-iso'],
  reserve: ['sub-verse642_dir-sag'],
  ambiguity: ['sub-verse581_dir-ax'],
  admission: ['sub-verse547', 'sub-verse585'],
} satisfies Record<CurationState['scene'], string[]>;
export function curationLayout(scene: CurationState['scene']) {
  const keys = curationKeys[scene];
  return keys.flatMap((key, scan) => {
    const objects = curationGeometry[key].objects.filter(
      (o) => scene !== 'preservation' || ['o705', 'o834', 'o909'].includes(o.id),
    );
    const points = objects.flatMap((o) => o.points);
    const low = [0, 1, 2].map((i) => Math.min(...points.map((p) => p[i]))),
      high = [0, 1, 2].map((i) => Math.max(...points.map((p) => p[i])));
    const span = Math.max(...high.map((v, i) => v - low[i]));
    const place = (p: number[]) =>
      p.map(
        (v, i) =>
          ((v - (low[i] + high[i]) / 2) * 330) / span +
          (i === 0 && keys.length === 2 ? (scan - 0.5) * 250 : 0),
      );
    return objects.map((o) => ({
      ...o,
      key,
      points: o.points.map(place),
      centroid: place(o.centroid),
      source: curationReference[key].objects.find((r) => r.id === o.id)!.source,
    }));
  });
}
export const curationLayouts = Object.fromEntries(
  (Object.keys(curationKeys) as CurationState['scene'][]).map((key) => [key, curationLayout(key)]),
) as Record<CurationState['scene'], ReturnType<typeof curationLayout>>;
export function curationRows(state: CurationState) {
  const rows = curationLayouts[state.scene];
  return rows.map((r, i) => ({
    ...r,
    selected:
      state.scene === 'preservation'
        ? r.id === 'o834'
        : i === Math.min(rows.length - 1, Math.floor(state.focus * rows.length)),
    source: state.reference > 0.5 ? r.source : null,
  }));
}
export const curationColor = (row: ReturnType<typeof curationRows>[number]) =>
  row.selected
    ? '#a34555'
    : !row.source
      ? '#8c9589'
      : row.source[0] === 'C'
        ? '#537d9b'
        : row.source[0] === 'T'
          ? '#b77128'
          : '#307f74';
export const curationProject = (p: number[]) => [300 + p[0], 210 - p[1]];
export const curationPaths = Object.fromEntries(
  Object.entries(curationLayouts).map(([scene, rows]) => [
    scene,
    Object.fromEntries(
      rows.map((r) => [
        r.key + r.id,
        r.points
          .map((p) => {
            const [x, y] = curationProject(p);
            return `M${x.toFixed(2)},${y.toFixed(2)}h.1`;
          })
          .join(''),
      ]),
    ),
  ]),
) as Record<CurationState['scene'], Record<string, string>>;

export function curationScanName(key: string) {
  if (key === 'sub-verse406_split-verse214') return '406 upper';
  if (key === 'sub-verse406_split-verse261') return '406 lower';
  return key.replace('sub-verse', '').split('_')[0];
}
