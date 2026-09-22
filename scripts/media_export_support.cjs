/** Small, testable helpers for deterministic media export. */
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { once } = require('node:events');

function normalizeTiming({ durationScale, previewSeconds }) {
  const normalizedScale = Number(durationScale ?? 1);
  if (!(normalizedScale > 0 && normalizedScale <= 10)) {
    throw Error('duration scale must be >0 and <=10');
  }
  const normalizedPreview =
    previewSeconds === undefined || previewSeconds === null ? null : Number(previewSeconds);
  if (
    normalizedPreview !== null &&
    !(Number.isFinite(normalizedPreview) && normalizedPreview > 0)
  ) {
    throw Error('Invalid preview duration');
  }
  return { durationScale: normalizedScale, previewSeconds: normalizedPreview };
}

function temporaryOutputPath(destination) {
  const extension = path.extname(destination);
  const stem = path.basename(destination, extension);
  const token = crypto.randomBytes(6).toString('hex');
  return path.join(
    path.dirname(destination),
    `.${stem}.partial-${process.pid}-${token}${extension}`,
  );
}

async function settle(promise) {
  try {
    await promise;
  } catch {
    // The original render or encoder error remains authoritative.
  }
}

async function stopProcess(child, finished) {
  if (child.exitCode !== null || child.signalCode !== null) {
    await settle(finished);
    return;
  }
  child.kill('SIGTERM');
  let timer;
  const timedOut = await Promise.race([
    finished.then(
      () => false,
      () => false,
    ),
    new Promise((resolve) => {
      timer = setTimeout(() => resolve(true), 1000);
    }),
  ]);
  if (timer) clearTimeout(timer);
  if (timedOut && child.exitCode === null && child.signalCode === null) {
    child.kill('SIGKILL');
    await settle(finished);
  }
}

async function runPipedEncoder({ command, args, destination, renderFrames, spawnProcess = spawn }) {
  const partial = temporaryOutputPath(destination);
  const child = spawnProcess(command, [...args, partial], {
    stdio: ['pipe', 'ignore', 'pipe'],
  });
  let stderr = '';
  let pipeError = null;
  child.stderr.on('data', (chunk) => (stderr += chunk));
  child.stdin.on('error', (error) => (pipeError = error));
  // Observe spawn errors immediately; renderFrames may still be awaiting the browser.
  const finished = once(child, 'close').then(
    ([code, signal]) => ({ code, signal, error: null }),
    (error) => ({ code: null, signal: null, error }),
  );
  let published = false;

  const writeFrame = async (frame) => {
    if (pipeError) throw Error(`${pipeError.message}: ${stderr}`);
    if (!child.stdin.write(frame)) {
      await Promise.race([
        once(child.stdin, 'drain'),
        finished.then((outcome) => {
          if (outcome.error) throw outcome.error;
          throw Error(stderr || 'Encoder stopped early');
        }),
      ]);
    }
    if (pipeError) throw Error(`${pipeError.message}: ${stderr}`);
  };

  try {
    await renderFrames(writeFrame);
    child.stdin.end();
    const outcome = await finished;
    if (outcome.error) throw outcome.error;
    if (outcome.code !== 0) {
      throw Error(stderr || `Encoder stopped with ${outcome.signal || `status ${outcome.code}`}`);
    }
    fs.renameSync(partial, destination);
    published = true;
  } catch (error) {
    if (!child.stdin.destroyed) child.stdin.destroy();
    await stopProcess(child, finished);
    throw error;
  } finally {
    if (!published) fs.rmSync(partial, { force: true });
  }
}

module.exports = { normalizeTiming, runPipedEncoder };
