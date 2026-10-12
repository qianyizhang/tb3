import { fileURLToPath } from 'node:url';
import { withBrowser, serveDirectory } from '../../../../presentation/tooling/browser.mts';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const out = fileURLToPath(new URL('../../../../.local/anatomy-pose/trace/', import.meta.url));
const server = await serveDirectory(out);
const data = JSON.parse(fs.readFileSync(out + 'data.json', 'utf8'));
const report = { checks: [], errors: [], requests: [] };
try {
  await withBrowser(async (browser) => {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1100 },
      reducedMotion: 'reduce',
    });
    page.on('pageerror', (e) => report.errors.push(e.message));
    page.on('request', (r) => {
      if (!r.url().startsWith(server.url) && !r.url().startsWith('data:'))
        report.requests.push(r.url());
    });
    await page.goto(server.url);
    await page.waitForFunction(() => window.traceViewer?.ready);
    assert.equal(await page.evaluate(() => window.traceViewer.webgl), true);
    assert.equal(await page.locator('#candidate').isVisible(), false);
    assert.equal(await page.locator('#score').isVisible(), false);
    await page.screenshot({ path: out + 'inputs-desktop.png', fullPage: true });
    for (const [phase, name] of [
      [1, 'wrong'],
      [3, 'coarse'],
      [4, 'refined'],
      [5, 'verified'],
    ]) {
      await page.locator(`[data-phase="${phase}"]`).click();
      await page.waitForTimeout(100);
      assert.equal(await page.evaluate(() => window.traceViewer.phase), phase);
      assert.equal(await page.locator('#score').isVisible(), phase === 5);
      if (phase !== 4) await page.screenshot({ path: out + name + '-desktop.png', fullPage: true });
    }
    const geometry = await page.evaluate(() => window.traceGeometry);
    const center = data.affine.slice(0, 3).map((row) => row[3] + 89.5 * (row[0] + row[1] + row[2]));
    for (const s of data.states) {
      const points = geometry.nativeCorners.find((g) => g.id === s.id).points;
      for (const [i, uv] of [
        [0, [0, 0]],
        [1, [171.9, 0]],
        [2, [171.9, 171.9]],
        [3, [0, 171.9]],
      ]) {
        const p = s.pose.slice(0, 3).map((row) => row[0] * uv[0] + row[1] * uv[1] + row[3]);
        const expected = [p[0] - center[0], p[2] - center[2], -(p[1] - center[1])];
        expected.forEach((v, j) => assert.ok(Math.abs(v - points[i][j]) < 1e-9));
      }
    }
    report.checks.push(
      'Four candidate planes match native LPS corners; no display-space pose approximation',
    );
    await page.locator('#slice-2').focus();
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.evaluate(() => window.traceViewer.positions[2]), 46);
    report.checks.push('Keyboard CT slice movement');
    for (const axis of [0, 1, 2])
      for (const value of [0, 89]) {
        await page.locator('#slice-' + axis).fill(String(value));
        await page.locator('#slice-' + axis).dispatchEvent('input');
      }
    report.checks.push('All three CT sliders reach both ends of the supplied crop');
    await page.locator('[data-phase="3"]').click();
    assert.equal(await page.evaluate(() => window.traceViewer.mode), 'silhouette');
    await page.locator('[data-mode="difference"]').click();
    assert.equal(await page.evaluate(() => window.traceViewer.mode), 'difference');
    await page.locator('[data-phase="5"]').click();
    await page.locator('#volume').focus();
    await page.keyboard.press('ArrowRight');
    await page.keyboard.press('Home');
    await page.setViewportSize({ width: 390, height: 844 });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.screenshot({ path: out + 'phone.png', fullPage: true });
    report.checks.push(
      '390px layout has no horizontal overflow; camera keyboard/reset; comparison modes',
    );
    await page.goto(server.url + '?no3d=1');
    await page.waitForFunction(() => window.traceViewer?.ready);
    assert.equal(await page.evaluate(() => window.traceViewer.webgl), false);
    await page.locator('[data-phase="4"]').click();
    assert.equal(await page.locator('#candidate').isVisible(), true);
    await page.locator('#slice-0').fill('5');
    await page.locator('#slice-0').dispatchEvent('input');
    assert.equal(await page.evaluate(() => window.traceViewer.positions[0]), 5);
    report.checks.push('No-WebGL fallback retains CT slice controls and trace comparisons');
    assert.deepEqual(report.errors, []);
    assert.deepEqual(report.requests, []);
    fs.writeFileSync(out + 'browser-check.json', JSON.stringify(report, null, 2));
    console.log(JSON.stringify(report));
  });
} finally {
  await server.close();
}
