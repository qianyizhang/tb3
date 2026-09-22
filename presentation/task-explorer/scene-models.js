// Original, procedural 3D teaching scenes. No patient geometry or scored results.
// Kept dependency-free so the complete Explorer works as a single offline file.
const TaskSceneModels = (() => {
  const C = {
    ink: '#284952',
    faint: '#89a3aa',
    teal: '#299786',
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

  function scene(e, stage, clock) {
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
    const label = (p, text, color = ink) => labels.push({ p: point(p), text, color });
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
    const mesh = (center, radii, color = ink, warp = 0, alpha = 0.5, power = 1, dash = false) => {
      const pos = (u, v) => {
        const a = u * TAU,
          b = v * Math.PI,
          mod = 1 + warp * Math.sin(3 * a + 1) * Math.sin(4 * b) * Math.sin(b);
        const q = (n) => Math.sign(n) * Math.abs(n) ** power;
        return [
          center[0] + radii[0] * q(Math.sin(b) * Math.cos(a)) * mod,
          center[1] + radii[1] * q(Math.cos(b)) * mod,
          center[2] + radii[2] * q(Math.sin(b) * Math.sin(a)) * mod,
        ];
      };
      const rows = power === 1 ? 10 : 6,
        cols = power === 1 ? 16 : 10;
      const vertices = Array.from({ length: rows + 1 }, (_, j) =>
        Array.from({ length: cols + 1 }, (_, i) => pos(i / cols, j / rows)),
      );
      for (let j = 0; j < rows; j++)
        for (let i = 0; i < cols; i++) {
          const a = vertices[j][i],
            b = vertices[j][i + 1],
            c = vertices[j + 1][i + 1],
            f = vertices[j + 1][i];
          face([a, b, c, f], color, 0.025);
          line(a, b, color, alpha, 1, dash);
          line(a, f, color, alpha, 1, dash);
          if ((i + j) % 3 === 0) line(a, c, color, alpha * 0.35, 0.65, dash);
        }
    };
    const box = (p, size, color = blue, dash = false) => {
      const pts = Array.from({ length: 8 }, (_, i) =>
        p.map((v, j) => v + size[j] * (((i >> j) & 1) - 0.5)),
      );
      for (let i = 0; i < 8; i++)
        for (let j = 0; j < 3; j++)
          if (!((i >> j) & 1)) line(pts[i], pts[i | (1 << j)], color, 0.65, 1, dash);
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
      for (let i = -4; i <= 4; i++) line([i * 0.25, y, -0.9], [i * 0.25, y, 0.9], color, 0.15);
    };
    const volume = (color = blue, n = 5) => {
      box([0, 0, 0], [2.5, 2.15, 1.8], color);
      for (let i = 0; i < n; i++) plane(-0.9 + (i * 1.8) / Math.max(1, n - 1), color, 0.07);
    };
    const tube = (pts, color = ink, r = 0.06, alpha = 0.75, dash = false) => {
      // Cross sections are perpendicular to the tangent; longitudinal ribs join them.
      const rings = pts.map((p, i) => {
        const a = pts[Math.max(0, i - 1)],
          b = pts[Math.min(pts.length - 1, i + 1)],
          t = b.map((x, j) => x - a[j]);
        const len = Math.hypot(...t) || 1;
        t.forEach((_, j) => (t[j] /= len));
        const ref = Math.abs(t[1]) > 0.9 ? [1, 0, 0] : [0, 1, 0];
        const u = [
          t[1] * ref[2] - t[2] * ref[1],
          t[2] * ref[0] - t[0] * ref[2],
          t[0] * ref[1] - t[1] * ref[0],
        ];
        const ul = Math.hypot(...u);
        u.forEach((_, j) => (u[j] /= ul));
        const v = [t[1] * u[2] - t[2] * u[1], t[2] * u[0] - t[0] * u[2], t[0] * u[1] - t[1] * u[0]];
        return Array.from({ length: 8 }, (_, j) =>
          p.map(
            (x, q) => x + r * (u[q] * Math.cos((j * TAU) / 8) + v[q] * Math.sin((j * TAU) / 8)),
          ),
        );
      });
      rings.forEach((rs, i) =>
        rs.forEach((p, j) => {
          line(p, rs[(j + 1) % 8], color, alpha * 0.55, 0.7, dash);
          if (i) {
            line(p, rings[i - 1][j], color, alpha, 1, dash);
            face([p, rs[(j + 1) % 8], rings[i - 1][(j + 1) % 8], rings[i - 1][j]], color, 0.06);
          }
        }),
      );
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
          tube(p.slice(1), override || (colored ? teal : ink), 0.065, 0.75, dash);
          return;
        }
        tube(
          p,
          override || (colored ? [teal, blue, rose, gold][i % 4] : ink),
          i === 0 ? 0.095 : 0.055,
          0.75,
          dash,
        );
      });
    };
    const anatomy = (colored = false) => {
      const col = (i) => (colored ? [teal, blue, rose, gold][i % 4] : ink);
      if (['brain-vessels', 'aorta', 'vessels'].includes(subject)) {
        branches(colored);
        return;
      }
      if (subject === 'brain') {
        mesh([-0.42, 0, 0], [0.52, 1.08, 0.76], col(0), 0.08);
        mesh([0.42, 0, 0], [0.52, 1.08, 0.76], col(1), 0.08);
        for (let j = 0; j < 5; j++)
          path(
            Array.from({ length: 30 }, (_, i) => {
              const a = (i * Math.PI) / 29;
              return [
                0.9 * Math.cos(a),
                -0.7 + j * 0.34 + 0.07 * Math.sin(a * 7),
                0.62 * Math.sin(a),
              ];
            }),
            col(0),
            0.5,
          );
      } else if (['chest', 'chest-ct', 'airways'].includes(subject)) {
        mesh([-0.55, 0, 0], [0.46, 1.12, 0.56], col(0), 0.045);
        mesh([0.55, 0, 0], [0.46, 1.12, 0.56], col(1), 0.045);
        tube(
          [
            [0, 1.35, 0],
            [0, 0.62, 0],
            [-0.42, 0.12, 0.12],
          ],
          subject === 'airways' && colored ? gold : ink,
          0.06,
        );
        tube(
          [
            [0, 0.62, 0],
            [0.42, 0.12, 0.12],
          ],
          subject === 'airways' && colored ? gold : ink,
          0.06,
        );
        if (subject === 'airways') group([0, 0, 0.15], 0.55, () => branches(colored));
      } else if (subject === 'heart' || subject === 'ultrasound') {
        mesh([-0.18, 0, 0], [0.71, 1.05, 0.59], col(0), 0.12);
        mesh([0.43, 0.23, -0.12], [0.4, 0.76, 0.4], col(1), 0.06);
        tube(
          [
            [-0.17, 0.85, 0],
            [-0.3, 1.25, 0],
            [0.12, 1.35, -0.1],
            [0.3, 1, -0.12],
          ],
          col(0),
          0.11,
        );
      } else if (subject === 'teeth') {
        for (let i = 0; i < 12; i++) {
          const a = 0.16 + (i * (Math.PI - 0.32)) / 11,
            x = 1.25 * Math.cos(a),
            z = 0.85 * Math.sin(a);
          mesh([x, 0.2, z], [0.19, 0.23, 0.19], col(i), 0.04, 0.6, 0.55);
          tube(
            [
              [x - 0.065, 0.13, z],
              [x - 0.07, -0.14, z - 0.03],
              [x - 0.1, -0.4, z - 0.05],
            ],
            col(i),
            0.035,
          );
          tube(
            [
              [x + 0.065, 0.13, z],
              [x + 0.07, -0.14, z - 0.03],
              [x + 0.1, -0.4, z - 0.05],
            ],
            col(i),
            0.035,
          );
        }
        path(
          Array.from({ length: 45 }, (_, i) => [
            1.45 * Math.cos((i * Math.PI) / 44),
            -0.63,
            Math.sin((i * Math.PI) / 44),
          ]),
          C.faint,
          0.5,
        );
      } else if (subject === 'abdomen') {
        mesh([-0.42, 0.48, 0], [0.86, 0.48, 0.53], col(0), 0.14);
        mesh([0.68, 0.38, -0.12], [0.27, 0.58, 0.32], col(1), 0.12);
        mesh([-0.61, -0.49, 0.1], [0.25, 0.43, 0.3], col(2), 0.16);
        mesh([0.6, -0.51, 0.12], [0.25, 0.43, 0.3], col(3), 0.16);
        tube(
          [
            [0, 0.9, -0.3],
            [0, 0.25, -0.3],
            [0, -0.9, -0.3],
          ],
          colored ? gold : ink,
          0.06,
        );
      } else if (subject === 'prostate') {
        mesh([0, 0, 0], [0.92, 0.73, 0.66], col(0), 0.055);
        mesh([0, 0, 0.22], [0.48, 0.49, 0.35], col(1), 0.035);
      } else if (subject === 'breast') {
        mesh([-0.64, 0, 0], [0.56, 0.65, 0.75], col(0), 0.035);
        mesh([0.64, 0, 0], [0.56, 0.65, 0.75], col(1), 0.035);
      } else if (['tissue', 'skin'].includes(subject)) {
        for (let i = 0; i < 9; i++) {
          const x = ((i % 3) - 1) * 0.68,
            y = (Math.floor(i / 3) - 1) * 0.62;
          mesh([x, y, 0.15 * Math.sin(i)], [0.33, 0.28, 0.15], col(i), 0.14, 0.45);
          mesh([x + 0.03, y, 0.2], [0.095, 0.1, 0.07], colored ? gold : rose, 0, 0.8);
        }
      } else if (['wrist', 'knee'].includes(subject)) {
        for (let i = 0; i < 2; i++)
          mesh([-0.36 + i * 0.72, -0.38, 0], [0.19, 0.8, 0.24], col(i), 0.1);
        for (let i = 0; i < 4; i++)
          mesh([-0.6 + i * 0.4, 0.65, 0.06], [0.18, 0.21, 0.23], col(i), 0.08);
      } else {
        volume(ink, 4);
        mesh([-0.35, 0.15, 0], [0.45, 0.63, 0.45], col(0), 0.12);
        mesh([0.5, -0.34, 0.1], [0.28, 0.36, 0.34], col(1), 0.08);
      }
    };
    const organ = () => {
      if (d.target === 'kidneys') {
        mesh([-0.55, 0, 0], [0.32, 0.65, 0.36], teal, 0.16);
        mesh([0.55, 0, 0], [0.32, 0.65, 0.36], teal, 0.16);
      } else if (d.target === 'pancreas') mesh([0, 0, 0], [1.12, 0.25, 0.32], teal, 0.17);
      else if (d.target === 'liver') mesh([0, 0, 0], [1.05, 0.66, 0.62], teal, 0.17);
      else if (d.target === 'spleen') mesh([0, 0, 0], [0.39, 0.91, 0.48], teal, 0.13);
      else if (d.target === 'lesion') mesh([0, 0, 0], [0.38, 0.45, 0.3], teal, 0.21);
      else mesh([0, 0, 0], [0.72, 0.87, 0.61], teal, 0.12);
    };
    const sweep = () => plane(Math.sin(clock * 0.8) * 1.05, teal, 0.16);
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
        face(
          [
            [-0.62, -0.85, 0],
            [0.62, -0.85, 0],
            [0.62, 0.85, 0],
            [-0.62, 0.85, 0],
          ],
          C.paper,
          0.8,
        );
        box([0, 0, -0.025], [1.24, 1.7, 0.05], color);
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
      line([-1, -0.8, 0], [1.05, -0.8, 0], ink, 0.6);
      line([-1, -0.8, 0], [-1, 0.9, 0], ink, 0.6);
      if (mode === 'bars')
        for (let i = 0; i < 5; i++) {
          const x = -0.78 + i * 0.38,
            h = 0.3 + ((i * 3) % 5) * 0.22;
          box([x, -0.8 + h / 2, 0], [0.18, h, 0.17], color);
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
    const field = (spectral = false) => {
      for (let j = 0; j < 15; j++)
        path(
          Array.from({ length: 20 }, (_, i) => {
            const x = (i - 9.5) / 8,
              z = (j - 7) / 7;
            return [x, 0.42 * Math.sin(x * 2.5 + clock * 0.15) * Math.cos(z * 2), z];
          }),
          spectral ? [blue, teal, gold, rose][j % 4] : teal,
          0.7,
        );
      for (let i = 0; i < 20; i++)
        path(
          Array.from({ length: 15 }, (_, j) => {
            const x = (i - 9.5) / 8,
              z = (j - 7) / 7;
            return [x, 0.42 * Math.sin(x * 2.5 + clock * 0.15) * Math.cos(z * 2), z];
          }),
          ink,
          0.25,
        );
    };
    const signals = () => {
      for (let j = 0; j < 5; j++)
        path(
          Array.from({ length: 75 }, (_, i) => {
            const x = (i - 37) / 29;
            return [
              x,
              Math.sin(i * 0.45 + clock * 0.6 + j) * Math.exp(-(((i - 35) / 22) ** 2)) * 0.18 +
                (j - 2) * 0.32,
              j * 0.04,
            ];
          }),
          [blue, teal, rose][j % 3],
          0.8,
        );
    };
    const sampled = () => {
      for (let j = 0; j < 17; j++) {
        if (!out && j % 3 === 1) continue;
        line([-1.15, (j - 8) * 0.13, 0], [1.15, (j - 8) * 0.13, 0], j % 3 ? blue : teal, 0.6);
      }
      ring([0, 0, 0], 0.36, gold, 'z');
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
          if (['aorta', 'vessels', 'brain-vessels'].includes(subject)) branches(false, false, teal);
          else organ();
          label([0, -1.25, 0], 'One target mask', teal);
        } else if (out && d.mask_mode === 'separate') {
          organ();
          mesh([0.6, 0.1, 0.5], [0.23, 0.27, 0.21], gold, 0.1);
          label([-0.85, -1, 0], 'Organ', teal);
          label([0.7, -0.6, 0.5], 'Lesion', gold);
        } else anatomy(out);
        if (work) sweep();
        break;
      }
      case 'localization':
        anatomy(false);
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
          );
        break;
      case 'audit':
        if (k === 'anatomy_audit') {
          anatomy(true);
          if (out) {
            target();
            label([0.6, 0.7, 0.5], 'Spatial witness', gold);
          }
        } else if (k === 'anatomy_curation') {
          for (let i = 0; i < 5; i++)
            mesh([0, -0.9 + i * 0.43, 0], [0.46, 0.16, 0.3], i === 2 ? gold : ink, 0.12);
          if (out) group([1.2, 0, 0], 0.6, () => documentMesh([0, 0, 0], teal));
        } else {
          for (let i = 0; i < 3; i++)
            group([-1 + i, 0, 0], 0.7, () => {
              mesh(
                [0, i * 0.15, 0],
                [0.3 + i * 0.09, 0.45 + i * 0.08, 0.35],
                out ? [teal, blue, gold][i] : ink,
                0.08,
              );
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
        const pulse = 1 - 0.16 * (0.5 + 0.5 * Math.sin(clock * 2.1));
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
            0.5,
            1,
            k === 'cardiac_anchors' && out,
          );
          if (k === 'cardiac_material' && out)
            mesh([0, 0, 0], [0.84 * pulse, 1.13 / pulse, 0.69 * pulse], blue, 0, 0.25, 1, true);
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
        const t = out ? 1 : work ? smooth((Math.sin(clock * 0.7) + 1) / 2) : 0;
        mesh([0, 0, 0], [0.79, 1, 0.65], blue, 0.09, 0.45);
        mesh([mix(0.63, 0, t), mix(0.3, 0, t), mix(0.3, 0, t)], [0.79, 1, 0.65], rose, 0.09, 0.45);
        if (k !== 'register') {
          dot([-0.5, 0.55, 0.55], 0.06, gold);
          if (out || d.initial_candidate)
            dot([mix(0.13, -0.5, t), mix(0.8, 0.55, t), 0.65], 0.06, teal);
          line(
            [-0.5, 0.55, 0.55],
            [mix(0.13, -0.5, t), mix(0.8, 0.55, t), 0.65],
            gold,
            0.8,
            1,
            true,
          );
        }
        label([-0.9, -1.28, 0], 'Source', blue);
        label([0.9, -1.28, 0], 'Target', rose);
        break;
      }
      case 'longitudinal':
        [-1, 1].forEach((side, i) =>
          group([side * 0.95, 0, 0], 0.57, () => {
            anatomy(false);
            if (out) {
              mesh([0.43, 0.1, 0.55], [0.2 + i * 0.08, 0.23 + i * 0.08, 0.21], gold, 0.06);
              label([0, -1.6, 0], i ? 'Later' : 'Earlier', ink);
            }
          }),
        );
        if (out) {
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
          label([0.1, -1.25, 0.5], 'Correspondence', teal);
        }
        break;
      case 'routes':
        branches(
          out && k === 'route_discovery',
          k === 'route_repair' || k === 'route_unfold',
          k === 'prediction_screen'
            ? blue
            : ['route_repair', 'route_unfold'].includes(k)
              ? teal
              : null,
          k === 'prediction_screen',
        );
        if (k === 'route_repair' || k === 'route_unfold') {
          if (out)
            tube(
              [
                [0, -0.15, 0],
                [0.48, 0.17, -0.12],
              ],
              gold,
              0.065,
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
          path(
            [
              [-1.1, -1.45, 0],
              [1.1, -1.45, 0],
            ],
            gold,
            1,
            5,
          );
          label([0, -1.7, 0], 'Unfolded route', gold);
        }
        if (work && k === 'route_discovery')
          dot([0, -1.1 + ((clock * 0.4) % 2.2), 0.12], 0.07, gold);
        break;
      case 'tomography':
        if (k === 'mri' || k === 'mri_dynamic') {
          if (out) anatomy(false);
          else {
            sampled();
            if (work) plane(Math.sin(clock) * 0.9, teal, 0.12);
          }
          if (k === 'mri_dynamic') label([0, -1.4, 0], 'Sequence over time', teal);
        } else {
          if (out) {
            if (k === 'ct_phantom') {
              mesh([0, 0, 0], [0.87, 1.12, 0.62], ink);
              mesh([-0.28, 0.02, 0.25], [0.24, 0.65, 0.3], blue);
              mesh([0.28, 0.12, 0.24], [0.2, 0.53, 0.28], teal);
              mesh([0, 0.68, 0.3], [0.28, 0.15, 0.18], C.faint);
            } else if (k === 'pet') {
              mesh([0, 0, 0], [0.8, 1, 0.6], ink, 0.06, 0.28);
              mesh([0.27, 0.23, 0.45], [0.24, 0.28, 0.2], gold, 0.08);
            } else anatomy(false);
          } else {
            mesh([0, 0, 0], [0.4, 0.65, 0.4], ink, 0.08, 0.25);
            for (let i = 0; i < 9; i++) {
              const a = (i * TAU) / 9 + clock * 0.2,
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
          if (work) ring([0, 0, 0], 0.7 + 0.2 * Math.sin(clock), gold, 'z');
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
          else
            for (let i = 0; i < 42; i++)
              dot(
                [((i % 7) - 3) * 0.34 + Math.sin(i) * 0.04, (Math.floor(i / 7) - 2.5) * 0.34, 0],
                0.025,
                blue,
              );
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
            group([0.72, 0, 0], 0.53, () => field(true));
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
              mesh([0, 0, 0], [0.68, 0.21, 0.25], [blue, teal, gold][i % 3], 0, 0.65),
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
          mesh([-0.15, 0, 0], [0.36, 0.36, 0.36], ink, 0, 0.4);
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
          for (let i = 0; i < 9; i++)
            ring([0, (i - 4) * 0.025, 0], 0.62 + i * 0.055, i % 3 ? ink : gold, 'y', 0.5);
          if (k === 'astro_uncertainty') {
            ring([0, 0, 0], 1.2, rose, 'y', 0.75, true);
            label([0, -1.1, 0], 'Uncertain structure', rose);
          }
          if (k === 'astro_dynamic') label([0, -1.1, 0], 'Time-varying reconstruction', teal);
        }
        break;
      case 'interpretation':
        if (!out) {
          anatomy(false);
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
            box(
              [((i % 3) - 1) * 0.65, (Math.floor(i / 3) - 1) * 0.6, 0],
              [0.53, 0.49, 0.08],
              i % 4 === 0 ? gold : teal,
            );
        } else resultCard();
        break;
      case 'records':
        if (k === 'risk') {
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
    return { primitives, labels };
  }

  function legend(e) {
    const d = e.illustration,
      k = d.kind;
    let keys = [
      [C.ink, 'Structure / input'],
      [C.teal, 'Derived structure'],
      [C.gold, 'Focus / correspondence'],
    ];
    if (['segment', 'instances', 'nuclei', 'object_identity'].includes(k))
      keys =
        d.mask_mode === 'separate'
          ? [
              [C.ink, 'Input'],
              [C.teal, 'Organ'],
              [C.gold, 'Lesion'],
            ]
          : [
              [C.ink, 'Input'],
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
    if (k === 'cardiac_material')
      keys = [
        [C.teal, 'Model / geometry'],
        [C.blue, 'Initial mesh / dashed reference', true],
        [C.gold, 'Material point A'],
        [C.rose, 'Material point B'],
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
    if (d.mask_mode === 'binary')
      keys = [
        [C.ink, 'Input'],
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
    legend,
    supports: (kind) => Object.hasOwn(recipes, kind),
    action: (kind) => recipes[kind].action,
  };
})();
