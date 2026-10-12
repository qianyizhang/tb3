/** Native CT/MRA/landmark matrix integrated into the existing browser run; never launches a browser. */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import type { Browser, BrowserContext, Page } from 'playwright';
import { captureComposedFrame } from '../presentation/tooling/media/capture.mts';

type Adapter = 'ct' | 'mra' | 'landmark' | 'mri';
interface Entry {
  entry_id: string;
  story_id: string;
  recipe: string;
}
interface Beat {
  id: string;
  state: string | null;
  reference: boolean;
  startFrame: number;
  endFrame: number;
}
interface Plan {
  id: string;
  recipe: string;
  fps: number;
  durationFrames: number;
  beats: Beat[];
}
interface FrameRow {
  locale: string;
  frame: number;
  file: string;
  sha256: string;
}
interface StoryRow {
  id: string;
  frames: FrameRow[];
  locales: string[];
  fallback: boolean;
  native: true;
  adapter: Adapter;
  html_sha256: string;
  plan_sha256: string;
  interactiveReferenceReset: boolean;
  mobile: boolean;
}
interface MatrixReport {
  stories: unknown[];
  navigation: unknown[];
  errors: string[];
  remote_requests: string[];
}
export interface NativeTraceMatrixOptions {
  folder: string;
  explorer: string;
  entries: Entry[];
  report: MatrixReport;
}
const sha = (bytes: Buffer) => createHash('sha256').update(bytes).digest('hex');
const rootSelector = '.scene-player[data-family="native-trace"]';
const stageSelector = '[data-native-ready][data-native-state]';
const stageReady = (page: Page) =>
  page.waitForSelector(`${stageSelector}[data-native-ready="true"]`);

async function noReference(page: Page) {
  assert.equal(
    await page.locator('[data-native-reference-result]').count(),
    0,
    'Private reference result leaked',
  );
  assert.equal(await page.locator(rootSelector).getAttribute('data-reference-shown'), 'false');
  const landmark = page.locator(
    '[data-native-adapter="ct-landmarks"] [data-native-reference-count]',
  );
  if (await landmark.count())
    assert.equal(await landmark.getAttribute('data-native-reference-count'), '0');
  const mri = page.locator('[data-native-adapter="longitudinal-mri"] [data-reference-visible]');
  if (await mri.count()) assert.equal(await mri.getAttribute('data-reference-visible'), 'false');
  const ct = page.locator('[data-native-reference]');
  if (await ct.count()) assert.equal(await ct.getAttribute('data-native-reference'), 'hidden');
}
async function chapter(page: Page, plan: Plan, index: number) {
  await page.locator(`[data-story-step="${index}"]`).click();
  await page.waitForFunction(
    ({ id, root }) => document.querySelector(root)?.getAttribute('data-beat') === id,
    { id: plan.beats[index].id, root: rootSelector },
  );
  await stageReady(page);
}
async function checkNativeData(page: Page, adapter: Adapter, fallback = false) {
  await stageReady(page);
  const role = page.locator(
    adapter === 'ct'
      ? '[role="img"][aria-label^="Native CT volume"]'
      : adapter === 'mri'
        ? '[role="img"][aria-label*="whole MRI in its native RAS grid"]'
        : adapter === 'landmark'
          ? '[role="img"][aria-label^="CT crop in physical RAS"]'
          : '[role="img"][aria-label^="Native MRA vessel mask"]',
  );
  assert.equal(await role.count(), 1);
  assert.equal(
    await page.locator(stageSelector).getAttribute('data-native-renderer'),
    fallback ? 'poster' : 'webgl',
  );
  const gpu = role.locator('canvas');
  assert.equal(
    await gpu.count(),
    fallback ? 0 : 1,
    'Native GPU canvas presence differs from requested mode',
  );
  if (!fallback) {
    assert.equal(
      await gpu.evaluate(
        (canvas: HTMLCanvasElement) => canvas.isConnected && canvas.width > 0 && canvas.height > 0,
      ),
      true,
    );
    if (adapter === 'ct')
      assert.equal(await role.locator('span').count(), 6, 'CT axis labels detached');
    // A screenshot verifies drawn pixels rather than a ready flag or an unrelated planar clock.
    const png = await role.screenshot({ animations: 'disabled' });
    const differingPixels = await page.evaluate(async (encoded) => {
      const image = new Image();
      image.src = `data:image/png;base64,${encoded}`;
      await image.decode();
      const canvas = document.createElement('canvas');
      canvas.width = image.width;
      canvas.height = image.height;
      const ctx = canvas.getContext('2d')!;
      ctx.drawImage(image, 0, 0);
      const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
      const counts = new Map<number, number>();
      for (let i = 0; i < pixels.length; i += 4) {
        const key = (pixels[i] >> 4) * 256 + (pixels[i + 1] >> 4) * 16 + (pixels[i + 2] >> 4);
        counts.set(key, (counts.get(key) ?? 0) + 1);
      }
      return {
        changed: canvas.width * canvas.height - Math.max(...counts.values()),
        total: canvas.width * canvas.height,
      };
    }, png.toString('base64'));
    assert.ok(
      differingPixels.changed > differingPixels.total * 0.01,
      'Native volume screenshot is blank or nearly uniform',
    );
  }
  // Retained scalar arrays must reach the actual native canvas, not a substitute illustration.
  const nativePixels = await page.locator(`${stageSelector} canvas`).evaluateAll(
    (elements) =>
      elements.filter((element) => {
        const canvas = element as HTMLCanvasElement;
        // Leave WebGL canvas untouched: asking for 2D cannot switch its existing context.
        const ctx = canvas.getContext('2d');
        if (!ctx) return false;
        const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
        let min = 255,
          max = 0;
        for (let index = 0; index < pixels.length; index += 4) {
          min = Math.min(min, pixels[index]);
          max = Math.max(max, pixels[index]);
        }
        return max - min > 20;
      }).length,
  );
  assert.ok(
    nativePixels >= (adapter === 'mra' ? 1 : 3),
    'Native slice canvases contain no scalar image data',
  );
  if (adapter === 'landmark')
    assert.equal(
      await page.locator(stageSelector).getAttribute('data-native-shape'),
      '512,512,920',
    );
  if (
    (adapter === 'landmark' || adapter === 'mri') &&
    new URL(page.url()).searchParams.has('capture')
  ) {
    const footer = await page.locator('.scene-reset').boundingBox();
    const resultNode = page.locator('[data-native-reference-result]');
    const result = (await resultNode.count()) ? await resultNode.boundingBox() : null;
    const ceiling = result?.y ?? footer!.y - 5;
    if (adapter === 'mri') {
      for (const card of await page.locator(`${stageSelector} > div:last-of-type > div`).all()) {
        const box = await card.boundingBox();
        assert.ok(box && box.y + box.height <= ceiling, 'MRI card overlaps result or footer');
      }
    }
    for (const slider of await page.locator(`${stageSelector} input[type="range"]`).all()) {
      const box = await slider.locator('..').boundingBox();
      assert.ok(
        box && box.y + box.height <= ceiling,
        'Native slice/readout clipped by result or footer',
      );
    }
  }
  if (adapter === 'mra')
    assert.equal(await page.locator(stageSelector).getAttribute('data-native-shape'), '187,132,53');
}
async function controls(page: Page, plan: Plan, adapter: Adapter) {
  if (adapter === 'ct') {
    const sliders = page.locator(`${stageSelector} input[type="range"]`);
    assert.equal(await sliders.count(), 3);
    for (const slider of await sliders.all()) {
      const before = await slider.inputValue();
      await slider.focus();
      await slider.press('ArrowRight');
      assert.notEqual(await slider.inputValue(), before);
    }
    const coarse = plan.beats.findIndex((beat) => beat.state === 'coarse');
    assert.ok(coarse >= 0);
    await chapter(page, plan, coarse);
    await page.getByRole('button', { name: 'Difference', exact: true }).click();
    await stageReady(page);
    assert.equal(
      await page.getByAltText('Absolute target-candidate difference amplified four times').count(),
      1,
    );
  } else if (adapter === 'mri') {
    const stage = page.locator(stageSelector);
    assert.equal(await stage.getAttribute('data-native-registered'), 'false');
    assert.equal(await stage.getAttribute('data-native-bbox-visible'), 'false');
    assert.equal(await stage.getAttribute('data-native-citation-count'), '0');
    const visits = page.getByLabel('MRI visit', { exact: true });
    await visits.selectOption('V2');
    await stageReady(page);
    assert.equal(await stage.getAttribute('data-native-shape'), '512,512,100');
    await page.getByLabel('MRI dynamic ordinal', { exact: true }).selectOption('7');
    await stageReady(page);
    assert.equal(await stage.getAttribute('data-native-series'), 'S122');
    assert.equal(await stage.getAttribute('data-native-phase'), '0');
    await page.getByLabel('MRI native slice axis', { exact: true }).selectOption('0');
    const slider = page.getByLabel('MRI native slice index', { exact: true });
    const before = await slider.inputValue();
    await slider.focus();
    await slider.press('ArrowRight');
    assert.notEqual(await slider.inputValue(), before);
    await visits.selectOption('V1');
    await stageReady(page);
    assert.equal(await stage.getAttribute('data-native-shape'), '512,512,106');
    await chapter(page, plan, 2);
    assert.equal(await page.getByAltText('Exact delivered MRI PNG at step 18').count(), 1);
    await chapter(page, plan, 3);
    await visits.selectOption('V1');
    await stageReady(page);
    assert.equal(await stage.getAttribute('data-native-reader-ijk'), '390,270,60');
    await visits.selectOption('V2');
    await stageReady(page);
    assert.equal(await stage.getAttribute('data-native-reader-ijk'), '386,302,64');
    assert.equal(await stage.getAttribute('data-native-citation-count'), '0');
    await chapter(page, plan, 4);
    assert.equal(await stage.getAttribute('data-native-bbox-visible'), 'true');
    assert.equal(await stage.getAttribute('data-native-citation-count'), '0');
    await chapter(page, plan, 5);
    assert.equal(await stage.getAttribute('data-native-visit'), 'V2');
    assert.equal(await stage.getAttribute('data-native-citation-count'), '2');
    assert.equal(await stage.getAttribute('data-reference-visible'), 'false');
  } else if (adapter === 'landmark') {
    const stage = page.locator(stageSelector);
    assert.equal(await stage.getAttribute('data-native-saved-visible'), 'false');
    assert.equal(await stage.getAttribute('data-native-reference-count'), '0');
    for (const axis of ['i', 'j', 'k']) {
      const slider = page.getByLabel(`Native ${axis} slice`, { exact: true });
      const before = await slider.inputValue();
      await slider.focus();
      await slider.press('ArrowRight');
      assert.notEqual(await slider.inputValue(), before);
    }
    await chapter(page, plan, 2);
    const inspections = page.getByLabel('Recorded inspection', { exact: true });
    await inspections.waitFor({ state: 'visible' });
    const alternatives = await inspections
      .locator('option')
      .evaluateAll((nodes) => nodes.map((node) => (node as HTMLOptionElement).value));
    assert.ok(alternatives.length >= 3, 'Recorded plane/slab choices missing');
    await inspections.selectOption(alternatives.at(-1)!);
    assert.equal(await stage.getAttribute('data-native-state'), alternatives.at(-1));
    assert.equal(await stage.getAttribute('data-native-reference-count'), '0');
    await chapter(
      page,
      plan,
      plan.beats.findIndex((b) => b.state === 'saved'),
    );
    assert.equal(await stage.getAttribute('data-native-saved-visible'), 'true');
    const names = page.getByLabel('Saved name', { exact: true });
    await names.selectOption('T4');
    assert.equal(await stage.getAttribute('data-native-selected-status'), 'observed');
    assert.equal(await stage.getAttribute('data-native-selected-ijk'), '269.8,154.6,906.1');
    const ras = (await stage.getAttribute('data-native-selected-ras'))!.split(',').map(Number);
    assert.ok(Math.abs(ras[0] - (181.640625 - 0.71875 * 269.8)) < 1e-6);
    assert.ok(Math.abs(ras[2] - (-1546.11474609375 + 0.70001220703125 * 906.1)) < 1e-6);
    await names.selectOption('C1');
    assert.equal(await stage.getAttribute('data-native-selected-status'), 'out_of_fov');
    assert.equal(await stage.getAttribute('data-native-point-count'), '0');
    await names.selectOption('T13');
    assert.equal(await stage.getAttribute('data-native-selected-status'), 'absent');
    assert.equal(await stage.getAttribute('data-native-selected-ijk'), '');
  } else {
    await chapter(page, plan, 2);
    await page.getByLabel('Recorded threshold').selectOption('150');
    assert.equal(await page.locator(stageSelector).getAttribute('data-native-additions'), '247');
    await chapter(page, plan, 3);
    assert.equal(await page.locator(stageSelector).getAttribute('data-native-contacts'), '65');
    await chapter(page, plan, 4);
    assert.equal(await page.locator(stageSelector).getAttribute('data-native-additions'), '198');
    assert.equal(await page.locator(stageSelector).getAttribute('data-native-state'), 'saved');
  }
  await noReference(page);
}
async function referenceAndReset(page: Page, plan: Plan) {
  const index = plan.beats.findIndex((beat) => beat.reference);
  assert.ok(index >= 0);
  await chapter(page, plan, index);
  await noReference(page);
  await page.locator('[data-native-reference-reveal]').click();
  await stageReady(page);
  assert.equal(await page.locator('[data-native-reference-result]').count(), 1);
  assert.equal(await page.locator(rootSelector).getAttribute('data-reference-shown'), 'true');
  if (await page.locator('[data-native-adapter="ct-landmarks"]').count()) {
    assert.ok(
      Number(await page.locator(stageSelector).getAttribute('data-native-reference-count')) >= 1,
    );
    assert.match(await page.locator('[data-native-reference-result]').innerText(), /1 \/ 13/);
  }
  await chapter(page, plan, 0);
  await noReference(page);
  await chapter(page, plan, index);
  await noReference(page);
  await page.locator('[data-native-reference-reveal]').click();
  await stageReady(page);
  await page.locator('.scene-reset').click();
  await page.waitForFunction(
    ({ id, root }) => {
      const player = document.querySelector(root);
      return (
        player?.getAttribute('data-beat') === id &&
        player.getAttribute('data-committed-frame') === '0'
      );
    },
    { id: plan.beats[0].id, root: rootSelector },
  );
  await stageReady(page);
  await noReference(page);
  await chapter(page, plan, index);
  await noReference(page);
}
async function mobile(page: Page, plan: Plan, path: string) {
  await page.setViewportSize({ width: 390, height: 844 });
  await chapter(page, plan, 2);
  assert.equal(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
    true,
    'Native reader overflows at 390px',
  );
  await noReference(page);
  await page.screenshot({ path, fullPage: true });
}
async function context(
  browser: Browser,
  report: MatrixReport,
  noGpu = false,
): Promise<BrowserContext> {
  const result = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    deviceScaleFactor: 1,
    reducedMotion: 'reduce',
  });
  await result.route(/^https?:/, (route) => {
    report.remote_requests.push(route.request().url());
    return route.abort();
  });
  if (noGpu)
    await result.addInitScript(() => {
      const original = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function (
        this: HTMLCanvasElement,
        type: string,
        ...args: unknown[]
      ) {
        if (type === 'webgl' || type === 'webgl2' || type === 'experimental-webgl') return null;
        return Reflect.apply(original, this, [type, ...args]);
      } as typeof original;
    });
  result.on('page', (page) => page.on('pageerror', (error) => report.errors.push(error.message)));
  return result;
}

export async function checkNativeTraceMatrix(
  browser: Browser,
  options: NativeTraceMatrixOptions,
): Promise<void> {
  const entries = options.entries.filter((entry) => entry.recipe === 'native-trace-v1');
  if (!entries.length) return;
  const { report } = options;
  const errorStart = report.errors.length,
    remoteStart = report.remote_requests.length;
  const standard = await context(browser, report);
  const noGpu = await context(browser, report, true);
  const explorerPage = await standard.newPage();
  try {
    for (const entry of entries) {
      const out = resolve(options.folder, entry.story_id);
      mkdirSync(out, { recursive: true });
      const rawPlan = readFileSync(join(out, 'plan.json'));
      const plan = JSON.parse(rawPlan.toString()) as Plan;
      assert.equal(plan.recipe, 'native-trace-v1');
      assert.equal(plan.id, entry.story_id);
      const url = pathToFileURL(join(out, 'index.html')).href;
      const page = await standard.newPage();
      const row: StoryRow = {
        id: plan.id,
        frames: [],
        locales: [],
        fallback: false,
        native: true,
        adapter: 'ct',
        html_sha256: sha(readFileSync(join(out, 'index.html'))),
        plan_sha256: sha(rawPlan),
        interactiveReferenceReset: false,
        mobile: false,
      };
      try {
        for (const locale of ['en', 'zh-CN']) {
          await page.setViewportSize({ width: 1280, height: 720 });
          await page.goto(`${url}?capture=1&lang=${locale}`);
          await page.waitForFunction(() => !!window.__tb3ExplainerCapture);
          await stageReady(page);
          const adapter = await page.locator(rootSelector).getAttribute('data-native-adapter');
          assert.ok(
            adapter === 'ct-pose' ||
              adapter === 'mra-repair' ||
              adapter === 'ct-landmarks' ||
              adapter === 'longitudinal-mri',
          );
          const nativeAdapter: Adapter =
            adapter === 'ct-pose'
              ? 'ct'
              : adapter === 'ct-landmarks'
                ? 'landmark'
                : adapter === 'longitudinal-mri'
                  ? 'mri'
                  : 'mra';
          row.adapter = nativeAdapter;
          for (const frame of [0, plan.durationFrames - 1]) {
            const png = await captureComposedFrame(page, {
              frame,
              fps: plan.fps,
              width: 1280,
              height: 720,
            });
            const file = `review-${locale}-${frame}.png`;
            writeFileSync(join(out, file), png);
            row.frames.push({ locale, frame, file, sha256: sha(png) });
            await checkNativeData(page, nativeAdapter);
            assert.equal(
              await page.locator(rootSelector).getAttribute('data-committed-frame'),
              String(frame),
            );
            if (frame === 0) await noReference(page);
            else
              assert.equal(
                await page.locator('[data-native-reference-result]').count(),
                1,
                'Canonical authored reference endpoint missing',
              );
          }
          if (locale === 'zh-CN') {
            const note = page.locator('[data-native-source-language]');
            assert.equal(await note.count(), 1);
            assert.equal(await note.getAttribute('lang'), 'zh-CN');
            assert.match(await note.innerText(), /英语|英文/);
          }
          row.locales.push(locale);
          await page.setViewportSize({ width: 1280, height: 900 });
          await page.goto(`${url}?lang=${locale}`);
          await stageReady(page);
          await checkNativeData(page, nativeAdapter);
          await controls(page, plan, nativeAdapter);
          await referenceAndReset(page, plan);
          await mobile(page, plan, join(out, `native-mobile-${locale}.png`));
          await explorerPage.setViewportSize({ width: 1280, height: 900 });
          await explorerPage.goto(
            pathToFileURL(resolve(options.explorer)).href +
              `?lang=${locale}#${entry.entry_id}/0/overview?view=repository`,
          );
          await stageReady(explorerPage);
          assert.equal(
            await explorerPage.locator(rootSelector).getAttribute('data-native-adapter'),
            adapter,
          );
          assert.equal(
            await explorerPage.evaluate(() => typeof window.__tb3ExplainerCapture),
            'undefined',
          );
          if (locale === 'zh-CN') {
            const note = explorerPage.locator('[data-native-source-language]');
            assert.equal(await note.count(), 1);
            assert.equal(await note.getAttribute('lang'), 'zh-CN');
            assert.match(await note.innerText(), /英语|英文/);
          }
          await checkNativeData(explorerPage, nativeAdapter);
          await controls(explorerPage, plan, nativeAdapter);
          await referenceAndReset(explorerPage, plan);
          await mobile(explorerPage, plan, join(out, `native-explorer-mobile-${locale}.png`));
        }
        row.interactiveReferenceReset = row.mobile = true;
        const fallback = await noGpu.newPage();
        try {
          for (const location of [
            url,
            pathToFileURL(resolve(options.explorer)).href +
              `#${entry.entry_id}/0/overview?view=repository`,
          ]) {
            await fallback.goto(location);
            await checkNativeData(fallback, row.adapter, true);
            await controls(fallback, plan, row.adapter);
            await referenceAndReset(fallback, plan);
            await fallback.screenshot({
              path: join(out, location === url ? 'no-gpu.png' : 'native-explorer-no-gpu.png'),
              fullPage: true,
            });
          }
        } finally {
          await fallback.close();
        }
        row.fallback = true;
        report.stories.push(row);
        report.navigation.push({
          id: entry.entry_id,
          native: true,
          chaptersAndReferenceReset: true,
          mobile: true,
          locales: row.locales,
          fallback: true,
        });
        // Switch from a revealed reference in the previous native entry to the next.
        if (entries.length < 2) {
          report.navigation.push({
            id: entry.entry_id,
            switchCoverage: 'not-applicable-single-entry',
          });
          continue;
        }
        const reference = plan.beats.findIndex((beat) => beat.reference);
        await explorerPage.setViewportSize({ width: 1280, height: 900 });
        await chapter(explorerPage, plan, reference);
        await explorerPage.locator('[data-native-reference-reveal]').click();
        await stageReady(explorerPage);
        const next = entries[(entries.indexOf(entry) + 1) % entries.length];
        await explorerPage.evaluate((id) => {
          location.hash = `${id}/0/overview?view=repository`;
        }, next.entry_id);
        const nextPlan = JSON.parse(
          readFileSync(join(options.folder, next.story_id, 'plan.json'), 'utf8'),
        ) as Plan;
        await explorerPage.waitForFunction(
          ({ id, root }) =>
            document.querySelector(root)?.getAttribute('data-beat') === id &&
            document.querySelector('[data-native-reference-result]') === null,
          { id: nextPlan.beats[0].id, root: rootSelector },
        );
        await stageReady(explorerPage);
        await noReference(explorerPage);
        report.navigation.push({
          id: entry.entry_id,
          switchedTo: next.entry_id,
          referenceLeakage: false,
        });
      } finally {
        await page.close();
      }
    }
    assert.deepEqual(report.errors.slice(errorStart), []);
    assert.deepEqual(report.remote_requests.slice(remoteStart), []);
  } finally {
    await standard.close();
    await noGpu.close();
  }
}
