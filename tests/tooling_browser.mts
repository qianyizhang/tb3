/** Real renderer classifications through the production review capture operation. */
import assert from 'node:assert/strict';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import type { Browser } from 'playwright';
import type { ExplorerData } from '../presentation/frontend/contracts.generated.ts';
import { captureReview, renderReview } from '../presentation/tooling/visual-review.mts';

export async function checkReview(browser: Browser, site: string, reports: string): Promise<void> {
  const output = join(reports, 'visual-review');
  mkdirSync(output, { recursive: true });
  const html = readFileSync(join(site, 'task-explorer/index.html'), 'utf8');
  const pattern = /(<script id="data" type="application\/json">)([\s\S]*?)(<\/script>)/;
  const match = html.match(pattern);
  assert.ok(match, 'Expected the production Explorer payload');
  const data: ExplorerData = JSON.parse(match[2]);
  const planar = data.entries.find(
    (entry) =>
      entry.illustration?.story_id &&
      data.explanation_stories?.[entry.illustration.story_id]?.recipe === 'multiscale-v1',
  );
  const spatial = data.entries.find((entry) => entry.id === 'ours');
  const staticEntry = data.entries.find(
    (entry) => entry.illustration?.kind === 'report' && !entry.illustration.story_id,
  );
  assert.ok(planar && spatial && staticEntry, 'Expected representative production views');
  data.entries = [spatial, planar, staticEntry];
  const input = join(output, 'input.html');
  writeFileSync(
    input,
    html.replace(
      pattern,
      () => match[1] + JSON.stringify(data).replaceAll('<', '\\u003c') + match[3],
    ),
  );
  const inventory = await captureReview(browser, input, output);
  assert.deepEqual(inventory.summary.errors, []);
  assert.deepEqual(
    inventory.entries.map((entry) => entry.mode),
    ['3d', 'planar', 'static'],
  );
  assert.equal(inventory.summary.spatial, 1);
  assert.equal(inventory.summary.planar, 1);
  writeFileSync(join(output, 'inventory.json'), JSON.stringify(inventory, null, 2) + '\n');
  writeFileSync(join(output, 'index.html'), renderReview(inventory));
  const page = await browser.newPage({ viewport: { width: 360, height: 800 } });
  try {
    await page.goto(pathToFileURL(join(output, 'index.html')).href);
    assert.equal(await page.locator('article').count(), 3);
    assert.equal(
      await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
      true,
      'The report fits a narrow viewport without horizontal scrolling',
    );
  } finally {
    await page.close();
  }
  console.log('Visual review: spatial, planar, static and mobile report checks passed.');
}
