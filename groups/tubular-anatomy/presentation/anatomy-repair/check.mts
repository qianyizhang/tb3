import { fileURLToPath } from 'node:url';
import { withBrowser, serveDirectory } from '../../../../presentation/tooling/browser.mts';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const out = fileURLToPath(new URL('../../../../.local/anatomy-pose/vessel/', import.meta.url));
const server = await serveDirectory(out);
const report = { checks: [], errors: [], requests: [] };
try {
  await withBrowser(async (browser) => {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1100 },
      reducedMotion: 'reduce',
    });
    page.on('pageerror', (e) => report.errors.push(e.message));
    page.on('request', (r) => {
      if (
        !r.url().startsWith(server.url) &&
        !r.url().startsWith('data:') &&
        !r.url().startsWith('blob:')
      )
        report.requests.push(r.url());
    });
    await page.goto(server.url);
    await page.waitForFunction(() => window.vesselViewer?.ready);
    assert.equal(await page.evaluate(() => window.vesselViewer.webgl), true);
    assert.equal(await page.locator('#score').isVisible(), false);
    assert.equal(await page.evaluate(() => window.vesselViewer.count), 0);
    await page.screenshot({ path: out + 'input.png', fullPage: true });
    for (const phase of [1, 2, 3, 4, 5]) {
      await page.locator(`[data-phase="${phase}"]`).click();
      assert.equal(await page.evaluate(() => window.vesselViewer.phase), phase);
      assert.equal(await page.locator('#score').isVisible(), phase === 5);
      if (phase === 2) {
        for (const [index, count] of [
          [0, 247],
          [1, 212],
          [2, 198],
          [3, 186],
          [4, 178],
          [5, 170],
          [6, 155],
          [7, 122],
          [8, 89],
        ]) {
          await page.locator('#threshold').fill(String(index));
          await page.locator('#threshold').dispatchEvent('input');
          assert.equal(await page.evaluate(() => window.vesselViewer.count), count);
        }
        await page.locator('#chosen').click();
        assert.equal(await page.evaluate(() => window.vesselViewer.threshold), 165);
      }
      if (phase === 3)
        assert.deepEqual(await page.evaluate(() => window.vesselViewer.contactSizes), [32, 33]);
      await page.screenshot({ path: out + `phase-${phase}.png`, fullPage: true });
    }
    report.checks.push(
      'All phases; evaluator reference only at final reveal; nine logged threshold counts; 32/33 contact patches',
    );
    for (const [axis, max] of [
      [0, 186],
      [1, 131],
      [2, 52],
    ]) {
      await page.locator('#axis').selectOption(String(axis));
      for (const value of [0, max]) {
        await page.locator('#slice').fill(String(value));
        await page.locator('#slice').dispatchEvent('input');
        assert.equal(await page.evaluate((a) => window.vesselViewer.positions[a], axis), value);
      }
    }
    await page.locator('#site').click();
    await page.locator('#axis').selectOption('2');
    await page.locator('#missed').click();
    assert.deepEqual(await page.evaluate(() => window.vesselViewer.positions), [62, 75, 13]);
    await page.locator('#missed').click();
    assert.deepEqual(await page.evaluate(() => window.vesselViewer.positions), [64, 72, 16]);
    await page.locator('#add-visible').uncheck();
    assert.equal(await page.evaluate(() => window.vesselViewer.count), 0);
    await page.locator('#add-visible').check();
    assert.equal(await page.evaluate(() => window.vesselViewer.count), 198);
    await page.locator('#site').click();
    await page.locator('#slice').focus();
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.evaluate(() => window.vesselViewer.positions[2]), 16);
    await page.locator('#site').click();
    await page.locator('#overview').click();
    assert.equal(await page.evaluate(() => window.vesselViewer.focus), false);
    await page.locator('#scene').focus();
    await page.keyboard.press('ArrowLeft');
    await page.keyboard.press('Home');
    await page.locator('#focus').click();
    assert.equal(await page.evaluate(() => window.vesselViewer.focus), true);
    await page.locator('#detail').uncheck();
    await page.locator('#detail').check();
    report.checks.push(
      'Native slice bounds on all three axes; keyboard; whole-volume/local view; image crop toggle',
    );
    const geometry = await page.evaluate(() => window.vesselGeometry);
    const data = JSON.parse(fs.readFileSync(out + 'data.json', 'utf8'));
    const p = data.affine
      .slice(0, 3)
      .map((r) =>
        r.slice(0, 3).reduce((s, v, i) => s + v * (data.seed[i] - (data.shape[i] - 1) / 2), 0),
      );
    [p[0], p[2], -p[1]].forEach((x, i) => assert.ok(Math.abs(geometry.seedScene[i] - x) < 1e-9));
    report.checks.push('Native seed transformed through full oblique NIfTI affine');
    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForTimeout(250);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.screenshot({ path: out + 'phone.png', fullPage: true });
    await page.goto(server.url + '?no3d=1');
    await page.waitForFunction(() => window.vesselViewer?.ready);
    assert.equal(await page.evaluate(() => window.vesselViewer.webgl), false);
    await page.locator('[data-phase="2"]').click();
    await page.locator('#chosen').click();
    assert.equal(await page.evaluate(() => window.vesselViewer.count), 198);
    await page.screenshot({ path: out + 'fallback.png', fullPage: true });
    report.checks.push(
      '390px layout without overflow; static no-WebGL fallback retains source images and threshold controls',
    );
    assert.deepEqual(report.errors, []);
    assert.deepEqual(report.requests, []);
  });
  fs.writeFileSync(out + 'browser-check.json', JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
} finally {
  await server.close();
}
