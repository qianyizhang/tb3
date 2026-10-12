import { fileURLToPath } from 'node:url';
import { withBrowser, serveDirectory } from '../../../../presentation/tooling/browser.mts';
const { LINE_ENDS } = await import(
  new URL('../../../../.local/anatomy-skill-trial/scripts/line-ends.mjs', import.meta.url)
);
import fs from 'node:fs';
import assert from 'node:assert/strict';
const out = fileURLToPath(new URL('../../../../.local/anatomy-pose/', import.meta.url));
const server = await serveDirectory(out);
try {
  await withBrowser(async (browser) => {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1100 },
      reducedMotion: 'reduce',
    });
    const errors = [];
    page.on('pageerror', (e) => errors.push(e.message));
    await page.goto(server.url);
    await page.waitForFunction(() => window.poseDemo);
    assert.equal(await page.locator('#score').isVisible(), false);
    await page.screenshot({ path: out + 'desktop.png', fullPage: true });
    await page.locator('#reveal').click();
    await page.locator('[data-preset="spin"]').click();
    const spin = await page.evaluate(() => window.poseDemo);
    assert.ok(spin.metrics.normal < 1e-5);
    assert.ok(spin.metrics.centre < 1e-10);
    assert.ok(spin.metrics.rms > 10);
    await page.screenshot({ path: out + 'spin-revealed.png', fullPage: true });
    await page.locator('#match').click();
    assert.ok((await page.evaluate(() => window.poseDemo.metrics.rms)) < 1e-8);
    await page.locator('#x').focus();
    await page.keyboard.press('ArrowRight');
    assert.equal((await page.evaluate(() => window.poseDemo.metrics.rms)).toFixed(3), '1.000');
    await page.locator('[data-preset="initial"]').click();
    const lineResult = await page.evaluate('(' + LINE_ENDS + ')({})');
    await page.locator('#theme').click();
    await page.screenshot({ path: out + 'dark.png', fullPage: true });
    const darkLines = await page.evaluate('(' + LINE_ENDS + ')({})');
    await page.locator('#theme').click();
    await page.setViewportSize({ width: 390, height: 844 });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.screenshot({ path: out + 'phone.png', fullPage: true });
    await page.setViewportSize({ width: 1440, height: 1100 });
    await page.setViewportSize({ width: 1440, height: 1100 });
    const zoom = await browser.newPage({
      viewport: { width: 1440, height: 1100 },
      deviceScaleFactor: 4,
      reducedMotion: 'reduce',
    });
    await zoom.goto(server.url);
    await zoom.waitForFunction(() => window.poseDemo);
    await zoom.locator('.iso-svg').screenshot({ path: out + 'detail-light.png' });
    await zoom.locator('#theme').click();
    await zoom.locator('.iso-svg').screenshot({ path: out + 'detail-dark.png' });
    await zoom.close();
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    await page.locator('#tour').click();
    await page.waitForTimeout(1000);
    const motion1 = await page.evaluate(() => window.poseDemo.pose);
    await page.waitForTimeout(500);
    const motion2 = await page.evaluate(() => window.poseDemo.pose);
    assert.notDeepEqual(motion1, motion2);
    await page.locator('#tour').click();
    await page.emulateMedia({ reducedMotion: 'reduce' });
    assert.deepEqual(errors, []);
    fs.writeFileSync(
      out + 'browser-check.json',
      JSON.stringify(
        {
          spin: spin.metrics,
          lightLines: lineResult,
          darkLines,
          errors,
          checks: [
            'hidden reference',
            'pure in-plane spin',
            'zero at reference',
            'keyboard 1mm displacement',
            '390px no overflow',
            'theme toggle',
            'motion',
            'reduced-motion input',
          ],
        },
        null,
        2,
      ),
    );
    console.log(
      JSON.stringify({
        spin: spin.metrics,
        lightLineEnds: lineResult.problems.length,
        darkLineEnds: darkLines.problems.length,
        errors,
      }),
    );
  });
} finally {
  await server.close();
}
