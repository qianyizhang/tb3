import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const entry = (name) => `/@fs/${root}/presentation/frontend/${name}.tsx`;

export default defineConfig({
  root: path.join(root, '.local/frontend-preview'),
  server: {
    host: '127.0.0.1',
    fs: {
      allow: [
        path.join(root, '.local/frontend-preview'),
        path.join(root, 'presentation/frontend'),
        path.join(root, 'presentation/task-explorer'),
        path.join(root, 'presentation/assets/teaching'),
        path.join(root, 'node_modules'),
      ],
    },
  },
  plugins: [
    {
      name: 'tb3-generated-data-shell',
      transformIndexHtml(html, context) {
        if (context.path.includes('task-explorer')) {
          return html.replace(
            /<script id="explorer-app">[\s\S]*?<\/script>/,
            `<script type="module" src="${entry('explorer')}"></script>`,
          );
        }
        return html.replace(
          /<script\s+src="overview\.js"[^>]*><\/script>/,
          `<script type="module" src="${entry('overview')}"></script>`,
        );
      },
    },
  ],
});
