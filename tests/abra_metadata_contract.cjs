/** Browser-free checks of format derivation and reference-only reveal. */
const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');
(async () => {
  const mod = await loadFrontend('../presentation/frontend/task-visuals/abra-metadata-qa.ts');
  const source = {
    source_example: {
      study_date: '20260102',
      study_uid: 'illustrative-study',
      series: [
        { modality: 'SR', num_instances: 1, series_uid: 'sr' },
        { modality: 'CT', num_instances: 12, series_uid: 'first-ct' },
        { modality: 'SEG', num_instances: 1, series_uid: 'seg' },
        { modality: 'CT', num_instances: 4, series_uid: 'second-ct' },
      ],
    },
  };
  assert.equal(
    JSON.stringify(mod.metadataCounts(source)),
    JSON.stringify({ study: 1, series: 4, total: 18, ct: 16 }),
  );
  assert.equal(
    JSON.stringify(mod.metadataValues(source)),
    JSON.stringify(['12', '4', 'CT, SEG, SR', '20260102', 'first-ct']),
  );
  const base = {
    recipe: 'abra-metadata-qa-v1',
    scene: 'input',
    progress: 0,
    detail: 0,
    reference: 0,
  };
  assert.equal(mod.metadataReferenceVisible({ ...base, scene: 'reference', reference: 1 }), true);
  for (const scene of ['input', 'operation', 'output', 'limits'])
    assert.equal(mod.metadataReferenceVisible({ ...base, scene, reference: 1 }), false);
  assert.equal(mod.metadataReferenceVisible({ ...base, scene: 'reference' }), false);
  const beats = [0, 0.25, 0.5, 0.75, 1].map((n, i) => ({
    scene: 'operation',
    channels: { progress: [n, n] },
    startFrame: 144 * (i + 1),
  }));
  const plan = { recipe: 'abra-metadata-qa-v1', beats };
  for (let i = 0; i < 5; i++) assert.equal(mod.queryFrame(plan, i), 144 * (i + 1));
  assert.throws(() => mod.queryFrame({ ...plan, recipe: 'abra-viewer-control-v1' }, 0), /mismatch/);
  console.log(
    'PASS: counts/first CT/sorted modality derivation; canonical query frames; reference reveal/reset boundary',
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
