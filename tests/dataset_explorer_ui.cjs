/** Dataset navigation regression; no external requests or native data reads. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { withBrowser } = require('../presentation/tooling/browser.mts');

withBrowser(async (browser) => {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
  const errors = [],
    requests = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('request', (r) => {
    if (/^https?:/.test(r.url())) requests.push(r.url());
  });
  await page.goto(pathToFileURL(path.resolve(process.argv[2])).href);
  await page.locator('#datasets-home').click();
  await page.waitForSelector('.dataset-intro');
  const data = await page.evaluate(() => JSON.parse(document.querySelector('#data').textContent));
  assert.equal(await page.locator('.dataset-cards>a').count(), data.datasets.records.length);
  for (const d of data.datasets.records) {
    await page.evaluate((id) => {
      location.hash = 'datasets/' + id;
    }, d.id);
    await page.waitForFunction(
      (id) => document.querySelector('.dataset-detail')?.dataset.dataset === id,
      d.id,
    );
    assert.equal(await page.locator('.dataset-sample').count(), d.sample_sets.length);
    assert.equal(await page.locator('.dataset-diagram').count(), 1);
    assert.equal(await page.locator('.dataset-reference[open]').count(), 0);
    const snapshot = data.datasets.previews[d.id];
    assert(snapshot, 'Every dataset has a frozen sample or explicit acquisition gap');
    assert.equal(await page.locator('.dataset-snapshot').count(), 1);
    assert.equal(
      await page.locator('.dataset-snapshot').getAttribute('data-snapshot-status'),
      snapshot.status,
    );
    assert.equal(await page.locator('.snapshot-panel').count(), snapshot.panels.length);
    if (snapshot.panels.some((p) => p.role === 'reference')) {
      await page.locator('.dataset-reference summary').click();
      assert.equal(await page.locator('.dataset-reference[open]').count(), 1);
    }
    for (const img of await page.locator('.snapshot-image img').all()) {
      await img.scrollIntoViewIfNeeded();
      await img.evaluate((el) => el.decode());
      assert(await img.evaluate((el) => el.naturalWidth > 0));
    }
    assert.equal(await page.locator('.dataset-task-links>a').count(), d.task_ids.length);
    for (const link of await page.locator('.dataset-task-links>a').all()) {
      const href = await link.getAttribute('href');
      assert(data.entries.some((e) => href === '#' + e.id + '/0/overview'));
    }
  }
  await page.evaluate(() => {
    location.hash = 'datasets/dataset-resect';
  });
  await page.waitForSelector('[data-dataset="dataset-resect"]');
  assert((await page.locator('.snapshot-image img').count()) > 0);
  await page.locator('.dataset-reference summary').click();
  assert.equal(await page.locator('.dataset-reference[open]').count(), 1);
  await page.reload();
  await page.waitForSelector('[data-dataset="dataset-resect"]');
  assert.equal(await page.locator('.dataset-reference[open]').count(), 0);
  await page.locator('[data-snapshot-enlarge]').first().click();
  assert.equal(await page.locator('#dataset-image-dialog[open]').count(), 1);
  await page.locator('#snapshot-zoom').fill('200');
  assert.equal(await page.locator('#snapshot-large').evaluate((el) => el.style.width), '200%');
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('#dataset-image-dialog[open]').count(), 0);
  await page.locator('#dataset-search').fill('F_018');
  assert.equal(await page.locator('#dataset-nav>a').count(), 1);
  assert.match(await page.locator('#dataset-nav').innerText(), /ToothFairy3/);
  await page.locator('#dataset-search').fill('no-such-sample-xyz');
  assert.match(await page.locator('#dataset-nav').innerText(), /No matching/);
  await page.locator('.dataset-task-links>a').first().click();
  await page.waitForSelector('.task-detail');
  assert.equal(await page.locator('body.dataset-mode').count(), 0);
  assert((await page.locator('.dataset-links a').count()) > 0);
  await page.locator('.dataset-links a[href="#datasets/dataset-resect"]').click();
  await page.waitForSelector('[data-dataset="dataset-resect"]');
  await page.goBack();
  await page.waitForSelector('.task-detail');
  await page.goForward();
  await page.waitForSelector('[data-dataset="dataset-resect"]');
  await page.screenshot({ path: '.local/dataset-explorer/desktop.png', fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => {
    location.hash = 'datasets/dataset-toothfairy3';
  });
  await page.waitForSelector('[data-dataset="dataset-toothfairy3"]');
  assert(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1),
    'No mobile horizontal overflow',
  );
  await page.screenshot({ path: '.local/dataset-explorer/mobile.png', fullPage: true });
  await page.evaluate(() => {
    location.hash = 'datasets/not-a-dataset';
  });
  await page.waitForSelector('#dataset-content h1');
  assert.equal(await page.locator('#dataset-content h1').innerText(), 'Dataset not found');
  assert.deepEqual(errors, []);
  assert.deepEqual(requests, []);
  const result = {
    datasets: data.datasets.records.length,
    sample_sets: data.datasets.coverage.sample_sets,
    experiments: data.datasets.coverage.experiments,
    errors,
    external_requests: requests,
    mobile: 'passed',
    navigation: 'passed',
    reveal: 'passed',
    frozen_snapshots: Object.keys(data.datasets.previews).length,
    image_decode: 'all rendered sample and reference images passed',
    enlargement: 'zoom and keyboard dismissal passed',
  };
  fs.writeFileSync(process.argv[3], JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result));
});
