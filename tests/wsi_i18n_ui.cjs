/** Optional bilingual WSI browser check against freshly built local outputs. */
const assert = require('node:assert/strict');
const path = require('node:path');
const { serveDirectory, withBrowser } = require('../presentation/tooling/browser.mts');

const report = path.resolve(process.argv[2] || '/private/tmp/tb3-wsi-i18n.png');
const reportPage = (suffix) => report.replace(/\.png$/, '-' + suffix + '.png');

withBrowser(async (browser) => {
  const server = await serveDirectory('.local');
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  try {
    await page.goto(server.url + 'wsi-i18n-explorer.html?lang=en');
    await page.locator('[data-brief="wsi-camelyon-search"]').waitFor();
    assert.match(await page.locator('.task-detail h2').innerText(), /Find metastases/);
    assert.equal(await page.locator('html').getAttribute('lang'), 'en');
    await page.screenshot({ path: reportPage('explorer-en'), fullPage: true });
    await page.locator('.language-switch select').selectOption('zh-CN');
    assert.match(await page.locator('.task-detail h2').innerText(), /从全片找转移灶/);
    assert.match(page.url(), /lang=zh-CN/);
    await page.locator('[data-tab="sources"]').click();
    await page.getByRole('button', { name: '复制完整元数据' }).click();
    const copied = JSON.parse(await page.evaluate(() => navigator.clipboard.readText()));
    assert.equal(copied.task_id, 'wsi-camelyon-search');
    assert.ok(copied.sources.some((source) => source.sha256));
    await page.goto(server.url + 'wsi-i18n-explorer.html');
    assert.match(await page.locator('.task-detail h2').innerText(), /从全片找转移灶/);
    await page.locator('#datasets-home').click();
    await page.locator('[data-dataset-card="dataset-hiesd"]').click();
    assert.match(await page.locator('.dataset-detail h1').innerText(), /胃 ESD/);
    assert.equal(await page.locator('.dataset-reference').count(), 1);
    assert.equal(await page.locator('.dataset-reference').getAttribute('open'), null);
    assert.equal(await page.locator('.dataset-detail').locator('text=SHA-256').count(), 0);
    await page.screenshot({ path: report, fullPage: true });

    await page.goto(server.url + 'wsi-ground-truth/explainer/index.html?lang=en');
    await page.locator('#title').waitFor();
    assert.match(await page.locator('#title').innerText(), /Find metastases/);
    assert.equal(await page.locator('html').getAttribute('lang'), 'en');
    assert.equal(await page.locator('#overlay').isVisible(), false);
    await page.screenshot({ path: reportPage('tour-en'), fullPage: true });
    await page.locator('#reveal').click();
    assert.equal(await page.locator('#overlay').isVisible(), true);
    await page.locator('#language').selectOption('zh-CN');
    assert.match(await page.locator('#title').innerText(), /从全片找转移灶/);
    assert.equal(await page.locator('#overlay').isVisible(), true);
    assert.equal(await page.locator('html').getAttribute('lang'), 'zh-CN');
    await page.locator('#tabs button[data-key="tiger"]').click();
    await page.locator('#view').selectOption('1');
    await page.locator('#reveal').click();
    assert.equal(await page.locator('#layers').isVisible(), true);
    await page.locator('#cells').uncheck();
    assert.equal(await page.locator('#overlay2').isVisible(), false);
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(
      await page.locator('body').evaluate((body) => body.scrollWidth <= innerWidth + 1),
      true,
    );
    await page.screenshot({ path: reportPage('tour-mobile'), fullPage: true });
    const freshContext = await browser.newContext({ locale: 'zh-CN' });
    try {
      const freshPage = await freshContext.newPage();
      await freshPage.goto(server.url + 'wsi-i18n-explorer.html');
      assert.match(await freshPage.locator('.task-detail h2').innerText(), /从全片找转移灶/);
    } finally {
      await freshContext.close();
    }
    assert.deepEqual(errors, []);
    console.log('WSI bilingual Explorer and tour passed');
  } finally {
    await context.close();
    await server.close();
  }
}).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
