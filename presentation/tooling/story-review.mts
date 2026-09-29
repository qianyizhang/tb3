/** Source-checked, pending visual review of a canonical story export. */
import { createHash } from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { withBrowser } from './browser.mts';
import { reviewSamples } from './review-samples.mts';

type Beat = {
  id: string;
  caption: string;
  startFrame: number;
  endFrame: number;
  channels?: Record<string, [number, number]>;
};
type Plan = {
  id: string;
  title: string;
  fps: number;
  durationFrames: number;
  source_sha256: string;
  dependencies?: Record<string, string>;
  beats: Beat[];
};
type Still = { frame: number; file: string; caption: string; narration?: string };
type Output = { sha256: string; bytes: number };
type Receipt = {
  story: string;
  plan_sha256: string;
  source_sha256: string;
  dependencies?: Record<string, string>;
  settings: { width: number; height: number; fps: number; frames: number };
  outputs: Record<string, Output>;
  errors: string[];
};

const digest = (bytes: Uint8Array) => createHash('sha256').update(bytes).digest('hex');
const shaPattern = /^[0-9a-f]{64}$/;
const leafPattern = /^[A-Za-z0-9][A-Za-z0-9._-]*$/;

export function safeLeaf(name: string): string {
  if (!leafPattern.test(name) || name === '.' || name === '..')
    throw Error(`Unsafe artifact name: ${name}`);
  return name;
}

export function safeWorkspacePath(name: string): string {
  if (
    name.startsWith('/') ||
    name.includes('\\') ||
    name.split('/').some((part) => !part || part === '.' || part === '..')
  )
    throw Error(`Unsafe source path: ${name}`);
  return name;
}

function plainObject(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}

async function readRegular(root: string, name: string): Promise<Buffer> {
  const file = path.join(root, safeLeaf(name));
  const stat = await fs.lstat(file);
  if (!stat.isFile() || stat.isSymbolicLink()) throw Error(`Expected regular artifact: ${name}`);
  return fs.readFile(file);
}

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw Error(message);
}

export function parseFrameNumbers(raw: string | undefined, durationFrames: number): number[] {
  if (raw === undefined || raw === '') return [];
  return [
    ...new Set(
      raw.split(',').map((item) => {
        if (!/^(0|[1-9]\d*)$/.test(item)) throw Error(`Invalid frame number: ${item}`);
        const frame = Number(item);
        if (!Number.isSafeInteger(frame) || frame >= durationFrames)
          throw RangeError(`Frame outside export: ${item}`);
        return frame;
      }),
    ),
  ].sort((a, b) => a - b);
}

export function reviewFrames(plan: Plan, extraFrames: readonly number[] = []): number[] {
  const baseline = reviewSamples(plan, { motion: true }).map((sample) => sample.frame);
  const frames = new Set<number>([...baseline, ...extraFrames]);
  for (const beat of plan.beats) {
    frames.add(beat.startFrame);
    // A numeric reference reveal has a derived threshold crossing. Other semantics
    // require an explicit --frames witness supplied by the reviewer.
    const reference = beat.channels?.reference;
    if (reference && reference.length === 2 && reference[0] !== reference[1]) {
      const crossing = (0.5 - reference[0]) / (reference[1] - reference[0]);
      if (crossing > 0 && crossing < 1) {
        const frame = beat.startFrame + Math.ceil(crossing * (beat.endFrame - beat.startFrame));
        frames.add(Math.max(beat.startFrame, frame - 1));
        frames.add(Math.min(beat.endFrame - 1, frame));
      }
    }
  }
  for (const frame of frames)
    if (!Number.isSafeInteger(frame) || frame < 0 || frame >= plan.durationFrames)
      throw RangeError(`Frame outside export: ${frame}`);
  return [...frames].sort((a, b) => a - b);
}

function srtTime(frame: number, fps: number): string {
  const ms = Math.round((frame / fps) * 1000);
  const hours = Math.floor(ms / 3_600_000);
  const minutes = Math.floor((ms % 3_600_000) / 60_000);
  const seconds = Math.floor((ms % 60_000) / 1000);
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')},${String(ms % 1000).padStart(3, '0')}`;
}

export function verifySrt(raw: string, plan: Plan): void {
  const normalized = raw.replace(/\r\n/g, '\n').trim();
  const blocks = normalized.split(/\n\s*\n/);
  assert(blocks.length === plan.beats.length, 'SRT cue count differs from plan beats');
  for (const [index, beat] of plan.beats.entries()) {
    const lines = blocks[index].split('\n');
    assert(lines[0] === String(index + 1), `SRT cue number ${index + 1} differs`);
    assert(
      lines[1] === `${srtTime(beat.startFrame, plan.fps)} --> ${srtTime(beat.endFrame, plan.fps)}`,
      `SRT timing differs for ${beat.id}`,
    );
    assert(lines.slice(2).join('\n') === beat.caption, `SRT caption differs for ${beat.id}`);
  }
}

export async function verifyExport(exportDir: string, playback: boolean) {
  const root = await fs.realpath(exportDir);
  const receiptBytes = await readRegular(root, 'receipt.json');
  const receipt: Receipt = JSON.parse(receiptBytes.toString('utf8'));
  assert(plainObject(receipt) && plainObject(receipt.outputs), 'Invalid export receipt');
  assert(
    Array.isArray(receipt.errors) && receipt.errors.length === 0,
    'Export receipt records errors',
  );
  const required = [
    'plan.json',
    'stills.json',
    'captions.srt',
    'captions.vtt',
    'canonical.story.md',
    'first.png',
    'poster.png',
    'index.html',
    'transcript.md',
  ];
  for (const name of required) assert(name in receipt.outputs, `Missing receipt output: ${name}`);
  const verified: Record<string, Output> = {};
  for (const [name, recorded] of Object.entries(receipt.outputs)) {
    safeLeaf(name);
    assert(
      plainObject(recorded) &&
        typeof recorded.sha256 === 'string' &&
        shaPattern.test(recorded.sha256) &&
        Number.isSafeInteger(recorded.bytes) &&
        recorded.bytes >= 0,
      `Invalid output receipt: ${name}`,
    );
    const bytes = await readRegular(root, name);
    assert(
      bytes.length === recorded.bytes && digest(bytes) === recorded.sha256,
      `Output differs from receipt: ${name}`,
    );
    verified[name] = recorded;
  }
  const plan: Plan = JSON.parse((await readRegular(root, 'plan.json')).toString('utf8'));
  const stills: Still[] = JSON.parse((await readRegular(root, 'stills.json')).toString('utf8'));
  assert(
    plainObject(plan) &&
      typeof plan.id === 'string' &&
      typeof plan.title === 'string' &&
      Number.isSafeInteger(plan.fps) &&
      plan.fps > 0 &&
      Number.isSafeInteger(plan.durationFrames) &&
      plan.durationFrames > 0 &&
      Array.isArray(plan.beats),
    'Invalid plan',
  );
  for (const beat of plan.beats)
    assert(
      plainObject(beat) &&
        typeof beat.id === 'string' &&
        beat.id.length > 0 &&
        typeof beat.caption === 'string',
      'Invalid plan beat',
    );
  assert(
    receipt.story === plan.id && receipt.plan_sha256 === verified['plan.json'].sha256,
    'Receipt and plan identity differ',
  );
  assert(
    shaPattern.test(plan.source_sha256) &&
      plan.source_sha256 === receipt.source_sha256 &&
      receipt.source_sha256 === verified['canonical.story.md'].sha256,
    'Canonical source hashes differ',
  );
  assert(
    plainObject(plan.dependencies) && plainObject(receipt.dependencies),
    'Missing source dependency hashes',
  );
  for (const [name, hash] of Object.entries(plan.dependencies)) {
    safeWorkspacePath(name);
    assert(
      typeof hash === 'string' && shaPattern.test(hash) && receipt.dependencies[name] === hash,
      `Source dependency hash differs: ${name}`,
    );
  }
  assert(
    Object.keys(plan.dependencies).length === Object.keys(receipt.dependencies).length,
    'Source dependency set differs',
  );
  assert(
    plainObject(receipt.settings) &&
      receipt.settings.width === 1280 &&
      receipt.settings.height === 720 &&
      receipt.settings.fps === plan.fps &&
      receipt.settings.frames === plan.durationFrames,
    'Export settings differ from plan or 1280×720 contract',
  );
  reviewSamples(plan);
  assert(
    Array.isArray(stills) && stills.length === plan.beats.length,
    'Stills differ from plan beats',
  );
  for (const [index, still] of stills.entries()) {
    const beat = plan.beats[index];
    assert(
      plainObject(still) &&
        still.frame === beat.endFrame - 1 &&
        still.caption === beat.caption &&
        typeof still.file === 'string' &&
        still.file in verified,
      `Invalid still for ${beat.id}`,
    );
    assert(still.file.endsWith('.png'), `Invalid still extension for ${beat.id}`);
  }
  verifySrt((await readRegular(root, 'captions.srt')).toString('utf8'), plan);
  const videos = Object.keys(verified).filter((name) => name.endsWith('.mp4'));
  assert(videos.length <= 1, 'Ambiguous video outputs');
  if (playback) assert(videos.length === 1, 'Playback requires one receipt-pinned MP4');
  return {
    root,
    plan,
    stills,
    receiptSha256: digest(receiptBytes),
    outputs: verified,
    video: videos[0] ?? null,
  };
}

function escapeHtml(value: string): string {
  return value.replace(
    /[&<>"']/g,
    (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]!,
  );
}

function gallery(
  manifest: Record<string, unknown>,
  stills: Still[],
  samples: {
    file: string;
    frame: number;
    actualTime: number;
    timeBefore: number;
    timeAfter: number;
  }[],
): string {
  const cards = [
    ...stills.map((still) => ({
      file: still.file,
      title: `Canonical frame ${still.frame}`,
      caption: still.caption,
    })),
    ...samples.map((sample) => ({
      file: sample.file,
      title: `Playback target frame ${sample.frame} · observed ${sample.timeBefore.toFixed(3)}–${sample.timeAfter.toFixed(3)} s`,
      caption: 'Inspect motion, boundaries and text against the source.',
    })),
  ];
  return `<!doctype html><html lang="en"><meta charset="utf-8"><title>Story review</title><style>body{font:16px system-ui;margin:2rem;background:#f6f5f1;color:#18222a}h1{margin-bottom:.2rem}.status{font-weight:700;color:#9a5300}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:1rem}figure{margin:0;background:white;padding:1rem;border:1px solid #ccc}img{width:100%;height:auto}figcaption{line-height:1.5}small{display:block}</style><h1>${escapeHtml(String(manifest.storyId))}</h1><p class="status">Pending human visual review</p><p>Export hashes and captions were checked. These images are review witnesses, not acceptance.</p><div class="grid">${cards.map((card) => `<figure><img src="${escapeHtml(card.file)}" alt="${escapeHtml(card.title)}"><figcaption><strong>${escapeHtml(card.title)}</strong><small>${escapeHtml(card.caption)}</small></figcaption></figure>`).join('')}</div></html>\n`;
}

export async function collectStoryReview(
  exportDir: string,
  outputDir: string,
  options: { playback?: boolean; frames?: string } = {},
) {
  const output = path.resolve(outputDir);
  await fs.mkdir(output); // Refuse reuse, even after a failed review.
  const manifest: Record<string, unknown> = {
    schema: 1,
    status: 'failed',
    visual_review: 'pending',
    export: path.resolve(exportDir),
    playbackRequested: !!options.playback,
    errors: [],
  };
  const writeReceipt = async () =>
    fs.writeFile(path.join(output, 'review.json'), `${JSON.stringify(manifest, null, 2)}\n`);
  try {
    const moduleDirectory = path.dirname(fileURLToPath(import.meta.url));
    const collectorFiles = [
      ['presentation/tooling/story-review.mts', path.join(moduleDirectory, 'story-review.mts')],
      ['presentation/tooling/review-samples.mts', path.join(moduleDirectory, 'review-samples.mts')],
      ['presentation/tooling/browser.mts', path.join(moduleDirectory, 'browser.mts')],
      ['scripts/review_story.mts', path.resolve(moduleDirectory, '../../scripts/review_story.mts')],
    ];
    manifest.collectorSources = Object.fromEntries(
      await Promise.all(
        collectorFiles.map(async ([name, file]) => [name, digest(await fs.readFile(file))]),
      ),
    );
    try {
      manifest.sourceReceiptSha256 = digest(
        await readRegular(await fs.realpath(exportDir), 'receipt.json'),
      );
    } catch {
      // The verified reader below records the precise missing or unsafe input.
    }
    const source = await verifyExport(exportDir, !!options.playback);
    const frames = reviewFrames(
      source.plan,
      parseFrameNumbers(options.frames, source.plan.durationFrames),
    );
    const canonicalStills = [
      { file: 'first.png', frame: 0, caption: 'First canonical frame' },
      ...source.stills,
      { file: 'poster.png', frame: source.plan.durationFrames - 1, caption: 'Canonical poster' },
    ];
    Object.assign(manifest, {
      storyId: source.plan.id,
      title: source.plan.title,
      sourceReceiptSha256: source.receiptSha256,
      sourceSha256: source.outputs['canonical.story.md'].sha256,
      planSha256: source.outputs['plan.json'].sha256,
      fps: source.plan.fps,
      durationFrames: source.plan.durationFrames,
      durationSeconds: source.plan.durationFrames / source.plan.fps,
      video: source.video,
      videoSha256: source.video ? source.outputs[source.video].sha256 : null,
      requestedFrames: options.playback ? frames : [],
      suggestedFrames: frames,
      sourceOutputs: source.outputs,
      sourceDependencies: source.plan.dependencies,
      canonicalStills: canonicalStills.map((still) => ({
        file: still.file,
        frame: still.frame,
        caption: still.caption,
        sha256: source.outputs[still.file].sha256,
      })),
    });
    for (const still of canonicalStills) {
      await fs.copyFile(path.join(source.root, still.file), path.join(output, still.file));
      assert(
        digest(await fs.readFile(path.join(output, still.file))) ===
          source.outputs[still.file].sha256,
        `Copied still differs from receipt: ${still.file}`,
      );
    }
    const samples: {
      file: string;
      frame: number;
      actualTime: number;
      timeBefore: number;
      timeAfter: number;
      sha256: string;
    }[] = [];
    manifest.samples = samples;
    if (options.playback && source.video) {
      const browserResult = await capturePlayback(
        source.root,
        source.video,
        output,
        source.plan,
        frames,
        samples,
      );
      assert(
        digest(await readRegular(source.root, source.video)) ===
          source.outputs[source.video].sha256,
        'Video changed during playback review',
      );
      manifest.playback = browserResult;
    }
    const finalSource = await verifyExport(exportDir, !!options.playback);
    assert(
      finalSource.receiptSha256 === source.receiptSha256,
      'Export receipt changed during review',
    );
    manifest.status = 'pending-human-review';
    await fs.writeFile(
      path.join(output, 'review.html'),
      gallery(manifest, canonicalStills, samples),
    );
    await writeReceipt();
    return manifest;
  } catch (error) {
    manifest.errors = [error instanceof Error ? error.message : String(error)];
    await writeReceipt();
    throw error;
  }
}

async function capturePlayback(
  root: string,
  videoName: string,
  output: string,
  plan: Plan,
  frames: number[],
  samples: {
    file: string;
    frame: number;
    actualTime: number;
    timeBefore: number;
    timeAfter: number;
    sha256: string;
  }[],
) {
  const remoteRequests: string[] = [];
  const pageErrors: string[] = [];
  const videoUrl = pathToFileURL(path.join(root, videoName)).href;
  const html = `<!doctype html><html><meta charset="utf-8"><style>*{margin:0}body{background:#000}video{display:block;width:1280px;height:720px}</style><video muted preload="auto" src="${videoUrl}"></video></html>`;
  await fs.writeFile(path.join(output, 'player.html'), html);
  return withBrowser(async (browser) => {
    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 },
      deviceScaleFactor: 1,
    });
    try {
      await context.route(/^https?:/, (route) => {
        remoteRequests.push(route.request().url());
        return route.abort();
      });
      const page = await context.newPage();
      page.on('pageerror', (error) => pageErrors.push(error.message));
      await page.goto(pathToFileURL(path.join(output, 'player.html')).href);
      await page.waitForFunction(
        () => (document.querySelector('video') as HTMLVideoElement).readyState >= 2,
      );
      const metadata = await page.evaluate(() => {
        const v = document.querySelector('video') as HTMLVideoElement;
        return {
          duration: v.duration,
          width: v.videoWidth,
          height: v.videoHeight,
          rate: v.playbackRate,
        };
      });
      const expectedDuration = plan.durationFrames / plan.fps;
      assert(
        metadata.width === 1280 &&
          metadata.height === 720 &&
          Math.abs(metadata.duration - expectedDuration) <= Math.max(0.1, 2 / plan.fps) &&
          metadata.rate === 1,
        'Video metadata differs from export plan',
      );
      const capture = async (frame: number) => {
        const target = frame / plan.fps;
        const before = await page.evaluate(() => {
          const v = document.querySelector('video') as HTMLVideoElement;
          return { time: v.currentTime, rate: v.playbackRate };
        });
        assert(before.rate === 1 && before.time >= target, `Playback missed frame ${frame}`);
        const file = `playback-${String(frame).padStart(6, '0')}.png`;
        const filePath = path.join(output, file);
        await page.screenshot({ path: filePath });
        const after = await page.evaluate(
          () => (document.querySelector('video') as HTMLVideoElement).currentTime,
        );
        samples.push({
          file,
          frame,
          actualTime: (before.time + after) / 2,
          timeBefore: before.time,
          timeAfter: after,
          sha256: digest(await fs.readFile(filePath)),
        });
      };
      // The first decoded frame is captured before normal-rate playback begins.
      await capture(0);
      const started = Date.now();
      await page.evaluate(() => (document.querySelector('video') as HTMLVideoElement).play());
      for (const frame of frames) {
        if (frame === 0) continue;
        const target = frame / plan.fps;
        await page.waitForFunction(
          (time) => {
            const v = document.querySelector('video') as HTMLVideoElement;
            return v.currentTime >= time || v.ended;
          },
          target,
          { timeout: Math.max(10_000, (expectedDuration + 10) * 1000) },
        );
        await capture(frame);
      }
      await page.waitForFunction(
        () => (document.querySelector('video') as HTMLVideoElement).ended,
        null,
        { timeout: Math.max(10_000, (expectedDuration + 10) * 1000) },
      );
      const completion = await page.evaluate(() => {
        const v = document.querySelector('video') as HTMLVideoElement;
        return { ended: v.ended, rate: v.playbackRate, time: v.currentTime };
      });
      assert(
        completion.ended &&
          completion.rate === 1 &&
          Date.now() - started >= (expectedDuration - Math.max(0.1, 2 / plan.fps)) * 1000,
        'Normal-rate playback did not complete',
      );
      const seeks = [];
      for (const fraction of [0, 0.5, 1]) {
        const target =
          fraction === 1
            ? Math.max(0, expectedDuration - 1 / plan.fps)
            : fraction * expectedDuration;
        await page.evaluate(
          (time) =>
            new Promise<void>((resolve) => {
              const v = document.querySelector('video') as HTMLVideoElement;
              v.addEventListener('seeked', () => requestAnimationFrame(() => resolve()), {
                once: true,
              });
              v.currentTime = time;
            }),
          target,
        );
        const actualTime = await page.evaluate(
          () => (document.querySelector('video') as HTMLVideoElement).currentTime,
        );
        assert(
          Math.abs(actualTime - target) <= Math.max(0.1, 2 / plan.fps),
          `Seek differed at ${target}`,
        );
        const file = `seek-${fraction === 0 ? 'start' : fraction === 0.5 ? 'middle' : 'end'}.png`;
        await page.screenshot({ path: path.join(output, file) });
        seeks.push({
          target,
          actualTime,
          file,
          sha256: digest(await fs.readFile(path.join(output, file))),
        });
      }
      assert(
        pageErrors.length === 0 && remoteRequests.length === 0,
        'Page errors or remote requests during playback',
      );
      return {
        browser: browser.version(),
        metadata,
        completion,
        elapsedMs: Date.now() - started,
        seeks,
        pageErrors,
        remoteRequests,
      };
    } finally {
      await context.close();
    }
  });
}
