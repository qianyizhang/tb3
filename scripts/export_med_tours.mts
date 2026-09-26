#!/usr/bin/env node
import { fileURLToPath } from 'node:url';
import { runMedia } from '../presentation/tooling/media/cli.mts';

runMedia(fileURLToPath(new URL('../', import.meta.url)), process.argv.slice(2)).catch(
  (error: unknown) => {
    console.error(error);
    process.exitCode = 1;
  },
);
