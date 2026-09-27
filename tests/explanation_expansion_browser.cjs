/** Integrated source/capture/locale/fallback matrix using the repository browser harness. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { pathToFileURL } = require('node:url');
const { withBrowser } = require('../presentation/tooling/browser.mts');
const { captureComposedFrame } = require('../presentation/tooling/media/capture.mts');
const folder = path.resolve(process.argv[2]),
  explorer = path.resolve(process.argv[3]);
const report = {
  stories: [],
  errors: [],
  remote_requests: [],
  file_protocol: true,
  navigation: [],
};
const sha = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
withBrowser(async (browser) => {
  report.browser = browser.version();
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    deviceScaleFactor: 1,
    reducedMotion: 'reduce',
  });
  await context.route(/^https?:/, (route) => {
    report.remote_requests.push(route.request().url());
    return route.abort();
  });
  const page = await context.newPage();
  page.on('pageerror', (error) => report.errors.push(error.message));
  for (const id of fs
    .readdirSync(folder)
    .filter((id) => fs.existsSync(path.join(folder, id, 'plan.json')))) {
    const out = path.join(folder, id),
      plan = JSON.parse(fs.readFileSync(path.join(out, 'plan.json'))),
      row = { id, frames: [], locales: [], fallback: false };
    const url = pathToFileURL(path.join(out, 'index.html')).href;
    for (const locale of ['en', 'zh-CN']) {
      await page.goto(url + '?capture=1&lang=' + locale);
      await page.waitForFunction(() => window.__tb3ExplainerCapture);
      const frames = [
        0,
        plan.beats[Math.floor(plan.beats.length / 2)].endFrame - 1,
        plan.durationFrames - 1,
        ...(plan.recipe === 'mask-screen-v1' ? plan.beats.map((b) => b.endFrame - 1) : []),
      ];
      for (const frame of frames) {
        const bytes = await captureComposedFrame(page, {
          frame,
          fps: plan.fps,
          width: 1280,
          height: 720,
        });
        const file = `review-${locale}-${frame}.png`;
        fs.writeFileSync(path.join(out, file), bytes);
        row.frames.push({ locale, frame, file, sha256: sha(bytes) });
        if (id === 'wsi-search') {
          const canvas = page.locator('.scene-stage svg');
          const selection = canvas.locator('g[opacity]');
          assert.equal(await selection.getAttribute('opacity'), frame === 0 ? '0' : '1');
          const tile = canvas.locator('rect[fill="#dae5e6"]');
          assert.equal(await tile.getAttribute('width'), frame === 0 ? '130' : '520');
          const returned = canvas.getByText('level-0 (2680, 2040) px', { exact: true });
          assert.equal(await returned.count(), frame === plan.durationFrames - 1 ? 1 : 0);
        }
        if (plan.recipe === 'mask-screen-v1') {
          assert.ok(
            await page
              .locator('[data-mask-screen-output]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Author-screen output overflows',
          );
          const output = await page.locator('[data-mask-screen-output]').boundingBox();
          assert.ok(output && output.y + output.height <= 720, 'Author-screen output clipped');
        }
        if (plan.recipe === 'mixed-tissue-v1') {
          const reveal = plan.beats.find((b) => b.channels.reference[1] > 0).startFrame;
          const witness = plan.beats.find((b) => b.channels.witness[1] > 0).startFrame;
          assert.equal(
            await page.locator('[data-mixed-reference]').count(),
            frame > reveal ? 1 : 0,
          );
          assert.equal(await page.locator('[data-mixed-answer]').count(), frame > witness ? 1 : 0);
          assert.ok(
            await page
              .locator('[data-mixed-output]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Mixed-tissue content overflows',
          );
          const output = await page.locator('[data-mixed-output]').boundingBox();
          assert.ok(output && output.y + output.height <= 720, 'Mixed-tissue output clipped');
        }
        if (plan.recipe === 'anatomy-identity-v1') {
          const labels = await page.locator('[data-identity-label]').allTextContents();
          assert.equal(labels.length, 7);
          assert.equal(
            labels.every((label) => label === 'unassigned'),
            frame !== plan.durationFrames - 1,
          );
          const output = await page.locator('[data-identity-output]').boundingBox();
          assert.ok(output && output.y + output.height <= 720, 'Identity output clipped');
          assert.ok(
            await page
              .locator('[data-identity-output]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Identity output content overflows its panel',
          );
        }
        if (plan.recipe === 'prototype-identity-v1') {
          const labels = await page.locator('[data-prototype-label]').allTextContents();
          assert.equal(labels.length, 17);
          assert.equal(
            labels.every((label) => label === 'unassigned'),
            frame !== plan.durationFrames - 1,
          );
          assert.ok(
            await page
              .locator('[data-prototype-output]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Prototype output content overflows',
          );
          const output = await page.locator('[data-prototype-output]').boundingBox();
          assert.ok(output && output.y + output.height <= 720, 'Prototype output clipped');
        }
        assert.equal(
          await page.locator('.scene-player').getAttribute('data-committed-frame'),
          String(frame),
        );
        const caption = await page.locator('[data-scene-title]').boundingBox();
        assert.ok(
          caption && caption.y + caption.height <= 720,
          `${id} caption clipped in ${locale}`,
        );
      }
      const end = await captureComposedFrame(page, {
        frame: frames[2],
        fps: plan.fps,
        width: 1280,
        height: 720,
      });
      const endDom = await page.locator('.scene-player').innerHTML();
      await captureComposedFrame(page, { frame: 0, fps: plan.fps, width: 1280, height: 720 });
      const repeated = await captureComposedFrame(page, {
        frame: frames[2],
        fps: plan.fps,
        width: 1280,
        height: 720,
      });
      assert.equal(
        await page.locator('.scene-player').innerHTML(),
        endDom,
        'Repeated frame DOM must match exactly: ' + id,
      );
      if (sha(repeated) !== sha(end)) {
        // Chromium can differ by one quantization level at SVG antialias and translucent-fill edges.
        // Keep an explicit pixel bound; do not tolerate displaced geometry or text.
        const delta = await page.evaluate(
          async ([a, b]) => {
            async function pixels(src) {
              const image = new Image();
              image.src = src;
              await image.decode();
              const canvas = new OffscreenCanvas(image.width, image.height);
              const ctx = canvas.getContext('2d');
              ctx.drawImage(image, 0, 0);
              return ctx.getImageData(0, 0, image.width, image.height).data;
            }
            const x = await pixels(a),
              y = await pixels(b);
            let changedPixels = 0,
              maxChannelError = 0;
            for (let i = 0; i < x.length; i += 4) {
              let changed = false;
              for (let j = 0; j < 4; j++) {
                const d = Math.abs(x[i + j] - y[i + j]);
                if (d) changed = true;
                maxChannelError = Math.max(maxChannelError, d);
              }
              if (changed) changedPixels++;
            }
            return { changedPixels, maxChannelError };
          },
          [end, repeated].map((bytes) => 'data:image/png;base64,' + bytes.toString('base64')),
        );
        assert.ok(
          delta.changedPixels <= (plan.schema === 1 ? 16 : 2048) &&
            delta.maxChannelError <= (plan.schema === 1 ? 8 : 1),
          'Repeated-frame raster drift ' + id + ': ' + JSON.stringify(delta),
        );
        row.rasterQuantization = delta;
      }
      row.locales.push(locale);
    }
    // IDs may change while explicit operation fields retain the rendered meaning.
    if (['multiscale-v1', 'topology-v1', 'correspondence-v1'].includes(plan.recipe)) {
      const renamed = structuredClone(plan);
      renamed.id = 'renamed-explicit-story';
      renamed.beats.forEach((beat, index) => {
        beat.id = `renamed-${index}`;
      });
      const renamedFile = path.join(out, 'renamed.html');
      fs.writeFileSync(
        renamedFile,
        fs
          .readFileSync(path.join(out, 'index.html'), 'utf8')
          .replace(
            /(<script id="story-plan" type="application\/json">)[\s\S]*?(<\/script>)/,
            (_match, start, end) =>
              start + JSON.stringify(renamed).replaceAll('<', '\\u003c') + end,
          ),
      );
      const semanticFrames = plan.beats.map((beat) => beat.endFrame - 1);
      await page.goto(url + '?capture=1&lang=en');
      const originals = [];
      for (const frame of semanticFrames) {
        await captureComposedFrame(page, { frame, fps: plan.fps, width: 1280, height: 720 });
        originals.push(
          await page.locator('.scene-player').evaluate((element) => ({
            caption: element.querySelector('[data-scene-title]')?.textContent,
            legend: element.querySelector('.scene-legend')?.textContent,
            // Ignore data attributes and identity; compare the actual composition and geometry.
            svg: [...element.querySelectorAll('svg')].map((svg) => svg.outerHTML),
            output: element.querySelector('[class*="storyOutput"]')?.innerHTML,
          })),
        );
      }
      await page.goto(pathToFileURL(renamedFile).href + '?capture=1&lang=en');
      for (const [index, frame] of semanticFrames.entries()) {
        await captureComposedFrame(page, { frame, fps: plan.fps, width: 1280, height: 720 });
        const renamedView = await page.locator('.scene-player').evaluate((element) => ({
          caption: element.querySelector('[data-scene-title]')?.textContent,
          legend: element.querySelector('.scene-legend')?.textContent,
          svg: [...element.querySelectorAll('svg')].map((svg) => svg.outerHTML),
          output: element.querySelector('[class*="storyOutput"]')?.innerHTML,
        }));
        assert.deepEqual(renamedView, originals[index], `${id} explicit rename at frame ${frame}`);
      }
      row.renameInvariant = semanticFrames;
    }
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(url + '?lang=zh-CN');
    await page.locator('.scene-player[data-rendered="true"]').waitFor();
    assert.equal(
      await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
      true,
      'mobile overflow ' + id,
    );
    await page.locator('.scene-player').screenshot({ path: path.join(out, 'mobile.png') });
    if (plan.recipe === 'mixed-tissue-v1') {
      assert.equal(await page.locator('[data-mixed-orientation]').isVisible(), true);
      assert.match(await page.locator('[data-mixed-orientation]').innerText(), /LPS mm/);
    }
    await page.setViewportSize({ width: 1280, height: 900 });
    const noGpu = await browser.newContext({
      viewport: { width: 1280, height: 900 },
      reducedMotion: 'reduce',
    });
    await noGpu.route(/^https?:/, (route) => {
      report.remote_requests.push(route.request().url());
      return route.abort();
    });
    await noGpu.addInitScript(() => {
      const original = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function (type, ...args) {
        return type === 'webgl2' || type === 'webgl' ? null : original.call(this, type, ...args);
      };
    });
    const fallback = await noGpu.newPage();
    await fallback.goto(url + '?lang=en');
    await fallback.locator('.scene-player[data-rendered="true"]').waitFor();
    const renderer = await fallback.locator('.scene-player').getAttribute('data-surface-renderer');
    const planar = [
      'multiscale-v1',
      'local-edit-v1',
      'longitudinal-v1',
      'inverse-v1',
      'anatomy-identity-v1',
      'prototype-identity-v1',
      'mask-screen-v1',
      'mixed-tissue-v1',
    ].includes(plan.recipe);
    assert.equal(renderer, planar ? 'planar' : 'poster');
    if (plan.recipe === 'mask-screen-v1') {
      await fallback.locator('[data-story-step="4"]').click();
      await fallback.waitForFunction(
        () => document.querySelectorAll('[data-screen-wrong="true"]').length === 2,
      );
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-exception.png') });
      await fallback.locator('[data-story-step="1"]').click();
      assert.ok(
        (await fallback.locator('[data-screen-reference]').allTextContents()).every(
          (t) => t === '—',
        ),
      );
      assert.equal(await fallback.locator('[data-screen-wrong="true"]').count(), 0);
    }

    if (plan.recipe === 'prototype-identity-v1') {
      assert.ok(
        (await fallback.locator('[data-prototype-label]').allTextContents()).every(
          (s) => s === 'unassigned',
        ),
      );
      await fallback.locator('[data-story-step="4"]').click();
      await fallback.waitForFunction(() =>
        [...document.querySelectorAll('[data-prototype-label]')].every(
          (e) => e.textContent !== 'unassigned',
        ),
      );
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.waitForFunction(() =>
        [...document.querySelectorAll('[data-prototype-label]')].every(
          (e) => e.textContent === 'unassigned',
        ),
      );
    }
    if (plan.recipe === 'mixed-tissue-v1') {
      assert.equal(await fallback.locator('[data-mixed-reference]').count(), 0);
      assert.equal(await fallback.locator('[data-mixed-answer]').count(), 0);
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.locator('[data-mixed-answer]').waitFor();
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.locator('[data-mixed-pending]').waitFor();
      assert.equal(await fallback.locator('[data-mixed-reference]').count(), 0);
    }
    if (plan.recipe === 'anatomy-identity-v1') {
      assert.equal(
        await fallback.locator('.scene-player').getAttribute('data-committed-frame'),
        '0',
      );
      assert.ok(
        (await fallback.locator('[data-identity-label]').allTextContents()).every(
          (label) => label === 'unassigned',
        ),
      );
      await fallback.locator('[data-story-step="4"]').click();
      await fallback.waitForFunction(() =>
        [...document.querySelectorAll('[data-identity-label]')].every(
          (e) => e.textContent !== 'unassigned',
        ),
      );
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.waitForFunction(() =>
        [...document.querySelectorAll('[data-identity-label]')].every(
          (e) => e.textContent === 'unassigned',
        ),
      );
    }
    if (!planar && plan.schema === 2)
      assert.equal(
        await fallback.locator('.scene-player').getAttribute('data-committed-frame'),
        String(plan.durationFrames - 1),
      );
    if (plan.schema === 2)
      assert.equal(await fallback.getByText('Route-conditioned image', { exact: true }).count(), 0);
    await fallback.locator('.scene-player').screenshot({ path: path.join(out, 'no-gpu.png') });
    row.fallback = true;
    await noGpu.close();
    report.stories.push(row);
    console.log('Reviewed matrix: ' + id);
  }
  await page.goto(
    pathToFileURL(explorer).href + '?lang=en#tb3-named-coronary/0/overview?view=repository',
  );
  await page.locator('.scene-player[data-rendered="true"]').waitFor();
  assert.equal(await page.evaluate(() => typeof window.__tb3ExplainerCapture), 'undefined');
  for (let pass = 0; pass < 3; pass++)
    for (const id of [
      'tb3-named-coronary',
      'wsi-hiesd-patches',
      'tb3-oblique-pose',
      'tb3-label-audit',
      'tb3-supplied-object-identity',
      'tb3-mixed-tissue-audit',
      'tb3-unlabeled-anatomy-prototype',
      'tb3-mask-reasoning-study',
    ]) {
      await page.evaluate((id) => {
        location.hash = `${id}/0/overview?view=repository`;
      }, id);
      await page.waitForFunction(
        (id) => document.querySelector('.task-detail')?.dataset.brief === id,
        id,
      );
      await page.locator('.scene-player[data-rendered="true"]').waitFor();
      const state = await page.locator('.scene-player').evaluate(
        (e, id) => ({
          id,
          renderer: e.dataset.surfaceRenderer,
          roots: e.dataset.nativeRoots,
          canvases: e.querySelectorAll('canvas').length,
        }),
        id,
      );
      assert.equal(state.canvases, 1);
      if (state.renderer === 'webgl') assert.equal(state.roots, '1');
      report.navigation.push(state);
    }
  await context.close();
  assert.deepEqual(report.errors, []);
  assert.deepEqual(report.remote_requests, []);
})
  .then(() => {
    fs.writeFileSync(
      path.join(folder, 'browser-matrix.json'),
      JSON.stringify(report, null, 2) + '\n',
    );
    console.log(
      'PASS: integrated locale/seek/mobile/no-GPU/navigation matrix; zero remote requests',
    );
  })
  .catch((error) => {
    report.errors.push(error.stack);
    fs.writeFileSync(
      path.join(folder, 'browser-matrix.json'),
      JSON.stringify(report, null, 2) + '\n',
    );
    console.error(error);
    process.exitCode = 1;
  });
