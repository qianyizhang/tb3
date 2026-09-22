/** Build local, self-contained UI bundles. Python verifies this receipt before export. */
import { createHash } from 'node:crypto';
import { readdir, readFile, mkdir, writeFile, rename, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'vite';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, '.local/frontend');
const pending = path.join(root, '.local/frontend-pending-' + process.pid);
const hash = (bytes) => createHash('sha256').update(bytes).digest('hex');
async function files(directory) {
  const entries = await readdir(path.join(root, directory), { withFileTypes: true });
  const nested = await Promise.all(
    entries.map((entry) => {
      const name = directory + '/' + entry.name;
      return entry.isDirectory() ? files(name) : [name];
    }),
  );
  return nested.flat();
}
async function inputHashes() {
  const names = [
    'package.json',
    'package-lock.json',
    'tsconfig.json',
    'scripts/build_frontend.mjs',
    'src/tb3_medical/presentation_contracts.py',
    'presentation/task-explorer/assets/Apache-2.0.txt',
    ...(await files('presentation/frontend')).filter((name) => /\.(tsx?|css|js)$/.test(name)),
    ...(await files('presentation/assets/teaching')).filter((name) =>
      /\.(tsx?|css|js)$/.test(name),
    ),
    ...(await readdir(path.join(root, 'presentation/task-explorer')))
      .filter((name) => /^scene.*\.(js|d\.ts)$/.test(name))
      .map((name) => 'presentation/task-explorer/' + name),
    ...(await files('presentation/task-explorer/anatomy')),
  ].sort();
  return Object.fromEntries(
    await Promise.all(
      names.map(async (name) => [name, hash(await readFile(path.join(root, name)))]),
    ),
  );
}
await mkdir(pending, { recursive: true });
try {
  const inputs = await inputHashes();
  for (const entry of ['explorer', 'overview']) {
    await build({
      configFile: false,
      root,
      base: './',
      define: { 'process.env.NODE_ENV': '"production"' },
      build: {
        outDir: pending,
        emptyOutDir: false,
        target: 'es2022',
        cssCodeSplit: false,
        lib: {
          entry: path.join(root, `presentation/frontend/${entry}.tsx`),
          name: `TB3${entry}`,
          formats: ['iife'],
          fileName: () => entry + '.js',
          cssFileName: entry,
        },
      },
    });
  }
  if (JSON.stringify(inputs) !== JSON.stringify(await inputHashes())) {
    throw Error('Frontend source changed during the build; rebuild the current source.');
  }
  const outputs = Object.fromEntries(
    await Promise.all(
      (await readdir(pending))
        .sort()
        .map(async (name) => [name, hash(await readFile(path.join(pending, name)))]),
    ),
  );
  await writeFile(
    path.join(pending, 'manifest.json'),
    JSON.stringify({ schema_version: 1, inputs, outputs }, null, 2) + '\n',
  );
  await rm(output, { recursive: true, force: true });
  await rename(pending, output);
  console.log('Frontend receipt: .local/frontend/manifest.json');
} finally {
  await rm(pending, { recursive: true, force: true });
}
