import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { rolldown } from 'rolldown';
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../../..');
const out = path.join(root, '.local/anatomy-pose/trace');
const bundle = await rolldown({ input: path.join(here, 'trace.js') });
const result = await bundle.generate({ format: 'iife', minify: true });
const script = result.output.find((x) => x.type === 'chunk').code;
const data = fs.readFileSync(path.join(out, 'data.json'), 'utf8').replaceAll('<', '\\u003c');
const license = fs.readFileSync(path.join(root, 'node_modules/three/LICENSE'), 'utf8');
const html = fs
  .readFileSync(path.join(here, 'trace.html'), 'utf8')
  .replace('__CSS__', fs.readFileSync(path.join(here, 'trace.css'), 'utf8'))
  .replace('__DATA__', () => data)
  .replace('__SCRIPT__', () => script.replace(/<\/script/gi, '<\\/script'))
  .replace('<head>', '<head><!-- Three.js license\n' + license + '\n-->');
fs.writeFileSync(path.join(out, 'index.html'), html);
fs.writeFileSync(path.join(out, 'THREE-LICENSE.txt'), license);
console.log(
  JSON.stringify({ output: path.join(out, 'index.html'), bytes: Buffer.byteLength(html) }),
);
await bundle.close();
