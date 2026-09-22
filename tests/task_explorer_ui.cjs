/* Optional browser regression check for a built offline Task Explorer.
 * PLAYWRIGHT_MODULE may point to an existing Playwright installation.
 * Usage: node tests/task_explorer_ui.cjs runs/task-explorer/index.html [report.json]
 * Does not install dependencies, fetch resources, or run external benchmarks.
 */
const { withBrowser } = require('../scripts/browser.cjs');
const { resolve, dirname } = require('path');
const { pathToFileURL } = require('url');
const fs = require('fs');
const assert = require('assert/strict');
const { createHash } = require('crypto');
async function checkExplorer(browser, input, report) {
  const file = resolve(input);
  const context = await browser.newContext({
    viewport: { width: 1010, height: 1324 },
    reducedMotion: 'reduce',
  });
  const errors = [],
    requests = [];
  try {
    const page = await context.newPage();
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('request', (r) => {
      if (/^https?:/.test(r.url())) requests.push(r.url());
    });
    await page.goto(pathToFileURL(file).href);
    const data = await page.evaluate(() => JSON.parse(document.querySelector('#data').textContent));
    assert.equal(
      await page.locator('#workbench-home').count(),
      data.presentation_context?.home_url ? 1 : 0,
      'Only integrated builds offer a workbench backlink',
    );
    if (process.env.TASK_EXPLORER_REQUIRE_ALL_MEDIA)
      assert.deepEqual(
        data.entries.flatMap((e) => e.missing_media),
        [],
      );
    const go = async (hash, id, section = 'overview') => {
      await page.evaluate((hash) => {
        location.hash = hash + (hash.includes('?') ? '' : '?view=repository');
      }, hash);
      await page.waitForFunction(
        ({ id, section }) =>
          document.querySelector('.task-detail')?.dataset.brief === id &&
          document.querySelector(`[data-tab="${section}"][aria-selected="true"]`),
        { id, section },
      );
    };
    // Every imported source record survives its old URL and keeps its source identity.
    let records = 0,
      conditions = 0,
      images = 0,
      drawings = 0,
      sourcePreviews = 0,
      fallbackDrawings = 0;
    const diagramTypes = new Set();
    for (const repo of data.inventory.repositories)
      for (const item of repo.items) {
        await go(
          `${repo.id}/task/${encodeURIComponent(item.id)}/${item.condition_index || 0}/sources`,
          item.brief_id,
          'sources',
        );
        await page.waitForFunction(
          (id) => document.querySelector('.provenance code')?.textContent === id,
          item.id,
        );
        assert.equal(await page.locator('.selected-source > a').getAttribute('href'), item.url);
        assert.equal(
          await page.locator('.provenance').getAttribute('open'),
          null,
          'Technical IDs must be collapsed',
        );
        records++;
      }
    for (const e of data.entries) {
      for (let n = 0; n < e.variants.length; n++) {
        await go(`${e.id}/${n}/brief`, e.id);
        if (
          e.task_family &&
          data.entries.filter((x) => x.task_family === e.task_family).length > 1
        ) {
          assert.equal(
            await page.locator('#task-variant').inputValue(),
            e.id,
            'Deep links select the exact dataset/target variant',
          );
          assert.equal(
            await page.locator('.detail-heading h2').innerText(),
            data.task_families[e.task_family].title,
          );
        }
        if (e.variants.length > 1) {
          await page.waitForFunction(
            (n) =>
              document.querySelector('[data-condition][aria-pressed=true]')?.dataset.condition ===
              String(n),
            n,
          );
        }
        if (data.require_overview_visuals)
          assert.equal(
            await page.locator('.task-picture').count(),
            1,
            `${e.id}/${n}: overview visual`,
          );
        conditions++;
      }
      if (e.illustration) {
        await page.locator('.scene-player[data-rendered="true"]').waitFor();
        assert.equal(await page.locator('.scene-canvas').count(), 1, `${e.id}: 3D scene`);
        assert.equal(
          await page.locator('.scene-fallback svg').count(),
          0,
          'SVG geometry stays lazy while Canvas works',
        );
        assert.equal(
          await page.locator('.scene-player').getAttribute('data-scene'),
          e.illustration.kind,
        );
        assert.equal(await page.locator('.scene-player').getAttribute('data-playing'), 'false');
        assert.ok(
          (await page.locator('.task-picture figcaption').innerText()).includes(
            'not case-specific',
          ),
        );
        for (const stage of [0, 1, 2]) {
          await page.locator(`[data-scene-step="${stage}"]`).click();
          assert.equal(
            await page.locator('.scene-player').getAttribute('data-stage'),
            String(stage),
          );
          assert.equal(
            await page.locator(`[data-scene-step="${stage}"]`).getAttribute('aria-pressed'),
            'true',
          );
        }
        assert.equal(await page.locator('[data-scene-title]').innerText(), e.illustration.output);
        if (e.illustration.labels?.length) {
          const names = await page.locator('.scene-label-space span').allTextContents();
          assert.deepEqual(
            names,
            e.illustration.labels,
            'The full label space remains readable outside the canvas',
          );
        }
        drawings++;
        diagramTypes.add(e.illustration.kind);
      }
      if (/<img\b/.test(e.visuals.input)) {
        await page.locator('.scene-source summary').click();
        assert.equal(await page.locator('.native-preview img').count(), 1);
        await page.locator('.native-preview img').evaluate((e) => e.decode());
        assert.equal(
          await page.locator('.native-input').innerHTML(),
          e.visuals.input,
          'Source preview preserves its authored selection caption',
        );
        sourcePreviews++;
      } else if (e.missing_media.length) {
        assert.equal(await page.locator('.preview-unavailable').count(), 1);
        assert.ok((await page.locator('.preview-unavailable').innerText()).includes('unavailable'));
      }
      if (Object.values(e.visuals).some((x) => /<img\b/.test(x))) {
        await page.locator('[data-tab="examples"]').click();
        assert.equal(
          await page.locator('[data-visible-role]').getAttribute('data-visible-role'),
          'input',
        );
        for (const role of ['input', 'helpers', 'answer']) {
          await page.locator(`[data-visual="${role}"]`).click();
          for (const image of await page.locator('.visual-content img').all()) {
            await image.evaluate((e) => e.decode());
            assert.ok(await image.evaluate((e) => e.naturalWidth > 0));
            images++;
          }
        }
      } else {
        assert.equal(
          await page.locator('[data-tab="examples"]').count(),
          0,
          'No repeated text pretending to be an image',
        );
      }
    }
    // Optional native images can be absent in a portable build. Every native entry
    // must still explain its task, without disguising the missing source example.
    for (const e of data.entries.filter((e) => /<img\b/.test(e.visuals.input))) {
      assert.ok(e.illustration, `${e.id}: portable illustration fallback`);
      await go(`${e.id}/0/overview`, e.id);
      await page.evaluate((id) => {
        const entry = DATA.entries.find((e) => e.id === id);
        entry.visuals.input = '<p>Source example unavailable in this build.</p>';
        entry.missing_media = ['optional-example.png'];
        render();
      }, e.id);
      assert.equal(await page.locator('.scene-canvas').count(), 1);
      assert.ok((await page.locator('.preview-unavailable').innerText()).includes('unavailable'));
      fallbackDrawings++;
      await page.reload();
    }
    // Motion is real, opt-out is respected, and camera controls work without a mouse.
    const moving = data.entries.find(
      (e) =>
        ['dynamic_mesh', 'cardiac_material'].includes(e.illustration.kind) &&
        e.illustration.input_form !== 'masks',
    );
    assert.ok(moving, 'A task with meaningful geometry motion is available');
    await go(`${moving.id}/0/overview`, moving.id);
    await page.locator('.scene-canvas').scrollIntoViewIfNeeded();
    const pixels = async () =>
      createHash('sha256')
        .update(await page.locator('.scene-canvas').evaluate((c) => c.toDataURL()))
        .digest('hex');
    await page.locator('.scene-player[data-rendered="true"]').waitFor();
    const still = await pixels();
    await page.waitForTimeout(180);
    assert.equal(await pixels(), still, 'Reduced motion starts at a static input');
    await page.locator('.scene-play').click();
    await page.waitForTimeout(250);
    assert.notEqual(
      await pixels(),
      still,
      'Play animates task geometry while the camera stays fixed',
    );
    await page.locator('.scene-play').click();
    const paused = await pixels();
    await page.waitForTimeout(180);
    assert.equal(await pixels(), paused, 'Pause stops animation');
    await page.locator('.scene-canvas').focus();
    await page.keyboard.press('ArrowRight');
    assert.notEqual(await pixels(), paused, 'Keyboard rotates the 3D camera');
    const keyboardView = await pixels();
    const bounds = await page.locator('.scene-canvas').boundingBox();
    await page.mouse.move(bounds.x + bounds.width / 2, bounds.y + bounds.height / 2);
    await page.mouse.down();
    await page.mouse.move(bounds.x + bounds.width / 2 + 70, bounds.y + bounds.height / 2 + 20);
    await page.mouse.up();
    assert.notEqual(await pixels(), keyboardView, 'Pointer drag rotates the camera');
    await page.locator('.scene-reset').click();
    assert.equal(await pixels(), still, 'Reset restores the initial pose and stage');
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    await page.reload();
    await page.locator('.scene-canvas').scrollIntoViewIfNeeded();
    assert.equal(await page.locator('.scene-player').getAttribute('data-playing'), 'true');
    await page.waitForFunction(() => document.querySelector('.scene-player').dataset.stage === '1');
    await page.waitForFunction(
      () => document.querySelector('.scene-player').dataset.playing === 'false',
      null,
      { timeout: 18000 },
    );
    assert.equal(await page.locator('.scene-player').getAttribute('data-stage'), '2');
    assert.equal(await page.locator('.scene-play').innerText(), 'Replay');
    const settled = await pixels();
    await page.waitForTimeout(180);
    assert.equal(await pixels(), settled, 'The demonstration finishes on a still output');
    await page.locator('.scene-play').click();
    assert.equal(await page.locator('.scene-player').getAttribute('data-stage'), '0');
    assert.equal(await page.locator('.scene-player').getAttribute('data-playing'), 'true');
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.waitForFunction(
      () => document.querySelector('.scene-player').dataset.playing === 'false',
    );
    assert.equal(await page.locator('.scene-player').getAttribute('data-playing'), 'false');
    // Manual stage changes ease between static poses, unless reduced motion is on.
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    await page.locator('[data-scene-step="2"]').click();
    const changing = await pixels();
    await page.waitForTimeout(450);
    const finalPose = await pixels();
    assert.notEqual(finalPose, changing, 'Stage changes crossfade into the next pose');
    await page.waitForTimeout(180);
    assert.equal(
      await pixels(),
      finalPose,
      'A manual transition settles without starting playback',
    );
    await page.locator('.scene-reset').click();
    assert.equal(await page.locator('.scene-play').innerText(), 'Play');
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.locator('[data-scene-step="2"]').click();
    const reducedPose = await pixels();
    await page.waitForTimeout(180);
    assert.equal(await pixels(), reducedPose, 'Reduced motion skips the crossfade');
    // GPU failure preserves inspectable surfaces through the Canvas renderer.
    for (const failure of ['unavailable', 'lost']) {
      const software = await context.newPage();
      software.on('pageerror', (e) => errors.push(e.message));
      await software.addInitScript((failure) => {
        const getContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function (type, ...options) {
          if (failure === 'unavailable' && type === 'webgl') return null;
          const context = getContext.call(this, type, ...options);
          if (type === 'webgl') window.surfaceContext = context;
          return context;
        };
      }, failure);
      await software.goto(pathToFileURL(file).href + '#tb3-dental-v3/0/overview');
      await software.locator('.scene-player[data-rendered="true"]').waitFor();
      if (failure === 'lost') {
        assert.equal(
          await software.locator('.scene-player').getAttribute('data-surface-renderer'),
          'webgl',
        );
        await software.evaluate(() => {
          window.surfaceContext.getExtension('WEBGL_lose_context').loseContext();
        });
        await software.waitForFunction(() => window.surfaceContext.isContextLost());
      }
      await software.locator('.scene-canvas').focus();
      await software.keyboard.press('ArrowRight');
      assert.equal(
        await software.locator('.scene-player').getAttribute('data-surface-renderer'),
        'canvas',
        `GPU ${failure}: software surfaces remain available`,
      );
      await software.close();
    }
    // Off-screen scenes stop changing and navigation releases the old canvas.
    await page.bringToFront();
    await page.locator('.scene-play').click();
    await page.setViewportSize({ width: 1010, height: 600 });
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    assert.ok(
      await page.locator('.scene-canvas').evaluate((c) => c.getBoundingClientRect().bottom < 0),
      'The canvas must leave the viewport before checking suspension',
    );
    await page.waitForTimeout(120);
    const offscreen = await pixels();
    await page.waitForTimeout(180);
    assert.equal(await pixels(), offscreen, 'Off-screen geometry stops updating');
    await page.locator('.scene-canvas').scrollIntoViewIfNeeded();
    await page.waitForTimeout(180);
    assert.notEqual(await pixels(), offscreen, 'Returning to the scene resumes playback');
    await page.evaluate(() => {
      window.detachedScene = document.querySelector('.scene-canvas');
    });
    await page.locator('#tab-requirements').click();
    const detached = await page.evaluate(() => window.detachedScene.toDataURL());
    await page.waitForTimeout(180);
    assert.equal(
      await page.evaluate(() => window.detachedScene.toDataURL()),
      detached,
      'Navigation disposes the old player',
    );
    await page.evaluate(() => {
      delete window.detachedScene;
    });
    await page.setViewportSize({ width: 1010, height: 1324 });
    // Playback must not spin an otherwise static anatomical input.
    await go('tb3-dental-v3/0/overview', 'tb3-dental-v3');
    await page.locator('.scene-canvas').scrollIntoViewIfNeeded();
    await page.locator('.scene-player[data-rendered="true"]').waitFor();
    const fixedInput = await pixels();
    await page.locator('.scene-play').click();
    await page.waitForTimeout(250);
    assert.equal(await pixels(), fixedInput, 'The camera stays fixed during stage playback');
    await page.locator('.scene-play').click();
    // Canvas-unavailable environments retain the authored, accessible SVG explanation.
    const fallback = await context.newPage();
    await fallback.addInitScript(() => {
      HTMLCanvasElement.prototype.getContext = () => null;
    });
    await fallback.goto(pathToFileURL(file).href + '#tb3-dental-v3/0/overview');
    assert.equal(await fallback.locator('.scene-fallback').isVisible(), true);
    assert.equal(await fallback.locator('.scene-fallback svg').count(), 2);
    assert.equal(await fallback.locator('.scene-controls').isVisible(), false);
    await fallback.close();
    await page.bringToFront();
    // Local sources remain inspectable from this single HTML file with exact downloads.
    let localSources = 0;
    const seenSources = new Set();
    for (const e of data.entries)
      for (const [, path] of e.sources) {
        const source = data.local_sources?.[path];
        if (!source || seenSources.has(path)) continue;
        seenSources.add(path);
        await go(`${e.id}/0/sources`, e.id, 'sources');
        if (source.unavailable) {
          assert.ok((await page.locator('#task-panel').innerText()).includes(source.unavailable));
          continue;
        }
        const button = page.locator(`[data-source="${source.sha256}"]`).first();
        await button.focus();
        await page.keyboard.press('Enter');
        assert.equal(await page.evaluate(() => document.activeElement.id), 'source-heading');
        assert.equal(new URLSearchParams(page.url().split('?')[1]).get('source'), source.sha256);
        assert.equal(await page.locator('.source-reader pre').textContent(), source.content);
        const download = await page.locator('#source-download').getAttribute('href');
        const raw = Buffer.from(download.split(',')[1], 'base64');
        assert.equal(raw.length, source.bytes);
        assert.equal(createHash('sha256').update(raw).digest('hex'), source.sha256);
        await page.reload();
        assert.equal(await page.locator('.source-reader pre').textContent(), source.content);
        await page.goBack();
        await page.waitForFunction(() => !document.querySelector('.source-reader'));
        assert.equal(
          await page.evaluate(() => document.activeElement.dataset.source),
          source.sha256,
        );
        await button.click();
        await page.locator('#source-close').click();
        assert.equal(
          await page.evaluate(() => document.activeElement.dataset.source),
          source.sha256,
        );
        localSources++;
      }
    // Image notices return to their original control when Back restores the preview.
    await go('abra/0/overview', 'abra');
    await page.locator('.scene-source summary').click();
    const noticeHash = await page.locator('[data-notice]').getAttribute('data-notice');
    await page.locator('[data-notice]').focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.evaluate(() => document.activeElement.id), 'source-heading');
    await page.goBack();
    await page.waitForFunction(
      () => document.querySelector('#tab-overview')?.getAttribute('aria-selected') === 'true',
    );
    assert.equal(
      await page.evaluate(() => document.activeElement.dataset.notice),
      noticeHash,
      'Back from image notices restores preview focus',
    );
    const clinical = 'healthagentbench-trial-matching',
      case29 = 'clinical_trial_matching_task_29';
    await go(`healthagentbench/task/${case29}/0/catalogue`, clinical);
    await page.waitForFunction(
      (id) => document.querySelector(`[data-entry="${id}"][aria-pressed=true]`),
      case29,
    );
    assert.equal(
      await page.locator('[data-definition]').count(),
      7,
      'Repeated disease/quality variants share one task entry',
    );
    assert.equal(await page.locator('[data-entry]').count(), 9);
    assert.equal(
      await page.locator('[data-definition="healthagentbench-trial-matching"]').count(),
      1,
    );
    assert.equal(await page.locator('#task-picker').count(), 0);
    assert.equal(await page.locator('.catalogue-glance').count(), 0);
    assert.ok(
      !(await page
        .locator('body')
        .innerText()
        .then((x) => x.includes('Task at a glance'))),
    );
    assert.ok((await page.locator('.case-facts').innerText()).includes('407 candidate trials'));
    assert.equal(
      await page.locator('.provenance').count(),
      0,
      'Technical IDs do not occupy the overview',
    );
    const heading = await page.locator('.detail-heading h2').innerText();
    await page.locator('[data-entry="clinical_trial_matching_task_27"]').click();
    assert.equal(await page.locator('.detail-heading h2').innerText(), heading);
    assert.ok((await page.locator('.case-facts').innerText()).includes('451 candidate trials'));
    await page.goBack();
    await page.waitForFunction(() =>
      document.querySelector('.case-facts')?.textContent.includes('407 candidate trials'),
    );
    await page.reload();
    await page.waitForFunction(() =>
      document.querySelector('.case-facts')?.textContent.includes('407 candidate trials'),
    );
    await page.locator('[data-tab="requirements"]').click();
    assert.ok((await page.locator('#task-panel').innerText()).includes('recall@50'));
    await page.locator('[data-tab="overview"]').click();
    if (process.env.TASK_EXPLORER_SCREENSHOTS) {
      fs.mkdirSync(process.env.TASK_EXPLORER_SCREENSHOTS, { recursive: true });
      await page.screenshot({
        path: resolve(process.env.TASK_EXPLORER_SCREENSHOTS, 'catalogue-desktop.png'),
        fullPage: true,
      });
    }
    // Search looks at task/case meaning, never arbitrary hash fragments in source URLs.
    await page.locator('#search').fill('bcbb8085');
    assert.equal(await page.locator('[data-group]').count(), 0);
    await page.locator('#search').fill(case29);
    assert.equal(await page.locator('[data-definition]').count(), 1);
    await page.locator('[data-definition]').click();
    assert.equal(
      await page.evaluate(() => document.activeElement.dataset.definition),
      clinical,
      'Task selection retains focus',
    );
    assert.equal(
      await page.locator('[data-entry]').count(),
      9,
      'The complete case set stays reachable',
    );
    await page.locator('#search').fill('');
    await page.locator('[data-group="abra"]').focus();
    await page.keyboard.press('Enter');
    assert.equal(
      await page.evaluate(() => document.activeElement.dataset.group),
      'abra',
      'Repository selection retains focus',
    );
    // Related datasets share a task entry, but switching retains the exact output and tier.
    await go(
      'automedbench-full-braintumor-cls-task/1/overview',
      'automedbench-full-braintumor-cls-task',
    );
    assert.equal(
      await page.locator('[data-definition]').count(),
      10,
      'AutoMedBench should have ten task families',
    );
    assert.equal(await page.locator('[data-task="automed-classification"]').count(), 1);
    assert.equal(await page.locator('#task-variant option').count(), 5);
    await page
      .locator('#task-variant')
      .selectOption('automedbench-full-chest-xray-pneumonia-cls-task');
    assert.ok((await page.locator('.deliverable').innerText()).includes('normal, pneumonia'));
    assert.ok(!(await page.locator('.deliverable').innerText()).includes('meningioma'));
    assert.equal(await page.locator('[data-condition="1"]').getAttribute('aria-pressed'), 'true');
    await page.goBack();
    await page.waitForFunction(
      () =>
        document.querySelector('#task-variant')?.value === 'automedbench-full-braintumor-cls-task',
    );
    assert.ok((await page.locator('.deliverable').innerText()).includes('meningioma'));
    await page.locator('#search').fill('classification');
    assert.equal(
      await page.locator('[data-definition]').count(),
      1,
      'Family titles are searchable',
    );
    await page.locator('#search').fill('');
    await go(
      'healthagentbench-predict-hypertension/0/overview',
      'healthagentbench-predict-hypertension',
    );
    assert.equal(await page.locator('#task-variant option').count(), 6);
    assert.equal(await page.locator('[data-task="hab-disease-prediction"]').count(), 1);
    // Search selection, explicit variant changes and restored routes must agree.
    await page.locator('#search').fill('celiac');
    assert.equal(
      await page.locator('.task-detail').getAttribute('data-brief'),
      'healthagentbench-predict-celiac',
    );
    assert.ok(page.url().includes('#healthagentbench-predict-celiac/0/overview?'));
    await page.reload();
    assert.equal(
      await page.locator('.task-detail').getAttribute('data-brief'),
      'healthagentbench-predict-celiac',
    );
    await go(
      'automedbench-full-chest-xray-pneumonia-cls-task/1/overview',
      'automedbench-full-chest-xray-pneumonia-cls-task',
    );
    await page.locator('#search').fill('pneumonia');
    await page.locator('#task-variant').selectOption('automedbench-full-braintumor-cls-task');
    assert.equal(await page.locator('#search').inputValue(), '');
    assert.equal(
      await page.locator('.task-detail').getAttribute('data-brief'),
      'automedbench-full-braintumor-cls-task',
    );
    assert.equal(await page.locator('[data-condition="1"]').getAttribute('aria-pressed'), 'true');
    await page.goBack();
    await page.waitForFunction(
      () =>
        document.querySelector('#task-variant')?.value ===
        'automedbench-full-chest-xray-pneumonia-cls-task',
    );
    await page.locator('#search').fill('pneumonia');
    await go('abra-birads/0/overview', 'abra-birads');
    assert.equal(
      await page.locator('#search').inputValue(),
      '',
      'An explicit route remains visible under an incompatible search',
    );
    // Keyboard tabs and selectors keep focus after the detail DOM is replaced.
    await page.locator('#tab-overview').focus();
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('#tab-requirements').getAttribute('aria-selected'), 'true');
    assert.equal(await page.evaluate(() => document.activeElement.id), 'tab-requirements');
    await page.keyboard.press('End');
    assert.equal(await page.evaluate(() => document.activeElement.id), 'tab-sources');
    await page.locator('#source-picker').selectOption({ index: 1 });
    assert.equal(await page.evaluate(() => document.activeElement.id), 'source-picker');
    await page.locator('#tab-overview').click();
    await page.locator('[data-condition="1"]').click();
    assert.equal(await page.evaluate(() => document.activeElement.dataset.condition), '1');
    // Unmerged workflows remain separate under collapsible navigation groups.
    await go('bcer-short-denoise/0/overview', 'bcer-short-denoise');
    const processing = page.locator('[data-family="repository/bcer/Single processing steps"]');
    assert.equal(await processing.getAttribute('open'), '');
    await processing.locator('summary').click();
    await page.locator('[data-tab="requirements"]').click();
    assert.equal(
      await processing.getAttribute('open'),
      null,
      'Group collapse survives detail rerender',
    );
    await processing.locator('summary').click();
    await processing.locator('[data-definition="bcer-short-superres"]').click();
    assert.equal(
      await page.locator('.task-detail').getAttribute('data-brief'),
      'bcer-short-superres',
    );
    await go('abra/catalogue/oracle_annotation', 'abra');
    assert.equal(await page.locator('[data-condition="1"]').getAttribute('aria-pressed'), 'true');
    await page.locator('[data-tab="examples"]').click();
    await page.locator('[data-visual="answer"]').click();
    await page.locator('[data-tab="overview"]').click();
    await page.locator('[data-condition="0"]').click();
    await page.locator('[data-tab="examples"]').click();
    assert.equal(
      await page.locator('[data-visible-role]').getAttribute('data-visible-role'),
      'input',
    );
    await go('automedbench/task/lite-case-TSG_00000040/0/examples', 'automedbench-tsg', 'examples');
    assert.ok((await page.locator('.scope-note').innerText()).includes('TSG_00000001'));
    if (process.env.TASK_EXPLORER_SCREENSHOTS) {
      for (const [id, name] of [
        ['automedbench-full-braintumor-cls-task', 'automed-families'],
        ['healthagentbench-predict-hypertension', 'health-families'],
      ]) {
        await go(`${id}/0/overview`, id);
        await page.screenshot({
          path: resolve(process.env.TASK_EXPLORER_SCREENSHOTS, name + '.png'),
          fullPage: true,
        });
      }
    }
    // The same legacy case link remains readable at the comment's viewport and on mobile.
    for (const width of [1010, 390]) {
      await page.setViewportSize({ width, height: width === 390 ? 844 : 1324 });
      for (const [hash, id, section] of [
        [`healthagentbench/task/${case29}/0/catalogue`, clinical, 'overview'],
        [
          'automedbench-full-tsg-multiorgan-seg-task/1/brief',
          'automedbench-full-tsg-multiorgan-seg-task',
          'overview',
        ],
        ['imaging101-ssnp-odt/0/overview', 'imaging101-ssnp-odt', 'overview'],
        ['bcer/0/examples', 'bcer', 'examples'],
        ['rexmle/0/sources', 'rexmle', 'sources'],
      ]) {
        await go(hash, id, section);
        assert.equal(
          await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),
          false,
          hash + ' overflows',
        );
      }
      if (width === 390 && process.env.TASK_EXPLORER_SCREENSHOTS) {
        await go(`healthagentbench/task/${case29}/0/catalogue`, clinical);
        await page.screenshot({
          path: resolve(process.env.TASK_EXPLORER_SCREENSHOTS, 'catalogue-mobile.png'),
          fullPage: true,
        });
      }
    }
    // Capability browsing spans repositories while keeping work and research roles separate.
    await page.setViewportSize({ width: 1440, height: 1100 });
    await go('tb3-ct-organ-segmentation/0/overview?view=capability', 'tb3-ct-organ-segmentation');
    assert.equal(await page.locator('#browse').inputValue(), 'capability');
    assert.equal(await page.locator('.repository-heading h1').innerText(), 'Segment images');
    assert.equal(await page.locator('[data-experiment]').count(), 4);
    assert.equal(await page.locator('[data-definition="tb3-segmentation-calibration"]').count(), 0);
    assert.ok(await page.locator('[data-task="automed-segmentation"]').count());
    await page.locator('#agent-work').selectOption('implementation');
    assert.equal(await page.locator('.repository-heading h1').innerText(), 'Segment images');
    assert.equal(await page.locator('[data-definition="tb3-ct-organ-segmentation"]').count(), 0);
    await page.reload();
    assert.equal(await page.locator('#agent-work').inputValue(), 'implementation');
    await page.locator('#lane').selectOption('supporting');
    assert.equal(await page.locator('#agent-work').inputValue(), '');
    assert.equal(
      await page.locator('.task-detail').getAttribute('data-brief'),
      'tb3-segmentation-calibration',
    );
    assert.ok(
      (await page.locator('.task-provenance').innerText()).includes('No general-agent task'),
    );
    await page.locator('#browse').selectOption('repository');
    await page.reload();
    assert.equal(await page.locator('#lane').inputValue(), 'supporting');
    const supportIds = new Set(
      data.entries.filter((e) => e.role && e.role !== 'task').map((e) => e.id),
    );
    for (const id of await page
      .locator('[data-definition]')
      .evaluateAll((nodes) => nodes.map((n) => n.dataset.definition)))
      assert.ok(supportIds.has(id));
    // Every internal experiment stays reachable, including the two scopes of BR-033.
    const internalExperiments = new Set();
    for (const entry of data.entries.filter((e) => e.studies?.length)) {
      await go(`${entry.id}/0/overview?view=capability`, entry.id);
      assert.equal(await page.locator('[data-experiment]').count(), entry.studies.length);
      for (const study of entry.studies) internalExperiments.add(study.id);
    }
    assert.equal(internalExperiments.size, data.experiment_count);
    await go('tb3-dental-v2/1/overview?view=capability', 'tb3-dental-v2');
    await page.locator('#task-variant').selectOption('tb3-dental-v3');
    assert.equal(await page.locator('[data-condition="1"]').getAttribute('aria-pressed'), 'true');
    assert.ok((await page.locator('.condition').innerText()).includes('F018'));
    await go('tb3-ct-organ-segmentation/0/overview?view=capability', 'tb3-ct-organ-segmentation');
    const study = page.locator('[data-experiment="ct-organ-segmentation-astra-medium-litemedsam"]');
    await study.locator('summary').click();
    await study.locator('[data-source]').click();
    assert.ok(
      (await page.locator('#source-content').innerText()).includes(
        'Fixed task and changed capability',
      ),
    );
    await page.goBack();
    await page.waitForFunction(
      () => document.querySelector('#tab-overview')?.getAttribute('aria-selected') === 'true',
    );
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: width === 390 ? 844 : 1100 });
      assert.equal(
        await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),
        false,
      );
      await page.evaluate(() => scrollTo(0, 0));
      if (process.env.TASK_EXPLORER_SCREENSHOTS)
        await page.screenshot({
          path: resolve(process.env.TASK_EXPLORER_SCREENSHOTS, `taxonomy-${width}.png`),
          fullPage: true,
        });
    }
    assert.deepEqual(errors, []);
    assert.deepEqual(requests, []);
    const result = {
      briefs: data.entries.length,
      taskFamilies: new Set(data.entries.map((e) => e.task_family || e.id)).size,
      sourceRecords: records,
      conditions,
      nativeImagesDecoded: images,
      conceptualIllustrations: drawings,
      diagramTypes: diagramTypes.size,
      sourcePreviews,
      portableFallbacks: fallbackDrawings,
      illustratedOverviews: drawings,
      animated3DScenes: drawings,
      motionPauseReducedMotionAndCamera: 'pass',
      singlePassReplayAndCrossfade: 'pass',
      webglUnavailableAndLostFallback: 'pass',
      canvasUnavailableFallback: 'pass',
      offscreenAndNavigationCleanup: 'pass',
      localSources,
      sourceReader: 'pass',
      keyboardFocus: 'pass',
      groupedTaskList: 'pass',
      datasetVariants: 'pass',
      caseDifferences: 'pass',
      legacyLinksAndBack: 'pass',
      collapsedProvenance: 'pass',
      search: 'pass',
      referenceReveal: 'pass',
      capabilityNavigation: 'pass',
      supportingResearch: 'pass',
      internalExperiments: internalExperiments.size,
      mobile: 'pass',
      pageErrors: errors,
      remoteRequests: requests,
    };
    if (report) {
      const p = resolve(report);
      fs.mkdirSync(dirname(p), { recursive: true });
      fs.writeFileSync(p, JSON.stringify(result, null, 2) + '\n');
    }
    console.log(JSON.stringify(result));
  } finally {
    await context.close();
  }
}

module.exports = { checkExplorer };
if (require.main === module) {
  withBrowser((browser) =>
    checkExplorer(browser, process.argv[2] || 'runs/task-explorer/index.html', process.argv[3]),
  ).catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}
