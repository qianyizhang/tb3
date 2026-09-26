/** Capture an Explorer or regenerate its report from the unchanged inventory. */
import { resolve } from 'node:path';
import { parseArgs } from 'node:util';
import { review } from '../presentation/tooling/visual-review.mts';

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: { 'from-inventory': { type: 'boolean' } },
});
if (positionals.length < 1 || positionals.length > 2)
  throw Error('Usage: task_visual_review.mts INPUT_HTML [OUTPUT_DIR] [--from-inventory]');
review(
  resolve(positionals[0]),
  resolve(positionals[1] || '.local/task-visual-review'),
  values['from-inventory'],
)
  .then((inventory) => {
    console.log(JSON.stringify(inventory.summary));
    if (inventory.summary.errors.length) process.exitCode = 1;
  })
  .catch((error: unknown) => {
    console.error(error);
    process.exitCode = 1;
  });
