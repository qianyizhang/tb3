/** Disposable browser and loopback server shared by presentation checks and exports. */
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');

const contentTypes = {
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

async function serveDirectory(directory) {
  const root = path.resolve(directory);
  const server = http.createServer(async (request, response) => {
    try {
      const name = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
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
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  return {
    url: `http://127.0.0.1:${server.address().port}/`,
    close: () =>
      new Promise((resolve, reject) =>
        server.close((error) => (error ? reject(error) : resolve())),
      ),
  };
}

async function withBrowser(run, options = {}) {
  const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
  const channel = process.env.PLAYWRIGHT_CHANNEL || 'chrome';
  // One launch per invocation. Startup failure ends the suite without retries.
  const browser = await chromium.launch({
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

module.exports = { serveDirectory, withBrowser };
