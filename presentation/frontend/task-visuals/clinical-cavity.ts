import sourceRaw from '../../task-explorer/clinical-cavity/source.json?raw';
import outputRaw from '../../task-explorer/clinical-cavity/output.json?raw';
import referenceRaw from '../../task-explorer/clinical-cavity/reference.json?raw';
import type { StoryState } from './story-timeline';
export type CavityState = Extract<StoryState, { recipe: 'clinical-cavity-v1' }>;
export type CavityKey = 'primary' | 'patient' | 'preserved';
export type OutputKey = CavityKey | 'static' | 'shift' | 'static_initialization';
export type Segment2D = [[number, number], [number, number]];
export type CavityMesh = {
  frames: number;
  vertices: number;
  points_f32le: string;
  faces_u16le: string;
  volume_ml: number[];
  sections: Segment2D[][][];
};
export type CavityPlane = {
  name: string;
  width: number;
  height: number;
  origin_mm: number[];
  dx_mm: number[];
  dy_mm: number[];
  frames: { png: string; gray_u8: string }[];
};
export type CavityCase = {
  recording: string;
  frames: number;
  native_indices: number[];
  timestamps_s: number[];
  shape_tzyx: number[];
  initial: CavityMesh;
  planes: CavityPlane[];
  bounds_mm: [number[], number[]];
  public_files: number;
};
export type CavityGrade = {
  surface_mean_mm: number;
  surface_p95_mm: number;
  ef_pct: number;
  reference_ef_pct: number;
  ef_error_pp: number;
  edv_error_pct: number;
  esv_error_pct: number;
  gates: { surface_mean: boolean; surface_p95: boolean; ef: boolean; edv: boolean; esv: boolean };
  declared_functional_class: string;
  reference_functional_class: string;
  diagnostic_class_matches: boolean;
};
export const cavityCases = (JSON.parse(sourceRaw) as { cases: Record<CavityKey, CavityCase> })
  .cases;
export const cavityOutputs = (
  JSON.parse(outputRaw) as {
    cases: Record<
      OutputKey,
      {
        mesh: CavityMesh;
        summary: { ef_pct: number; ed_frame: number; es_frame: number };
      }
    >;
  }
).cases;
export const cavityReferences = JSON.parse(referenceRaw) as Record<
  CavityKey,
  {
    mesh: CavityMesh;
    grade: CavityGrade;
  }
> & { static_initialization: { grade: CavityGrade } };
export const cavityColors = { helper: '#8398ad', output: '#18c6d4', reference: '#f4bc49' };
export const cavityNames = {
  primary: 'Primary · one model attempt',
  patient: 'Hidden reduced · executable replay',
  preserved: 'Supplementary preserved · executable replay',
};
const decoded = new WeakMap<CavityMesh, { frames: Float32Array[]; faces: Uint16Array }>();
export function decodeCavity(mesh: CavityMesh) {
  let result = decoded.get(mesh);
  if (!result) {
    // Explicit little-endian decoding also works on a big-endian JS host.
    const floats = Uint8Array.from(atob(mesh.points_f32le), (c) => c.charCodeAt(0));
    const indices = Uint8Array.from(atob(mesh.faces_u16le), (c) => c.charCodeAt(0));
    if (floats.length !== mesh.frames * mesh.vertices * 12 || indices.length % 6)
      throw Error('Invalid cavity packing');
    const fv = new DataView(floats.buffer),
      iv = new DataView(indices.buffer);
    const points = Float32Array.from({ length: floats.length / 4 }, (_, i) =>
      fv.getFloat32(i * 4, true),
    );
    const faces = Uint16Array.from({ length: indices.length / 2 }, (_, i) =>
      iv.getUint16(i * 2, true),
    );
    result = {
      frames: Array.from({ length: mesh.frames }, (_, t) =>
        points.subarray(t * mesh.vertices * 3, (t + 1) * mesh.vertices * 3),
      ),
      faces,
    };
    decoded.set(mesh, result);
  }
  return result;
}
/** One acquired frame at a time: no interpolated surfaces or invented in-between images. */
export function cavitySelection(state: CavityState) {
  const key: CavityKey =
    state.scene === 'patient' ? 'patient' : state.scene === 'preserved' ? 'preserved' : 'primary';
  const data = cavityCases[key];
  const time = Math.max(0, Math.min(1, state.phase)) * data.timestamps_s.at(-1)!;
  let frame = 0;
  data.timestamps_s.forEach((t, i) => {
    if (Math.abs(t - time) < Math.abs(data.timestamps_s[frame] - time)) frame = i;
  });
  const outputKey: OutputKey =
    state.scene === 'static' || state.scene === 'shift'
      ? state.scene
      : state.scene === 'judgment'
        ? 'static_initialization'
        : key;
  const imageFrame =
    state.scene === 'static' || state.scene === 'initial'
      ? 0
      : state.scene === 'shift'
        ? (frame - 5 + data.frames) % data.frames
        : frame;
  const refFrame = state.scene === 'shift' ? imageFrame : frame;
  const output = cavityOutputs[outputKey].mesh;
  const reference = cavityReferences[key].mesh;
  const reveal = state.reference > 0.5;
  return {
    key,
    data,
    frame,
    imageFrame,
    refFrame,
    outputKey,
    output,
    reference,
    reveal,
    grade:
      state.scene === 'judgment'
        ? cavityReferences.static_initialization.grade
        : cavityReferences[key].grade,
  };
}
export function cavityCaseLabel(state: CavityState) {
  if (state.scene === 'static' || state.scene === 'shift')
    return 'Primary source · counterfactual executable replay';
  if (state.scene === 'judgment') return 'Primary source · static-surface control';
  return cavityNames[cavitySelection(state).key];
}
export function cavityFrameLabel(state: CavityState) {
  const s = cavitySelection(state);
  if (state.scene === 'shift')
    return `Permuted ${s.frame} → original ${s.imageFrame} · initialization at 5`;
  if (state.scene === 'static') return `Control ${s.frame} · repeats acquired frame 0`;
  return `Frame ${s.imageFrame}/${s.data.frames - 1} · ${(s.data.timestamps_s[s.imageFrame] * 1000).toFixed(0)} ms · native ${s.data.native_indices[s.imageFrame]}`;
}
const sectionPaths = new WeakMap<Segment2D[], string>();
/** Join existing segment endpoints so dash cadence continues along each contour. */
export function cavitySectionPath(segments: Segment2D[]) {
  const cached = sectionPaths.get(segments);
  if (cached !== undefined) return cached;
  const key = (p: number[]) => p.map((v) => v.toFixed(3)).join(',');
  const neighbors = new Map<string, number[]>();
  segments.forEach((segment, i) =>
    segment.forEach((p) => {
      const k = key(p);
      neighbors.set(k, [...(neighbors.get(k) || []), i]);
    }),
  );
  const used = new Set<number>();
  const paths: string[] = [];
  segments.forEach((segment, i) => {
    if (used.has(i)) return;
    used.add(i);
    const chain = [segment[0], segment[1]];
    // Extend both ends; every original segment is retained once.
    for (const prepend of [false, true]) {
      let endpoint = prepend ? chain[0] : chain.at(-1)!;
      while (true) {
        const next = neighbors.get(key(endpoint))?.find((j) => !used.has(j));
        if (next === undefined) break;
        used.add(next);
        const edge = segments[next];
        endpoint = key(edge[0]) === key(endpoint) ? edge[1] : edge[0];
        if (prepend) chain.unshift(endpoint);
        else chain.push(endpoint);
      }
    }
    paths.push(chain.map((p, j) => `${j ? 'L' : 'M'}${p[0] + 0.5},${p[1] + 0.5}`).join(''));
  });
  const result = paths.join('');
  sectionPaths.set(segments, result);
  return result;
}
