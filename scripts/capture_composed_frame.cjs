'use strict';
/** Adapter for the EXISTING encoder's renderFrames callback, not another exporter.
 * The export-only page must supply __tb3ExplainerCapture.ready and .seekFrame().
 * seekFrame resolves after both GPU draw and React/DOM commit. It must not depend
 * on interactive visibility or playing state. No arbitrary sleep is used here.
 */
async function captureComposedFrame(page, request) {
  const { frame, fps, width, height, selector = '[data-explainer-export-frame]' } = request;
  for (const [name, value, min] of [
    ['frame', frame, 0],
    ['fps', fps, 1],
    ['width', width, 1],
    ['height', height, 1],
  ]) {
    if (!Number.isSafeInteger(value) || value < min)
      throw new RangeError(`${name} must be an integer >= ${min}`);
  }
  if (typeof selector !== 'string' || !selector.trim())
    throw new TypeError('Expected export root selector');
  await page.evaluate(
    async ({ frame, fps, width, height, selector }) => {
      const bridge = globalThis.__tb3ExplainerCapture;
      if (
        !bridge ||
        typeof bridge.seekFrame !== 'function' ||
        !bridge.ready ||
        typeof bridge.ready.then !== 'function'
      )
        throw new Error('Missing export-only composed-capture bridge');
      await bridge.ready;
      await bridge.seekFrame({ frame, fps, width, height });
      const root = document.querySelector(selector);
      if (!root) throw new Error('Missing composed export root');
      if (document.fonts) await document.fonts.ready;
      await Promise.all(
        [...root.querySelectorAll('img')].map(async (image) => {
          await image.decode();
          if (!image.complete || image.naturalWidth === 0)
            throw new Error('Export image did not decode');
        }),
      );
      await Promise.all(
        [...root.querySelectorAll('svg image')].map(async (element) => {
          const image = new Image();
          image.src = element.getAttribute('href') || '';
          await image.decode();
        }),
      );
    },
    { frame, fps, width, height, selector },
  );
  const root = page.locator(selector);
  if ((await root.count()) !== 1) throw new Error('Expected exactly one composed export root');
  const box = await root.boundingBox();
  if (!box || Math.abs(box.width - width) > 0.01 || Math.abs(box.height - height) > 0.01)
    throw new Error(`Export root must be exactly ${width}x${height} CSS pixels`);
  return root.screenshot({ type: 'png', scale: 'css', caret: 'hide', animations: 'disabled' });
}
module.exports = { captureComposedFrame };
