/** One disposable browser; each suite uses its own isolated context. */
const path = require('node:path');
const { withBrowser } = require('../presentation/tooling/browser.mts');
const { checkWorkbench } = require('./workbench_ui.cjs');
const { checkExplorer } = require('./task_explorer_ui.cjs');
const { checkCohesion } = require('./frontend_cohesion.cjs');
const { checkPortability } = require('./frontend_portability.cjs');
const { checkReview } = require('./tooling_browser.mts');

const root = path.resolve(process.argv[2] || '.local/presentation-check');
const reports = path.resolve(process.argv[3] || root + '-qa');
if (reports === root || reports.startsWith(root + path.sep)) {
  throw Error('Keep browser reports outside the publishable site directory');
}
withBrowser(async (browser) => {
  await checkWorkbench(browser, root, reports);
  await checkExplorer(
    browser,
    path.join(root, 'task-explorer/index.html'),
    path.join(reports, 'explorer-qa.json'),
  );
  await checkCohesion(browser, root, reports);
  await checkPortability(browser, root, reports);
  await checkReview(browser, root, reports);
}).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
