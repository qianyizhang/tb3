import { mapPoint, polygon } from './coordinates';
import { AnatomyAssets } from './anatomy';
import type { Annotation, ScenePoint, Primitive, VisualEntry, Stage } from './types';
export const C = {
  ink: '#284952',
  stone: '#aaa99f',
  faint: '#89a3aa',
  teal: '#328c7d',
  gold: '#c38a36',
  blue: '#548ab0',
  rose: '#bc708a',
  paper: '#e5edeb',
};
export const TAU = Math.PI * 2;
export const mix = (a: number, b: number, t: number) => a + (b - a) * t;
export const smooth = (t: number) => t * t * (3 - 2 * t);

/** Shared geometry construction. No DOM, GPU resources or application state. */
export function createGeometry(e: VisualEntry, stage: Stage, clock: number, progress: number) {
  const d = e.illustration,
    k = d.kind,
    subject = d.subject || 'generic';
  const out = stage === 2,
    work = stage === 1;
  const { ink, teal, gold, blue, rose } = C;
  const primitives: Primitive[] = [],
    labels: Annotation[] = [];
  let offset: ScenePoint = [0, 0, 0];
  let scale = 1;
  const point = (p: ScenePoint) => mapPoint(p, (v, i) => offset[i] + v * scale);
  const line = (a: ScenePoint, b: ScenePoint, color = ink, alpha = 0.65, width = 1, dash = false) =>
    primitives.push({ type: 'line', points: [point(a), point(b)], color, alpha, width, dash });
  const dot = (p: ScenePoint, r = 0.045, color = gold) =>
    primitives.push({ type: 'dot', points: [point(p)], radius: r * scale, color, alpha: 1 });
  const face = (pts: ScenePoint[], color = C.paper, alpha = 0.25) =>
    primitives.push({ type: 'face', points: polygon(pts.map(point)), color, alpha });
  const label = (p: ScenePoint, text: string, color = ink, anchor: ScenePoint | null = null) =>
    labels.push({ p: point(p), text, color, ...(anchor ? { anchor: point(anchor) } : {}) });
  const group = (p: ScenePoint, s: number, fn: () => void) => {
    const old = offset,
      oldScale = scale;
    offset = point(p);
    scale *= s;
    fn();
    offset = old;
    scale = oldScale;
  };
  const path = (pts: ScenePoint[], color = ink, alpha = 0.65, width = 1, dash = false) => {
    for (let i = 1; i < pts.length; i++) line(pts[i - 1], pts[i], color, alpha, width, dash);
  };
  const ring = (p: ScenePoint, r: number, color = ink, axis = 'y', alpha = 0.55, dash = false) => {
    const pts = Array.from({ length: 49 }, (_, i): ScenePoint => {
      const a = (i * TAU) / 48;
      return axis === 'y'
        ? [p[0] + r * Math.cos(a), p[1], p[2] + r * Math.sin(a)]
        : [p[0] + r * Math.cos(a), p[1] + r * Math.sin(a), p[2]];
    });
    path(pts, color, alpha, 1, dash);
  };
  // Every physical form uses the same smooth surface material, whether its
  // geometry comes from a public mask or from a procedural teaching model.
  const surface = (
    vertices: ScenePoint[],
    faces: number[][],
    color: string,
    normals: ScenePoint[] | null = null,
    asset: string | null = null,
  ) => {
    if (!normals) {
      const accumulated = vertices.map(() => [0, 0, 0]);
      faces.forEach(([a, b, c]) => {
        const u = vertices[b].map((v, i) => v - vertices[a][i]),
          v = vertices[c].map((v, i) => v - vertices[a][i]);
        const n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
        for (const index of [a, b, c]) n.forEach((v, i) => (accumulated[index][i] += v));
      });
      normals = accumulated.map(([x, y, z]): ScenePoint => [x, y, z]);
    }
    const points = vertices.map(point);
    faces.forEach((indices) =>
      primitives.push({
        type: 'face',
        points: polygon(indices.map((i) => points[i])),
        color: color === ink ? C.stone : color,
        alpha: 1,
        surface: true,
        normals: indices.map((i) => normals![i]),
        asset,
      }),
    );
  };
  const mesh = (center: ScenePoint, radii: ScenePoint, color = ink, warp = 0, dash = false) => {
    const pos = (u: number, v: number): ScenePoint => {
      const a = u * TAU,
        b = v * Math.PI,
        mod = 1 + Math.min(warp, 0.065) * Math.sin(3 * a + 1) * Math.sin(2 * b) * Math.sin(b) ** 2;
      return [
        center[0] + radii[0] * (Math.sin(b) * Math.cos(a)) * mod,
        center[1] + radii[1] * Math.cos(b) * mod,
        center[2] + radii[2] * (Math.sin(b) * Math.sin(a)) * mod,
      ];
    };
    if (dash) {
      // Sparse reference contours carry meaning; tessellation edges do not.
      for (const v of [0.22, 0.5, 0.78])
        path(
          Array.from({ length: 49 }, (_, i) => pos(i / 48, v)),
          color,
          0.8,
          1.4,
          true,
        );
      for (const u of [0, 0.25, 0.5, 0.75])
        path(
          Array.from({ length: 25 }, (_, i) => pos(u, i / 24)),
          color,
          0.8,
          1.4,
          true,
        );
      return;
    }
    const rows = 24,
      cols = 40;
    const vertices = [pos(0, 0)];
    for (let j = 1; j < rows; j++)
      for (let i = 0; i < cols; i++) vertices.push(pos(i / cols, j / rows));
    const bottom = vertices.push(pos(0, 1)) - 1,
      faces = [];
    const at = (j: number, i: number) => 1 + (j - 1) * cols + (i % cols);
    for (let i = 0; i < cols; i++) {
      faces.push([0, at(1, i), at(1, i + 1)]);
      for (let j = 1; j < rows - 1; j++) {
        const a = at(j, i),
          b = at(j, i + 1),
          c = at(j + 1, i + 1),
          d = at(j + 1, i);
        faces.push([a, d, c], [a, c, b]);
      }
      faces.push([at(rows - 1, i), bottom, at(rows - 1, i + 1)]);
    }
    surface(vertices, faces, color);
  };
  const cavityPoint = (u: number, v: number, phase = 1): ScenePoint => {
    const a = u * TAU,
      b = 0.55 + v * (Math.PI - 0.55);
    const radius = Math.sin(b),
      y = (1.12 * Math.cos(b)) / phase;
    return [0.77 * radius * Math.cos(a) * phase + 0.12 * y, y, 0.63 * radius * Math.sin(a) * phase];
  };
  const cavity = (color = ink, phase = 1) => {
    const rows = 30,
      cols = 48,
      vertices: ScenePoint[] = [],
      faces: number[][] = [];
    // Separate inner and outer walls, joined at the basal rim. This is an
    // authored explanatory shell; thickness is not a patient measurement.
    for (const inner of [false, true]) {
      for (let row = 0; row < rows; row++)
        for (let col = 0; col < cols; col++) {
          const p = cavityPoint(col / cols, row / rows, phase);
          vertices.push(inner ? [p[0] * 0.82, p[1] * 0.91 + 0.09, p[2] * 0.82] : p);
        }
      const offset = inner ? rows * cols + 1 : 0;
      const apex =
        vertices.push(
          inner ? [(0.12 * -1.03) / phase, -1.03 / phase, 0] : cavityPoint(0, 1, phase),
        ) - 1;
      for (let row = 0; row < rows - 1; row++)
        for (let col = 0; col < cols; col++) {
          const a = offset + row * cols + col,
            b = offset + row * cols + ((col + 1) % cols);
          const c = b + cols,
            d = a + cols;
          faces.push(
            ...(inner
              ? [
                  [a, c, b],
                  [a, d, c],
                ]
              : [
                  [a, b, c],
                  [a, c, d],
                ]),
          );
        }
      for (let col = 0; col < cols; col++) {
        const a = offset + (rows - 1) * cols + col,
          b = offset + (rows - 1) * cols + ((col + 1) % cols);
        faces.push(inner ? [a, apex, b] : [a, b, apex]);
      }
    }
    const innerOffset = rows * cols + 1;
    for (let col = 0; col < cols; col++) {
      const a = col,
        b = (col + 1) % cols,
        c = innerOffset + b,
        d = innerOffset + a;
      faces.push([a, c, b], [a, d, c]);
    }
    surface(vertices, faces, color);
  };
  const box = (p: ScenePoint, size: ScenePoint, color = blue, dash = false) => {
    const pts = Array.from({ length: 8 }, (_, i) =>
      mapPoint(p, (v, j) => v + size[j] * (((i >> j) & 1) - 0.5)),
    );
    for (let i = 0; i < 8; i++)
      for (let j = 0; j < 3; j++)
        if (!((i >> j) & 1)) line(pts[i], pts[i | (1 << j)], color, 0.65, 1, dash);
  };
  const panel = (p: ScenePoint = [0, 0, -0.12], size = [2.8, 2.35]) => {
    const first = primitives.length;
    const [x, y, z] = p,
      [w, h] = size;
    // A shallow physical plate gives image/signal data the same material
    // vocabulary as anatomy. Its content remains planar and readable.
    face(
      [
        [x - w / 2, y - h / 2, z - 0.06],
        [x + w / 2, y - h / 2, z - 0.06],
        [x + w / 2, y + h / 2, z - 0.06],
        [x - w / 2, y + h / 2, z - 0.06],
      ],
      '#d7e2de',
      1,
    );
    face(
      [
        [x - w / 2, y - h / 2, z - 0.06],
        [x + w / 2, y - h / 2, z - 0.06],
        [x + w / 2, y - h / 2, z],
        [x - w / 2, y - h / 2, z],
      ],
      '#bacfc9',
      1,
    );
    face(
      [
        [x + w / 2, y - h / 2, z - 0.06],
        [x + w / 2, y + h / 2, z - 0.06],
        [x + w / 2, y + h / 2, z],
        [x + w / 2, y - h / 2, z],
      ],
      '#c4d6cf',
      1,
    );
    face(
      [
        [x - w / 2, y - h / 2, z],
        [x + w / 2, y - h / 2, z],
        [x + w / 2, y + h / 2, z],
        [x - w / 2, y + h / 2, z],
      ],
      '#f4f7f3',
      1,
    );
    // Large information planes form a backdrop, not an occluding polygon.
    primitives.slice(first).forEach((item) => {
      if (item.type === 'face') item.backdrop = true;
    });
  };
  const imagePanel = (
    p: ScenePoint = [0, 0, 0],
    size = [2.7, 1.8],
    imageSubject = subject,
    tilt = 0,
  ) => {
    const [x, y, z] = p,
      [w, h] = size;
    const corner = (u: number, v: number) =>
      point([x + u, y + v * Math.cos(tilt), z + v * Math.sin(tilt)]);
    primitives.push({
      type: 'image',
      points: [
        corner(-w / 2, h / 2),
        corner(w / 2, h / 2),
        corner(w / 2, -h / 2),
        corner(-w / 2, -h / 2),
      ],
      subject: imageSubject,
      color: ink,
      alpha: 1,
    });
  };
  const plane = (y: number, color = blue, alpha = 0.15) => {
    face(
      [
        [-1.25, y, -0.9],
        [1.25, y, -0.9],
        [1.25, y, 0.9],
        [-1.25, y, 0.9],
      ],
      color,
      alpha,
    );
    path(
      [
        [-1.25, y, -0.9],
        [1.25, y, -0.9],
        [1.25, y, 0.9],
        [-1.25, y, 0.9],
        [-1.25, y, -0.9],
      ],
      color,
      0.65,
    );
  };
  const volume = (color = blue, n = 5) => {
    for (let i = 0; i < n; i++) {
      const y = -0.9 + (i * 1.8) / Math.max(1, n - 1);
      face(
        [
          [-1.25, y, -0.9],
          [1.25, y, -0.9],
          [1.25, y, 0.9],
          [-1.25, y, 0.9],
        ],
        '#dfe9e2',
        0.92,
      );
      line([-1.25, y, 0.91], [1.25, y, 0.91], color, 0.6, 1.5);
    }
  };
  const tube = (control: ScenePoint[], color = ink, r = 0.06, dash = false) => {
    if (dash) {
      path(control, color, 0.9, 2, true);
      return;
    }
    // Catmull-Rom interpolation makes continuous branches instead of wire cages.
    const pts: ScenePoint[] = [];
    for (let i = 0; i < control.length - 1; i++) {
      const a = control[Math.max(0, i - 1)],
        b = control[i],
        c = control[i + 1],
        d = control[Math.min(control.length - 1, i + 2)];
      for (let j = 0; j < 5; j++) {
        const t = j / 5;
        pts.push(
          mapPoint(
            b,
            (v, q) =>
              0.5 *
              (2 * v +
                (-a[q] + c[q]) * t +
                (2 * a[q] - 5 * v + 4 * c[q] - d[q]) * t * t +
                (-a[q] + 3 * v - 3 * c[q] + d[q]) * t * t * t),
          ),
        );
      }
    }
    pts.push(control.at(-1)!);
    const vertices: ScenePoint[] = [],
      normals: ScenePoint[] = [];
    const faces: number[][] = [],
      sides = 16;
    let previousU: ScenePoint | null = null;
    const tangents: ScenePoint[] = [];
    pts.forEach((p, i) => {
      const a = pts[Math.max(0, i - 1)],
        b = pts[Math.min(pts.length - 1, i + 1)],
        t = mapPoint(b, (x, j) => x - a[j]);
      const len = Math.hypot(...t) || 1;
      t.forEach((_, j) => (t[j] /= len));
      tangents.push(t);
      const reference: ScenePoint = previousU || (Math.abs(t[1]) > 0.9 ? [1, 0, 0] : [0, 1, 0]);
      const along = reference.reduce((sum, v, q) => sum + v * t[q], 0);
      const u = mapPoint(reference, (v, q) => v - along * t[q]);
      const length = Math.hypot(...u) || 1;
      u.forEach((_, q) => (u[q] /= length));
      previousU = u;
      const v = [t[1] * u[2] - t[2] * u[1], t[2] * u[0] - t[0] * u[2], t[0] * u[1] - t[1] * u[0]];
      for (let j = 0; j < sides; j++) {
        const n = mapPoint(
          u,
          (x, q) => x * Math.cos((j * TAU) / sides) + v[q] * Math.sin((j * TAU) / sides),
        );
        normals.push(n);
        vertices.push(mapPoint(p, (x, q) => x + r * (1 - (0.12 * i) / (pts.length - 1)) * n[q]));
        if (i) {
          const a = (i - 1) * sides + j,
            b = (i - 1) * sides + ((j + 1) % sides),
            c = i * sides + ((j + 1) % sides),
            d = i * sides + j;
          faces.push([a, b, c], [a, c, d]);
        }
      }
    });
    for (const [ring, sign] of [
      [0, -1],
      [pts.length - 1, 1],
    ]) {
      const center = pts[ring],
        tangent = tangents[ring];
      const radius = r * (1 - (0.12 * ring) / (pts.length - 1));
      const radial = normals.slice(ring * sides, (ring + 1) * sides);
      let previous = Array.from({ length: sides }, (_, j) => ring * sides + j);
      for (let band = 1; band <= 4; band++) {
        const angle = (band * Math.PI) / 10;
        const current = radial.map((n) => {
          const index = vertices.length;
          vertices.push(
            mapPoint(
              center,
              (v, q) => v + radius * (n[q] * Math.cos(angle) + sign * tangent[q] * Math.sin(angle)),
            ),
          );
          normals.push(
            mapPoint(n, (v, q) => v * Math.cos(angle) + sign * tangent[q] * Math.sin(angle)),
          );
          return index;
        });
        for (let j = 0; j < sides; j++) {
          const next = (j + 1) % sides;
          const triangles = [
            [previous[j], previous[next], current[next]],
            [previous[j], current[next], current[j]],
          ];
          faces.push(...triangles.map((f) => (sign < 0 ? f.reverse() : f)));
        }
        previous = current;
      }
      const tip = vertices.push(mapPoint(center, (v, q) => v + sign * radius * tangent[q])) - 1;
      normals.push(mapPoint(tangent, (v) => v * sign));
      for (let j = 0; j < sides; j++) {
        const triangle = [previous[j], previous[(j + 1) % sides], tip];
        faces.push(sign < 0 ? triangle.reverse() : triangle);
      }
    }
    surface(vertices, faces, color, normals);
  };
  const branches = (colored = false, gap = false, override: string | null = null, dash = false) => {
    const paths: ScenePoint[][] = [
      [
        [0, -1.15, 0],
        [0, -0.6, 0.08],
        [0, -0.05, 0],
        [0.06, 0.55, 0],
        [0.2, 1.12, -0.2],
      ],
      [
        [0, -0.3, 0.04],
        [-0.45, 0.03, 0.08],
        [-0.78, 0.4, 0.1],
        [-1.1, 0.8, 0.23],
      ],
      [
        [-0.45, 0.03, 0.08],
        [-0.55, 0.6, -0.3],
        [-0.9, 1.04, -0.5],
      ],
      [
        [0, -0.15, 0],
        [0.48, 0.17, -0.12],
        [0.83, 0.55, -0.1],
        [1.05, 1.05, 0.07],
      ],
      [
        [0.48, 0.17, -0.12],
        [0.88, 0.15, 0.42],
        [1.2, 0.48, 0.67],
      ],
      [
        [-0.78, 0.4, 0.1],
        [-1.15, 0.3, -0.4],
      ],
      [
        [0.83, 0.55, -0.1],
        [0.65, 0.94, -0.48],
      ],
    ];
    paths.forEach((p, i) => {
      if (gap && i === 3) {
        tube(p.slice(1), override || (colored ? teal : ink), 0.065, dash);
        return;
      }
      tube(
        p,
        override || (colored ? [teal, blue, rose, gold][i % 4] : ink),
        i === 0 ? 0.12 : 0.075,
        dash,
      );
    });
  };
  const asset = (name: string, color: string | null = null, focus: string | null = null) => {
    const parts = AnatomyAssets.get(name);
    if (!parts) return false;
    parts.forEach((part, i) =>
      surface(
        part.vertices,
        part.faces,
        focus ? (part.id === focus ? teal : ink) : color || [teal, blue, rose, gold][i % 4],
        part.normals || null,
        part.id,
      ),
    );
    return true;
  };
  const anatomy = (colored = false) => {
    if (asset(subject, colored ? null : ink)) return;
    const col = (i: number) => (colored ? [teal, blue, rose, gold][i % 4] : ink);
    if (['brain-vessels', 'vessels'].includes(subject)) {
      branches(colored);
      return;
    }
    if (subject === 'breast') {
      imagePanel();
    } else if (['tissue', 'skin'].includes(subject)) {
      for (let i = 0; i < 9; i++) {
        const x = ((i % 3) - 1) * 0.68,
          y = (Math.floor(i / 3) - 1) * 0.62;
        mesh([x, y, 0.15 * Math.sin(i)], [0.33, 0.28, 0.15], col(i), 0.14);
        mesh([x + 0.03, y, 0.2], [0.095, 0.1, 0.07], colored ? gold : rose, 0);
      }
    } else if (['wrist', 'knee'].includes(subject)) {
      for (let i = 0; i < 2; i++)
        mesh([-0.36 + i * 0.72, -0.38, 0], [0.19, 0.8, 0.24], col(i), 0.1);
      for (let i = 0; i < 4; i++)
        mesh([-0.6 + i * 0.4, 0.65, 0.06], [0.18, 0.21, 0.23], col(i), 0.08);
    } else {
      imagePanel();
    }
  };
  const organ = () => {
    if (asset(d.target || subject, teal)) return;
    // Unspecified target regions are schematic, not an invented named organ.
    mesh([0, 0, 0], [0.38, 0.45, 0.3], teal, 0.21);
  };
  const sweep = () => plane(mix(-1.05, 1.05, smooth(progress)), teal, 0.1);
  const target = (p: ScenePoint = [0.52, 0.15, 0.48], boxed = false) => {
    if (boxed) box(p, [0.65, 0.65, k === 'detect' ? 0 : 0.6], gold);
    else {
      ring(p, 0.24, gold, 'z', 1);
      dot(p, 0.05, gold);
      line([p[0] - 0.34, p[1], p[2]], [p[0] + 0.34, p[1], p[2]], gold, 0.8);
      line([p[0], p[1] - 0.34, p[2]], [p[0], p[1] + 0.34, p[2]], gold, 0.8);
    }
  };
  const documentMesh = (p: ScenePoint = [0, 0, 0], color = ink, rows = 5) =>
    group(p, 1, () => {
      panel([0, 0, -0.04], [1.24, 1.7]);
      for (let i = 0; i < rows; i++)
        line(
          [-0.43, 0.53 - i * 0.24, 0.02],
          [i % 2 ? 0.3 : 0.43, 0.53 - i * 0.24, 0.02],
          color,
          0.75,
          2,
        );
    });
  const chart = (mode: 'decay' | 'phase', color = teal) => {
    panel();
    line([-1, -0.8, 0], [1.05, -0.8, 0], ink, 0.6);
    line([-1, -0.8, 0], [-1, 0.9, 0], ink, 0.6);
    path(
      Array.from({ length: 65 }, (_, i) => {
        const x = i / 64;
        return [
          -1 + 2 * x,
          mode === 'decay' ? 0.8 - 1.5 * (1 - Math.exp(-3 * x)) : -0.6 + 1.2 * x,
          0,
        ];
      }),
      color,
      1,
      2,
    );
  };
  const field = (spectral = false, color = teal) => {
    const vertices: ScenePoint[] = [],
      faces: number[][] = [],
      cols = 20,
      rows = 15;
    for (let j = 0; j < rows; j++)
      for (let i = 0; i < cols; i++) {
        const x = (i - 9.5) / 8,
          z = (j - 7) / 7;
        vertices.push([
          x,
          0.42 * Math.sin(x * 2.5 + (work ? clock * 0.08 : 0)) * Math.cos(z * 2),
          z,
        ]);
        if (i && j) {
          const a = (j - 1) * cols + i - 1,
            b = a + 1,
            c = j * cols + i,
            d = c - 1;
          faces.push([a, b, c], [a, c, d]);
        }
      }
    const before = primitives.length;
    surface(vertices, faces, color);
    if (spectral)
      primitives.slice(before).forEach((item, i) => {
        const y = faces[i].reduce((sum, n) => sum + vertices[n][1], 0) / 3;
        item.color = y > 0.16 ? gold : y < -0.16 ? blue : teal;
      });
  };
  const signals = () => {
    panel();
    for (let j = 0; j < 5; j++)
      path(
        Array.from({ length: 75 }, (_, i) => {
          const x = (i - 37) / 29;
          return [
            x,
            Math.sin(i * 0.45 + (work ? clock * 0.35 : 0) + j) *
              Math.exp(-(((i - 35) / 22) ** 2)) *
              0.18 +
              (j - 2) * 0.32,
            j * 0.04,
          ];
        }),
        ink,
        0.8,
      );
  };
  const sampled = () => {
    panel();
    for (let j = 0; j < 17; j++) {
      if (!out && j % 3 === 1) continue;
      line([-1.15, (j - 8) * 0.13, 0], [1.15, (j - 8) * 0.13, 0], ink, 0.6);
    }
    ring([0, 0, 0], 0.36, ink, 'z');
  };

  return {
    cavity,
    cavityPoint,
    primitives,
    labels,
    line,
    dot,
    face,
    label,
    group,
    path,
    ring,
    mesh,
    box,
    panel,
    imagePanel,
    volume,
    tube,
    branches,
    asset,
    anatomy,
    organ,
    sweep,
    target,
    documentMesh,
    chart,
    field,
    signals,
    sampled,
  };
}
