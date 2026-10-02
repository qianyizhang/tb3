/** Build local, self-contained UI bundles. Python verifies this receipt before export. */
import { createHash } from 'node:crypto';
import { readdir, readFile, mkdir, writeFile, rename, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'vite';
import { runPython } from '../presentation/tooling/python.mts';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, '.local/frontend');
const pending = path.join(root, '.local/frontend-pending-' + process.pid);
const hash = (bytes: Buffer) => createHash('sha256').update(bytes).digest('hex');
function inputHashes(validate = false): Record<string, string> {
  return JSON.parse(
    runPython(root, ['-m', 'tb3_medical.frontend', ...(validate ? ['--validate-stories'] : [])]),
  );
}
await mkdir(pending, { recursive: true });
try {
  const inputs = inputHashes(true);
  let servedOutputs: string[] = [];
  const modules: Record<string, string[]> = {};
  for (const entry of [
    'explorer',
    'overview',
    'explainer-export',
    'restoration-export',
    'explorer-served',
  ]) {
    const served = entry === 'explorer-served';
    const result = await build({
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
          entry: path.join(root, `presentation/frontend/${served ? 'explorer' : entry}.tsx`),
          name: `TB3${entry.replaceAll('-', '')}`,
          formats: served ? ['es'] : ['iife'],
          fileName: () => entry + '.js',
          cssFileName: entry,
        },
      },
    });
    const bundles = Array.isArray(result) ? result : [result];
    const files = bundles.flatMap((bundle) => ('output' in bundle ? bundle.output : []));
    modules[entry] = [
      ...new Set(
        files.flatMap((file) =>
          file.type === 'chunk'
            ? Object.keys(file.modules).map((id) => path.relative(root, id))
            : [],
        ),
      ),
    ].sort();
    if (served) servedOutputs = files.map((file) => file.fileName);
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
    JSON.stringify({ schema_version: 1, inputs, outputs, servedOutputs, modules }, null, 2) + '\n',
  );
  await rm(output, { recursive: true, force: true });
  await rename(pending, output);
  console.log('Frontend receipt: .local/frontend/manifest.json');
} finally {
  await rm(pending, { recursive: true, force: true });
}
