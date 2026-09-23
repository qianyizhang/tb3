/* Focused bilingual reading and declared source-language fallback in a portable site. */
const assert = require('node:assert/strict');
const { serveDirectory } = require('../scripts/browser.cjs');

async function checkLanguage(browser, directory) {
  const server = await serveDirectory(directory);
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  try {
    await page.goto(server.url + '?lang=zh-CN');
    await page.locator('.group-card').first().waitFor();
    assert.match(await page.locator('.translation-notice').first().innerText(), /英文原文/);
    const story = new URL(
      await page.locator('.group-card').first().getAttribute('href'),
      page.url(),
    );
    assert.equal(story.searchParams.get('lang'), 'zh-CN');
    await page.goto(story.href);
    assert.equal(await page.locator('#story-language').inputValue(), 'zh-CN');
    assert.equal(await page.locator('html').getAttribute('lang'), 'zh-CN');
    assert.equal(await page.locator('#story-translation-notice').isVisible(), false);
    assert.equal(await page.locator('[data-story-locale="zh-CN"] h1').isVisible(), true);
    assert.equal(
      new URL(await page.locator('.story-footer a').first().getAttribute('href')).searchParams.get(
        'lang',
      ),
      'zh-CN',
    );
    await page.locator('#story-language').selectOption('en');
    assert.equal(await page.locator('#story-translation-notice').isVisible(), false);
    assert.equal(new URL(page.url()).searchParams.get('lang'), 'en');
    assert.equal(
      new URL(await page.locator('.story-footer a').first().getAttribute('href')).searchParams.get(
        'lang',
      ),
      'en',
    );

    await page.goto(server.url + 'stories/longitudinal-reading.html?lang=zh-CN');
    assert.equal(await page.locator('html').getAttribute('lang'), 'zh-CN');
    assert.equal(await page.locator('#story-translation-notice').isVisible(), false);
    assert.match(await page.locator('[data-story-locale="zh-CN"] h1').innerText(), /跨访视变化/);
    await page.locator('#story-language').selectOption('en');
    assert.match(await page.locator('[data-story-locale="en"] h1').innerText(), /Read change/);

    await page.goto(server.url + 'task-explorer/index.html?lang=zh-CN#tb3-label-audit/0/brief');
    await page.locator('[data-brief="tb3-label-audit"]').waitFor();
    assert.match(await page.locator('.task-detail h2').innerText(), /审查已提供的解剖标签/);
    assert.equal(await page.locator('html').getAttribute('lang'), 'zh-CN');
    assert.match(await page.locator('.scene-play').innerText(), /暂停|播放/);
    assert.match(await page.locator('.scene-player .translation-notice').innerText(), /英文原文/);

    await page.goto(server.url + 'task-explorer/index.html?lang=zh-CN#tb3-airway-repair/0/brief');
    await page.locator('[data-brief="tb3-airway-repair"]').waitFor();
    assert.match(
      await page.locator('.task-detail > .detail-heading .translation-notice').innerText(),
      /英文原文/,
    );
    await page.locator('[data-tab="requirements"]').click();
    assert.equal(await page.locator('.requirements .box > [lang="en"]').count(), 4);

    await page.goto(server.url + 'task-explorer/index.html?lang=zh-CN#datasets/dataset-resect');
    await page.locator('[data-dataset="dataset-resect"]').waitFor();
    assert.match(await page.locator('.dataset-detail h1').innerText(), /术中超声/);
    assert.equal(await page.locator('.dataset-reference').getAttribute('open'), null);
    const download = await page.locator('#dataset-download').getAttribute('href');
    const metadata = JSON.parse(decodeURIComponent(download.split(',')[1]));
    assert.equal(metadata.dataset.id, 'dataset-resect');
    assert.equal(metadata.source_language, 'en');
    assert.equal(metadata.display_language, 'zh-CN');
    assert.equal(metadata.dataset.title, 'RESECT MRI and intraoperative ultrasound');
    assert.equal(metadata.dataset.locales['zh-CN'].title, 'RESECT MRI 与术中超声');

    await page.goto(server.url + 'task-explorer/index.html?lang=zh-CN#datasets/dataset-aeropath');
    await page.locator('[data-dataset="dataset-aeropath"]').waitFor();
    assert.match(await page.locator('.dataset-detail h1').innerText(), /气道/);
    assert.equal(await page.locator('.dataset-detail .translation-notice').count(), 0);
    assert.equal(await page.locator('.dataset-lead').getAttribute('lang'), null);
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(
      await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1),
      true,
    );
    assert.deepEqual(errors, []);
  } finally {
    await context.close();
    await server.close();
  }
}

module.exports = { checkLanguage };
if (require.main === module) {
  const { withBrowser } = require('../scripts/browser.cjs');
  withBrowser((browser) =>
    checkLanguage(browser, process.argv[2] || '.local/presentation-check'),
  ).catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}
