/** Failure and publication contracts for the media encoder helper; no browser or FFmpeg. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { normalizeTiming, runPipedEncoder } = require('../scripts/media_export_support.cjs');

async function waitForFile(file) {
  const deadline = Date.now() + 2000;
  while (!fs.existsSync(file)) {
    if (Date.now() >= deadline) throw Error(`Timed out waiting for ${file}`);
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
}

(async () => {
  const unhandled = [];
  process.on('unhandledRejection', (error) => unhandled.push(error));
  assert.deepEqual(normalizeTiming({}), { durationScale: 1, previewSeconds: null });
  assert.deepEqual(normalizeTiming({ durationScale: '1.25', previewSeconds: '2' }), {
    durationScale: 1.25,
    previewSeconds: 2,
  });
  for (const invalid of [0, false, '']) {
    assert.throws(() => normalizeTiming({ durationScale: invalid }), /duration scale/);
    assert.throws(() => normalizeTiming({ previewSeconds: invalid }), /preview duration/);
  }

  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'tb3-media-export-'));
  try {
    const destination = path.join(directory, 'tour.mp4');
    const marker = path.join(directory, 'child-started');
    fs.writeFileSync(destination, 'previous export');
    const waitingChild = `
      const fs = require('node:fs');
      fs.writeFileSync(process.argv[2], 'partial export');
      fs.writeFileSync(process.argv[1], String(process.pid));
      process.stdin.resume();
      setInterval(() => {}, 1000);
    `;
    await assert.rejects(
      runPipedEncoder({
        command: process.execPath,
        args: ['-e', waitingChild, marker],
        destination,
        renderFrames: async () => {
          await waitForFile(marker);
          throw Error('render failed');
        },
      }),
      /render failed/,
    );
    assert.equal(fs.readFileSync(destination, 'utf8'), 'previous export');
    assert.deepEqual(
      fs.readdirSync(directory).sort(),
      ['child-started', 'tour.mp4'],
      'failed render removes only its partial output',
    );

    await assert.rejects(
      runPipedEncoder({
        command: path.join(directory, 'missing-encoder'),
        args: [],
        destination,
        renderFrames: async (writeFrame) => writeFrame(Buffer.from('frame')),
      }),
      /ENOENT|spawn/,
    );
    assert.equal(fs.readFileSync(destination, 'utf8'), 'previous export');
    assert.deepEqual(fs.readdirSync(directory).sort(), ['child-started', 'tour.mp4']);

    const failingChild = `
      process.stderr.write('encoder failed');
      process.exit(7);
    `;
    await assert.rejects(
      runPipedEncoder({
        command: process.execPath,
        args: ['-e', failingChild],
        destination,
        renderFrames: async (writeFrame) => {
          await new Promise((resolve) => setTimeout(resolve, 30));
          await writeFrame(Buffer.from('frame'));
        },
      }),
      /encoder failed|EPIPE|write/,
    );
    assert.equal(fs.readFileSync(destination, 'utf8'), 'previous export');
    assert.deepEqual(fs.readdirSync(directory).sort(), ['child-started', 'tour.mp4']);

    const copyingChild = `
      const fs = require('node:fs');
      const chunks = [];
      process.stdin.on('data', (chunk) => chunks.push(chunk));
      process.stdin.on('end', () => fs.writeFileSync(process.argv[1], Buffer.concat(chunks)));
    `;
    await runPipedEncoder({
      command: process.execPath,
      args: ['-e', copyingChild],
      destination,
      renderFrames: async (writeFrame) => writeFrame(Buffer.from('replacement export')),
    });
    assert.equal(fs.readFileSync(destination, 'utf8'), 'replacement export');
    assert.deepEqual(fs.readdirSync(directory).sort(), ['child-started', 'tour.mp4']);
    await new Promise((resolve) => setImmediate(resolve));
    assert.deepEqual(unhandled, [], 'encoder failures are observed immediately');
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
  console.log('Media export: timing validation, failure cleanup and atomic publication passed.');
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
