const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const mod = await loadFrontend('../presentation/frontend/task-visuals/radagent-vqa.ts');
  const chosen = '(b) Amber token';
  assert.equal(mod.fullOptionFormatMatches(chosen, chosen), true);
  assert.equal(mod.fullOptionFormatMatches(' (B) AMBER TOKEN ', chosen), true);
  for (const candidate of ['b', 'Amber token', 'b Amber token', '(b) Amber  token'])
    assert.equal(mod.fullOptionFormatMatches(candidate, chosen), false);
  const base = { recipe: 'radagent-vqa-v1', scene: 'input', progress: 0, detail: 0, reference: 0 };
  assert.equal(mod.vqaReferenceVisible({ ...base, scene: 'reference', reference: 1 }), true);
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(mod.vqaReferenceVisible({ ...base, scene, reference: 1 }), false);
  assert.equal(mod.vqaReferenceVisible({ ...base, scene: 'reference' }), false);
  const beats = [0, 0.5, 1].map((n, i) => ({
    scene: 'operation',
    channels: { progress: [n, n] },
    startFrame: 168 * (i + 1),
  }));
  for (let i = 0; i < 3; i++)
    assert.equal(mod.operationFrame({ recipe: 'radagent-vqa-v1', beats }, i), 168 * (i + 1));
  assert.throws(() => mod.operationFrame({ recipe: 'abra-metadata-qa-v1', beats }, 0), /mismatch/);
  console.log(
    'PASS: full-option prefix/string rule; source-defined normalization; reference/reset and canonical tool-scope frames',
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
