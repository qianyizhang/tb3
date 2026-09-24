/** Pure fixture math. No renderer, clock, network, patient-frame inference or mutable state.
 * Port into task-visuals; production asset DTOs remain Python-owned/generated.
 */
export type Vec3 = readonly [number, number, number];
export interface RouteSample {
  readonly column: number;
  readonly row: number; // Raster row: positive transverse offset is UP.
  readonly distanceM: number;
  readonly center: Vec3;
  readonly worldPoint: Vec3;
  readonly lineStart: Vec3;
  readonly lineEnd: Vec3;
  readonly profile: readonly number[]; // Increasing transverse offset, NOT raster row order.
  readonly intensity: number; // Dimensionless synthetic scalar, never HU.
  readonly displayUV: readonly [number, number]; // Pixel centre; top-left origin.
}
function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value))
    throw new TypeError('Expected route object');
  return value as Record<string, unknown>;
}
function numbers(value: unknown, label: string): readonly number[] {
  if (
    !Array.isArray(value) ||
    !value.length ||
    value.some((v) => typeof v !== 'number' || !Number.isFinite(v))
  )
    throw new TypeError(`${label}: expected finite nonempty numeric array`);
  return Object.freeze([...value] as number[]);
}
function vectors(value: unknown, label: string): readonly Vec3[] {
  if (!Array.isArray(value) || value.length < 2)
    throw new TypeError(`${label}: expected at least two vectors`);
  return Object.freeze(
    value.map((v) => {
      const a = numbers(v, label);
      if (a.length !== 3) throw new TypeError(`${label}: expected exactly three components`);
      return Object.freeze([a[0], a[1], a[2]]) as Vec3;
    }),
  );
}
function offset(c: Vec3, n: Vec3, u: number): Vec3 {
  return Object.freeze([c[0] + u * n[0], c[1] + u * n[1], c[2] + u * n[2]]);
}
export function createRouteSampler(raw: unknown) {
  const r = object(raw);
  if (r.schema !== 1 || r.units !== 'm' || r.frame !== 'teaching-y-up')
    throw new TypeError('Only the declared metre-based synthetic teaching frame is supported');
  const points = vectors(r.points, 'points');
  const normals = vectors(r.normals, 'normals');
  const arc = numbers(r.arc_m, 'arc_m');
  const offsets = numbers(r.u_m, 'u_m');
  if (points.length !== normals.length || points.length !== arc.length || offsets.length < 2)
    throw new TypeError('Inconsistent route dimensions');
  if (arc[0] !== 0 || arc.some((v, i) => i > 0 && v <= arc[i - 1]))
    throw new TypeError('arc_m must start at zero and increase strictly');
  if (offsets.some((v, i) => i > 0 && v <= offsets[i - 1]))
    throw new TypeError('u_m must increase strictly');
  if (normals.some((n) => Math.abs(Math.hypot(...n) - 1) > 1e-5))
    throw new TypeError('Expected unit sampling normals');
  if (!Array.isArray(r.sample_values) || r.sample_values.length !== points.length)
    throw new TypeError('Expected one sample profile per route position');
  const profiles = Object.freeze(
    r.sample_values.map((row) => {
      const a = numbers(row, 'sample_values');
      if (a.length !== offsets.length) throw new TypeError('Profile width differs from u_m');
      return a;
    }),
  );
  const columns = points.length;
  const rows = offsets.length;
  function atColumn(column: number, transverseIndex = Math.floor(rows / 2)): RouteSample {
    if (!Number.isInteger(column) || column < 0 || column >= columns)
      throw new RangeError('Invalid output column');
    if (!Number.isInteger(transverseIndex) || transverseIndex < 0 || transverseIndex >= rows)
      throw new RangeError('Invalid transverse index');
    const center = points[column],
      normal = normals[column],
      row = rows - 1 - transverseIndex;
    return Object.freeze({
      column,
      row,
      distanceM: arc[column],
      center,
      worldPoint: offset(center, normal, offsets[transverseIndex]),
      lineStart: offset(center, normal, offsets[0]),
      lineEnd: offset(center, normal, offsets[rows - 1]),
      profile: profiles[column],
      intensity: profiles[column][transverseIndex],
      displayUV: Object.freeze([(column + 0.5) / columns, (row + 0.5) / rows]) as readonly [
        number,
        number,
      ],
    });
  }
  function atDistanceFraction(fraction: number): RouteSample {
    if (!Number.isFinite(fraction) || fraction < 0 || fraction > 1)
      throw new RangeError('Expected distance fraction in [0,1]');
    const distance = fraction * arc[columns - 1];
    let lo = 0,
      hi = columns - 1;
    while (lo < hi) {
      const mid = Math.floor((lo + hi) / 2);
      if (arc[mid] < distance) lo = mid + 1;
      else hi = mid;
    }
    const index = lo > 0 && distance - arc[lo - 1] <= arc[lo] - distance ? lo - 1 : lo;
    return atColumn(index);
  }
  return Object.freeze({ columns, rows, atColumn, atDistanceFraction });
}
