import { point, rotation } from './model.mjs';
export function renderSection(pose, PROJ, k) {
  const screen = (p) => k.iso(p, PROJ);
  const polygon = (points) =>
    'M' +
    points
      .map((p) =>
        screen(p)
          .map((x) => x.toFixed(2))
          .join(','),
      )
      .join('L') +
    'Z';
  const view = [
    Math.cos((48 * Math.PI) / 180) * Math.cos((32 * Math.PI) / 180),
    Math.sin((48 * Math.PI) / 180) * Math.cos((32 * Math.PI) / 180),
    Math.sin((32 * Math.PI) / 180),
  ];
  function boxFaces(x, y, z, w, d, h) {
    const corners = [
      [x, y, z],
      [x + w, y, z],
      [x + w, y + d, z],
      [x, y + d, z],
      [x, y, z + h],
      [x + w, y, z + h],
      [x + w, y + d, z + h],
      [x, y + d, z + h],
    ].map((p) => point(pose, p));
    const r = rotation(pose);
    return [
      [
        [0, 3, 2, 1],
        [0, 0, -1],
      ],
      [
        [4, 5, 6, 7],
        [0, 0, 1],
      ],
      [
        [0, 1, 5, 4],
        [0, -1, 0],
      ],
      [
        [1, 2, 6, 5],
        [1, 0, 0],
      ],
      [
        [2, 3, 7, 6],
        [0, 1, 0],
      ],
      [
        [3, 0, 4, 7],
        [-1, 0, 0],
      ],
    ].flatMap(([ids, n]) => {
      const normal = r.map((row) => row.reduce((s, v, j) => s + v * n[j], 0));
      if (normal.reduce((s, v, i) => s + v * view[i], 0) <= 0) return [];
      const points = ids.map((i) => corners[i]);
      const depth = points.reduce((s, p) => s + k.depthOf(p, PROJ), 0) / 4;
      const shade =
        n[2] > 0
          ? 'var(--anatomy-top)'
          : `var(--anatomy-shade-${Math.min(3, Math.max(0, Math.floor(2 + normal[0] - normal[1])))})`;
      return [
        {
          depth,
          html: `<path d="${polygon(points)}" fill="${shade}" stroke="var(--anatomy-hi)" stroke-width=".7" stroke-linejoin="round"/>`,
        },
      ];
    });
  }
  const pattern = `<rect x="-40" y="-40" width="80" height="80" rx="1" fill="#202123"/><ellipse cx="0" cy="0" rx="32" ry="36" fill="#a8a8a3"/><ellipse cx="-12" cy="-6" rx="12" ry="20" fill="#3e4041"/><ellipse cx="12" cy="-3" rx="10" ry="22" fill="#494b4c"/><ellipse cx="4" cy="7" rx="12" ry="14" fill="#d3d3cc"/><ellipse cx="0" cy="25" rx="6" ry="6" fill="#e7e7df"/><rect x="-37" y="-37" width="4" height="4" fill="#f4f4ec"/>`;
  function sectionArt() {
    let faces = boxFaces(-46, -46, -4, 92, 92, 3);
    for (const b of [
      [-46, -46, -1, 92, 4, 2],
      [-46, 42, -1, 92, 4, 2],
      [-46, -42, -1, 4, 84, 2],
      [42, -42, -1, 4, 84, 2],
    ])
      faces.push(...boxFaces(...b));
    const a = screen(point(pose, [0, 0, 0])),
      u = screen(point(pose, [1, 0, 0])),
      v = screen(point(pose, [0, 1, 0]));
    const normal = rotation(pose).map((row) => row[2]);
    if (normal.reduce((sum, v, i) => sum + v * view[i], 0) > 0)
      faces.push({
        depth: k.depthOf(point(pose, [0, 0, 0]), PROJ),
        html: `<g transform="matrix(${u[0] - a[0]},${u[1] - a[1]},${v[0] - a[0]},${v[1] - a[1]},${a[0]},${a[1]})">${pattern}</g>`,
      });
    for (const x of [-44, 40])
      for (const y of [-44, 40]) {
        faces.push(...boxFaces(x, y, 1, 4, 4, 2));
        const p = screen(point(pose, [x + 2, y + 2, 3.1]));
        faces.push({
          depth: k.depthOf(point(pose, [x + 2, y + 2, 3.2]), PROJ),
          html: `<circle cx="${p[0]}" cy="${p[1]}" r=".8" fill="var(--anatomy-hi)"/>`,
        });
      }
    faces.sort((a, b) => a.depth - b.depth);
    return faces.map((f) => f.html).join('');
  }
  return sectionArt();
}
