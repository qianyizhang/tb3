import geometry from '../../task-explorer/mask-screen/geometry.json?raw';
import reference from '../../task-explorer/mask-screen/reference.json?raw';
import type { StoryState } from './story-timeline';

export type MaskScreenState = Extract<StoryState, { recipe: 'mask-screen-v1' }>;
export type ScreenKey = 'ribs-32' | 'ribs-74' | 'organs-32';
type ObjectPoints = { id: string; points_lps_mm: number[][]; centroid_lps_mm: number[] };
export const screenGeometry = (
  JSON.parse(geometry) as {
    scenes: Record<ScreenKey, { case_id: number; objects: ObjectPoints[] }>;
  }
).scenes;
export const screenReference = JSON.parse(reference) as {
  feature_example: {
    object_id: string;
    features: number[];
    training_cases: number[];
    nearest_templates: { label: string; squared_distance: number }[];
  };
  scenes: Record<ScreenKey, { id: string; source: string }[]>;
  coordinate_sort: {
    families_all_correct: number;
    families_tested: number;
    rows: { case_id: number; family: string; source_order: string[]; centroid_order: string[] }[];
  };
  organ_baseline: {
    correct: number;
    total: number;
    rows: {
      case_id: number;
      correct: number;
      total: number;
      all_correct: boolean;
      predictions: { source_label: string; predicted: string; correct: boolean }[];
    }[];
  };
};
export const screenDisplay = (p: number[]) => [p[0], p[2], -p[1]];
export const screenKey = (state: MaskScreenState): ScreenKey =>
  state.scene === 'context' ? 'ribs-32' : state.scene === 'admission' ? 'organs-32' : state.scene;
export function screenRows(state: MaskScreenState) {
  const key = screenKey(state),
    scene = screenGeometry[key];
  const ordered = [...scene.objects].sort((a, b) => b.centroid_lps_mm[2] - a.centroid_lps_mm[2]);
  const labels = screenReference.coordinate_sort.rows.find(
    (r) => r.case_id === scene.case_id && r.family === 'left_ribs_5_10',
  )!.source_order;
  const predictions = screenReference.organ_baseline.rows.find(
    (r) => r.case_id === 32,
  )!.predictions;
  const objects = key === 'organs-32' ? scene.objects : ordered;
  const count = Math.floor(state.prediction * objects.length + 1e-8);
  return objects.map((object, index) => {
    const source = screenReference.scenes[key].find((r) => r.id === object.id)!.source;
    const guess =
      key === 'organs-32'
        ? predictions.find((r) => r.source_label === source)!.predicted
        : labels[index];
    return {
      ...object,
      rank: index + 1,
      selected: index === Math.min(objects.length - 1, Math.floor(state.focus * objects.length)),
      predicted: index < count ? guess : null,
      source: state.reference > 0 ? source : null,
      wrong: state.reference > 0 && index < count && guess !== source,
    };
  });
}
export const screenBounds = Object.fromEntries(
  Object.entries(screenGeometry).map(([key, scene]) => {
    const points = scene.objects.flatMap((o) => o.points_lps_mm.map(screenDisplay));
    const low = [0, 1, 2].map((i) => Math.min(...points.map((p) => p[i])));
    const high = [0, 1, 2].map((i) => Math.max(...points.map((p) => p[i])));
    const span = Math.max(...high.map((v, i) => v - low[i]));
    return [key, { low, high, span }];
  }),
) as Record<ScreenKey, { low: number[]; high: number[]; span: number }>;
export function screenProject(key: ScreenKey, point: number[]) {
  const p = screenDisplay(point),
    b = screenBounds[key];
  return [
    300 + ((p[0] - (b.low[0] + b.high[0]) / 2) * 330) / b.span,
    220 - ((p[1] - (b.low[1] + b.high[1]) / 2) * 330) / b.span,
  ];
}
export const screenPaths = Object.fromEntries(
  Object.entries(screenGeometry).map(([key, scene]) => [
    key,
    Object.fromEntries(
      scene.objects.map((o) => [
        o.id,
        o.points_lps_mm
          .map((p) => {
            const [x, y] = screenProject(key as ScreenKey, p);
            return `M${x.toFixed(2)},${y.toFixed(2)}h.1`;
          })
          .join(''),
      ]),
    ),
  ]),
) as Record<ScreenKey, Record<string, string>>;
export function screenColor(row: ReturnType<typeof screenRows>[number]) {
  return row.wrong ? '#a34555' : row.selected ? '#307f74' : '#8c9589';
}
