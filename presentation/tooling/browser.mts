/** Disposable browser and loopback server shared by presentation checks and exports. */
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { createRequire } from 'node:module';
import type { chromium, Browser, LaunchOptions } from 'playwright';

const contentTypes: Record<string, string> = {
  '.html': 'text/html',
  '.json': 'application/json',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
  '.jpg': 'image/jpeg',
  '.gz': 'application/gzip',
  '.mp4': 'video/mp4',
  '.webm': 'video/webm',
  '.vtt': 'text/vtt',
};

export async function serveDirectory(directory: string) {
  const root = path.resolve(directory);
  const server = http.createServer(async (request, response) => {
    try {
      const name = decodeURIComponent(new URL(request.url || '/', 'http://localhost').pathname);
      const target = path.resolve(root, '.' + (name.endsWith('/') ? name + 'index.html' : name));
      if (!target.startsWith(root + path.sep)) {
        response.writeHead(404).end();
        return;
      }
      const stat = await fs.promises.stat(target);
      if (!stat.isFile()) throw Error('Not a file');
      response.writeHead(200, {
        'Content-Type': contentTypes[path.extname(target)] || 'application/octet-stream',
        'Content-Length': stat.size,
      });
      const stream = fs.createReadStream(target);
      stream.on('error', (error) => response.destroy(error));
      stream.pipe(response);
    } catch {
      response.writeHead(404).end();
    }
  });
  await new Promise<void>((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const address = server.address();
  if (!address || typeof address === 'string') throw Error('Expected loopback TCP address');
  return {
    url: `http://127.0.0.1:${address.port}/`,
    close: () =>
      new Promise<void>((resolve, reject) =>
        server.close((error) => (error ? reject(error) : resolve())),
      ),
  };
}

export async function withBrowser<T>(
  run: (browser: Browser) => Promise<T>,
  options: LaunchOptions = {},
): Promise<T> {
  const engine: typeof chromium = createRequire(import.meta.url)(
    process.env.PLAYWRIGHT_MODULE || 'playwright',
  ).chromium;
  const channel = process.env.PLAYWRIGHT_CHANNEL || 'chrome';
  // One launch per invocation. Startup failure ends the suite without retries.
  const browser = await engine.launch({
    headless: true,
    ...(channel === 'chromium' ? {} : { channel }),
    ...options,
  });
  try {
    return await run(browser);
  } finally {
    await browser.close();
  }
}
