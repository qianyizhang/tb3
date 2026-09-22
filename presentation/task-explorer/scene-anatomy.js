// Shared teaching assets. Source surfaces and derivation are documented in anatomy/.
const AnatomyAssets = (() => {
  const source = __ANATOMY_MESHES__;
  const notice = __ANATOMY_NOTICE__;
  const names = {
    liver: 'Liver',
    kidney_left: 'Left kidney',
    kidney_right: 'Right kidney',
    spleen: 'Spleen',
    pancreas: 'Pancreas',
    stomach: 'Stomach',
    gallbladder: 'Gallbladder',
    heart: 'Heart',
    aorta: 'Aorta',
    trachea: 'Trachea',
    pulmonary_vein: 'Pulmonary veins',
    lung_upper_lobe_left: 'Left upper lobe',
    lung_lower_lobe_left: 'Left lower lobe',
    lung_upper_lobe_right: 'Right upper lobe',
    lung_middle_lobe_right: 'Right middle lobe',
    lung_lower_lobe_right: 'Right lower lobe',
    vertebrae_L3: 'Lumbar vertebra',
    prostate: 'Prostate',
  };
  const lungs = [
    'lung_upper_lobe_left',
    'lung_lower_lobe_left',
    'lung_upper_lobe_right',
    'lung_middle_lobe_right',
    'lung_lower_lobe_right',
  ];
  const abdomen = [
    'liver',
    'stomach',
    'spleen',
    'pancreas',
    'kidney_left',
    'kidney_right',
    'gallbladder',
  ];
  const groups = {
    abdomen,
    torso: [...lungs, 'heart', ...abdomen],
    chest: [...lungs, 'trachea'],
    'chest-ct': [...lungs, 'trachea'],
    lungs,
    airways: [...lungs, 'trachea'],
    heart: ['heart', 'pulmonary_vein'],
    ultrasound: ['heart', 'pulmonary_vein'],
    kidneys: ['kidney_left', 'kidney_right'],
    spine: ['vertebrae_L3'],
  };
  const cache = new Map();
  const bounds = (parts) => {
    const lo = [Infinity, Infinity, Infinity],
      hi = [-Infinity, -Infinity, -Infinity];
    parts.forEach((p) =>
      p.vertices.forEach((v) =>
        v.forEach((n, i) => {
          lo[i] = Math.min(lo[i], n);
          hi[i] = Math.max(hi[i], n);
        }),
      ),
    );
    return { center: lo.map((n, i) => (n + hi[i]) / 2), span: hi.map((n, i) => n - lo[i]) };
  };
  const fit = (parts) => {
    const { center, span } = bounds(parts),
      scale = Math.min(2.5 / span[0], 2.5 / span[1], 1.9 / span[2]);
    return parts.map((p) => ({
      ...p,
      vertices: p.vertices.map((v) => v.map((n, i) => (n - center[i]) * scale)),
    }));
  };
  function parametric(id, label, fn, rows = 30, cols = 48) {
    const vertices = [],
      faces = [];
    for (let j = 0; j <= rows; j++)
      for (let i = 0; i <= cols; i++) vertices.push(fn(i / cols, j / rows));
    for (let j = 0; j < rows; j++)
      for (let i = 0; i < cols; i++) {
        const a = j * (cols + 1) + i,
          b = a + cols + 1;
        faces.push([a, b, a + 1], [a + 1, b, b + 1]);
      }
    return { id, label, vertices, faces, provenance: 'authored' };
  }
  // Authored cortical folds and dental surfaces stay distinct from extracted CT assets.
  function brain() {
    const hemispheres = [-1, 1].map((side) =>
      parametric(
        'hemisphere' + side,
        side < 0 ? 'Right hemisphere' : 'Left hemisphere',
        (u, v) => {
          const a = u * Math.PI * 2,
            b = v * Math.PI;
          const folds =
            Math.sin(13 * a + 2.8 * Math.sin(4 * b)) * Math.sin(16 * b + 1.7 * Math.cos(5 * a));
          const relief = 1 + 0.052 * folds + 0.028 * Math.cos(23 * a + 8 * b);
          return [
            side * (0.035 + 0.8 * (0.5 + 0.5 * Math.cos(a)) * Math.sin(b) * relief),
            0.64 * Math.cos(b) * relief + 0.2,
            0.92 * Math.sin(a) * Math.sin(b) * relief,
          ];
        },
        36,
        64,
      ),
    );
    const cerebellum = parametric(
      'cerebellum',
      'Cerebellum',
      (u, v) => {
        const a = u * Math.PI * 2,
          b = v * Math.PI,
          ridge = 1 + 0.045 * Math.cos(b * 42);
        return [
          0.61 * Math.cos(a) * Math.sin(b) * ridge,
          -0.48 + 0.34 * Math.cos(b),
          -0.46 + 0.47 * Math.sin(a) * Math.sin(b) * ridge,
        ];
      },
      24,
      36,
    );
    const stem = parametric(
      'brainstem',
      'Brainstem',
      (u, v) => {
        const a = u * Math.PI * 2,
          r = 0.14 * Math.sin(v * Math.PI);
        return [r * Math.cos(a), -0.38 - 0.65 * v, -0.07 - 0.18 * v + r * Math.sin(a)];
      },
      12,
      20,
    );
    return fit([...hemispheres, cerebellum, stem]);
  }
  function teeth() {
    const parts = [];
    for (let i = 0; i < 14; i++) {
      const a = 0.12 + (i * (Math.PI - 0.24)) / 13,
        x = 1.18 * Math.cos(a),
        z = 0.88 * Math.sin(a);
      const front = Math.abs(i - 6.5),
        molar = front > 4,
        canine = front > 2 && front < 4;
      const width = molar ? 0.2 : canine ? 0.15 : 0.13;
      parts.push(
        parametric(
          'tooth-' + i,
          'Tooth ' + (i + 1),
          (u, v) => {
            const angle = u * Math.PI * 2,
              b = v * Math.PI;
            const cusp = molar ? 0.04 * Math.cos(angle * 4) : canine ? 0.035 : 0;
            return [
              x + width * Math.cos(angle) * Math.sin(b),
              0.22 + (0.2 + cusp) * Math.cos(b),
              z + (molar ? 0.19 : 0.11) * Math.sin(angle) * Math.sin(b),
            ];
          },
          10,
          16,
        ),
      );
      for (let r = 0; r < (molar ? 2 : 1); r++) {
        parts.push(
          parametric(
            'root-' + i + '-' + r,
            'Root',
            (u, v) => {
              const angle = u * Math.PI * 2,
                radius = 0.075 * (1 - v) ** 0.6;
              return [
                x + (molar ? (r ? 1 : -1) * (0.065 + 0.055 * v) : 0) + radius * Math.cos(angle),
                0.15 - 0.65 * v,
                z - 0.08 * v + radius * Math.sin(angle),
              ];
            },
            8,
            12,
          ),
        );
      }
    }
    return fit(parts);
  }
  function get(name) {
    if (cache.has(name)) return cache.get(name);
    let parts;
    if (name === 'brain') parts = brain();
    else if (name === 'teeth') parts = teeth();
    else {
      const ids = groups[name] || (source[name] ? [name] : null);
      if (!ids) return null;
      parts = fit(
        ids.map((id) => {
          // Distant multi-organ arrangements use a lighter mesh, preserving the same source frame.
          const data = name === 'torso' || name === 'abdomen' ? source[id].lod : source[id];
          return {
            id,
            label: names[id],
            faces: data.faces,
            vertices: data.vertices.map(([r, a, s]) => [-r, s, a]),
            provenance: 'TotalSegmentator',
          };
        }),
      );
    }
    parts.forEach((part) => {
      const normals = part.vertices.map(() => [0, 0, 0]);
      part.faces.forEach(([a, b, c]) => {
        const u = part.vertices[b].map((n, i) => n - part.vertices[a][i]),
          v = part.vertices[c].map((n, i) => n - part.vertices[a][i]),
          n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
        for (const index of [a, b, c]) n.forEach((value, i) => (normals[index][i] += value));
      });
      part.normals = normals.map((n) => {
        const length = Math.hypot(...n) || 1;
        return n.map((v) => v / length);
      });
    });
    cache.set(name, parts);
    return parts;
  }
  const has = (name) =>
    name === 'brain' ||
    name === 'teeth' ||
    Object.hasOwn(groups, name) ||
    Object.hasOwn(source, name);
  return { get, has, names, notice, sourceIds: Object.keys(source) };
})();
