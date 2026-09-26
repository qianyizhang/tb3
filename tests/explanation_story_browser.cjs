/** Integrated production witnesses; invoke outside the macOS browser sandbox. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { pathToFileURL } = require('node:url');
const { withBrowser } = require('../presentation/tooling/browser.mts');
const { captureComposedFrame } = require('../presentation/tooling/media/capture.mts');
const folder = path.resolve(process.argv[2]),
  explorer = path.resolve(process.argv[3]);
const plan = JSON.parse(fs.readFileSync(path.join(folder, 'plan.json'), 'utf8'));
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');
const report = { production: [], simulated: [], errors: [], browser: null };
withBrowser(async (browser) => {
  report.browser = browser.version();
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    deviceScaleFactor: 1,
    reducedMotion: 'reduce',
  });
  await context.route(/^https?:/, (route) => {
    report.errors.push('remote ' + route.request().url());
    return route.abort();
  });
  const page = await context.newPage();
  page.on('pageerror', (e) => report.errors.push(e.message));
  await page.goto(pathToFileURL(path.join(folder, 'index.html')).href + '?capture=1');
  await page.waitForFunction(() => window.__tb3ExplainerCapture);
  const capture = (frame) =>
    captureComposedFrame(page, { frame, fps: plan.fps, width: 1280, height: 720 });
  const frames = [
    ...new Set([0, 791, 350, 530, ...plan.beats.flatMap((b) => [b.startFrame, b.endFrame - 1])]),
  ];
  const witnesses = {};
  for (const frame of frames) {
    const bytes = await capture(frame);
    witnesses[frame] = sha(bytes);
    fs.writeFileSync(path.join(folder, `seek-${frame}.png`), bytes);
    const beat = plan.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);
    assert.equal(await page.locator('[data-scene-title]').innerText(), beat.caption);
    assert.equal(await page.locator('.scene-player').getAttribute('data-playing'), 'false');
    assert.ok((await page.locator('.scene-annotation').count()) >= 2);
    assert.ok((await page.locator('.scene-leaders path').count()) >= 2);
  }
  const pixelComparisons = [];
  for (const frame of [...frames].reverse()) {
    const bytes = await capture(frame);
    fs.writeFileSync(path.join(folder, `repeat-${frame}.png`), bytes);
    if (sha(bytes) !== witnesses[frame]) {
      const difference = await page.evaluate(
        async ([first, second]) => {
          const pixels = async (raw) => {
            const img = new Image();
            img.src = 'data:image/png;base64,' + raw;
            await img.decode();
            const c = document.createElement('canvas');
            c.width = 1280;
            c.height = 720;
            const ctx = c.getContext('2d');
            ctx.drawImage(img, 0, 0);
            return ctx.getImageData(0, 0, 1280, 720).data;
          };
          const a = await pixels(first),
            b = await pixels(second);
          let count = 0,
            max = 0;
          for (let i = 0; i < a.length; i += 4) {
            let changed = false;
            for (let j = 0; j < 3; j++) {
              const d = Math.abs(a[i + j] - b[i + j]);
              max = Math.max(max, d);
              changed ||= d > 0;
            }
            if (changed) count++;
          }
          return { count, max };
        },
        [
          fs.readFileSync(path.join(folder, `seek-${frame}.png`)).toString('base64'),
          bytes.toString('base64'),
        ],
      );
      pixelComparisons.push({ frame, ...difference });
      assert.ok(
        difference.count <= 16 && difference.max <= 8,
        `Repeat seek ${frame}: ${JSON.stringify(difference)}`,
      );
    }
  }
  report.production.push({
    absolute_seek: 'all boundaries plus mid-beat / final paused / reverse order',
    png_equality:
      'at most 16 of 921600 pixels differ; max 8/255 channel delta (DOM raster edge tolerance)',
    pixelComparisons,
    frames: witnesses,
  });
  await assert.rejects(() => capture(-1));
  await assert.rejects(() => capture(plan.durationFrames));
  await page.goto(pathToFileURL(explorer).href + '?lang=en#ours/0/overview?view=repository');
  await page.locator('.scene-player[data-rendered="true"]').waitFor();
  assert.equal(await page.evaluate(() => typeof window.__tb3ExplainerCapture), 'undefined');
  assert.equal(await page.locator('.scene-player').getAttribute('data-playing'), 'false');
  const payload = await page.evaluate(() =>
    JSON.parse(document.querySelector('#data').textContent),
  );
  const selected = [
    payload.entries.find((e) => e.illustration?.kind === 'cardiac_material'),
    payload.entries.find((e) => e.id === 'tb3-ct-organ-segmentation'),
    payload.entries.find((e) => e.illustration?.kind === 'report'),
  ].filter(Boolean);
  assert.equal(selected.length, 3);
  async function select(id) {
    await page.evaluate((id) => {
      location.hash = `${id}/0/overview?view=repository`;
    }, id);
    await page.waitForFunction(
      (id) => document.querySelector('.task-detail')?.dataset.brief === id,
      id,
    );
  }
  const resources = [];
  for (let i = 0; i < 4; i++) {
    for (const entry of selected) {
      await select(entry.id);
      await page.locator('.task-scene-host > [data-scene]').waitFor();
    }
    await select('ours');
    await page.locator('.scene-player[data-rendered="true"]').waitFor();
    await page.locator('[data-scene-step="4"]').click();
    resources.push(
      await page.locator('.scene-player').evaluate((e) => ({
        roots: e.dataset.nativeRoots,
        geometry: e.dataset.gpuGeometries,
        canvases: e.querySelectorAll('canvas').length,
      })),
    );
  }
  resources.forEach((r) => assert.deepEqual(r, resources[0]));
  assert.equal(resources[0].roots, '1');
  assert.equal(resources[0].canvases, 1);
  report.production.push({ task_switches: 4, legacy: selected.map((e) => e.id), resources });
  const canvas = page.locator('.scene-canvas');
  await canvas.focus();
  await page.keyboard.press('ArrowRight');
  await page.getByRole('button', { name: 'Reset illustration view', exact: true }).click();
  assert.equal(await page.locator('.scene-player').getAttribute('data-frame'), '0');
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator('.scene-player').scrollIntoViewIfNeeded();
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
  await page.locator('.scene-player').screenshot({ path: path.join(folder, 'mobile.png') });
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.locator('[data-scene-step="3"]').click();
  await canvas.scrollIntoViewIfNeeded();
  await page.getByRole('button', { name: 'Play animation', exact: true }).click();
  await page.waitForFunction(
    () => document.querySelector('.scene-player').dataset.playing === 'true',
  );
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.evaluate(() => new Promise(requestAnimationFrame));
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.waitForFunction(
    () => document.querySelector('.scene-player').dataset.playing === 'false',
    undefined,
    { timeout: 2000 },
  );
  assert.ok(Number(await page.locator('.scene-player').getAttribute('data-frame')) < 791);
  report.production.push(
    'paused load, keyboard orbit/reset, 390px no overflow, reduced-motion change pauses',
  );
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.locator('[data-scene-step="3"]').click();
  await canvas.scrollIntoViewIfNeeded();
  await page.getByRole('button', { name: 'Play animation', exact: true }).click();
  await page.waitForFunction(
    () => Number(document.querySelector('.scene-player').dataset.frame) > 432,
  );
  await page.evaluate(() => scrollTo(0, 0));
  await page.waitForFunction(
    () => document.querySelector('.scene-canvas').getBoundingClientRect().top > innerHeight,
  );
  await page.waitForTimeout(150);
  const offscreen = await page.locator('.scene-player').getAttribute('data-frame');
  await page.waitForTimeout(150);
  assert.equal(await page.locator('.scene-player').getAttribute('data-frame'), offscreen);
  await canvas.scrollIntoViewIfNeeded();
  await page.waitForFunction(
    (frame) => Number(document.querySelector('.scene-player').dataset.frame) > Number(frame),
    offscreen,
  );
  report.production.push('Scripted playback suspends offscreen and resumes on return');
  await page.evaluate(() => {
    Object.defineProperty(document, 'hidden', { configurable: true, get: () => true });
    document.dispatchEvent(new Event('visibilitychange'));
  });
  const hiddenFrame = await page.locator('.scene-player').getAttribute('data-frame');
  await page.waitForTimeout(150);
  assert.equal(await page.locator('.scene-player').getAttribute('data-frame'), hiddenFrame);
  await page.evaluate(() => {
    delete document.hidden;
    document.dispatchEvent(new Event('visibilitychange'));
  });
  report.simulated.push(
    'document.hidden visibility-change event suspends the shared story clock; physical tab hiding is not claimed',
  );

  await page.goto(pathToFileURL(explorer).href + '?lang=zh-CN#ours/0/overview?view=repository');
  await page.locator('.scene-player[data-rendered="true"]').waitFor();
  assert.ok(await page.getByRole('button', { name: '播放动画', exact: true }).count());
  assert.match(await page.locator('.scene-language-note').innerText(), /英文/);
  await page.locator('.scene-player').screenshot({ path: path.join(folder, 'chinese.png') });
  report.production.push('Chinese controls and explicit English source-copy note');
  await page.evaluate(() => {
    const gl = document.querySelector('.scene-canvas').getContext('webgl2');
    gl.getExtension('WEBGL_lose_context').loseContext();
  });
  await page.locator('.scene-fallback:not([hidden])').waitFor();
  assert.ok(await page.locator('.scene-fallback img').count());
  await page.locator('.scene-notes').last().locator('summary').click();
  assert.match(await page.locator('.scene-notes').last().innerText(), /The real task still needs/);
  report.simulated.push('WEBGL_lose_context: derived fixture poster and canonical transcript');
  const noGpu = await context.newPage();
  await noGpu.addInitScript(() => {
    const original = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (kind, ...args) {
      return kind === 'webgl2' ? null : original.call(this, kind, ...args);
    };
  });
  await noGpu.goto(pathToFileURL(explorer).href + '?lang=en#ours/0/overview?view=repository');
  await noGpu.locator('.scene-fallback:not([hidden]) img').waitFor();
  report.simulated.push('No WebGL2: derived fixture poster and canonical transcript');
  await context.close();
  assert.deepEqual(report.errors, []);
  fs.writeFileSync(
    path.join(folder, 'browser-acceptance.json'),
    JSON.stringify(report, null, 2) + '\n',
  );
  console.log(
    'PASS: production file://, full composed frame, tolerance-stable repeated seeks, selected legacy scenes, lifecycle, mobile, localization and fallback',
  );
}).catch((e) => {
  report.errors.push(e.stack);
  fs.writeFileSync(
    path.join(folder, 'browser-acceptance.json'),
    JSON.stringify(report, null, 2) + '\n',
  );
  console.error(e);
  process.exitCode = 1;
});
