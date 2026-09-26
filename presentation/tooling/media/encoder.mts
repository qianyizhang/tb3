/** Pipe frames to an encoder; publish only after successful process completion. */
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { spawn, type ChildProcessByStdio } from 'node:child_process';
import type { Readable, Writable } from 'node:stream';
import { once } from 'node:events';

function temporaryOutputPath(destination: string): string {
  const extension = path.extname(destination);
  const stem = path.basename(destination, extension);
  const token = crypto.randomBytes(6).toString('hex');
  return path.join(
    path.dirname(destination),
    `.${stem}.partial-${process.pid}-${token}${extension}`,
  );
}

type EncoderProcess = ChildProcessByStdio<Writable, null, Readable>;
interface Outcome {
  code: number | null;
  signal: NodeJS.Signals | null;
  error: Error | null;
}

async function stopProcess(child: EncoderProcess, finished: Promise<Outcome>): Promise<void> {
  if (child.exitCode !== null || child.signalCode !== null) {
    await finished;
    return;
  }
  child.kill('SIGTERM');
  let timer: ReturnType<typeof setTimeout> | undefined;
  const timedOut = await Promise.race([
    finished.then(() => false),
    new Promise<boolean>((resolve) => {
      timer = setTimeout(() => resolve(true), 1000);
    }),
  ]);
  if (timer) clearTimeout(timer);
  if (timedOut && child.exitCode === null && child.signalCode === null) {
    child.kill('SIGKILL');
    await finished;
  }
}

export interface EncoderRequest {
  command: string;
  args: string[];
  destination: string;
  renderFrames(writeFrame: (frame: Uint8Array) => Promise<void>): Promise<void>;
}

export async function runPipedEncoder({
  command,
  args,
  destination,
  renderFrames,
}: EncoderRequest): Promise<void> {
  const partial = temporaryOutputPath(destination);
  const child = spawn(command, [...args, partial], {
    stdio: ['pipe', 'ignore', 'pipe'],
  });
  let stderr = '';
  let pipeError: Error | undefined;
  child.stderr.on('data', (chunk) => (stderr += chunk));
  child.stdin.on('error', (error: Error) => (pipeError = error));
  // Observe spawn errors immediately; renderFrames may still be awaiting the browser.
  const finished: Promise<Outcome> = once(child, 'close').then(
    ([code, signal]) => ({ code, signal, error: null }),
    (error) => ({ code: null, signal: null, error }),
  );
  let published = false;

  const checkPipe = () => {
    if (pipeError) throw Error(`${pipeError.message}: ${stderr}`);
  };
  const writeFrame = async (frame: Uint8Array): Promise<void> => {
    checkPipe();
    if (!child.stdin.write(frame)) {
      await Promise.race([
        once(child.stdin, 'drain'),
        finished.then((outcome) => {
          if (outcome.error) throw outcome.error;
          throw Error(stderr || 'Encoder stopped early');
        }),
      ]);
    }
    checkPipe();
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
