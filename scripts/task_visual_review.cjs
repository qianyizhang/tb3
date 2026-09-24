/* Capture every authored Task Explorer illustration from a built offline file.
 * Usage: node scripts/task_visual_review.cjs path/to/index.html output-directory [--from-inventory]
 * The output stays local: inventory.json, index.html and stage PNGs.
 */
const { withBrowser } = require('./browser.cjs');
const { resolve, join, basename } = require('node:path');
const { mkdirSync, readFileSync, writeFileSync } = require('node:fs');
const { pathToFileURL } = require('node:url');

const esc = (value) =>
  String(value).replace(
    /[&<>"']/g,
    (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char],
  );

async function main() {
  const input = resolve(process.argv[2] || '');
  const output = resolve(process.argv[3] || '.local/task-visual-review');
  mkdirSync(output, { recursive: true });
  mkdirSync(join(output, 'images'), { recursive: true });
  const failures = [];
  const rows = process.argv.includes('--from-inventory')
    ? JSON.parse(readFileSync(join(output, 'inventory.json'), 'utf8')).entries
    : await withBrowser(async (browser) => {
        const context = await browser.newContext({
          viewport: { width: 1280, height: 1000 },
          reducedMotion: 'reduce',
        });
        const page = await context.newPage();
        page.on('pageerror', (error) => failures.push(error.message));
        page.on('request', (request) => {
          if (/^https?:/.test(request.url())) failures.push(`External request: ${request.url()}`);
        });
        const url = pathToFileURL(input).href;
        await page.goto(url);
        const data = await page.evaluate(() =>
          JSON.parse(document.querySelector('#data').textContent),
        );
        const entries = data.entries;
        const results = [];
        for (const entry of entries.filter((item) => item.illustration)) {
          const plan = data.explanation_stories?.[entry.illustration.story_id];
          await page.evaluate((id) => {
            location.hash = `${id}/0/overview?view=repository`;
          }, entry.id);
          await page.waitForFunction(
            ({ id, kind }) =>
              document.querySelector('.task-detail')?.dataset.brief === id &&
              document.querySelector('.task-scene-host > [data-scene]')?.dataset.scene === kind,
            { id: entry.id, kind: entry.illustration.kind },
          );
          const staticView = page.locator('.scene-static');
          const mode = (await staticView.count()) ? 'static' : '3d';
          const name = entry.id.replace(/[^a-z0-9_-]/gi, '_');
          const images = [];
          if (mode === 'static') {
            const path = `images/${name}.png`;
            await staticView.screenshot({ path: join(output, path) });
            images.push(path);
          } else {
            await page.locator('.scene-player[data-rendered="true"]').waitFor();
            await page.waitForFunction(
              () => document.querySelector('.scene-player')?.dataset.texturesReady === 'true',
            );
            for (const stage of Array.from({ length: plan?.beats.length || 3 }, (_, i) => i)) {
              if (stage) await page.locator(`[data-scene-step="${stage}"]`).click();
              const path = `images/${name}-${stage}.png`;
              await page
                .locator(plan ? '.scene-player' : '.scene-stage')
                .screenshot({ path: join(output, path) });
              images.push(path);
            }
          }
          results.push({
            id: entry.id,
            title: entry.title,
            kind: entry.illustration.kind,
            mode,
            disposition:
              mode === '3d'
                ? 'spatial 3D explanation'
                : entry.illustration.kind === 'segment'
                  ? '2D-first: no matched target surface'
                  : '2D-first: image, signal, text or record output',
            sourceImage: /<img\b/.test(entry.visuals.input),
            missingMedia: entry.missing_media?.length || 0,
            images,
            chapters: plan?.beats.map((beat) => beat.caption),
          });
        }
        await context.close();
        return results;
      });
  const summary = {
    entries: rows.length,
    spatial: rows.filter((row) => row.mode === '3d').length,
    static: rows.filter((row) => row.mode === 'static').length,
    sourceImages: rows.filter((row) => row.sourceImage).length,
    errors: failures,
  };
  writeFileSync(
    join(output, 'inventory.json'),
    JSON.stringify({ source: basename(input), summary, entries: rows }, null, 2) + '\n',
  );
  const cards = rows
    .map(
      (row) =>
        `<article data-mode="${row.mode}"><h2>${esc(row.title)}</h2><p><code>${esc(row.id)}</code> · ${esc(row.kind)} · ${row.mode === '3d' ? 'spatial 3D' : '2D-first'}${row.sourceImage ? ' · source image' : ''}</p><div>${row.images
          .map((path, i) => {
            const stage =
              row.mode === '3d'
                ? (row.chapters || ['Input', 'Action', 'Output'])[i]
                : 'Input and output';
            return `<figure><img loading="lazy" src="${esc(path)}" alt="${esc(row.title)}: ${stage}"><figcaption>${stage}</figcaption></figure>`;
          })
          .join('')}</div></article>`,
    )
    .join('');
  writeFileSync(
    join(output, 'index.html'),
    `<!doctype html><html lang="en"><meta charset="utf-8"><title>Task visual review</title><style>body{font:15px system-ui;color:#28413e;background:#f4f2ec;margin:24px}header{position:sticky;top:0;background:#f4f2ecee;padding:8px 0}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:18px}article{min-width:0;background:white;border:1px solid #dadbd2;border-radius:8px;padding:14px}h2{font-size:17px;margin:0}p{font-size:12px;color:#586e66;overflow-wrap:anywhere}article>div{display:grid;gap:5px}figure{margin:0}figcaption{font-size:12px;color:#586e66;padding:2px 0 8px}img{width:100%;height:auto;background:#faf9f5}</style><header><h1>Task visual review</h1><p>${summary.entries} illustrations · ${summary.spatial} spatial 3D · ${summary.static} 2D-first · ${summary.sourceImages} source-image companions</p></header><main>${cards}</main></html>`,
  );
  console.log(JSON.stringify(summary));
  if (failures.length) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
