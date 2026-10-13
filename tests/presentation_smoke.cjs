/** Critical portable journeys; exhaustive catalogue, geometry and captures stay local. */
const assert = require('node:assert/strict');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { withBrowser } = require('../presentation/tooling/browser.mts');
const { checkWorkbench } = require('./workbench_ui.cjs');
const { checkCohesion } = require('./frontend_cohesion.cjs');
const { checkPortability } = require('./frontend_portability.cjs');
const { checkLanguage } = require('./presentation_language.cjs');
const { checkNativeReader } = require('./native_reader_ui.cjs');

const root = path.resolve(process.argv[2] || '.local/presentation-check');
const reports = path.resolve(process.argv[3] || root + '-qa');
if (reports === root || reports.startsWith(root + path.sep)) {
  throw Error('Keep browser reports outside the publishable site directory');
}
withBrowser(async (browser) => {
  await checkWorkbench(browser, root, reports);
  await checkCohesion(browser, root, reports);
  await checkPortability(browser, root, reports);
  await checkLanguage(browser, root);
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  try {
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', (error) => errors.push(error.message));
    await context.route(/^https?:/, (route) => {
      errors.push(`Unexpected external request: ${route.request().url()}`);
      return route.abort();
    });
    await page.goto(pathToFileURL(path.join(root, 'task-explorer/index.html')).href);
    const data = await page.evaluate(() => JSON.parse(document.querySelector('#data').textContent));
    const entries = data.entries.filter(
      (entry) => data.explainer_views?.[entry.illustration?.story_id]?.family === 'native-trace',
    );
    assert.ok(entries.length, 'Smoke coverage includes native trace readers');
    for (const entry of entries) {
      await page.evaluate((id) => {
        location.hash = `${id}/0/brief?view=repository`;
      }, entry.id);
      await page.waitForFunction(
        (id) => document.querySelector('.task-detail')?.dataset.brief === id,
        entry.id,
      );
      await checkNativeReader(page, entry, data);
    }
    assert.deepEqual(errors, []);
    console.log(
      `Native reader smoke: ${entries.length} readers, chapter/reset/fallback checks passed.`,
    );
  } finally {
    await context.close();
  }
}).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
