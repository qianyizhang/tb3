const assert = require('node:assert/strict');
const path = require('node:path');
const vm = require('node:vm');
const { execFileSync } = require('node:child_process');
(async () => {
  const root = path.resolve(__dirname, '..');
  const plans = JSON.parse(
    execFileSync(
      path.join(root, '.venv/bin/python'),
      [
        '-c',
        'import json; from pathlib import Path; from tb3_medical.explanation_stories import compile_story; r=Path.cwd(); print(json.dumps([compile_story(r,p) for pattern in ["groups/*/presentation/stories/*.story.md","presentation/external-tasks/stories/*.story.md"] for p in r.glob(pattern)]))',
      ],
      { cwd: root, encoding: 'utf8' },
    ),
  );
  const { build } = await import('vite');
  const bundle = await build({
    configFile: false,
    logLevel: 'silent',
    build: {
      write: false,
      minify: false,
      lib: {
        entry: path.join(__dirname, 'expansion_fixture.mjs'),
        name: 'Fixture',
        formats: ['iife'],
      },
    },
  });
  const sandbox = vm.createContext({});
  vm.runInContext(bundle[0].output.find((c) => c.type === 'chunk').code, sandbox);
  const {
    sampleStory,
    nativeFactory,
    isPlanarStory,
    Group,
    traceEdges,
    graph,
    residualM,
    level0Point,
  } = sandbox.Fixture;
  let frames = 0,
    native = 0;
  for (const plan of plans) {
    const snapshots = Array.from({ length: plan.durationFrames }, (_, frame) =>
      JSON.stringify(sampleStory(plan, frame)),
    );
    frames += snapshots.length;
    for (const frame of [plan.durationFrames - 1, 0, ...plan.beats.map((b) => b.startFrame), 17]) {
      const state = sampleStory(plan, frame);
      assert.equal(JSON.stringify(state), snapshots[frame]);
      assert.ok(Object.isFrozen(state));
      assert.equal(state.recipe, plan.recipe);
    }
    assert.throws(() => sampleStory(plan, 1.5));
    if (isPlanarStory(plan)) continue;
    native++;
    const parent = new Group(),
      content = nativeFactory(plan)(parent);
    assert.equal(parent.children.length, 1);
    for (const beat of plan.beats) content.update(sampleStory(plan, beat.endFrame - 1));
    const geometries = new Set(),
      materials = new Set();
    parent.traverse((o) => {
      if (o.geometry) geometries.add(o.geometry);
      if (o.material) materials.add(o.material);
    });
    let disposed = 0;
    for (const resource of [...geometries, ...materials])
      resource.addEventListener('dispose', () => disposed++);
    content.dispose();
    content.dispose();
    assert.equal(parent.children.length, 0);
    assert.equal(disposed, geometries.size + materials.size);
    assert.throws(() => content.update(sampleStory(plan, 0)));
  }
  const full = traceEdges(1);
  assert.equal(full.length, 3);
  for (const { edge, points } of full) assert.equal(points.length, edge.points.length);
  assert.equal(new Set(graph.edges.map((e) => e.id)).size, 7);
  assert.ok(residualM(3) < 1e-12 && residualM(4) < 1e-12);
  assert.equal(JSON.stringify(level0Point([70, 110])), JSON.stringify([2680, 2040]));
  assert.equal(JSON.stringify(level0Point([0, 0])), JSON.stringify([2400, 1600]));
  console.log(
    `PASS: ${plans.length} stories / ${frames} deterministic frames / ${native} native lifetimes; connected trace and held-out rigid witnesses`,
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
