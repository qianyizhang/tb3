/* Browser checks against a fresh portable site. Loopback only; no restored scans needed. */
const { serveDirectory, withBrowser } = require('../presentation/tooling/browser.mts');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');

async function checkWorkbench(browser, directory, reportDirectory = directory) {
  const root = path.resolve(directory);
  const reports = path.resolve(reportDirectory);
  await fs.mkdir(reports, { recursive: true });
  const server = await serveDirectory(root);
  const base = server.url;
  let context;
  try {
    context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await context.newPage();
    const errors = [],
      remoteRequests = [];
    page.on('pageerror', (error) => errors.push(error.message));
    page.on('request', (request) => {
      if (/^https?:/.test(request.url()) && !request.url().startsWith(base))
        remoteRequests.push(request.url());
    });
    const data = JSON.parse(await fs.readFile(path.join(root, 'records.json'), 'utf8'));
    const groups = data.records.filter((row) => row.kind === 'group');
    await page.goto(base);
    await page.waitForFunction(
      (count) => document.querySelectorAll('.group-card').length === count,
      groups.length,
    );
    const explorerLink = new URL(
      await page.locator('#task-explorer-link').getAttribute('href'),
      page.url(),
    );
    assert.equal(explorerLink.pathname, '/task-explorer/index.html');
    assert.equal(explorerLink.searchParams.get('lang'), 'en');

    const target =
      data.records.find(
        (row) => row.kind === 'experiment' && row.current.assessment === 'not_assessed',
      ) || data.records.find((row) => row.kind === 'experiment');
    const status = 'assessment:' + target.current.assessment;
    await page.locator('#kind').selectOption('experiment');
    await page.locator('#group').selectOption(target.group_id);
    await page.locator('#status').selectOption(status);
    await page.locator('#search').fill(target.id);
    await page.locator(`[id="${target.id}"] > summary`).click();
    const query = new URL(page.url()).searchParams;
    for (const [key, value] of Object.entries({
      kind: 'experiment',
      group: target.group_id,
      status,
      q: target.id,
      record: target.id,
    }))
      assert.equal(query.get(key), value, key);
    await page.reload();
    await page.waitForFunction((id) => document.getElementById(id)?.open, target.id);
    assert.equal(await page.locator('#status').inputValue(), status);
    assert.equal(await page.locator('#search').inputValue(), target.id);
    await page.screenshot({ path: path.join(reports, 'workbench-desktop.png'), fullPage: true });

    // Filter changes have history entries, and Back restores the selected record.
    await page.locator('#group').selectOption('');
    await page.goBack();
    await page.waitForFunction(
      ({ id, group }) =>
        document.getElementById(id)?.open && document.querySelector('#group').value === group,
      { id: target.id, group: target.group_id },
    );
    await page.locator('#task-explorer-link').click();
    await page.waitForSelector('.task-detail');
    const home = page.locator('#workbench-home');
    assert.ok(await home.count(), 'Integrated Explorer has a usable home link');
    assert.equal(new URL(await home.first().getAttribute('href')).searchParams.get('lang'), 'en');
    await home.first().click();
    await page.waitForSelector('.group-card');

    // Closing an older open card must preserve the most recently selected one.
    const cards = page.locator('#records > details.record');
    const firstId = await cards.nth(0).getAttribute('id');
    const secondId = await cards.nth(1).getAttribute('id');
    await cards.nth(0).locator(':scope > summary').click();
    await cards.nth(1).locator(':scope > summary').click();
    await page.locator(`[id="${firstId}"] > summary`).click();
    assert.equal(new URL(page.url()).searchParams.get('record'), secondId);
    await page.reload();
    await page.waitForFunction((id) => document.getElementById(id)?.open, secondId);

    let chapterLinks = 0;
    for (const group of groups) {
      await page.goto(base + group.story_url);
      assert.equal(
        await page.locator('a[href*="/story.md"]').count(),
        0,
        'Chapter links stay rendered',
      );
      for (const href of await page
        .locator('a[href]')
        .evaluateAll((links) => links.map((link) => link.getAttribute('href')))) {
        const url = new URL(href, page.url());
        if (!url.pathname.startsWith('/stories/') || !url.pathname.endsWith('.html')) continue;
        chapterLinks++;
        const response = await page.request.get(url.href);
        assert.equal(response.status(), 200);
        if (url.hash)
          assert.ok(
            (await response.text()).includes(`id="${decodeURIComponent(url.hash.slice(1))}"`),
            'Chapter fragment exists',
          );
      }
    }
    assert.ok(chapterLinks > 0);
    await page.goto(base);
    await page.waitForSelector('.group-card');
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(
      await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),
      false,
    );
    await page.screenshot({ path: path.join(reports, 'workbench-mobile.png'), fullPage: false });
    assert.deepEqual(errors, []);
    assert.deepEqual(remoteRequests, []);
    const report = {
      groups: groups.length,
      chapterLinks,
      filterReloadAndBack: 'pass',
      selectedRecord: 'pass',
      multipleRecordClose: 'pass',
      explorerRoundTrip: 'pass',
      mobile: 'pass',
      pageErrors: errors,
      remoteRequests,
    };
    await fs.writeFile(
      path.join(reports, 'workbench-qa.json'),
      JSON.stringify(report, null, 2) + '\n',
    );
    console.log(JSON.stringify(report));
  } finally {
    try {
      if (context) await context.close();
    } finally {
      await server.close();
    }
  }
}

module.exports = { checkWorkbench };
if (require.main === module) {
  withBrowser((browser) =>
    checkWorkbench(browser, process.argv[2] || '.local/presentation-check'),
  ).catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}
