import { AnatomyAssets } from './scene-anatomy.js';

// Task choreography over shared teaching assets; no task-specific results.
// Kept dependency-free so the complete Explorer works as a single offline file.
export const TaskSceneModels = (() => {
  const C = {
    ink: '#284952',
    stone: '#aaa99f',
    faint: '#89a3aa',
    teal: '#328c7d',
    gold: '#c38a36',
    blue: '#548ab0',
    rose: '#bc708a',
    paper: '#e5edeb',
  };
  const TAU = Math.PI * 2;
  const mix = (a, b, t) => a + (b - a) * t;
  const smooth = (t) => t * t * (3 - 2 * t);
  const recipes = {};
  const register = (kinds, family, action) =>
    kinds.split(' ').forEach((kind) => {
      recipes[kind] = { family, action };
    });
  register('segment instances nuclei', 'segmentation', 'Separate the spatial structures');
  register(
    'landmark_point nodule_outline detect box3d candidate_judgment',
    'localization',
    'Search the image space',
  );
  register(
    'anatomy_audit object_identity mask_shortcuts anatomy_curation',
    'audit',
    'Inspect the supplied objects',
  );
  register(
    'dynamic_mesh cardiac_contours cardiac_anchors cardiac_material',
    'motion',
    'Follow shape through time',
  );
  register(
    'point_correspondence register registration_diagnosis',
    'registration',
    'Find spatial correspondence',
  );
  register('longitudinal', 'longitudinal', 'Match structures across examinations');
  register(
    'route_repair route_discovery route_unfold vesselgraph vessel_source_screen prediction_screen',
    'routes',
    'Inspect the branching structure',
  );
  register('mri mri_dynamic ct ct_phantom dualct pet', 'tomography', 'Reconcile the measurements');
  register(
    'denoise superres restore3d synthesis lensless image_sequence',
    'restoration',
    'Recover image structure',
  );
  register(
    'ultrasound photoacoustic soundmap seismic conductivity',
    'waves',
    'Infer structure from signals',
  );
  register(
    'odt idt diffraction opticalvolume molecules nlos wavefront deflectometry',
    'optics',
    'Resolve the hidden structure',
  );
  register(
    'tensor t2 spectral spectral_cube temperature phase geofield',
    'fields',
    'Estimate the physical quantity',
  );
  register(
    'astronomy astro_uncertainty astro_dynamic astro_features astro_volume planet',
    'astronomy',
    'Infer structure from observations',
  );
  register(
    'classify multilabel report caption vqa quality tiles workflow viewer metadata',
    'interpretation',
    'Read the evidence',
  );
  register(
    'records etl trials risk source_provenance',
    'records',
    'Connect evidence to the deliverable',
  );
  register('segmenter_calibration', 'calibration', 'Compare boundaries under the supplied box');

  function scene(e, stage, clock, progress = 0) {
    const d = e.illustration,
      k = d.kind,
      subject = d.subject || 'generic',
      recipe = recipes[k];
    if (!recipe) throw Error('Missing 3D scene: ' + k);
    const out = stage === 2,
      work = stage === 1,
      ink = C.ink,
      teal = C.teal,
      gold = C.gold,
      blue = C.blue,
      rose = C.rose;
    const primitives = [],
      labels = [];
    let offset = [0, 0, 0],
      scale = 1;
    const point = (p) => p.map((v, i) => offset[i] + v * scale);
    const line = (a, b, color = ink, alpha = 0.65, width = 1, dash = false) =>
      primitives.push({ type: 'line', points: [point(a), point(b)], color, alpha, width, dash });
    const dot = (p, r = 0.045, color = gold) =>
      primitives.push({ type: 'dot', points: [point(p)], radius: r * scale, color, alpha: 1 });
    const face = (pts, color = C.paper, alpha = 0.25) =>
      primitives.push({ type: 'face', points: pts.map(point), color, alpha });
    const label = (p, text, color = ink, anchor = null) =>
      labels.push({ p: point(p), text, color, ...(anchor ? { anchor: point(anchor) } : {}) });
    const group = (p, s, fn) => {
      const old = offset,
        oldScale = scale;
      offset = point(p);
      scale *= s;
      fn();
      offset = old;
      scale = oldScale;
    };
    const path = (pts, color = ink, alpha = 0.65, width = 1, dash = false) => {
      for (let i = 1; i < pts.length; i++) line(pts[i - 1], pts[i], color, alpha, width, dash);
    };
    const ring = (p, r, color = ink, axis = 'y', alpha = 0.55, dash = false) => {
      const pts = Array.from({ length: 49 }, (_, i) => {
        const a = (i * TAU) / 48;
        return axis === 'y'
          ? [p[0] + r * Math.cos(a), p[1], p[2] + r * Math.sin(a)]
          : [p[0] + r * Math.cos(a), p[1] + r * Math.sin(a), p[2]];
      });
      path(pts, color, alpha, 1, dash);
    };
    // Every physical form uses the same smooth surface material, whether its
    // geometry comes from a public mask or from a procedural teaching model.
    const surface = (vertices, faces, color, normals = null, asset = null) => {
      if (!normals) {
        normals = vertices.map(() => [0, 0, 0]);
        faces.forEach(([a, b, c]) => {
          const u = vertices[b].map((v, i) => v - vertices[a][i]),
            v = vertices[c].map((v, i) => v - vertices[a][i]);
          const n = [
            u[1] * v[2] - u[2] * v[1],
            u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0],
          ];
          for (const index of [a, b, c]) n.forEach((v, i) => (normals[index][i] += v));
        });
      }
      const points = vertices.map(point);
      faces.forEach((indices) =>
        primitives.push({
          type: 'face',
          points: indices.map((i) => points[i]),
          color: color === ink ? C.stone : color,
          alpha: 1,
          surface: true,
          normals: indices.map((i) => normals[i]),
          asset,
        }),
      );
    };
    const mesh = (center, radii, color = ink, warp = 0, dash = false) => {
      const pos = (u, v) => {
        const a = u * TAU,
          b = v * Math.PI,
          mod =
            1 + Math.min(warp, 0.065) * Math.sin(3 * a + 1) * Math.sin(2 * b) * Math.sin(b) ** 2;
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
      const at = (j, i) => 1 + (j - 1) * cols + (i % cols);
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
    const box = (p, size, color = blue, dash = false) => {
      const pts = Array.from({ length: 8 }, (_, i) =>
        p.map((v, j) => v + size[j] * (((i >> j) & 1) - 0.5)),
      );
      for (let i = 0; i < 8; i++)
        for (let j = 0; j < 3; j++)
          if (!((i >> j) & 1)) line(pts[i], pts[i | (1 << j)], color, 0.65, 1, dash);
    };
    const panel = (p = [0, 0, -0.12], size = [2.8, 2.35]) => {
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
      primitives.slice(first).forEach((item) => (item.backdrop = true));
    };
    const imagePanel = (p = [0, 0, 0], size = [2.7, 1.8], imageSubject = subject, tilt = 0) => {
      const [x, y, z] = p,
        [w, h] = size;
      const corners = [
        [-w / 2, h / 2],
        [w / 2, h / 2],
        [w / 2, -h / 2],
        [-w / 2, -h / 2],
      ];
      primitives.push({
        type: 'image',
        points: corners.map(([u, v]) =>
          point([x + u, y + v * Math.cos(tilt), z + v * Math.sin(tilt)]),
        ),
        subject: imageSubject,
        color: ink,
        alpha: 1,
      });
    };
    const plane = (y, color = blue, alpha = 0.15) => {
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
    const tube = (control, color = ink, r = 0.06, dash = false) => {
      if (dash) {
        path(control, color, 0.9, 2, true);
        return;
      }
      // Catmull-Rom interpolation makes continuous branches instead of wire cages.
      const pts = [];
      for (let i = 0; i < control.length - 1; i++) {
        const a = control[Math.max(0, i - 1)],
          b = control[i],
          c = control[i + 1],
          d = control[Math.min(control.length - 1, i + 2)];
        for (let j = 0; j < 5; j++) {
          const t = j / 5;
          pts.push(
            b.map(
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
      pts.push(control.at(-1));
      const vertices = [],
        normals = [],
        faces = [],
        sides = 16;
      let previousU = null;
      const tangents = [];
      pts.forEach((p, i) => {
        const a = pts[Math.max(0, i - 1)],
          b = pts[Math.min(pts.length - 1, i + 1)],
          t = b.map((x, j) => x - a[j]);
        const len = Math.hypot(...t) || 1;
        t.forEach((_, j) => (t[j] /= len));
        tangents.push(t);
        const reference = previousU || (Math.abs(t[1]) > 0.9 ? [1, 0, 0] : [0, 1, 0]);
        const along = reference.reduce((sum, v, q) => sum + v * t[q], 0);
        const u = reference.map((v, q) => v - along * t[q]);
        const length = Math.hypot(...u) || 1;
        u.forEach((_, q) => (u[q] /= length));
        previousU = u;
        const v = [t[1] * u[2] - t[2] * u[1], t[2] * u[0] - t[0] * u[2], t[0] * u[1] - t[1] * u[0]];
        for (let j = 0; j < sides; j++) {
          const n = u.map(
            (x, q) => x * Math.cos((j * TAU) / sides) + v[q] * Math.sin((j * TAU) / sides),
          );
          normals.push(n);
          vertices.push(p.map((x, q) => x + r * (1 - (0.12 * i) / (pts.length - 1)) * n[q]));
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
        const center = vertices.push(pts[ring]) - 1;
        normals.push(tangents[ring].map((v) => v * sign));
        for (let j = 0; j < sides; j++)
          faces.push([center, ring * sides + j, ring * sides + ((j + 1) % sides)]);
      }
      surface(vertices, faces, color, normals);
    };
    const branches = (colored = false, gap = false, override = null, dash = false) => {
      const paths = [
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
          i === 0 ? 0.095 : 0.055,
          dash,
        );
      });
    };
    const asset = (name, color = null, focus = null) => {
      const parts = AnatomyAssets.get(name);
      if (!parts) return false;
      parts.forEach((part, i) =>
        surface(
          part.vertices,
          part.faces,
          focus ? (part.id === focus ? teal : ink) : color || [teal, blue, rose, gold][i % 4],
          part.normals,
          part.id,
        ),
      );
      return true;
    };
    const anatomy = (colored = false) => {
      if (asset(subject, colored ? null : ink)) return;
      const col = (i) => (colored ? [teal, blue, rose, gold][i % 4] : ink);
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
    const target = (p = [0.52, 0.15, 0.48], boxed = false) => {
      if (boxed) box(p, [0.65, 0.65, k === 'detect' ? 0 : 0.6], gold);
      else {
        ring(p, 0.24, gold, 'z', 1);
        dot(p, 0.05, gold);
        line([p[0] - 0.34, p[1], p[2]], [p[0] + 0.34, p[1], p[2]], gold, 0.8);
        line([p[0], p[1] - 0.34, p[2]], [p[0], p[1] + 0.34, p[2]], gold, 0.8);
      }
    };
    const documentMesh = (p = [0, 0, 0], color = ink, rows = 5) =>
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
    const chart = (mode = 'curve', color = teal) => {
      panel();
      line([-1, -0.8, 0], [1.05, -0.8, 0], ink, 0.6);
      line([-1, -0.8, 0], [-1, 0.9, 0], ink, 0.6);
      if (mode === 'bars')
        for (let i = 0; i < 5; i++) {
          const x = -0.78 + i * 0.38,
            h = 0.3 + ((i * 3) % 5) * 0.22;
          face(
            [
              [x - 0.09, -0.8, 0],
              [x + 0.09, -0.8, 0],
              [x + 0.09, -0.8 + h, 0],
              [x - 0.09, -0.8 + h, 0],
            ],
            color,
            0.85,
          );
        }
      else
        path(
          Array.from({ length: 65 }, (_, i) => {
            const x = i / 64;
            return [
              -1 + 2 * x,
              mode === 'decay'
                ? 0.8 - 1.5 * (1 - Math.exp(-3 * x))
                : mode === 'phase'
                  ? -0.6 + 1.2 * x
                  : Math.sin(x * 9) * 0.45 * Math.exp(-x * 0.65),
              0,
            ];
          }),
          color,
          1,
          2,
        );
    };
    const field = (spectral = false, color = teal) => {
      const vertices = [],
        faces = [],
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
    const resultCard = () => {
      documentMesh([0, 0, 0], teal, k === 'caption' ? 2 : 5);
      label(
        [0, -1.12, 0],
        k === 'vqa' ? 'Answer' : k === 'caption' ? 'Description' : 'Structured output',
        teal,
      );
    };

    switch (recipe.family) {
      case 'segmentation': {
        if (k === 'instances' || k === 'nuclei') {
          for (let i = 0; i < 7; i++) {
            const p = [
              Math.cos(i * 2.4) * (0.4 + i * 0.1),
              Math.sin(i * 2.4) * (0.4 + i * 0.1),
              Math.sin(i) * 0.17,
            ];
            mesh(p, [0.34, 0.28, 0.24], out ? [teal, blue, gold, rose][i % 4] : ink, 0.12);
            if (out) {
              if (k === 'nuclei') dot(p, 0.08, [teal, blue, gold][i % 3]);
              else label([p[0], p[1], p[2] + 0.27], String(i + 1), teal);
            }
          }
        } else if (out && d.mask_mode === 'binary') {
          if (['vessels', 'brain-vessels'].includes(subject)) branches(false, false, teal);
          else organ();
          label(
            [0, -1.25, 0],
            d.target ? d.target.replaceAll('_', ' ') + ' · binary mask' : 'One target mask',
            teal,
          );
        } else if (out && d.mask_mode === 'separate') {
          group([-0.8, 0, 0], 0.63, organ);
          mesh([0.95, 0, 0], [0.3, 0.36, 0.27], gold, 0.1);
          label([-0.8, -1.08, 0], 'Organ mask', teal);
          label([0.95, -1.08, 0], 'Lesion mask', gold);
        } else anatomy(out);
        if (work) {
          // A bounded reveal colors the actual displayed regions. The movement
          // teaches region labeling rather than scanning a decorative light beam.
          const cutoff = mix(-1.4, 1.4, smooth(progress));
          const palette = [teal, blue, rose, gold];
          const classes = new Map();
          primitives
            .filter((item) => item.surface)
            .forEach((item) => {
              const y = item.points.reduce((sum, p) => sum + p[1], 0) / item.points.length;
              if (y > cutoff) return;
              if (!classes.has(item.asset)) classes.set(item.asset, classes.size);
              const isTarget =
                !d.target ||
                item.asset === d.target ||
                (d.target === 'kidneys' && item.asset?.startsWith('kidney_'));
              if (d.mask_mode !== 'binary' || isTarget)
                item.color =
                  d.mask_mode === 'binary'
                    ? teal
                    : palette[classes.get(item.asset) % palette.length];
            });
          const selected = AnatomyAssets.get(subject)?.find((part) => part.id === d.target);
          if (selected) {
            const bounds = [0, 1, 2].map((axis) => [
              Math.min(...selected.vertices.map((vertex) => vertex[axis])),
              Math.max(...selected.vertices.map((vertex) => vertex[axis])),
            ]);
            const anchor = [
              (bounds[0][0] + bounds[0][1]) / 2,
              (bounds[1][0] + bounds[1][1]) / 2,
              bounds[2][1] + 0.08,
            ];
            ring(
              anchor,
              Math.max(bounds[0][1] - bounds[0][0], bounds[1][1] - bounds[1][0]) * 0.56,
              teal,
              'z',
              0.8,
              true,
            );
            label([0.9, 0.88, 0.3], 'Inspect target boundary', teal, anchor);
          }
          label([0, -1.35, 0], 'Assign labels along the boundaries', teal);
        }
        break;
      }
      case 'localization':
        if (k === 'box3d') {
          for (let i = 0; i < 3; i++)
            imagePanel([(i - 1) * 0.13, (i - 1) * 0.18, (i - 1) * 0.25], [2.5, 1.65]);
        } else imagePanel();
        if (work) sweep();
        if (out || k === 'candidate_judgment') target(undefined, ['detect', 'box3d'].includes(k));
        if (out)
          label(
            [0.6, 0.63, 0.55],
            k === 'nodule_outline'
              ? 'Outline'
              : k === 'candidate_judgment'
                ? 'Candidate judgment'
                : k === 'detect' || k === 'box3d'
                  ? 'Region'
                  : 'Coordinate',
            gold,
            [0.52, 0.15, 0.48],
          );
        break;
      case 'audit':
        if (k === 'anatomy_audit') {
          const focus = d.target || (subject === 'abdomen' ? 'kidney_left' : null);
          const selected = AnatomyAssets.get(subject)?.find((part) => part.id === focus);
          const witness = selected
            ? [
                (Math.min(...selected.vertices.map((point) => point[0])) +
                  Math.max(...selected.vertices.map((point) => point[0]))) /
                  2,
                (Math.min(...selected.vertices.map((point) => point[1])) +
                  Math.max(...selected.vertices.map((point) => point[1]))) /
                  2,
                Math.max(...selected.vertices.map((point) => point[2])) + 0.04,
              ]
            : [0.52, 0.15, 0.48];
          if (!asset(subject, null, focus)) anatomy(false);
          if (work) {
            ring(witness, 0.28, teal, 'z', 0.85, true);
            dot(witness, 0.05, teal);
            label([0.9, 0.95, 0.3], 'Selected supplied label', teal, witness);
          }
          if (out) {
            target(witness);
            label([0.6, 0.7, 0.5], 'Spatial witness', gold, witness);
          }
        } else if (k === 'anatomy_curation') {
          for (let i = 0; i < 5; i++)
            mesh([0, -0.9 + i * 0.43, 0], [0.46, 0.16, 0.3], i === 2 ? gold : ink, 0.12);
          if (out) group([1.2, 0, 0], 0.6, () => documentMesh([0, 0, 0], teal));
        } else {
          for (let i = 0; i < 3; i++)
            group([-1 + i, 0, 0], 0.7, () => {
              asset(['liver', 'kidney_left', 'spleen'][i], out ? [teal, blue, gold][i] : ink);
              label(
                [0, -0.95, 0],
                out ? ['Identity A', 'Identity B', 'Identity C'][i] : 'Object ' + (i + 1),
                out ? teal : ink,
              );
            });
          if (k === 'mask_shortcuts' && out)
            path(
              [
                [-1, -0.6, 0],
                [1, 0.75, 0],
              ],
              gold,
              0.8,
              1,
              true,
            );
        }
        break;
      case 'motion': {
        if (k === 'cardiac_material' && out) {
          for (const [x, phase, color] of [
            [-0.82, 'Initial', blue],
            [0.82, 'Later', teal],
          ]) {
            group([x, 0.1, 0], 0.54, () => {
              mesh(
                [0, 0, 0],
                phase === 'Initial' ? [0.8, 1.1, 0.67] : [0.7, 1.19, 0.74],
                color,
                0.06,
              );
              dot([-0.57, 0.55, 0.55], 0.075, gold);
              dot([0.4, -0.7, 0.52], 0.075, rose);
              label([-0.7, 0.73, 0.6], 'A', gold);
              label([0.5, -0.86, 0.6], 'B', rose);
            });
            label([x, -1.14, 0], phase + ' phase', color);
          }
          line([-1.13, 0.4, 0.38], [0.51, 0.43, 0.38], gold, 0.9, 1.5, true);
          line([-0.61, -0.27, 0.36], [1.03, -0.24, 0.36], rose, 0.9, 1.5, true);
          break;
        }
        const settle = out ? 1 - smooth(Math.max(0, (progress - 0.6) / 0.4)) : 1;
        const pulse = 1 - settle * 0.065 * (0.5 - 0.5 * Math.cos((clock * TAU) / 4.8));
        if (!out && d.input_form === 'masks') {
          for (let i = 0; i < 3; i++)
            group([(i - 1) * 0.9, 0, 0], 0.48, () => mesh([0, 0, 0], [0.8, 1.1, 0.65], blue));
        } else if (!out && k === 'cardiac_contours') {
          for (let i = 0; i < 7; i++)
            group([0, (i - 3) * 0.27, 0], 1, () =>
              ring([0, 0, 0], Math.sqrt(1 - ((i - 3) / 4) ** 2) * 0.75, blue),
            );
        } else {
          mesh(
            [0, 0, 0],
            [0.8 * pulse, 1.1 / pulse, 0.67 * pulse],
            out ? teal : k === 'cardiac_material' ? blue : ink,
            0.06,
          );
          if (k === 'cardiac_anchors' && out)
            mesh([0, 0, 0], [0.81 * pulse, 1.12 / pulse, 0.68 * pulse], teal, 0.06, true);
          if (k === 'cardiac_anchors') {
            ring([0, 0.8, 0], 0.5, gold);
            ring([0, -0.8, 0], 0.42, gold);
          }
        }
        if (k === 'cardiac_material') {
          dot([-0.58 * pulse, 0.55, 0.3 * pulse], 0.06, gold);
          dot([0.38 * pulse, -0.7, 0.3 * pulse], 0.06, rose);
          label([-0.68 * pulse, 0.63, 0.4], 'A', gold);
          label([0.43 * pulse, -0.83, 0.4], 'B', rose);
        }
        if (out) label([0, -1.45, 0], 'Time-varying geometry', teal);
        break;
      }
      case 'registration': {
        const t = out ? 1 : work ? smooth(progress) : 0;
        if (d.scene_variant === 'slice-to-volume') {
          // The source is one oblique section, not a second full CT. The output
          // is its placement and orientation in the patient's volume frame.
          const center = out || work ? mix(-1.4, 0.72, t) : -1.4;
          for (let i = 0; i < 4; i++)
            imagePanel(
              [0.8 + i * 0.09, (i - 1.5) * 0.24, -0.42 + i * 0.1],
              [1.75, 1.18],
              subject,
              -0.2,
            );
          box([0.95, 0, -0.12], [1.94, 1.94, 0.8], blue);
          imagePanel([center, mix(0, 0.12, t), 0.62], [1.75, 1.18], subject, mix(0, -0.46, t));
          const planeCenter = [center, mix(0, 0.12, t), 0.63];
          dot(planeCenter, 0.045, gold);
          label(
            [-1.22, -1.22, 0],
            out ? 'Pixel → patient transform' : 'One oblique section',
            gold,
            planeCenter,
          );
          label([1.04, -1.22, -0.1], 'Target CT volume', blue);
          if (out || work) line([-1.4, 0.1, 0.65], planeCenter, teal, 0.85, 1.7, true);
          break;
        }
        // Distinct image planes keep the actual matching question visible. A
        // cross-modality example uses the modality explicitly named in its input.
        const ultrasoundTarget = /ultrasound/i.test(d.input || '');
        [-0.95, 0.95].forEach((x, i) =>
          group([x, 0, 0], 0.6, () => {
            group(i ? [mix(0.3, 0, t), mix(0.2, 0, t), 0] : [0, 0, 0], 1, () => {
              imagePanel([0, 0, 0], [2.75, 1.88], i && ultrasoundTarget ? 'ultrasound' : subject);
            });
          }),
        );
        if (k !== 'register') {
          const source = [-1.25, 0.33, 0.4],
            returned = [0.95 + mix(0.18, -0.3, t), mix(0.48, 0.33, t), 0.4];
          dot(source, 0.055, gold);
          if (out || d.initial_candidate) dot(returned, 0.055, teal);
          if (out || work) line(source, returned, gold, 0.8, 1.4, true);
        }
        label([-0.95, -1.08, 0], k === 'register' ? 'Fixed image' : 'Source · fixed query', blue);
        label(
          [0.95, -1.08, 0],
          k === 'register'
            ? 'Moving image'
            : ultrasoundTarget
              ? 'Ultrasound · target'
              : 'Target · search here',
          rose,
        );
        if (out && k === 'point_correspondence')
          label([0.9, 0.85, 0.4], 'Returned point', teal, [0.65, 0.33, 0.4]);
        break;
      }
      case 'longitudinal':
        [-1, 1].forEach((side, i) =>
          group([side * 0.95, 0, 0], 0.57, () => {
            anatomy(false);
            if (out || work) {
              if (subject === 'breast' || subject === 'generic') {
                ring([0.43, 0.1, 0.55], 0.2 + i * 0.06, gold, 'z', 1);
                dot([0.43, 0.1, 0.55], 0.04, gold);
              } else mesh([0.43, 0.1, 0.55], [0.2 + i * 0.08, 0.23 + i * 0.08, 0.21], gold, 0.06);
            }
            label([0, -1.6, 0], i ? 'Later examination' : 'Earlier examination', ink);
          }),
        );
        if (out || work) {
          path(
            [
              [-0.72, 0.08, 0.34],
              [-0.2, -0.35, 0.55],
              [0.3, -0.35, 0.55],
              [1.19, 0.08, 0.34],
            ],
            teal,
            0.8,
            2,
            true,
          );
          label([0.1, -1.35, 0.5], 'Link identity before describing change', teal);
        }
        break;
      case 'routes':
        if (k === 'route_unfold' && out) group([-0.76, 0.1, 0], 0.62, () => branches(false, true));
        else
          branches(
            out && k === 'route_discovery',
            k === 'route_repair' || k === 'route_unfold',
            k === 'prediction_screen' ? blue : k === 'route_repair' ? teal : null,
            k === 'prediction_screen',
          );
        if (k === 'route_unfold')
          group(out ? [-0.76, 0.1, 0] : [0, 0, 0], out ? 0.62 : 1, () => {
            dot([0, -0.15, 0.15], 0.075, teal);
            dot([1.05, 1.05, 0.2], 0.075, teal);
          });
        if (k === 'route_repair' || k === 'route_unfold') {
          if (work) {
            const traced = smooth(progress);
            const cursor = [mix(0, 0.48, traced), mix(-0.15, 0.17, traced), 0.2];
            line([0, -0.15, 0.2], cursor, gold, 0.9, 2, true);
            dot(cursor, 0.065, gold);
            label([0.85, -0.85, 0.2], 'Trace candidate route', gold, cursor);
          }
          if (out)
            group(
              k === 'route_unfold' ? [-0.76, 0.1, 0] : [0, 0, 0],
              k === 'route_unfold' ? 0.62 : 1,
              () =>
                tube(
                  k === 'route_unfold'
                    ? [
                        [0, -0.15, 0],
                        [0.48, 0.17, -0.12],
                        [0.83, 0.55, -0.1],
                        [1.05, 1.05, 0.07],
                      ]
                    : [
                        [0, -0.15, 0],
                        [0.48, 0.17, -0.12],
                      ],
                  gold,
                  0.065,
                ),
            );
          else ring([0.22, 0.03, 0], 0.31, gold, 'z', 0.8, true);
        }
        if (out && k === 'vesselgraph') {
          [
            [0, -0.3, 0.04],
            [-0.45, 0.03, 0.08],
            [0.48, 0.17, -0.12],
            [0.83, 0.55, -0.1],
          ].forEach((p) => dot(p, 0.075, gold));
          label([0.85, -0.65, 0.2], 'Connection labels', gold);
        }
        if (k === 'prediction_screen') {
          group([0.06, 0.04, 0.12], 1, () => branches(false, false, teal));
          label([0, -1.45, 0], 'Prediction / reference comparison', teal);
        }
        if (k === 'vessel_source_screen') {
          ring([0.5, 0.3, 0.05], 0.3, gold, 'z', 0.8, true);
          label([0.85, -0.6, 0], 'Connection uncertain', gold);
        }
        if (out && k === 'route_unfold') {
          group([0.83, 0, 0], 0.63, () => {
            panel([0, 0, -0.14], [1.45, 2.4]);
            path(
              [
                [-0.3, -0.95, 0.04],
                [-0.38, -0.48, 0.04],
                [-0.26, 0.1, 0.04],
                [-0.36, 0.95, 0.04],
              ],
              teal,
              0.85,
              2,
            );
            path(
              [
                [0.3, -0.95, 0.04],
                [0.22, -0.48, 0.04],
                [0.34, 0.1, 0.04],
                [0.24, 0.95, 0.04],
              ],
              teal,
              0.85,
              2,
            );
            line([0, -0.95, 0.06], [-0.08, 0.95, 0.06], gold, 1, 2);
            for (const y of [-0.7, -0.2, 0.3, 0.8])
              line([-0.31, y, 0.05], [0.29, y, 0.05], blue, 0.5);
          });
          label([-0.8, -1.34, 0], 'Selected vessel route', gold);
          label([0.83, -1.34, 0], 'Curved planar view', teal);
        }
        if (work && k === 'route_discovery')
          dot([0, mix(-1.1, 1.1, smooth(progress)), 0.12], 0.07, gold);
        break;
      case 'tomography':
        if (k === 'mri' || k === 'mri_dynamic') {
          if (out) anatomy(false);
          else {
            sampled();
            if (work) sweep();
          }
          if (k === 'mri_dynamic') label([0, -1.4, 0], 'Sequence over time', teal);
        } else {
          if (out) {
            if (k === 'ct_phantom') {
              panel();
              mesh([0, 0, 0], [0.87, 1.12, 0.06], ink);
              mesh([-0.28, 0.02, 0.12], [0.24, 0.65, 0.04], blue);
              mesh([0.28, 0.12, 0.12], [0.2, 0.53, 0.04], teal);
              mesh([0, 0.68, 0.12], [0.28, 0.15, 0.04], C.faint);
            } else if (k === 'pet') {
              mesh([0, 0, 0], [0.8, 1, 0.6], ink, 0.06);
              mesh([0.27, 0.23, 0.45], [0.24, 0.28, 0.2], gold, 0.08);
            } else anatomy(false);
          } else {
            mesh([0, 0, 0], [0.4, 0.65, 0.4], ink, 0.08);
            for (let i = 0; i < 9; i++) {
              const a = (i * TAU) / 9 + (work ? smooth(progress) * 0.6 : 0),
                p = [1.35 * Math.cos(a), 0.18, 1.35 * Math.sin(a)];
              dot(p, 0.04, k === 'dualct' && i % 2 ? rose : teal);
              line(p, [-p[0], -0.25, -p[2]], i % 2 ? blue : teal, 0.3);
            }
            ring([0, 0.18, 0], 1.35, ink);
          }
          if (k === 'dualct' && out) {
            group([-0.72, 0, 0], 0.5, () => mesh([0, 0, 0], [0.7, 1, 0.65], blue));
            group([0.72, 0, 0], 0.5, () => mesh([0, 0, 0], [0.7, 1, 0.65], gold));
            label([-0.8, -1.3, 0], 'Material A', blue);
            label([0.8, -1.3, 0], 'Material B', gold);
          }
        }
        break;
      case 'restoration':
        anatomy(false);
        if (!out && ['denoise', 'restore3d', 'lensless'].includes(k))
          for (let i = 0; i < 110; i++)
            dot(
              [Math.sin(i * 13.7) * 1.15, Math.sin(i * 4.3) * 1.05, Math.cos(i * 7.7) * 0.85],
              0.011,
              C.faint,
            );
        if (k === 'superres') volume(out ? teal : blue, out ? 11 : 4);
        if (work) sweep();
        if (out && k === 'synthesis') group([0, 0, 0.04], 1, () => anatomy(true));
        if (k === 'image_sequence') label([0, -1.4, 0], 'Frames retain temporal order', teal);
        break;
      case 'waves':
        if (!out) {
          signals();
          if (work) ring([0, 0, 0], 0.65 + 0.3 * smooth(progress), gold, 'z');
        } else if (k === 'seismic') {
          for (let j = 0; j < 6; j++) group([0, (j - 3) * 0.35, 0], 1, () => field(false));
        } else if (['soundmap', 'conductivity'].includes(k)) {
          field(true);
          label([0, -1.25, 0], k === 'soundmap' ? 'Sound speed' : 'Conductivity', teal);
        } else anatomy(false);
        break;
      case 'optics':
        if (k === 'nlos') {
          face(
            [
              [0.2, -1, -0.6],
              [0.2, 1, -0.6],
              [0.2, 1, 0.8],
              [0.2, -1, 0.8],
            ],
            C.faint,
            0.15,
          );
          box([-0.6, -0.35, -0.25], [0.6, 0.9, 0.55], ink);
          path(
            [
              [1, 1, 1],
              [0.2, 0.35, 0.65],
              [-0.7, -0.2, -0.2],
            ],
            teal,
            0.8,
            2,
            true,
          );
          if (out) mesh([-0.6, -0.35, -0.25], [0.35, 0.5, 0.3], teal, 0.05);
        } else if (k === 'deflectometry') {
          if (out) {
            mesh([0, 0, 0], [0.34, 1, 0.78], teal, 0.015);
            label([0.9, 0, 0], 'Thickness / curvature', teal);
          } else
            for (let view = 0; view < 2; view++)
              group([view ? 0.75 : -0.75, 0, 0], 0.56, () => {
                panel();
                for (let i = 0; i < 12; i++)
                  path(
                    Array.from({ length: 30 }, (_, j) => [
                      (i - 5.5) * 0.18 + 0.15 * Math.sin(j * 0.14 + view * 0.3),
                      -1 + j / 15,
                      0,
                    ]),
                    blue,
                    0.8,
                  );
                label([0, -1.3, 0], 'Camera ' + (view + 1), blue);
              });
        } else if (k === 'wavefront') {
          if (out) field(false);
          else {
            panel();
            for (let i = 0; i < 42; i++)
              dot(
                [((i % 7) - 3) * 0.34 + Math.sin(i) * 0.04, (Math.floor(i / 7) - 2.5) * 0.34, 0],
                0.025,
                blue,
              );
          }
        } else if (k === 'molecules') {
          if (out) {
            box([0, 0, 0], [2.2, 2, 1.6], C.faint);
            for (let i = 0; i < 12; i++)
              dot(
                [Math.sin(i * 2.3), Math.cos(i * 3.6) * 0.8, Math.sin(i * 4.7) * 0.7],
                0.045,
                gold,
              );
          } else sampled();
        } else if (out) {
          if (k === 'diffraction') {
            group([-0.72, 0, 0], 0.53, () => field(false));
            group([0.72, 0, 0], 0.53, () => field(false, rose));
            label([-0.85, -0.9, 0], 'Amplitude', teal);
            label([0.85, -0.9, 0], 'Phase', rose);
          } else {
            volume(teal, 7);
            mesh([0, 0, 0], [0.6, 0.7, 0.5], teal, 0.12);
          }
        } else {
          for (let i = 0; i < 6; i++)
            group(
              [Math.cos((i * TAU) / 6) * 0.9, Math.sin((i * TAU) / 6) * 0.7, Math.sin(i) * 0.35],
              0.45,
              () => {
                ring([0, 0, 0], 0.6, blue, 'z');
                ring([0, 0, 0], 0.3, gold, 'z');
              },
            );
          if (work) ring([0, 0, 0], 1.2, teal);
        }
        break;
      case 'fields':
        if (!out) {
          if (k === 't2') chart('decay', blue);
          else if (k === 'geofield') {
            field(false);
            for (let i = 0; i < 12; i++)
              dot([Math.sin(i) * 1.2, 0.5, Math.cos(i * 2.1)], 0.035, gold);
          } else signals();
        } else if (k === 'temperature') {
          tube(
            [
              [0, -0.7, 0],
              [0, 0.9, 0],
            ],
            ink,
            0.08,
          );
          dot([0, -0.8, 0], 0.16, gold);
          line([0, -0.7, 0.1], [0, 0.45, 0.1], gold, 1, 3);
          label([0.4, 0.2, 0], 'Temperature', gold);
        } else if (k === 'tensor') {
          for (let i = 0; i < 25; i++)
            group([((i % 5) - 2) * 0.45, (Math.floor(i / 5) - 2) * 0.45, 0], 0.25, () =>
              mesh(
                [0, 0, 0],
                [
                  [0.68, 0.21, 0.25],
                  [0.21, 0.68, 0.25],
                  [0.21, 0.25, 0.68],
                ][i % 3],
                [blue, teal, gold][i % 3],
              ),
            );
        } else if (k === 'spectral_cube') {
          volume(teal, 9);
          label([0, -1.4, 0], 'λ · wavelength, not depth', teal);
        } else if (k === 'phase') chart('phase');
        else field(['spectral', 't2'].includes(k));
        break;
      case 'astronomy':
        if (!out) {
          sampled();
          if (work) signals();
        } else if (k === 'planet') {
          mesh([-0.15, 0, 0], [0.36, 0.36, 0.36], ink, 0);
          dot([1, 0.45, 0.3], 0.055, gold);
          ring([1, 0.45, 0.3], 0.17, gold, 'z');
          label([0.85, 0.85, 0.3], 'Candidate', gold);
        } else if (d.scene_variant === 'moon') {
          mesh([0, 0, 0], [0.9, 0.9, 0.9], ink, 0.025);
          for (let i = 0; i < 6; i++) {
            const r = 0.06 + (i % 3) * 0.04;
            path(
              Array.from({ length: 33 }, (_, j) => {
                const a = (j * TAU) / 32,
                  x = Math.sin(i * 2.3) * 0.53 + r * Math.cos(a),
                  y = Math.cos(i * 3.1) * 0.5 + r * Math.sin(a);
                return [x, y, Math.sqrt(0.9 ** 2 - x * x - y * y)];
              }),
              C.faint,
            );
          }
        } else if (d.scene_variant === 'galaxy') {
          mesh([0, 0, 0], [1.2, 0.24, 0.75], teal, 0.1);
          mesh([0, 0, 0], [0.3, 0.32, 0.3], gold, 0.05);
        } else if (k === 'astro_features') chart();
        else if (k === 'astro_volume') {
          volume(teal, 7);
          mesh([0, 0, 0], [0.7, 0.45, 0.7], gold, 0.08);
        } else {
          const vertices = [],
            faces = [],
            around = 64,
            cross = 16;
          for (let i = 0; i < around; i++)
            for (let j = 0; j < cross; j++) {
              const a = (i * TAU) / around,
                b = (j * TAU) / cross,
                variation = k === 'astro_dynamic' ? 0.018 * Math.sin(3 * a + clock * 0.4) : 0,
                r = 0.82 + (0.2 + variation) * Math.cos(b);
              vertices.push([r * Math.cos(a), 0.15 * Math.sin(b), r * Math.sin(a)]);
              const u = i * cross + j,
                v = ((i + 1) % around) * cross + j,
                w = ((i + 1) % around) * cross + ((j + 1) % cross),
                z = i * cross + ((j + 1) % cross);
              faces.push([u, v, w], [u, w, z]);
            }
          surface(vertices, faces, teal);
          if (k === 'astro_uncertainty') {
            ring([0, 0, 0], 1.2, rose, 'y', 0.75, true);
            label([0, -1.1, 0], 'Uncertain structure', rose);
          }
          if (k === 'astro_dynamic') label([0, -1.1, 0], 'Time-varying reconstruction', teal);
        }
        break;
      case 'interpretation':
        if (!out) {
          if (/\bpair\b/i.test(d.input || '')) {
            imagePanel([-0.88, 0, 0], [1.75, 1.22]);
            imagePanel([0.98, 0.05, -0.18], [1.75, 1.22]);
          } else imagePanel();
          if (k === 'vqa') label([1, 0.8, 0.2], 'Question', gold);
          if (k === 'tiles') volume(blue, 4);
          if (work) sweep();
        } else if (k === 'quality') {
          chart('bars');
          label([0, -1.2, 0], 'Quality estimate', teal);
        } else if (k === 'viewer') {
          anatomy(false);
          plane(0.35, teal, 0.2);
          label([0, -1.5, 0], 'Requested view', teal);
        } else if (k === 'classify') {
          documentMesh([0, 0, 0], teal, 0);
          label([0, 0.15, 0.08], 'One class label', teal);
          line([-0.35, -0.15, 0.06], [0.35, -0.15, 0.06], teal, 0.8, 2);
        } else if (k === 'multilabel') {
          documentMesh([0, 0, 0], teal, 0);
          ['Finding A', 'Finding B', 'Finding C'].forEach((name, i) => {
            const y = 0.5 - i * 0.5;
            dot([-0.46, y, 0.05], 0.035, i !== 1 ? teal : C.faint);
            label([0, y, 0.08], name, ink);
          });
        } else if (k === 'workflow') {
          group([-0.72, 0, 0], 0.6, () => anatomy(true));
          group([0.9, 0, 0], 0.55, () => documentMesh([0, 0, 0], teal));
        } else if (k === 'tiles') {
          for (let i = 0; i < 9; i++)
            group([((i % 3) - 1) * 0.75, (Math.floor(i / 3) - 1) * 0.7, 0], 0.22, () => {
              panel();
              mesh([0, 0, 0], [0.7, 0.6, 0.12], i % 4 === 0 ? gold : teal, 0.08);
            });
        } else resultCard();
        break;
      case 'records':
        if (k === 'risk') {
          panel();
          if (out) {
            line([-1, 0, 0], [1, 0, 0], C.faint, 1, 5);
            dot([0.24, 0, 0], 0.08, teal);
            label([-1, -0.3, 0], '0', ink);
            label([1, -0.3, 0], '1', ink);
            label([0, 0.55, 0], 'One probability per row', teal);
            label([0, -0.7, 0], 'Illustrative marker', C.faint);
          } else {
            for (let i = 0; i < 5; i++) {
              const x = -1 + i * 0.4;
              dot([x, 0.2 * Math.sin(i), 0], 0.05, blue);
              if (i) line([x - 0.4, 0.2 * Math.sin(i - 1), 0], [x, 0.2 * Math.sin(i), 0], blue);
            }
            line([0.95, -0.6, 0], [0.95, 0.8, 0], rose, 0.8, 1, true);
            label([0.95, -0.9, 0], 'Cutoff', rose);
          }
        } else if (k === 'etl') {
          for (let i = 0; i < 3; i++)
            group([out ? 0 : (i - 1) * 0.8, out ? 0 : Math.sin(i) * 0.3, (i - 1) * 0.4], 0.7, () =>
              documentMesh([0, 0, 0], out ? teal : ink, 4),
            );
        } else if (k === 'trials') {
          group([-0.8, 0, 0], 0.72, () => documentMesh([0, 0, 0], blue));
          group([0.8, 0, 0], 0.72, () => documentMesh([0, 0, 0], out ? teal : ink));
          path(
            [
              [-0.3, 0, 0.1],
              [0.3, 0, 0.1],
            ],
            out ? teal : gold,
            0.9,
            2,
            true,
          );
          label([-0.8, -1, 0], 'Patient', blue);
          label([0.8, -1, 0], out ? 'Trial IDs' : 'Criteria', out ? teal : ink);
        } else {
          documentMesh([0, 0, 0], out ? teal : ink, 5);
          if (out && k === 'records') {
            [0.3, -0.18].forEach((y) => box([0, y, 0.05], [1.07, 0.2, 0.04], gold));
          }
          if (k === 'source_provenance') {
            group([-0.95, 0, -0.25], 0.55, () => documentMesh());
            path(
              [
                [-0.6, 0.3, 0],
                [0.3, 0.7, 0.1],
              ],
              gold,
              0.8,
              1,
              true,
            );
          }
        }
        break;
      case 'calibration':
        if (!out) {
          anatomy(false);
          box([0.1, 0.05, 0.4], [1.2, 1, 0.1], gold, true);
        } else {
          mesh([0, 0, 0], [0.83, 0.68, 0.55], teal, 0.08);
          for (let i = 0; i < 6; i++)
            ring(
              [0, (i - 2.5) * 0.2, 0],
              Math.sqrt(1 - ((i - 2.5) / 4) ** 2) * 0.88,
              blue,
              'y',
              0.8,
              true,
            );
          label([-0.9, -1, 0], 'Reference · dashed', blue);
          label([0.85, -1, 0], 'Tool · solid', teal);
        }
        break;
    }
    // Paused action stages need an inspectable cue, including families whose
    // output is a static comparison. These marks indicate the operation only;
    // they do not depict a reference, prediction or adjudicated result.
    if (work) {
      switch (k) {
        case 'object_identity':
        case 'mask_shortcuts':
          ring([0, 0, 0.65], 0.42, gold, 'z', 0.85, true);
          label(
            [0.75, 0.75, 0.65],
            k === 'mask_shortcuts' ? 'Check spatial cue' : 'Inspect one object',
            gold,
            [0, 0, 0.65],
          );
          break;
        case 'anatomy_curation':
          ring([0, 0, 0.5], 0.48, gold, 'z', 0.85, true);
          label([0.8, 0.65, 0.5], 'Review candidate', gold, [0, 0, 0.5]);
          break;
        case 'cardiac_contours':
          ring([0, 0, 0.35], 0.7, teal, 'z', 0.9, true);
          label([0.8, 0.8, 0.35], 'Fit between contours', teal, [0, 0, 0.35]);
          break;
        case 'dynamic_mesh':
          if (d.input_form === 'masks') {
            line([-0.9, 0, 0.5], [0, 0, 0.5], teal, 0.9, 2, true);
            label([0.8, 0.8, 0.5], 'Connect phase shapes', teal, [0, 0, 0.5]);
          }
          break;
        case 'vesselgraph':
          dot([0, -0.3, 0.28], 0.06, gold);
          dot([0.48, 0.17, 0.28], 0.06, gold);
          line([0, -0.3, 0.28], [0.48, 0.17, 0.28], gold, 0.9, 2, true);
          label([0.9, -0.7, 0.3], 'Check connectivity', gold, [0.48, 0.17, 0.28]);
          break;
        case 'vessel_source_screen':
          line([0.2, 0.03, 0.3], [0.7, 0.4, 0.3], gold, 0.9, 2, true);
          label([0.9, -0.65, 0.3], 'Inspect source route', gold, [0.5, 0.25, 0.3]);
          break;
        case 'prediction_screen':
          ring([0.28, 0.08, 0.45], 0.28, gold, 'z', 0.8, true);
          label([0.9, -0.7, 0.45], 'Compare structures', gold, [0.28, 0.08, 0.45]);
          break;
        case 'nlos':
          ring([0.2, 0.35, 0.7], 0.22, gold, 'z', 0.85, true);
          label([0.8, -0.8, 0.7], 'Trace wall return', gold, [0.2, 0.35, 0.7]);
          break;
        case 'deflectometry':
          line([-0.55, 0.1, 0.45], [0.55, 0.1, 0.45], gold, 0.9, 2, true);
          label([0.8, -0.9, 0.45], 'Compare views', gold, [0, 0.1, 0.45]);
          break;
        case 'wavefront':
          ring([0, 0, 0.22], 0.48, gold, 'z', 0.85, true);
          label([0.85, -0.8, 0.22], 'Fit wavefront', gold, [0, 0, 0.22]);
          break;
        case 'molecules':
          box([0, 0, 0.3], [0.9, 0.9, 0.6], gold, true);
          label([0.85, -0.85, 0.3], 'Localize emitters', gold, [0, 0, 0.3]);
          break;
        case 't2':
          dot([0.35, 0.2, 0.3], 0.06, gold);
          label([0.8, 0.7, 0.3], 'Fit decay', gold, [0.35, 0.2, 0.3]);
          break;
      }
    }
    return { primitives, labels };
  }

  function legend(e) {
    const d = e.illustration,
      k = d.kind;
    let keys = [
      [C.stone, 'Structure / input'],
      [C.teal, 'Derived structure'],
      [C.gold, 'Focus / correspondence'],
    ];
    if (k === 'anatomy_audit')
      keys = [
        [C.stone, 'Anatomical context'],
        [C.teal, 'Illustrative supplied mask'],
        [C.gold, 'Spatial witness'],
      ];
    if (['segment', 'instances', 'nuclei', 'object_identity'].includes(k))
      keys =
        d.mask_mode === 'separate'
          ? [
              [C.stone, 'Input'],
              [C.teal, 'Organ'],
              [C.gold, 'Lesion'],
            ]
          : [
              [C.stone, 'Input'],
              [C.teal, 'Spatial class A'],
              [C.blue, 'Class B'],
              [C.rose, 'Class C'],
              [C.gold, 'Class D / focus'],
            ];
    if (['point_correspondence', 'register', 'registration_diagnosis'].includes(k))
      keys = [
        [C.blue, 'Source'],
        [C.rose, 'Target'],
        [C.gold, 'Query'],
        [C.teal, 'Returned point'],
      ];
    if (k === 'register' && d.scene_variant === 'slice-to-volume')
      keys = [
        [C.gold, 'Oblique section'],
        [C.blue, 'Target CT volume'],
        [C.teal, 'Placement path · dashed', true],
      ];
    if (k === 'cardiac_material')
      keys = [
        [C.blue, 'Initial phase geometry'],
        [C.teal, 'Later phase geometry'],
        [C.gold, 'Material point A · dashed track', true],
        [C.rose, 'Material point B · dashed track', true],
      ];
    if (k === 'cardiac_anchors')
      keys = [
        [C.gold, 'Supplied anchors · solid'],
        [C.teal, 'Recovered motion · dashed', true],
      ];
    if (k === 'cardiac_contours')
      keys = [
        [C.blue, 'Supplied contours'],
        [C.teal, 'Recovered surface'],
      ];
    if (k === 'prediction_screen')
      keys = [
        [C.blue, 'Reference · dashed', true],
        [C.teal, 'Prediction · solid'],
      ];
    if (k === 'diffraction')
      keys = [
        [C.ink, 'Input measurements'],
        [C.teal, 'Amplitude'],
        [C.rose, 'Phase'],
      ];
    if (['spectral', 't2', 'soundmap', 'conductivity'].includes(k))
      keys = [
        [C.ink, 'Input'],
        [C.blue, 'Lower field value'],
        [C.teal, 'Mid field value'],
        [C.gold, 'Higher field value'],
      ];
    if (k === 'tensor')
      keys = [
        [C.ink, 'Input'],
        [C.blue, 'Axis A'],
        [C.teal, 'Axis B'],
        [C.gold, 'Axis C'],
      ];
    if (d.mask_mode === 'binary')
      keys = [
        [C.stone, 'Input'],
        [C.teal, 'Single target mask'],
      ];
    if (k === 'segmenter_calibration')
      keys = [
        [C.gold, 'Supplied box · dashed', true],
        [C.blue, 'Reference · dashed', true],
        [C.teal, 'Tool · solid'],
      ];
    return keys;
  }

  return {
    build: scene,
    animated: (e, stage) => {
      const d = e.illustration,
        family = recipes[d.kind]?.family;
      if (family === 'motion')
        return d.kind === 'cardiac_material'
          ? stage < 2
          : stage === 2 || (d.input_form !== 'masks' && d.kind !== 'cardiac_contours');
      if (d.kind === 'astro_dynamic' && stage === 2) return true;
      return (
        stage === 1 &&
        [
          'segmentation',
          'localization',
          'registration',
          'routes',
          'tomography',
          'restoration',
          'waves',
          'optics',
          'fields',
          'astronomy',
          'interpretation',
        ].includes(family)
      );
    },
    usesAnatomy: (e) =>
      recipes[e.illustration.kind]?.family !== 'motion' &&
      (AnatomyAssets.has(e.illustration.subject) ||
        AnatomyAssets.has(e.illustration.target) ||
        ['object_identity', 'mask_shortcuts'].includes(e.illustration.kind)),
    legend,
    supports: (kind) => Object.hasOwn(recipes, kind),
    action: (kind) => recipes[kind].action,
  };
})();
