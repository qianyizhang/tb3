/* Cross-page navigation and responsive discovery in a fresh portable site. */
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { serveDirectory } = require('../scripts/browser.cjs');

async function checkCohesion(browser, directory, reportDirectory) {
  const root = path.resolve(directory);
  const reports = path.resolve(reportDirectory);
  await fs.mkdir(reports, { recursive: true });
  const server = await serveDirectory(root);
  const base = server.url;
  const errors = [],
    remoteRequests = [],
    failedResponses = [];
  let context;
  try {
    context = await browser.newContext({
      viewport: { width: 1440, height: 1000 },
      reducedMotion: 'reduce',
    });
    await context.route('**/*', (route) => {
      const url = route.request().url();
      if (/^https?:/.test(url) && !url.startsWith(base)) {
        remoteRequests.push(url);
        return route.abort();
      }
      return route.continue();
    });
    const page = await context.newPage();
    page.on('pageerror', (error) => errors.push(error.message));
    page.on('response', (response) => {
      if (response.status() >= 400) failedResponses.push(`${response.status()} ${response.url()}`);
    });
    const activeNavigation = async (label) => {
      const navigation = page.locator('.site-header .site-nav');
      assert.deepEqual(await navigation.locator('a').allTextContents(), [
        'Overview',
        'Tasks',
        'Datasets',
      ]);
      assert.equal(await navigation.locator('[aria-current="page"]').count(), 1);
      assert.equal(await navigation.locator('[aria-current="page"]').innerText(), label);
    };
    const noOverflow = async (name) => {
      assert.equal(
        await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),
        false,
        `${name} stays within the viewport`,
      );
    };
    const screenshot = async (name) => {
      await page.evaluate(() => scrollTo(0, 0));
      await noOverflow(name);
      await page.screenshot({ path: path.join(reports, name + '.png'), fullPage: false });
    };
    const skipToContent = async () => {
      const previousUrl = page.url();
      const detail = page.locator('.task-detail');
      const previousBrief = (await detail.count()) ? await detail.getAttribute('data-brief') : null;
      await page.locator('.skip-link').focus();
      await page.keyboard.press('Enter');
      assert.equal(page.url(), previousUrl, 'Skipping to content preserves the selected route');
      assert.equal(
        await page.locator('#main').evaluate((node) => node === document.activeElement),
        true,
      );
      if (previousBrief) {
        assert.equal(await page.locator('.task-detail').getAttribute('data-brief'), previousBrief);
      }
    };
    const visibleTaskFocus = async () => {
      await page.waitForFunction(
        () => {
          const node = document.activeElement;
          return (
            node &&
            node !== document.body &&
            node.getClientRects().length > 0 &&
            !node.closest('[hidden]') &&
            (node.id === 'browse-toggle' || node.closest('#main, #task-browser'))
          );
        },
        null,
        { timeout: 5000 },
      );
      assert.equal(await page.locator(':focus').isVisible(), true, 'Task focus stays visible');
    };

    await page.goto(base);
    await page.waitForSelector('.group-card');
    await activeNavigation('Overview');
    await screenshot('home-desktop');
    assert.equal(
      await page.locator('#task-explorer-link').getAttribute('href'),
      'task-explorer/index.html',
    );

    // A search dead end should have a direct escape that clears every active filter.
    const group = await page.locator('#group option').nth(1).getAttribute('value');
    await page.locator('#group').selectOption(group);
    await page.locator('#kind').selectOption('experiment');
    await page.locator('#status').selectOption('attention');
    await page.locator('#search').fill('no-record-can-match-cohesion-check-9bfe');
    await page.locator('#empty').waitFor({ state: 'visible' });
    await page
      .locator('#empty')
      .getByRole('button', { name: /reset|clear/i })
      .click();
    for (const [id, expected] of Object.entries({
      search: '',
      group: '',
      kind: 'overview',
      status: '',
    })) {
      assert.equal(await page.locator('#' + id).inputValue(), expected, `${id} resets`);
    }
    assert.ok((await page.locator('#records > details.record').count()) > 0);
    assert.equal(await page.locator('#empty').isVisible(), false);
    assert.equal(new URL(page.url()).search, '');

    await page.locator('#task-explorer-link').click();
    await page.waitForSelector('.task-detail');
    await activeNavigation('Tasks');
    await screenshot('explorer-desktop');
    await page.locator('[data-tab="requirements"]').click();
    const selectedBrief = await page.locator('.task-detail').getAttribute('data-brief');
    const selectedRoute = new URL(page.url()).hash;
    await skipToContent();
    await page.locator('#datasets-home').click();
    await page.waitForSelector('.dataset-intro');
    await activeNavigation('Datasets');
    assert.equal(new URL(page.url()).hash, '#datasets');
    await screenshot('datasets-desktop');
    await skipToContent();
    assert.equal(await page.locator('#tasks-home').getAttribute('href'), selectedRoute);

    // Searching must filter the visible overview, as well as the source navigation.
    const cards = page.locator('.dataset-cards > a:visible');
    const sourceCount = await cards.count();
    assert.ok(sourceCount > 1, 'The dataset collection contains multiple sources');
    const firstTitle = await cards.first().locator('h2').innerText();
    const firstHref = await cards.first().getAttribute('href');
    await page.locator('#dataset-search').fill(firstTitle);
    const matches = await cards.count();
    assert.ok(matches > 0 && matches < sourceCount, 'Dataset search narrows overview cards');
    assert.equal(await page.locator('#dataset-nav > a').count(), matches);
    assert.ok(
      (await cards.evaluateAll((links) => links.map((link) => link.getAttribute('href')))).includes(
        firstHref,
      ),
    );
    await page.locator('#dataset-search').fill('no-dataset-can-match-cohesion-check-9bfe');
    assert.equal(await cards.count(), 0);
    assert.equal(await page.locator('#dataset-empty').isVisible(), true);
    await page.locator('#dataset-clear-search').click();
    assert.equal(await page.locator('#dataset-search').inputValue(), '');
    assert.equal(await page.locator('#dataset-empty').isVisible(), false);
    assert.equal(await cards.count(), sourceCount);

    await page.locator('#tasks-home').click();
    await page.waitForSelector('.task-detail');
    await activeNavigation('Tasks');
    assert.equal(await page.locator('.task-detail').getAttribute('data-brief'), selectedBrief);
    assert.equal(new URL(page.url()).hash, selectedRoute);
    assert.equal(
      await page.locator('[data-tab="requirements"]').getAttribute('aria-selected'),
      'true',
    );
    await page.locator('#workbench-home').click();
    await page.waitForSelector('.group-card');
    await activeNavigation('Overview');

    // These captures use the ordinary landing pages, without filtered or expanded UI.
    await page.setViewportSize({ width: 390, height: 844 });
    await screenshot('home-mobile');
    await page.locator('#task-explorer-link').click();
    await page.waitForSelector('.task-detail');
    const mobileLandingUrl = page.url();
    const mobilePicker = page.locator('#mobile-task-picker');
    assert.equal(await mobilePicker.isVisible(), true);
    const currentMobileTask = await mobilePicker.inputValue();
    const otherMobileTask = await mobilePicker
      .locator('option')
      .evaluateAll(
        (options, selected) =>
          options.find((option) => !option.disabled && option.value !== selected)?.value,
        currentMobileTask,
      );
    assert.ok(otherMobileTask, 'The mobile picker offers another task in this collection');
    await mobilePicker.selectOption(otherMobileTask);
    await page.waitForFunction(
      (id) => document.querySelector('.task-detail')?.dataset.brief === id,
      otherMobileTask,
    );
    const mobileTaskRoute = new URL(page.url()).hash;
    assert.equal(decodeURIComponent(mobileTaskRoute.slice(1).split('/')[0]), otherMobileTask);
    await noOverflow('Mobile task picker');
    await page.reload();
    await page.waitForFunction(
      (id) => document.querySelector('.task-detail')?.dataset.brief === id,
      otherMobileTask,
    );
    assert.equal(await mobilePicker.inputValue(), otherMobileTask);
    assert.equal(new URL(page.url()).hash, mobileTaskRoute);
    await page.goto(mobileLandingUrl);
    await page.waitForSelector('.task-detail');
    await screenshot('explorer-mobile');
    const browse = page.locator('#browse-toggle');
    assert.equal(await browse.isVisible(), true);
    assert.equal(await browse.getAttribute('aria-expanded'), 'false');
    assert.equal(await page.locator('#task-browser').isVisible(), false);
    await browse.click();
    assert.equal(await browse.getAttribute('aria-expanded'), 'true');
    assert.equal(await page.locator('#task-browser').isVisible(), true);
    assert.equal(
      await page.locator('#search').evaluate((node) => node === document.activeElement),
      true,
    );
    await noOverflow('Expanded mobile task browser');
    await page.locator('#search').fill('no-task-can-match-cohesion-check-9bfe');
    await page.locator('#main [data-reset-filters]').waitFor({ state: 'visible' });
    await browse.click();
    assert.equal(await browse.getAttribute('aria-expanded'), 'false');
    assert.equal(await page.locator('#task-browser').isVisible(), false);
    await page.locator('#main [data-reset-filters]').click();
    await page.locator('.task-detail[data-brief]').waitFor({ state: 'visible' });
    assert.equal(await page.locator('#search').inputValue(), '');
    await visibleTaskFocus();

    // A responsive sidebar must not strand keyboard focus when it becomes hidden.
    if ((await browse.getAttribute('aria-expanded')) === 'true') await browse.click();
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.locator('#search').waitFor({ state: 'visible' });
    await page.locator('#search').focus();
    await page.setViewportSize({ width: 390, height: 844 });
    await page.locator('#task-browser').waitFor({ state: 'hidden' });
    await visibleTaskFocus();
    await page.locator('#datasets-home').click();
    await page.waitForSelector('.dataset-intro');
    await activeNavigation('Datasets');
    await screenshot('datasets-mobile');
    assert.equal(await browse.isVisible(), false);

    const data = JSON.parse(await fs.readFile(path.join(root, 'records.json'), 'utf8'));
    const story = data.records.find((record) => record.kind === 'group' && record.story_url);
    if (story) {
      await page.setViewportSize({ width: 1440, height: 1000 });
      await page.goto(new URL(story.story_url, base).href);
      await activeNavigation('Overview');
      await screenshot('story-desktop');
    }
    assert.deepEqual(errors, []);
    assert.deepEqual(remoteRequests, []);
    assert.deepEqual(failedResponses, []);
    const report = {
      primaryNavigation: 'pass',
      filterRecovery: 'pass',
      selectedTaskReturn: 'pass',
      skipLinkPreservesRoute: 'pass',
      datasetSearch: 'pass',
      mobileDisclosure: 'pass',
      mobileTaskPicker: 'pass',
      mobileFocusRecovery: 'pass',
      responsiveScreenshots: 'pass',
      pageErrors: errors,
      remoteRequests,
      failedResponses,
    };
    await fs.writeFile(
      path.join(reports, 'cohesion-qa.json'),
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

module.exports = { checkCohesion };
