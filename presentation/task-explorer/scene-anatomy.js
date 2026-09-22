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
  // Weld periodic seams and collapsed poles before computing normals. Leaving
  // each parameter strip disconnected produced spikes and visible shading seams.
  function parametric(id, label, fn, rows = 30, cols = 48) {
    const vertices = [],
      faces = [],
      indices = [],
      unique = new Map();
    for (let j = 0; j <= rows; j++)
      for (let i = 0; i <= cols; i++) {
        const p = fn(i / cols, j / rows),
          key = p.map((v) => Math.round(v * 1e6)).join(',');
        if (!unique.has(key)) {
          unique.set(key, vertices.length);
          vertices.push(p);
        }
        indices.push(unique.get(key));
      }
    for (let j = 0; j < rows; j++)
      for (let i = 0; i < cols; i++) {
        const a = j * (cols + 1) + i,
          b = a + cols + 1;
        for (const face of [
          [a, b, a + 1],
          [a + 1, b, b + 1],
        ]) {
          const mapped = face.map((n) => indices[n]);
          if (new Set(mapped).size === 3) faces.push(mapped);
        }
      }
    return { id, label, vertices, faces, provenance: 'authored' };
  }
  // One display-only Loop subdivision rounds coarse source silhouettes. Retained
  // meshes and scientific evidence remain byte-identical; assemblies share a frame.
  function subdivide(part) {
    const { vertices, faces } = part;
    const neighbors = vertices.map(() => new Set()),
      edges = new Map();
    const key = (a, b) => (a < b ? a + ':' + b : b + ':' + a);
    for (const [a, b, c] of faces)
      for (const [u, v, opposite] of [
        [a, b, c],
        [b, c, a],
        [c, a, b],
      ]) {
        neighbors[u].add(v);
        neighbors[v].add(u);
        const id = key(u, v);
        if (!edges.has(id)) edges.set(id, { a: u, b: v, opposites: [] });
        edges.get(id).opposites.push(opposite);
      }
    const boundary = vertices.map(() => []);
    for (const edge of edges.values())
      if (edge.opposites.length === 1) {
        boundary[edge.a].push(edge.b);
        boundary[edge.b].push(edge.a);
      }
    const result = vertices.map((p, i) => {
      if (boundary[i].length === 2)
        return p.map(
          (v, q) => 0.75 * v + 0.125 * (vertices[boundary[i][0]][q] + vertices[boundary[i][1]][q]),
        );
      const adjacent = [...neighbors[i]],
        n = adjacent.length;
      if (!n) return [...p];
      const beta = (5 / 8 - (3 / 8 + Math.cos((2 * Math.PI) / n) / 4) ** 2) / n;
      return p.map(
        (v, q) => (1 - n * beta) * v + beta * adjacent.reduce((sum, j) => sum + vertices[j][q], 0),
      );
    });
    for (const edge of edges.values()) {
      edge.index = result.length;
      result.push(
        vertices[edge.a].map((v, q) =>
          edge.opposites.length === 2
            ? 0.375 * (v + vertices[edge.b][q]) +
              0.125 * (vertices[edge.opposites[0]][q] + vertices[edge.opposites[1]][q])
            : 0.5 * (v + vertices[edge.b][q]),
        ),
      );
    }
    const refined = [];
    for (const [a, b, c] of faces) {
      const ab = edges.get(key(a, b)).index,
        bc = edges.get(key(b, c)).index,
        ca = edges.get(key(c, a)).index;
      refined.push([a, ab, ca], [b, bc, ab], [c, ca, bc], [ab, bc, ca]);
    }
    return { ...part, vertices: result, faces: refined };
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
            Math.sin(7 * a + 1.4 * Math.sin(3 * b)) * Math.sin(9 * b + 0.8 * Math.cos(3 * a));
          const relief = 1 + 0.055 * folds * Math.sin(b) ** 2;
          return [
            side * (0.035 + 0.8 * (0.5 + 0.5 * Math.cos(a)) * Math.sin(b) * relief),
            0.64 * Math.cos(b) * relief + 0.2,
            0.92 * Math.sin(a) * Math.sin(b) * relief,
          ];
        },
        28,
        48,
      ),
    );
    const cerebellum = parametric(
      'cerebellum',
      'Cerebellum',
      (u, v) => {
        const a = u * Math.PI * 2,
          b = v * Math.PI,
          ridge = 1 + 0.018 * Math.cos(b * 26) * Math.sin(b) ** 2;
        return [
          0.61 * Math.cos(a) * Math.sin(b) * ridge,
          -0.48 + 0.34 * Math.cos(b),
          -0.46 + 0.47 * Math.sin(a) * Math.sin(b) * ridge,
        ];
      },
      18,
      36,
    );
    const stem = parametric(
      'brainstem',
      'Brainstem',
      (u, v) => {
        const a = u * Math.PI * 2,
          r = 0.14 * Math.sin(v * Math.PI);
        return [r * Math.cos(a), -0.64 + 0.29 * Math.cos(v * Math.PI), -0.13 + r * Math.sin(a)];
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
              0.22 + (0.2 + cusp * Math.sin(b) ** 2) * Math.cos(b),
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
                radius = 0.08 * Math.cos((v * Math.PI) / 2);
              return [
                x + (molar ? (r ? 1 : -1) * (0.055 + 0.03 * v) : 0) + radius * Math.cos(angle),
                0.12 - 0.49 * Math.sin((v * Math.PI) / 2),
                z - 0.04 * v + radius * Math.sin(angle),
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
        ids
          .map((id) => {
            // Distant multi-organ arrangements use a lighter mesh, preserving the same source frame.
            const data = name === 'torso' || name === 'abdomen' ? source[id].lod : source[id];
            return {
              id,
              label: names[id],
              faces: data.faces,
              vertices: data.vertices.map(([r, a, s]) => [-r, s, a]),
              provenance: 'TotalSegmentator',
            };
          })
          .map(subdivide),
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
