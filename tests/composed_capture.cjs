/** Capture exact committed roots without waiting for an interactive animation clock. */
const assert = require('node:assert/strict');
const { withBrowser } = require('../presentation/tooling/browser.mts');
const { captureComposedFrame } = require('../presentation/tooling/media/capture.mts');

async function checkComposedCapture(browser) {
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  try {
    await page.clock.install({ time: new Date('2026-09-27T00:00:00Z') });
    await page.clock.pauseAt(new Date('2026-09-27T00:00:01Z'));
    await page.setContent(
      `<style>body{margin:0;background:magenta}#capture{position:absolute;left:31px;top:37px;width:1280px;height:720px;background:#123456}.sentinel{position:absolute;right:0;bottom:0;width:16px;height:16px;background:#fedcba}</style><div id="capture" data-explainer-export-frame><div class="scene-player"><div class="sentinel"></div></div></div>`,
    );
    await page.evaluate(() => {
      window.__tb3ExplainerCapture = {
        ready: Promise.resolve(),
        async seekFrame({ frame }) {
          document
            .querySelector('.scene-player')
            .setAttribute('data-committed-frame', String(frame));
        },
      };
    });
    const request = { frame: 7, fps: 24, width: 1280, height: 720 };
    const first = await captureComposedFrame(page, request);
    assert.equal(first.readUInt32BE(16), 1280);
    assert.equal(first.readUInt32BE(20), 720);
    await page.locator('#capture').evaluate((el) => {
      el.style.left = '0';
      el.style.top = '0';
    });
    const second = await captureComposedFrame(page, request);
    assert.deepEqual(
      first,
      second,
      'capture clips the complete root, not the surrounding viewport',
    );
    await page.locator('#capture').evaluate((el) => {
      el.style.left = '200px';
    });
    await assert.rejects(captureComposedFrame(page, request), /entirely inside/);
    await page.locator('#capture').evaluate((el) => {
      el.style.left = '0';
      el.style.width = '1279px';
    });
    await assert.rejects(captureComposedFrame(page, request), /exactly 1280x720/);
    await page.locator('#capture').evaluate((el) => {
      el.style.width = '1280px';
    });
    const screenshot = page.screenshot.bind(page);
    for (const mutation of ['frame', 'layout']) {
      page.screenshot = async (options) => {
        const bytes = await screenshot(options);
        await page.evaluate((kind) => {
          if (kind === 'frame')
            document.querySelector('.scene-player').setAttribute('data-committed-frame', '8');
          else document.querySelector('#capture').style.top = '1px';
        }, mutation);
        return bytes;
      };
      await assert.rejects(captureComposedFrame(page, request), /changed during capture/);
    }
    page.screenshot = screenshot;
    console.log(
      'PASS: paused-clock capture, exact root clipping, viewport/size guards and post-capture frame/layout rejection',
    );
  } finally {
    await page.close();
  }
}
module.exports = { checkComposedCapture };
if (require.main === module)
  withBrowser(checkComposedCapture).catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
