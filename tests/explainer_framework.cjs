/** Selected offline closure, shared controls/capture, design variants and nested served loading. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { withBrowser, serveDirectory } = require('../presentation/tooling/browser.mts');
const { runPython } = require('../presentation/tooling/python.mts');
const root = path.resolve(__dirname, '..');
const output = path.resolve(process.argv[2] || '.local/explainer-framework-check');
const definitions = JSON.parse(
  fs.readFileSync(path.join(root, 'presentation/explainers/restoration.json')),
).definitions;
const stories = Object.values(definitions).map(({ pack }) => {
  const index = JSON.parse(
    fs.readFileSync(path.join(root, 'presentation/assets/teaching-prefabs.json')),
  );
  return path.basename(path.dirname(index.packs[pack].manifest));
});
fs.mkdirSync(output, { recursive: true });
for (const story of stories)
  runPython(root, [
    '-m',
    'tb3_medical.cli',
    'story',
    'build',
    story,
    '--output',
    path.join(output, story),
  ]);
runPython(root, [
  '-m',
  'tb3_medical.cli',
  'brief',
  'build',
  '--delivery',
  'served',
  '--output',
  path.join(output, 'served/nested/catalogue/index.html'),
]);

withBrowser(async (browser) => {
  const context = await browser.newContext({
    viewport: { width: 1280, height: 1050 },
    reducedMotion: 'reduce',
  });
  await context.addInitScript(() => {
    const original = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (type, ...args) {
      return type === 'webgl' || type === 'webgl2' ? null : original.call(this, type, ...args);
    };
  });
  const page = await context.newPage();
  const errors = [],
    requests = [],
    sizes = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await context.route('https://**/*', (route) => route.abort());
  page.on('request', (request) => {
    if (/^https?:/.test(request.url())) requests.push(request.url());
  });
  try {
    for (const story of stories) {
      const directory = path.join(output, story);
      const url = pathToFileURL(path.join(directory, 'index.html')).href;
      const plan = JSON.parse(fs.readFileSync(path.join(directory, 'plan.json')));
      const receipt = JSON.parse(fs.readFileSync(path.join(directory, 'package.json')));
      assert.equal(receipt.delivery, 'selected-offline');
      assert.ok(receipt.html_bytes < 1_000_000, 'Symbolic selected HTML must stay below 1 MB');
      assert.equal(receipt.assets.length, 6);
      assert.ok(receipt.assets.every((asset) => asset.path.includes('/' + story + '/')));
      assert.ok(
        !receipt.modules.some((name) => /task-explorer\//.test(name)),
        'No eager scientific asset modules in selected renderer',
      );
      sizes.push({ story, bytes: receipt.html_bytes, gzip: receipt.gzip_bytes });
      await page.goto(url + '?review=1');
      await page.locator('[data-family="restoration-protocol"][data-rendered="true"]').waitFor();
      assert.equal(await page.locator('canvas,img,svg').count(), 0, 'No invented native image');
      assert.equal(await page.locator('[data-reader-evidence]').getAttribute('open'), null);
      for (let index = 0; index < plan.beats.length; index++) {
        await page.locator(`[data-story-step="${index}"]`).click();
        assert.equal(
          await page.locator('.scene-player').getAttribute('data-committed-frame'),
          String(plan.beats[index].startFrame),
        );
        assert.equal(
          await page.locator('[data-scene-title]').innerText(),
          plan.beats[index].caption,
        );
        await page.screenshot({
          path: path.join(directory, `chapter-${index}.png`),
          fullPage: true,
        });
      }
      await page.getByRole('button', { name: 'Reveal source metric rules', exact: true }).click();
      assert.equal(await page.getByRole('group', { name: 'Metric rule' }).count(), 1);
      await page.locator('[data-story-step="3"]').click();
      assert.equal(await page.getByRole('group', { name: 'Metric rule' }).count(), 0);
      await page.getByRole('button', { name: 'Inspect format contract', exact: true }).click();
      await page.getByRole('button', { name: 'Actually checked', exact: true }).click();
      await page.locator('[data-story-step="2"]').click();
      for (let step = 0; step < 4; step++) {
        await page.locator(`[data-restoration-step="${step}"]`).click();
        assert.equal(
          await page
            .locator('[data-restoration-currentstep]')
            .getAttribute('data-restoration-currentstep'),
          String(step),
        );
      }
      await page.locator('[data-story-step="1"]').click();
      await page.getByRole('button', { name: 'Standard', exact: true }).click();
      await page.locator('.scene-reset').click();
      await page.locator('[data-story-step="1"]').click();
      assert.equal(
        await page.getByRole('button', { name: 'Lite', exact: true }).getAttribute('aria-pressed'),
        'true',
      );
      const frame = await page.locator('.scene-player').getAttribute('data-committed-frame');
      for (const variant of ['Compare', 'Focus', 'Guided']) {
        await page.getByRole('button', { name: variant, exact: true }).click();
        assert.equal(
          await page.locator('.scene-player').getAttribute('data-committed-frame'),
          frame,
          'Changing layout does not fork the player',
        );
        await page.screenshot({
          path: path.join(directory, variant.toLowerCase() + '.png'),
          fullPage: true,
        });
      }
      await page.setViewportSize({ width: 390, height: 844 });
      for (let index = 0; index < plan.beats.length; index++) {
        await page.locator(`[data-story-step="${index}"]`).click();
        assert.equal(
          await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),
          false,
        );
      }
      await page.screenshot({ path: path.join(directory, 'mobile.png'), fullPage: true });
      await page.goto(url + '?lang=zh-CN');
      await page.locator('.scene-language-note').waitFor();
      assert.match(await page.locator('.scene-play').innerText(), /播放/);
      await page.setViewportSize({ width: 1280, height: 720 });
      await page.goto(url + '?capture=1&layout=focus');
      await page.evaluate(() => window.__tb3ExplainerCapture.ready);
      assert.equal(
        await page.locator('.scene-player').getAttribute('data-reader-variant'),
        'guided',
      );
      for (let index = 0; index < plan.beats.length; index++) {
        await page.evaluate(
          ({ frame, fps }) =>
            window.__tb3ExplainerCapture.seekFrame({ frame, fps, width: 1280, height: 720 }),
          { frame: plan.beats[index].startFrame, fps: plan.fps },
        );
        assert.equal(
          await page.locator('.scene-player').getAttribute('data-committed-frame'),
          String(plan.beats[index].startFrame),
        );
        const bounds = await page.locator('[data-restoration-stage]').boundingBox();
        assert.ok(
          bounds.y + bounds.height <= 720,
          `${story}/${index}: canonical protocol content fits the capture (${bounds.y + bounds.height}px)`,
        );
        await page.screenshot({ path: path.join(directory, `capture-${index}.png`) });
      }
      const last = plan.beats.at(-1).startFrame;
      await page.getByRole('button', { name: 'Reveal source metric rules', exact: true }).click();
      await page.evaluate(
        ({ frame, fps }) =>
          window.__tb3ExplainerCapture.seekFrame({ frame, fps, width: 1280, height: 720 }),
        { frame: last, fps: plan.fps },
      );
      assert.equal(
        await page.getByRole('group', { name: 'Metric rule' }).count(),
        0,
        'Canonical capture resets reader-only reveals even at the same frame',
      );
      await page.setViewportSize({ width: 1280, height: 1050 });
    }
    assert.deepEqual(requests, [], 'Every selected file works without any network request');
    const server = await serveDirectory(path.join(output, 'served'));
    try {
      await page.goto(server.url + 'nested/catalogue/index.html#' + stories[0] + '/0/overview');
      await page.locator('[data-family="restoration-protocol"][data-rendered="true"]').waitFor();
      const modules = requests.filter((url) => /\.(js|mjs)$/.test(url));
      assert.ok(
        !modules.some((url) => /TaskVisual-|LegacyWarning-|story-recipes-/.test(url)),
        'Migrated entry does not load legacy visual packs',
      );
      assert.equal(
        requests.filter((url) => url.endsWith('.json')).length,
        1,
        'Only selected story is fetched',
      );
      await page.evaluate((id) => {
        location.hash = id + '/0/overview';
      }, stories[1]);
      await page.locator(`[data-recipe="${Object.keys(definitions)[1]}"]`).waitFor();
      await page.goBack();
      await page.locator(`[data-recipe="${Object.keys(definitions)[0]}"]`).waitFor();
      await page.screenshot({ path: path.join(output, 'served.png'), fullPage: true });
      const failure = await context.newPage();
      await failure.route('**/assets/*.json', (route) =>
        route.fulfill({ status: 404, body: 'missing' }),
      );
      await failure.goto(server.url + 'nested/catalogue/index.html#' + stories[0] + '/0/overview');
      await failure.getByRole('alert').waitFor();
      assert.match(await failure.getByRole('alert').innerText(), /could not load/);
      assert.equal(await failure.locator('.detail-heading').isVisible(), true);
      await failure.close();
    } finally {
      await server.close();
    }
    assert.deepEqual(errors, []);
    fs.writeFileSync(
      path.join(output, 'report.json'),
      JSON.stringify({ stories: stories.length, variants: 3, sizes, requests, errors }, null, 2) +
        '\n',
    );
    console.log(
      'PASS: four restoration stories; three layouts; offline/no-GPU, mobile, locale, control resets, capture and nested served loading',
    );
  } finally {
    await context.close();
  }
}).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
