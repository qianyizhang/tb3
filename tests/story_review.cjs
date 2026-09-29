const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const { test } = require('node:test');
const {
  collectStoryReview,
  parseFrameNumbers,
  reviewFrames,
  safeLeaf,
  safeWorkspacePath,
  verifySrt,
} = require('../presentation/tooling/story-review.mts');

const plan = {
  id: 'fixture',
  title: 'Fixture',
  fps: 25,
  durationFrames: 100,
  beats: [
    { id: 'a', caption: 'First caption', startFrame: 0, endFrame: 40 },
    {
      id: 'b',
      caption: 'Second caption',
      startFrame: 40,
      endFrame: 100,
      channels: { reference: [0, 1] },
    },
  ],
};

test('review frames include boundaries, motion and explicit witnesses', () => {
  assert.deepEqual(reviewFrames(plan, [73]), [0, 19, 39, 40, 69, 70, 73, 99]);
  assert.deepEqual(parseFrameNumbers('99,0,99', 100), [0, 99]);
  assert.throws(() => parseFrameNumbers('100', 100), /outside export/);
  assert.throws(() => parseFrameNumbers('-1', 100), /Invalid frame/);
});

test('SRT matches dynamic fps, beat captions and boundaries', () => {
  const valid =
    '1\n00:00:00,000 --> 00:00:01,600\nFirst caption\n\n2\n00:00:01,600 --> 00:00:04,000\nSecond caption\n';
  assert.doesNotThrow(() => verifySrt(valid, plan));
  assert.throws(
    () => verifySrt(valid.replace('Second caption', 'Wrong caption'), plan),
    /caption differs/,
  );
  assert.throws(
    () => verifySrt(valid.replace('00:00:04,000', '00:00:04,040'), plan),
    /timing differs/,
  );
});

test('artifact names reject traversal and nested paths', () => {
  assert.equal(safeLeaf('first.png'), 'first.png');
  for (const name of ['../first.png', 'x/y.png', '.', '..', 'a\\b.png'])
    assert.throws(() => safeLeaf(name), /Unsafe artifact/);
  assert.equal(safeWorkspacePath('groups/example/story.md'), 'groups/example/story.md');
  for (const name of ['../source.md', '/absolute.md', 'a//b.md', 'a/./b.md', 'a\\b.md'])
    assert.throws(() => safeWorkspacePath(name), /Unsafe source path/);
});

test('offline collection pins artifacts and leaves visual review pending', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'tb3-story-review-'));
  try {
    const source = path.join(root, 'source');
    await fs.mkdir(source);
    const single = {
      id: 'fixture',
      title: 'Fixture',
      source_sha256: '',
      dependencies: {},
      fps: 25,
      durationFrames: 50,
      beats: [{ id: 'only', caption: 'Caption', startFrame: 0, endFrame: 50 }],
    };
    const files = {
      'canonical.story.md': 'story\n',
      'captions.srt': '1\n00:00:00,000 --> 00:00:02,000\nCaption\n',
      'captions.vtt': 'WEBVTT\n',
      'first.png': 'first',
      'poster.png': 'poster',
      'only.png': 'only',
      'index.html': '<!doctype html>',
      'transcript.md': 'Transcript',
      'stills.json': JSON.stringify([{ file: 'only.png', frame: 49, caption: 'Caption' }]),
    };
    const hash = (data) => crypto.createHash('sha256').update(data).digest('hex');
    single.source_sha256 = hash(files['canonical.story.md']);
    files['plan.json'] = JSON.stringify(single);
    const outputs = {};
    for (const [name, value] of Object.entries(files)) {
      await fs.writeFile(path.join(source, name), value);
      outputs[name] = { sha256: hash(value), bytes: Buffer.byteLength(value) };
    }
    await fs.writeFile(
      path.join(source, 'receipt.json'),
      JSON.stringify({
        story: 'fixture',
        source_sha256: single.source_sha256,
        plan_sha256: outputs['plan.json'].sha256,
        settings: { width: 1280, height: 720, fps: 25, frames: 50 },
        outputs,
        dependencies: {},
        errors: [],
      }),
    );
    const output = path.join(root, 'review');
    const manifest = await collectStoryReview(source, output);
    assert.equal(manifest.status, 'pending-human-review');
    assert.equal(manifest.visual_review, 'pending');
    assert.equal(manifest.storyId, 'fixture');
    assert.deepEqual(manifest.requestedFrames, []);
    assert.equal(await fs.readFile(path.join(output, 'only.png'), 'utf8'), 'only');
    await fs.writeFile(path.join(source, 'only.png'), 'altered');
    const failed = path.join(root, 'failed');
    await assert.rejects(() => collectStoryReview(source, failed), /Output differs from receipt/);
    assert.equal(
      JSON.parse(await fs.readFile(path.join(failed, 'review.json'), 'utf8')).status,
      'failed',
    );
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});
