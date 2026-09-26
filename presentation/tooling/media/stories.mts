/** Canonical-story source adapter for export_med_tours, sharing its browser and pipe encoder. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import os from 'node:os';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import type { StoryPlan } from '../../frontend/contracts.generated.ts';
import { withBrowser } from '../browser.mts';
import { runPython } from '../python.mts';
import { runPipedEncoder } from './encoder.mts';
import { captureComposedFrame } from './capture.mts';

const sha = (bytes: string | Buffer) => crypto.createHash('sha256').update(bytes).digest('hex');
export interface StoryOptions {
  story: string;
  output: string;
  stillsOnly: boolean;
}

export async function exportStory(root: string, options: StoryOptions): Promise<void> {
  const output = path.resolve(options.output);
  if (fs.existsSync(output)) throw Error('Story exports require a fresh output directory');
  runPython(root, [
    '-m',
    'tb3_medical.cli',
    '--root',
    root,
    'story',
    'build',
    options.story,
    '--output',
    output,
  ]);
  const plan: StoryPlan = JSON.parse(fs.readFileSync(path.join(output, 'plan.json'), 'utf8'));
  const git = (...args: string[]) => execFileSync('git', args, { cwd: root, encoding: 'utf8' });
  const changed = [
    ...new Set([
      ...git('diff', '--name-only', '-z', 'HEAD').split('\0'),
      ...git('ls-files', '--others', '--exclude-standard', '-z').split('\0'),
    ]),
  ]
    .filter(Boolean)
    .sort();
  const dirty = Object.fromEntries(
    changed.map((name) => [
      name,
      fs.existsSync(path.join(root, name))
        ? sha(fs.readFileSync(path.join(root, name)))
        : 'deleted',
    ]),
  );
  const receipt = {
    schema: 1,
    story: plan.id,
    revision: git('rev-parse', 'HEAD').trim(),
    dirty_sources: dirty,
    dirty_sha256: sha(JSON.stringify(dirty)),
    source_sha256: plan.source_sha256,
    plan_sha256: sha(fs.readFileSync(path.join(output, 'plan.json'))),
    dependencies: plan.dependencies,
    frontend_manifest_sha256: sha(
      fs.readFileSync(path.join(root, '.local/frontend/manifest.json')),
    ),
    lockfile_sha256: sha(fs.readFileSync(path.join(root, 'package-lock.json'))),
    os: { platform: os.platform(), release: os.release(), arch: os.arch() },
    locale: plan.locale,
    camera: ['multiscale-v1', 'local-edit-v1', 'longitudinal-v1', 'inverse-v1'].includes(
      plan.recipe,
    )
      ? 'Planar coordinate-preserving SVG/DOM'
      : plan.recipe === 'anatomy-audit-v1'
        ? 'stage fitted perspective; yaw -0.24; pitch 0.14; retained shared source-world mm assembly normalized by the existing anatomy owner'
        : 'stage fitted perspective; yaw -0.24; pitch 0.14; one parent metre-to-display transform',
    settings: {
      width: 1280,
      height: 720,
      fps: plan.fps,
      frames: plan.durationFrames,
      audio: false,
      codec: 'H.264',
      crf: 18,
    },
    outputs: {} as Record<string, { sha256: string; bytes: number }>,
    errors: [] as string[],
    browser: '',
    renderer: '',
  };
  await withBrowser(async (browser) => {
    receipt.browser = browser.version();
    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 },
      deviceScaleFactor: 1,
      reducedMotion: 'reduce',
    });
    await context.route(/^https?:/, (route) => {
      receipt.errors.push('Forbidden remote request: ' + route.request().url());
      return route.abort();
    });
    const page = await context.newPage();
    page.on('pageerror', (e) => receipt.errors.push(e.message));
    await page.goto(pathToFileURL(path.join(output, 'index.html')).href + '?capture=1');
    await page.waitForFunction(() => window.__tb3ExplainerCapture);
    const capture = (frame: number) =>
      captureComposedFrame(page, { frame, fps: plan.fps, width: 1280, height: 720 });
    fs.writeFileSync(path.join(output, 'first.png'), await capture(0));
    const stills = [];
    for (const beat of plan.beats) {
      const frame = beat.endFrame - 1,
        file = `${beat.id}.png`;
      fs.writeFileSync(path.join(output, file), await capture(frame));
      stills.push({ frame, file, caption: beat.caption, narration: beat.narration });
    }
    fs.writeFileSync(path.join(output, 'stills.json'), JSON.stringify(stills, null, 2) + '\n');
    const posterBeat =
      plan.beats.find((beat) => 'output' in beat && beat.output?.every((value) => value === 1)) ||
      plan.beats.at(-1)!;
    fs.copyFileSync(path.join(output, `${posterBeat.id}.png`), path.join(output, 'poster.png'));
    if (!options.stillsOnly)
      await runPipedEncoder({
        command: process.env.FFMPEG || 'ffmpeg',
        args: [
          '-hide_banner',
          '-loglevel',
          'error',
          '-y',
          '-f',
          'image2pipe',
          '-vcodec',
          'png',
          '-framerate',
          String(plan.fps),
          '-i',
          'pipe:0',
          '-an',
          '-c:v',
          'libx264',
          '-preset',
          'slow',
          '-crf',
          '18',
          '-pix_fmt',
          'yuv420p',
          '-movflags',
          '+faststart',
        ],
        destination: path.join(output, plan.schema === 1 ? 'route-unfold.mp4' : plan.id + '.mp4'),
        renderFrames: async (writeFrame) => {
          for (let frame = 0; frame < plan.durationFrames; frame++) {
            await writeFrame(await capture(frame));
            if (frame % (plan.fps * 4) === 0)
              console.log(`Story ${plan.id}: ${frame}/${plan.durationFrames} frames`);
          }
        },
      });
    receipt.renderer = await page.evaluate(() => {
      if (
        document.querySelector<HTMLElement>('.scene-player')?.dataset.surfaceRenderer === 'planar'
      )
        return 'DOM/SVG planar';
      const gl = document.querySelector('canvas')?.getContext('webgl2');
      if (!gl) throw Error('Missing export WebGL renderer');
      const ext = gl.getExtension('WEBGL_debug_renderer_info');
      return ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
    });
    await context.close();
  });
  for (const name of fs.readdirSync(output))
    receipt.outputs[name] = {
      sha256: sha(fs.readFileSync(path.join(output, name))),
      bytes: fs.statSync(path.join(output, name)).size,
    };
  fs.writeFileSync(path.join(output, 'receipt.json'), JSON.stringify(receipt, null, 2) + '\n');
  if (receipt.errors.length) throw Error(receipt.errors.join('\n'));
  console.log(`Integrated story exported: ${output}`);
}
