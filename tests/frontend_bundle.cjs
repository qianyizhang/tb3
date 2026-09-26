/** Load production modules through Vite; optional adapters control resources and time. */
const path = require('node:path');
const vm = require('node:vm');

async function loadFrontend(entry, { globals = {}, plugins = [] } = {}) {
  const { build } = await import('vite');
  const bundles = await build({
    configFile: false,
    root: path.resolve(__dirname, '..'),
    logLevel: 'silent',
    plugins,
    build: {
      write: false,
      minify: false,
      target: 'es2022',
      lib: { entry: path.resolve(__dirname, entry), name: 'Fixture', formats: ['iife'] },
    },
  });
  const chunk = bundles[0].output.find((item) => item.type === 'chunk' && item.isEntry);
  if (!chunk) throw new Error('Vite did not produce a frontend fixture entry');
  const context = vm.createContext(globals);
  vm.runInContext(chunk.code, context);
  return context.Fixture;
}

module.exports = { loadFrontend };
