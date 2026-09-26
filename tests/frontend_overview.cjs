/* URL restoration and evidence semantics, without a browser or research artifacts. */
const assert = require('node:assert/strict');
const { loadFrontend } = require('./frontend_bundle.cjs');

async function checkOverview() {
  const { parseOverviewData, initialRoute, readOverviewRoute, overviewUrl, filterRecords } =
    await loadFrontend('../presentation/frontend/overview-data.ts', {
      globals: { URL, URLSearchParams },
    });
  const plain = (value) => JSON.parse(JSON.stringify(value));

  const payload = {
    schema_version: 1,
    local_media: false,
    records: [
      { id: 'area-a', kind: 'group', title: 'Brain imaging', current: {} },
      {
        id: 'idea-a',
        kind: 'idea',
        group_id: 'area-a',
        title: 'Find the change',
        current: { idea_state: 'selected' },
      },
      {
        id: 'experiment-a',
        kind: 'experiment',
        group_id: 'area-a',
        title: 'Longitudinal MRI',
        current: { assessment: 'needs_review', attention: true },
      },
      {
        id: 'experiment-b',
        kind: 'experiment',
        group_id: 'area-a',
        title: 'Longitudinal MRI control',
        current: { assessment: 'not_assessed', attention: false },
      },
      {
        id: 'evaluation-a',
        kind: 'evaluation',
        group_id: 'area-a',
        model: 'oracle',
        outcome: 'pass',
        current: {},
      },
      { id: 'finding-b', kind: 'finding', group_id: 'area-b', current: {} },
    ],
    vocabulary: {
      axes: {
        assessment: {
          values: {
            needs_review: {
              label: 'Needs review',
              definition: 'A concrete issue needs assessment.',
            },
            not_assessed: {
              label: 'Not assessed',
              definition: 'No explicit assessment is available.',
            },
          },
        },
      },
      context_badges: {},
      display_rules: { experiment_primary: ['assessment'] },
    },
  };
  const data = parseOverviewData(payload);
  const ids = (route) => plain(filterRecords(data.records, route).map((row) => row.id));

  assert.deepEqual(ids(initialRoute), ['idea-a', 'experiment-a', 'experiment-b', 'finding-b']);
  assert.deepEqual(ids({ ...initialRoute, group: 'area-a', search: 'longitudinal mri' }), [
    'experiment-a',
    'experiment-b',
  ]);
  assert.deepEqual(ids({ ...initialRoute, kind: 'finding', status: 'attention' }), [
    'experiment-a',
  ]);
  assert.deepEqual(
    ids({ ...initialRoute, kind: 'experiment', status: 'assessment:not_assessed' }),
    ['experiment-b'],
  );
  assert.deepEqual(ids({ ...initialRoute, kind: '', search: 'oracle pass' }), ['evaluation-a']);

  const route = readOverviewRoute(
    '?q=longitudinal%20MRI&group=area-a&kind=experiment&status=assessment%3Aneeds_review&record=experiment-a',
    data,
  );
  assert.deepEqual(ids(route), ['experiment-a']);
  const target = overviewUrl('http://localhost/index.html?other=kept#research-record', route);
  assert.equal(target.searchParams.get('other'), 'kept');
  assert.equal(target.hash, '#research-record');
  assert.deepEqual(plain(readOverviewRoute(target.search, data)), plain(route));
  assert.equal(
    overviewUrl('http://localhost/?q=term&kind=experiment&record=a', initialRoute).search,
    '',
  );
  assert.equal(readOverviewRoute('?kind=&q=', data).kind, '');
  assert.deepEqual(
    plain(readOverviewRoute('?kind=unrecognized&group=missing&status=assessment%3Amissing', data)),
    plain(initialRoute),
  );

  assert.throws(
    () => parseOverviewData({ ...payload, schema_version: 2 }),
    /Invalid research record payload/,
  );
  assert.throws(
    () => parseOverviewData({ ...payload, local_media: 'false' }),
    /Invalid research record payload/,
  );
  assert.throws(
    () => parseOverviewData({ ...payload, vocabulary: {} }),
    /Invalid research status vocabulary/,
  );
  assert.throws(
    () => parseOverviewData({ ...payload, records: [payload.records[0], payload.records[0]] }),
    /Invalid research record/,
  );
  assert.throws(
    () =>
      parseOverviewData({
        ...payload,
        records: [{ ...payload.records[0], portable_links: [{ label: 'Source', url: 42 }] }],
      }),
    /Invalid research record links/,
  );
  assert.throws(
    () =>
      parseOverviewData({
        ...payload,
        records: [{ ...payload.records[0], current: { review_flags: [{}] } }],
      }),
    /Invalid research review flags/,
  );
  console.log('Overview URL restoration, filter semantics and payload validation passed');
}
checkOverview().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
