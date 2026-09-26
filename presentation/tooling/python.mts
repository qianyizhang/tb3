/** Invoke a named Python operation in the selected workbench environment. */
import { execFileSync } from 'node:child_process';

export function runPython(root: string, args: string[]): string {
  const interpreter = process.env.TB3_PYTHON;
  return execFileSync(
    interpreter || 'uv',
    interpreter ? args : ['run', '--no-sync', 'python', ...args],
    {
      cwd: root,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'inherit'],
    },
  );
}
