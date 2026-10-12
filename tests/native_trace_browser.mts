/** Opt-in native reader checks against locally packaged retained assets; no trials. */
import assert from 'node:assert/strict';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { createHash } from 'node:crypto';
import { serveDirectory, withBrowser } from '../presentation/tooling/browser.mts';
import type {} from '../presentation/frontend/capture.ts';

const root = resolve(process.argv[2] || '.local/anatomy-pose');
const output = resolve(process.argv[3] || join(root, `native-reader-review-${Date.now()}`));
mkdirSync(output, { recursive: true });
const server = await serveDirectory(root);
const results: object[] = [];
try {
  await withBrowser(async (browser) => {
    for (const adapter of ['ct', 'mra']) {
      const folder = `native-${adapter}-review`;
      const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
      const errors: string[] = [];
      page.on('pageerror', (error) => errors.push(error.message));
      const ready = () => page.waitForSelector('[data-native-ready="true"]');
      const chapter = async (index: number) => {
        await page.locator(`[data-story-step="${index}"]`).click();
        await ready();
      };
      await page.goto(server.url + folder + '/');
      await ready();
      assert.equal(await page.locator('[data-native-reference-result]').count(), 0);
      if (adapter === 'ct') {
        assert.equal(
          await page
            .getByRole('img', { name: /Native CT volume/ })
            .locator('canvas')
            .count(),
          1,
        );
        assert.equal(
          await page
            .getByRole('img', { name: /Native CT volume/ })
            .locator('span')
            .count(),
          6,
        );
        assert.equal(await page.locator('input[type="range"]').count(), 3);
        for (const slider of await page.locator('input[type="range"]').all()) {
          await slider.focus();
          const before = await slider.inputValue();
          await slider.press('ArrowRight');
          assert.notEqual(await slider.inputValue(), before);
        }
        await chapter(3);
        assert.equal(
          await page.locator('[data-native-state]').getAttribute('data-native-state'),
          'coarse',
        );
        await page.getByRole('button', { name: 'Difference', exact: true }).click();
        assert.equal(
          await page
            .getByAltText('Absolute target-candidate difference amplified four times')
            .count(),
          1,
        );
      } else {
        assert.equal(
          await page.locator('[data-native-shape]').getAttribute('data-native-shape'),
          '187,132,53',
        );
        await chapter(2);
        await page.getByLabel('Recorded threshold').selectOption('150');
        assert.equal(
          await page.locator('[data-native-additions]').getAttribute('data-native-additions'),
          '247',
        );
        await chapter(3);
        assert.equal(
          await page.locator('[data-native-contacts]').getAttribute('data-native-contacts'),
          '65',
        );
        await chapter(4);
        assert.equal(
          await page.locator('[data-native-additions]').getAttribute('data-native-additions'),
          '198',
        );
        assert.equal(
          await page.locator('[data-native-state]').getAttribute('data-native-state'),
          'saved',
        );
      }
      await page.screenshot({ path: join(output, `${adapter}-desktop.png`), fullPage: true });
      await chapter(5);
      assert.equal(await page.locator('[data-native-reference-result]').count(), 0);
      await page.locator('[data-native-reference-reveal]').click();
      assert.equal(await page.locator('[data-native-reference-result]').count(), 1);
      await page.locator('.scene-reset').click();
      await ready();
      await chapter(5);
      assert.equal(await page.locator('[data-native-reference-result]').count(), 0);
      await page.setViewportSize({ width: 390, height: 844 });
      await chapter(2);
      assert.equal(
        await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
        true,
      );
      await page.screenshot({ path: join(output, `${adapter}-mobile.png`), fullPage: true });
      await page.goto(server.url + folder + '/?no3d=1');
      await ready();
      assert.equal(
        await page.locator('input[type="range"]:enabled').count(),
        adapter === 'ct' ? 3 : 1,
      );
      await page.screenshot({ path: join(output, `${adapter}-fallback.png`), fullPage: true });
      await page.setViewportSize({ width: 1280, height: 720 });
      await page.goto(server.url + folder + '/?capture=1');
      await page.waitForFunction(() => !!window.__tb3ExplainerCapture);
      for (const frame of [0, 480, 768]) {
        await page.evaluate(async (frame) => {
          await window.__tb3ExplainerCapture!.seekFrame({
            frame,
            fps: 24,
            width: 1280,
            height: 720,
          });
        }, frame);
        assert.equal(
          await page.locator('.scene-player').getAttribute('data-committed-frame'),
          String(frame),
        );
        const bounds = await page.locator('.scene-player').boundingBox();
        assert.equal(bounds?.height, 720);
        if (adapter === 'ct')
          assert.equal(
            await page
              .getByRole('img', { name: /Native CT volume/, includeHidden: true })
              .locator('canvas')
              .count(),
            1,
          );
        assert.equal(
          await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          true,
        );
        await page.screenshot({ path: join(output, `${adapter}-frame-${frame}.png`) });
      }
      assert.deepEqual(errors, []);
      const bytes = readFileSync(join(root, folder, 'index.html'));
      results.push({
        adapter,
        html_sha256: createHash('sha256').update(bytes).digest('hex'),
        checks: 'passed',
        package: JSON.parse(readFileSync(join(root, folder, 'package.json'), 'utf8')),
      });
      await page.close();
    }
  });
  writeFileSync(
    join(output, 'receipt.json'),
    JSON.stringify({ schema: 1, results }, null, 2) + '\n',
  );
  console.log(
    'CT and MRA shared reader: interaction, reference reset, native state, mobile, fallback and canonical captures passed.',
  );
} finally {
  await server.close();
}
