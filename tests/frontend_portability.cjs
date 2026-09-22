/* A nested static host and modality URLs use the same portable publication. */
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const { serveDirectory } = require('../scripts/browser.cjs');

async function checkPortability(browser, directory, reportDirectory) {
  const temporary = await fs.mkdtemp(path.join(os.tmpdir(), 'tb3-frontend-nested-'));
  let server, context;
  try {
    await fs.cp(path.resolve(directory), path.join(temporary, 'nested/workbench'), {
      recursive: true,
    });
    server = await serveDirectory(temporary);
    const base = server.url + 'nested/workbench/';
    context = await browser.newContext({
      viewport: { width: 1360, height: 1000 },
      reducedMotion: 'reduce',
    });
    const errors = [],
      requests = [];
    await context.route('**/*', (route) => {
      const url = route.request().url();
      if (/^https?:/.test(url) && !url.startsWith(base)) {
        requests.push(url);
        return route.abort();
      }
      return route.continue();
    });
    const page = await context.newPage();
    page.on('pageerror', (error) => errors.push(error.message));
    await page.goto(base);
    await page.waitForSelector('.group-card');
    await page.locator('#task-explorer-link').click();
    await page.waitForSelector('.task-detail');
    const data = await page.locator('#data').textContent().then(JSON.parse);
    const matches = data.entries.filter(
      (entry) => entry.role === 'task' && entry.modalities.includes('mri'),
    );
    assert.ok(matches.length > 1);
    await page.locator('#modality').selectOption('mri');
    await page.waitForFunction(() => location.hash.includes('modality=mri'));
    assert.equal(await page.locator('[data-modality="mri"]').count(), 1);
    const filtered = page.url();
    await page.reload();
    await page.waitForSelector('.task-detail');
    assert.equal(await page.locator('#modality').inputValue(), 'mri');
    assert.equal(page.url(), filtered);
    const visibleDefinitions = await page
      .locator('[data-definition]')
      .evaluateAll((nodes) => nodes.map((node) => node.dataset.definition));
    assert.ok(visibleDefinitions.length);
    for (const id of visibleDefinitions) assert.ok(matches.some((entry) => entry.id === id));
    await page.locator('#modality').selectOption('ct');
    await page.waitForFunction(() => location.hash.includes('modality=ct'));
    await page.goBack();
    await page.waitForFunction(() => document.querySelector('#modality').value === 'mri');
    await page.locator('#reset-filters').click();
    assert.equal(await page.locator('#modality').inputValue(), '');
    assert.ok(!page.url().includes('modality='));
    assert.deepEqual(errors, []);
    assert.deepEqual(requests, []);
    const result = {
      nestedStaticPath: 'pass',
      modalityFilter: 'pass',
      reloadAndBack: 'pass',
      noExternalRequests: 'pass',
    };
    await fs.writeFile(
      path.join(reportDirectory, 'portability.json'),
      JSON.stringify(result, null, 2),
    );
    console.log(JSON.stringify(result));
  } finally {
    if (context) await context.close();
    if (server) await server.close();
    await fs.rm(temporary, { recursive: true, force: true });
  }
}
module.exports = { checkPortability };
