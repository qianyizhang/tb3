/** Pure production evaluator / prefab lifecycle witnesses through Vite. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const root = path.resolve(__dirname, '..');
  const plan = JSON.parse(
    execFileSync(
      path.join(root, '.venv/bin/python'),
      [
        '-c',
        'import json; from pathlib import Path; from tb3_medical.explanation_stories import compile_story; r=Path.cwd(); print(json.dumps(compile_story(r,r/"groups/tubular-anatomy/presentation/stories/route-unfold-teaching-v1.story.md")))',
      ],
      { cwd: root, encoding: 'utf8' },
    ),
  );
  const { sampleStory, createRouteSampler, createRoutePrefab, Group } =
    await loadFrontend('story_fixture.mjs');
  const route = JSON.parse(
    fs.readFileSync(
      path.join(root, 'presentation/assets/teaching-fixtures/route-unfold-v1/route.json'),
      'utf8',
    ),
  );
  const sampler = createRouteSampler(route),
    parent = new Group(),
    prefab = createRoutePrefab(parent);
  const snapshots = new Map();
  for (let frame = 0; frame < plan.durationFrames; frame++)
    snapshots.set(frame, JSON.stringify(sampleStory(plan, frame)));
  for (const frame of [791, 0, 120, 264, 432, 576, 696, 27, 599, 265, 119, 790, 0]) {
    const state = sampleStory(plan, frame);
    assert.equal(JSON.stringify(state), snapshots.get(frame));
    const labels = prefab.update(state);
    assert.equal(labels.length, state.index >= 2 ? 3 : 2);
    const sample = sampler.atDistanceFraction(state.cursor);
    assert.equal(sample.profile[route.u_m.length - 1 - sample.row], sample.intensity);
    assert.ok(Object.isFrozen(state));
    assert.ok(Object.isFrozen(sample.profile));
  }
  const group = parent.children[0],
    context = group.getObjectByName('context');
  const positions = Array.from(context.geometry.getAttribute('position').array);
  for (let frame = 0; frame < 792; frame += 17) prefab.update(sampleStory(plan, frame));
  assert.deepEqual(
    Array.from(context.geometry.getAttribute('position').array),
    positions,
    'tree never morphs',
  );
  const counts = { geometry: 0, material: 0 };
  const gs = new Set(),
    ms = new Set();
  group.traverse((object) => {
    if (object.geometry) gs.add(object.geometry);
    if (object.material) ms.add(object.material);
  });
  gs.forEach((g) => g.addEventListener('dispose', () => counts.geometry++));
  ms.forEach((m) => m.addEventListener('dispose', () => counts.material++));
  prefab.dispose();
  prefab.dispose();
  assert.equal(parent.children.length, 0);
  assert.equal(counts.geometry, gs.size);
  assert.equal(counts.material, ms.size);
  assert.throws(() => sampleStory(plan, NaN));
  assert.throws(() => sampleStory(plan, 0.5));
  assert.throws(() => sampler.atColumn(-1));
  for (const column of [0, 47, 132, 191])
    for (const transverse of [0, 48, 96]) {
      const sample = sampler.atColumn(column, transverse);
      assert.equal(sample.row, 96 - transverse);
      assert.equal(sample.intensity, route.sample_values[column][transverse]);
      sample.worldPoint.forEach((v, axis) =>
        assert.equal(
          v,
          route.points[column][axis] + route.u_m[transverse] * route.normals[column][axis],
        ),
      );
    }
  console.log(
    'PASS: 792 absolute states, seek order, sentinels, fixed tree and exactly-once native disposal',
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
