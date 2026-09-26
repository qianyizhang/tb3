/* Task state, modality composition and portable URL restoration; no browser or scans. */
const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');

async function checkExplorer() {
  const { createModel, inScope, initialState, explorerReducer, taskRoute, parseExplorerData } =
    await loadFrontend('explorer_fixture.mjs', { globals: { URLSearchParams } });
  const entry = (id, modalities, role = 'task') => ({
    id,
    modalities,
    role,
    title: id,
    repo: 'Fixture repository',
    repository_id: 'fixture',
    category: 'segmentation',
    agent_work: 'implementation',
    task_family: 'image-task',
    goal: 'Mark the target',
    value: 'Explain the workflow',
    raw: 'Original image',
    helpers: 'Supplied example',
    output: 'Mask',
    challenge: 'Locate the boundary',
    spec: 'Mark the image',
    tools: 'Image viewer',
    score: 'Overlap',
    reference: 'Hidden mask',
    families: 'Fixture family',
    gap: 'No scientific inference',
    case_note: 'Not yet specified.',
    variants: [
      { name: 'Raw image', helper: 'None', remaining: 'Locate and mark' },
      { name: 'Supplied box', helper: 'Box', remaining: 'Mark' },
    ],
    visuals: { input: '', helpers: '', answer: '' },
    sources: [['Fixture source', 'fixture.md']],
  });
  const payload = {
    schema_version: 1,
    entries: [
      entry('mri-task', ['mri']),
      entry('ct-task', ['ct']),
      entry('paired-task', ['ct', 'mri']),
      entry('supporting', ['mri'], 'supporting'),
    ],
    inventory: {
      repositories: [
        {
          id: 'fixture',
          coverage: 'Fixture only',
          observed_on: '2026-09-22',
          commit: 'fixture',
          items: [
            {
              id: 'case-1',
              title: 'Case one',
              brief_id: 'ct-task',
              kind: 'case',
              definition: 'ct-task',
              condition: 'Supplied box',
              condition_index: 1,
              url: 'https://example.com/case',
            },
          ],
        },
      ],
    },
    taxonomy: {
      categories: { segmentation: { title: 'Segment images', description: 'Mark targets' } },
      agent_work: { implementation: 'Implementation' },
      modalities: { ct: 'CT', mri: 'MRI', ultrasound: 'Ultrasound' },
    },
    task_families: { 'image-task': { title: 'Mark an image', selector: 'Image' } },
    local_sources: {
      'fixture.md': { sha256: 'fixture-source', bytes: 2, base64: 'eAo=', content: 'x\n' },
    },
  };
  const model = createModel(parseExplorerData(JSON.stringify(payload)));
  const reduce = (state, action) => explorerReducer(model, state, action);
  const filters = (modality, lane = 'tasks', work = 'implementation') => ({
    type: 'filters',
    view: 'capability',
    lane,
    work,
    modality,
  });
  const start = initialState(model);
  assert.equal(inScope(model.get('paired-task'), 'tasks', 'implementation', 'ct'), true);
  assert.equal(inScope(model.get('paired-task'), 'tasks', '', 'mri'), true);
  assert.equal(inScope(model.get('mri-task'), 'tasks', '', 'ct'), false);
  assert.equal(inScope(model.get('supporting'), 'tasks', '', 'mri'), false);
  assert.equal(model.match(model.get('ct-task'), 'ct'), true, 'Search includes authored modality');
  let state = reduce(start, filters('ct'));
  assert.equal(state.selected, 'ct-task', 'Choose a task compatible with the selected modality');
  assert.equal(state.modality, 'ct');
  assert.equal(state.work, 'implementation');
  assert.equal(
    model.data.entries.filter((row) => inScope(row, state.lane, state.work, state.modality)).length,
    2,
  );
  const restored = reduce(start, { type: 'route', hash: taskRoute(state, model) });
  assert.deepEqual(restored, state, 'A portable task URL restores all independent filters');
  state = reduce(state, { type: 'condition', condition: 1 });
  state = reduce(state, { type: 'variant', id: 'paired-task' });
  assert.equal(state.condition, 1, 'Compatible assistance survives a variant change');
  assert.equal(state.modality, 'ct', 'A multi-modality variant retains the active filter');
  state = reduce(state, { type: 'variant', id: 'mri-task' });
  assert.equal(state.modality, '', 'An explicitly selected incompatible variant remains reachable');
  const incompatible = reduce(start, {
    type: 'route',
    hash: '#mri-task/0/overview?modality=ct&view=capability&lane=tasks',
  });
  assert.equal(incompatible.selected, 'mri-task');
  assert.equal(incompatible.modality, '');
  const noMatches = reduce(start, filters('ultrasound'));
  assert.equal(
    noMatches.modality,
    'ultrasound',
    'Keep a zero-result filter visible so it can be reset',
  );
  assert.equal(
    model.data.entries.filter((row) =>
      inScope(row, noMatches.lane, noMatches.work, noMatches.modality),
    ).length,
    0,
  );
  assert.deepEqual(
    reduce(start, { type: 'route', hash: taskRoute(noMatches, model) }),
    noMatches,
    'Reload preserves a valid modality with no matching tasks',
  );
  const emptyCombination = reduce(start, filters('ct', 'supporting'));
  assert.equal(emptyCombination.lane, 'supporting');
  assert.equal(emptyCombination.modality, 'ct');
  assert.deepEqual(
    reduce(start, { type: 'route', hash: taskRoute(emptyCombination, model) }),
    emptyCombination,
    'An impossible role/modality combination survives reload and history restoration',
  );
  assert.equal(reduce(noMatches, { type: 'reset' }).modality, '');
  assert.equal(
    reduce(restored, { type: 'search', query: 'mri-task' }).selected,
    'ct-task',
    'Search does not select tasks outside the active modality',
  );
  const supporting = reduce(restored, filters('mri', 'supporting'));
  assert.equal(supporting.selected, 'supporting');
  assert.equal(supporting.work, '', 'Supporting research resets the task-only work filter');
  assert.equal(supporting.modality, 'mri');

  const source = reduce(restored, { type: 'source', source: 'fixture-source' });
  assert.equal(source.tab, 'sources');
  assert.equal(
    reduce(start, { type: 'route', hash: taskRoute(source, model) }).source,
    'fixture-source',
  );
  assert.equal(reduce(source, { type: 'tab', tab: 'overview' }).source, '');
  assert.equal(
    reduce(start, { type: 'route', hash: '#ct-task/0/sources?source=unknown' }).source,
    '',
    'Only sources belonging to the task can be opened',
  );
  const selectedCase = reduce(start, { type: 'route', hash: '#fixture/task/case-1/1/sources' });
  assert.equal(selectedCase.selected, 'ct-task');
  assert.equal(selectedCase.selectedItem, 'case-1');
  assert.equal(selectedCase.condition, 1);
  assert.equal(
    reduce(start, { type: 'route', hash: taskRoute(selectedCase, model) }).selectedItem,
    'case-1',
  );
  const datasets = reduce(selectedCase, { type: 'route', hash: '#datasets/source' });
  assert.equal(datasets.dataset, 'source');
  assert.equal(
    datasets.selectedItem,
    'case-1',
    'Dataset navigation retains the task return target',
  );
  assert.equal(reduce(datasets, { type: 'route', hash: taskRoute(datasets, model) }).dataset, null);
  assert.equal(
    reduce(start, { type: 'route', hash: '#fixture/task/%E0%A4%A/invalid/unknown' }).selected,
    'mri-task',
    'Malformed legacy links use a valid task',
  );
  assert.throws(
    () => parseExplorerData(JSON.stringify({ ...payload, schema_version: 2 })),
    /schema_version 1/,
  );
  assert.throws(
    () => parseExplorerData(JSON.stringify({ ...payload, entries: [entry('bad', [])] })),
    /modalities/,
  );
  console.log('Explorer modality composition, case/source routes and payload validation passed');
}
checkExplorer().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
