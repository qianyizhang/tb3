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
    const receipt = JSON.parse(fs.readFileSync(path.join(out, 'receipt.json')));
    if (receipt.renderer === 'DOM/SVG planar')
      assert.equal(receipt.camera, 'Planar coordinate-preserving SVG/DOM');
    const url = pathToFileURL(path.join(out, 'index.html')).href;
    for (const locale of ['en', 'zh-CN']) {
      await page.goto(url + '?capture=1&lang=' + locale);
      await page.waitForFunction(() => window.__tb3ExplainerCapture);
      const frames = [
        0,
        plan.beats[Math.floor(plan.beats.length / 2)].endFrame - 1,
        plan.durationFrames - 1,
        ...([
          'mask-screen-v1',
          'anatomy-curation-v1',
          'mri-importer-v1',
          'localized-ct-v1',
          'aneurysm-localization-v1',
          'segmentation-calibration-v1',
          'dental-v3-v1',
          'dental-v2-v1',
          'dental-original-v1',
          'ct-organ-v1',
          'named-landmarks-v1',
          'clinical-cavity-v1',
          'respiratory-v1',
          'registration-analysis-v1',
          'resect-correspondence-v1',
          'resect-pilot-v1',
          'vessel-source-v1',
          'airway-repair-v1',
          'topbrain-screen-v1',
          'hubmap-inventory-v1',
          'tiger-context-v1',
          'longitudinal-mri-v1',
          'longitudinal-ct-original-v1',
          'longitudinal-ct-revised-v1',
        ].includes(plan.recipe)
          ? plan.beats.map((b) => b.endFrame - 1)
          : []),
      ];
      if (
        [
          'hubmap-inventory-v1',
          'tiger-context-v1',
          'longitudinal-mri-v1',
          'longitudinal-ct-original-v1',
          'longitudinal-ct-revised-v1',
        ].includes(plan.recipe)
      ) {
        for (const b of plan.beats) frames.push(b.startFrame);
      }
      if (plan.recipe === 'mri-importer-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const [scene, count] of [
          ['association', 12],
          ['geometry', 8],
          ['reference', 4],
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (let i = 0; i < count; i++)
            frames.push(
              Math.floor(b.startFrame + ((i + 0.5) / count) * (b.endFrame - b.startFrame)),
            );
        }
      }
      if (plan.recipe === 'localized-ct-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const [scene, count] of [
          ['axial', 4],
          ['orthogonal', 6],
          ['serial', 12],
          ['reference', 4],
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (let i = 0; i < count; i++)
            frames.push(
              Math.floor(b.startFrame + ((i + 0.5) / count) * (b.endFrame - b.startFrame)),
            );
        }
      }
      if (plan.recipe === 'aneurysm-localization-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const [scene, count] of [
          ['slabs', 12],
          ['depth', 7],
          ['reference', 4],
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (let i = 0; i < count; i++)
            frames.push(
              Math.floor(b.startFrame + ((i + 0.5) / count) * (b.endFrame - b.startFrame)),
            );
        }
      }
      if (plan.recipe === 'segmentation-calibration-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const scene of [
          'sampling',
          'preprocess',
          'reference',
          'sensitivity',
          'duodenum',
          'backend',
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (const fraction of [0.08, 0.25, 0.42, 0.58, 0.75, 0.92])
            frames.push(Math.round(b.startFrame + fraction * (b.endFrame - b.startFrame - 1)));
        }
      }
      if (plan.recipe === 'dental-v3-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const scene of [
          'example',
          'transfer',
          'shape',
          'pulp-gain',
          'pulp-reach',
          'pulp-loss',
          'canal-crop',
          'canal-extent',
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (const fraction of [0.1, 0.3, 0.5, 0.7, 0.9])
            frames.push(Math.round(b.startFrame + fraction * (b.endFrame - b.startFrame - 1)));
        }
      }
      if (plan.recipe === 'dental-v2-v1') {
        for (const b of plan.beats) frames.push(b.startFrame);
        for (const scene of [
          'example',
          'transfer',
          'identity',
          'pulp-contents',
          'pulp-clip',
          'canals',
          'small-canals',
        ]) {
          const b = plan.beats.find((b) => b.scene === scene);
          for (const fraction of [0.125, 0.375, 0.625, 0.875])
            frames.push(Math.round(b.startFrame + fraction * (b.endFrame - b.startFrame - 1)));
        }
      }
      if (plan.recipe === 'topbrain-screen-v1') {
        for (const scene of ['cohort', 'variants', 'contacts', 'calibration', 'cpr']) {
          const beat = plan.beats.find((b) => b.scene === scene);
          for (const fraction of [0, 0.25, 0.5, 0.75])
            frames.push(
              Math.round(beat.startFrame + fraction * (beat.endFrame - beat.startFrame - 1)),
            );
        }
      }
      if (['vessel-source-v1', 'airway-repair-v1'].includes(plan.recipe)) {
        const inspect = plan.beats.find((b) => b.scene === 'inspect');
        frames.push(Math.floor((inspect.startFrame + inspect.endFrame) / 2));
        if (plan.recipe === 'airway-repair-v1') {
          for (const scene of ['controls', 'cpr', 'route']) {
            const beat = plan.beats.find((b) => b.scene === scene);
            frames.push(beat.startFrame, Math.floor((beat.startFrame + beat.endFrame) / 2));
          }
        }
      }
      for (const frame of new Set(frames)) {
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
        if (plan.recipe === 'airway-repair-v1') {
          const panel = page.locator('[data-airway-output]');
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Airway legend clipped');
          assert.ok(
            await panel.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Airway output overflows',
          );
          if (frame === 0) {
            assert.equal(await page.locator('[data-airway-reference-image]').count(), 0);
            assert.equal(await page.locator('[data-airway-added-slice]').count(), 0);
          }
        }
        if (plan.recipe === 'longitudinal-ct-revised-v1') {
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'CT legend clipped');
          assert.ok(
            await page
              .locator('[data-revised-output-panel]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'CT output overflows',
          );
          const figure = page.locator('[data-revised-scene]');
          assert.deepEqual(
            await figure.evaluate((svg) => {
              const box = svg.getBoundingClientRect();
              return [...svg.querySelectorAll('text')]
                .filter((t) => {
                  const b = t.getBoundingClientRect();
                  return (
                    b.left < box.left - 1 || b.right > box.right + 1 || b.bottom > box.bottom + 1
                  );
                })
                .map((t) => t.textContent);
            }),
            [],
            'CT figure label outside bounds',
          );
          if (frame === 0) {
            assert.equal(await page.locator('[data-ct-reference], [data-ct-output]').count(), 0);
            assert.equal(await page.locator('[data-ct-input]').count(), 4);
          }
          const b = plan.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);
          if (b.scene === 'decisions') {
            assert.equal(await page.locator('[data-revised-point]').count(), 2);
            if (frame === b.startFrame)
              assert.equal(await page.locator('image[data-ct-reference]').count(), 0);
            if (frame === b.endFrame - 1)
              assert.equal(await page.locator('image[data-ct-reference]').count(), 2);
          }
          if (['partition', 'newfocus'].includes(b.scene) && frame === b.endFrame - 1)
            assert.ok(await page.locator('[data-revised-local-id]').count());
          if (b.scene === 'partition' && frame === b.endFrame - 1)
            assert.ok(await page.locator('image[data-ct-reference]').count());
        }
        if (plan.recipe === 'longitudinal-ct-original-v1') {
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'CT legend clipped');
          assert.ok(
            await page
              .locator('[data-ct-output-panel]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'CT output overflows',
          );
          const figure = page.locator('[data-ct-scene]');
          assert.deepEqual(
            await figure.evaluate((svg) => {
              const box = svg.getBoundingClientRect();
              return [...svg.querySelectorAll('text')]
                .filter((t) => {
                  const b = t.getBoundingClientRect();
                  return (
                    b.left < box.left - 1 || b.right > box.right + 1 || b.bottom > box.bottom + 1
                  );
                })
                .map((t) => t.textContent);
            }),
            [],
            'CT figure label outside bounds',
          );
          if (frame === 0) {
            assert.equal(await page.locator('[data-ct-reference], [data-ct-output]').count(), 0);
            assert.equal(await page.locator('[data-ct-input]').count(), 2);
          }
          const b = plan.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);
          if (b.scene === 'partition' && frame === b.endFrame - 1)
            assert.ok(await page.locator('[data-ct-reference] image[data-ct-reference]').count());
        }
        if (plan.recipe === 'longitudinal-mri-v1') {
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'MRI legend clipped');
          assert.ok(
            await page
              .locator('[data-mri-output-panel]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'MRI output overflows',
          );
          const b = plan.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);
          const figure = page.locator('[data-mri-scene]');
          assert.deepEqual(
            await figure.evaluate((svg) => {
              const box = svg.getBoundingClientRect();
              return [...svg.querySelectorAll('text')]
                .filter((t) => {
                  const b = t.getBoundingClientRect();
                  return (
                    b.left < box.left - 1 || b.right > box.right + 1 || b.bottom > box.bottom + 1
                  );
                })
                .map((t) => t.textContent);
            }),
            [],
            'MRI figure label outside bounds',
          );
          if (frame === 0) {
            assert.equal(await page.locator('[data-mri-reference], [data-mri-output]').count(), 0);
            assert.equal(await page.locator('[data-mri-input]').count(), 6);
          }
          if (
            frame === b.endFrame - 1 &&
            ['phases', 'sequences', 'reference', 'forecast'].includes(b.scene)
          )
            assert.ok((await page.locator('[data-mri-reference]').count()) > 0);
        }
        if (plan.recipe === 'tiger-context-v1') {
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'TIGER legend clipped');
          assert.ok(
            await page
              .locator('[data-tiger-output]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'TIGER output overflows',
          );
          const beat = plan.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);
          if (
            ['inputs', 'conditions', 'output', 'limits'].includes(beat.scene) ||
            (beat.scene === 'tissue' && frame === beat.startFrame)
          ) {
            assert.equal(await page.locator('[data-tiger-reference]').count(), 0);
            assert.equal(
              await page
                .locator('[data-tiger-measurement],[data-tiger-density],[data-tiger-coordinate]')
                .count(),
              0,
            );
          }
          if (beat.scene === 'density' && frame === beat.endFrame - 1) {
            assert.equal(await page.locator('[data-tiger-density] tbody tr').count(), 3);
            assert.equal(await page.locator('[data-tiger-reference] path').count(), 175);
            assert.match(await page.locator('[data-tiger-measurement]').textContent(), /2,049.19/);
          }
        }
        if (plan.recipe === 'hubmap-inventory-v1') {
          const panel = page.locator('[data-hubmap-output]');
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'HuBMAP legend clipped');
          assert.ok(
            await panel.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'HuBMAP output overflows',
          );
          const beat = plan.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);
          if (
            ['inputs', 'helpers', 'detail', 'conditions', 'limits'].includes(beat.scene) ||
            (beat.scene === 'outline' && frame === beat.startFrame)
          ) {
            assert.equal(await page.locator('[data-hubmap-reference]').count(), 0);
            assert.equal(
              await page
                .locator(
                  '[data-hubmap-measurement], [data-hubmap-worked-rows], [data-hubmap-inventory]',
                )
                .count(),
              0,
            );
          }
          if (beat.scene === 'inventory' && frame === beat.endFrame - 1) {
            assert.equal(await page.locator('[data-hubmap-reference] path').count(), 99);
            assert.equal(await page.locator('[data-hubmap-worked-rows] tbody tr').count(), 5);
          }
          if (beat.scene === 'duplicate' && frame === beat.endFrame - 1) {
            assert.match(
              await page.locator('[data-hubmap-duplicate-count]').textContent(),
              /1 unique source object/,
            );
            assert.equal(await page.locator('[data-hubmap-reference] path').count(), 2);
          }
        }
        if (plan.recipe === 'topbrain-screen-v1') {
          const panel = page.locator('[data-brain-output]');
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'TopBrain legend clipped');
          assert.ok(
            await panel.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'TopBrain output overflows',
          );
          if (frame === 0) {
            assert.equal(await page.locator('[data-brain-reference-image]').count(), 0);
            assert.equal(await page.locator('[data-brain-answer]').count(), 0);
          }
        }
        if (plan.recipe === 'vessel-source-v1') {
          const output = page.locator('[data-vessel-output]');
          assert.ok(
            await output.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Source output overflows',
          );
          const box = await output.boundingBox();
          assert.ok(box && box.y + box.height <= 720, 'Source output clipped');
          if (frame === 0) {
            assert.equal(await page.locator('[data-vessel-reference-image]').count(), 0);
            assert.equal(await page.locator('[data-vessel-answer]').count(), 0);
            assert.equal(await page.locator('[data-vessel-node]').count(), 0);
          }
        }
        if (plan.recipe === 'resect-pilot-v1') {
          const output = page.locator('[data-pilot-output]');
          assert.ok(
            await output.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Pilot output overflows',
          );
          const box = await output.boundingBox();
          assert.ok(box && box.y + box.height <= 720, 'Pilot output clipped');
          if (frame === 0) {
            assert.equal(await page.locator('[data-pilot-point="reference"]').count(), 0);
            assert.equal(await page.locator('[data-pilot-answer]').count(), 0);
          }
        }
        if (plan.recipe === 'resect-correspondence-v1') {
          const output = page.locator('[data-resect-output]');
          assert.ok(
            await output.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'RESECT output overflows',
          );
          const box = await output.boundingBox();
          assert.ok(box && box.y + box.height <= 720, 'RESECT output clipped');
          if ((await output.getAttribute('data-resect-output')) === 'helpers') {
            assert.equal(
              await page.locator('[data-resect-mask-legend="mri"]').getAttribute('fill'),
              '#e65b9f',
            );
            assert.equal(
              await page.locator('[data-resect-mask-legend="us"]').getAttribute('fill'),
              '#37cdcd',
            );
          }
          if (frame === 0) assert.equal(await page.locator('[data-resect-target]').count(), 0);
        }
        if (plan.recipe === 'registration-analysis-v1') {
          const output = page.locator('[data-registration-analysis-output]');
          assert.ok(
            await output.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Analysis output overflows',
          );
          const box = await output.boundingBox();
          assert.ok(box && box.y + box.height <= 720, 'Analysis output clipped');
          if (frame === 0) assert.equal(await page.locator('[data-analysis-reference]').count(), 0);
        }
        if (plan.recipe === 'mri-importer-v1') {
          const scene = page.locator('[data-mri-scene]');
          const reveal = (await scene.getAttribute('data-mri-reference')) === 'visible';
          if (!reveal) assert.equal(await page.locator('[data-mri-private]').count(), 0);
          if (frame === 0) assert.equal(await page.locator('[data-mri-output]').count(), 0);
          if ((await scene.getAttribute('data-mri-scene')) === 'reference')
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              reveal ? 1 : 0,
            );
          if ((await scene.getAttribute('data-mri-scene')) === 'association') {
            const selected = page.locator('[data-mri-grid] article[data-selected="true"]');
            assert.equal(await selected.count(), 2);
            assert.equal(
              await selected.nth(0).getAttribute('data-storage'),
              await selected.nth(1).getAttribute('data-storage'),
            );
            assert.equal(
              await selected.nth(0).getAttribute('data-target'),
              await selected.nth(1).getAttribute('data-target'),
            );
          }
          for (const selector of [
            '.scene-player > header',
            '[data-mri-scene]',
            '[class*="mriAside"]',
            '.scene-legend',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'MR overflow ' + selector,
            );
            const box = await page.locator(selector).boundingBox();
            assert.ok(box && box.y + box.height <= 720, 'MR clipping ' + selector);
          }
        }
        if (plan.recipe === 'localized-ct-v1') {
          const scene = page.locator('[data-localized-scene]');
          const reveal = (await scene.getAttribute('data-localized-reference')) === 'visible';
          if (!reveal) assert.equal(await page.locator('[data-localized-private]').count(), 0);
          if (frame === 0) {
            assert.equal(await page.locator('[data-localized-output]').count(), 0);
            assert.equal(await page.locator('[data-localized-point]').count(), 2);
          }
          if ((await scene.getAttribute('data-localized-scene')) === 'reference')
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              reveal ? 1 : 0,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-localized-scene]',
            '[class*="localizedAside"]',
            '.scene-legend',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'Localized CT overflow ' + selector,
            );
            const box = await page.locator(selector).boundingBox();
            assert.ok(box && box.y + box.height <= 720, 'Localized CT clipping ' + selector);
          }
        }
        if (plan.recipe === 'aneurysm-localization-v1') {
          const scene = page.locator('[data-aneurysm-scene]');
          const reveal = (await scene.getAttribute('data-aneurysm-reference')) === 'visible';
          if (!reveal) assert.equal(await page.locator('[data-aneurysm-private]').count(), 0);
          if (frame === 0) assert.equal(await page.locator('[data-aneurysm-point]').count(), 0);
          if ((await scene.getAttribute('data-aneurysm-scene')) === 'reference')
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              reveal ? 1 : 0,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-aneurysm-scene]',
            '[data-aneurysm-output]',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'Aneurysm overflow: ' + selector,
            );
            const box = await page.locator(selector).boundingBox();
            assert.ok(box && box.y + box.height <= 720, 'Aneurysm panel clipped: ' + selector);
          }
          for (const point of await page.locator('[data-aneurysm-point]').all())
            assert.equal(await point.getAttribute('data-depth-offset'), '0');
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Aneurysm legend clipped');
        }
        if (plan.recipe === 'segmentation-calibration-v1') {
          const scene = page.locator('[data-calibration-scene]');
          const reveal = (await scene.getAttribute('data-calibration-reference')) === 'visible';
          if (!reveal)
            assert.equal(
              await page
                .locator('[data-calibration-private], [data-calibration-layer="reference"]')
                .count(),
              0,
            );
          if (frame === 0) assert.equal(await page.locator('[data-calibration-layer]').count(), 0);
          if ((await scene.getAttribute('data-calibration-scene')) === 'reference')
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              reveal ? 1 : 0,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-calibration-scene]',
            '[data-calibration-output]',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'Calibration overflow: ' + selector,
            );
            const box = await page.locator(selector).boundingBox();
            assert.ok(box && box.y + box.height <= 720, 'Calibration panel clipped: ' + selector);
          }
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Calibration legend clipped');
        }
        if (plan.recipe === 'dental-v3-v1') {
          const scene = page.locator('[data-dental-v3-scene]');
          const reveal = (await scene.getAttribute('data-dental-v3-reference')) === 'visible';
          if (!reveal)
            assert.equal(
              await page
                .locator('[data-dental-v3-private], [data-dental-v3-layer="reference"]')
                .count(),
              0,
            );
          if (frame === 0) assert.equal(await page.locator('[data-dental-v3-layer]').count(), 0);
          if ((await scene.getAttribute('data-dental-v3-scene')) === 'shape')
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              reveal ? 1 : 0,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-dental-v3-scene]',
            '[data-dental-v3-output]',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'Dental v3 overflow: ' + selector,
            );
          }
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Dental v3 legend clipped');
          if ((await scene.getAttribute('data-dental-v3-scene')) === 'example')
            assert.equal(await page.locator('[data-dental-v3-layer="reference"]').count(), 0);
        }
        if (plan.recipe === 'dental-v2-v1') {
          const scene = page.locator('[data-dental-v2-scene]');
          const reveal = (await scene.getAttribute('data-dental-v2-reference')) === 'visible';
          if (!reveal)
            assert.equal(
              await page
                .locator('[data-dental-v2-private], [data-dental-v2-layer="reference"]')
                .count(),
              0,
            );
          if (frame === 0) assert.equal(await page.locator('[data-dental-v2-layer]').count(), 0);
          if ((await scene.getAttribute('data-dental-v2-scene')) === 'identity')
            assert.equal(
              await page.locator('[data-scene-inline-narration]').count(),
              reveal ? 1 : 0,
            );
          for (const selector of [
            '.scene-player > header',
            '[data-dental-v2-scene]',
            '[data-dental-v2-output]',
          ]) {
            assert.ok(
              await page
                .locator(selector)
                .evaluate(
                  (e) => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth,
                ),
              'Dental v2 overflow: ' + selector,
            );
          }
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Dental v2 legend clipped');
          if ((await scene.getAttribute('data-dental-v2-scene')) === 'example')
            assert.equal(await page.locator('[data-dental-v2-layer="reference"]').count(), 0);
        }
        if (plan.recipe === 'dental-original-v1') {
          assert.ok(
            await page
              .locator('.scene-player > header')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Dental story heading clipped',
          );
          const scene = page.locator('[data-dental-scene]');
          const reveal = (await scene.getAttribute('data-dental-reference')) === 'visible';
          if (!reveal)
            assert.equal(
              await page.locator('[data-dental-private], [data-dental-layer="reference"]').count(),
              0,
            );
          if (frame === 0) assert.equal(await page.locator('[data-dental-layer]').count(), 0);
          for (const selector of ['[data-dental-scene]', '[data-dental-output]'])
            assert.ok(
              await page.locator(selector).evaluate((e) => e.scrollHeight <= e.clientHeight),
              'Dental content overflows',
            );
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Dental legend clipped');
          if ((await scene.getAttribute('data-dental-scene')) === 'diagnostic') {
            const paths = async (key) =>
              page
                .locator(`[data-dental-panel="${key}"] path`)
                .evaluateAll((xs) => xs.map((x) => x.getAttribute('d')));
            assert.deepEqual(
              await paths('xhigh'),
              await paths('diagnostic'),
              'ID diagnostic moved geometry',
            );
          }
        }
        if (plan.recipe === 'ct-organ-v1') {
          const scene = page.locator('[data-ct-scene]');
          const reveal = (await scene.getAttribute('data-ct-reference')) === 'visible';
          if (!reveal)
            assert.equal(
              await page.locator('[data-ct-layer="reference"], [data-ct-private]').count(),
              0,
            );
          if (frame === 0) assert.equal(await page.locator('[data-ct-layer]').count(), 0);
          assert.ok(
            await page
              .locator('[data-ct-output]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'CT output overflow',
          );
          assert.ok(
            await scene.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'CT scene overflow',
          );
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'CT legend clipped');
        }
        if (plan.recipe === 'named-landmarks-v1') {
          const panel = page.locator('[data-landmark-output]');
          assert.ok(
            await panel.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Landmark output overflows',
          );
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Landmark legend clipped');
          assert.ok(
            await page
              .locator('[data-landmark-scene]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Landmark scene overflows',
          );
          const revealed = (await panel.getAttribute('data-landmark-reference')) === 'visible';
          if (!revealed)
            assert.equal(
              await page
                .locator('[data-landmark-mark="reference"], [data-landmark-private]')
                .count(),
              0,
            );
          if (frame === 0) assert.equal(await page.locator('[data-landmark-mark]').count(), 0);
        }
        if (plan.recipe === 'clinical-cavity-v1') {
          const panel = page.locator('[data-cavity-output]');
          const legend = await page.locator('.scene-legend').boundingBox();
          assert.ok(legend && legend.y + legend.height <= 720, 'Cavity legend clipped');
          assert.ok(
            await panel.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Cavity output overflows',
          );
          const box = await panel.boundingBox();
          assert.ok(box && box.y + box.height <= 720, 'Cavity output clipped');
          const beat = plan.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);
          const reveal = (await panel.getAttribute('data-cavity-reference')) === 'revealed';
          assert.equal(
            await panel.locator('[data-cavity-reference-section]').count(),
            reveal ? 3 : 0,
          );
          assert.equal(
            await panel.locator('[data-cavity-reference-curve]').count(),
            reveal ? 1 : 0,
          );
          if (frame === 0)
            assert.equal(await panel.locator('[data-cavity-output-section]').count(), 0);
          const selected = Number(await panel.getAttribute('data-cavity-frame'));
          const image = Number(await panel.getAttribute('data-cavity-image-frame'));
          if (beat.scene === 'static') assert.equal(image, 0);
          else if (beat.scene === 'shift') assert.equal(image, (selected - 5 + 18) % 18);
          else assert.equal(image, selected);
        }
        if (plan.recipe === 'respiratory-v1') {
          const output = page.locator('[data-respiratory-output]');
          assert.ok(
            await output.evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Respiratory output overflows',
          );
          const box = await output.boundingBox();
          assert.ok(box && box.y + box.height <= 720, 'Respiratory output clipped');
        }
        if (plan.recipe === 'anatomy-curation-v1') {
          assert.ok(
            await page
              .locator('[data-curation-output]')
              .evaluate((e) => e.scrollHeight <= e.clientHeight),
            'Curation output overflows',
          );
          const box = await page.locator('[data-curation-output]').boundingBox();
          assert.ok(box && box.y + box.height <= 720, 'Curation output clipped');
          if (frame === 0)
            assert.deepEqual(await page.locator('[data-curation-reference]').allTextContents(), [
              'hidden',
              'hidden',
            ]);
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
    if (plan.recipe === 'mri-importer-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'MR mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
        if (step === 7) {
          assert.ok(
            await page.locator('[data-mri-controls] tbody td:nth-child(2)').evaluateAll((cells) =>
              cells.every((cell) => {
                const r = document.createRange();
                r.selectNodeContents(cell);
                return (
                  r.getBoundingClientRect().height <=
                  parseFloat(getComputedStyle(cell).lineHeight) + 1
                );
              }),
            ),
            'MR score denominator wraps across lines',
          );
        }
        if (step === 6) {
          await page.locator('.scene-play').click();
          await page.locator('[data-mri-private]').first().waitFor();
          await page.locator('.scene-play').click();
          assert.ok(
            await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
            'MR mobile reference overflow',
          );
          await page
            .locator('.scene-player')
            .screenshot({ path: path.join(out, 'mobile-reference.png') });
        }
      }
    }
    if (plan.recipe === 'localized-ct-v1') {
      for (let step = 1; step < plan.beats.length; step++) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Localized mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'aneurysm-localization-v1') {
      for (const step of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Aneurysm mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'segmentation-calibration-v1') {
      for (const step of [1, 2, 3, 5, 6, 7, 8, 9, 10, 11]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Calibration mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'dental-v3-v1') {
      for (const step of [2, 3, 5, 6, 7, 8, 9, 10, 11]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Dental v3 mobile overflow',
        );
        if (step === 5)
          assert.equal(await page.locator('[data-scene-inline-narration]').count(), 0);
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'dental-v2-v1') {
      for (const step of [2, 3, 5, 6, 7, 8, 9, 10, 11]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Dental v2 mobile overflow',
        );
        if (step === 5)
          assert.equal(await page.locator('[data-scene-inline-narration]').count(), 0);
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'dental-original-v1') {
      for (const step of [4, 5, 6, 8, 9, 10]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Dental mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'ct-organ-v1') {
      for (const step of [2, 3, 6, 8, 9]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (f) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(f),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'CT mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'named-landmarks-v1') {
      for (const step of [4, 5, 8, 9, 10]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        assert.equal(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          true,
          'Landmark mobile overflow',
        );
        await page
          .locator('.scene-player')
          .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'clinical-cavity-v1') {
      for (const step of [4, 5, 6, 7, 8, 9, 10]) {
        await page.locator(`[data-story-step="${step}"]`).click();
        await page.waitForFunction(
          (frame) =>
            document.querySelector('.scene-player')?.getAttribute('data-committed-frame') ===
            String(frame),
          plan.beats[step].startFrame,
        );
        assert.ok(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          'Cavity mobile chapter overflows',
        );
        const panel = await page.locator('[data-cavity-output]').boundingBox();
        assert.ok(
          panel && panel.x >= 0 && panel.x + panel.width <= 390,
          'Cavity mobile panel clipped',
        );
        if ([4, 9, 10].includes(step))
          await page
            .locator('.scene-player')
            .screenshot({ path: path.join(out, `mobile-chapter-${step}.png`) });
      }
    }
    if (plan.recipe === 'tiger-context-v1') {
      const labels = await page.locator('[data-tiger-scene]').evaluate((svg) => {
        const box = svg.getBoundingClientRect();
        return [...svg.querySelectorAll('text')].every((text) => {
          const b = text.getBoundingClientRect();
          return b.width > 0 && b.height > 0 && b.left >= box.left - 1 && b.right <= box.right + 1;
        });
      });
      assert.ok(
        labels,
        'TIGER mobile scale and source labels must remain visible and inside the figure',
      );
    }
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
      'mri-importer-v1',
      'localized-ct-v1',
      'aneurysm-localization-v1',
      'segmentation-calibration-v1',
      'dental-v3-v1',
      'dental-v2-v1',
      'dental-original-v1',
      'ct-organ-v1',
      'multiscale-v1',
      'local-edit-v1',
      'longitudinal-v1',
      'inverse-v1',
      'anatomy-identity-v1',
      'prototype-identity-v1',
      'mask-screen-v1',
      'anatomy-curation-v1',
      'named-landmarks-v1',
      'clinical-cavity-v1',
      'respiratory-v1',
      'registration-analysis-v1',
      'resect-correspondence-v1',
      'resect-pilot-v1',
      'vessel-source-v1',
      'airway-repair-v1',
      'topbrain-screen-v1',
      'hubmap-inventory-v1',
      'tiger-context-v1',
      'longitudinal-mri-v1',
      'longitudinal-ct-original-v1',
      'longitudinal-ct-revised-v1',
      'mixed-tissue-v1',
    ].includes(plan.recipe);
    assert.equal(renderer, planar ? 'planar' : 'poster');
    if (plan.recipe === 'mri-importer-v1') {
      assert.equal(await fallback.locator('[data-mri-private]').count(), 0);
      await fallback.locator('[data-story-step="2"]').click();
      assert.equal(
        await fallback.locator('[data-mri-grid] article[data-selected="true"]').count(),
        2,
      );
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-association.png') });
      await fallback.locator('[data-story-step="6"]').click();
      await fallback.locator('.scene-play').click();
      await fallback.locator('[data-mri-private]').first().waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-mri-reference]')?.getAttribute('data-mri-reference') ===
          'hidden',
      );
      assert.equal(await fallback.locator('[data-mri-private]').count(), 0);
    }
    if (plan.recipe === 'localized-ct-v1') {
      assert.equal(await fallback.locator('[data-localized-private]').count(), 0);
      assert.equal(await fallback.locator('[data-localized-point]').count(), 2);
      await fallback.locator('[data-story-step="7"]').click();
      await fallback.locator('.scene-play').click();
      await fallback.locator('path[data-localized-private]').first().waitFor();
      await fallback.locator('.scene-play').click();
      assert.equal(await fallback.locator('path[data-localized-private]').count(), 2);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-localized-reference]')
            ?.getAttribute('data-localized-reference') === 'hidden',
      );
      assert.equal(await fallback.locator('[data-localized-private]').count(), 0);
    }
    if (plan.recipe === 'aneurysm-localization-v1') {
      assert.equal(
        await fallback.locator('[data-aneurysm-point], [data-aneurysm-private]').count(),
        0,
      );
      await fallback.locator('[data-story-step="7"]').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-aneurysm-reference]')
            ?.getAttribute('data-aneurysm-reference') === 'visible',
      );
      assert.ok((await fallback.locator('[data-aneurysm-private]').count()) > 0);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-aneurysm-reference]')
            ?.getAttribute('data-aneurysm-reference') === 'hidden',
      );
      assert.equal(
        await fallback.locator('[data-aneurysm-point], [data-aneurysm-private]').count(),
        0,
      );
    }
    if (plan.recipe === 'segmentation-calibration-v1') {
      assert.equal(await fallback.locator('[data-calibration-layer]').count(), 0);
      await fallback.locator('[data-story-step="7"]').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-calibration-reference]')
            ?.getAttribute('data-calibration-reference') === 'visible',
      );
      assert.ok((await fallback.locator('[data-calibration-layer="reference"]').count()) > 0);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-calibration-reference]')
            ?.getAttribute('data-calibration-reference') === 'hidden',
      );
      assert.equal(await fallback.locator('[data-calibration-layer]').count(), 0);
    }
    if (plan.recipe === 'dental-v3-v1') {
      assert.equal(await fallback.locator('[data-dental-v3-layer]').count(), 0);
      await fallback.locator('[data-story-step="9"]').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-dental-v3-reference]')
            ?.getAttribute('data-dental-v3-reference') === 'visible',
      );
      assert.ok((await fallback.locator('[data-dental-v3-layer="reference"]').count()) > 0);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-dental-v3-reference]')
            ?.getAttribute('data-dental-v3-reference') === 'hidden',
      );
      assert.equal(await fallback.locator('[data-dental-v3-layer]').count(), 0);
    }

    if (plan.recipe === 'dental-v2-v1') {
      assert.equal(await fallback.locator('[data-dental-v2-layer]').count(), 0);
      await fallback.locator('[data-story-step="9"]').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-dental-v2-reference]')
            ?.getAttribute('data-dental-v2-reference') === 'visible',
      );
      assert.ok((await fallback.locator('[data-dental-v2-layer="reference"]').count()) > 0);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-dental-v2-reference]')
            ?.getAttribute('data-dental-v2-reference') === 'hidden',
      );
      assert.equal(await fallback.locator('[data-dental-v2-layer]').count(), 0);
    }

    if (plan.recipe === 'dental-original-v1') {
      assert.equal(await fallback.locator('[data-dental-layer]').count(), 0);
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-dental-reference]')
            ?.getAttribute('data-dental-reference') === 'visible',
      );
      assert.ok((await fallback.locator('[data-dental-layer="reference"]').count()) > 0);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-dental-reference]')
            ?.getAttribute('data-dental-reference') === 'hidden',
      );
      assert.equal(await fallback.locator('[data-dental-layer]').count(), 0);
    }
    if (plan.recipe === 'ct-organ-v1') {
      assert.equal(await fallback.locator('[data-ct-layer]').count(), 0);
      await fallback.locator('[data-story-step="6"]').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-ct-reference]')?.getAttribute('data-ct-reference') ===
          'visible',
      );
      assert.equal(await fallback.locator('[data-ct-layer="reference"]').count(), 2);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-ct-reference]')?.getAttribute('data-ct-reference') ===
          'hidden',
      );
      assert.equal(await fallback.locator('[data-ct-layer]').count(), 0);
    }
    if (plan.recipe === 'named-landmarks-v1') {
      assert.equal(await fallback.locator('[data-landmark-mark]').count(), 0);
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-landmark-reference]')
            ?.getAttribute('data-landmark-reference') === 'visible',
      );
      assert.equal(await fallback.locator('[data-landmark-mark="reference"]').count(), 3);
      assert.equal(await fallback.locator('[data-landmark-mark="sol"]').count(), 0);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document
            .querySelector('[data-landmark-reference]')
            ?.getAttribute('data-landmark-reference') === 'hidden',
      );
      assert.equal(await fallback.locator('[data-landmark-mark]').count(), 0);
    }
    if (plan.recipe === 'clinical-cavity-v1') {
      assert.equal(await fallback.locator('[data-cavity-projection]').count(), 1);
      assert.equal(await fallback.locator('[data-cavity-reference-section]').count(), 0);
      await fallback.locator('[data-story-step="4"]').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-cavity-output]')?.getAttribute('data-cavity-reference') ===
          'revealed',
      );
      assert.equal(await fallback.locator('[data-cavity-reference-section]').count(), 6);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-cavity-output]')?.getAttribute('data-cavity-reference') ===
          'hidden',
      );
      assert.equal(await fallback.locator('[data-cavity-reference-section]').count(), 0);
    }
    if (plan.recipe === 'longitudinal-ct-revised-v1') {
      assert.equal(await fallback.locator('[data-ct-reference], [data-ct-output]').count(), 0);
      await fallback.locator('[data-story-step="2"]').click();
      assert.equal(await fallback.locator('image[data-ct-reference]').count(), 2);
      await fallback.locator('.scene-reset').click();
      assert.equal(await fallback.locator('[data-ct-reference], [data-ct-output]').count(), 0);
    }
    if (plan.recipe === 'longitudinal-ct-original-v1') {
      assert.equal(await fallback.locator('[data-ct-reference], [data-ct-output]').count(), 0);
      await fallback.locator('[data-story-step="2"]').click();
      assert.equal(await fallback.locator('image[data-ct-reference]').count(), 1);
      await fallback.locator('.scene-reset').click();
      assert.equal(await fallback.locator('[data-ct-reference], [data-ct-output]').count(), 0);
    }
    if (plan.recipe === 'longitudinal-mri-v1') {
      assert.equal(await fallback.locator('[data-mri-reference], [data-mri-output]').count(), 0);
      await fallback.locator('[data-story-step="2"]').click();
      assert.equal(await fallback.locator('[data-mri-reference] [data-mri-input]').count(), 2);
      await fallback.locator('.scene-reset').click();
      assert.equal(await fallback.locator('[data-mri-reference], [data-mri-output]').count(), 0);
    }
    if (plan.recipe === 'airway-repair-v1') {
      // Check rendered pixels, not only nonempty paths: opposite mesh-face winding
      // can silently cancel a complete silhouette inside a compound SVG path.
      const bluePixels = await fallback.locator('.scene-stage svg').evaluate(async (svg) => {
        const image = new Image();
        const url = URL.createObjectURL(
          new Blob([new XMLSerializer().serializeToString(svg)], { type: 'image/svg+xml' }),
        );
        try {
          await new Promise((resolve, reject) => {
            image.onload = resolve;
            image.onerror = reject;
            image.src = url;
          });
          const canvas = document.createElement('canvas');
          canvas.width = 600;
          canvas.height = 420;
          const context = canvas.getContext('2d');
          context.drawImage(image, 0, 0, 600, 420);
          const pixels = context.getImageData(0, 0, 600, 420).data;
          let count = 0;
          for (let i = 0; i < pixels.length; i += 4)
            if (
              pixels[i + 3] > 100 &&
              pixels[i + 2] > pixels[i] + 20 &&
              pixels[i + 1] > pixels[i] + 15
            )
              count++;
          return count;
        } finally {
          URL.revokeObjectURL(url);
        }
      });
      assert.ok(bluePixels > 1000, 'Fallback must visibly render the supplied airway mask');
      row.fallbackMaskPixels = bluePixels;
      assert.equal(await fallback.locator('[data-airway-reference-geometry]').count(), 0);
      assert.equal(await fallback.locator('[data-airway-result]').count(), 0);
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-airway-reference-state]')?.textContent === 'hidden',
      );
      await fallback.locator('.scene-play').click();
      await fallback.locator('[data-airway-reference-geometry]').waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-airway-output]')?.getAttribute('data-airway-output') ===
          'inputs',
      );
      assert.equal(await fallback.locator('[data-airway-reference-geometry]').count(), 0);
      assert.equal(await fallback.locator('[data-airway-result]').count(), 0);
    }
    if (plan.recipe === 'tiger-context-v1') {
      assert.equal(await fallback.locator('[data-tiger-reference]').count(), 0);
      await fallback.locator('[data-story-step="2"]').click();
      assert.equal(await fallback.locator('[data-tiger-reference]').count(), 0);
      await fallback.locator('.scene-play').click();
      await fallback.locator('.scene-stage').scrollIntoViewIfNeeded();
      await fallback.locator('[data-tiger-reference]').first().waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-tiger-scene]')?.getAttribute('data-tiger-scene') ===
          'inputs',
      );
      assert.equal(await fallback.locator('[data-tiger-reference]').count(), 0);
      assert.equal(await fallback.locator('[data-tiger-measurement]').count(), 0);
    }
    if (plan.recipe === 'hubmap-inventory-v1') {
      assert.equal(await fallback.locator('[data-hubmap-reference]').count(), 0);
      await fallback.locator('[data-story-step="3"]').click();
      assert.equal(await fallback.locator('[data-hubmap-reference]').count(), 0);
      await fallback.locator('.scene-play').click();
      await fallback.locator('.scene-stage').scrollIntoViewIfNeeded();
      await fallback.locator('[data-hubmap-reference]').waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-hubmap-scene]')?.getAttribute('data-hubmap-scene') ===
          'inputs',
      );
      assert.equal(await fallback.locator('[data-hubmap-reference]').count(), 0);
      assert.equal(await fallback.locator('[data-hubmap-measurement]').count(), 0);
    }
    if (plan.recipe === 'topbrain-screen-v1') {
      assert.equal(await fallback.locator('[data-brain-reference-image]').count(), 0);
      await fallback.locator('[data-story-step="6"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-brain-reference-state]')?.textContent === 'hidden',
      );
      await fallback.locator('.scene-play').click();
      await fallback.locator('.scene-stage').scrollIntoViewIfNeeded();
      await fallback.locator('[data-brain-reference-image]').first().waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-brain-output]')?.getAttribute('data-brain-output') ===
          'inputs',
      );
      assert.equal(await fallback.locator('[data-brain-reference-image]').count(), 0);
      assert.equal(await fallback.locator('[data-brain-answer]').count(), 0);
    }
    if (plan.recipe === 'vessel-source-v1') {
      assert.equal(await fallback.locator('[data-vessel-reference-image]').count(), 0);
      await fallback.locator('[data-story-step="1"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-vessel-reference]')?.textContent === 'hidden',
      );
      await fallback.locator('.scene-play').click();
      await fallback.locator('[data-vessel-reference-image]').first().waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('.scene-reset').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-vessel-output]')?.getAttribute('data-vessel-output') ===
          'sources',
      );
      assert.equal(await fallback.locator('[data-vessel-reference-image]').count(), 0);
      assert.equal(await fallback.locator('[data-vessel-answer]').count(), 0);
    }
    if (plan.recipe === 'resect-pilot-v1') {
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-pilot-reference]')?.textContent === 'hidden',
      );
      assert.equal(await fallback.locator('[data-pilot-point="reference"]').count(), 0);
      await fallback.locator('.scene-play').click();
      await fallback.locator('[data-pilot-point="reference"]').first().waitFor();
      await fallback.locator('.scene-play').click();
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-pilot-output]')?.getAttribute('data-pilot-output') ===
          'inputs',
      );
      assert.equal(await fallback.locator('[data-pilot-point="reference"]').count(), 0);
      assert.equal(await fallback.locator('[data-pilot-answer]').count(), 0);
    }
    if (plan.recipe === 'resect-correspondence-v1') {
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-resect-reference]')?.textContent === 'hidden',
      );
      await fallback.locator('[data-story-step="6"]').click();
      await fallback.waitForFunction(() =>
        document.querySelector('[data-resect-output]')?.textContent.includes('9.58'),
      );
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-cases.png') });
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.waitForFunction(
        () =>
          document.querySelector('[data-resect-output]')?.getAttribute('data-resect-output') ===
          'inputs',
      );
      assert.equal(await fallback.locator('[data-resect-target]').count(), 0);
    }
    if (plan.recipe === 'registration-analysis-v1') {
      await fallback.locator('[data-story-step="1"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-analysis-reference]')?.textContent === 'hidden',
      );
      await fallback.locator('[data-story-step="3"]').click();
      await fallback.waitForFunction(() =>
        document
          .querySelector('[data-registration-analysis-output]')
          ?.textContent.includes('18.994'),
      );
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-support.png') });
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.waitForFunction(() =>
        document
          .querySelector('[data-registration-analysis-output]')
          ?.textContent.includes('A postmortem of one selected failure'),
      );
      assert.equal(await fallback.locator('[data-analysis-reference]').count(), 0);
    }
    if (plan.recipe === 'respiratory-v1') {
      await fallback.locator('[data-story-step="4"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-respiratory-reference]')?.textContent === 'hidden',
      );
      await fallback.locator('[data-story-step="5"]').click();
      await fallback.waitForFunction(() =>
        document
          .querySelector('[data-respiratory-output]')
          ?.textContent.includes('User visual judgment'),
      );
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-reference.png') });
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.waitForFunction(() =>
        document
          .querySelector('[data-respiratory-output]')
          ?.textContent.includes('Eight source queries'),
      );
      assert.equal(await fallback.locator('[data-respiratory-reference]').count(), 0);
    }
    if (plan.recipe === 'anatomy-curation-v1') {
      assert.deepEqual(await fallback.locator('[data-curation-reference]').allTextContents(), [
        'hidden',
        'hidden',
      ]);
      await fallback.locator('[data-story-step="2"]').click();
      await fallback.waitForFunction(() =>
        document.querySelector('[data-curation-output]')?.textContent.includes('37.49'),
      );
      assert.deepEqual(await fallback.locator('[data-curation-reference]').allTextContents(), [
        'T9',
        'T10',
        'T11',
      ]);
      await fallback
        .locator('.scene-player')
        .screenshot({ path: path.join(out, 'no-gpu-preservation.png') });
      await fallback.locator('[data-story-step="0"]').click();
      await fallback.waitForFunction(
        () => document.querySelector('[data-curation-reference]')?.textContent === 'hidden',
      );
      assert.deepEqual(await fallback.locator('[data-curation-reference]').allTextContents(), [
        'hidden',
        'hidden',
      ]);
    }
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
      'tb3-anatomy-curation',
      'tb3-respiratory-correspondence',
      'tb3-registration-analysis',
      'tb3-clinical-cavity-adaptation',
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
      if (id === 'tb3-clinical-cavity-adaptation') {
        assert.equal(
          await page.locator('.scene-player').getAttribute('data-recipe'),
          'clinical-cavity-v1',
        );
        assert.equal(
          await page.locator('[data-cavity-output]').getAttribute('data-cavity-reference'),
          'hidden',
        );
        if (pass === 0) {
          await page.locator('[data-story-step="4"]').click();
          await page.waitForFunction(
            () =>
              document
                .querySelector('[data-cavity-output]')
                ?.getAttribute('data-cavity-reference') === 'revealed',
          );
          assert.match(await page.locator('[data-cavity-output]').innerText(), /45.31%/);
          const playerBox = await page.locator('.scene-player').boundingBox();
          const stageBox = await page.locator('.scene-stage').boundingBox();
          const outputBox = await page.locator('[data-cavity-output]').boundingBox();
          if (playerBox.width <= 900)
            assert.ok(
              outputBox.y >= stageBox.y + stageBox.height - 1,
              'Narrow Explorer must stack the cavity measurements beneath the stage',
            );

          await page
            .locator('.scene-player')
            .screenshot({ path: path.join(folder, 'explorer-clinical-reference.png') });
          await page.locator('.scene-reset').click();
          await page.waitForFunction(
            () =>
              document
                .querySelector('[data-cavity-output]')
                ?.getAttribute('data-cavity-reference') === 'hidden',
          );
        }
      }
      report.navigation.push(state);
    }
  await page.evaluate(() => {
    location.hash = 'tb3-named-landmarks/0/overview?view=repository';
  });
  await page.waitForFunction(
    () =>
      document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'named-landmarks-v1',
  );
  assert.equal(await page.locator('[data-landmark-mark]').count(), 0);
  await page.locator('[data-story-step="5"]').click();
  await page.waitForFunction(
    () =>
      document
        .querySelector('[data-landmark-reference]')
        ?.getAttribute('data-landmark-reference') === 'visible',
  );
  assert.match(await page.locator('[data-landmark-output]').innerText(), /visible miss/);
  assert.equal(await page.locator('[data-landmark-mark="sol"]').count(), 0);
  await page
    .locator('.scene-player')
    .screenshot({ path: path.join(folder, 'integrated-landmarks.png') });
  await page.locator('.scene-reset').click();
  await page.waitForFunction(
    () =>
      document
        .querySelector('[data-landmark-reference]')
        ?.getAttribute('data-landmark-reference') === 'hidden',
  );
  report.navigation.push({ id: 'tb3-named-landmarks', revealAndReset: true });
  await page.evaluate(() => {
    location.hash = 'tb3-ct-organ-segmentation/0/overview?view=repository';
  });
  await page.waitForFunction(
    () => document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'ct-organ-v1',
  );
  assert.equal(await page.locator('[data-ct-layer]').count(), 0);
  await page.locator('[data-story-step="6"]').click();
  await page.waitForFunction(
    () =>
      document.querySelector('[data-ct-reference]')?.getAttribute('data-ct-reference') ===
      'visible',
  );
  assert.equal(await page.locator('[data-ct-layer="reference"]').count(), 2);
  await page
    .locator('.scene-player')
    .screenshot({ path: path.join(folder, 'integrated-ct-organ.png') });
  await page.locator('.scene-reset').click();
  await page.waitForFunction(
    () =>
      document.querySelector('[data-ct-reference]')?.getAttribute('data-ct-reference') === 'hidden',
  );
  assert.equal(await page.locator('[data-ct-layer]').count(), 0);
  report.navigation.push({ id: 'tb3-ct-organ-segmentation', revealAndReset: true });
  await page.evaluate(() => {
    location.hash = 'tb3-dental-original/0/overview?view=repository';
  });
  await page.waitForFunction(
    () =>
      document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'dental-original-v1',
  );
  assert.equal(await page.locator('[data-dental-layer]').count(), 0);
  await page.locator('[data-story-step="5"]').click();
  await page.waitForFunction(
    () =>
      document.querySelector('[data-dental-reference]')?.getAttribute('data-dental-reference') ===
      'visible',
  );
  assert.ok((await page.locator('[data-dental-layer="reference"]').count()) > 0);
  await page
    .locator('.scene-player')
    .screenshot({ path: path.join(folder, 'integrated-dental-original.png') });
  await page.locator('.scene-reset').click();
  await page.waitForFunction(
    () =>
      document.querySelector('[data-dental-reference]')?.getAttribute('data-dental-reference') ===
      'hidden',
  );
  assert.equal(await page.locator('[data-dental-layer]').count(), 0);
  report.navigation.push({ id: 'tb3-dental-original', revealAndReset: true });
  await page.evaluate(() => {
    location.hash = 'tb3-dental-v2/0/overview?view=repository';
  });
  await page.waitForFunction(
    () => document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'dental-v2-v1',
  );
  assert.equal(await page.locator('[data-dental-v2-layer]').count(), 0);
  await page.locator('[data-story-step="9"]').click();
  await page.waitForFunction(
    () =>
      document
        .querySelector('[data-dental-v2-reference]')
        ?.getAttribute('data-dental-v2-reference') === 'visible',
  );
  assert.ok((await page.locator('[data-dental-v2-layer="reference"]').count()) > 0);
  await page
    .locator('.scene-player')
    .screenshot({ path: path.join(folder, 'integrated-dental-v2.png') });
  await page.locator('.scene-reset').click();
  await page.waitForFunction(
    () =>
      document
        .querySelector('[data-dental-v2-reference]')
        ?.getAttribute('data-dental-v2-reference') === 'hidden',
  );
  assert.equal(await page.locator('[data-dental-v2-layer]').count(), 0);
  report.navigation.push({ id: 'tb3-dental-v2', revealAndReset: true });

  await page.evaluate(() => {
    location.hash = 'tb3-dental-v3/0/overview?view=repository';
  });
  await page.waitForFunction(
    () => document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'dental-v3-v1',
  );
  assert.equal(await page.locator('[data-dental-v3-layer]').count(), 0);
  await page.locator('[data-story-step="9"]').click();
  await page.waitForFunction(
    () =>
      document
        .querySelector('[data-dental-v3-reference]')
        ?.getAttribute('data-dental-v3-reference') === 'visible',
  );
  assert.ok((await page.locator('[data-dental-v3-layer="reference"]').count()) > 0);
  await page
    .locator('.scene-player')
    .screenshot({ path: path.join(folder, 'integrated-dental-v3.png') });
  await page.locator('.scene-reset').click();
  await page.waitForFunction(
    () =>
      document
        .querySelector('[data-dental-v3-reference]')
        ?.getAttribute('data-dental-v3-reference') === 'hidden',
  );
  assert.equal(await page.locator('[data-dental-v3-layer]').count(), 0);
  report.navigation.push({ id: 'tb3-dental-v3', revealAndReset: true });
  await page.evaluate(() => {
    location.hash = 'tb3-segmentation-calibration/0/overview?view=repository';
  });
  await page.waitForFunction(
    () =>
      document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
      'segmentation-calibration-v1',
  );
  assert.equal(await page.locator('[data-calibration-layer]').count(), 0);
  await page.locator('[data-story-step="7"]').click();
  await page.waitForFunction(
    () =>
      document
        .querySelector('[data-calibration-reference]')
        ?.getAttribute('data-calibration-reference') === 'visible',
  );
  assert.ok((await page.locator('[data-calibration-layer="reference"]').count()) > 0);
  await page
    .locator('.scene-player')
    .screenshot({ path: path.join(folder, 'integrated-calibration.png') });
  await page.locator('.scene-reset').click();
  await page.waitForFunction(
    () =>
      document
        .querySelector('[data-calibration-reference]')
        ?.getAttribute('data-calibration-reference') === 'hidden',
  );
  assert.equal(await page.locator('[data-calibration-layer]').count(), 0);
  report.navigation.push({ id: 'tb3-segmentation-calibration', revealAndReset: true });
  await page.evaluate(() => {
    location.hash = 'tb3-aneurysm-localization/0/overview?view=repository';
  });
  await page.waitForFunction(
    () =>
      document.querySelector('.scene-player')?.getAttribute('data-recipe') ===
      'aneurysm-localization-v1',
  );
  assert.equal(await page.locator('[data-aneurysm-point], [data-aneurysm-private]').count(), 0);
  await page.locator('[data-story-step="7"]').click();
  await page.waitForFunction(
    () =>
      document
        .querySelector('[data-aneurysm-reference]')
        ?.getAttribute('data-aneurysm-reference') === 'visible',
  );
  assert.ok((await page.locator('[data-aneurysm-private]').count()) > 0);
  await page
    .locator('.scene-player')
    .screenshot({ path: path.join(folder, 'integrated-aneurysm.png') });
  await page.locator('.scene-reset').click();
  await page.waitForFunction(
    () =>
      document
        .querySelector('[data-aneurysm-reference]')
        ?.getAttribute('data-aneurysm-reference') === 'hidden',
  );
  assert.equal(await page.locator('[data-aneurysm-point], [data-aneurysm-private]').count(), 0);
  report.navigation.push({ id: 'tb3-aneurysm-localization', revealAndReset: true });

  await page.evaluate(() => {
    location.hash = 'tb3-localized-candidate-recognition/0/overview?view=repository';
  });
  await page.waitForFunction(
    () =>
      document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'localized-ct-v1',
  );
  assert.equal(await page.locator('[data-localized-private], [data-localized-output]').count(), 0);
  assert.equal(await page.locator('[data-localized-point]').count(), 2);
  await page.locator('[data-story-step="8"]').click();
  await page.locator('[data-localized-private]').first().waitFor();
  await page
    .locator('.scene-player')
    .screenshot({ path: path.join(folder, 'integrated-localized-ct.png') });
  await page.locator('.scene-reset').click();
  await page.waitForFunction(
    () =>
      document
        .querySelector('[data-localized-reference]')
        ?.getAttribute('data-localized-reference') === 'hidden',
  );
  assert.equal(await page.locator('[data-localized-private], [data-localized-output]').count(), 0);
  report.navigation.push({ id: 'tb3-localized-candidate-recognition', revealAndReset: true });
  await page.evaluate(() => {
    location.hash = 'tb3-mri-importer/0/overview?view=repository';
  });
  await page.waitForFunction(
    () =>
      document.querySelector('.scene-player')?.getAttribute('data-recipe') === 'mri-importer-v1',
  );
  assert.equal(await page.locator('[data-mri-private], [data-mri-output]').count(), 0);
  await page.locator('[data-story-step="2"]').click();
  assert.equal(await page.locator('[data-mri-grid] article[data-selected="true"]').count(), 2);
  await page
    .locator('.scene-player')
    .screenshot({ path: path.join(folder, 'integrated-mri-importer.png') });
  await page.locator('[data-story-step="7"]').click();
  await page.locator('[data-mri-private]').first().waitFor();
  await page.locator('.scene-reset').click();
  await page.waitForFunction(
    () =>
      document.querySelector('[data-mri-reference]')?.getAttribute('data-mri-reference') ===
      'hidden',
  );
  assert.equal(await page.locator('[data-mri-private], [data-mri-output]').count(), 0);
  report.navigation.push({ id: 'tb3-mri-importer', revealAndReset: true });

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
