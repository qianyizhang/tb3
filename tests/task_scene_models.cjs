// Geometry contracts that can be checked without a browser or medical runtime.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const context = vm.createContext({});
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
