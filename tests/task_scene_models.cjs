// Geometry contracts that can be checked without a browser or medical runtime.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
async function main() {
  const { build } = await import('vite');
  const bundles = await build({
    configFile: false,
    root: path.join(__dirname, '..'),
    logLevel: 'silent',
    build: {
      write: false,
      minify: false,
      target: 'es2022',
      lib: {
        entry: path.join(__dirname, 'scene_fixture.mjs'),
        name: 'TB3SceneFixture',
        formats: ['iife'],
      },
    },
  });
  assert.equal(bundles.length, 1, 'One IIFE fixture bundle');
  const chunk = bundles[0].output.find((item) => item.type === 'chunk' && item.isEntry);
  assert.ok(chunk, 'Vite builds the real scene module entry');
  const sandbox = vm.createContext({});
  vm.runInContext(chunk.code, sandbox);
  const context = sandbox.TB3SceneFixture;
  for (const invalid of [
    [1, 2],
    [1, 2, 3, 4],
    [1, NaN, 3],
    [1, Infinity, 3],
    ['1', 2, 3],
  ])
    assert.throws(() => context.scenePoint(invalid), /three finite coordinates/);
  assert.throws(
    () =>
      context.polygon([
        [0, 0, 0],
        [1, 1, 1],
      ]),
    /at least three/,
  );
  const anatomyDir = path.join(__dirname, '../presentation/task-explorer/anatomy');
  const sourceMeshes = Object.fromEntries(
    fs
      .readdirSync(anatomyDir)
      .filter((n) => n.endsWith('.json') && n !== 'manifest.json')
      .map((n) => [n.slice(0, -5), JSON.parse(fs.readFileSync(path.join(anatomyDir, n), 'utf8'))]),
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
  const craterPoints = moon.primitives
    .filter((p) => p.color === '#89a3aa')
    .flatMap((p) => p.points);
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
  // Rounded vessel caps must shade from the same side as their face winding.
  // A mismatch reverses the lighting even though every vertex is finite.
  for (const face of output('route_unfold').primitives.filter(
    (p) => p.type === 'face' && p.surface,
  )) {
    const [a, b, c] = face.points;
    const u = b.map((v, i) => v - a[i]),
      v = c.map((v, i) => v - a[i]);
    const normal = [
      u[1] * v[2] - u[2] * v[1],
      u[2] * v[0] - u[0] * v[2],
      u[0] * v[1] - u[1] * v[0],
    ];
    assert.ok(
      normal.reduce((sum, value, i) => sum + value * face.normals[0][i], 0) >= -1e-12,
      'Vessel winding and shading normals agree',
    );
  }
  const cavity = output('cardiac_material');
  const cavityVertices = cavity.primitives
    .filter((p) => p.type === 'face' && p.surface)
    .flatMap((p) => p.points);
  for (const marker of cavity.primitives.filter((p) => p.type === 'dot')) {
    assert.ok(
      cavityVertices.some((p) => Math.hypot(...p.map((v, i) => v - marker.points[0][i])) < 0.055),
      'Material marker stays on the schematic cavity surface',
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
      .build(
        entry('segment', { subject: 'abdomen', target: 'pancreas', mask_mode: 'binary' }),
        2,
        0,
      )
      .primitives.filter((p) => p.surface)
      .every((p) => p.asset === 'pancreas'),
  );
  const audit = output('anatomy_audit', { subject: 'abdomen' });
  const witness = audit.labels.find((item) => item.text === 'Spatial witness')?.anchor;
  const focused = audit.primitives.filter((item) => item.asset === 'kidney_left');
  assert.ok(witness && focused.length, 'Audit keeps a highlighted supplied object and witness');
  for (const axis of [0, 1]) {
    const values = focused.flatMap((item) => item.points.map((point) => point[axis]));
    assert.ok(witness[axis] >= Math.min(...values) && witness[axis] <= Math.max(...values));
  }
  assert.equal(
    models.legend(entry('segment', { mask_mode: 'binary' }))[0][0],
    '#aaa99f',
    'Binary input legend matches neutral anatomy',
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

  // The reusable storyboard must remain complete without Canvas, app globals or
  // source media. Its labels describe schemas, not invented clinical answers.
  const rootDir = path.join(__dirname, '..');
  const entriesFrom = (file) => {
    const catalog = JSON.parse(fs.readFileSync(path.join(rootDir, file), 'utf8'));
    return [...(catalog.entries || []), ...(catalog.collections || []).flatMap(entriesFrom)];
  };
  const entries = entriesFrom('presentation/task-explorer/catalog.json');
  const illustrated = entries.filter((e) => e.illustration);
  const kinds = new Set();
  for (const e of illustrated) {
    kinds.add(e.illustration.kind);
    assert.ok(models.supports(e.illustration.kind), e.id + ': supported illustration kind');
    assert.ok(['3d', 'static'].includes(context.mode(e)), e.id + ': explicit rendering mode');
    if (e.illustration.subject === 'wsi')
      assert.equal(context.mode(e), 'static', e.id + ': planar WSI explanation');
    const story = context.teachingStory.describe(e);
    assert.ok(story.action && story.cue && story.form, e.id + ': concrete teaching recipe');
    assert.equal(story.stages.length, 3);
    for (const output of [false, true]) {
      const svg = context.teachingArt.render(e, output);
      assert.match(svg, /^<svg .*role="img"/);
      assert.match(svg, /conceptual drawing/);
      assert.doesNotMatch(svg, /(?:undefined|NaN|<script|https?:\/\/[^" ]+\.(?:png|jpg))/);
    }
  }
  assert.deepEqual([...kinds].sort(), [...context.teachingStory.kinds].sort());
  assert.equal(context.mode(entry('segment', { subject: 'abdomen', target: 'colon' })), 'static');
  assert.equal(context.mode(entry('segment', { subject: 'abdomen', target: 'spleen' })), '3d');
  const auditWork = models.build(entry('anatomy_audit', { subject: 'abdomen' }), 1, 0, 0.45);
  assert.ok(auditWork.labels.some((label) => label.text === 'Selected supplied label'));
  const routeWork = models.build(entry('route_unfold', { subject: 'vessels' }), 1, 0, 0.45);
  assert.ok(routeWork.labels.some((label) => label.text === 'Trace candidate route'));
  const teachingOutput = (kind, fields = {}) =>
    context.teachingArt.render(entry(kind, { input: 'Input', output: 'Output', ...fields }), true);
  assert.match(teachingOutput('classify', { labels: ['normal', 'pneumonia'] }), /class_label/);
  assert.doesNotMatch(teachingOutput('classify', { labels: ['normal', 'pneumonia'] }), /pneumonia/);
  assert.match(teachingOutput('multilabel'), /true \/ false/);
  assert.match(teachingOutput('risk'), /one probability per test row/);
  assert.match(teachingOutput('landmark_point'), /point → \(x, y, z\)/);
  assert.match(teachingOutput('landmark_point', { subject: 'wsi' }), /points → \(x, y\)/);
  assert.equal(
    context.teachingStory.describe(entry('landmark_point', { subject: 'wsi' })).action,
    'Search the whole slide',
  );
  assert.match(
    context.teachingStory.describe(entry('nuclei', { subject: 'wsi' })).cue,
    /annotated reference regions/,
  );
  assert.match(teachingOutput('detect'), /box → location \+ extent/);
  assert.match(teachingOutput('report'), /Impression \/ uncertainty/);
  assert.match(teachingOutput('segment', { mask_mode: 'separate' }), /organ mask/);
  assert.match(teachingOutput('segment', { mask_mode: 'separate' }), /lesion mask/);
  assert.notEqual(
    teachingOutput('segment', { subject: 'abdomen', target: 'pancreas', mask_mode: 'binary' }),
    teachingOutput('segment', { subject: 'abdomen', target: 'spleen', mask_mode: 'binary' }),
    'Named target masks use distinct spatial shapes',
  );
  const malicious = teachingOutput('segment', {
    subject: 'abdomen',
    target: '<script>alert(1)</script>',
    mask_mode: 'binary',
  });
  assert.doesNotMatch(malicious, /<script>/);
  assert.match(malicious, /&lt;script&gt;/);
  const tracing = entry('segment', { subject: 'abdomen' });
  const revealColors = (progress) =>
    models
      .build(tracing, 1, 0, progress)
      .primitives.filter((p) => p.surface && p.color !== '#aaa99f').length;
  assert.ok(revealColors(0.9) > revealColors(0.1), 'Process reveals labels on displayed regions');
  console.log(
    `teaching assets: ${illustrated.length} entries / ${kinds.size} kinds, complete static storyboards and honest output schemas pass`,
  );

  const planeScene = models.build(entry('register', { scene_variant: 'slice-to-volume' }), 2, 0);
  assert.equal(planeScene.primitives.filter((p) => p.type === 'image').length, 5);
  assert.ok(planeScene.labels.some((p) => p.text === 'Pixel → patient transform'));
  assert.ok(
    depth(planeScene.primitives.filter((p) => p.type === 'image').at(-1).points) > 0.4,
    'Oblique section preserves a tilted plane inside the volume',
  );
  assert.equal(
    models
      .build(entry('longitudinal', { subject: 'breast' }), 0, 0)
      .primitives.filter((p) => p.type === 'image').length,
    2,
    'Breast longitudinal input uses two image contexts rather than paired spheres',
  );
  assert.deepEqual(
    Array.from(
      models
        .build(
          entry('point_correspondence', { subject: 'brain', input: 'MRI and ultrasound' }),
          0,
          0,
        )
        .primitives.filter((p) => p.type === 'image')
        .map((p) => p.subject),
    ),
    ['brain', 'ultrasound'],
    'Explicit cross-modality input retains distinct image contexts',
  );
  assert.equal(
    context.teachingStory.describe(entry('register', { scene_variant: 'slice-to-volume' })).action,
    'Place the section in 3D',
  );
  assert.match(
    teachingOutput('register', { scene_variant: 'slice-to-volume' }),
    /position \+ orientation/,
  );
  console.log(
    'image context: reusable scan planes, modality distinctions and slice-to-volume pose pass',
  );
}
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
