// Geometry contracts that can be checked without a browser or medical runtime.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const context = vm.createContext({});
const anatomyDir = path.join(__dirname, '../presentation/task-explorer/anatomy');
const sourceMeshes = Object.fromEntries(
  fs
    .readdirSync(anatomyDir)
    .filter((n) => n.endsWith('.json') && n !== 'manifest.json')
    .map((n) => [n.slice(0, -5), JSON.parse(fs.readFileSync(path.join(anatomyDir, n), 'utf8'))]),
);
vm.runInContext(
  fs
    .readFileSync(path.join(__dirname, '../presentation/task-explorer/scene-anatomy.js'), 'utf8')
    .replace('__ANATOMY_MESHES__', () => JSON.stringify(sourceMeshes))
    .replace('__ANATOMY_NOTICE__', '"Test notice"') + '\nthis.anatomy=AnatomyAssets;',
  context,
);

vm.runInContext(
  fs.readFileSync(path.join(__dirname, '../presentation/task-explorer/scene-models.js'), 'utf8') +
    '\nthis.models = TaskSceneModels;',
  context,
);
const models = context.models;
const entry = (kind, fields = {}) => ({ illustration: { kind, ...fields } });
const output = (kind, fields) => models.build(entry(kind, fields), 2, 0);
const focusPoints = (model) =>
  model.primitives.filter((p) => p.color === '#c38a36').flatMap((p) => p.points);
const depth = (points) =>
  Math.max(...points.map((p) => p[2])) - Math.min(...points.map((p) => p[2]));
assert.equal(depth(focusPoints(output('detect'))), 0, 'Image detections have planar boxes');
assert.ok(depth(focusPoints(output('box3d'))) > 0.5, 'Volume localization keeps box depth');
assert.equal(
  output('dynamic_mesh').labels.some((l) => l.text === 'A' || l.text === 'B'),
  false,
  'Cavity geometry does not imply tracked material particles',
);
assert.ok(output('cardiac_material').labels.some((l) => l.text === 'A'));
assert.equal(
  output('classify', { labels: ['normal', 'pneumonia'] }).labels.some((l) =>
    ['normal', 'pneumonia'].includes(l.text),
  ),
  false,
  'Classification shows an output schema rather than assigning a diagnosis',
);
const vessel = output('segment', { subject: 'aorta', mask_mode: 'binary' });
assert.equal(
  new Set(vessel.primitives.map((p) => p.color)).size,
  1,
  'Binary targets use one class',
);
const moon = output('astronomy', { scene_variant: 'moon' });
const craterPoints = moon.primitives.filter((p) => p.color === '#89a3aa').flatMap((p) => p.points);
assert.ok(craterPoints.length > 0);
assert.ok(
  craterPoints.every((p) => Math.abs(Math.hypot(...p) - 0.9) < 1e-10),
  'Lunar marks lie on the surface',
);
for (const kind of [
  'prediction_screen',
  'cardiac_anchors',
  'cardiac_material',
  'segmenter_calibration',
]) {
  assert.ok(
    models.legend(entry(kind)).some(([, , dashed]) => dashed),
    `${kind}: dashed legend`,
  );
  assert.ok(
    output(kind).primitives.some((p) => p.dash),
    `${kind}: dashed geometry`,
  );
}
console.log(
  'task scene geometry: dimensionality, mask classes, motion semantics and reference styles pass',
);

for (const name of [...context.anatomy.sourceIds, 'brain', 'teeth', 'torso']) {
  const parts = context.anatomy.get(name);
  assert.ok(
    parts.length && parts.reduce((n, p) => n + p.faces.length, 0) >= 600,
    name + ': detailed surface',
  );
  assert.ok(
    parts.every((p) => p.vertices.every((v) => v.every(Number.isFinite))),
    name + ': finite coordinates',
  );
  assert.ok(
    parts.every((p) => p.faces.every((f) => f.every((i) => i >= 0 && i < p.vertices.length))),
    name + ': valid faces',
  );
}
const kidneys = context.anatomy.get('kidneys');
const centerX = (p) => p.vertices.reduce((sum, v) => sum + v[0], 0) / p.vertices.length;
assert.ok(
  centerX(kidneys.find((p) => p.id === 'kidney_left')) >
    centerX(kidneys.find((p) => p.id === 'kidney_right')),
  'Frontal view preserves source left/right',
);
const torso = models.build(entry('longitudinal', { subject: 'torso' }), 0, 0);
assert.ok(torso.primitives.some((p) => p.asset === 'liver'));
assert.ok(torso.primitives.some((p) => p.asset === 'lung_upper_lobe_left'));
assert.ok(
  models
    .build(entry('segment', { subject: 'abdomen', target: 'pancreas', mask_mode: 'binary' }), 2, 0)
    .primitives.filter((p) => p.surface)
    .every((p) => p.asset === 'pancreas'),
);
console.log(
  'shared anatomy: finite surfaces, assembly laterality, torso reuse and target isolation pass',
);

const { createHash } = require('node:crypto');
const manifest = JSON.parse(fs.readFileSync(path.join(anatomyDir, 'manifest.json'), 'utf8'));
for (const [id, record] of Object.entries(manifest.assets)) {
  assert.equal(
    createHash('sha256')
      .update(fs.readFileSync(path.join(anatomyDir, id + '.json')))
      .digest('hex'),
    record.asset_sha256,
    id + ': retained mesh hash',
  );
  assert.equal(record.truncated_at_image_boundary, false);
  assert.ok(sourceMeshes[id].lod.faces.length <= 300, id + ': bounded assembly mesh');
}

// The material system applies to authored shapes and source-derived anatomy alike.
// Actual contours and reference paths are tested separately above.
for (const kind of ['dynamic_mesh', 'nuclei', 'vesselgraph', 'tensor', 'diffraction']) {
  const model = output(kind);
  assert.ok(
    model.primitives.some((p) => p.surface),
    kind + ': shaded physical form',
  );
  assert.ok(
    model.primitives
      .filter((p) => p.surface)
      .every(
        (p) =>
          p.points.length === 3 &&
          p.normals.length === 3 &&
          p.normals.every((n) => n.every(Number.isFinite)),
      ),
    kind + ': finite smooth triangle normals',
  );
  assert.equal(
    model.primitives.filter((p) => p.type === 'line' && !p.dash).length,
    0,
    kind + ': no decorative tessellation edges',
  );
}
console.log('shared materials: anatomy, cells, vessels, motion and fields use shaded surfaces');

for (const part of context.anatomy.get('brain')) {
  const edges = new Map();
  for (const [a, b, c] of part.faces)
    for (const [u, v] of [
      [a, b],
      [b, c],
      [c, a],
    ]) {
      const key = u < v ? u + ':' + v : v + ':' + u;
      edges.set(key, (edges.get(key) || 0) + 1);
    }
  assert.ok(
    [...edges.values()].every((n) => n === 2),
    part.id + ': closed seams and poles',
  );
  assert.ok(
    part.normals.every((n) => Math.hypot(...n) > 0.99),
    part.id + ': nondegenerate normals',
  );
}
const cardiac = entry('dynamic_mesh');
assert.equal(models.animated(entry('segment', { subject: 'abdomen' }), 0), false);
assert.equal(models.animated(cardiac, 0), true);
const atRest = models.build(cardiac, 2, 0, 1);
assert.equal(
  JSON.stringify(models.build(cardiac, 2, 10, 1)),
  JSON.stringify(atRest),
  'Motion settles at the completed output',
);
console.log('refined geometry: welded brain surfaces, finite normals and settled output pass');
