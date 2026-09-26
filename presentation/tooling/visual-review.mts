/** Capture authored illustrations or rebuild a report from retained inventory bytes. */
import { basename, join } from 'node:path';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import type { Browser } from 'playwright';
import type { ExplorerData } from '../frontend/contracts.generated.ts';
import { withBrowser } from './browser.mts';

export type ReviewMode = 'static' | '3d' | 'planar' | 'fallback';
export interface ReviewEntry {
  id: string;
  title: string;
  kind: string;
  mode: ReviewMode;
  disposition: string;
  sourceImage: boolean;
  missingMedia: number;
  images: string[];
  chapters?: string[];
}
export interface ReviewInventory {
  source: string;
  summary: {
    entries: number;
    spatial: number;
    static: number;
    planar?: number;
    fallback?: number;
    sourceImages: number;
    errors: string[];
  };
  entries: ReviewEntry[];
}

export function reviewMode(renderer: string): ReviewMode {
  if (renderer === 'webgl') return '3d';
  if (renderer === 'planar') return 'planar';
  if (renderer === 'poster' || renderer === 'svg') return 'fallback';
  if (renderer === 'static') return 'static';
  throw Error(`Unknown scene renderer: ${renderer}`);
}
const labels: Record<ReviewMode, string> = {
  '3d': 'spatial 3D',
  planar: 'planar DOM/SVG',
  static: '2D-first',
  fallback: 'static fallback',
};
const esc = (value: string | number) =>
  String(value).replace(
    /[&<>"']/g,
    (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]!,
  );

export async function captureReview(
  browser: Browser,
  input: string,
  output: string,
): Promise<ReviewInventory> {
  mkdirSync(join(output, 'images'), { recursive: true });
  const errors: string[] = [];
  const rows: ReviewEntry[] = [];
  const context = await browser.newContext({
    viewport: { width: 1280, height: 1000 },
    reducedMotion: 'reduce',
  });
  try {
    const page = await context.newPage();
    page.on('pageerror', (error) => errors.push(error.message));
    await context.route(/^https?:/, (route) => {
      errors.push(`External request: ${route.request().url()}`);
      return route.abort();
    });
    await page.goto(pathToFileURL(input).href);
    const data: ExplorerData = await page.evaluate(() =>
      JSON.parse(document.querySelector('#data')!.textContent!),
    );
    for (const entry of data.entries) {
      if (!entry.illustration) continue;
      const plan = entry.illustration.story_id
        ? data.explanation_stories?.[entry.illustration.story_id]
        : undefined;
      await page.evaluate((id) => {
        location.hash = `${id}/0/overview?view=repository`;
      }, entry.id);
      await page.waitForFunction(
        ({ id, kind }) =>
          document.querySelector<HTMLElement>('.task-detail')?.dataset.brief === id &&
          document.querySelector<HTMLElement>('.task-scene-host > [data-scene]')?.dataset.scene ===
            kind,
        { id: entry.id, kind: entry.illustration.kind },
      );
      const staticView = page.locator('.scene-static');
      const isStatic = (await staticView.count()) > 0;
      if (!isStatic) await page.locator('.scene-player[data-rendered="true"]').waitFor();
      const mode = reviewMode(
        isStatic
          ? 'static'
          : (await page.locator('.scene-player').getAttribute('data-surface-renderer')) || '',
      );
      const name = entry.id.replace(/[^a-z0-9_-]/gi, '_');
      const images: string[] = [];
      if (mode === 'static' || mode === 'fallback') {
        const file = `images/${name}.png`;
        await (isStatic ? staticView : page.locator('.scene-player')).screenshot({
          path: join(output, file),
        });
        images.push(file);
      } else {
        await page.waitForFunction(
          () =>
            document.querySelector<HTMLElement>('.scene-player')?.dataset.texturesReady === 'true',
        );
        for (let stage = 0; stage < (plan?.beats.length || 3); stage++) {
          if (stage) await page.locator(`[data-scene-step="${stage}"]`).click();
          const file = `images/${name}-${stage}.png`;
          await page
            .locator(plan ? '.scene-player' : '.scene-stage')
            .screenshot({ path: join(output, file) });
          images.push(file);
        }
      }
      rows.push({
        id: entry.id,
        title: entry.title,
        kind: entry.illustration.kind,
        mode,
        disposition: labels[mode],
        sourceImage: /<img\b/.test(entry.visuals.input),
        missingMedia: entry.missing_media?.length || 0,
        images,
        chapters: plan?.beats.map((beat) => beat.caption),
      });
    }
  } finally {
    await context.close();
  }
  return {
    source: basename(input),
    entries: rows,
    summary: {
      entries: rows.length,
      spatial: rows.filter((row) => row.mode === '3d').length,
      planar: rows.filter((row) => row.mode === 'planar').length,
      static: rows.filter((row) => row.mode === 'static').length,
      fallback: rows.filter((row) => row.mode === 'fallback').length,
      sourceImages: rows.filter((row) => row.sourceImage).length,
      errors,
    },
  };
}

function renderEntry(row: ReviewEntry): string {
  const images = row.images.map((path, i) => {
    const stage =
      row.mode === 'static'
        ? 'Input and output'
        : row.mode === 'fallback'
          ? 'Static fallback'
          : (row.chapters || ['Input', 'Action', 'Output'])[i];
    return `<figure>
      <img loading="lazy" src="${esc(path)}" alt="${esc(row.title)}: ${esc(stage)}">
      <figcaption>${esc(stage)}</figcaption>
    </figure>`;
  });
  return `<article data-mode="${row.mode}">
    <h2>${esc(row.title)}</h2>
    <p><code>${esc(row.id)}</code> · ${esc(row.kind)} · ${labels[row.mode]}${row.sourceImage ? ' · source image' : ''}</p>
    <div>${images.join('\n')}</div>
  </article>`;
}

export function renderReview(inventory: ReviewInventory): string {
  const { summary } = inventory;
  const totals = [
    `${summary.entries} illustrations`,
    `${summary.spatial} spatial 3D`,
    `${summary.planar ?? 0} planar`,
    `${summary.static} 2D-first`,
    `${summary.fallback ?? 0} fallbacks`,
    `${summary.sourceImages} source-image companions`,
  ].join(' · ');
  const failures = summary.errors.length
    ? `<aside role="alert"><h2>Recorded capture errors</h2><ul>${summary.errors.map((error) => `<li>${esc(error)}</li>`).join('')}</ul></aside>`
    : '';
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Task visual review</title>
  <style>
    body { font: 15px system-ui; color: #28413e; background: #f4f2ec; margin: 24px; }
    header { position: sticky; top: 0; background: #f4f2ecee; padding: 8px 0; }
    main { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 330px), 1fr)); gap: 18px; }
    article { min-width: 0; background: white; border: 1px solid #dadbd2; border-radius: 8px; padding: 14px; }
    h2 { font-size: 17px; margin: 0; }
    p { font-size: 12px; color: #586e66; overflow-wrap: anywhere; }
    article > div { display: grid; gap: 5px; }
    figure { margin: 0; }
    figcaption { font-size: 12px; color: #586e66; padding: 2px 0 8px; }
    img { width: 100%; height: auto; background: #faf9f5; }
    aside { border: 2px solid #a84535; padding: 12px; }
  </style>
</head>
<body>
  <header><h1>Task visual review</h1><p>${esc(totals)}</p>${failures}</header>
  <main>${inventory.entries.map(renderEntry).join('\n')}</main>
</body>
</html>`;
}

export async function review(
  input: string,
  output: string,
  fromInventory = false,
): Promise<ReviewInventory> {
  const file = join(output, 'inventory.json');
  const inventory: ReviewInventory = fromInventory
    ? JSON.parse(readFileSync(file, 'utf8'))
    : await withBrowser((browser) => captureReview(browser, input, output));
  if (
    !Array.isArray(inventory.entries) ||
    !Array.isArray(inventory.summary?.errors) ||
    inventory.summary.errors.some((error) => typeof error !== 'string')
  )
    throw Error('Invalid review inventory');
  if (inventory.entries.some((row) => !Object.hasOwn(labels, row.mode)))
    throw Error('Unknown inventory mode');
  if (!fromInventory) writeFileSync(file, JSON.stringify(inventory, null, 2) + '\n');
  writeFileSync(join(output, 'index.html'), renderReview(inventory));
  return inventory;
}
