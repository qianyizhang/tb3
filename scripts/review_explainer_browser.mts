/** Pin the existing browser matrix to the exact batch and Explorer it exercises. */
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, realpathSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = realpathSync(process.cwd());
const sha = (file: string) => createHash('sha256').update(readFileSync(file)).digest('hex');
function inside(file: string) {
  const absolute = realpathSync(file);
  if (!absolute.startsWith(root + path.sep)) throw Error('Browser witness must stay in workspace');
  return path.relative(root, absolute);
}
let failure: string | undefined;
try {
  const entryOnly = process.argv[4] === '--entry-only';
  if (process.argv.length !== 4 && !(process.argv.length === 5 && entryOnly))
    throw Error(
      'Usage: node scripts/review_explainer_browser.mts BATCH-DIRECTORY EXPLORER-HTML [--entry-only]',
    );
  const batchDir = path.resolve(process.argv[2]);
  const explorer = path.resolve(process.argv[3]);
  const batchFile = path.join(batchDir, 'batch.json');
  const matrixFile = path.join(batchDir, 'browser-matrix.json');
  const witnessFile = path.join(batchDir, 'browser-witness.json');
  failure = path.join(batchDir, 'browser-witness.failure.json');
  inside(batchFile);
  inside(explorer);
  if ([matrixFile, witnessFile, failure].some(existsSync))
    throw Error('Browser matrix already attempted; use a fresh batch');
  const batch = JSON.parse(readFileSync(batchFile, 'utf8')) as {
    entries: { entry_id: string; story_id: string }[];
  };
  const paths = [
    batchFile,
    explorer,
    'tests/explanation_expansion_browser.cjs',
    'presentation/tooling/browser.mts',
    'scripts/review_explainer_browser.mts',
  ];
  for (const entry of batch.entries) {
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(entry.story_id)) throw Error('Unsafe story id');
    paths.push(
      ...['plan.json', 'receipt.json', 'index.html'].map((name) =>
        path.join(batchDir, entry.story_id, name),
      ),
    );
  }
  const pins = Object.fromEntries(paths.map((file) => [inside(file), sha(file)]));
  execFileSync(
    process.execPath,
    [
      'tests/explanation_expansion_browser.cjs',
      batchDir,
      explorer,
      ...(entryOnly ? ['--entry-only'] : []),
    ],
    {
      cwd: root,
      stdio: 'inherit',
    },
  );
  for (const [file, expected] of Object.entries(pins))
    if (sha(file) !== expected) throw Error(`Browser input changed: ${file}`);
  const matrix = JSON.parse(readFileSync(matrixFile, 'utf8')) as {
    errors: unknown[];
    remote_requests: unknown[];
  };
  if (matrix.errors.length || matrix.remote_requests.length)
    throw Error('Browser matrix reported errors');
  writeFileSync(
    witnessFile,
    JSON.stringify(
      {
        schema: 1,
        kind: 'explainer-browser-witness',
        navigation_scope: entryOnly ? 'current-entry' : 'full-regression',
        sources: pins,
        batch: inside(batchFile),
        explorer: inside(explorer),
        entries: batch.entries,
        matrix: { path: inside(matrixFile), sha256: sha(matrixFile) },
      },
      null,
      2,
    ) + '\n',
    { flag: 'wx' },
  );
  process.stdout.write(`Browser witness: ${witnessFile}\n`);
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  if (failure && !existsSync(failure))
    writeFileSync(failure, JSON.stringify({ error: message }) + '\n', { flag: 'wx' });
  process.stderr.write(message + '\n');
  process.exitCode = 1;
}
