/** Behavior at the CLI, saved-report and media-planning boundaries; no browser or encoder. */
import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  mkdtempSync,
  readFileSync,
  readdirSync,
  realpathSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { runPython } from '../presentation/tooling/python.mts';
import { parseMediaArgs } from '../presentation/tooling/media/cli.mts';
import {
  captions,
  resolveConfig,
  resolveStories,
  type Stories,
} from '../presentation/tooling/media/tour-plan.mts';
import {
  renderReview,
  reviewMode,
  type ReviewInventory,
} from '../presentation/tooling/visual-review.mts';

const preset = {
  fps: 24,
  crf: 26,
  codec: 'h264',
  encoderPreset: 'slow',
  formats: ['landscape', 'portrait'],
  stills: 'jpeg',
  music: null,
  musicVolume: 0.12,
  fadeSeconds: 2,
};
const stories: Stories = {
  sample: {
    title: 'Source',
    subtitle: 'Subtitle',
    source: 'Attribution',
    duration: 5,
    steps: [
      { at: 0, title: 'First', caption: 'Base copy' },
      { at: 2, title: 'Last', caption: 'End' },
    ],
  },
};

test('Python bridge honors the selected executable and working directory', () => {
  const output = mkdtempSync(join(tmpdir(), 'tb3-python-bridge-'));
  const previous = process.env.TB3_PYTHON;
  try {
    process.env.TB3_PYTHON = process.execPath;
    assert.equal(
      runPython(output, ['-e', 'process.stdout.write(process.cwd())']),
      realpathSync(output),
    );
  } finally {
    if (previous === undefined) delete process.env.TB3_PYTHON;
    else process.env.TB3_PYTHON = previous;
    rmSync(output, { recursive: true, force: true });
  }
});

test('CLI validates types and separates canonical stories from configurable tours', () => {
  assert.deepEqual(parseMediaArgs(['--story=sample', '--output=fresh', '--stills-only']), {
    kind: 'story',
    story: 'sample',
    output: 'fresh',
    stillsOnly: true,
  });
  for (const args of [
    ['--story=sample'],
    ['--story=sample', '--output=fresh', '--fps=24'],
    ['--stills-only=false'],
    ['--fps'],
    ['--typo'],
  ])
    assert.throws(() => parseMediaArgs(args));
  const request = parseMediaArgs(['--fps=30', '--only=sample']);
  assert.equal(request.kind, 'tour');
  if (request.kind === 'tour') assert.deepEqual(request.flags, { fps: '30', only: 'sample' });
});

test('CLI values override custom settings and presets; copy edits preserve scene timing', () => {
  const base = structuredClone(stories);
  const defaults = resolveConfig(preset, {}, {});
  assert.equal(defaults.durationScale, 1);
  assert.equal(defaults.previewSeconds, null);
  for (const invalid of [0, false, '', 'NaN', -1, Infinity]) {
    assert.throws(() => resolveConfig(preset, { durationScale: invalid }, {}), /duration scale/);
    assert.throws(() => resolveConfig(preset, { previewSeconds: invalid }, {}), /preview duration/);
  }
  const config = resolveConfig(
    preset,
    {
      fps: 25,
      durations: { sample: [1, 2] },
      overrides: { sample: { steps: [{ caption: 'Edited copy' }] } },
    },
    { fps: '30', 'duration-scale': '1.5', 'preview-seconds': '2' },
  );
  assert.equal(config.fps, 30);
  assert.equal(config.previewSeconds, 2);
  const resolved = resolveStories(
    base,
    {
      labels: {},
      stories: { sample: { title: 'Translated', steps: [{ caption: 'Translated copy' }] } },
    },
    config,
  );
  assert.equal(resolved.sample.title, 'Translated');
  assert.equal(resolved.sample.steps[0].caption, 'Edited copy');
  assert.deepEqual(
    resolved.sample.steps.map((step) => step.at),
    [0, 1.5],
  );
  assert.equal(resolved.sample.duration, 4.5);
  assert.deepEqual(base, stories, 'planning must not change source storyboards');
  assert.equal(
    captions(resolved.sample, 2, 'vtt'),
    'WEBVTT\n\n1\n00:00:00.000 --> 00:00:01.500\nFirst\nEdited copy\n\n2\n00:00:01.500 --> 00:00:02.000\nLast\nEnd\n',
  );
  assert.match(captions(resolved.sample, 2, 'srt'), /00:00:01,500 --> 00:00:02,000/);
  for (const invalid of [
    { fps: 0 },
    { durationScale: 0 },
    { formats: [] },
    { durations: { sample: ['1', 2] } },
    { overrides: { sample: { steps: [{ caption: 12 }] } } },
  ])
    assert.throws(() => resolveConfig(preset, invalid, {}));
  assert.throws(
    () =>
      resolveStories(
        base,
        { labels: {}, stories: {} },
        resolveConfig(preset, { durations: { sample: [1] } }, {}),
      ),
    /durations/,
  );
});

test('report-only replay preserves inventory bytes, provenance, and failed exit status', () => {
  const output = mkdtempSync(join(tmpdir(), 'tb3-review-test-'));
  try {
    const original = JSON.stringify(
      {
        source: 'original.html',
        summary: {
          entries: 0,
          spatial: 0,
          static: 0,
          sourceImages: 0,
          errors: ['Retained page error <witness>'],
        },
        entries: [],
      },
      null,
      4,
    );
    const inventory = join(output, 'inventory.json');
    writeFileSync(inventory, original);
    const result = spawnSync(
      process.execPath,
      [
        fileURLToPath(new URL('../scripts/task_visual_review.mts', import.meta.url)),
        'unused.html',
        output,
        '--from-inventory',
      ],
      { encoding: 'utf8' },
    );
    assert.equal(result.status, 1, result.stderr);
    assert.equal(readFileSync(inventory, 'utf8'), original);
    assert.match(
      readFileSync(join(output, 'index.html'), 'utf8'),
      /Retained page error &lt;witness&gt;/,
    );
    assert.deepEqual(JSON.parse(result.stdout).errors, ['Retained page error <witness>']);
  } finally {
    rmSync(output, { recursive: true, force: true });
  }
});

test('review labels retain the actual planar and fallback renderer modes', () => {
  const modes = ['webgl', 'planar', 'poster', 'svg', 'static'].map(reviewMode);
  assert.deepEqual(modes, ['3d', 'planar', 'fallback', 'fallback', 'static']);
  assert.throws(() => reviewMode('uninitialized'));
  const inventory: ReviewInventory = {
    source: 'planar.html',
    summary: { entries: 1, spatial: 0, planar: 1, static: 0, sourceImages: 0, errors: [] },
    entries: [
      {
        id: 'sample',
        title: 'Planar sample',
        kind: 'multiscale',
        mode: 'planar',
        disposition: 'planar DOM/SVG',
        sourceImage: false,
        missingMedia: 0,
        images: ['images/sample.png'],
        chapters: ['Caption <one>'],
      },
    ],
  };
  const html = renderReview(inventory);
  assert.match(html, /0 spatial 3D · 1 planar/);
  assert.match(html, /data-mode="planar"/);
  assert.match(html, /Caption &lt;one&gt;/);
});

test('importing the media library performs no export or filesystem work', () => {
  const output = mkdtempSync(join(tmpdir(), 'tb3-import-test-'));
  try {
    const moduleUrl = new URL('../presentation/tooling/media/cli.mts', import.meta.url).href;
    const result = spawnSync(
      process.execPath,
      ['--input-type=module', '-e', `await import(${JSON.stringify(moduleUrl)})`],
      { cwd: output, encoding: 'utf8' },
    );
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout, '');
    assert.deepEqual(readdirSync(output), []);
  } finally {
    rmSync(output, { recursive: true, force: true });
  }
});
