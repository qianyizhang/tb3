/** Build local, self-contained UI bundles. Python verifies this receipt before export. */
import { createHash } from 'node:crypto';
import { readdir, readFile, mkdir, writeFile, rename, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'vite';
import { execFileSync } from 'node:child_process';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, '.local/frontend');
const pending = path.join(root, '.local/frontend-pending-' + process.pid);
const hash = (bytes) => createHash('sha256').update(bytes).digest('hex');
function inputHashes() {
  return JSON.parse(
    execFileSync(path.join(root, '.venv/bin/python'), ['-m', 'tb3_medical.frontend'], {
      cwd: root,
      encoding: 'utf8',
    }),
  );
}
await mkdir(pending, { recursive: true });
try {
  execFileSync(
    path.join(root, '.venv/bin/python'),
    [
      '-c',
      'from pathlib import Path; from tb3_medical.explanation_stories import compile_story; r=Path.cwd(); [compile_story(r,p) for p in [*r.glob("groups/*/presentation/stories/*.story.md"), *r.glob("presentation/external-tasks/stories/*.story.md")]]',
    ],
    { cwd: root, stdio: 'inherit' },
  );
  const inputs = inputHashes();
  for (const entry of ['explorer', 'overview', 'explainer-export']) {
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
          name: `TB3${entry.replaceAll('-', '')}`,
          formats: ['iife'],
          fileName: () => entry + '.js',
          cssFileName: entry,
        },
      },
    });
  }
  if (JSON.stringify(inputs) !== JSON.stringify(inputHashes())) {
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
